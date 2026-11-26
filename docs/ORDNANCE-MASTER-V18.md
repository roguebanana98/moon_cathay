# Ordnance Master v18

The user requested renaming Master Engineer to **Ordnance Master** and enabling it for Custom Battle testing.

Installed update: `mc_moonshadow_heroes_v18_ordnance_master.pack`, replacing active v17. Both original engineer Workshop mods remain disabled; the integration is still standalone with respect to those two mods. No new dependency.

All five unit display names, subtype/category labels and engineer-specific effect descriptions now use Ordnance Master. The subtype/unit keys remain `Luke_cth_master_engineer` and its existing mount suffixes to preserve campaign/save references. No campaign stat, skill, model, recruitment, capacity or ordinary repeatable-hero flag changed.

Custom Battle: **Grand Cathay > Heroes > Ordnance Master**. Base unit and four mount variants retain their native permissions and mount links. Permissions now point to an explicit named set-piece character and the correct foot/horse/Gyrobomber battle uniforms. A level-40 Custom Battle-only preset exposes four existing engineer-tree options: Portable Fire Rain Rocket, Ballistics Calibration, Flash Bomb and the native Gunnery Wight support skill used by the donor. Availability on each mounted variant still follows the original unit's ability grants; no unsupported mount is given a rocket ability. No campaign character receives XP, points or free skills.

Original Warhorse, Sky Lantern, Sky Junk and Gyrobomber are retained. Existing art, icons and VFX are unchanged. Other heroes, including Tidecaller healing selection, remain byte-identical outside the scoped engineer Custom Battle and localization files.

Validation: DB/loc roundtrip, all five English unit names, hero permissions, existing four mount links and original-tree skill membership; zero blocking RPFM diagnostics. Game/UI runtime is unverified; no game launch, save edits, native/Workshop modification, public publishing or Git push.

Restart the game to reload localization, open Custom Battle, select Grand Cathay, add an army lord, then select Ordnance Master under Heroes. Re-add the hero if an old saved army preset retains previous options.

Build: `tools/Build-Ordnance-Master-Custom-Battle.py`. Deployment: `tools/Deploy-Ordnance-Master-Custom-Battle.py`. Reports and launcher backup: `build/moon-heroes-v18-ordnance-master/`.
