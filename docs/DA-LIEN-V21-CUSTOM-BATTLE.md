# Da Lien — v21 Custom Battle animation test

03/11/2026. User requested Custom Battle access to test Da Lien animations.

Installed private integrated pack:
`build/huyen-ve-v21-da-lien-custom-battle/mc_huyen_ve_v21_da_lien_custom_battle.pack`.
v21 is enabled in launcher, v20 disabled; backup recorded in `deployment-report.json`.
The game was already running during deployment: restart it to load this version.

## Test

1. Custom Battle → Grand Cathay → Heroes → **Da Lien**.
2. Bring a normal Lord as army leader; Da Lien is a Hero, not a Lord entry.
3. Enable the available Metal spells in army setup for casting tests; select
   a normal land map. Remove/re-add her if reusing a saved army preset.
4. Inspect idle, walk/run, turning, staff/dagger grip, melee and death animation.
   Test Searing Doom on enemies and Glittering Robe on allies to inspect casting.

This is a temporary native Alchemist/Metal preset, not the final AOE/heal/armour
skill tree. Model and native battle/campaign animation lookups are unchanged
from v20. The one-time Long Vi campaign spawn is also unchanged.

## Validation and deployment

- Seven new DB/loc payloads: Cathay MP Hero permission, character/preset,
  12 native magic/passive skill entries, two name records, military group and loc.
- All previous v20 entries byte-identical, including campaign script, model,
  Huyen Ve stats/items/skills and startpos. No map or quest battle was created.
- All added DB/loc roundtrip checked; no new blocking diagnostics. Two schema
  metadata warnings for names type/gender are recorded separately.
- Source/installed SHA256:
  `38063b7a1ed2fbf0b9efc2be6ca2258c65bf12c21ccc5313bd48d724d26cc198`.
- Launcher backup made; other entries, saves and Workshop files preserved.
  Runtime roster visibility, spells and animations still need in-game confirmation.

Tools: `Build-Da-Lien-Custom-Battle-Test.py`, `Deploy-Da-Lien-Custom-Battle-Test.py`.
Reports: `pack-validation.json`, `diagnostics-review.json`, `deployment-report.json`
in the v21 build directory. For campaign test details see `DA-LIEN-V20-VISUAL-TEST.md`.
