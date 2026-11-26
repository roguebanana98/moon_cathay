# Tidecaller healing selection v16

User reported Restorative Waters (Earth Blood) and Renewing Tide (Regrowth) missing from Custom Battle.

V15 attached separate Deep (page 0) and Life (page 1) spell groups to Tidecaller, while its Custom Battle character selected only the Deep group as `magic_lore`. Both healing skills were present in the preset, but both abilities belonged only to the other group. V15 static validation incorrectly accepted the union of owned groups without checking the actual Custom Battle-selected group. The game symptom is user-reported; no direct UI observation was made.

V16 uses a single composite display group, following the native Teclis mixed-lore pattern. `mc_tidecaller_lore_combined` contains the six base spells and Life Bloom; the upgraded companion contains the six upgraded spells. This is the only group assigned to Tidecaller at page 0 and is also the Custom Battle character's selected lore. It uses the existing Deep group icon, without changing any image file.

The original private Deep/Life source groups and native cost/cooldown modifier bindings remain in the database as membership records. Spell definitions, unlock effects, overcasts, ranks, skills, icons, VFX, models, campaign recruitment, stats and other heroes are byte-identical to v15. No new heal, damage or free campaign skill was introduced.

Regression checks now require both healing abilities to belong to the actual Custom Battle-selected group, both matching skills to appear in that character's preset, and both level-1 effects to enable the correct abilities. RPFM roundtrip passed with zero blocking diagnostics. This does not prove in-game UI behavior.

Build/report directory: `build/tidecaller-v16-healing-selection`. Scripts: `tools/Fix-Tidecaller-Healing-Selection.py`, `tools/Deploy-Tidecaller-Healing-Fix.py`. Installed update: `mc_moonshadow_heroes_v16_tidecaller_healing.pack`.

Test after restarting the game: select Grand Cathay > Heroes, remove an existing Tidecaller from the Custom Battle army and add a fresh Tidecaller, then check its spell selection for Restorative Waters and Renewing Tide. Existing saved army presets may retain previous selections. The original green Life VFX remain intentional.

No game launch, save changes, native/Workshop edits or Git upload.
