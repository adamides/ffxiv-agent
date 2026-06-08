# FFXIV Job Defensive Toolkits

This file catalogs the **survival-relevant** toolkit of each job: mitigation, shields, defensive heals, invulnerabilities, knockback resistance, and cleanses. It deliberately **excludes** DPS/rotation actions — mit analysis does not need them.

## How the agent uses this file

The data-fetching script decodes the **buff/status names** active on each player at the moment of every hit. The agent's core loop is:

1. Read a decoded buff name from the log (e.g., `Holy Sheltron`, `Reprisal`, `Kerachole`).
2. Look it up here via its **Log status(es)** field to learn what it does.
3. Use the **Tags** and **Coverage** to reason across jobs ("what party mit was up?", "was the magical raidwide covered by magic-appropriate mit?").

Because the log shows *statuses*, the **Log status(es)** field is the join key — it is recorded separately from the action name, since one action often grants several differently-named statuses, and the status name is what actually appears in the data.

## Per-cooldown schema

Each entry records:

- **Log status(es)** — the exact status name(s) as they appear in decoded log buffs (the join key)
- **Effect** — concise mechanical effect (mit %, shield, heal)
- **Scope** — `self` / `targeted` (one ally) / `party`
- **Coverage** — `all` / `physical` / `magical` (links to the Damage Types entry in `fundamentals.md`)
- **Duration / Recast** — seconds (recast captured now for later cooldown-availability analysis)
- **Tags** — controlled vocabulary (below)

## Tag vocabulary

