# Two ordinary Moon generals - private v20

Adds Assault General and Bastion General to Agents of the Moon campaign lord recruitment and Cathay Custom Battle Lords. Both are ordinary, repeatable recruitable lords, not unique characters or heroes. Only this faction's native Yin/Yang Celestial General recruitment permissions are replaced; existing characters and other factions are untouched.

Assault uses the approved edited WWD gallery08 body and repaired gallery09 polearm, native humanoid01b and hu1b_elf_2handed_spear. The native compiled lookup contains all eight reviewed clips. Campaign uses the original WWD donor's native cam_hu1b_bretonnian_staff_and_sword profile, matching the skeleton. Cathay culture mapping explicitly enables the native battle profile.

Bastion uses gallery01, native humanoid01e and Celestial General battle/campaign profiles. The true vanilla hammer shaft is retained, with its golden head replaced by the guandao blade, aligned to the hammer strike axis. Black armour borders, white scale fields and original human skin are baked into private DDS textures.

| Lord | Armour | Attack | Defence | Charge |
| --- | ---: | ---: | ---: | ---: |
| Assault General | 90 | 65 | 35 | 45 |
| Bastion General | 110 | 55 | 50 | 20 |

Other core stats, costs, damage and army skills use native Celestial General values. Each has a private cloned native Yang/Yin skill tree with original skill effects and icons. The three mount nodes are excluded because only the foot models are prepared. Custom Battle presets use the native personal rows, without hidden innate reward traits. New names, descriptions, portraits and cards are English ASCII. No ownership/DLC tables are modified (RPFM bans writing these tables).

## Validation

- Four generated LODs for each body and weapon; native bone indices and normalized weights checked.
- Exact exported RMV/DDS files reimported for visual inspection and portraits; skin/armour colours and connected weapons checked.
- Twenty clips across both models: eight battle and two campaign clips each, three sampled frames each (60 samples). Finite deformation and nonzero motion; no importer warnings.
- Compiled native battle lookups verified, not just text DB animation keys.
- All new DB/localization tables roundtripped through RPFM. No blocking diagnostics.
- Every v19 payload retained byte-for-byte, including Da Anh movement, Tidecaller healing and Ordnance Master hero-category fixes.

The game has not been launched; campaign recruitment, save compatibility and combat behaviour still require in-game testing. The approved Assault native spear twirl can briefly release the weapon; the same choreography from the user-reviewed preview is preserved. These Blender checks do not establish perfect grip or a full game runtime pass.

## Local artifacts and rollback

- Editable final source: build/moon-generals-preview/moon-generals-assault-polearm-connected.blend.
- Output and reports: build/moon-generals-v20, including export-report.json, model-review.json, pack-validation.json and deployment.json.
- New combined pack: mc_moonshadow_heroes_v20_two_generals.pack.
- Previous mc_moonshadow_heroes_v19_hero_category.pack retained disabled. Disable v20 and re-enable v19 to roll back; do not enable both.
- Deployment copies only the new private pack and updates two launcher entries, with a launcher backup. No saves, native packs or Workshop files modified. No public distribution or Git upload.

Build tools: Export-Moon-General-Models.py, Review-Moon-General-Exports.py, Build-Moon-Generals-Pack.py, Deploy-Moon-Generals.py. Source donor assets remain under ignored reference/build paths.
