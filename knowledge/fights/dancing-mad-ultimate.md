# Dancing Mad (Ultimate) — Fight Catalog

This file catalogs the **observed** mechanics of Dancing Mad (Ultimate), keyed to FFLogs data. It is a **catalog, not a mit plan**. During progression the correct resolution of a mechanic is often unknown; each entry separates what the log *shows* from what has been *figured out* from what is *still open*.

Every entry uses:

- **Observed** — what the log data shows (abilities, targets, debuffs, timing, source actor).
- **Resolution** — what the mechanic actually is / how it's meant to be solved (or `UNKNOWN — testing X`).
- **Open questions** — what isn't yet known.

Match each mechanic to a pattern in [primitives.md](../primitives.md); cross-cutting rules live in [fundamentals.md](../fundamentals.md).

## Boss & actors

- **Kefka** — the boss. Source of most casts (tankbusters, the orb telegraphs, Tele-Portent, the finale damage).
- **Graven Image** — a recurring **statue add** and the spine of P1: the whole phase is built around three statue sequences the static's strat doc calls **Graven Image 1 / 2 / 3**. Source of the knockback tethers, the vuln lasers, the half-room cleave orbs, the gravity tethers, and the late Confused/Sleep CC tethers. When a debuff's source actor is "Graven Image," it came from the statue, not Kefka — this distinction is a primary diagnostic.
- **Environment** — engine source for arena-driven effects (the confetti / Double-Trouble Trap debuff, post-raise Weakness).

## Source data

Built from FFLogs report `XnWJp61MzhGkFtBc`, **fight 37** (deepest prog pull seen, 3:10, full wipe inside P1). Pull through `py scripts/fetch_fight.py XnWJp61MzhGkFtBc 37`. Cross-referenced against the static's P1 strat doc ("UMAD P1: Merry Go Round," XIVPlan v4.0). Composition for this pull (anonymized to role labels): WAR (MT), PLD (OT), WHM-less — SGE, SCH; DPS DRG, VPR, DNC, RDM.

**Second reference pull:** report `v8nM1zQ6C2FYjPVa`, **fight 52** (4:36 — the deepest pull, clearing all of P1 and wiping in the P2 *God Kefka* towers). Pull via `py scripts/fetch_fight.py v8nM1zQ6C2FYjPVa 52`. Same core comp **except the OT-side healer is AST, not SCH** — a healer swap between reports (the static's current comp is SGE+AST). This pull's clean P1 is the source for the **timeline placements and damage values** in the P1 catalog below. Only P1 death in this pull: the VPR at 3:11 (finale).

**Full-clear reference:** report `ApYjk8dZqz7LRbMy`, **fight 1** (18:40 **KILL**, no deaths). Pull via `py scripts/fetch_fight.py ApYjk8dZqz7LRbMy 1`. This is the source for the **phase map** below and for **P2 (God Kefka) onward**. It's a *different* static — a different comp (PLD, DRK, AST, SCH; DNC, PCT, RPR, VPR — anonymized to role labels in any catalog text), and a **clean clear**: it shows each phase's *intended* execution but **not its failure modes**, which still need a prog log per phase.

**Log-name ↔ strat-name bridge.** The log records *internal damage-ability* names; the strat doc and players use *telegraph* names. The agent must bridge them:

| Log ability | Player-facing mechanic |
|---|---|
| Flagrant Fire III | the "Fire" stack/spread orb |
| Blizzard III Blowout | the "Ice" cone hazard |
| Thrumming Thunder III | the "Thunder/Lightning" spread |
| Idyllic / Indulgent / Indolent Will | the "Fire" stack/spread of the GI3 finale |
| Gravity III | the central-tether "Gravity" stack |
| Gravitas | the lingering gravity puddles |
| Double-Trouble Trap | "confetti" (the hot-potato debuff) |
| Tele-Portent / Tele-Trouncing | the teleporter placement / activation |
| Revolting Ruin III | "Ruin III" cleave tankbuster |

---

## Phase map

Dancing Mad (Ultimate) runs **five phases**. Boundaries below are read from the full clear `ApYjk8dZqz7LRbMy` fight 1; each phase transition shows in the log as an **auto-attack-only lull** — the boss stays targetable and keeps auto-attacking the tank but stops casting while it transforms, so the lull itself needs **no raidwide mit** (just the autos).

| Phase | Name | Clear timing | Catalog status |
|---|---|---|---|
| **P1** | OG Kefka ("Merry Go Round") | 0:00 – 3:09 | **Authored** (below) |
| — | *transition* | 3:10 – 3:40 | autos only — no cast damage |
| **P2** | God Kefka | 3:41 – 6:19 | skeleton below; mechanics not yet authored |
| — | *transition* | 6:21 – 7:14 | autos only — no cast damage |
| **P3** | Chaos and Exdeath | 7:15 – TBD | uncharted |
| **P4** | Kefka Says | TBD | uncharted |
| **P5** | Ultimate Kefka | TBD – 18:40 (kill) | uncharted |

Phase names are the static's. P1/P2 boundaries are confirmed against the clear; P3 starts ~7:15; the P3→P4 and P4→P5 boundaries are **not yet pinned** (distinctive abilities noted below for when they're charted).

