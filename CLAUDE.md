# Working in this repo

This repo builds an FFXIV mitigation & mechanic-solving agent. The product is a **knowledge layer** (`knowledge/`) that gets pasted into claude.ai as a system prompt to analyze FFLogs data. This file is guidance for **you, the build agent**, when authoring that knowledge layer — it is *not* loaded into the analysis agent at runtime.

For project state and roadmap see [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md). For the shared glossary see [CONTEXT.md](CONTEXT.md).

## The two agents — keep them separate

- **Analysis agent** (runs on claude.ai): consumes `knowledge/` + a fight file + reference guides as its system prompt. Everything in `knowledge/` is written *for it*.
- **Build agent** (you, in Claude Code): authors the knowledge layer. This file is for you.

The analysis agent itself runs in **two runtime modes** — *analysis* (diagnose a past pull) and *planning* (author a forward mit plan), two halves of one plan→raid→observe cycle. That split lives *within* the analysis agent and is orthogonal to the build-vs-analysis split above; both modes share the `knowledge/` layer. See `knowledge/fundamentals.md` → Cooldown Economy & Planning Mode.

Don't leak build-time concerns into `knowledge/` files, and don't write runtime knowledge here.

## FFXIV corrections to never repeat

The original design session made these errors. Do not reintroduce them:

- **Revolting Ruin III is a CLEAVE TANKBUSTER**, not a raidwide. It hits #1 enmity, then #2 enmity ~1s later.
- **The boss in Dancing Mad Ultimate is Kefka**, not Ultima Weapon. Boss actor ID in the test log was 38 (and 43 in a different phase).
- **Towers are positioning mechanics; positioning and mit are *separate axes*.** A tower's defining job is body-allocation (who soaks — see the 8-player budget), and an unsoaked-tower failure is solved by *playing the mechanic*, never by mit. The soak's *damage* is an independent question, decided like any hit by its magnitude/school — often a clean soak is calibrated survivable and needs nothing, sometimes it's chunky and wants covering. Do **not** attach mit rules to "positional": the old "towers get pre-shields only / no %-cooldowns" was wrong and has been removed. **Mit follows damage, not mechanic type.** (See `knowledge/fundamentals.md` → "Mit follows damage, not mechanic type".)
- **Gazes apply debuffs AND can deal damage** — not one or the other.
- **The log does NOT show player facing.** Gaze analysis is always post-mortem from the applied debuff.
- **Damage Down ≠ vulnerability.** Damage Down reduces damage *dealt* and never affects survivability; it's a non-fatal failure marker. Vulns amplify damage *taken* and can be applied by design. (See `knowledge/fundamentals.md`.)
- **Weakness / Brink of Death ≠ Damage Down.** Those are post-raise debuffs, not mechanic-failure punishments.
- **AST is a regen healer (by identity, not absolutes).** The Sect stances (Diurnal/Nocturnal) were removed — AST has **no shield *stance*** that converts its regens into barriers. It does, however, carry a few discrete barrier tools (Celestial Intersection, the Neutral Sect–enhanced Aspected Benefic/Helios Conjunction, The Spire card) — author these with the `barrier` tag. The classification is about healing *identity*: AST is regen-flavored the way SGE is barrier-flavored despite having a couple of heals. So "only SGE/SCH are barrier healers" means barrier-*identity*, not "AST has zero barriers." When authoring AST, do not model a Sect/shield stance, but do capture its real barriers from the live guide.
- **Trust the live job-guide fetch over memory.** Several errors came from overriding fetched tooltip text with outdated training knowledge (e.g. GNB Superbolide drops to 50% HP, not 1). When the guide and memory disagree, the guide wins.

## Honesty about FFXIV knowledge limits

Claude's FFXIV knowledge is incomplete and sometimes wrong. Treat existing drafts as living documents, not ground truth. When a log contains a mechanic that doesn't cleanly match a primitive, that's a signal to **refine the primitive**, not to force the mechanic to fit. When unsure of a specific number (debuff %, duration), prefer a qualitative statement over asserting a value you can't stand behind — or ask.

## File-design principles

1. **Fight files are catalogs, NOT mit plans.** During prog the resolution is unknown. Each mechanic entry separates:
   - **Observed:** what the log shows
   - **Resolution:** what's been figured out (or "UNKNOWN — currently testing X")
   - **Open questions:** what's not yet known
2. **`jobs.md` is by-job for maintainability, with effect tags for queryability** (`party-mit`, `percent-mit`, `debuff-based`, etc.) so the agent can pivot to "what 20% party mits exist?" without a separate by-effect view.
3. **`primitives.md` is the vocabulary layer** — patterns for recognizing mechanics across any fight. Write-once knowledge that compounds.
4. **`fundamentals.md` is the rules-of-the-game layer** — cross-cutting concepts referenced by primitives. **DRY**: don't duplicate a concept across primitives; put it in fundamentals and reference it. (Example: the 8-player budget lives in fundamentals; the Tower primitive references it.)

## Primitive entry template

Each primitive entry follows:

- **Recognition signals** — observable features in log data
- **Variants** — sub-patterns within the primitive
- **Failure modes** — what counts as failure, classified by *outcome*, not strategy
- **Notes for the agent** — heuristics, common confusions, caveats

## Classify by outcome, not strategy

A non-standard execution that worked is still a **success** (e.g., MT solo'ing a shared tankbuster with Hallowed Ground). Flag interesting executions as observations, not failures. This principle governs every failure-mode section.