- *Who it protects:* `personal-mit`, `targeted-mit`, `party-mit`
- *Mechanism:* `percent-mit`, `barrier`, `heal`, `enemy-debuff` (reduces the boss's damage *dealt*)
- *Special:* `tank-mit`, `invuln`, `knockback-resist`, `cleanse`

## Role actions are authored once

Role actions (Rampart, Reprisal, Addle, etc.) are shared across every job of a role. They are defined **once** in the Role Actions section below; each job entry lists only its **job-specific** kit and references its role block. This keeps the file DRY — a role action changes in one place.

Numbers are sourced from the official job guide (https://na.finalfantasyxiv.com/jobguide/battle/) at level 100 / current patch. Re-verify after balance patches.

---

# Role Actions

## Tank role actions

### Rampart
- **Log status(es):** `Rampart`
- **Effect:** −20% damage taken; +15% HP recovery from healing on self
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 20s / 90s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`

### Reprisal
- **Log status(es):** `Reprisal` — appears directly in the decoded buff list of the hits it affected (confirmed in fight-6 data, e.g. alongside `Feint` on party-wide hits), even though mechanically it is a debuff on the boss
- **Effect:** −10% damage dealt by nearby enemies — i.e. protects the whole party from the boss's output
- **Scope:** party (via enemy debuff)  **Coverage:** all
- **Duration / Recast:** 15s / 60s
- **Tags:** `enemy-debuff`, `party-mit`, `tank-mit`

### Arm's Length
- **Log status(es):** `Arm's Length`
- **Effect:** knockback/draw-in resistance; applies a slow to melee attackers on hit
- **Scope:** self  **Coverage:** — (positioning, not damage)
- **Duration / Recast:** 6s / 120s
- **Tags:** `knockback-resist`
- **Shared role action:** also available to **melee** and **phys-ranged** (not tank-only). Authored here once; the Melee/Phys-Ranged role blocks reference this entry. (The healer/caster equivalent is **Surecast**, in the Healer role actions.)

> Note: Low Blow (stun), Provoke/Shirk (enmity), and Interject (interrupt) are tank role actions but are **not** survival tools, so they are omitted here.

## Healer role actions

### Esuna
- **Log status(es):** — (removes a debuff; no status granted)
- **Effect:** removes one removable (cleansable) debuff from a target
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** — / 1s (instant)
- **Tags:** `cleanse`

### Surecast
- **Log status(es):** `Surecast`
- **Effect:** knockback/draw-in resistance; also lets casts finish through interruption
- **Scope:** self  **Coverage:** — (positioning, not damage)
- **Duration / Recast:** 6s / 120s
- **Tags:** `knockback-resist`
- **Shared role action:** also available to **casters** (not healer-only). Authored here once; the Caster role block references this entry. (The tank/melee/phys-ranged equivalent is **Arm's Length**, in the Tank role actions.)

> Note: Swiftcast (instant-cast enabler — relevant for emergency heals/raises), Rescue (pulls an ally out of danger), Lucid Dreaming (MP), and Repose (sleep) are healer role actions. Swiftcast and Rescue are situational survival utilities but carry no mit; the others are omitted as non-survival.

## Melee role actions

The melee defensive role kit is thin, and only one entry contributes to party survival analysis.

### Feint
- **Log status(es):** `Feint` — appears in the decoded buff list of the hits it affected (confirmed in fight-6 data, e.g. alongside `Reprisal` on party-wide hits), even though mechanically it is a debuff on the boss
- **Effect:** lowers the target's physical damage dealt by 10% and magic damage dealt by 5% — i.e. protects the whole party from the boss's output, weighted physical
- **Scope:** party (via enemy debuff)  **Coverage:** all (weighted physical)
- **Duration / Recast:** 15s / 90s
- **Tags:** `enemy-debuff`, `party-mit`
- See the damage-types table in `fundamentals.md` for how Feint compares to Addle/Reprisal by school.

### Arm's Length (shared)
- Knockback/draw-in resistance — **see Arm's Length under Tank role actions** (one shared definition; not re-authored here).

> Note: Second Wind and Bloodbath are self-heals (Bloodbath is weak lifesteal), and True North (positional accuracy) and Leg Sweep (stun) are not survival tools — all omitted, mirroring how the Tank block drops Low Blow/Provoke and the Healer block drops Repose. Only Feint matters for a melee's party-mit contribution.

## Phys-ranged role actions

Phys-ranged has **no party-mit role action** — its signature −10% party mitigations (BRD Troubadour, MCH Tactician, DNC Shield Samba) are job-specific and authored under each job. The only survival-relevant role action is the shared knockback tool.

### Arm's Length (shared)
- Knockback/draw-in resistance — **see Arm's Length under Tank role actions** (one shared definition; not re-authored here).

> Note: Second Wind (self-heal) is omitted as a trivial self-heal (mirroring the melee block), and the Grazes (Foot/Leg/Head) and Peloton are non-survival utility. Unlike melee's Feint, phys-ranged carries no party-mit role action at all — all phys-ranged party mit is per-job.

## Caster role actions

The caster role contributes one party-facing mit (Addle) plus the shared knockback tool.

### Addle
- **Log status(es):** `Addle` — a debuff on the boss, but protects the whole party from its output while active (mirrors Feint/Reprisal appearing in the decoded buff list)
- **Effect:** lowers the target's physical damage dealt by 5% and magic damage dealt by 10% — weighted magical
- **Scope:** party (via enemy debuff)  **Coverage:** all (weighted magical)
- **Duration / Recast:** 15s / 90s
- **Tags:** `enemy-debuff`, `party-mit`
- See the damage-types table in `fundamentals.md` — Addle is the magic-weighted counterpart to melee's Feint; on a magic-heavy window Addle out-mitigates Feint.

### Surecast (shared)
- Knockback/draw-in resistance — **see Surecast under Healer role actions** (one shared definition; not re-authored here). Surecast is the healer/caster role action; Arm's Length is its tank/melee/phys-ranged twin.

> Note: Swiftcast (instant-cast enabler — relevant for emergency raises, e.g. RDM Verraise), Lucid Dreaming (MP), and Sleep are caster role actions but carry no mit; omitted as non-survival, mirroring the healer block.

---

# Paladin (PLD)

Role actions: see **Tank role actions**. PLD is the shield/barrier tank — much of its kit is block- and barrier-flavored, and it carries the most party-facing mitigation of the tanks (Divine Veil, Passage of Arms).

### Holy Sheltron
- **Log status(es):** `Holy Sheltron`, `Knight's Resolve` (and `Knight's Benediction` regen)
- **Effect:** −15% damage taken; Knight's Resolve adds a further −15% for 4s; Knight's Benediction regen (250 potency)
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 8s (+4s Resolve) / 5s — gated by 50 Oath Gauge, not the recast
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`, `heal`

### Sentinel / Guardian
- **Log status(es):** `Sentinel`; at Lv.92 upgrades to `Guardian` (+ `Guardian's Will` barrier)
- **Effect:** Sentinel −30%; Guardian −40% **and** a magic barrier nullifying ~1,000 potency of damage
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 15s / 120s
- **Tags:** `personal-mit`, `percent-mit`, `barrier`, `tank-mit`

### Bulwark
- **Log status(es):** `Bulwark`
- **Effect:** raises block rate (blocks a portion of incoming attacks). Block now applies to **all** damage types, but it is per-hit and not a flat % — treat as situational mitigation, not reliable percent-mit.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 90s
- **Tags:** `personal-mit`, `tank-mit`

### Hallowed Ground
- **Log status(es):** `Hallowed Ground`
- **Effect:** invulnerability — impervious to most attacks
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 420s
- **Tags:** `invuln`, `personal-mit`, `tank-mit`

### Divine Veil
- **Log status(es):** `Divine Veil`
- **Effect:** party barrier absorbing 10% of PLD's max HP, plus a heal (400 potency)
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 30s / 90s
- **Tags:** `party-mit`, `barrier`, `heal`, `tank-mit`

### Passage of Arms
- **Log status(es):** `Passage of Arms`
- **Effect:** party members in a cone behind the PLD take only 85% damage (−15%); 100% block for self. Channeled — ends on moving or acting.
- **Scope:** party (positional)  **Coverage:** all
- **Duration / Recast:** 18s / 120s
- **Tags:** `party-mit`, `percent-mit`, `tank-mit`

### Intervention
- **Log status(es):** `Intervention`, `Knight's Resolve` (and `Knight's Benediction` regen on target)
- **Effect:** −10% damage taken on a targeted ally; Knight's Resolve adds −10% for 4s; regen (250 potency)
- **Scope:** targeted ally — **cannot be cast on self.** The self-cast counterpart is [Holy Sheltron](#holy-sheltron); both spend Oath Gauge, so a PLD's Oath budget is shared between protecting itself (Holy Sheltron) and protecting an ally (Intervention).  **Coverage:** all
- **Duration / Recast:** 8s (+4s Resolve) / 10s — gated by 50 Oath Gauge
- **Tags:** `targeted-mit`, `percent-mit`, `tank-mit`, `heal`
- **Agent note:** an `Intervention` status on a player always came from the *other* tank (a PLD), never from that player on themselves — useful for attributing a tank's incoming-mit to a co-tank cover (e.g. on a shared/cleave buster).

### Cover
- **Log status(es):** `Cover` (and `Covered` on the protected ally)
- **Effect:** takes all damage intended for a targeted ally within 20y. Damage *redirection*, not reduction.
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 12s / 120s
- **Tags:** `targeted-mit`, `tank-mit`

### Clemency
- **Log status(es):** — (instant heal, no lasting status)
- **Effect:** large single-target heal (1,000 potency); heals PLD for 50% of that when cast on an ally
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** — / 2.5s (1.5s cast)
- **Tags:** `heal`

---

# Dark Knight (DRK)

Role actions: see **Tank role actions**. DRK pairs strong personal mit (Shadowed Vigil −40%, plus a magic-weighted Dark Mind) with a flexible self-or-ally barrier (The Blackest Night), a magic-weighted *party* mit (Dark Missionary), and an invuln (Living Dead). Two of its tools are magic-weighted, which makes DRK especially strong on magical fights.

### Shadow Wall / Shadowed Vigil
- **Log status(es):** `Shadow Wall`; at Lv.92 upgrades to `Shadowed Vigil` (+ `Vigilant`)
- **Effect:** Shadow Wall −30%; Shadowed Vigil −40% and grants Vigilant, a heal (1,200 potency) when HP drops below 50% or on expiration
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 15s (Vigilant 20s) / 120s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`, `heal`

### Dark Mind
- **Log status(es):** `Dark Mind`
- **Effect:** −10% physical / **−20% magic** damage taken (magic-weighted)
- **Scope:** self  **Coverage:** all (magic-weighted)
- **Duration / Recast:** 10s / 60s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`

### Dark Missionary
- **Log status(es):** `Dark Missionary`
- **Effect:** −5% physical / **−10% magic** damage taken for self and nearby party (magic-weighted)
- **Scope:** party  **Coverage:** all (magic-weighted)
- **Duration / Recast:** 15s / 90s
- **Tags:** `party-mit`, `percent-mit`, `tank-mit`

### The Blackest Night
- **Log status(es):** `Blackest Night`
- **Effect:** barrier absorbing 25% of target's max HP (self or an ally)
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 7s / 15s — gated by MP cost
- **Tags:** `targeted-mit`, `barrier`, `tank-mit`

### Oblation
- **Log status(es):** `Oblation`
- **Effect:** −10% damage taken (self or a targeted ally); 2 charges
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 10s / 60s (2 charges)
- **Tags:** `targeted-mit`, `percent-mit`, `tank-mit`

### Living Dead
- **Log status(es):** `Living Dead` → `Walking Dead` → `Undead Rebirth`
- **Effect:** invuln-style — while Walking Dead, HP cannot drop below 1; healing it to full max HP within the window survives, otherwise KO. Requires healing to "clear."
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s + 10s / 300s
- **Tags:** `invuln`, `personal-mit`, `tank-mit`, `heal`

---

# Warrior (WAR)

Role actions: see **Tank role actions**. WAR is the self-sustain tank — its mit is bundled with heavy self-healing (Bloodwhetting, Equilibrium, Thrill of Battle), it brings a party barrier (Shake It Off), and its invuln (Holmgang) is unconditional. Mostly all-coverage percent mit; little magic-weighting.

### Thrill of Battle
- **Log status(es):** `Thrill of Battle`
- **Effect:** +20% max HP (and heals the increase); +20% HP recovery from healing on self. Effective-HP buff rather than damage reduction.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 90s
- **Tags:** `personal-mit`, `tank-mit`, `heal`

### Vengeance / Damnation
- **Log status(es):** `Vengeance`; at Lv.92 upgrades to `Damnation` (+ `Primeval Impulse` regen)
- **Effect:** Vengeance −30%; Damnation −40%, plus a damage reflect and Primeval Impulse regen (300 potency) on expiry/damage
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 15s / 120s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`, `heal`

### Bloodwhetting (upgrade of Raw Intuition)
- **Log status(es):** `Bloodwhetting`, `Stem the Flow`, `Stem the Tide`
- **Effect:** −10% (Bloodwhetting) + −10% (Stem the Flow, 4s) + heal-on-weaponskill (400) + a small barrier (Stem the Tide, ~400 potency)
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 8s / 25s
- **Tags:** `personal-mit`, `percent-mit`, `barrier`, `tank-mit`, `heal`

### Nascent Flash
- **Log status(es):** `Nascent Flash` (self), `Nascent Glint` (ally), `Stem the Flow`, `Stem the Tide`
- **Effect:** the ally-targeted version of Bloodwhetting — grants the targeted ally −10% (Nascent Glint) + heal-on-WS + Stem the Flow/Tide
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 8s / 25s
- **Tags:** `targeted-mit`, `percent-mit`, `barrier`, `tank-mit`, `heal`

### Equilibrium
- **Log status(es):** `Equilibrium` (regen)
- **Effect:** large self-heal (1,200 potency) + regen (200 potency, 15s)
- **Scope:** self  **Coverage:** —
- **Duration / Recast:** 15s (regen) / 60s
- **Tags:** `heal`

### Shake It Off
- **Log status(es):** `Shake It Off`
- **Effect:** party barrier worth 15% max HP (+2% per WAR buff it consumes: Thrill / Damnation / Bloodwhetting) + party regen + heal
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 30s / 90s
- **Tags:** `party-mit`, `barrier`, `heal`, `tank-mit`

### Holmgang
- **Log status(es):** `Holmgang`
- **Effect:** invuln — prevents most attacks from reducing HP below 1. Unconditional (no heal required to survive the window).
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 240s
- **Tags:** `invuln`, `personal-mit`, `tank-mit`

---

# Gunbreaker (GNB)

Role actions: see **Tank role actions**. GNB carries a magic-weighted party mit (Heart of Light, mirroring DRK's Dark Missionary), strong single-target mit it can throw on itself or an ally (Heart of Corundum), and an invuln (Superbolide) with a steep cost — it sets the GNB to 1 HP, so it demands an immediate heal.

### Heart of Stone / Heart of Corundum
- **Log status(es):** `Heart of Corundum`, `Clarity of Corundum`, `Catharsis of Corundum` (Lv.68 `Heart of Stone` / `Brutal Shell`)
- **Effect:** −15% damage taken (self or targeted ally); Clarity adds −15% for 4s; Catharsis heals 900 potency at ≤50% HP
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 8s (+4s Clarity) / 25s
- **Tags:** `targeted-mit`, `percent-mit`, `tank-mit`, `heal`

### Camouflage
- **Log status(es):** `Camouflage`
- **Effect:** −10% damage taken; +50% parry rate
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 20s / 90s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`

### Heart of Light
- **Log status(es):** `Heart of Light`
- **Effect:** −5% physical / **−10% magic** for self and nearby party (magic-weighted)
- **Scope:** party  **Coverage:** all (magic-weighted)
- **Duration / Recast:** 15s / 90s
- **Tags:** `party-mit`, `percent-mit`, `tank-mit`

### Nebula / Great Nebula
- **Log status(es):** `Nebula`; at Lv.92 upgrades to `Great Nebula`
- **Effect:** Nebula −30%; Great Nebula −40% **and** +20% max HP (heals the increase)
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 15s / 120s
- **Tags:** `personal-mit`, `percent-mit`, `tank-mit`

### Superbolide
- **Log status(es):** `Superbolide`
- **Effect:** invuln (impervious to most attacks); reduces HP to 50% of max on use. Less punishing than the old 1-HP version — the GNB is left at half HP, not on the brink — but still wants topping up after.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 360s
- **Tags:** `invuln`, `personal-mit`, `tank-mit`

### Aurora
- **Log status(es):** `Aurora` (regen)
- **Effect:** regen (300 potency) on self or an ally; 2 charges
- **Scope:** targeted (self or ally)  **Coverage:** —
- **Duration / Recast:** 18s / 60s (2 charges)
- **Tags:** `heal`

---

# Sage (SGE)

Role actions: see **Healer role actions**. SGE is a **barrier healer**: its mitigation is bundled into party % mits (Kerachole, Holos) and shields (Eukrasian Prognosis/Diagnosis, Haima, Panhaima). Many tools are gated by the Addersgall gauge rather than a recast. Note the shield-overwrite interaction with SCH in double-shield comps is **not modeled** here (see deferred note in PROJECT_CONTEXT).

### Kerachole
- **Log status(es):** `Kerachole` (and `Kerakeia` regen)
- **Effect:** −10% damage taken for self and nearby party; regen (100 potency)
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 30s — Addersgall-gated
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Taurochole
- **Log status(es):** `Taurochole`
- **Effect:** −10% damage taken on a targeted ally; heal (700 potency)
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 15s / 45s — Addersgall-gated
- **Tags:** `targeted-mit`, `percent-mit`, `heal`

### Holos
- **Log status(es):** `Holos`, `Holosakos` (barrier)
- **Effect:** −10% damage taken for self and nearby party (20s); plus a barrier equal to a 300-potency heal and a heal
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 20s (mit) / 120s
- **Tags:** `party-mit`, `percent-mit`, `barrier`, `heal`

### Eukrasian Prognosis (II)
- **Log status(es):** `Eukrasian Prognosis`
- **Effect:** party shield. At Lv.96 (Eukrasian Prognosis II) the barrier nullifies damage equal to 360% of a 100-potency heal
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 30s / 1.5s (GCD, 800 MP)
- **Tags:** `party-mit`, `barrier`, `heal`

### Eukrasian Diagnosis
- **Log status(es):** `Eukrasian Diagnosis`
- **Effect:** single-target shield nullifying damage equal to 180% of a 300-potency heal
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 30s / 1.5s (GCD, 800 MP)
- **Tags:** `targeted-mit`, `barrier`, `heal`

### Haima
- **Log status(es):** `Haima`, `Haimatinon`
- **Effect:** single-target stacking barrier — initial ~300-potency shield, refreshing across 5 stacks; heals on expiry per remaining stack
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 15s / 120s
- **Tags:** `targeted-mit`, `barrier`, `heal`

### Panhaima
- **Log status(es):** `Panhaima`, `Panhaimatinon`
- **Effect:** the party version of Haima — refreshing party barrier (~200 potency) across 5 stacks; heals on expiry per remaining stack
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 120s
- **Tags:** `party-mit`, `barrier`, `heal`

### Physis II
- **Log status(es):** `Physis II`, `Autophysis`
- **Effect:** party regen (130 potency) + increases HP recovered by healing actions by 10%
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** 15s / 60s
- **Tags:** `heal`

### Krasis
- **Log status(es):** `Krasis`
- **Effect:** increases HP recovery via healing actions on a targeted ally/self by 20% (a healing-received amplifier)
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** 10s / 60s
- **Tags:** `heal`

### Raw heals (defensive use, no mit/shield)
- **Druochole** — single-target heal 600, Addersgall, 1s recast. `heal`
- **Ixochole** — party heal 400, Addersgall, 30s recast. `heal`
- **Pneuma** — party heal 600 (also deals damage), 120s recast. `heal`
- **Soteria / Zoe** — healing *amplifiers* (boost Kardia / next heal); not mitigation. `heal`

---

# Scholar (SCH)

Role actions: see **Healer role actions**. SCH is the other **barrier healer**: its shields are `Galvanize`-based (Adloquium single-target, Succor/Concitation party-wide), and it uniquely can *spread* a shield (Deployment Tactics). It also brings strong party % mits (Sacred Soil, Expedient), a magic-only party mit (Fey Illumination), and a pre-emptive safety-net heal (Excogitation). The shield-overwrite interaction with SGE's Eukrasian shields in double-shield comps is **not modeled** (deferred — see PROJECT_CONTEXT).

### Adloquium
- **Log status(es):** `Galvanize` (crit-enhanced: `Catalyze`)
- **Effect:** heal (300 potency) + a single-target shield (Galvanize) nullifying 180% of the amount healed
- **Scope:** targeted  **Coverage:** all
- **Duration / Recast:** 30s / 2.5s (GCD)
- **Tags:** `targeted-mit`, `barrier`, `heal`

### Succor / Concitation
- **Log status(es):** `Galvanize` (crit-enhanced: `Catalyze`)
- **Effect:** party heal (200 potency) + a party shield nullifying 160% of the amount healed. Concitation (Lv.96) is the upgrade.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 30s / 2.5s (GCD)
- **Tags:** `party-mit`, `barrier`, `heal`

### Sacred Soil
- **Log status(es):** `Sacred Soil`
- **Effect:** party take only 90% damage (−10%) in a ground AoE; regen (100 potency)
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 30s — Aetherflow-gated
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Fey Illumination
- **Log status(es):** `Fey Illumination`
- **Effect:** −5% **magic** damage taken for nearby party; +10% healing magic potency (magic-only mit)
- **Scope:** party  **Coverage:** magical
- **Duration / Recast:** 20s / 120s
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Expedient
- **Log status(es):** `Desperate Measures` (mit), `Expedience` (movement)
- **Effect:** party −10% damage taken (Desperate Measures); also a movement-speed buff
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 20s / 120s
- **Tags:** `party-mit`, `percent-mit`

### Deployment Tactics
- **Log status(es):** spreads `Galvanize` to the party (no new status of its own)
- **Effect:** takes a Galvanize shield on self/an ally and copies it to all nearby party members — turns a single Adloquium into a party-wide shield
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** (inherits the shield's remaining time) / 90s
- **Tags:** `party-mit`, `barrier`

### Excogitation
- **Log status(es):** `Excogitation`
- **Effect:** pre-placed safety-net heal (800 potency) that fires when the target drops to ≤50% HP or on expiry
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** 45s / 45s — Aetherflow-gated
- **Tags:** `heal`

### Protraction
- **Log status(es):** `Protraction`
- **Effect:** +10% max HP on a targeted ally/self (heals the increase) + 10% healing received. Effective-HP buff, not damage reduction.
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** 10s / 60s
- **Tags:** `heal`

### Raw heals & enablers (defensive use, no mit/shield)
- **Lustrate** — single-target heal 600, Aetherflow, 1s recast. `heal`
- **Indomitability** — party heal 400, Aetherflow, 30s recast. `heal`
- **Whispering Dawn / Fey Blessing / Seraphism** — fairy/party heals & regens. `heal`
- **Recitation** — guarantees a crit Adloquium/Concitation/etc. (bigger shield/heal) for free; an *amplifier*. `heal`
- **Emergency Tactics** — converts the next Galvanize shield into a direct heal (trades shield for cure). `heal`
- **Dissipation** — +20% healing potency (and refills Aetherflow); amplifier. `heal`

---

# Astrologian (AST)

Role actions: see **Healer role actions**. AST is a **regen healer** by identity — its kit is regen- and direct-heal-flavored, with **no shield *stance*** (the old Diurnal/Nocturnal Sects were removed). It is *not* shield-free, though: it carries a handful of discrete barriers (Celestial Intersection, the Neutral Sect–enhanced regens, The Spire card), the way SGE carries a couple of heals despite being a barrier healer. Its planned party-mit is thin — essentially the Neutral Sect + Sun Sign window (10% + barriers) and the rarely-channeled Collective Unconscious — with the rest being opportunistic card mit and single-target tools.

### Sun Sign
- **Log status(es):** `Sun Sign`
- **Effect:** −10% damage taken for self and nearby party. Gated behind **Suntouched**, granted by Neutral Sect — it cannot be used without having pressed Neutral Sect first, so the two function as a paired window (see Neutral Sect).
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / — (gated by Neutral Sect / Suntouched)
- **Tags:** `party-mit`, `percent-mit`

### Neutral Sect
- **Log status(es):** `Neutral Sect` (and `Suntouched`, which enables Sun Sign)
- **Effect:** +20% healing magic potency for 20s; while active, **Aspected Benefic** and **Helios Conjunction** additionally erect a barrier (250% / 125% of the HP they restore). Its mit value is *indirect* — it converts AST's party regen (Helios Conjunction) into a party barrier, and it unlocks Sun Sign. Together, **Neutral Sect + Sun Sign is AST's one scheduled party-barrier/mit window** (the closest thing AST has to a SCH Succor-wall or SGE Panhaima moment).
- **Scope:** party (via the heals it enhances)  **Coverage:** all
- **Duration / Recast:** 20s / 120s
- **Tags:** `barrier`, `heal`

### Collective Unconscious
- **Log status(es):** `Collective Unconscious` / `Wheel of Fortune` (regen)
- **Effect:** a celestial ring granting −10% damage taken **and** a regen (Wheel of Fortune, 100 potency) to party members in it. The −10% is **channel-gated** — like Passage of Arms, it persists only while the AST stands still and does nothing else, and breaks on moving/acting. In high-end play the channel is **almost never held**, so in real logs you typically see only the lingering Wheel of Fortune regen, not a sustained −10% window. Do **not** treat the mit as a schedulable raidwide cooldown the way Sun Sign or Kerachole are.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 18s (mit, channel-gated) / 60s
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Exaltation
- **Log status(es):** `Exaltation`
- **Effect:** −10% damage taken on self or a targeted ally for 8s; restores HP (500 potency) when the effect ends.
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 8s / 60s
- **Tags:** `targeted-mit`, `percent-mit`, `heal`

### Celestial Intersection
- **Log status(es):** `Intersection` (barrier) — *status name unverified*
- **Effect:** heal (200 potency) on self or a targeted ally **+ a barrier nullifying damage equal to 200% of the HP restored**.
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 30s / 30s (2 charges)
- **Tags:** `targeted-mit`, `barrier`, `heal`

### The Bole (card)
- **Log status(es):** `The Bole` — *status name unverified*
- **Effect:** −10% damage taken on a party member or self. **Opportunistic** — cards arrive on the Astral/Umbral Draw cadence, not on demand, so do **not** flag the absence of a card mit on any given hit as a mit gap.
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 15s / (draw-gated)
- **Tags:** `targeted-mit`, `percent-mit`

### The Spire (card)
- **Log status(es):** `The Spire` — *status name unverified*
- **Effect:** barrier on a party member or self absorbing damage equal to a 400-potency heal. **Opportunistic** (draw cadence — see The Bole).
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 30s / (draw-gated)
- **Tags:** `targeted-mit`, `barrier`

### Macrocosmos
- **Log status(es):** `Macrocosmos`
- **Effect:** grants the party a status that, over 15s, **compiles 50% of damage taken and refunds it as healing** (plus a 200-potency base heal) when the status expires or is detonated by Microcosmos. This is a **deferred heal, not mitigation** — it does nothing to the incoming hit at snapshot, so a player can still be **killed** by the hit before the refund lands. Never read Macrocosmos as "the raidwide was mitigated"; it heals survivors, it does not prevent the death.
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** 15s / 180s
- **Tags:** `heal`

### Raw heals & regens (defensive use, no mit/barrier)
- **Benefic / Benefic II** — single-target heal (500 / 800). `heal`
- **Aspected Benefic** — single-target heal + regen (250 + 250). **Gains a barrier under Neutral Sect** (see above). `heal`
- **Helios / Aspected Helios / Helios Conjunction** — party heal (400) / heal + regen (250 + 150/175). **Helios Conjunction gains a barrier under Neutral Sect.** `heal`
- **Celestial Opposition** — party heal + regen (200 + 100), 60s recast. `heal`
- **Essential Dignity** — emergency single-target heal (400, scaling to 900 at low HP), 40s recast, 3 charges. `heal`
- **Horoscope** — delayed party heal (200, or 400 if refreshed with a Helios cast), 60s recast. `heal`
- **Earthly Star / Stellar Detonation** — large delayed AoE heal (540, or 720 when fully grown), 60s recast. `heal`
- **Lady of Crowns (card)** — instant AoE party heal (400); opportunistic (draw cadence). `heal`
- **The Ewer (card)** — party-member/self regen (200); opportunistic. `heal`
- **The Arrow (card)** — +10% HP recovery via healing on a party member/self; opportunistic *amplifier*. `heal`
- **Synastry** — bonds an ally so single-target heals also heal them (40% of the spell); a healing *amplifier*. `heal`

---

# White Mage (WHM)

Role actions: see **Healer role actions**. WHM is a **regen healer** built on direct heals and regens (Regen, the Medica line, Asylum) plus a strong emergency kit (Benediction full heal, Tetragrammaton). For mitigation it is better-equipped than AST: **three percent-mit cooldowns** — Temperance (10% party), Plenary Indulgence (10% party, via Confession), Aquaveil (15% single-target) — and **two barriers** (Divine Benison single-target, Divine Caress party). No invuln; cleanse/knockback come from the shared Esuna/Surecast role actions.

### Temperance
- **Log status(es):** `Temperance` (and `Divine Grace`, which enables Divine Caress)
- **Effect:** −10% damage taken for self and all party members (50y), and +20% healing magic potency, for 20s. Also grants **Divine Grace**, which unlocks Divine Caress — so Temperance → Divine Caress is a paired window (a party mit followed by a party barrier).
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 20s / 120s
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Plenary Indulgence
- **Log status(es):** `Confession`
- **Effect:** grants Confession to self and nearby party, −10% damage taken for 10s; party members under Confession also receive extra healing (200 potency) from Medica / Medica III / Cure III / Afflatus Rapture. A genuine party percent-mit, not merely a healing rider.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 10s / 60s
- **Tags:** `party-mit`, `percent-mit`, `heal`

### Aquaveil
- **Log status(es):** `Aquaveil`
- **Effect:** −15% damage taken on self or a targeted ally. (A flat percent reduction — *not* a barrier, despite some tooltips' phrasing.)
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 8s / 60s
- **Tags:** `targeted-mit`, `percent-mit`

### Divine Benison
- **Log status(es):** `Divine Benison`
- **Effect:** barrier on self or a targeted ally absorbing damage equal to a 500-potency heal.
- **Scope:** targeted (self or ally)  **Coverage:** all
- **Duration / Recast:** 15s / 30s (2 charges)
- **Tags:** `targeted-mit`, `barrier`

### Divine Caress
- **Log status(es):** `Divine Caress` (and `Divine Aura` regen after the barrier expires)
- **Effect:** party barrier absorbing damage equal to a 400-potency heal; on expiry grants Divine Aura (regen, 200 potency, 15s). **Gated by Divine Grace** from Temperance — cannot be used without Temperance first.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 10s / — (gated by Temperance / Divine Grace)
- **Tags:** `party-mit`, `barrier`, `heal`

### Raw heals & regens (defensive use, no mit/barrier)
- **Cure / Cure II / Cure III** — single-target heal (500 / 800) / party heal around the target (600). `heal`
- **Medica / Medica II / Medica III** — party heal (400) / heal + regen (250 + 150/175). `heal`
- **Regen** — single-target regen (250, 18s). `heal`
- **Afflatus Solace / Afflatus Rapture** — Lily-fed instant single (800) / party (400) heal. `heal`
- **Benediction** — emergency **full HP restore** on a target, 180s recast. The big single-target panic button. `heal`
- **Tetragrammaton** — single-target heal (700), 60s recast, 2 charges. `heal`
- **Asylum** — ground regen (100) + 10% healing received for party in the zone, 90s recast. `heal`
- **Liturgy of the Bell** — places a blossom that procs a party heal (400) each time the WHM takes damage (up to 5 times), 180s recast; reactive party healing, not mit. `heal`
- **Assize** — party heal (400) bundled onto a damage GCD, 40s recast; also restores MP. `heal`

---

# Samurai (SAM)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback). SAM's job-specific survival kit is a single tool — Third Eye and its Lv.82 upgrade Tengentsu — and it is **reactive, not schedulable**: the base reduction only covers one incoming hit, and the meaningful sustained mit+heal exists only after that hit procs Tengentsu's Foresight.

### Third Eye / Tengentsu
- **Log status(es):** `Third Eye`; at Lv.82 upgrades to `Tengentsu` — on being hit, grants `Tengentsu's Foresight`
- **Effect:** reduces damage taken **by the next attack** by 10% (a single-hit reduction, not a sustained window). At Lv.82 (Tengentsu), being struck during the window additionally grants **Tengentsu's Foresight**: −10% damage taken + a regen (200 cure potency) for 9s.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 4s (base window) / 15s — Foresight lasts 9s once procced
- **Tags:** `personal-mit`, `percent-mit`, `heal`
- **Agent note:** do **not** credit the base reduction as a sustained −10% the way Rampart is — it applies to a *single* hit inside a 4s window. The 9s sustained −10% + regen (Tengentsu's Foresight) only appears *after* the SAM is actually struck, so its presence in a log is reactive evidence the SAM took a hit, not a planned party cooldown.

---

# Monk (MNK)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback). MNK carries the strongest melee personal mit — Riddle of Earth, a true schedulable −20% window — plus a conditional party heal (Earth's Reply) and a party healing-received amplifier (Mantra). Its mit is still **personal**, though: only the MNK gets the −20%.

### Riddle of Earth
- **Log status(es):** `Riddle of Earth`; on taking damage grants `Earth's Resolve` (regen); also grants `Earth's Rumination` (enables Earth's Reply)
- **Effect:** −20% damage taken for 10s. On taking damage, grants Earth's Resolve (regen, 100 cure potency, 15s); also grants Earth's Rumination (30s) which unlocks Earth's Reply.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 120s
- **Tags:** `personal-mit`, `percent-mit`, `heal`
- **Agent note:** unlike SAM's Third Eye, this is a genuine sustained −20% window the agent *can* read like Rampart — but it is **personal**, covering only the MNK, not the party.

### Earth's Reply
- **Log status(es):** — (party heal; no lasting mit status)
- **Effect:** party heal (300 cure potency; 500 if it consumes Earth's Resolve). Executable **only** while under Earth's Rumination — i.e. only after Riddle of Earth was used and triggered.
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** — / 1s
- **Tags:** `heal`
- **Agent note:** MNK's only party heal, and it is conditional — its presence implies Riddle of Earth was pressed first.

### Mantra
- **Log status(es):** `Mantra`
- **Effect:** +10% HP recovery via healing actions for self and nearby party. A healing-received amplifier, not mitigation.
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** 15s / 90s
- **Tags:** `heal`

---

# Ninja (NIN)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback). NIN's job-specific survival kit is a single self-barrier.

### Shade Shift
- **Log status(es):** `Shade Shift`
- **Effect:** self-barrier nullifying damage up to 20% of NIN's max HP
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 20s / 120s
- **Tags:** `personal-mit`, `barrier`

---

# Reaper (RPR)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback). RPR's job-specific survival kit is a single small self-barrier with a conditional party-regen tail.

### Arcane Crest
- **Log status(es):** `Crest of Time Borrowed` (the barrier); on full absorption grants `Crest of Time Returned` (regen) to self + nearby party
- **Effect:** self-barrier nullifying up to 10% of max HP (5s). If the barrier is *completely absorbed*, grants Crest of Time Returned (regen, 50 cure potency, 15s) to self and nearby party (15y).
- **Scope:** self (barrier); conditional party regen tail  **Coverage:** all
- **Duration / Recast:** 5s (barrier) / 30s
- **Tags:** `personal-mit`, `barrier`, `heal`
- **Agent note:** small and short (10% HP / 5s) and frequent (30s) — not a major cooldown. The party regen only appears if the barrier was fully eaten, so its presence implies the RPR took a hit large enough to break it.

---

# Dragoon (DRG)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback).

DRG has **no job-specific PvE survival cooldown** — no personal mit, barrier, party mit, or invuln of its own. Life Surge is a DPS action (guaranteed crit/direct hit on the next weaponskill); any lifesteal rider is negligible and not modeled, consistent with the self-heals dropped from the melee role block. In a log, a DRG's only survival-relevant contributions are the role actions (Feint, Arm's Length). (PvP-only actions are out of scope.)

---

# Viper (VPR)

Role actions: see **Melee role actions** (Feint is its party-mit contribution; Arm's Length for knockback).

VPR has **no job-specific PvE survival cooldown** at all — no personal mit, barrier, party mit, or invuln. Its only survival-relevant contributions in a log are the role actions (Feint, Arm's Length). (PvP-only actions such as Snake Scales are out of scope.)

---

# Machinist (MCH)

Role actions: see **Phys-ranged role actions** (Arm's Length for knockback; no party-mit role action). MCH's survival kit is its party % mit (Tactician) plus an all-school enemy damage-down (Dismantle).

### Tactician
- **Log status(es):** `Tactician`
- **Effect:** −15% damage taken for self and nearby party
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 90s
- **Tags:** `party-mit`, `percent-mit`
- The phys-ranged −15% party mit (mirrors DNC Shield Samba / BRD Troubadour — same value, identical role).

### Dismantle
- **Log status(es):** `Dismantle` — a debuff on the boss, but protects the whole party from its output while active
- **Effect:** lowers the target's damage dealt by 10% (all schools)
- **Scope:** party (via enemy debuff)  **Coverage:** all
- **Duration / Recast:** 10s / 120s
- **Tags:** `enemy-debuff`, `party-mit`
- See the damage-types table in `fundamentals.md` (the only all-school enemy damage-down besides Reprisal).

---

# Dancer (DNC)

Role actions: see **Phys-ranged role actions** (Arm's Length for knockback; no party-mit role action). DNC is the richest phys-ranged defensive kit: a party % mit (Shield Samba), a party heal (Curing Waltz), a party regen (Improvisation), and a party barrier (Improvised Finish).

### Shield Samba
- **Log status(es):** `Shield Samba`
- **Effect:** −15% damage taken for self and nearby party
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 90s
- **Tags:** `party-mit`, `percent-mit`
- The phys-ranged −15% party mit (mirrors MCH Tactician / BRD Troubadour).

### Curing Waltz
- **Log status(es):** — (instant party heal, no lasting status)
- **Effect:** party heal (300 cure potency) to self and nearby party; the Dance Partner also re-emits the heal to those near them
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** — / 60s
- **Tags:** `heal`

### Improvisation
- **Log status(es):** `Improvisation`, `Rising Rhythm` (building stacks)
- **Effect:** party regen (up to 100 cure potency) to self and nearby party while channeled; builds Rising Rhythm stacks (every 3s, max 4) that scale the follow-up Improvised Finish barrier
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** 15s / 120s
- **Tags:** `heal`

### Improvised Finish
- **Log status(es):** `Improvised Finish` (party barrier)
- **Effect:** party barrier (~5–10% of max HP, scaling with Rising Rhythm stacks) for self and nearby party. Released from Improvisation.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 30s / — (released from Improvisation)
- **Tags:** `party-mit`, `barrier`
- **Agent note:** the barrier size depends on how long Improvisation was channeled (stacks), so it varies; its presence implies the DNC committed the Improvisation channel first.

---

# Bard (BRD)

Role actions: see **Phys-ranged role actions** (Arm's Length for knockback; no party-mit role action). BRD brings a party % mit (Troubadour), a party healing-received amplifier (Nature's Minne), and a single-target debuff cleanse/prevention (The Warden's Paean).

### Troubadour
- **Log status(es):** `Troubadour`
- **Effect:** −15% damage taken for self and nearby party
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 15s / 90s
- **Tags:** `party-mit`, `percent-mit`
- The phys-ranged −15% party mit (mirrors MCH Tactician / DNC Shield Samba).

### Nature's Minne
- **Log status(es):** `Nature's Minne`
- **Effect:** +15% HP recovery via healing actions for self and nearby party. A healing-received amplifier, not mitigation.
- **Scope:** party  **Coverage:** —
- **Duration / Recast:** 15s / 120s
- **Tags:** `heal`

### The Warden's Paean
- **Log status(es):** `The Warden's Paean` (the pre-emptive debuff-block status, when target is not enfeebled)
- **Effect:** removes one removable detrimental effect from a party member; if the target has none, instead grants a barrier that nullifies the **next** detrimental effect they suffer. The "barrier" absorbs a *debuff*, not damage.
- **Scope:** targeted  **Coverage:** —
- **Duration / Recast:** 30s (debuff-block) / 45s
- **Tags:** `cleanse`
- **Agent note:** this is debuff cleanse/prevention, **not** damage mitigation — do not read its barrier as damage absorption. Functionally a ranged Esuna with a pre-emptive option (e.g. to pre-empt a known incoming vuln/Damage Down debuff).

---

# Black Mage (BLM)

Role actions: see **Caster role actions** (Addle is its party-mit contribution; Surecast for knockback). BLM's job-specific survival kit is a single large self-barrier.

### Manaward
- **Log status(es):** `Manaward`
- **Effect:** self-barrier nullifying damage up to 30% of max HP. (Now absorbs **all** damage, not magic-only as in older patches.)
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 20s / 120s
- **Tags:** `personal-mit`, `barrier`

---

# Summoner (SMN)

Role actions: see **Caster role actions** (Addle is its party-mit contribution; Surecast for knockback). SMN's job-specific survival kit is a self-barrier plus a few raw heals — notably it is the only caster besides RDM that brings meaningful healing.

### Radiant Aegis
- **Log status(es):** `Radiant Aegis`
- **Effect:** self-barrier absorbing damage up to 20% of max HP
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 30s / 60s (2 charges)
- **Tags:** `personal-mit`, `barrier`

### Raw heals (defensive use, no mit/barrier)
- **Physick** — single-target heal (400), 2.5s recast. `heal`
- **Rekindle** — targeted heal (400) + a regen that fires if the target drops below 75% HP, 30s/20s recast. `heal`
- **Lux Solaris** — party heal (500) to self and nearby party, 60s recast (available after Searing Light). `heal`

---

# Red Mage (RDM)

Role actions: see **Caster role actions** (Addle is its party-mit contribution; Surecast for knockback). RDM brings the only genuinely **school-locked party mit** in the game — Magick Barrier (magical only) — plus a raw heal and a raise.

### Magick Barrier
- **Log status(es):** `Magick Barrier`
- **Effect:** −10% **magic** damage taken for self and nearby party, and +5% HP recovered by healing actions
- **Scope:** party  **Coverage:** magical
- **Duration / Recast:** 10s / 120s
- **Tags:** `party-mit`, `percent-mit`, `heal`
- **Agent note:** the only truly magic-locked party mit (see `fundamentals.md`). Does **nothing** against physical or unaspected damage — flag it spent on a physical hit as wasted, and a heavy magical raidwide with no Magick Barrier as a possible gap. Embolden is **not** mit (it is a party damage-*dealt* buff in the current patch) and is not cataloged.

### Raw heal & raise (defensive use, no mit/barrier)
- **Vercure** — single-target heal (350), 2.5s recast. `heal`
- **Verraise** — raise (resurrects to a weakened state); recovery utility, not mit. Often paired with Swiftcast. Not tagged as mitigation, but relevant for post-death recovery analysis.

---

# Pictomancer (PCT)

Role actions: see **Caster role actions** (Addle is its party-mit contribution; Surecast for knockback). PCT carries a self-barrier that can be converted into a party barrier.

### Tempera Coat
- **Log status(es):** `Tempera Coat`
- **Effect:** self-barrier absorbing damage up to 20% of max HP. Recast is reduced by 60s if the barrier is fully absorbed.
- **Scope:** self  **Coverage:** all
- **Duration / Recast:** 10s / 120s
- **Tags:** `personal-mit`, `barrier`

### Tempera Grassa
- **Log status(es):** `Tempera Grassa`
- **Effect:** consumes Tempera Coat to create a **party** barrier (self + nearby party, 30y) absorbing damage up to 10% of max HP. Recast of Tempera Coat reduced by 30s if fully absorbed.
- **Scope:** party  **Coverage:** all
- **Duration / Recast:** 10s / — (consumes Tempera Coat)
- **Tags:** `party-mit`, `barrier`
- **Agent note:** Grassa requires Tempera Coat to be active (it converts the self-barrier into a weaker party-wide one), so the two are a paired window — PCT trades its own 20% barrier for a 10% party barrier.
