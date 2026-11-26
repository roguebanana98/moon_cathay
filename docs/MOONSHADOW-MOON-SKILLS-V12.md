# Moonshadow / Da Anh moon skills v12

Private local deployment: `mc_moonshadow_heroes_v12_moon_skills.pack`.

SHA256: `ec666bfa8561a7b8e3b7ead6159e1d68fe8004c6923c2f8dea865a87ada9d24f`. V11 is retained and disabled; launcher configuration was backed up. No game launch, save edits, native/Workshop changes or Git upload.

## Da Anh personal row

| Skill | Character level | Behavior |
|---|---:|---|
| Moonshadow Veil | 6 | Existing Concealment Bombs unlock, unchanged. |
| Sever the Supply Lines | 8 | Existing -15% action cost, +10 percentage points action success, unchanged. |
| Moonlit Prey | 12 | Replaces Silent Execution at the same skill/node key. Enemy lord/hero within 100m: -15 Melee Defence, speed x0.8 for 20s. 90s cooldown. |
| The Last Shadow | 20 | Requires Moonlit Prey. Self: base and AP melee damage x1.5, -15 Melee Defence for 10s. 120s cooldown. |

Both new active abilities require the relevant skill, use no Winds of Magic and have unlimited uses subject to cooldown. They use native targeting/phase behavior with custom keys; no casting animation or skeleton changes. Existing native artwork is reused in the ignored private pack.

## Shared skill names

| Original key | New English name |
|---|---|
| `wh2_main_skill_def_spy_unbreakable` | Moonbound Oath |
| `wh2_main_skill_def_generic_ward_of_khaine` | Lunar Aegis |
| `wh2_main_skill_all_immortality_hero` | Eternal Vigil |
| `wh3_main_skill_all_mentor_hero` | Teachings of the Moon |
| `wh2_main_skill_def_spy_poison_1` | Moonshade Venom |
| `wh2_main_skill_def_spy_poison_2` | Heartseeker Venom |
| `wh2_main_skill_def_spy_poison_3` | Night Lotus |
| `wh2_main_skill_def_combat_dance_of_death` | Moonblade Dance |
| `wh_main_skill_all_spy_self_gutter_fighter_2` | Close-Quarters Training |
| `wh_main_skill_all_spy_self_elusive` | Elusive Shadow |
| `wh_main_skill_all_spy_self_precise_2` | Measured Strikes |
| `wh_main_skill_all_spy_self_survivalist_2` | Twilight Endurance |
| `wh2_main_skill_def_spy_shroud_of_darkness` | Mantle of the Moon |
| `wh_main_skill_all_spy_self_fleet-footed` | Silent Footsteps |
| `wh_main_skill_all_spy_self_opportunist` | Exploit the Opening |
| `wh_main_skill_all_spy_self_counter-striker_2` | Reprisal |
| `wh_main_skill_all_spy_self_bloody_blade` | Moonforged Blade |
| `wh2_main_skill_skv_trophy_heads_assassin` | Moonshadow Execution |
| `wh2_main_skill_def_assassin_missile_range_hawk_eyed` | Moonlit Sight |
| `wh_dlc05_skill_wef_general_personal_buff_missile_damage` | Moonpiercer Bolts |
| `wh2_main_skill_def_combat_deadeye` | Unerring Aim |
| `wh2_main_skill_all_hero_assist_army_increase_mobility` | Hidden Paths |
| `wh2_main_skill_all_hero_hinder_settlement_assault_garrison` | Sabotage the Watch |
| `wh2_main_skill_all_hero_hinder_agent_assassinate` | Silent Elimination |
| `wh2_main_skill_all_hero_hinder_army_assault_units` | Strike from the Shadows |
| `wh2_main_skill_all_hero_reduce_action_cost` | Covert Preparation |
| `wh2_main_skill_all_hero_hinder_settlement_damage_building` | Sabotage the Foundations |

## Scope and verification

- The 27 shared skills are private copies referenced only by these two hero trees. Vanilla skill names elsewhere remain untouched.
- All native effects, ranks and rank requirements for renamed skills are copied exactly. Poison mutual-exclusion locks point to the new skill keys.
- Original node IDs are retained. One new node and its required parent link are added for The Last Shadow. Visible skills still start with zero points.
- Pack add/extract roundtrip passed. RPFM diagnostics contain zero blocking reports. Every payload outside the declared skill/ability/loc files is byte-identical to v11, including appearance, unit stats, recruitment and turn-one movement Lua.
- Static checks do not prove engine behavior. Existing-save learned-skill migration is unverified because renamed shared skills use new keys. No skill points or XP are automatically granted. A fresh campaign is the clean baseline; inspect learned ranks before continuing an old save, and use the normal in-game skill reset if necessary.

## In-game check

Restart the game and confirm v12 is the sole enabled Moonshadow hero pack. Check both trees for English names; verify poison choices remain exclusive. On a test character, learn Moonlit Prey at level 12 and The Last Shadow at level 20; confirm only Da Anh gains them, targeting, cooldown and tooltip values. Confirm turn-one normal movement and the approved dagger/handbow appearance.

## Reproduction

`tools/Build-Moonshadow-Moon-Skills.py` builds from the installed v11 and local native DB reference. `tools/Deploy-Moonshadow-Moon-Skills.py` installs a validated candidate with hash checks and an atomic launcher update. Build and deployment reports: `build/moonshadow-v12-moon-skills/`.
