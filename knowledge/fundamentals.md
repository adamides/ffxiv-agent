# FFXIV Combat Fundamentals

This file defines cross-cutting concepts that apply across all fights and all mechanics. Where the `primitives.md` file describes patterns the boss uses, this file describes rules of the game itself — how damage, debuffs, and mitigation actually work.

The agent should treat the concepts here as **always-on context** when reasoning about any log. These are not patterns to recognize; they are rules to apply.

---

# Vulnerability Debuffs

**Vulnerability debuffs** amplify incoming damage to the affected player. They are one of the most consequential debuffs in high-end FFXIV content because the multiplier is typically large enough to make any subsequent significant hit lethal.

## Common variants

- **Magic Vulnerability Up** — amplifies magical damage
- **Physical Vulnerability Up** — amplifies physical damage
- **Damage Down** — see the separate entry on Damage Down

Individual fights may use uniquely-named debuffs that follow the same pattern (e.g., "X-Vulnerability" where X is a fight-specific element). The fight file should document these as they are discovered. The agent should treat any debuff matching the pattern "[type] Vulnerability Up" as functionally equivalent for analysis purposes.

## How they affect analysis

In high-end content (Savage, Ultimate), vulnerability debuffs effectively mean **the affected player cannot survive another significant hit** until the debuff expires. The damage multiplier is not a small percentage — it is calibrated so that any meaningful damage event during the debuff window is fatal.

The agent should treat vuln debuffs qualitatively, not quantitatively:

- ❌ Do not try to compute exact post-vuln damage values
- ✅ Treat the affected player as "cannot take another major hit" for the duration

## Diagnosis pattern

When investigating an unexplained death:

1. Check the target's debuff state at the time of the lethal hit
2. If a vulnerability debuff was active, the diagnosis is "pre-existing vuln amplified the hit," not "this hit was too strong"
3. Trace the vuln back to its source — what mechanic applied it, and was that mechanic's failure the root cause?

This is a frequent diagnostic path for tower failures, gaze chains, and mechanics where one mistake snowballs into a death on the next hit.

## Duration

Vulnerability debuff durations vary by fight and by source ability. The agent should always check the actual duration in the log rather than assuming. If a vuln is applied at timestamp X with duration Y, any significant damage event in the window [X, X+Y] to that player should be examined as a potential vuln-amplified death.

## Stacking

Vuln debuffs may or may not stack depending on the fight's implementation. The mechanical detail is less important than the practical implication: once a player has any vulnerability debuff active, the next significant hit is likely lethal. The agent should not get bogged down modeling stack counts — the qualitative outcome is what matters.

## Failure vs. by-design

**A vulnerability debuff does not automatically mean a mechanic was failed.** Vulns are frequently applied *by design* as part of normal fight flow:

- A tankbuster stamps a vuln to force the tank swap
- Intended stack mechanics pile vuln stacks on the party as they resolve correctly
- Some tower soaks or other "you took this on purpose" hits apply a vuln

So the presence of a vuln is **ambiguous** — it can mean "failed" or "working as intended." Always trace the source ability and decide which. This is the key contrast with **Damage Down** (see below), which is essentially *never* by-design and is therefore the unambiguous failure marker. When the diagnosis hinges on "did someone fail here?", Damage Down answers it directly; a vuln does not.

---

# Damage Down

**Damage Down** is a debuff applied for failing a mechanic or getting clipped by avoidable damage. Unlike a vulnerability debuff, it is **essentially never applied by design** — its presence on a player is the single most reliable signal in any log that *a mechanic was failed*. This is what makes it the most diagnostic debuff in FFXIV log analysis.

Its magnitude is large — typically a **60%+** reduction in damage dealt. This is itself a useful tell: a *large* damage-dealt penalty is almost certainly Damage Down, while a smaller one (25–50%) points to post-raise Weakness/Brink of Death instead (see below).

## What it tells you: the "got away with it" detector

