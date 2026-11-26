# Da Anh Legendary Hero appearance v8

Da Anh now uses the approved Celestial Concubines body01 and head01, two
Dark Society Death Squad knives, opaque black fitted fabric on torso/arms/legs,
and original charcoal cloth extended across the chest openings. Gold ornaments
and shoulder dragons are hidden; the two plain shoulder plates remain. Structural
footwear is charcoal. Hidden source geometry remains recoverable in the authoring file.

Authoring checkpoint: `assets/working/da-anh/da-anh-legendary-hero.blend`.
The original source hash is recorded in `checkpoint.json`; its embedded pending
integration notes describe the checkpoint creation stage. Current deployment state
is recorded by the external checkpoint and deployment reports.

## Installed build

Enabled `mc_moonshadow_heroes_v8_da_anh.pack` in game/data and the launcher.
Retained v7 disabled. All unrelated launcher entries and previous pack files were
verified unchanged; launcher backed up before replacement. No saves, native game
packs or Workshop files changed; no game launch and no Git upload.

Pack SHA256: `37f3aa7a52438aca2ff56e439feb073d76135890dd5f3ad168036222695a26e6`.
Authoritative reports: `build/da-anh-v8-appearance/deployment.json`,
`pack-validation.json`, `export-report.json`, `campaign-animation-check.json`.

## Runtime setup

The user explicitly selected sword-and-shield animations while keeping two knives.
Battle: `hu1e_sword_and_shield`. Campaign:
`cam_hero_hu1e_dlc24_gatemaster_sword_and_shield` (available native game asset).
The left-hand motion therefore retains the shield role, with a knife visually in
that hand as requested; this is not a dual-dagger animation set.

The genuine 96-bone humanoid01e bind and body weights are retained. Both knives
are baked into the weighted body RMV with one hand-bone influence per knife,
using the corrected handle-to-palm transforms. This reproduces the Blender grip
without custom animation databases, skeletons, or Blender-only runtime constraints.
Four LODs: 46296 / 23145 / 11570 / 5781 triangles; nine parts in each LOD.
All texture references are included in the new pack. Black procedural fabric uses
constant PBR maps at runtime; chest-cloth material/normal maps are neutral fabric
while its colour is taken from the original cloth atlas. Microbump is not exported.

Da Anh is now configured as melee: removed old handbow/ammo and skirmish setting,
melee unit category, female presentation and zero missile valuation. Existing melee
weapon, combat stats, cap, skills, effects, spawning and recruitment are unchanged.
All four Moonshadow Assassin appearances and every unrelated payload/row are
unchanged from v7. Battle/campaign uniforms, VMD, cards and portraits point to the
new Da Anh assets. Existing campaign art-set ID is retained.

## Validation and limits

Reimported the actual exported RMV on the native rig and sampled six battle clips
(18 poses), plus two native campaign clips (6 poses). Geometry remained finite and
showed nonzero motion. Verified four LODs, weight normalization, native bone index
limits, DDS references, TSV pack roundtrips, and zero blocking RPFM diagnostics
(schema metadata warnings only). Rendered new cards and head portraits from the
exported RMV. These checks do not prove in-game appearance or absence of all
clipping. Restart/reload campaign to test; cached appearance in an old save has
not been assessed. Existing ranged-themed skills are retained; this update does
not redesign the skill tree or its balance.
