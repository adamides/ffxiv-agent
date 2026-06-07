#!/usr/bin/env python3
"""
Fetch one FFLogs fight and emit paste-ready, decoded text for the analysis agent.

Usage:
    python scripts/fetch_fight.py <REPORT_CODE> [FIGHT_ID]

If FIGHT_ID is omitted, lists the fights in the report and exits.

Reads FFLOGS_CLIENT_ID / FFLOGS_CLIENT_SECRET from the repo-root .env file (or
the environment). The .env path is resolved relative to this script's location,
so it can be launched from any directory. Precedence: variables already set in
the environment win; .env only fills in ones that are unset (the conventional
dotenv behavior). Uses only the Python standard library so it runs without pip.

Design notes (see knowledge/fundamentals.md):
  - Damage school is on the ability, not the event: masterData.abilities[].type
    128 = physical, 1024 = magical; anything else -> "unknown".
  - The event's `multiplier` is the realized combined % mitigation (shields are
    separate and not represented here).
  - Max HP is not cheaply exposed by the API; we capture `vitality` as a proxy.
  - Failure markers (Damage Down, vulns, Weakness) and many mechanic debuffs
    (e.g. confetti, the magic-vuln laser) live in `applydebuff` events, NOT
    damage events. We pull a Debuffs timeline so the agent can read who failed
    and who is out of the soak pool, per the diagnostic path in fundamentals.md.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from urllib import request, error

TOKEN_URL = "https://www.fflogs.com/oauth/token"
GQL_URL = "https://www.fflogs.com/api/v2/client"

# Confirmed against the test report; extend as new codes are identified.
SCHOOL_BY_TYPE = {128: "physical", 1024: "magical"}


# --------------------------------------------------------------------------- #
# Auth + transport
# --------------------------------------------------------------------------- #
def load_env(path=Path(__file__).resolve().parent.parent / ".env"):
    """Parse a simple KEY=VALUE .env file into os.environ (does not overwrite).

    The default path is anchored to the repo root (this script's grandparent
    dir), not the cwd, so the script can be launched from any directory.
    """
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)


def get_token():
    cid = os.environ.get("FFLOGS_CLIENT_ID")
    secret = os.environ.get("FFLOGS_CLIENT_SECRET")
    if not cid or not secret:
        sys.exit("ERROR: FFLOGS_CLIENT_ID / FFLOGS_CLIENT_SECRET not set (.env or env).")
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    body = b"grant_type=client_credentials"
    req = request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with request.urlopen(req) as resp:
            return json.load(resp)["access_token"]
    except error.HTTPError as exc:
        sys.exit(f"ERROR: token request failed ({exc.code}): {exc.read().decode()}")


def gql(token, query):
    req = request.Request(
        GQL_URL,
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req) as resp:
            payload = json.load(resp)
    except error.HTTPError as exc:
        sys.exit(f"ERROR: query failed ({exc.code}): {exc.read().decode()}")
    if "errors" in payload:
        sys.exit("ERROR: GraphQL errors: " + json.dumps(payload["errors"]))
    return payload["data"]


# --------------------------------------------------------------------------- #
# Fetchers
# --------------------------------------------------------------------------- #
def fetch_fights(token, code):
    q = (
        '{ reportData { report(code:"%s") { '
        "fights { id name kill startTime endTime } } } }" % code
    )
    return gql(token, q)["reportData"]["report"]["fights"]


def fetch_master(token, code):
    q = (
        '{ reportData { report(code:"%s") { masterData { '
        "abilities { gameID name type } "
        "actors { id name type subType } } } } }" % code
    )
    md = gql(token, q)["reportData"]["report"]["masterData"]
    abilities = {str(a["gameID"]): a for a in md["abilities"]}
    actors = {str(a["id"]): a for a in md["actors"]}
    return abilities, actors


def fetch_combatantinfo(token, code, fid):
    q = (
        '{ reportData { report(code:"%s") { '
        "events(fightIDs:[%d], dataType: CombatantInfo, limit: 100) { data } } } }"
        % (code, fid)
    )
    return gql(token, q)["reportData"]["report"]["events"]["data"]


def fetch_deaths(token, code, fid):
    q = (
        '{ reportData { report(code:"%s") { '
        "events(fightIDs:[%d], dataType: Deaths, limit: 200) { data } } } }"
        % (code, fid)
    )
    return gql(token, q)["reportData"]["report"]["events"]["data"]


def fetch_damage_taken(token, code, fid, start, end):
    """Paginate all DamageTaken events in [start, end] via nextPageTimestamp."""
    events = []
    cursor = start
    while True:
        q = (
            '{ reportData { report(code:"%s") { '
            "events(fightIDs:[%d], dataType: DamageTaken, "
            "startTime: %d, endTime: %d, limit: 10000) "
            "{ data nextPageTimestamp } } } }" % (code, fid, cursor, end)
        )
        page = gql(token, q)["reportData"]["report"]["events"]
        events.extend(page["data"])
        nxt = page.get("nextPageTimestamp")
        if not nxt:
            break
        cursor = nxt
    return events


def fetch_debuffs(token, code, fid, start, end):
    """Paginate all Debuffs (status) events in [start, end] via nextPageTimestamp.

    Returns apply/remove/refresh/stack events; emit_debuffs pairs them into a
    per-player timeline with durations.
    """
    events = []
    cursor = start
    while True:
        q = (
            '{ reportData { report(code:"%s") { '
            "events(fightIDs:[%d], dataType: Debuffs, "
            "startTime: %d, endTime: %d, limit: 10000) "
            "{ data nextPageTimestamp } } } }" % (code, fid, cursor, end)
        )
        page = gql(token, q)["reportData"]["report"]["events"]
        events.extend(page["data"])
        nxt = page.get("nextPageTimestamp")
        if not nxt:
            break
        cursor = nxt
    return events


# --------------------------------------------------------------------------- #
# Decoding helpers
# --------------------------------------------------------------------------- #
def fmt_time(ts, start):
    """Milliseconds-from-report -> mm:ss relative to fight start."""
    sec = max(0, (ts - start)) // 1000
    return f"{sec // 60:01d}:{sec % 60:02d}"


def school_of(ability):
    """Damage school from ability.type. The API returns type as a string."""
    if not ability:
        return "unknown"
    try:
        t = int(ability.get("type"))
    except (TypeError, ValueError):
        return "unknown"
    return SCHOOL_BY_TYPE.get(t, "unknown")


def ability_name(abilities, gid):
    a = abilities.get(str(gid))
    return a["name"] if a else f"#{gid}"


def actor_name(actors, aid):
    a = actors.get(str(aid))
    return a["name"] if a else f"#{aid}"


def decode_buffs(abilities, buffs):
    """'1001191.1002604.' -> 'Galvanize, Kardia' (best-effort)."""
    if not buffs:
        return ""
    names = []
    for bid in str(buffs).split("."):
        bid = bid.strip()
        if bid:
            names.append(ability_name(abilities, bid))
    return ", ".join(names)


def mit_pct(multiplier):
    if multiplier is None:
        return "—"
    return f"{round((1 - multiplier) * 100)}%"


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def list_fights(fights):
    print("Fights in report:")
    for f in fights:
        dur = (f["endTime"] - f["startTime"]) // 1000
        tag = "KILL" if f["kill"] else "wipe"
        print(f"  [{f['id']:>3}] {f['name']}  ({tag}, {dur // 60}:{dur % 60:02d})")


def emit_debuffs(start, abilities, actors, debuffs, player_ids):
    """Per-player debuff timeline: failure markers + mechanic debuffs.

    Pairs each apply with its matching remove to compute a duration. Source is
    the actor that applied the status (usually the boss); correlate its
    timestamp with the damage log to attribute the triggering mechanic.
    """
    print("Debuffs on players (time | target | debuff | source | dur | stacks):")
    pending = {}   # (target, ability) -> open apply record
    records = []
    for e in sorted(debuffs, key=lambda x: x["timestamp"]):
        tgt = str(e.get("targetID"))
        if tgt not in player_ids:
            continue
        key = (tgt, str(e.get("abilityGameID")))
        typ = e.get("type")
        if typ == "applydebuff" or (typ in ("refreshdebuff", "applydebuffstack")
                                    and key not in pending):
            rec = {"ts": e["timestamp"], "target": e.get("targetID"),
                   "ability": e.get("abilityGameID"), "source": e.get("sourceID"),
                   "stacks": e.get("stack"), "remove_ts": None}
            records.append(rec)
            pending[key] = rec
        elif typ in ("refreshdebuff", "applydebuffstack"):
            if e.get("stack") is not None:
                pending[key]["stacks"] = e.get("stack")
        elif typ == "removedebuff":
            rec = pending.pop(key, None)
            if rec is not None:
                rec["remove_ts"] = e["timestamp"]

    if not records:
        print("  (none on players)")
    for r in records:
        dur = f"{round((r['remove_ts'] - r['ts']) / 1000)}s" if r["remove_ts"] else "?"
        stacks = f"x{r['stacks']}" if r.get("stacks") else ""
        print(
            f"  {fmt_time(r['ts'], start)} | "
            f"{actor_name(actors, r['target']):<18} | "
            f"{ability_name(abilities, r['ability']):<26} | "
            f"{actor_name(actors, r['source']):<18} | "
            f"{dur:>4} | {stacks}"
        )
    print()


def emit_fight(code, fight, abilities, actors, combatant_info, deaths, damage, debuffs):
    start, end = fight["startTime"], fight["endTime"]
    dur = (end - start) // 1000

    print(f"=== FFLogs {code} - Fight {fight['id']}: {fight['name']} ===")
    print(f"Result: {'KILL' if fight['kill'] else 'wipe'}   Duration: {dur // 60}:{dur % 60:02d}\n")

    # --- composition: the actual fight participants (one CombatantInfo row each) ---
    print("Composition (job | name | vitality[HP proxy]):")
    for c in sorted(combatant_info,
                    key=lambda c: actors.get(str(c["sourceID"]), {}).get("subType", "")):
        actor = actors.get(str(c["sourceID"]), {})
        vit = c.get("vitality")
        vit_s = f"{vit:,}" if isinstance(vit, int) else "?"
        print(f"  {actor.get('subType', '?'):<12} {actor.get('name', '?'):<20} vit {vit_s}")
    print()

    # --- deaths ---
    print(f"Deaths ({len(deaths)}):")
    if not deaths:
        print("  (none)")
    for d in deaths:
        who = actor_name(actors, d["targetID"])
        killer = ability_name(abilities, d.get("killingAbilityGameID", 0))
        print(f"  {fmt_time(d['timestamp'], start)}  {who:<20} killed by {killer}")
    print()

    player_ids = {str(c["sourceID"]) for c in combatant_info}

    # --- debuffs on players: failure markers + mechanic debuffs ---
    emit_debuffs(start, abilities, actors, debuffs, player_ids)

    # --- damage taken: only hits on the fight's participants ---
    hits = [e for e in damage if str(e.get("targetID")) in player_ids]

    # grouped summary by ability
    print("Damage taken - summary by ability (school | hits | max unmit):")
    groups = {}
    for e in hits:
        gid = str(e.get("abilityGameID"))
        g = groups.setdefault(gid, {"hits": 0, "max_unmit": 0})
        g["hits"] += 1
        g["max_unmit"] = max(g["max_unmit"], e.get("unmitigatedAmount") or 0)
    for gid, g in sorted(groups.items(), key=lambda kv: kv[1]["max_unmit"], reverse=True):
        ab = abilities.get(gid)
        print(
            f"  {ability_name(abilities, gid):<28} "
            f"{school_of(ab):<8} hits {g['hits']:>3}  max unmit {g['max_unmit']:>10,}"
        )
    print()

    # full decoded event log
    print("Damage taken - full event log (time | target | ability | school | unmit | took | mit | buffs):")
    for e in sorted(hits, key=lambda x: x["timestamp"]):
        ab = abilities.get(str(e.get("abilityGameID")))
        print(
            f"  {fmt_time(e['timestamp'], start)} | "
            f"{actor_name(actors, e['targetID']):<18} | "
            f"{ability_name(abilities, e.get('abilityGameID')):<26} | "
            f"{school_of(ab):<8} | "
            f"{(e.get('unmitigatedAmount') or 0):>9,} | "
            f"{(e.get('amount') or 0):>9,} | "
            f"{mit_pct(e.get('multiplier')):>4} | "
            f"{decode_buffs(abilities, e.get('buffs'))}"
        )


# --------------------------------------------------------------------------- #
def main():
    # Emit UTF-8 regardless of the Windows console code page (output is paste-ready text).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(description="Fetch & decode an FFLogs fight.")
    ap.add_argument("report_code")
    ap.add_argument("fight_id", nargs="?", type=int)
    args = ap.parse_args()

    load_env()
    token = get_token()

    fights = fetch_fights(token, args.report_code)
    if args.fight_id is None:
        list_fights(fights)
        return

    fight = next((f for f in fights if f["id"] == args.fight_id), None)
    if fight is None:
        sys.exit(f"ERROR: fight {args.fight_id} not found in report.")

    abilities, actors = fetch_master(token, args.report_code)
    combatant_info = fetch_combatantinfo(token, args.report_code, args.fight_id)
    deaths = fetch_deaths(token, args.report_code, args.fight_id)
    damage = fetch_damage_taken(
        token, args.report_code, args.fight_id, fight["startTime"], fight["endTime"]
    )
    debuffs = fetch_debuffs(
        token, args.report_code, args.fight_id, fight["startTime"], fight["endTime"]
    )
    emit_fight(args.report_code, fight, abilities, actors,
               combatant_info, deaths, damage, debuffs)


if __name__ == "__main__":
    main()
