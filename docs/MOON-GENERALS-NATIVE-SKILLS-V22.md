# Ordinary Moon general skills - private v22

User requested native game skills only, the same six special-skill nodes as Celestial General, Bastion renamed without mechanical changes, and Assault's Bulwark replaced by a native offensive skill.

| Native Celestial General skill | Bastion name | Assault name/source |
| --- | --- | --- |
| Leader of Men | Lunar Command | Lunar Command |
| Bulwark of Wei-Jin | Moonlit Bulwark | Moonlit Onslaught: native Deadly Onslaught |
| Hammer of Wei-Jin | Might of the Moon | Might of the Moon |
| Comet of Wei-Jin | Moonfall Charge | Moonfall Charge |
| Titanic Impact | Lunar Impact | Lunar Impact |
| Lead from the Front | Unyielding Advance | Unyielding Advance |

These are private skill-name aliases, scoped through the two generals' own existing nodes. The native Celestial General and other characters are not globally renamed. No new battle ability, phase, effect, VFX, icon, stat bonus, cooldown or duration is authored. Original skill fields except key/name, effect rows, rank details and criteria are equal to the native donors. Deadly Onslaught uses wh_main_skill_all_all_self_deadly_onslaught -> wh_main_effect_ability_enable_deadly_onslaught -> wh_main_character_abilities_deadly_onslaught. The native ability is bound to Assault's foot, horse and stag units and remains effect-gated.

Node count, positions, point settings, prerequisite links and the native Bulwark/Hammer/Comet mutually exclusive choice remain unchanged. On Assault, Deadly Onslaught takes the Bulwark choice, not an extra node. All twelve lock rows are remapped to each general's private names, preserving balance. Other yellow/red/blue skills and all five mounts are unchanged.

Custom Battle now matches the native ordinary Celestial General character setup: level1, empty skillset, normal native ability selection. The previous v20 preset preassigned all three exclusive specializations and every yellow-row skill; it is no longer referenced by these two CB characters. Historical unused preset rows remain inert in the pack to preserve unrelated payloads.

## Checks

- Six skill aliases per lord and exact equality of donor mechanics/icon/rank fields.
- Unchanged node count/settings and twelve retained exclusive lock rows.
- Ability bindings for all three Assault units; no new ability/phase/effect tables.
- All new or changed TSVs roundtripped through RPFM; zero blocking diagnostics.
- Only three existing payloads changed: the two generals' node table, lock table and CB character table. Models, textures, animations, mounts, stats, other heroes and campaign Lua remain byte-identical.
- Deployed combined v22, retaining v21 disabled and backing up launcher configuration. No saves, native packs or Workshop files changed; no Git/public upload.

The game was not launched. Existing recruited characters may retain investments in former skill IDs; use newly recruited lords or a new campaign for a clean test. No live save migration was performed.

Reports/build: build/moon-generals-v22-native-skills. Tools: Build-Moon-General-Native-Skills.py and Deploy-Moon-General-Native-Skills.py.
