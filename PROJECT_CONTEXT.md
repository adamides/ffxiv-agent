# FFXIV Mitigation & Mechanic-Solving Agent — Project State & Roadmap

This document tracks project state, architecture, and the build roadmap. Authoring guidance (FFXIV corrections, file-design principles, templates) lives in [CLAUDE.md](CLAUDE.md); the glossary lives in [CONTEXT.md](CONTEXT.md).

---

## Project goal

Build a custom agent that reads live logs from FFLogs and helps with:

1. **Mitigation analysis** — diagnose mit gaps, identify failures, and (eventually) suggest mit plans
2. **Mechanic solving** — analyze prog logs to help figure out unsolved fight mechanics

**Primary user:** the project owner, for personal use after raid nights. May share output with their static. The **knowledge layer + scripts + docs are now shared publicly** as a clone-and-tweak hobby project (see [Sharing & repo](#sharing--repo)); the *analysis* is still run per-user (each person brings their own FFLogs creds and keeps their own sheets).

**Current prog target:** Dancing Mad Ultimate (the new Ultimate featuring Kefka as the boss).

---

## Workflow & PoC scope

The PoC is intentionally minimal to validate feasibility before deeper investment.

**Interaction shape:** Conversational, in Claude.ai itself. No custom UI required.

**Workflow per session:**
1. User provides an FFLogs report URL (and optionally a specific fight ID)
2. A data-fetching script pulls fight data and decodes it into human-readable form
3. User pastes the decoded output into Claude.ai with the knowledge layer as system prompt
4. Claude responds with a **light structured summary first** (pulls, durations, deaths, top damage abilities) — NOT a full analysis
5. User drills in conversationally: "why did X die?", "was Reprisal up for the second tankbuster?", etc.
6. Deeper analysis happens on demand, not upfront

**Mode evolution:** Start with "summarize then investigate" (B). Likely evolves into explicit modes (quick summary vs deep mechanic investigation) once usage patterns become clear. Don't design for that yet.

---

## Architecture decisions

### Runtime / deployment (decided)

The analysis agent runs **in Claude Code, single-operator** (the project owner). Invoked with **`/ffxivanalyze <report-code> [fight-id]`** (`.claude/commands/ffxivanalyze.md`): it loads `knowledge/AGENT.md` + the knowledge layer, runs `scripts/fetch_fight.py` itself (no manual paste), and runs the summary-then-drill-in workflow in the main conversation. Fight ID is optional — omit it to list the whole raid night's pulls and pick which to analyze; cross-pull questions fetch additional pulls on demand. Decoded dumps land in gitignored `.fights/`.

- **Why not paste-into-claude.ai:** that model means re-pasting the persona + knowledge layer every session. A claude.ai **Project** (custom instructions + project knowledge, optionally GitHub-synced) would fix the re-paste but still can't run the fetcher, and live multi-user sharing needs a Team plan (everyone with their own account/usage). For a single operator the run-it-here path is lowest-friction. `knowledge/AGENT.md` stays portable, so dropping it into a claude.ai Project later remains an option for sharing.
- **Sharing model:** share *output* (post findings to the static), not *access*. No accounts/tokens needed for consumers.

### Tooling

- **Interface:** Claude Code, via the `/ffxivanalyze` slash command (no UI to build; superseded the earlier "claude.ai chat" plan)
- **Data pipeline:** Script that queries FFLogs GraphQL API and formats data as text for paste-in
- **Reasoning engine:** Claude Sonnet 4.6 at Medium effort. Only upgrade to Opus if Sonnet fails on real analysis — quality of knowledge layer matters more than model tier.
- **Thinking mode:** Not needed for this work.
- **Development environment:** VSCode + Claude Code CLI (transitioning from claude.ai chat at this handoff point).

### Why not other options

- **GitHub Copilot:** Wrong tool. Copilot is a coding assistant, not an agent-building platform.
- **Claude Desktop with MCP filesystem:** Viable, but Claude Code is the cleaner fit for this incremental authoring + scripting workflow.
- **Custom UI / web app:** Premature. Validate the agent's reasoning quality first.
- **Pro subscription:** Already on a paid tier; Pro doesn't unlock custom skills. The "skills" feature seen in chat is an internal Anthropic backend — not user-installable.

---

## Sharing & repo

Decided 2026-06 in a grill session, then executed (git repo created, first commit, pushed to GitHub).

- **Visibility — public GitHub.** It's a personal tool but meant to be clone-and-tweak shareable, and fork+PR needs public. **Consequence handled:** the fight catalog originally hardcoded the static's real character names tied to deaths/performance — these were **anonymized to role labels** (MT/OT/SGE/DRG/…) before the first commit. This also realigned the catalog with the project's own comp-agnostic ethos. Keep catalogs anonymized.
- **License — MIT, whole repo.** Owner doesn't care about attribution or "theft" (a fun project), so the simplest, most-recognized permissive license. A license is still required for "clone and contribute back" to be legally clean. The repo is mostly prose; MIT is a software license but covers it fine for these purposes. No dual code/prose license.
- **Contribution model — fork + PR**, documented in the README. **Factual FFXIV corrections go through an Issue first** (with a citation), since correctness is debatable and the project's whole history is correcting FFXIV facts. No separate `CONTRIBUTING.md` — a README section suffices.
- **Google Sheets boundary — optional, per-user.** The mit-plan-to-sheet workflow uses a service-account-backed [`mcp-google-sheets`](https://github.com/xing5/mcp-google-sheets) server pointed at the owner's *private* "AI Mitty" sheet; collaborators can't access it. So the shareable product is the **knowledge layer + scripts + docs**; each user runs their own analysis and keeps their own sheets. README frames Sheets as an optional add-on; `.mcp.json.example` is the genericized template.

**Repo-hygiene landmines handled at first commit:**
- `.env` (live FFLogs creds) — already gitignored. ✅
- `.mcp.json` (hardcoded local paths + a private service-account key *path*, not the key itself) — **now gitignored**; shipped `.mcp.json.example` instead.
- The service-account key file lives outside the repo (`~/.secrets/`) and was never tracked. ✅
- Community raid-guide PDF (`UMAD P1_ Merry Go Round.pdf`, third-party IP) — **gitignored** (`*.pdf`), not redistributed; the catalog still *cites* it by name, which is fine.
- `scripts/fetch_fight.py` reads creds from env only — clean.

---

## FFLogs API setup

The FFLogs GraphQL API is the data source. Credentials and access have been set up:

- **Client created:** named "mitigation-agent" (or similar) on https://www.fflogs.com/api/clients/
- **Auth flow:** Client credentials (NOT PKCE — the script can store the secret locally)
- **Redirect URL:** `http://localhost` (placeholder — the form required a value but the redirect flow is unused)
- **Public Client checkbox:** unchecked
- **Token endpoint:** `https://www.fflogs.com/oauth/token` with grant_type=client_credentials
- **Query endpoint:** `https://www.fflogs.com/api/v2/client`
- **Credentials:** stored as environment variables `FFLOGS_CLIENT_ID` and `FFLOGS_CLIENT_SECRET`. The original credentials shared in the chat session were instructed to be regenerated.

### Confirmed working queries

**1. List fights in a report:**
```graphql
{ reportData { report(code: "REPORT_CODE") { fights { id name kill startTime endTime } } } }
```

**2. Damage events for a specific fight:**
```graphql
{ reportData { report(code: "REPORT_CODE") { events(fightIDs: [N], dataType: DamageTaken, limit: 20) { data nextPageTimestamp } } } }
```

**3. Master data (ability & actor name lookups):**
```graphql
{ reportData { report(code: "REPORT_CODE") { masterData { abilities { gameID name } actors { id name type } } } } }
```

### Key data fields discovered

In damage events (verified against fight 6 of the test report, 2026-06):
- `timestamp` — milliseconds from report start
- `abilityGameID` — resolves to ability name via masterData
- `sourceID` / `targetID` — resolve to actor names via masterData
- `amount` vs `unmitigatedAmount` — actual vs theoretical damage
- `multiplier` — combined mit multiplier (e.g., 0.8 = 20% mitigated)
- `buffs` — dot-separated list of buff IDs active on target at hit time
- `type` — **event category** (`"calculateddamage"` / `"damage"`), NOT the damage school
- `hitType`, `packetID`, `fight` — also present
- ⚠️ `mitigated` / `absorbed` / `blocked` were **not** present in the fight-6 DamageTaken sample — they may appear only when nonzero or via a different dataType. Don't assume they're always there.

**Damage school is on the ability, not the event.** Join `abilityGameID` → `masterData.abilities[].type`:
- `type=128` → **physical**, `type=1024` → **magical** (confirmed against real incoming damage)
- `type=8` healing/shields, `type=1` utility/non-combat (not damage)
- `type=32 / 64 / 256` → small unconfirmed buckets (possibly unaspected/darkness/DoT/special); none hit players in fight 6. Script should pass these through as raw `type=N` / "unknown school" rather than guess.
- Script requirement: emit a decoded `school` column (physical / magical / unknown) per damage row.

### Test report used during this session

Report code `AqCGxhZgX8N6W9Rm` — a Dancing Mad Ultimate prog session, 9 wipes. Fight 6 was the longest pull (~97s) and is the working example for design discussions.

---

## Knowledge layer architecture

The agent's reasoning quality depends almost entirely on a well-structured knowledge layer. Decided structure:

```
knowledge/
├── AGENT.md              # the analysis agent's persona/behavior layer (selectable-mode style)
├── fundamentals.md       # cross-cutting rules of the game
├── jobs.md               # all jobs' mitigation/defensive toolkits with tags
├── primitives.md         # mechanic concept vocabulary (towers, baits, etc.)
├── fights/
│   └── dancing-mad-ultimate.md   # observed catalog, NOT a mit plan
└── reference-guides/
    ├── current-savage-tier.md    # most recent savage tier (AAC tier in progress)
    ├── fru.md                    # Futures Rewritten reference
    └── top.md                    # The Omega Protocol reference
```

**`AGENT.md` is the behavioral layer, not substrate.** It's the analysis-agent counterpart to `CLAUDE.md` (which instructs the build agent). It defines *who the agent is, how it responds (light summary → drill-in), and the load-bearing reasoning discipline* — and **references** the other knowledge files rather than restating any FFXIV facts (DRY). It sits at the **top** of the assembled system prompt.

### Loading strategy

Sessions assemble a system prompt from:
- `AGENT.md` (always — the persona/behavior header, loaded first)
- `fundamentals.md` (always)
- `primitives.md` (always)
- `jobs.md` (always)
- The relevant `fights/<current-fight>.md` (per session)
- `reference-guides/` files for current savage tier + last two Ultimates (default)
- Older Ultimates loaded selectively if a mechanic echoes one

### Reference guides

Sourced from community resources (The Balance Discord, FFLogs articles, Hector Hectorson's writeups, raid.zone, etc.). The user will manually curate — copy mechanic descriptions, strip personality/memes, tag with source and patch version. Not auto-fetched.

_File-design principles moved to [CLAUDE.md](CLAUDE.md)._

---

## Party composition convention

The agent **reads the actual comp from each log** rather than assuming a fixed comp. Typical FFXIV statics run:

- 2 tanks
- 1 regen healer (WHM or AST)
- 1 barrier healer (SCH or SGE)
- 2 melee DPS
- 1 phys ranged
- 1 magical ranged

Common variant: **double shield (SCH + SGE)**. ⚠️ The prior session asserted "SCH's Galvanize overwrites SGE's Eukrasian Prognosis/Diagnosis" — this is **unverified and likely imprecise** (the real interaction may be the narrower "enhanced Eukrasian Diagnosis shield is suppressed when a barrier already exists," not a blanket overwrite). **Deferred** — not authored into `fundamentals.md`. Verify against The Balance / patch notes before writing it, and only if it proves load-bearing for analysis.

---

## Primitives — full target list

14 primitives identified for full vocabulary coverage. Authored lazily — only when first encountered in real prog data, to avoid speculative writing.

**Authored (day-one set):**
1. ✅ **Tankbuster** — drafted
2. ✅ **Raidwide** — drafted
3. ✅ **Tower** — drafted
4. ✅ **Gaze** — drafted

**Pending (author as encountered):**
5. Stacks (whole-party, partner, role-stack variants)
6. Spreads (full party only — "melee in / ranged out" is a separate primitive, not a spread)
7. Role positioning (melee in / ranged out splits)
8. Baits (AOE bait variants)
9. Knockback (directional, positional, with/without immunity)
10. Proteans (fixed-angle line AOEs, A3S-pattern)
11. Tethers (bait, share, break)
12. Hazards / anti-soak zones (orbs, lines, puddles to avoid)
13. Debuff resolutions (vuln stacks, passable debuffs, expiring debuffs)
14. Enmity-based targeting (#1/#2 threat patterns — Revolting Ruin III is an example)

_Primitive entry template and the classify-by-outcome principle moved to [CLAUDE.md](CLAUDE.md)._

---

## Fundamentals — pending entries

Started with vulnerability debuffs. All originally-planned entries are now authored.

**Deferred (not authored):**
- **Shield overwrite rules** — Galvanize vs Eukrasian Prognosis/Diagnosis. Prior claim unverified/likely imprecise; low load-bearing for analysis. Revisit only if it matters in real logs (verify against The Balance first).

### Already authored in fundamentals.md

- **Vulnerability debuffs** — the most important entry. Key points:
  - In high-end content, vulns are essentially lethal on the next major hit
  - Treat them qualitatively ("player cannot take another major hit"), not quantitatively
  - Duration varies — always check actual duration in the log
  - Don't model stack counts — the qualitative outcome is what matters
  - Vulns can be applied **by design** (tankbuster swaps, intended stacks, soaks) — vuln ≠ automatic failure
- **Damage Down** — the unambiguous failure marker (vulns are ambiguous; Damage Down is essentially never by-design). Key points:
  - Marks a **non-fatal** failure — the "got away with it" detector that surfaces survived mistakes
  - **Not** a survivability factor (reduces damage *dealt*) — never cite it as a contributing cause of a death
  - Marks consequence-holder, not cause — party-wide Damage Down can trace to one player (shared- vs. individual-punishment models; needs the source ability + mechanic type to attribute)
  - Distinct from Weakness/Brink of Death (post-raise; disambiguate by magnitude ~25/50% vs 60%+ and duration ~100s)
- **The 8-player budget** — content is tuned for exactly 8 live players. Key points:
  - General body-allocation invariant (towers, stacks, tethers, baits) — not tower-specific
  - Simultaneous body requirements sum to ≤8
  - Available pool = 8 − dead − vuln'd (Damage Down does NOT disqualify)
  - Deaths cascade: a death breaks the budget downstream → budget-failure vs positioning-failure fork
  - Tower primitive trimmed to reference this entry (DRY)
- **Damage types (physical vs magical)** — school matters because some mit is school-locked. Key points:
  - Recognition: school is on the ability (`masterData.abilities[].type`: 128=physical, 1024=magical), NOT the event — script emits a `school` column
  - Boss-applied damage-down (all reduce party damage): Reprisal −10% all, Dismantle −10% all, Feint −10%phys/−5%mag, Addle −10%mag/−5%phys
  - Party damage-taken: Magick Barrier −10% magic only (the only genuinely school-locked tool)
  - Diagnostic value: judge whether mit *matched the school* (fight 6 is ~all magical → Addle/Magick Barrier > Feint)
- **How mitigation stacks** — multiplicative, and read-don't-compute. Key points:
  - Multiplicative not additive (0.9×0.9×0.9≈27%, not 30%) → diminishing returns
  - The event's `multiplier` field already gives the realized combined %; attribute it via `buffs`, don't recompute
  - Shields are a separate axis (`absorbed`), NOT in `multiplier`
  - Mit-gap detection (multiplier ≈1.0 on designed damage) gated on designed-vs-failure: never recommend mit on a failure/overkill (e.g. Gravitational Explosion 1.4M)
  - Prescriptive "cooldown X would've saved you" deferred until HP + cooldown-availability tracking exist

---

_Authoring conventions, FFXIV corrections, and the critical-facts list moved to [CLAUDE.md](CLAUDE.md). The FFXIV facts themselves are now captured in the `knowledge/` files._

---

## Build order

### Completed
- [x] Architecture decisions
- [x] Knowledge layer structure
- [x] FFLogs API client setup
- [x] Test queries confirmed working
- [x] `primitives.md` intro + 4 entries (tankbusters, raidwides, towers, gazes)
- [x] `fundamentals.md` — intro + vulnerability debuffs, Damage Down, 8-player budget, damage types, mit stacking (shield overwrite deferred)
- [x] Doc restructure — `CLAUDE.md` (authoring guidance), `CONTEXT.md` (glossary), `PROJECT_CONTEXT.md` (state/roadmap)
- [x] Verified damage-school recognition path against live API (`ability.type`: 128=physical, 1024=magical)
- [x] **`fetch_fight.py`** — Python 3 (stdlib-only) FFLogs fetcher/decoder. Reads `.env`, lists fights, and for a fight emits paste-ready text: composition (from CombatantInfo), deaths (with killing ability), damage-taken summary + full event log with decoded school, mit%, and decoded buff names. Validated against fight 6. Lives in `scripts/`. Usage: `py scripts/fetch_fight.py <REPORT_CODE> [FIGHT_ID]` (redirect `> fight.txt` for pasting). Resolves `.env` relative to the repo root (via `__file__`), so it can be launched from any directory.
  - Known limitations: max HP not available (vitality only sometimes populated — HP proxy weak); `ability.type` returned as a string (handled); rare type codes (32/64/256) pass through as "unknown" school.

#### Validated findings from fight 6 (seeds for the fight file)
- Boss damage is almost entirely **magical**; auto-attacks are physical.
- **Revolting Ruin III** = magical cleave TB, two ability IDs, hits #1/#2 enmity; PLD survived at ~69% mit (stacked tank CDs).
- **Gravitational Explosion** (1:31) = ~1.5M unmitigated to all 8, ~10% mit → 8 deaths. Failure-overkill, not designed damage (do NOT diagnose as a mit gap). This was the wipe cause.

### Next steps (in suggested order)
1. ~~**`jobs.md`**~~ — **COMPLETE.** All 19 jobs across all five role groups authored from the LIVE job guide: 4 tanks (PLD/DRK/WAR/GNB), 4 healers (SGE/SCH/WHM/AST), 6 melee (MNK/DRG/NIN/SAM/RPR/VPR), 3 phys-ranged (MCH/DNC/BRD), 4 casters (BLM/SMN/RDM/PCT), plus role-action blocks for each role group. Principle held throughout: author by complete role, always fetch live + quote, never from memory.
   - **Role-block decisions:** melee block = **Feint only**; phys-ranged block = no party-mit role action (job-specific); caster block = Addle. Knockback tools are cross-role and authored once: **Arm's Length** under Tank (tank/melee/phys-ranged), **Surecast** under Healer (healer/caster) — referenced via light-touch cross-refs, not a separate shared section.
   - **Verified findings that corrected memory (guide wins):** phys-ranged party mits (Tactician/Shield Samba/Troubadour) are **−15%, not −10%**; **RDM Embolden is no longer mit** (it's a party damage-*dealt* buff now) — excluded; BLM Manaward now absorbs **all** damage, not magic-only. DRG and VPR have **no job-specific PvE survival cooldown** (stub entries). PvP actions excluded throughout. Warden's Paean tagged `cleanse` (its "barrier" absorbs a debuff, not damage).
   - **Unverified, low-risk to fix later:** AST card/Intersection status names (`The Bole`, `The Spire`, Celestial Intersection's barrier status) were authored from inference, not confirmed against a log.
   - Tank role actions: Rampart from guide; Reprisal/Arm's Length from memory — verify when convenient.
   - Shield-overwrite (SCH `Galvanize` vs SGE `Eukrasian Prognosis`) still deferred — but they're *different statuses*, so the old "overwrite" claim is likely wrong (they coexist). Resolve/drop when it actually appears in a log.
2. **Populate `fights/dancing-mad-ultimate.md`** — feed real log data through the script, document mechanics as discovered, using "Observed / Resolution / Open questions" structure.
   - ⚠️ **Pick a good log first.** The `AqCGxhZgX8N6W9Rm` test report was an arbitrary pull used only to validate the script — *not* a representative or far-progged session. Before authoring the catalog, select a solid prog log (ideally a long, clean pull that reaches deep into the fight). The user will provide the report code (and fight ID).
   - `knowledge/fights/` and `knowledge/reference-guides/` do **not exist yet** — create lazily when authoring begins.
   - The fetcher can be run directly in Claude Code (`py scripts/fetch_fight.py <CODE> [FIGHT_ID]`) using the repo `.env`; best done at the start of a fresh session once the log is chosen.
3. **Curate reference guides** — pull from The Balance, Hector, raid.zone for FRU, TOP, current savage tier
4. **Lazy-author remaining 10 primitives** as encountered in real logs

### Open questions for next session

- ~~Whether to set up a GitHub repo immediately~~ **RESOLVED (2026-06): public GitHub repo, MIT, fork+PR.** See [Sharing & repo](#sharing--repo).
- How to handle private logs if needed (currently scoped to public only)
- ~~**Does the pipeline have access to player max HP per hit?**~~ **RESOLVED (2026-06, probed `XnWJp61MzhGkFtBc` fight 37):** no. DamageTaken events carry `absorbed`/`mitigated`/`blocked` but **no `hitPoints`/`maxHitPoints`**; the `Resources` dataType returns 0 events and its graph series is empty; CombatantInfo `vitality` is mostly null. **But** the killing hit carries `overkill`, and on that hit `amount` ≈ the victim's remaining HP — so for **deaths** the EHP gap is known directly (no max HP needed); only *survived*-hit HP and the top-off fill-state hedge remain blocked. See `fundamentals.md` → death counterfactuals.
- ~~**Cooldown-availability tracking**~~ **RESOLVED (2026-06):** not a pipeline gap — availability is *derived* (all cooldowns up at pull start + each use event + its `jobs.md` recast). The agent may now assert "cooldown X was up and unused." Formalized as the two-mode split + recast-feasibility check in `fundamentals.md` → Cooldown Economy & Planning Mode. Remaining soft spot: gauge-gated tools (Addersgall/Aetherflow/Oath/MP) are only approximable; rotation-fed gauges aren't derivable from mit-only data.

---

## Glossary

Moved to [CONTEXT.md](CONTEXT.md) — the project's glossary-only doc. Canonical FFXIV mechanic definitions live in `knowledge/primitives.md` and `knowledge/fundamentals.md`.

