#!/usr/bin/env python3
"""
Fetch a raidplan.io plan and emit a paste-ready, per-step text digest for the
analysis agent.

Usage:
    python scripts/fetch_raidplan.py <PLAN_URL_OR_CODE>

Examples:
    python scripts/fetch_raidplan.py https://raidplan.io/plan/UATE__aDcw1-bgVv
    python scripts/fetch_raidplan.py UATE__aDcw1-bgVv

raidplan.io is a Next.js app. The complete plan ships *inside the page* as JSON
in <script id="__NEXT_DATA__">; there is no public REST endpoint (the obvious
/api/plan/<code> paths 404). So we GET the plan page, pull that one script blob,
and read props.pageProps._plan. Stdlib only -- no pip, mirrors fetch_fight.py.

What a plan is (version 2):
  - A flat list of `nodes`, each tagged with a single integer `meta.step`. A
    "step" is one timeline snapshot of the fight; we group by it and render the
    steps in order. The arena diagram is one node (type "arena"); everything
    else is drawn on top of it.
  - Node `type`s we decode:
      arena    background field (defines the coordinate frame: center + radius)
      ability  an AoE telegraph; attr.abilityId is the shape (ff-circle puddle,
               ff-pie / ff-wedge cone, ff-stack stack, ff-boss enemy marker)
      marker   a token, usually a player job icon (attr.asset
               "game/ffxiv/job/pld.png" -> PLD) or a role icon
      itext    a free text label -- these carry the strategy callouts
      arrow    a movement / pointer arrow (meta.angle = facing)
      circle / rect   a freeform zone or annotation
      waypoint a point on a movement path

Positions are raw canvas pixels. Players reason in FFXIV terms, so we convert
every position to a clock face + 8-wind compass + a coarse radius band
(center/mid/edge), measured from the arena node's center. Screen-y grows
downward, so North is -y; bearings are clockwise from North, matching how these
tools and callouts ("go NE", "12 o'clock") are spoken. We report the geometry we
can stand behind (shape, position, facing, relative size) and do NOT invent AoE
arc widths or damage values -- the plan does not encode those.
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from urllib import request, error

PLAN_URL = "https://raidplan.io/plan/"
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)

# abilityId -> human-readable shape. Extend as new ids appear.
ABILITY_SHAPE = {
    "ff-circle": "circle AoE",
    "ff-pie": "cone/pie AoE",
    "ff-wedge": "wedge/cone AoE",
    "ff-stack": "stack marker",
    "ff-boss": "boss/enemy marker",
    "ff-donut": "donut AoE",
    "ff-line": "line AoE",
    "ff-knockback": "knockback",
}

COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


# --------------------------------------------------------------------------- #
# Fetch + extract
# --------------------------------------------------------------------------- #
def extract_code(arg):
    """Accept a full /plan/<code> URL or a bare code."""
    arg = arg.strip()
    if "raidplan.io" in arg:
        m = re.search(r"/plan/([A-Za-z0-9_\-]+)", arg)
        if not m:
            sys.exit(f"ERROR: could not find a plan code in URL: {arg}")
        return m.group(1)
    return arg


def fetch_plan(code):
    url = PLAN_URL + code
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0 (raidplan-digest)"})
    try:
        with request.urlopen(req) as resp:
            html = resp.read().decode("utf-8", "replace")
    except error.HTTPError as exc:
        sys.exit(f"ERROR: fetch failed ({exc.code}) for {url}")
    except error.URLError as exc:
        sys.exit(f"ERROR: fetch failed ({exc.reason}) for {url}")
    m = NEXT_DATA_RE.search(html)
    if not m:
        sys.exit("ERROR: __NEXT_DATA__ not found -- page layout may have changed.")
    data = json.loads(m.group(1))
    try:
        return data["props"]["pageProps"]["_plan"]
    except (KeyError, TypeError):
        sys.exit("ERROR: _plan not present -- plan may be private or the code is wrong.")


# --------------------------------------------------------------------------- #
# Geometry -> FFXIV-native description
# --------------------------------------------------------------------------- #
def arena_frame(nodes):
    """Return (cx, cy, radius) from the arena node, with a sane fallback."""
    for n in nodes:
        if n.get("type") == "arena":
            m = n["meta"]
            cx, cy = m["pos"]["x"], m["pos"]["y"]
            scale = m.get("scale", {}).get("x", 1) or 1
            radius = (m["size"]["w"] / 2) * scale
            return cx, cy, radius
    return 600.0, 337.5, 300.0  # observed default field


def bearing_to_clock(deg):
    """Clockwise-from-North degrees -> 1..12 clock hour."""
    hour = round(deg / 30.0) % 12
    return 12 if hour == 0 else hour


def describe_pos(pos, frame):
    cx, cy, radius = frame
    dx = pos["x"] - cx
    dy = pos["y"] - cy
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return "center"
    bearing = (math.degrees(math.atan2(dx, -dy))) % 360  # 0=N, CW
    comp = COMPASS[round(bearing / 45.0) % 8]
    clock = bearing_to_clock(bearing)
    frac = dist / radius if radius else 0
    band = "center" if frac < 0.18 else "mid" if frac < 0.66 else "edge"
    return f"{comp} {clock}o'clock {band} (r={frac:.2f})"


def facing(deg):
    """meta.angle (0=up/N, clockwise) -> compass facing."""
    return COMPASS[round((deg % 360) / 45.0) % 8]


def job_from_asset(asset):
    if not asset:
        return None
    name = asset.rsplit("/", 1)[-1].replace(".png", "")
    if name.startswith("role_"):
        return name[5:].capitalize() + " (role)"
    return name.upper()


def rel_size(node):
    """Coarse size cue from scale, when it departs from 1."""
    s = node["meta"].get("scale", {}).get("x", 1) or 1
    if s >= 1.6:
        return " ~large"
    if s <= 0.6:
        return " ~small"
    return ""


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def render(plan):
    nodes = plan["nodes"]
    frame = arena_frame(nodes)
    out = []
    out.append(f"PLAN: {plan.get('name', '(unnamed)')}")
    out.append(f"code: {plan.get('code')}  raid: {plan.get('raid')}  "
               f"boss: {plan.get('boss')}  steps: {plan.get('steps')}")
    if plan.get("time_saved"):
        out.append(f"last saved: {plan['time_saved']}")
    notes = (plan.get("notes_raw") or "").strip()
    if notes:
        out.append("\nNOTES:")
        for line in notes.splitlines():
            out.append("  " + line)
    out.append(f"\nCoordinate frame: arena center, clockwise-from-North bearings; "
               f"radius band center<0.18<mid<0.66<edge.")

    by_step = defaultdict(list)
    for n in nodes:
        by_step[n["meta"].get("step", 0)].append(n)

    for step in sorted(by_step):
        items = by_step[step]
        out.append("\n" + "=" * 60)
        out.append(f"STEP {step}  ({len(items)} elements)")
        out.append("=" * 60)

        labels, abilities, players, arrows, zones, other = [], [], [], [], [], []
        for n in items:
            t = n["type"]
            if t == "arena":
                continue
            elif t == "itext":
                labels.append(n)
            elif t == "ability":
                abilities.append(n)
            elif t == "marker":
                players.append(n)
            elif t == "arrow":
                arrows.append(n)
            elif t in ("circle", "rect"):
                zones.append(n)
            else:
                other.append(n)

        if labels:
            out.append("\n  Labels / callouts:")
            for n in labels:
                txt = (n["attr"].get("text") or "").replace("\n", " / ").strip()
                if txt:
                    out.append(f"    - \"{txt}\"  @ {describe_pos(n['meta']['pos'], frame)}")

        if abilities:
            out.append("\n  AoEs / mechanics:")
            for n in abilities:
                aid = n["attr"].get("abilityId", "?")
                shape = ABILITY_SHAPE.get(aid, aid)
                line = f"    - {shape}{rel_size(n)} @ {describe_pos(n['meta']['pos'], frame)}"
                ang = n["meta"].get("angle", 0)
                if aid in ("ff-pie", "ff-wedge", "ff-line") and ang:
                    line += f", facing {facing(ang)} ({ang:.0f}deg)"
                out.append(line)

        if players:
            out.append("\n  Tokens / players:")
            for n in players:
                job = job_from_asset(n["attr"].get("asset"))
                tag = job or (n["attr"].get("text") or "marker")
                out.append(f"    - {tag} @ {describe_pos(n['meta']['pos'], frame)}")

        if zones:
            out.append("\n  Zones / shapes:")
            for n in zones:
                col = n["attr"].get("fill") or n["attr"].get("bgColor") or ""
                out.append(f"    - {n['type']}{rel_size(n)} {col} @ "
                           f"{describe_pos(n['meta']['pos'], frame)}")

        if arrows:
            out.append("\n  Arrows (movement):")
            for n in arrows:
                ang = n["meta"].get("angle", 0)
                out.append(f"    - arrow from {describe_pos(n['meta']['pos'], frame)} "
                           f"pointing {facing(ang)} ({ang:.0f}deg)")

        if other:
            out.append("\n  Other:")
            counts = defaultdict(int)
            for n in other:
                counts[n["type"]] += 1
            for t, c in sorted(counts.items()):
                out.append(f"    - {c}x {t}")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="raidplan.io plan -> per-step text digest")
    ap.add_argument("plan", help="raidplan.io plan URL or bare code")
    args = ap.parse_args()
    code = extract_code(args.plan)
    plan = fetch_plan(code)
    print(render(plan))


if __name__ == "__main__":
    main()