**P2 (God Kefka) skeleton** — the clean-clear order, bracketed by the two **Ultimate Embrace** busters:
Ultimate Embrace #1 (solo MT, ~1.25M *physical*) → **Forsaken** (raidwide, ~50% mit) → **spell-towers** (`The Path of Light` telegraph + `Spelldriver`/`Spellscatter`/`Spellwave` + the `Spells' Trouble` / `Unknown_13DC/DD/DE` Magic-Vuln puzzle — the static's old prog wall) → **Past's End / Future's End** cycles → **Wings of Destruction** → Ultimate Embrace #2 (shared 2-tank). Failure modes (esp. the tower vuln puzzle and the UE#2 share) are **not** visible in this clean clear and need a P2 prog log.

**Later-phase ability fingerprints** (for future charting, not yet placed):
- **P3 Chaos and Exdeath** (~7:15+): Bowels of Agony, Stray Flames, Inferno, Cyclone, Thunder III (~1.47M TB), Tsunami, Earthquake, **Nothingness** (~10M single-target soaks).
- **P4 / P5** (Kefka Says / Ultimate Kefka): the `Ultima *` set (Ultima Upsurge / Repeater / Blaster), Grand Cross, Chaotic Holy (~11M) / Chaotic Flare / Chaotic Flood, White/Black Antilight.

---

# P1: Merry Go Round

The opening phase. A `Graven Image` statue drives three mechanic sequences (GI1/GI2/GI3) interleaved with two `Revolting Ruin III` cleave tankbusters and recurring `Hyperdrive` MT busters, closing on a Thunder + Fire finale. Fight 37 wiped at 3:10 still inside this phase — nothing in the log crosses into P2.

## Opening — Revolting Ruin III (cleave tankbuster)

**Observed.** `Revolting Ruin III`, magical, appears as two ability rows (max unmit ~993k and ~895k), 4 hits each. First cast window ~0:15–0:19, both hits landing on the WAR (MT). A second cast ~1:38–1:42 lands both hits on the PLD (OT) — i.e., the tank taking both hits *swaps* between the two casts. No Damage Down attached.