A death announces itself — the log shows the KO plainly. Damage Down is the only thing that surfaces the failures the party **survived**: the gaze three people ate, the tower someone clipped, the spread that overlapped. On a prog pull that didn't wipe, these mistakes are otherwise invisible. For mechanic-solving, this is the entry's highest value: **Damage Down tells you who is still fuzzy on a mechanic even when nobody died.**

So the agent's framing is: **Damage Down = a non-fatal failure marker.** If a player has Damage Down, they survived something they should not have walked away from cleanly.

## Damage Down is not a survivability factor

This is the most important distinction from vulnerability debuffs, and an easy trap. Damage Down reduces **damage dealt** — the player's *output*. It has **zero effect on the player's survivability**. A player with Damage Down is exactly as likely to survive the next hit as one without it.

The diagnostic move that is correct for vulns is therefore *wrong* for Damage Down:

- ❌ "Player died with Damage Down active, so the Damage Down contributed to the death" — false. Damage Down never contributes to a death.
- ✅ Damage Down is purely a **failure marker**, never a **death-risk factor**. Treat it as evidence that a mechanic was failed, not as a reason a subsequent hit landed harder.

(Because Damage Down only reduces output, its DPS impact is outside this agent's scope — the agent cares about it strictly as a failure signal.)

## Attribution: consequence-holder vs. cause

Damage Down marks **who holds the consequence, not necessarily who caused the failure.** The number of players with Damage Down is *not* the number of failures. Two punishment models exist, and they map Damage Down to root cause very differently:

- **Individual-punishment mechanics** (gaze, spread, personal avoidables): each player's Damage Down is their *own* mistake. Here "who is debuffed" does equal "who messed up."
- **Shared-punishment mechanics** (unsoaked tower, a missed party stack — the propagating kind): *one* player's failure stamps Damage Down on the *entire party*. Here a party-wide Damage Down can trace to a single root cause.

The agent **cannot** tell these apart from the Damage Down events alone. It must identify the mechanic via the `applydebuff` event's **source ability**, then consult the relevant primitive / fight file to learn which punishment model applies. The source ability is what decides whether eight Damage Downs mean eight failures or one.

## Recognition in log data

Damage Down appears as an `applydebuff` (status) event, not necessarily alongside a damage event to that player. As with gazes, **searching only damage events will miss it** — the agent must inspect status/debuff events. The diagnostic path:

1. Find the `applydebuff` for Damage Down and its timestamp
2. Resolve its **source ability** — this names the failed mechanic
3. Use the primitive / fight file to determine the punishment model (individual vs. shared) and thus map the debuff back to a root cause

## Weakness and Brink of Death are *not* Damage Down

A separate pair of debuffs also reduces damage dealt, and must not be confused with Damage Down:

- **Weakness** is applied when a player is KO'd and then raised by a healer.
- **Brink of Death** is the stronger form, applied if the player is KO'd *again* while still under Weakness and raised once more.

These are **post-raise aftermath**, not a mechanic-failure punishment. The failure they point to is the *death itself*, which the log already shows as a KO — so they add no failure information the death event didn't. If the agent sees a damage-dealt penalty on a player, it must confirm whether it is Damage Down (a fresh failure at this timestamp) or Weakness/Brink of Death (residual from an earlier death — look backward for the KO, do **not** attribute a failure to the mechanic at this timestamp).

Two signals disambiguate:

- **Magnitude** — Weakness reduces damage dealt by ~25%, Brink of Death by ~50%; Damage Down is larger, typically 60%+. A penalty under ~50% is post-raise; a large one is Damage Down.
- **Duration** — Weakness runs long (~100s) and trails the player well past the death that caused it, whereas Damage Down is tied to a specific failed mechanic at its own timestamp.

---

# The 8-Player Budget

High-end FFXIV content is **tuned for exactly 8 live players.** Every mechanic is designed assuming a full, available party — so the party's 8 bodies are a fixed resource that mechanics spend. This is a general invariant, not a tower-specific one: it governs any mechanic that requires a number of players to be in specific places at once (tower soaks, shared stacks, tether catches, bait spots, soak duties of every kind).

## Body-allocation

Any set of simultaneous "needs a body here" requirements must sum to **≤ 8**. For example, towers spawning together can be 8 single-soaker towers, 4 two-soaker towers, or any mix summing to 8. If a fight presents a body-allocation mechanic, the agent can use the budget to infer the intended assignment even before the fight file documents it.

## The available pool is often less than 8

The *required* count is fixed by the mechanic, but the *available* pool shrinks when players cannot participate:

- **Dead players** — a KO'd (or not-yet-raised) player is simply gone from the pool.
- **Vuln'd players** — a player carrying a vulnerability debuff cannot safely take a soak/hit they'd otherwise survive; assigning them is a death. They are effectively out of the pool for that mechanic.

Critically, **Damage Down does *not* shrink the pool.** Damage Down reduces damage *dealt*, not survivability (see the Damage Down entry) — a Damage-Down'd player can soak a tower or take a shared hit perfectly well. The "can't participate" set is *dead + vuln'd players only.*

## Diagnostic value: deaths cascade through the budget

Because the budget assumes 8, a death is not a self-contained loss — it **breaks the budget for every later body-allocation mechanic.** A tower can go unsoaked, or a stack go under-bodied, purely because the party was already short, even if everyone still alive played correctly.

This gives the agent a clean fork when a body-allocation mechanic fails:

- **Budget failure** — there were not enough available bodies (someone was dead or vuln'd). Root cause is the *earlier* event that shrank the pool, not the mechanic that visibly failed.
- **Positioning failure** — enough bodies were available, but a player was in the wrong place. Root cause is at this mechanic.

The agent should count available bodies (8 − dead − vuln'd) at the moment of resolution before classifying. If the available pool was already below the required count, the visible failure is a downstream symptom, and the agent should trace back to what depleted the pool.

---

# Damage Types (Physical vs. Magical)

Every damaging hit in FFXIV belongs to a **damage school**. The school matters because a few mitigation tools only affect one school — so "was mit used?" is not the whole question; "was the *right* mit used for this school?" is.

## The schools

- **Physical** — auto-attacks, most weaponskill-flavored boss abilities.
- **Magical** — most spell-flavored boss abilities. In practice, a large share of high-end boss damage (including most of Dancing Mad's fight-6 kit) is magical.
- **Unaspected / "darkness"** — a rarer third school that ignores school-specific mit (e.g., Magick Barrier does nothing to it) but is still reduced by all-school tools. Its `type` code is **not yet confirmed** in our data (see below) — treat as "unknown school" when encountered, don't guess.

## Recognition: school is on the ability, not the event

The damage **event** does not carry the school. Its `type` field is the event *category* (`"calculateddamage"` / `"damage"`). To get the school, join the event's `abilityGameID` to `masterData.abilities[].type`:

- `type=128` → **physical**
- `type=1024` → **magical**
- (`type=8` healing/shields, `type=1` utility — not damage)
- `type=32 / 64 / 256` → small unconfirmed buckets; emit as "unknown school" rather than guessing.

Both `128`→physical and `1024`→magical are confirmed against real incoming damage in the test report. The data-fetching script should decode this into an explicit `school` column so the agent never has to infer it.

## Mitigation tools by school

Two mechanically different categories reduce party damage:

**Debuffs applied to the boss** (lower the damage it *deals*, so they protect everyone in range while active):

| Tool | Job | Reduction | Schools |
|---|---|---|---|
| Reprisal | any tank | −10% | **all** |
| Dismantle | MCH | −10% | **all** |
| Feint | melee | −10% physical / −5% magical | both, **weighted physical** |
| Addle | caster | −10% magical / −5% physical | both, **weighted magical** |

**Buffs applied to the party** (lower the damage it *takes*):

| Tool | Job | Reduction | Schools |
|---|---|---|---|
| Magick Barrier | RDM | −10% magic damage taken (+healing received) | **magical only** |

(Full job toolkits live in `jobs.md`; this is only the school-relevant subset. The official job guide is the canonical source for exact values.)

## Key points for the agent

1. **Almost nothing is single-school.** Reprisal and Dismantle cover all schools; Feint and Addle cover *both* schools and merely lean one way. Never treat Feint as useless on magic or Addle as useless on physical — they still apply, just at the weaker 5%.
2. **The one genuinely school-locked tool is Magick Barrier** — magical only. It does *nothing* against a physical (or unaspected) hit. Flag Magick Barrier spent on a physical hit as wasted, and a heavy magical hit taken with no Magick Barrier as a possible gap.
3. **Feint vs. Addle is a school choice.** On a magic-heavy window, Addle out-mitigates Feint; on a physical window, the reverse. Because Dancing Mad's fight-6 damage is almost entirely magical, the agent can flag patterns like "Feint used into an all-magic phase where Addle would have mitigated more," or "no Addle/Magick Barrier up for a stack of magical raidwides."

This is what damage-type recognition buys: the agent can judge whether the mit chosen *matched the school of the incoming damage*, not merely whether some cooldown was active.

---

# How Mitigation Stacks

## Mitigation is multiplicative, not additive

Multiple mitigation effects combine by **multiplying their remaining-damage fractions**, not by summing their percentages. Three separate 10% reductions are not 30% off — they are:

```
0.9 × 0.9 × 0.9 = 0.729  →  ~27% total reduction
```

The practical consequence: **stacking mit has diminishing returns.** The agent must never add percentages ("we had 10 + 10 + 20 = 40%"), and must not assume "stack more cooldowns" scales linearly. Each additional layer shaves a fraction of an already-shrunken number.

## Read the multiplier — don't compute it

The agent rarely needs to do this math itself, because **every damage event already carries the realized combined multiplier** in its `multiplier` field. `multiplier = 0.8` means 20% total mitigation was active on that hit; `0.648` means ~35%. This is the *actual* result after all percentage reductions stacked.

So the operational moves are:

1. **Read `multiplier`** to know how mitigated a hit actually was.
2. **Attribute it** via the event's `buffs` field — the buff IDs active on the target at hit time tell you *which* cooldowns produced that multiplier.
3. **Reason about gaps** (below), rather than reverse-engineering exact per-cooldown contributions.

## Shields are a separate axis

The `multiplier` field captures only **percentage reductions**. Barrier/shield absorbs are *not* in it — they reduce the post-multiplier amount separately (via `absorbed`). So "how protected was this hit" is **two numbers**: the percentage multiplier *and* the shield absorb. Do not conflate them, and do not expect a shield to show up in `multiplier`.

## Mit-gap detection

This is the high-value diagnostic: catching damage that *should* have been mitigated but wasn't. The pattern:

- A hit's `multiplier` is at or near **1.0** (little or no reduction), **and**
- the hit was **designed to be taken** (a raidwide or tankbuster — see `primitives.md`), **and**
- ideally, school-appropriate mit existed and wasn't used (see Damage Types).

→ Flag a mit gap: "this magical raidwide landed at `0.96` — effectively no party mitigation was up; there was room for a 10–20% cooldown."

### The guardrail: only designed damage is mit-solvable

**Before suggesting any mitigation would have helped, classify the hit.** Mit-gap analysis applies *only* to damage that was designed to be taken. It does **not** apply to:

- **Failed avoidables / overkill hits.** Example from the Dancing Mad test report: *Gravitational Explosion* at `unmitigatedAmount` 1,435,472 — no realistic stack of cooldowns survives that. The correct diagnosis is "solve the mechanic," **never** "use more mit." An agent that recommends mitigation on a failure-overkill is actively misleading.
- **Mechanic failures generally.** If a death traces to a vuln, an unsoaked tower, or a gaze chain, the fix is the mechanic, not a cooldown.

So the rule: **on designed damage, look for mit gaps; on failures, recommend solving the mechanic, never mitigating it.**

### Mit follows damage, not mechanic type

Whether a designed hit comes from a "positional" mechanic — a tower soak, a spread, a puddle — is **irrelevant** to the mit decision. Only the damage matters: its **magnitude**, its **school**, and whether it's designed-vs-failure (above). A soak is just damage; read its actual value and mit it exactly like any hit that size — often a clean soak is calibrated survivable and wants nothing, sometimes it's chunky and wants covering. "Positional" neither forbids nor requires mit. Positioning — who stands where, the soak/body assignment — is a **separate axis**, governed by the 8-player budget; it is never itself a reason to apply or withhold mit. (So there is no "towers don't take mit" rule: a tower's *positioning* is one question, the *damage* its soak deals is an independent one.)

## Death counterfactuals: bounded by overkill

Naming a cooldown that "would have saved" a death once required data the pipeline lacked. Two of the three former blockers are now resolved, so the guardrail is narrower than "stay qualitative about everything":

- **Cooldown availability — resolved.** It is *derived*, not read from the log (see **Cooldown Economy & Planning Mode** below). The agent may assert that a specific cooldown "was available and went unused."
- **The lethal threshold on a death — resolved by overkill.** A death's killing hit carries an `overkill` amount (verified in report `XnWJp61MzhGkFtBc` fight 37: 12 deaths, 12 overkill values on the killing DamageTaken events). On the killing blow, `amount` is the victim's *remaining HP* (the damage that brought them exactly to 0) and `overkill` is the excess — so the death's **effective EHP gap is known directly, with no max-HP needed.** This separates savable deaths from unsurvivable ones *quantitatively*: in that pull, the DNC died to Double-Trouble Trap by an overkill of **12,701** (a ~13k shield or top-off — or two stacked party mits — saves it; a single 10% mit shaves only ~6k and does **not**), while the SCH and MT died by **~1.3M** (no stack of cooldowns survives that — solve the mechanic, never mit). This is the real, per-death form of the "never mit an overkill" guardrail above.
- **Max HP on a *survived* hit — still missing.** Remaining HP is only recoverable on the killing blow, never on a hit a player lived through. So **survivor** counterfactuals stay **qualitative** ("a party mit was missing here," not "you were one hit from death"). Max HP now matters only as a hedge on one branch: a *top-off* saves a small-overkill death **only if the victim was not already full**, which the log does not show — so hedge top-off claims, while shield/mit claims (which don't depend on fill state) can be firm.

So, sharpened: for a **death**, classify by overkill and, when the gap is small, name the tool *class* (shield / top-off / stacked mit) sized against the overkill and confirmed available by derived recast — hedging only top-offs on fill state. For a **survived** hit, stay qualitative.

---

# Cooldown Economy & Planning Mode

Every other entry in this file is mode-agnostic — the rules hold whether you are reading a past pull or authoring a future one. This entry is the exception: it draws the line between the agent's **two modes** and defines the discipline the forward mode requires.

## Two modes: observe the past vs. compute the future

The agent does two jobs with opposite epistemics:

- **Analysis mode** — reading a *past* pull's log to diagnose what happened. Backward and **observational**.
- **Planning mode** — authoring a *forward* mit plan (assigning cooldowns to fight timestamps) before the pull. Forward and **derivational**.

They are two halves of one cycle: **plan → raid → observe**. A plan is authored, the pull is run, and analysis grades the pull against the plan; analysis findings ("this death was savable"; "this window had no party mit") feed the next plan.

## Cooldown availability is *derived*, not read

A recurring mistake is to treat cooldown availability as unknowable because the log carries no "recast timer" field. It does not need one. Availability is **reconstructed** from two things the agent already has:

1. **The anchor assumption:** every cooldown is available at pull start.
2. **Forward derivation:** each use event's timestamp + that cooldown's recast (from `jobs.md`) tells you exactly when it returns.

This works in **both** modes — only the *obligation* differs. In analysis you derive availability to **check** a past pull (so the agent *can* say "Reprisal was up at 1:38 and went unused"). In planning you derive it to **guarantee** a future one: a plan that schedules a cooldown before its recast is up is not a plan, it is fiction.

## The recast-feasibility check (mandatory in planning)

Before presenting any mit plan, the agent **must** diff every cooldown's scheduled uses against its recast. This is not optional polish — an un-castable plan is the exact failure this discipline exists to prevent (an early Kefka plan double-scheduled PLD tank cooldowns 32s apart, stacked one DRG's Feint five times, and re-pressed Reprisal inside its recast). The check has **three buckets**, because cooldowns are not all gated the same way:

1. **Flat recast + charges → hard-verify.** Most cooldowns (Reprisal 60s, Feint 90s, Rampart 90s, Oblation 2 charges/60s). Mechanically checkable against `jobs.md`: spacing ≥ recast, and no more simultaneous uses than charges. This bucket catches most slop (Feint ×5, Reprisal at 55s).
2. **Timer-accrued gauges → approximate ceiling.** A few tools are gated by a resource that fills on wall-clock time, not a flat recast: **SCH Aetherflow** (a burst of 3 stacks per 60s, shared across Sacred Soil / Lustrate / Indomitability / Excogitation) and **SGE Addersgall** (+1 per ~20s, capped at 3, shared across Kerachole / Taurochole / Druochole / Ixochole). Check scheduled uses against the accrual ceiling, but flag it **approximate** — overcap, Rhizomata, and Dissipation perturb the real count. "Kerachole on every window" is caught here: ~2/min is plausible on the timer alone but competes with the healer's other Addersgall spends.
3. **Rotation-accrued gauges + bundle shorthand → judgment / decompose.** **PLD Oath Gauge** (Holy Sheltron, Intervention) and **DRK MP** (The Blackest Night) fill from the DPS rotation, which this knowledge layer deliberately excludes — they are *not* mechanically derivable here. In practice they refill fast; treat them as **near-always available**, never the binding constraint. And **sheet shorthand is not a cooldown**: a label like "Kitchen Sink" (throw everything short of invuln) must be **decomposed into its named component cooldowns** (Sentinel/Guardian, Bulwark, Rampart, …) before bucket 1 can check any of them. A bundle scheduled twice 32s apart is really its 90–120s components scheduled twice 32s apart.

A reuse that lands *exactly* at the recast boundary passes the check but is fragile to pull drift. The fix is not to abandon it: **press the first use a few seconds early.** The hit is a single instant and mit buffs last 15–20s, so an early press still covers it *and* starts the recast sooner, buying slack for the reuse (and for a pre-shield, an early application is required anyway — the barrier must exist before the cast snapshots). So "zero-slack" is an *activation-timing* note, not an infeasibility — schedule the press, not just the hit.

> Gauge-regen rates live **here**, not in `jobs.md`. `jobs.md` stays a clean per-cooldown catalog; its "gated by X" notes are pointers into this bucket. Modeling gauges precisely would require importing the whole rotation / MP-tick layer the project scopes out — so the timer ceilings are deliberately approximate.

## Cooldowns are a scarce timeline budget (opportunity cost)

Recast feasibility is one face of a deeper rule: a cooldown is a **scarce resource spent across a whole timeline**, and every press has two costs. Pressing a cooldown at time T (a) makes it unavailable until T+recast (the feasibility face), and (b) spends it *here* instead of everywhere else it could have gone (the **opportunity-cost** face). So the planning question is never "is *this* hit survivable with *this* mit" in isolation — it is "across the fight, is this the best place to spend this press, given every other hit competing for it."

Party %-mit cooldowns are the scarcest layer and are **earmarked for designed party damage** — raidwides and heavy tankbusters (see Raidwide / Tankbuster in `primitives.md`). The waste to avoid is spending a **party-wide** mit on a hit that only lands on **one or two bodies**: a party %-mit covers eight, so putting Kerachole or Reprisal on a 1–2-target hit pays its full opportunity cost to protect mostly no one. If such a hit needs covering, use a **targeted/personal** tool — a pre-shield *or* a targeted % (Aquaveil, Oblation, a personal tank mit) — and keep the party-wide budget for the party-wide hits. The axis here is **target breadth** (party-wide vs. targeted), **not** barrier-vs-%, and **not** whether the mechanic is positional.

The same waste applies to **layering mit on an invuln'd target**. A *pure* invuln (Hallowed Ground, Holmgang) nullifies the hit, so any barrier / %-mit / heal placed on that player *for the hit the invuln covers* does nothing — e.g. AST Celestial Intersection on a PLD using Hallowed Ground is wasted. The exception is invulns that *require* healing to survive or clear: **GNB Superbolide** (drops the GNB to 50% HP) and **DRK Living Dead** (must be healed to full within the window) genuinely want heals — but heals to recover, not mit to reduce a hit that isn't landing. Spend nothing extra on a pure-invuln'd hit.

**Healer GCD heals and shields carry a hidden cost: damage.** A barrier or heal cast on the global cooldown — SGE Eukrasian Prognosis, SCH Succor / Adloquium, WHM Cure / Medica, any raw GCD heal — occupies a GCD that would otherwise be a damage spell. Unlike an **oGCD** mit (which is free of this cost), a GCD heal/shield is a **DPS loss**. So in planning, cover a window with **oGCD** mit and barriers first, and schedule a GCD heal/shield only to fill a gap the oGCDs can't. This agent doesn't model DPS, but a plan that leans on a GCD shield *every* window is spending damage it didn't need to — flag the GCD-heavy windows so the cost is a deliberate choice, not an accident. (This is why the sheet's "Extras" slot is for *spare oGCD* layering, while GCD healing stays minimal.)

## Match the mit to the school (forward)

The school discipline from the **Damage Types** entry applies forward in planning: schedule mit whose coverage matches the **damage school of the window** it covers. A magic-heavy window wants Addle / Magick Barrier / the magic-weighted party mits (Dark Missionary, Heart of Light); a physical hit wants Feint and the all-school tools. Scheduling a school-locked tool against the wrong school is planned waste — e.g. a *physical* tankbuster like Ultimate Embrace #1 gains **nothing** from Magick Barrier, so a plan that "covers" it with Magick Barrier has a hole where real mit should be.

## Match the mit to the positioning, too

School is not the only fit a plan must check — some party mits are **shape- or position-bound**, covering only players inside an area, and those must be scheduled onto mechanics where the party is actually *grouped inside that area*:

- **PLD Passage of Arms** — a cone behind the PLD; only protects party members standing in the cone.
- **AST Collective Unconscious**, **SCH Sacred Soil**, **WHM Asylum**, **DNC Improvisation** — ground-placed rings/zones; only cover players standing in them.

These are wasted on **spread / scatter** mechanics, where the party is deliberately apart and can't sit in one cone or zone. Schedule them onto **grouped** windows (stack raidwides, group-up hits). The canonical error: putting Passage of Arms on a raidwide that *requires spreading* (e.g. Wave Cannon) — the cone catches no one; the same cooldown is excellent on a grouped raidwide (e.g. a Light of Judgement the party stacks for). So the fit test is **two-dimensional — right school *and* right positioning** — before a scheduled mit actually does what the plan assumes. (Instant whole-party tools — Divine Veil, Shake It Off, Succor, Kerachole — have no such positional constraint; this applies only to the area/cone/channeled ones.)