# FFXIV Mechanic Primitives

This file defines the recurring mechanic patterns used in FFXIV raid and trial encounters. It is the vocabulary the agent uses to recognize, classify, and reason about boss mechanics when analyzing FFLogs data.

## Purpose

FFXIV reuses a small set of mechanic design patterns across every fight in the game. A "tower" in The Omega Protocol works the same way as a "tower" in Futures Rewritten. A "tankbuster" in a level 50 trial follows the same structural rules as a tankbuster in the current Ultimate. By learning the patterns once, the agent can reason about any fight — including fights it has never seen before — by recognizing which primitives are in play.

This file is **not** a catalog of specific abilities or fights. Specific boss abilities live in the per-fight files under `fights/`. This file describes the abstract patterns those abilities instantiate.

## How the agent should use this file

When analyzing a log, the agent should:

1. **Identify the primitive** — when an unfamiliar boss ability appears, match it to the closest primitive defined here based on its observable signals (damage magnitude, target pattern, debuffs applied, etc.)
2. **Apply the failure modes** — use the primitive's failure mode definitions to classify each instance as success or failure
3. **Reason about resolution** — use the primitive's structural properties to infer what the mechanic likely requires, even when fight-specific resolution is not yet documented

The agent should **not** treat these definitions as exhaustive. FFXIV occasionally introduces new mechanic patterns, and existing patterns have edge cases. When a log contains something that does not cleanly match any primitive here, flag it as a candidate for a new primitive rather than forcing a bad fit.

## File conventions

Each primitive entry follows this structure:

- **Recognition signals** — observable features in log data that identify this primitive
- **Variants** — sub-patterns within the primitive
- **Failure modes** — what counts as failure, classified by outcome rather than strategy
- **Notes for the agent** — heuristics, common confusions, and caveats

---

# Tankbuster

A **tankbuster** is a boss ability designed to deal heavy single-target or near-single-target damage to a tank. It is the most common designed mechanic in FFXIV and appears in essentially every fight.

## Recognition signals

A hit in a log is almost certainly a tankbuster if **all** of these are true:

- The target is a tank (by job/role)
- The `unmitigatedAmount` exceeds the max HP of any non-tank role in the party
- The damage is from a named ability, not a basic auto-attack

A `begincast` event preceding the damage is a **common but not required** signal. Some tankbusters are instant-cast (e.g., Hyperdrive in Dancing Mad Ultimate). Do not require a cast event to classify a hit as a tankbuster — damage magnitude and target role are stronger signals.

## Variants

### Single-target tankbuster
Hits the main tank only. The simplest form. Mit responsibility is on the MT and their support cooldowns (Reprisal, healer mits, etc.).

### Cleave tankbuster
Hits the #1 enmity target, then the #2 enmity target — usually in quick succession. Both tanks take damage. Tanks must be positioned so the cleave does not catch non-tanks. Revolting Ruin III in Dancing Mad Ultimate is an example.

### Shared tankbuster
Both tanks must stack within the hit zone to split the damage. One tank alone in the hit zone takes the full unsplit damage, which is typically lethal without major cooldowns.

### Auto-tankbuster
During specific phases, the boss's auto-attacks become lethal enough to require active mitigation. Less common, but the recognition signal is "regular auto-attack ability ID, but damage magnitude tankbuster-tier."

## Tank swap signal

Many tankbusters apply a vulnerability debuff (typically **Physical Vulnerability Up** or **Magic Vulnerability Up**) to the target. If the debuff duration is longer than the time until the next tankbuster, a tank swap is required — the other tank must take the next hit while the debuff is active. The agent can detect this by:

1. Identifying the vuln debuff applied alongside the tankbuster hit
2. Checking the debuff's remaining duration at the time of the next tankbuster
3. Comparing which tank took each consecutive tankbuster

If the same tank takes consecutive tankbusters while a vuln debuff is active, that is a tank swap failure.

## Failure modes

