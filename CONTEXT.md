# FFXIV Mitigation & Mechanic-Solving Agent

Shared vocabulary for the project. This is a **glossary only** — the canonical, agent-facing definitions of FFXIV mechanics live in [primitives.md](knowledge/primitives.md) and [fundamentals.md](knowledge/fundamentals.md). Entries here stay terse and point there. Project state, decisions, and build order live in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Mechanic primitives

Canonical definitions in [primitives.md](knowledge/primitives.md).

**Tankbuster**:
Heavy damage targeted at a tank, designed to require tank cooldowns.

**Cleave tankbuster**:
A tankbuster that hits multiple targets in enmity order (e.g. #1 then #2). Looks like a raidwide by magnitude but only hits specific targets.

**Shared tankbuster**:
A tankbuster requiring both tanks stacked to split the damage.

**Raidwide**:
Damage that hits the entire party and is *designed to be taken*, not avoided.
_Avoid_: AOE (too generic)

**Tower**:
A ground AOE requiring one or more soakers; unsoaked, it damages the whole party. A positioning mechanic (body-allocation). Whether the soak needs [[Mit]] is a *separate, damage-driven* question — being positional neither forbids nor requires mit.

**Gaze**:
A mechanic punishing players facing the source at snapshot. Resolved by facing away. Player facing is not in the log — gaze analysis is always post-mortem from the applied debuff.

**Stack**:
Damage divided among everyone in its radius; resolved by grouping the required bodies. Under-stacked → larger lethal share. The mirror of spread.

**Spread**:
Damage that hits players individually; resolved by separating so no two overlap. Overlap → stacked lethal hits. The mirror of stack.
_Note_: stack-vs-spread is the most common resolution confusion; the damage *distribution* (many similar values vs. many individual values) discriminates.

**Knockback**:
A displacement effect. The danger is *where you land*, not the hit. Position isn't in the log, so analysis is inferred from what happened next. Can be resisted (Arm's Length/Surecast) or ridden for positioning.

**Tether**:
A line from a source selecting target(s) for a positional rule or follow-up effect (knockback, CC, bait). Diagnosed via the follow-up `applydebuff`/effect and its source actor, not a "tether" event.

**Debuff pass / hot-potato**:
A debuff that AOEs and transfers to a new holder on expiry, repeating a fixed number of times. A budget+chain mechanic — a broken chain wipes. _aka_ "confetti" (Double-Trouble Trap in Dancing Mad).

**Hazard**:
A telegraphed AOE meant to be dodged — the canonical *avoidable*. Taking it is a failure, reliably marked by Damage Down. Never solved by mit.

**Telegraph inversion**:
A meta-modifier (a `?` orb, color, debuff) that flips another mechanic's resolution (`?`stack→spread, `?`avoid→stand-in). Invisible to the log; inferred from the success/failure split.

**Snapshot**:
The instant a mechanic locks in its targets/resolution, typically at the end of a cast.

## Damage & debuffs

Canonical definitions in [fundamentals.md](knowledge/fundamentals.md).

**Mit**:
Mitigation — defensive cooldowns/effects that reduce incoming damage.
_Avoid_: defensives (use when specifically meaning personal cooldowns)

**Party Mit**:
In a mit sheet, the generic raid-mitigation slot a role presses for a raidwide — named by role rather than by job. A tank's "Party Mit" = whichever raid mit that tank carries (PLD Divine Veil · WAR Shake It Off · DRK Dark Missionary · GNB Heart of Light); Reprisal is the universal tank party mit. Keeps the sheet comp-agnostic.

**Extra**:
A spare/bonus cooldown a player layers *if free*, not part of the scheduled party-mit budget — e.g. PLD Passage of Arms (a positional cone, only on grouped windows). Lives in the sheet's "Extras" column, distinct from a [[Party Mit]] slot.

**Vuln**:
Vulnerability debuff — amplifies damage taken. In high-end content, treat as "cannot survive the next major hit."

**Damage Down**:
A debuff applied for failing a mechanic or getting hit by avoidable damage. The unique signal of a *non-fatal* failure (a death already shows up on its own). Distinct from Weakness/Brink of Death.

**Weakness / Brink of Death**:
Post-raise debuffs. A player KO'd and raised gets **Weakness**; if KO'd and raised *again* while still weak, they get the stronger **Brink of Death**. Not a Damage Down — the death is the failure, this is the aftermath. Reduces damage dealt.

**Overkill**:
On a death's killing hit, the damage dealt beyond the victim's remaining HP. Small overkill = a savable near-miss (shield/top-off/stacked mit); huge overkill = an unsurvivable mechanic failure. The killing blow's `amount` ≈ the victim's remaining HP.

**Cooldown economy**:
Treating cooldowns as a scarce budget spent across the whole fight timeline: each press both locks the cooldown for its recast *and* forgoes spending it elsewhere (opportunity cost). Party %-mit is earmarked for designed party damage (raidwides, heavy busters).

**Recast-feasibility check**:
The mandatory planning-mode step — diff every cooldown's scheduled uses against its recast / charges / gauge before presenting a plan. An un-castable plan is invalid.

**Pre-shield**:
A barrier placed on a soaker ahead of a positional hit (e.g. a tight tower soak) — the lean alternative to spending a party %-mit cooldown on a survivable soak.

## Roles & composition

**Tank / MT / OT**:
Main tank / off tank — the #1 and #2 enmity holders respectively.

**Regen healer**:
WHM or AST — healing built on regens and direct heals.

**Barrier healer**:
SCH or SGE — healing built on shields. "Double shield" = SCH + SGE.
_Avoid_: shield healer (barrier is the in-game term)

**Static**:
A consistent raid group that progs a fight together over time.

## Process & meta

**Analysis mode**:
The agent reading a *past* pull's log to diagnose what happened — backward and observational. Cooldown availability is *derived* (assume all cooldowns up at pull start; each usage event + its jobs.md recast tells when it returns), not read from any recast field in the log.

**Planning mode**:
The agent authoring a *forward* mit plan (assigning cooldowns to fight timestamps) before the pull — forward and derivational. Every scheduled cooldown must be recast-feasible. The mirror of analysis; the cycle is plan → raid → observe.
_Avoid_: authoring mode (use "planning")

**Prog**:
Progression — learning a fight before farming it. Prog logs are the primary input.

**PoC**:
Proof of concept — the minimum build that validates the agent is useful before deeper investment.

**Knowledge layer**:
The set of files under `knowledge/` assembled into the agent's system prompt (fundamentals, primitives, jobs, the active fight file, relevant reference guides).

**Fight file / catalog**:
A per-fight file under `knowledge/fights/` documenting *observed* mechanics — explicitly **not** a mit plan. Structured as Observed / Resolution / Open questions.
_Avoid_: mit plan, guide (a catalog is neither)

**AAC**:
Arcadion — the savage tier nomenclature from Dawntrail onward.
