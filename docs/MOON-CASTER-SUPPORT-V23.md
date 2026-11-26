# Astromancer support for three Moon casters - private v23

Adds seven native Astromancer support skills to Pyromancer, Tidecaller and Astral Weaver. Existing spell/campaign/innate nodes remain untouched. Each tree goes from41 to48 nodes, without increasing skill points per level or adding automatic starting bonuses.

| Native skill | Private English skill name |
| --- | --- |
| Attuned to the Heavens | Attuned to the Moon |
| Martial Interests | Martial Discipline |
| Trusted Counsel | Counsel of the Moon |
| Celestial Conduit | Lunar Conduit |
| Astromantic Warding | Moonlit Warding |
| Heavenly Bonds | Moonbound Beasts |
| Peerless Astromancy | Mastery of the Moon |

The seven private skill aliases are shared by the three separate hero trees. Effect keys/scopes/values, icon paths, skill fields and rank details are copied exactly from native Astromancer. Only names and identifiers change; original descriptions receive ASCII punctuation normalization. Native ability names and VFX remain unchanged; no new ability, phase, effect, icon or artwork is defined. The three army-support skills target the original native unit groups, not all units indiscriminately.

Weavings the Winds is omitted because it only reduces Lore of Heavens cooldowns. The remaining native row1 starts with Attuned to the Moon and leads to Martial Discipline/Counsel of the Moon. Lunar Conduit retains required_num_parents=2 and its two surviving SUBSET_REQUIRED links, so it requires both remaining alternatives rather than two out of the original three. This keeps the capstone reachable with the same point cost, with no useless Heavens-only prerequisite.

The row3 skills Moonlit Warding, Moonbound Beasts and Mastery of the Moon remain mutually exclusive, exactly like Astromancer. Their native level13 gates remain; Attuned keeps its native level11 gate. New skill nodes use native row positions in previously empty rows1/3. No existing skills, rank limits, capacity, buildings, recruitment, caster spells, CB spell presets, models or animations are altered.

## Validation and deployment

- Seven source-equivalent skill records,21 nodes and21 set memberships.
- Four valid prerequisite links and six native exclusion locks per hero (12 links/18 locks total).
- All new node positions are free in the actual existing trees; capstone remains reachable.
- Exact native effect/rank/icon equivalence checked; no Heavens cooldown effect copied.
- Every previous v22 internal payload retained byte-for-byte; additive tables/localization only.
- All tables roundtripped through RPFM; zero blocking diagnostics.
- Combined v23 installed/enabled; previous v22 retained disabled, launcher backed up. No saves, native or Workshop packs changed. No game launch, Git upload or public distribution.

The change is statically validated, not tested inside the running game. New skills should be checked on the campaign trees, including rank gates and the mutually exclusive army-support choices.

Build/report folder: build/moon-casters-v23-astromancer-support. Tools: Build-Moon-Caster-Astromancer-Support.py and Deploy-Moon-Caster-Astromancer-Support.py.