**Resolution.** **Cleave tankbuster** ([primitives.md](../primitives.md#tankbuster), cleave variant). Hits #1 enmity, then #2 enmity ~1s later. The static resolves it by **tank-swapping so both hits land on the current MT** (the off-tank avoids the second AOE; GI2's cast adds an OT invuln on the swap). The two summary rows are the two hits (slightly different magnitudes), not two different abilities. Roles reverse across the two casts: WAR eats the first pair, PLD eats the second.

**Open questions.** Exact enmity-order timing between the two hits; whether the vuln/duration forces the swap or it's positional only.

## Hyperdrive (MT tankbuster)

**Observed.** `Hyperdrive`, magical, 12 hits across the pull, max unmit ~588k. Bursts entirely onto the MT at ~1:06–1:11 and again ~2:16–2:21 (multiple hits ~520–588k each in quick succession). No other role targeted.

**Resolution.** **Multi-hit MT tankbuster** ([primitives.md](../primitives.md#tankbuster), single-target, instant-cast) — a 3-hit buster on #1 enmity with an AOE around the target, so the MT must be separated from the party. Confirmed P1. The repeated same-second hits are the multi-hit nature, not separate casts.

**Open questions.** Exact hit count per cast (log shows clusters; strat says 3); how the AOE-around-target radius interacts with party positioning at each window.

## Graven Image 1

The first statue sequence. Knockback tethers → Fire/Ice orb resolve → lasers + towers → confetti → Lightning/Ice orb resolve.

### KB tethers (statue → role group)

**Observed.** No distinct damage event isolates this; inferred from the strat doc and the role-grouped follow-ups around the GI1 window.

**Resolution.** **Knockback tether** ([primitives.md](../primitives.md#tether), knockback variant). The statue tethers to **all DPS or all Supports**; the tether resolves as a knockback the players *ride* to their assigned spot (a directed-positioning knockback — see [Knockback](../primitives.md#knockback)). DPS resolve East, Supports West.

**Open questions.** Whether the tether produces any logged event (damage or debuff) we can key on, or whether it is purely positional and invisible to the log.

### Fire / Ice orb telegraph

**Observed.** `Flagrant Fire III` (magical, ~203k, appears as two rows: 16 hits and 6 hits). At **0:38** Kefka applies **1s Magic Vulnerability Up to all 8** — a brief two-hit amplifier (the second fire hit lands into the fresh vuln, explaining a larger second instance). `Blizzard III Blowout` (magical, ~217k, 4 hits) is the ice component; it **killed the DRG at 0:57**.

**Resolution.** Kefka spawns **two rings of orbs**: top ring = **Fire**, bottom ring = **Ice**. Fire = telegraphed **stack-or-spread** ([Stack](../primitives.md#stack) / [Spread](../primitives.md#spread)); Ice = telegraphed **90° cone hazards** ([Hazard](../primitives.md#hazard-avoidable-ground-aoe)) to dodge. Any orb may carry the **`?` inverter** ([Telegraph Inversion](../primitives.md#telegraph-inversion-the--modifier)): `?`Spread→Stack, `?`Ice→stand-in-the-AOE. DPS resolve the stack/spread East, Supports West; melee/tanks spread N/S or E/W on the safe half. The all-party 1s Magic Vuln is **by design** (the fire's own two-hit amplify), *not* a failure marker — see [fundamentals.md](../fundamentals.md#vulnerability-debuffs).

**Open questions.** Which `Flagrant Fire III` row is the stack vs. the spread resolution; exact cone geometry; confirm Blizzard III Blowout is the ice cone rather than a separate ice mechanic.

### Lasers → towers

**Observed.** At **0:43**, `Graven Image` applies **4s Magic Vulnerability Up to exactly 4 players** (RDM, MT, OT, VPR). `Explosion` (magical, ~334k, 8 hits) lands on the **other 4** (SCH, SGE, DRG, DNC) around 0:46–0:47. No Damage Down on the soakers.

**Resolution.** Lasers fire at **2 Supports + 2 DPS at random**, applying a vuln **and spawning a tower under each laser'd player's feet** ([Tower](../primitives.md#tower)). The four laser'd (now vuln'd) players step out; the **four clean players soak** the towers in a fixed left-to-right priority (H1 > T1 > M1 > R2). This is a textbook **8-player budget fork** ([fundamentals.md](../fundamentals.md#the-8-player-budget)): the laser'd four are *removed from the soak pool by design* (a vuln'd soaker dies), leaving exactly four clean bodies for four towers. `Explosion` hitting precisely the non-vuln'd four is the soak, resolved correctly here (survivable, no Damage Down).

**Open questions.** Confirm tower count is exactly 4 single-soaker. *Resolved (pull 52): `Explosion` is the **soak** damage — it lands on the four clean soakers (~160–313k unmit, ~100–112k taken, magical, no Damage Down) and is survivable. It is **real, mittable magical damage**, not a free hit: the soakers lived on heavy carryover party mit (Holos/Samba/Collective Unconscious/Magick Barrier/Shake It Off/E.Prog). "Positional" does not mean "no mit" — see [fundamentals.md](../fundamentals.md) → "Mit follows damage, not mechanic type."*

### Confetti (Double-Trouble Trap)

**Observed.** At **0:45**, `Environment` applies `Double-trouble Trap` (5s) to **one Support (SCH) + one DPS (DNC)**. The debuff later reappears on other players (e.g., the VPR at 0:50 with a long duration; the MT at 1:59). `Double-Trouble Trap` damage is the **largest in the fight** (max unmit ~1.63M, 26 hits across the pull) and **killed the SGE at 0:53, the DNC at 2:01, the SCH at 2:51**.

**Resolution.** **Debuff pass / hot-potato** ([primitives.md](../primitives.md#debuff-pass-hot-potato), knockback variant). On expiry it deals a shared AOE around the holder and **knocks nearby players back, passing the debuff to one of them**. Three players must stack with each confetti holder to share the AOE; the holder stands behind the group to **knock them through** and pass it on. The strat pairs **Support-with-Support-confetti, DPS-with-DPS-confetti** (Supports North, DPS South in later iterations). The chain *must* continue or the fight ends early. The ~1.63M solo hits are **failed shares** (too few catchers → undivided AOE → death), the same fingerprint as a failed stack.

**Open questions.** Exact required catcher count per pass (strat says 3 others); how many total passes the chain demands before it ends; whether role-locking is strict.

### Lightning / Ice orb resolve

**Observed.** At **0:54–0:55**, Kefka applies **Damage Down to 5 players** (DRG, DNC, SCH, MT, VPR; ~61s duration). Coincides with the ice damage (`Blizzard III Blowout` killed the DRG at 0:57).

**Resolution.** A **second orb telegraph** before the confetti knockback fully resolves: top ring = **Lightning**, bottom = **Ice**, again with possible `?` inversion (`?`Lightning→stand-in-it, true Ice→avoid). The 5 Damage Downs are **failed avoidables** ([Hazard](../primitives.md#hazard-avoidable-ground-aoe)) — players clipped the ice cones / mis-read the lightning placement. Damage Down here is the unambiguous **non-fatal failure marker** ([fundamentals.md](../fundamentals.md#damage-down)): 5 players got away with a mistake they shouldn't have (the DRG did not — the ice killed them). This is an **individual-punishment** mechanic, so 5 Damage Downs ≈ 5 individual mis-resolves.

**Open questions.** Which damage ability stamped each Damage Down (source is Kefka, but the exact failed-orb ability isn't isolated); whether lightning and ice resolve simultaneously or staggered.

## Graven Image 2

The second statue sequence. Gravity/Rock tethers over quadstack puddles, a second `Revolting Ruin III` + half-room cleave, a second gravity set, a second confetti.

### Gravity / Rock tethers (quadstack puddles)

**Observed.** `Gravity III` (magical, max unmit **~1.07M**, 13 hits) **killed the OT at 2:04**. `Gravitas` (magical, ~213k, **62 hits** — heavily pulsing) runs through the window. `Vitrophyre` (magical, very low ~22k, 16 hits) appears here. `Gravitational Wave` (magical, ~218k, **8 hits** — full party). At **1:55** `Graven Image` applies **Damage Down to 4 players** (SCH, MT, VPR ~59–61s; DNC only 4s). *VOD frame at 2:02 (X:6.1 Y:6.0, arena center): purple gravity puddles cover the ground; multiple floating `Gravity III 0` / `Gravity III 0 (-20% blocked)` texts (shared hits fully eaten by Divine Veil + Eukrasian Prognosis shields) alongside the lone ~901k instance — both outcomes of the same detonation visible at once.*

**Resolution.** The statue tethers all players in two sets: **central tether → gravity players**, who **drop purple gravity puddles on the ground**, and **right-side tether → rock players** (`Vitrophyre`, a low-damage [Spread](../primitives.md#spread)) whose **rock spread detonates the puddles**. **The gravity damage comes from the puddles, not a player-marker stack** — players **quadstack on each puddle** to divide the detonation (`Gravity III`); the strat notes a quadstack "does the same damage as a 2-stack," i.e. the puddle's damage is fixed and split by the bodies soaking it. This is a **shared puddle soak** — a [Hazard](../primitives.md#hazard-avoidable-ground-aoe) you *stand in and share* rather than dodge, resolved like a [Stack](../primitives.md#stack). It is **shieldable**: in the 2:02 frame, sharers with Divine Veil + E.Prog took `Gravity III` as **0**. `Gravity III` is therefore **confirmed shared damage**; the OT's lone **~1.02–1.07M** (6 hits, vs. the SGE/DRG's ~110–123k splash) is a **soaked-puddle-solo death** — too few bodies on his puddle. Not a mit problem — ~868k *taken* on one body is unsurvivable; the fix is putting more bodies on the puddle, not adding cooldowns ([fundamentals.md](../fundamentals.md#mit-gap-detection)). `Gravitas` is the **lingering puddle field** ([Hazard](../primitives.md#hazard-avoidable-ground-aoe), persistent-puddle variant — its 62 small hits are the puddles ticking before detonation). `Gravitational Wave` is an 8-target **raidwide** ([Raidwide](../primitives.md#raidwide)). The 1:55 Damage Downs are failed avoidables in this window (ice AOE or rock-spread overlap).

**Open questions.** Confirm the intended soak count per puddle is **4** (strat says "quadstack") and how many puddles spawn per set; whether `Vitrophyre` is the rock-spread hit itself or specifically the puddle-detonation trigger; exact role of `Gravitational Wave` in the timeline (its own cast vs. part of gravity resolution).

### Ruin III #2 + half-room cleave

**Observed.** The second `Revolting Ruin III` cast (~1:38–1:42, both hits on PLD/OT — see Opening entry). `Guardian's Will` buff visible on the OT through this window (PLD mitigating the buster).

**Resolution.** Same cleave tankbuster as the opening, resolved with **OT invuln + tank swap** facing the buster North. The statue also summons an **orb for a half-room cleave** — dodge to the safe half ([Hazard](../primitives.md#hazard-avoidable-ground-aoe)). A second half-room cleave follows later in GI2.

**Open questions.** Which log ability is the half-room cleave damage (not yet isolated — may be a low/zero-damage telegraph if cleanly dodged every pull seen).

### Confetti #2

**Observed.** `Double-Trouble Trap` reappears (the MT at 1:59, 49s duration; further chain into the 2:48–2:51 window where the SCH takes ~1.63M and dies at 2:51).

**Resolution.** Same **debuff pass** as GI1 (Supports preposition North, DPS South), here players are **knocked back through the gravity puddles to pop them** — the confetti knockback doubles as the puzzle solution. Confetti holders then move back to help soak.

**Open questions.** How the GI2 confetti chain interleaves with the gravity-puddle pop timing; whether the 1.63M SCH death is a failed share or a vuln-amplified catch.

## Graven Image 3

The third statue sequence. Teleporters (Tele-Portent), Confused/Sleep tethers + a confetti, closing on the Thunder + Fire finale.

### Tele-Portent (teleporters)

**Observed.** At **2:33**, Kefka applies `Tele-Portent` to **all 8 players, twice each** — two debuff instances per player with **different durations (7s and 10s)**. `Tele-Trouncing` (unknown school, **27 hits, 0 damage**) fires in this region.

**Resolution.** **Teleporter placement.** Each player receives **2 arrow debuffs** (the 7s + 10s instances = the two arrows); when each expires it **drops a teleporter**, placed so the arrows point **clockwise** around the arena. Players read their **leftmost arrow debuff** to determine where they go. `Tele-Trouncing` is the teleporter *activation* — **0 damage, pure positioning** ([Knockback](../primitives.md#knockback) / displacement, here a forced teleport). The strat notes teleporters are server-tick-unreliable; fixed spots mitigate this.

**Open questions.** Whether the 7s/10s split maps to a fixed "first TP / second TP" ordering we can read per player; whether matching-vs-differing arrow pairs are distinguishable in the log (both show as two `Tele-Portent` instances).

### Confused / Sleep tethers + confetti

**Observed.** At **2:54**, `Graven Image` applies **`Confused` to 3 players** (SGE, OT, MT) and **`Sleep` to the rest** (DNC, DRG, RDM, VPR) — 6s durations — plus a 1s Magic Vuln to most. A `Double-Trouble Trap` chain is live in the same window.

**Resolution.** **Effect/CC tethers** ([primitives.md](../primitives.md#tether), CC variant): **left tether = Confused, right tether = Sleep**. Resolution is positional — Supports NW, DPS SE — and players go to **fixed tether spots regardless of which tether they hold**. Simultaneously a confetti is resolved by being **knocked back through the boss**. The CC statuses are the danger: a Confused/Slept player can't react to the incoming finale (see compound-failure note in [Tether](../primitives.md#tether)).

**Open questions.** How the CC duration overlaps the finale cast (did anyone get caught Slept/Confused into the Thunder/Fire? — the MT held Confused at 2:54 and died in the finale, a likely carryover). *Resolved: the **left tether = Confused, right tether = Sleep** mapping is consistent across pulls.*

### Finale — Thunder + Fire

**Observed.** At **2:54** and **3:07**, a burst of finale damage:
- `Idyllic Will` (magical, **14 hits, max unmit 1,477,520**) — hits all 8 ~120–220k each **except the MT took 1,477,520** (≈10× the per-player share), **killing the MT at 2:56**.
- `Indulgent Will` (magical, ~191k, 6 hits) — a subset.
- `Indolent Will` (unknown school, ~206k, 6 hits) at 3:07.
- `Thrumming Thunder III` (magical, ~210k; two rows, 6 + 8 hits) — scattered targets; **killed the DNC & DRG at 3:10**.
- A cluster of finale deaths at 3:10 attributed to `Flagrant Fire III` and `Thrumming Thunder III` (RDM, SGE, OT, DNC, DRG) — the wipe.
- *(pull 52)* `Ave Maria` (magical, 10 hits, **~219k**) at **3:07** and a finale `Flagrant Fire III` (**~213k**) at **3:08** — two ~200k **raidwides back-to-back**, with the party at only **~10% mit** in this window. **the VPR — lacking the E.Prog shield the rest of the party had — died at 3:11** to the finale `Flagrant Fire III`; a 1s Magic Vuln (Kefka) stamped at 3:08 amplified. Here the `...Will` stack split **cleanly** (no 1.48M solo), so this death was a **raidwide death (under-mit + missing shield)**, not a failed share.

**Resolution.** The GI3 closer: **"final Thunder + Fire"** (a static-spread/stack resolution). `Thrumming Thunder III` = the **Thunder spread** ([Spread](../primitives.md#spread); per-player scattered hits). The **`...Will` family = the Fire stack/spread damage events** — Idyllic/Indulgent/Indolent are the internal damage names behind the "Fire" telegraph. The **1.48M Idyllic Will on the MT is a failed share** ([Stack](../primitives.md#stack)): the ~10× multiple over the clean ~130k others took *is* the count of missing bodies — the MT ate a stack/spread ~solo and died. The seven clean ~130k hits are the *correct* split. The strat offers a stack version (Supports on waymark 3, DPS on 1) and a spread version. Pull 52 shows the closer also **layers true raidwides** — `Ave Maria` and a finale `Flagrant Fire III` (~200k each) — *on top of* the Fire stack/spread (`...Will`) and the Thunder spread (`Thrumming Thunder III`). So the finale is a **dense stack of magical hits (stack + spread + two raidwides) across 2:54–3:11** that demands *sustained* party mit and a barrier reaching all 8, not a single cooldown — the window where a party that front-loaded its mit (e.g. heavy on Wave Cannon) runs dry and loses a body.

**Open questions.** Decompose the three `...Will` variants — is each a distinct sub-mechanic (spread vs. stack vs. a third), or successive iterations of one Fire resolution? Which is the by-design clean value vs. the failure value for each. Whether the MT's death was a stack-share failure or a CC-tether carryover (the MT held `Confused` at 2:54, which may have prevented repositioning into the stack — a likely compound failure).

---

# Unplaced / recurring damage (needs timeline placement)

Abilities seen in the summary not yet pinned to a specific GI sequence:

- **`Light of Judgment`** (magical, ~300k) — a **repeating raidwide** ([Raidwide](../primitives.md#raidwide)). *Placed (pull 52): fires at **1:03 and 2:13**, ~300k unmit, ~31% mit (Reprisal + Feint + Addle + Kerachole + E.Prog), ~150–165k taken. The high summary hit-count is the two 8-target casts plus their second ticks.*
- **`Wave Cannon`** (magical, ~365k, **8 hits** — full party) — an 8-target **raidwide**. *Placed (pull 52): fires at **0:43**, the single biggest P1 raidwide; the static stacks heavy party mit here (~40–60%), comfortably over-covered.*
- **`Attack`** (physical ~159k / unknown ~453k) — auto-attacks on the MT; the ~453k "unknown" instances on the VPR at 2:56–2:57 are likely cleave/positional rather than true autos. *Open: confirm the high "Attack" hits aren't a mislabeled mechanic.*

# P2: God Kefka

P1 transforms into **God Kefka** across an auto-only lull (3:10–3:40 in the clear — see [Phase map](#phase-map); no mit needed there). The phase is bookended by two **Ultimate Embrace** tank busters and built around one signature body-check: the **spell-towers** (`Spells' Trouble` vuln puzzle), the static's longest-standing P2 wall.

Source for this section: the clean clear `ApYjk8dZqz7LRbMy` f1 (intended execution + values) cross-referenced with two wipes from `8wTfHmWy2JgrcbQL` — **f33** (4:33, wiped in the spell-towers) and **f21** (6:27, wiped to Wings of Destruction at the phase end). All players anonymized to role labels.

## Ultimate Embrace #1 (opening tank buster)

**Observed.** At **3:41–3:42** (clear), `Ultimate Embrace` — **physical**, max unmit ~1.25M — lands on **both tanks** (PLD ~1.25M → 26k taken behind Guardian + Holy Sheltron + The Spire / Intersection / Divine Veil shields; DRK ~1.20M → 133k at 72% mit). No Damage Down. This is the fight's first big **physical** hit — contrast P1's all-magical profile ([fundamentals.md](../fundamentals.md#damage-types-physical-vs-magical)).

**Resolution.** **Proximity tank buster** ([primitives.md](../primitives.md#tankbuster)), physical — it targets the **nearest and farthest players** (by distance, *not* #1/#2 enmity), so the two tanks deliberately position as the nearest and farthest bodies to eat both hits. This is why both tanks show ~equal ~1.25M unmit. Each targeted tank covers their hit with **stacked personal mit + a shield wall** (or an invuln — see below). Because it's **physical**, magic-weighted mit (Dark Mind, Magick Barrier) is partly wasted — favour all-school mit (Rampart, Reprisal, Guardian/Shadowed Vigil) + raw shields.

**Notes for the agent.** Targeting is **proximity-based**, so a non-tank caught as the nearest/farthest body would eat a ~1.25M physical buster — a positioning failure, not a mit one. The static's sheet models UE#1 as a *solo MT invuln* (WAR Holmgang / PLD Hallowed) and UE#2 as the shared 2-tank Kitchen Sink; both are valid ways to cover the two proximity targets (classify by outcome).

## Forsaken (raidwide)

**Observed.** At **3:56 and 3:58** (clear), `Forsaken` — magical, 8-target, two pulses — at ~50% mit: first pulse ~210–290k unmit → ~105–132k taken; second pulse ~480–573k unmit → similar taken behind the heavier stack (Reprisal + Feint + Addle + Seraphic Illumination + Shield Samba + Collective Unconscious + Sacred Soil + a barrier). No deaths, no Damage Down.

**Resolution.** **Raidwide** ([primitives.md](../primitives.md#raidwide)), two-hit, magical — designed party damage. The ~50% realized mit (a full party stack + barrier) covers it comfortably; a "designed party damage" window, not a failure point. `Forsaken Bonds` (in the fight-wide summary) is a related tethered/chain variant, not isolated to a timestamp here.

**Open questions.** Whether the two pulses are one cast's double-hit or two casts; the role of `Forsaken Bonds` (tether/chain variant) in the P2 timeline.

## The spell-towers — `Spells' Trouble` vuln puzzle (THE P2 WALL)

**Observed.** At **3:58** (both logs) `Environment` stamps **all 8 players** with `Spells' Trouble` **×4** (~32–85s) plus one of three assignment debuffs — `Unknown_13DC` / `Unknown_13DD` / `Unknown_13DE` (~12–43s, refreshed ~4:10 and ~4:20). `The Path of Light` (unknown school, **0 damage**) telegraphs each resolve ~1s prior. The towers then resolve as **eight hits on a ~10–11s cadence** (clear: **4:10 / 4:20 / 4:31 / 4:41 / 4:52 / 5:02 / 5:13 / 5:23**), each dealing `Spelldriver` / `Spellscatter` / `Spellwave` (magical); resolved cleanly these land **~95–190k** per player. **Odd towers (1/3/5/7) are spell-only; even towers (2/4/6/8) add a clone bait** — `Future's End` on towers 2 & 6, `Past's End` on 4 & 8 (see next entry). Brief 1–2s Magic Vulns (Kefka) stamp the resolves.

**Failure (f33, 4:33).** The **RDM took `Spellwave` 1,935,022 (~1.74M taken)** at 4:20 — ~10× the clean ~150–190k share — and **died at 4:23**; the missing body then cascaded the whole party 4:28–4:31. The **soak-while-vuln'd / wrong-spell signature**: a player resolved the wrong spell (or resolved it carrying the magic vuln), ate an undivided ~1.9M, and the broken body count wiped the follow-up ([fundamentals.md](../fundamentals.md#the-8-player-budget)).

**Resolution.** A **layered body-check**. The `Unknown_13DC/DD/DE` debuffs are **group/rotation-assignment markers, NOT spell-type tags** (the earlier "DC = stack, DD = cone, DE = spread" guess is *wrong* — cross-referencing the clear's debuffs against the spells each holder took shows no such 1:1 mapping, and the debuffs re-roll every tower). What actually encodes the split is the **debuff duration**: at each set, four players carry a long-lived assignment and four a short one — the long-duration group **soaks the spells** for the next towers while the short-duration group **baits the clones** (verified at 4:31, where the four given a 52s debuff all took `Spelldriver`/`Spellscatter`/`Spellwave` at Tower 8 while the other four took `Past's End`). The **spell *sub-type*** a soaker takes (`Spelldriver` = stack · `Spellscatter` = cone · `Spellwave` = spread) is then purely **positional**, set by the raidplan's POV rule — the towers "anchor your POV for left/right for all of Forsaken," **supports resolving stack/cone on the left, DPS the spread on the right**. Each spell is divided among the correctly-positioned bodies to the ~95–190k share; the interleaved [Past's / Future's End](#pasts-end--futures-end) clone shots are baited by the off-group in the same window ("EVERYONE baits; mis-turned clones wipe the party"). **Mit does not fix the *failure*** — the ~1.9M (f33) is an unsoaked/mis-positioned spell, solved by playing the assignment, not cooldowns. **But the resolve damage itself is mit-worthy:** the spell shares (~95–190k) are real magical damage that **goes out on every tower set across the sequence**, and each resolve should be covered with party mit (positioning and mit are *separate axes* — [fundamentals.md](../fundamentals.md) → "Mit follows damage, not mechanic type"). The clean clear ran the waves at only ~0–10% mit *because Forsaken 14s prior had drained the 90s cooldowns* — and the **chunkiest exposure is the *early* towers, not the late**: Towers 2 (4:20) and 5 (4:52) ran at literal **0% mit** in the clear (the 30s healer oGCDs land in their recovery gaps, Reprisal isn't back until ~4:56), taking ~107–201k and ~80–170k raw. A staggered plan covers each resolve instead — lead with healer oGCDs on T1/T3/T4, **hold one DPS mit (Addle, −10% magic) off Forsaken for the bare Tower 2**, spend a saved SGE Holos on the bare Tower 5, and let recharged Reprisal cover T6–T7 (see the AI Mitty "God Kefka" tab).

**Open questions.** Which of `Spelldriver`/`Spellscatter`/`Spellwave` is canonically stack vs cone vs spread (inferred above from share-distribution, not confirmed against the raidplan geometry); what the `Spells' Trouble ×4` stacks track and what the DC/DD/DE *letters* (vs durations) select; whether the per-wave magic vuln is a by-design two-hit amplifier (like P1's fire) or a failure marker. **Strat reference:** the static's tower raidplan — <https://raidplan.io/plan/UATE__aDcw1-bgVv> — decode it with `py scripts/fetch_raidplan.py <url>` (renders each step to FFXIV clock/compass callouts). It's a group- and comp-specific solution (a "Rinon" variant), so treat its exact waymark positions as one static's plan, not the canonical mechanic.

## Past's End / Future's End (the time mechanic)

**Observed.** `Past's End` and `Future's End` (both magical, ~150–176k max unmit) fire **on the even towers**, not as a separate phase: clear shows `Future's End` at 4:19–4:20 (Tower 2) & 5:01–5:02 (Tower 6), `Past's End` at 4:40–4:41 (Tower 4) & 5:22–5:23 (Tower 8) — each a two-tick hit, ~10–27% mit, ~60–120k taken. No deaths in the clear; in f33 `Past's End` (~65–165k) landed alongside the lethal Spellwave.

**Resolution.** **Dodgeable directional AOEs from the clones** ([Hazard](../primitives.md#hazard-avoidable-ground-aoe), avoidable). God Kefka's clones fire a large AOE either **in front of or behind** themselves; `Past's End` and `Future's End` are the two shots, read off each clone's facing and **dodged to the safe side**. Not a soak and **not mit-solved** — taking the full AOE is the failure. Player facing/position isn't in the log, so a clean dodge reads as low/zero and a clip reads as the ~60–120k hit seen here (the clear's mid-size values are clips/edge damage, not a designed party-wide soak). Per the static's tower raidplan this is **baited** ("EVERYONE baits") in the **same window as the spell-towers** — the party turns the clones to controlled facings, and **mis-turned or late clones wipe the party** — so it's tightly coupled to the tower resolution, not an independent dodge.

**Open questions.** Which of Past's / Future's End is the **front** shot vs the **behind** shot; how many clones fire per set and the safe-spot geometry; whether the ~60–120k in the clear is unavoidable chip or just imperfect dodges; whether the clone shots interleave with the spell-tower waves or are a distinct sub-phase.

## Wings of Destruction (phase-end heavy hit)

**Observed.** At **6:11–6:12**, `Wings of Destruction` — magical, two-tick. **Clear:** hits **only the two tanks** (PLD + DRK) — ~384–669k unmit at ~57–61% mit → ~166–247k taken, survived (the summary's "4 hits" = 2 tanks × 2 ticks, *not* 4 players). **Failure (f21):** with the PLD already down (died 6:12), Wings landed on **four non-tanks** (DRG/BLM/BRD/AST) at ~985k–1.13M unmit, only 27% mit → ~720–824k taken → **dead 6:14**; the DRK ate its share at 75% mit and lived.

**Resolution.** A **two-tank mechanic** — by design **only the two tanks are hit** (each takes their own ~669k magical hit, covered by tank mit; the clear's unequal PLD vs DRK values say it's two tank-targeted hits, not one shared stack). A non-tank taking Wings is a **positioning / tank-handling failure**, *not* a party-mit gap — so it is **not** a raidwide and party %-mit is the wrong tool; the fix is the two tanks being the only bodies in the hit. The f21 wipe is precisely that: a tank down/out of position left the hit to catch four squishies for ~800k each (lethal). [primitives.md → Tankbuster](../primitives.md#tankbuster), two-tank variant.

**Open questions.** The exact positioning rule that keeps Wings on the tanks and off the party (proximity? a tank-only target? tanks intercepting a line?); what killed the PLD at 6:12 in f21 (the trigger that cascaded the party into Wings).

## Ultimate Embrace #2 (phase-end shared buster)

**Observed.** At **6:18–6:19** (clear), a second `Ultimate Embrace` — physical, ~1.25M max unmit — on **both tanks** at **75–77% mit** → ~156–177k taken (survived). In f21 the party had already collapsed to Wings (6:14) before a clean UE#2; the trailing 6:19–6:25 deaths are the wipe completing.

**Resolution.** **Proximity tank buster** ([primitives.md](../primitives.md#tankbuster)), the bookend twin of UE#1 — same **nearest + farthest** targeting, with the two tanks positioned as the nearest/farthest bodies. Taken here as a 2-tank covered hit (~75–77% mit). The static's sheet models UE#2 as the shared "Kitchen Sink" buster (vs UE#1's solo invuln) — consistent with both tanks showing ~equal unmit here.

**Open questions.** Whether the two Embraces share a recast/positioning pattern that forces the invuln-vs-Kitchen-Sink split the sheet uses, or it's a free choice.

---

# Catalog conventions used here

- Mechanics are classified **by outcome, not strategy** ([CLAUDE.md](../../CLAUDE.md)): a non-standard execution that survived is a success, flagged as an observation.
- Damage Down marks **non-fatal failures** and is read as a "got away with it" signal, never as a survivability factor ([fundamentals.md](../fundamentals.md#damage-down)).
- Vulns are **ambiguous** (by-design or failure) and always traced to their source ability before classifying ([fundamentals.md](../fundamentals.md#vulnerability-debuffs)).
- Body-allocation mechanics (towers, stacks, confetti chain) are read against the **8-player budget** ([fundamentals.md](../fundamentals.md#the-8-player-budget)).
