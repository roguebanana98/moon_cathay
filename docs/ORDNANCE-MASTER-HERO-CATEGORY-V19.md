# Ordnance Master Hero category fix v19

Ordnance Master is an ordinary repeatable Hero. User observed it listed under Lords in Custom Battle after v18.

Root cause: all five original engineer `main_units.ui_unit_group_land` fields referenced `wh3_dlc24_cth_cha_celestial_general`. Its native `ui_unit_groupings.parent_group` is `commander`, so the unit was displayed in the Lord category even though `caste=hero` and `units_custom_battle_permissions.general_unit=false`. Prior static checks incorrectly treated those two hero flags as sufficient and did not validate the UI grouping hierarchy.

V19 changes exactly one field in five rows: `ui_unit_group_land=emp_engineer`. The native Empire Engineer group has `parent_group=heroes_agents`, the appropriate existing Engineer Hero group. No new artwork/group/icon is created. Subtype, unit keys, names, stats, models, skills, mount links, campaign recruitment and repeatable-hero behavior remain unchanged. All other packed payloads are byte-identical to v18.

Regression checks validate all three classification controls together for all five variants: `caste=hero`, permission `general_unit=false`, and the referenced UI group's `parent_group=heroes_agents`. DB roundtrip passed; zero blocking RPFM diagnostics. Game UI/runtime remains unverified; the original symptom is user-reported.

Installed update: `mc_moonshadow_heroes_v19_hero_category.pack`, replacing active v18. Both original engineer Workshop mods remain disabled. No save/native/Workshop edits, game launch or Git upload. Restart and inspect **Grand Cathay > Heroes > Ordnance Master**, with the four original mount choices.

Build/fix: `tools/Fix-Ordnance-Master-Hero-Category.py`. Deployment: `tools/Deploy-Ordnance-Master-Hero-Fix.py`. Reports and launcher backup: `build/ordnance-master-v19-hero-category/`.
