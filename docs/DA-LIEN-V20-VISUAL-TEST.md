# Da Lien — v20 campaign appearance test

Current integrated test is [v21](DA-LIEN-V21-CUSTOM-BATTLE.md), inheriting all
v20 campaign/model payloads and adding Custom Battle Hero access for Da Lien.
Version-specific v20 deployment/rollback details below are historical.

03/11/2026 (Asia/Saigon). User requested private integration and a spawn at
Long Vi to inspect the selected Beautiful Neferata appearance in game.

## Installed test

`build/huyen-ve-v20-da-lien-visual-test/mc_huyen_ve_v20_da_lien_visual_test.pack`
is deployed to the configured game data directory. Launcher v20 is enabled,
v19 is disabled, and the other launcher entries are preserved. Previous pack
files remain. Backup and installed hash are in that build's `deployment-report.json`.

SHA256: `0fd13e2141afc5e8c0f4ef358d9a1d32bf47ace4b866be1a7c89231b3d6c4854`.

## What the test adds

- New subtype `mc_da_lien`, unit `mc_da_lien_human`, campaign agent type engineer
  and battle caste hero, based on the living Cathay Alchemist framework.
- Beautiful Neferata body, staff, dagger and selected-mod portraits, with new
  resource paths so the vanilla character and the Workshop mod are not overwritten.
  Reference-derived art is bundled only in this ignored private test pack.
- Native battle lookup `hu1ba_dlc29_vmp_neferata_staff_and_sword`; native campaign
  lookup `cam_hu1ba_dlc29_vmp_neferata_staff_and_sword`. Compiled runtime BIN
  existence verified, no invented custom animation lookup or bundled native clips.
- Human Cathay attribute group and temporary Alchemist skill/lore framework,
  excluding mount/immortality skill nodes; script sets immortality directly.
  No Neferata Lord tree, Vampire/Undead abilities or transformation mechanics.
- This is an appearance prototype. Final AOE/light healing/armour-buff kit and
  custom wizard skill tree are not implemented. Voice uses the Cathay donor.
- Original model geometry and its single LOD are preserved; optimisation remains
  pending. The preview Blender export is not used as the game mesh.

## Spawn and user check

1. Restart the game with v20 as the only enabled integrated Huyen Ve pack.
   The IEE/MIXER dependencies remain as before; no new campaign is required.
2. Load the existing Agents of the Moon campaign. After first tick, the script
   attempts to create Da Lien once on valid land near owned Long Vi.
3. If she is not visible immediately, check the faction's next turn and the
   Hero list. Missing/unowned Long Vi or no valid position defers creation;
   the script does not transfer a region or spawn her elsewhere.
4. Inspect campaign model, name, portrait, movement, then embed her into an army
   and inspect the battle model/idle/movement/casting when convenient.

A saved marker and subtype-presence scan prevent repeat grants on reload or
faction turns. Marker is written only after a valid creation result; wounds do
not intentionally trigger another spawn. Wounded return and script behaviour
still need runtime verification. The assistant did not launch gameplay or edit
a save: the spawn executes when the user runs the campaign with this pack.

## Validation performed

- Dependencies IEE/MIXER SHA256 unchanged against recorded fingerprints.
- All existing v19 payloads, including Huyen Ve, startpos, items, skills, models
  and province data, byte-identical; 74 new payloads added.
- Every added DB/loc payload roundtrips through the configured RPFM schema;
  added binary/graphics/script bytes match the pack.
- Re-keyed XML model/material/VMD paths resolve; portrait-settings generated
  for the new art set; description references and fallback porthole supplied.
- No banned DLC ownership tables. No new blocking RPFM diagnostics; ten new
  schema-reference metadata warnings are recorded separately.
- Source/installed pack hashes match; launcher backup made; saves and Workshop
  files untouched. No runtime success is claimed.

Tools: `Build-Da-Lien-Visual-Test.py`, `Validate-Da-Lien-Visual-Test.py`,
`Deploy-Da-Lien-Visual-Test.py`. Source script:
`src/script/campaign/mod/mc_da_lien_visual_test.lua`.

Rollback: disable v20 and re-enable the preserved v19 pack. For a clean rollback
after testing, load a save made before v20 created the custom Hero; do not assume
a save containing Da Lien is compatible after removing her DB definitions.

The eventual quest-progression release must remove the automatic visual-test
spawn and handle migration of test saves explicitly. Current quests remain
unimplemented; this spawn is not completion of the final Hero quest.
