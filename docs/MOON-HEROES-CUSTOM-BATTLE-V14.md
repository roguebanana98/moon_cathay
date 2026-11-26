# Four heroes in Custom Battle, v14

The user requested the three new casters and Da Anh in Custom Battle for testing.

Select **Grand Cathay > Heroes**, add a lord to lead the army, then select:

- Pyromancer (model 1)
- Astral Weaver (model 2)
- Tidecaller (model 3)
- Da Anh (approved dagger and handbow)

This uses native `wh3_main_cth_cathay_mp`, matching the established Huyen Ve and Da Lien Custom Battle test entries. Campaign recruitment remains limited to Agents of the Moon. No new playable faction/menu was added.

Each entry has its own English name, existing portrait, uniform, subtype and exact campaign art-model ID. All four are hero entries (`general_unit=false`), not army leaders. Native wizard/assassin records supply the required Custom Battle permission and set-piece character fields. A Cathay military grouping permission is added for each.

Da Anh has a level-40 Custom Battle skill preset containing Moonshadow Veil, Moonlit Prey and The Last Shadow. This preset is isolated to Custom Battle; no campaign character receives XP, points or free skills. The three casters have no starting spell or assigned lore, as the user explicitly deferred their spell trees. They are currently suitable for model, movement and combat-animation checks.

Pack: `mc_moonshadow_heroes_v14_custom_battle.pack`, additive over v13. All existing payloads remain byte-identical, including models, cards, stats, campaign trees, recruitment, capacity and turn-one movement Lua. Only new Custom Battle permissions, military grouping permissions, set-piece characters, Da Anh's Custom Battle skillset, zero-frequency names and English ASCII localization are added.

Validation: names/portrait/art/subtype links, all-four hero permissions, no caster lore, DB/loc roundtrip and zero blocking RPFM diagnostics. Engine behavior and UI selection remain unverified; no game launch was performed. No saves, native or Workshop packs were modified.

Build: `tools/Build-Moon-Heroes-Custom-Battle.py`. Deployment: `tools/Deploy-Moon-Heroes-Custom-Battle.py`. Reports and launcher backup: `build/moon-heroes-v14-custom-battle/`. V13 is retained for rollback, disabled after deployment. No Git upload.
