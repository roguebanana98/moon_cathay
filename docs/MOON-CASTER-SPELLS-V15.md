# Native caster spells v15

Installed and enabled: `mc_moonshadow_heroes_v15_caster_spells.pack`. V14 retained disabled; launcher backed up.

SHA256: `f760fa5fc705efaa12c945805a4076e5e8f2bb5cd4d4ee717ba2c79d44868648`.

User approved the revised proposal: use existing skills and spell mechanics, only change English display names; no new icon or VFX edits. This supersedes the v13/v14 deferred-spell state.

## mc_pyromancer

| Native skill | English display name |
|---|---|
| `wh_main_skill_all_magic_fire_01_fireball` | Fireball |
| `wh_main_skill_all_magic_fire_04_kindleflame` | Kindleflame |
| `wh_main_skill_all_magic_fire_02_cascading_fire-cloak` | Ember Cloak |
| `wh_main_skill_all_magic_fire_03_flaming_sword_of_rhuin` | Flameforged Blade |
| `wh_main_skill_all_magic_fire_05_the_burning_head` | Blazing Wrath |
| `wh_main_skill_all_magic_fire_09_piercing_bolts_of_burning` | Rain of Embers |
| `wh_main_skill_all_magic_fire_10_flame_storm` | Inferno |

## mc_tidecaller

| Native skill | English display name |
|---|---|
| `wh2_dlc11_skill_all_magic_deep_01_spiteful_shot` | Blessing of the Tides |
| `wh_dlc05_skill_magic_life_life_bloom` | Restorative Flow |
| `wh2_dlc11_skill_all_magic_deep_02_tidecall` | Tidecall |
| `wh_dlc05_skill_magic_life_wizard_earth_blood` | Restorative Waters |
| `wh2_dlc11_skill_all_magic_deep_05_fog_of_the_damned` | Sea Mist |
| `wh2_dlc11_skill_all_magic_deep_09_krakens_pull` | Maelstrom |
| `wh_dlc05_skill_magic_life_wizard_regrowth` | Renewing Tide |

## mc_astral_weaver

| Native skill | English display name |
|---|---|
| `wh3_main_skill_cth_magic_yin_01_cloak_of_jet` | Veil of the Moon |
| `wh3_main_skill_cth_magic_yin_05_power_of_yin` | Lunar Ascendancy |
| `wh3_main_skill_cth_magic_yin_02_storm_of_shadows` | Lunar Snare |
| `wh3_main_skill_cth_magic_yin_03_blossom_wind` | Astral Gale |
| `wh3_main_skill_cth_magic_yin_04_missile_mirror` | Moonlit Mirror |
| `wh3_main_skill_cth_magic_yin_07_talons_of_night` | Grasp of the Eclipse |
| `wh3_main_skill_cth_magic_yin_08_ancestral_warriors` | Lunar Guardians |

## Campaign and Custom Battle

- Each hero gains a standard native-style magic line: six spells, one lore passive, Evasion, Earthing, Magical Reserves and Arcane Conduit, plus a hidden starting-spell node. Existing general/campaign/innate nodes remain unchanged.
- Spell blocks, graph links and prerequisite counts come from native Bright Wizard, Fleet Captain (Deep) and Yin Shugengan templates. Spell skill effects, effect values, scopes, rank requirements and level details are copied from the selected native hero spell skills. The template is moved to the empty magic row without changing those requirements.
- New recruits start with one ordinary native starting spell: Fireball / Blessing of the Tides (Spiteful Shot) / Veil of the Moon (Cloak of Jet). No extra XP or visible skill points granted.
- Custom Battle remains Grand Cathay > Heroes. Each caster has a level-40 spell preset with the hidden starter, six spells and lore passive; native overcast and rank upgrades are retained. Da Anh and her existing preset are unchanged.
- Tidecaller uses four Deep spells, Earth Blood and Regrowth, with Life Bloom as the passive. Deep and Life retain separate native-style group membership and original icons, so source-lore-specific cost/cooldown modifiers remain scoped correctly. Both Life healing spells retain the original green VFX.

## Mechanical and asset preservation

Private skill, ability, group and effect keys isolate the renamed titles from vanilla casters. Active spell definitions differ only in IDs and links to those private IDs. All numeric fields, projectile/bombardment/vortex/spawn records, cast stances, phase references, targeting restrictions, recharge contexts, native skill rank effects, icon paths and artwork/video references are retained.

Native ability effect and lore-group effect mappings are extended only to the private copies to preserve native equipment and group cost/cooldown modifiers. Native characters do not gain the private groups. No shared native ability or localization record is overridden. No special-ability phase is cloned or edited; no icon, VFX, model or animation file is added or changed.

All payloads outside declared spell DB/loc and the three caster magic-node/Custom Battle/ability-grant tables are byte-identical to v14. Recruitment, wizard capacity, unit stats, Da Anh/Moonshadow graphics and turn-one AP Lua are preserved.

## Verification and limits

- RPFM DB/loc roundtrip passed; zero blocking diagnostics.
- Per-ability equality checks verify native mechanics/icon fields and per-skill rank effect equivalence after identifier remapping.
- Independent decoded-data checks verify the exact English spell/passive titles, one starter unlock, spell ownership through assigned groups and all Custom Battle presets. Report: `build/moon-casters-v15-spells/spell-unlock-validation.json`.
- Game runtime remains unverified. No game launch, save edits, public publishing or Git upload. Existing-save migration of newly added free starter nodes is unverified; freshly recruited heroes are the clean test baseline.

## In-game test

Restart with v15 enabled. In Custom Battle, select Grand Cathay > Heroes and inspect each caster spell list, original icons, normal/overcast behavior and original VFX. In campaign recruit a new caster at a Celestial Tower with an available shared wizard slot, confirm the starter and skill-tree unlocks. Check native cost/cooldown modifiers and verify Da Anh remains unchanged.

## Files

- Specification: `src/campaign/moon-caster-spells.json`.
- Build: `tools/Build-Moon-Caster-Spells.py`.
- Independent validation: `tools/Validate-Moon-Caster-Spells.py`.
- Deployment: `tools/Deploy-Moon-Caster-Spells.py`.
- Build/deployment reports and launcher backup: `build/moon-casters-v15-spells/`.
