# Master Engineer standalone integration v17

The user requested the Cathay Master Engineer from Workshop mod 2815205063 in Agents of the Moon, then clarified that only the current integrated pack should need enabling. This private local build embeds the required original mod records and model/UI assets. Neither the original engineer mod nor portrait submod is required or enabled. Existing IEE/MIXER/other project requirements are not removed by this change.

Installed/enabled: `mc_moonshadow_heroes_v17_master_engineer.pack`. V16 retained disabled. Both `Luke_cth_master_engineer.pack` and `!Luke_cth_master_engineer.pack` launcher entries remain disabled. Workshop files are unchanged; this is not public redistribution.

## Recruitment

Master Engineer is a regular repeatable hero, `auto_generate=true`, `recruitable=true`, subtype cap=-1 and all five campaign unit caps=-1. The only added faction permission is `cr_cth_agents_of_the_moon`, agent category `wizard`, preserving the donor's category.

Recruit at the existing Forge chain: `wh3_main_cth_gunners_1`, `_2`, `_3`. The six original recruitment/capacity effects now require the owner context `Region.Owner.RecordKey == "cr_cth_agents_of_the_moon"`. As in the donor, Forge adds 1/2/3 shared wizard capacity at its three upgrade levels, not an independent engineer pool. Normal recruitment pool availability still applies. No new building, automatic hero spawn or independent capacity system.

Base stats, recruitment/upkeep, weapons, ability definitions, native-derived skill effects and four mount unlock criteria are preserved. Five unit variants: foot, Sky Lantern, Sky Junk, Warhorse and Gyrobomber. Native compiled foot, horse and Gyrobomber animation lookups were found in local native animation tables. No animation retarget or custom clips are included.

## Scope and original-mod differences

The original hero's Chinese localization is replaced with English ASCII names/descriptions, including mounts and rocket skills. Original source artwork is retained. Missing unit-card/minspec aliases reuse the existing PNG bytes. The portrait-settings mask path incorrectly set to `0` is replaced with valid settings for head/body portraits.

Original material files are moved to a private material namespace and WSModel references redirected, preventing the source mod's vanilla Cathay peasant-head material overwrite. Required geometry, materials, textures referenced from the game and other mod assets are included/reference-native as appropriate; the original Workshop pack itself is not a runtime dependency.

Five unrelated vanilla Astromancer art overrides and three global vanilla technology effect additions from the donor are deliberately omitted. This keeps the requested hero integration from globally changing other Cathay characters/capacity through those technology rows. Forge effects are owner-scoped. The source hero's own skill-effect values are unchanged.

Original Custom Battle entries and four mount choices are retained in Grand Cathay. No additional Custom Battle skill preset was invented for this engineer.

## Verification

- All pre-existing v16 payloads are byte-identical, including Tidecaller composite healing selection, Da Anh, all other hero trees, models and starting-movement Lua.
- Decoded DB/loc roundtrip passed; zero blocking RPFM diagnostics.
- Independent checks confirm the one-faction permission, regular hero flags, owner-scoped Forge effects and 1/2/3 capacity values, five unit variants, four mounts and equality of original hero stats/skill effects/abilities/mount unlocks.
- Source Workshop SHA256 is unchanged. Launcher configuration was backed up; only the previous/current project version and the two engineer dependency entries are in deployment scope. Other entries and previous active pack hashes were preserved.
- Runtime recruitment, animation, equipment and UI have not been tested in game. No game launch, save edits, original/native/Workshop modification or Git upload.

## Test

Restart with v17 active. Keep the original engineer and portrait-only submod disabled. In an Agents of the Moon province with a Forge and an available shared wizard slot, inspect the hero recruitment pool for Master Engineer. Normal pool refresh may be needed for an existing save; a new campaign/recruit is the clean baseline. Test foot and mount models, original abilities and portrait cards. Custom Battle remains Grand Cathay > Heroes.

Authoring manifest: `src/campaign/master-engineer.json`. Build: `tools/Integrate-Cathay-Master-Engineer.py`. Deployment: `tools/Deploy-Integrated-Master-Engineer.py`. Exact paths, source/current hashes, validation and launcher backup: `build/moon-heroes-v17-engineer/`.