Classify by outcome, not by strategy. A non-standard execution that succeeded (e.g., MT solo'd a shared tankbuster with Hallowed Ground) is still a success.

For **single-target** tankbusters:
- MT died → failure

For **cleave** tankbusters:
- MT died → failure
- OT died → failure
- A non-tank took damage from the cleave ability → failure (positioning)
- Both hits landed on the same tank → failure (OT did not establish #2 enmity)

For **shared** tankbusters:
- Any tank died → failure
- Surviving with non-standard mit (one tank solo'ing it) → success, but worth flagging as an observation

For **auto-tankbusters**:
- MT died during the auto-attack window → failure

## Notes for the agent

- Tankbusters are the cleanest mechanic to analyze because the signals are unambiguous (large damage, tank target, often a vuln debuff).
- The "would one-shot a non-tank" heuristic is reliable: check `unmitigatedAmount` against the lowest max HP in the party.
- When in doubt about whether something is a tankbuster, look for the vuln debuff. If a tank-targeted hit applies a vuln, it is almost certainly a tankbuster.
- Do not assume cleave tankbusters are raidwides. They look like raidwides in damage magnitude but only hit specific targets in a specific order. Check the target list.

---

# Raidwide

A **raidwide** is damage that hits the entire party and is designed to be taken. It is part of the intended fight flow, mitigated by healer cooldowns and party damage reduction, not by avoidance.

The defining distinction is intent: **raidwide damage is supposed to be taken; avoidable damage is not**. A failed mechanic that happens to hit everyone is not a raidwide — it is a collection of failed dodges.

## Recognition signals

A damage event set is almost certainly a raidwide if **all** of these are true:

- Roughly 8 simultaneous damage events with the same `abilityGameID` at the same timestamp
- All targets are players (not pets or environment)
- No `Damage Down` debuff is applied to the targets
- The damage values are within a reasonable range for healable raidwide damage (see below)

## Avoidable vs designed: the Damage Down signal

The clearest signal that damage was **not** supposed to be taken is the `Damage Down` debuff applied to the targets. In FFXIV, this debuff is the standard punishment for failing avoidable mechanics. If a damage event applies Damage Down to the targets, it is not a raidwide — it is a failed avoidable.

A secondary signal: damage that is grossly disproportionate. As a starting heuristic, if `unmitigatedAmount` is more than **2x the magnitude of normal raidwide damage in the same fight**, treat the hit as a failed avoidable rather than a raidwide, even if Damage Down is not visibly applied. This threshold can be tuned as we gather more data.

## Variants

### Pure raidwide
Single damage event to all 8 players. Healed and mitigated, no further effects.

### Raidwide with DOT
Initial damage event followed by a damage-over-time component (e.g., a bleed or magical DOT). The DOT continues to tick after the initial hit, which affects healing requirements and may overlap with subsequent mechanics.

### Magical raidwide
Damage type is magical. Mitigated by magic-specific tools (Addle, Magick Barrier, Shake It Off's magical portion). Reprisal works on all damage types.

### Physical raidwide
Damage type is physical. Mitigated by physical-specific tools (Feint, Arm's Length is not a mit but is relevant for knockback-paired raidwides). Reprisal works on all damage types.

### Phased / sequential raidwides
Multiple raidwides in close sequence, typical of burn phases or "enrage windups." Mit cooldowns must be staggered across the sequence rather than burned on the first hit.

## Failure modes

- A player died from a raidwide → failure (insufficient mit or insufficient healing)
- Multiple players died → systemic failure (mit plan was wrong, not an individual error)
- A player took damage but the rest of the party did not → not a raidwide failure, classify as a failed avoidable

## Notes for the agent

- Raidwides are the easiest damage events to identify because of the 8-target simultaneous pattern.
- Use raidwide damage values as a baseline for the rest of the fight. Most other damage events can be classified relative to "how much bigger or smaller than a raidwide is this?"
- The mit applied to raidwides is the most diagnostic data in a log — it reveals the party's mit plan. If multiple raidwides go out with no party-wide mit active, that is a plan gap worth flagging.
- Do not assume all 8-target damage events are raidwides. Cleaves that happen to catch the whole party (positioning failure) look similar in raw event counts but will show Damage Down or disproportionate damage values.

---

# Tower

A **tower** is a ground AOE that requires one or more players to stand inside it ("soak") to resolve safely. A correctly soaked tower deals survivable damage to its soakers. An unsoaked tower explodes outward, dealing heavy damage to the entire party — typically with `Damage Down` or another failure debuff applied.

Towers are a **positioning** mechanic — their defining axis is body-allocation (who soaks). Whether a soak needs *mit* is a **separate, damage-driven** question (see `fundamentals.md` → "Mit follows damage, not mechanic type"), not something the "tower" label settles. A clean soak's damage is often calibrated to be survivable by any player with normal HP and no pre-existing debuffs, so it frequently needs nothing — but that's a fact about the *damage*, read per-fight, not a rule that positional mechanics get no mit.

## Recognition signals

A damage event is likely a tower soak if **all** of these are true:

- A small number of players (typically 1-2) take damage from the same ability at the same timestamp
- The damage is heavy enough to be notable but survivable without major cooldowns
- No `Damage Down` is applied to the soakers (a successful soak does not punish the soaker)
- The rest of the party takes no damage

A damage event is likely an **unsoaked tower failure** if:

- The entire party takes damage from an ability (often named like "Unmitigated Explosion" or similar)
- `Damage Down` or another failure debuff is applied to the affected players
- The ability ID and source actor are often distinct from the "successful soak" damage — towers typically have separate ability IDs for "soaked" vs "exploded" outcomes

The agent cannot reliably determine the *required* soak count, soaker count, or role restrictions from the log alone. These constraints must be authored in the fight file. **Default assumption: single-player tower, no role restriction**, unless the fight file says otherwise.

## The 8-player budget

Towers are a body-allocation mechanic, so they are bounded by the **8-player budget** (see `fundamentals.md`). Across all simultaneously-spawning towers, the total required soakers cannot exceed 8 — commonly 8 single-soaker towers, 4 two-soaker towers, or a mix summing to 8.

The available soaker pool is often **less than 8**: dead or vuln'd players cannot soak (a vuln'd soaker dies). Damage Down does *not* disqualify a soaker. The agent should count available bodies (8 − dead − vuln'd) at resolution and, if the pool is below the required soak count, treat the unsoaked tower as a downstream symptom — trace back to what depleted the pool rather than calling it a positioning error. See the 8-Player Budget entry in `fundamentals.md` for the full budget-vs-positioning fork.

## Variants

### Solo soak
One player per tower. Most common. The simplest form.

### Shared soak
Two (or more) players per tower. Damage is split among soakers. An understaffed shared tower may still resolve but kill the lone soaker.

### Role-restricted soak
Only certain roles can correctly soak (e.g., "tanks only," "non-tanks only"). The tower itself usually still resolves if soaked by the wrong role, but the wrong-role soaker dies. Role restrictions are not inferable from the log — they must be authored in the fight file.

## Failure modes

Tower failures are **two-stage**: the tower itself either resolves or does not, AND each soaker either survives or does not. These are independent.

### Tower-level failures
- Tower was not soaked at all → unsoaked explosion damages the party with Damage Down → failure
- Insufficient soakers in a shared tower → may still resolve but with reduced safety margin

### Soaker-level failures
- The wrong-role player soaked a role-restricted tower → tower resolves, soaker dies → failure
- A player with a pre-existing vulnerability debuff soaked → tower resolves, soaker dies → failure (see `fundamentals.md` on vulnerability debuffs)
- An extra player joined a tower beyond the required count → tower resolves, both/all soakers take damage but survive → **not a failure**, but worth flagging as inefficient

### Compound failures
- Both tower-level and soaker-level failures in the same instance (e.g., unsoaked tower causes party damage, and a player with a vuln dies from the explosion)

## Notes for the agent

- A tower's *positioning* — who was where when — is its primary analysis axis. Whether the soak needed *mit* is a **separate** question decided by the soak's actual damage, not by it being a tower; don't assume "positional ⇒ no mit" (see `fundamentals.md` → "Mit follows damage, not mechanic type"). An unsoaked-tower *failure*, by contrast, is solved by positioning and never by recommending mit (the general designed-vs-failure guardrail).
- The 8-player budget is a useful sanity check. If a fight has 4 simultaneous two-player towers, the agent knows the entire party must be available to soak — any player with a vuln is a problem.
- When a player dies near a tower mechanic, check the debuff state at the time of death before classifying it as a positioning error. A player with a magic vuln who soaks a normal tower will die, and the diagnosis is "pre-existing debuff" rather than "wrong position."
- Distinguishing a tower failure from a generic avoidable failure requires the ability ID. Towers have specific source actors and ability IDs; the fight file should document these as they are discovered.

---

# Gaze

A **gaze** is a mechanic that punishes players who are facing a specific source — usually the boss, sometimes a designated add or marker — during the snapshot window. The required resolution is to face away from the source before the cast resolves.

Failure typically applies a status effect rather than dealing significant direct damage. Common gaze failure debuffs include Petrification, Stun, Damage Down, or a vulnerability stack. The follow-on damage from being stunned/petrified through subsequent mechanics is usually the real punishment.

## Recognition signals

The agent **cannot** directly detect player facing from log data. Player orientation is not recorded in FFLogs events. Gaze analysis is therefore always **post-mortem**: the agent infers a gaze failure from the debuff that was applied, not from observing the act of looking.

A gaze failure is likely if:

- A specific debuff (Petrify, Stun, Damage Down, vulnerability up) is applied to one or more players at the timestamp of a known gaze ability resolving
- The ability is documented in the fight file as a gaze
- Players without the debuff at the same timestamp can be assumed to have faced away correctly

The direct damage from a gaze ability is often modest or zero. **Do not use damage magnitude as a recognition signal for gazes.** The debuff application is the signal.

## Variants

### Boss-source gaze
The boss itself is the source. All players must face away from the boss during the cast. Most common form.

### Add-source gaze
A specific add NPC is the source. Players must face away from the add, which may not be in the same direction as the boss. Requires authoring in the fight file to identify the source actor.

### Targeted gaze
Only specific players are at risk (e.g., players with a debuff that makes them gaze sources for others, or players being individually targeted). The fight file must document which players are affected.

### Multi-source gaze
Multiple sources active simultaneously, requiring positioning to face away from all of them at once. Resolution is often "stand at a specific position from which all sources are behind you."

## Failure modes

Classify by debuff application, not by damage.

- A player has the failure debuff applied at the gaze snapshot → failure (faced the source)
- Multiple players failed the same gaze → systemic failure (likely a positioning or callout issue, not individual error)
- A player survived the gaze but the failure debuff carries into the next mechanic and kills them → compound failure, but the root cause is the gaze

A player taking *direct damage* from a gaze ability without the failure debuff is unusual and may indicate a different mechanic was actually responsible — investigate further before classifying.

## Notes for the agent

- The agent cannot referee gazes in real-time. All gaze analysis is post-mortem inference from debuffs.
- The most common gaze failure debuffs in modern FFXIV content are **Petrification** (immobilize + take damage from subsequent hits) and **Damage Down**. Watch for either.
- When a player has an unexplained debuff at a timestamp, check whether a gaze ability was casting at that moment in the fight file. This is the primary diagnostic path.
- A gaze ability whose targets are listed as the entire party but where only some players have the failure debuff confirms the gaze worked correctly for the players without the debuff. This is one of the few mechanics where the *absence* of a signal on most players is the success indicator.
- Some gazes only apply the debuff and do no damage at all. These will not appear as damage events in the log — only as `applydebuff` events. Searching only damage events will miss these.

---

# Stack

A **stack** is damage targeted at one or more players that is **divided among everyone standing in its radius** at snapshot. The intended resolution is for the required number of players to group up so the hit is split below lethal. A stack taken by too few players deals a larger share to each — often lethal to a lone catcher.

Stacks are a **proximity** mechanic. Like towers, they consume bodies and are governed by the **8-player budget** (see `fundamentals.md`): a "stack in two groups of four" allocates all 8.

## Recognition signals

A damage event set is likely a stack if **all** of these are true:

- Several players take the **same ability** at the **same timestamp** with **similar `unmitigatedAmount`** values (the split share)
- The target count is a designed subset (a full-party stack = 8; a two-group stack = 4+4; a partner stack = 2)
- A lone player taking a *much larger* value from the same ability at the same timestamp is the tell of a **failed/under-stacked** instance (the share didn't divide)

The clearest failure fingerprint: one player's `unmitigatedAmount` is a small-integer multiple (≈2×, ≈4×, ≈8×) of the per-person share other players took — that multiple *is* how many bodies were missing from the stack.

## Variants

### Full-party stack
All 8 group on a marker. Damage divided by 8. The most common form.

### Group stack
The party splits into designated sub-stacks (e.g., two groups of 4, by role). Each group divides its own hit. Budget must sum to 8 across groups.

### Partner / pair stack
Exactly two players share. Often role- or position-paired (tank+healer, melee+ranged).

### Stack-or-spread (telegraphed)
The same telegraph resolves as *either* a stack or a spread depending on an indicator (marker, orb, debuff). See **Telegraph Inversion**. The agent must read the indicator, not assume.

## Failure modes

- A player died to a stack → under-bodied stack (too few sharers) or a pre-existing vuln amplified their share → failure
- One player took a multiple of the shared value → the stack didn't form correctly → failure (and the multiple tells you how short)
- A player who should have stacked was elsewhere and took a *spread*/individual hit instead → resolution confusion (read against the stack-or-spread indicator)
- Everyone took a clean even share and survived → success, even if a non-standard group composition was used

## Notes for the agent

- Stack vs. spread is the single most common point of confusion. The signal is the **damage distribution**: stacks show *many similar* values, spreads show *many individual* values to *different* players. A lone large value against a backdrop of small even ones means a stack was failed.
- A stack share scales with mit and shields like any hit — read `multiplier` and `absorbed` per sharer.
- Do not call a high-magnitude stack hit a tankbuster just because it's large. Check whether other players took an even share at the same timestamp.

---

# Spread

A **spread** is damage that hits players **individually**, requiring each affected player to be far enough from the others that no two spreads overlap. The intended resolution is separation. Overlapping spreads stack their damage on the caught players — frequently lethal, and usually flagged with `Damage Down` or a vuln.

Spread is the mirror of Stack: stack punishes being *apart*, spread punishes being *together*.

## Recognition signals

A damage event set is likely a spread if **all** of these are true:

- Multiple players take the **same ability** at the **same timestamp**, each as a **separate** hit (not a divided share)
- The per-player `unmitigatedAmount` is consistent across players when resolved cleanly (each ate their own, undivided)
- A player taking a **higher** value than peers indicates **overlap** — they caught someone else's spread on top of their own

## Variants

### Party-wide spread
All players must separate. Often paired with markers on each player.

### Role/subset spread
Only some players are targeted (e.g., DPS get spread markers). Untargeted players ignore it.

### Spread-with-debuff
The spread also applies a debuff (vuln, a DOT, or a follow-up marker). The debuff, not the damage, may be the real mechanic — check `applydebuff`.

### Stack-or-spread (telegraphed)
See Stack and **Telegraph Inversion**.

## Failure modes

- Two or more players overlapped → each took multiple spread instances → failure (positioning), often with Damage Down
- A player died to an *individual* spread with no overlap → check for a pre-existing vuln amplifying it; the spread itself is usually survivable
- A player meant to spread instead stacked with others → resolution confusion
- All targets took a single clean instance each → success

## Notes for the agent

- Distinguish from raidwide: a raidwide hits all 8 with one shared design intent and *no* spacing requirement; a spread requires separation and punishes proximity with overlap. Overlap damage (a player taking 2× the spread value) is the discriminator.
- Spread overlap is an **individual-punishment** model for Damage Down attribution (see `fundamentals.md`): each debuffed player owns their mistake.

---

# Knockback

A **knockback** displaces players a fixed distance away from a source point (or in a fixed direction). The danger is rarely the knockback's own damage — it is *where you land*: off the arena (instant death), into an unsafe zone, or out of position for the next mechanic.

## Recognition signals

- Knockbacks are **positioning effects** and may carry little or no damage. Like gazes, a small/zero damage event is not evidence of absence — check the ability and the fight file.
- The log does **not** record position, so the agent cannot see *where* a player was knocked. Knockback analysis is inferred: a death to "fell off" or a player taking a *later* mechanic they should have avoided can trace back to a mishandled knockback.
- Knockback immunity tools (**Arm's Length**, **Surecast**) appear as buffs on players at the knockback timestamp — their presence/absence is the diagnostic signal for whether a player chose to anchor or to ride the knockback.

## Variants

### Anchored knockback
Players use Arm's Length/Surecast (or a fixed-immunity mechanic) to ignore the displacement and hold position.

### Directed-positioning knockback
The knockback is *intended* to be ridden to a destination (the strat uses the push to move players to safe spots). Resisting it is the failure here, not riding it. (Common in this fight — see the Graven Image KB-tethers and confetti.)

### Chained knockback
Multiple knockbacks in sequence; immunity can only cover some, so the order of anchoring vs. riding matters.

## Failure modes

- A player died with no damage event explaining it shortly after a knockback → likely knocked off the arena → failure
- A player took a subsequent avoidable they were positioned to dodge → knockback landed them wrong → failure
- A player anchored (Arm's Length up) through a *directed* knockback that was supposed to move them → failure (wrong tool usage), classify by the downstream consequence
- Player rode/anchored the knockback and resolved the next mechanic cleanly → success

## Notes for the agent

- Knockback is the clearest case of "absence of a signal isn't absence of the mechanic" — most of its consequence is invisible to the log and must be inferred from what happened *next*.
- Always read knockbacks together with the mechanic they feed into. A knockback is almost never terminal on its own; it sets up the following resolution.

---

# Tether

A **tether** is a visible line connecting a source (boss, add, or another player) to one or more targets. It resolves by a positional rule: *stretch* it (move away to a distance), *break* it by line-of-sight or proximity, *pass* it to an eligible catcher, or simply *be the selected target* for a follow-up effect. The tether is a **selection + instruction**, not damage in itself.

## Recognition signals

- The tether itself is usually invisible in damage data. Its presence is inferred from a **follow-up effect on the tethered players**: a debuff applied, a knockback originating from the source, a directional hit, or a CC status (`Confused`, `Sleep`).
- The **source actor** of the follow-up debuff/effect identifies who the tether came from (e.g., the statue add vs. the boss). This is a primary use of source-actor attribution.
- Tethers frequently select **by role** (all DPS, all supports) — the affected set in the follow-up event reveals the selection rule.

## Variants

### Knockback tether
The tether resolves as a knockback from the source. Used for directed positioning (see Knockback). Selecting role groups is common.

### Effect/CC tether
The tether applies a status to the tethered side (e.g., left tether → `Confused`, right tether → `Sleep`). Resolution is positional (go to your assigned spot) and the *side* of the tether maps to *which* effect you get.

### Bait/aggro tether
The tethered player is the designated target for a follow-up (a directional AOE, a chasing mechanic). They must aim/place it safely.

## Failure modes

- The follow-up debuff/effect landed on the wrong role set, or a player resolved their tether in the wrong spot → positioning failure (read the source actor + the affected set)
- A CC tether (Confused/Sleep) carried a player into a subsequent hit they couldn't react to → compound failure, root cause is the tether resolution
- The tethered set resolved into correct spots with expected follow-ups → success

## Notes for the agent

- Tethers are diagnosed almost entirely through their **follow-up `applydebuff`/effect events and source actor**, not through any "tether" event. Treat the follow-up as the observable and reason backward.
- Role-selected tethers are a body-allocation cousin: the selection rule (all DPS / all supports) tells you the intended split before the fight file documents it.

---

# Debuff Pass (Hot-Potato)

A **debuff pass** is a debuff that, on expiry, deals an AOE around its holder **and transfers to a new holder**, who must then resolve it again — repeating a fixed number of times. The mechanic is a chain: each pass must be caught by an eligible player, and skipping a pass (no eligible catcher in range) typically ends the fight early or wipes the party. Often combined with a **knockback** on expiry (the AOE launches nearby players).

## Recognition signals

- A named debuff with a **short duration** that **reapplies to a different player** shortly after expiring on the previous holder (track the `applydebuff` → `removedebuff` → new `applydebuff` chain by ability name).
- An AOE damage event at the holder's position coinciding with the debuff's expiry; nearby players take it (shared/divided among catchers).
- The pass often alternates by **role** (e.g., one Support holder + one DPS holder, each passing within their role) — the holder sequence reveals the rule.
- A holder taking a **massive** AOE value alone is the tell that the pass wasn't shared/caught correctly (the share didn't divide — same fingerprint as a failed stack).

## Variants

### Stationary pass
Holder stays; catchers come to them to share and receive the pass.

### Knockback pass
The expiry AOE knocks nearby players back, and one of them inherits the debuff. The knockback is part of the resolution (see Knockback) — players line up to be launched and to catch the pass. (This fight's "confetti" / Double-Trouble Trap is this variant.)

### Role-locked pass
The pass can only transfer within a role group, requiring each group to keep an eligible catcher available for every iteration.

## Failure modes

- The pass had no eligible catcher in range → chain broke → fight-ending failure (the budget ran out of bodies for the chain)
- A holder took the expiry AOE undivided (huge solo value) → too few sharers → failure, often a death
- A player caught the pass while carrying a vuln or already debuffed inappropriately → death on the next AOE → failure
- Every iteration was caught and shared cleanly for the required count → success

## Notes for the agent

- This is a **budget + chain** mechanic: it requires not just bodies in a spot now, but an *unbroken sequence* of available catchers. A death earlier in the fight can break a later pass chain even with correct play — trace back to the depleted pool (see the 8-Player Budget in `fundamentals.md`).
- Identify it by the **debuff that hops between players**, not by the damage alone. The hop is the signature.

---

# Hazard (Avoidable Ground AOE)

A **hazard** is a telegraphed area of effect — on the ground or around the boss — that is **meant to be dodged**. It is the canonical *avoidable*: taking it is a failure, and the punishment is typically `Damage Down` plus damage that is survivable once but punishing in stacks. Hazards are the negative space the other mechanics position you around.

## Recognition signals

- A damage event hitting **only the players who failed to move**, not the whole party, usually with `Damage Down` applied (the unambiguous avoidable marker — see `fundamentals.md`).
- The same ability hitting a *variable* subset across pulls (whoever was clipped), unlike a raidwide's consistent 8.
- Often **pulsing/persistent**: many small hits from one ability over a window (a lingering puddle) rather than a single snapshot.

## Variants

### Snapshot hazard
A single telegraphed burst (donut, cone, line, circle). Dodge by the resolution instant.

### Persistent puddle
A lingering ground AOE that ticks for as long as a player stands in it. Shows as repeated small hits from one ability.

### Boss-relative pattern
AOEs telegraphed *around the boss* (rings, rotating cones) that define a safe spot relative to the boss — frequently paired with **Telegraph Inversion** (the `?` indicator).

## Failure modes

- A player took the hazard → failure (avoidable), confirmed by Damage Down or a subset-only hit pattern
- A player took *repeated* puddle ticks → stood in it too long → failure, severity scales with tick count
- A hazard caught a player who was displaced there by a knockback → failure, but root cause is the knockback
- No one took it → success (the absence of the damage event is the success signal)

## Notes for the agent

- Hazards are the primitive most reliably caught by the **Damage Down** signal, because they are essentially never by-design. A subset-only hit + Damage Down = a failed hazard, full stop.
- Do **not** recommend mitigation for hazard damage — it is a failure to solve by movement, not by cooldown (see the mit-gap guardrail in `fundamentals.md`).
- A pulsing many-hit ability with a low per-hit value is more likely a puddle hazard than a raidwide; check whether the target set is the failed subset or the whole party.

---

# Telegraph Inversion (the "?" Modifier)

**Telegraph inversion** is not a damage mechanic but a **meta-modifier**: an indicator (a `?` orb, a color, a debuff) that *flips the resolution* of an otherwise-normal telegraphed mechanic. A "stack" marked with the inverter resolves as a spread; an "avoid this AOE" marked with it means "stand in it"; and so on. The mechanic tests whether players read the indicator rather than the base telegraph.

## Recognition signals

- The agent **cannot see the indicator** (orb state, marker color) in log data. Inversion is inferred only from the **outcome**: the resolution that succeeded contradicts the base telegraph's normal reading.
- The diagnostic tell is a population that did the *opposite* of the apparent telegraph and survived clean, while those who followed the literal telegraph took damage + Damage Down.
- Requires the **fight file** to document which mechanics carry an inversion indicator and how it presents. Without that, the agent should flag "resolution appears inverted" rather than asserting the rule.

## Variants

### Inverted stack/spread
`?` stack → spread, `?` spread → stack. Pairs with the Stack/Spread primitives.

### Inverted hazard
`?` "avoid AOE" → "stand in the AOE"; the safe and unsafe zones swap. Pairs with Hazard.

### Mixed-ring inversion
Multiple telegraphs resolve simultaneously, each independently inverted or true (e.g., two rings of orbs around the boss, top and bottom resolving different elements, any orb possibly `?`). The party must read each independently.

## Failure modes

- A player resolved the **literal** telegraph when it was inverted (or vice versa) → took the punished outcome → failure
- Half the party read it right and half wrong → split outcome in the damage/Damage-Down distribution; a callout/communication failure rather than individual error
- Everyone resolved the *effective* (post-inversion) mechanic → success

## Notes for the agent

- Inversion is a layer *on top of* a base primitive, never standalone. Classify the underlying mechanic first (stack, spread, hazard), then ask whether an inverter was present per the fight file.
- Because the indicator is invisible to the log, the agent's job is limited to detecting *that* a resolution was inverted (from the success/failure split), not refereeing whether a given player read the orb. State conclusions accordingly.
