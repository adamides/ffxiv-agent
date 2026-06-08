# Mit-sheet conventions

A reusable model for laying out a **comp-agnostic FFXIV mitigation plan** — the player-facing
"press X at Y" sheet a static reads during a pull. This is reference material for *planning mode*
(authoring a forward mit plan); it is deliberately generic, with no fight-, comp-, or
tool-specific details. Pairs with the [glossary](../CONTEXT.md) (Party Mit, Extra, Pre-shield)
and the planning-mode discipline in [knowledge/fundamentals.md](../knowledge/fundamentals.md).

## Core idea: role slots, not jobs

Columns are **roles**, not specific players, so one sheet serves any comp that fits the role
template. A cell holds the cooldown(s) that slot presses on that row. A typical layout:

```
Time | Activate | Mechanic | Tank 1 | Tank 2 | SCH | SGE | WHM | AST |
                            Melee 1 | Melee 2 | Phys Ranged | Caster | Extras | Notes
```

Rows run in **timeline order** under sub-phase dividers.

## Column conventions

- **Party Mit** = a slot's *generic raid mitigation* — named by role, resolved per job:
  PLD Divine Veil · WAR Shake It Off · DRK Dark Missionary · GNB Heart of Light. **Reprisal** is
  the universal tank party mit. This keeps the tank columns comp-agnostic.
- **Extras** = a spare cooldown layered *only if free*, not part of the scheduled budget — e.g.
  PLD Passage of Arms (a positional cone, useful only on grouped windows), or a job-specific bonus
  like RDM Magick Barrier. Distinct from a Party Mit slot.
- **DPS columns are role-generic:** Melee = Feint, Caster = Addle, Phys Ranged = the role's −15%
  party mit (Tactician / Shield Samba / Troubadour). Job-specific extras go in **Extras**.
- **All four healer columns filled as a menu.** A real comp runs one regen (WHM **or** AST) + one
  barrier (SCH **or** SGE); each player reads only their two columns. Filling all four keeps the
  sheet comp-agnostic.

## The `Activate` column

Separate **when to press** from **when it matters**. `Activate` = the recommended *press* time,
typically ≈ snapshot − 3s, earlier for pre-shields or tools with a ramp/early-pop. Useful glyphs:

- `↪` — mit **carried over** from a previous press (still active, no new button)
- `↻` — **re-press** (the cooldown has come back and is used again)
- `✓` (in Extras) — an extra mit here is *helpful but optional*

## Barrier columns stay oGCD-lean

A barrier healer's GCD heals/shields cost a damage GCD, so schedule them sparingly: lean on
**oGCD** mitigation/shields (Kerachole / Holos / Panhaima; Sacred Soil / Expedient / Fey
Illumination) and reserve GCD shields (Recitation→Succor, Eukrasian Prognosis) for the few windows
that truly need a full-party barrier.

## Tankbusters live on tank-pairing tabs, not the party sheet

Keep the main party-mit sheet free of tank-survival detail. Put **busters on per-pairing tabs**
(WAR/PLD, GNB/DRK, …) with the two tanks' personal mits and invuln assignments. Common shorthand:

- **Kitchen Sink** — throw everything *short of* an invuln at a buster
- **Invuln** — a true invulnerability (Hallowed Ground, Holmgang, Living Dead, Superbolide)

A buster row on the main sheet therefore has **empty party columns** — tank survival is resolved on
the pairing tab; any party-wide soak damage is covered by oGCD + carryover.

## Player view vs. authoring layer

The sheet a player reads should be **lean** ("press X at Y"). The supporting analysis — damage
profile per row, Σ%mit, cooldown-availability checks — belongs in a separate **authoring backing
layer**, not the player view. Two things *are* worth surfacing on the player sheet itself:

- a **one-glyph damage-school tag** per row (physical / magical), so school-locked mit lands right;
- **no %-mit cells on tower / failure rows** — those want a **pre-shield**, not a party %-cooldown
  (mit follows damage, not mechanic type — see
  [fundamentals.md](../knowledge/fundamentals.md)).
