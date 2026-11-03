# Huyen Ve — concept03 local rig prototype

Appearance selection superseded on 2026-11-03: use
[the approved intact reskin model](HUYEN-VE-APPROVED-MODEL.md) for future model work.
The concept03 body and integration notes below are historical. The approved source
was integrated in fixed v16 and inherited by the latest recorded deployed private
test v19. See [current Lord status](LEGENDARY-LORD.md); runtime checks remain pending.

Updated 2026-11-02. This is a **rig prototype requiring garment cleanup and
game testing**, not a release-ready character. Original FBX and lotus sword
sources remain untouched. The current gameplay build remains v14 native icons.

CURRENT HANDOFF: v15 now integrates the approved original hands/manual sword
placement and complete native animation graph. See
[HUYEN-VE-ANIMATION-INTEGRATION.md](HUYEN-VE-ANIMATION-INTEGRATION.md).
The v1/rebuilt-hand reports below are historical and are not the current
model/animation deliverables.

USER REVIEW OVERRIDES THE EARLIER GRIP STATUS: the user rejected the rebuilt
hands as damaged. The next step is manual sword placement by the user, not
further automatic hand reconstruction. Baseline recorded from the saved
`huyen-ve-before-hand-fix.blend` at QA_stand frame 1:
`sword-placement-baselines/20261102-205852-939967.json`. The earlier baseline
from grip-fixed was selected in error and must not be used. Work only on
before-hand-fix for the user's manual placement. This baseline includes local/world
transforms, mesh coordinates/hashes and weapon_2/constraint matrices. Compare
the user's saved edited file to this baseline before applying any offsets.

Manual placement received from the live before-hand-fix window at QA_stand
frame 0. Preserved copy: `huyen-ve-user-sword-placement-20261102-211120.blend`;
report `sword-manual-adjustment-20261102-211120.json`. Object translation delta
XYZ is (-0.0252098087, -0.0738133043, +0.0113643212), no rotation or scale
change. Sword vertex hash matches the baseline. No changes to hands, body,
bones, constraints, other LODs or exports were made during capture. The source
file on disk had not been saved by the user; use this preserved copy for the
next step, not the stale disk version or rejected grip-fixed revision.

Animation review of that manual placement is now available in
`huyen-ve-manual-sword-attack-preview.blend`: native QA_attack, frames 0-62,
30 fps, viewport locked to root. Body/sword vertex hashes and sword basis
matrix were checked unchanged. This selects an existing animation for review;
it does not edit native keys or establish that the grip is correct in every
pose. Script: `tools/Prepare-Huyen-Ve-Manual-Attack.py`.

Preview fix: the initial file saved the Layout viewport in Solid mode. All 3D
viewports now open in Material Preview, and the eight body/sword texture inputs
use PNGs packed inside the blend. This also restores the intended colour in
the Blender preview previously using DDS. Saved-file reopening and embedded
image presence were verified; `qa_textured.png` is the corrected render.
The exported DDS/RMV2 and graphics pack are unchanged by this preview fix.

Grip correction (later on 2026-11-02): the fused Tripo hands were replaced
with authored palms, wrist bridges and four articulated fingers plus thumb
per hand. The native two long-finger chains each drive a pair of fingers;
thumb uses its own chain. Distal gauntlets are fitted to the wrist landmarks,
and authored hand weights are excluded from garment smoothing. Skin colour
samples the source hand texture; nails and detailed skin UVs are not authored.
This is functional prototype hand geometry, not finished close-up hand art.

Sword prop translation is now (-0.035, 0.020, 0); the authored grip/pommel is
30% longer to accommodate the native two-hand grip. Native animations, bone
bind matrices and hierarchy remain unchanged. The full 63-frame attack clip
passes finite deformation and weapon_2 attachment checks. Both hands touch
the grip in the reviewed frame-20 pose; proximity checks do not prove absence
of penetration in every pose. New close-ups: `grip_final_stand.png` and
`grip_final_attack.png`; report `grip-validation.json`.

`huyen-ve-sword-grip-fixed.blend` is a copy of the updated main scene, opening
with QA_attack frames 0-62 ready to play, frame 20 selected. The viewport locks
to the rig's root bone so native root motion stays in view. The earlier open
UI scene was preserved as `huyen-ve-ui-before-grip-update.blend` before loading
the correction. The corrected body/sword RMV2 and graphics pack were rebuilt
and validated too; gameplay integration remains unchanged.

## Deliverables

All generated binary assets are in ignored `build/huyen-ve-model-v1/`:

- `huyen-ve-rigged-prototype.blend`: body, separate sword, native humanoid01e
  rig, four stored QA actions, lights/camera. Hidden native reference geometry
  is present only in this private working scene, excluded from model exports.
- `variantmeshes/`: exported body/sword RMV2, WSMODEL, material XMLs, DDS textures
  and `mc_huyen_ve_human.variantmeshdefinition`.
- `mc_huyen_ve_model_v1_assets.pack`: 16 graphics assets only. No DB links or
  gameplay tables; loading it alone does not switch Huyen Ve's current model.
- `qa_stand.png`, `qa_run.png`, `qa_attack.png`, `qa_cast.png`: sampled poses.
- `model-build-report.json`, `export-validation.json`,
  `roundtrip-validation.json`, `pack-manifest.json`: measured build checks.

## Mesh and rig

| Part | LOD0 | LOD1 | LOD2 | LOD3 |
|---|---:|---:|---:|---:|
| Body triangles | 24,000 | 13,999 | 7,999 | 3,999 |
| Sword triangles | 1,800 | 1,100 | 600 | 466 |

Body reduction is UV-preserving decimation from 474,836 triangles, about 95%
fewer triangles at LOD0. This is not hand-built retopology. Original UVs remain;
exported vertex counts are higher than Blender counts due to UV/normal splits.

The body is fitted to Yuan Bo's 96-bone `humanoid01e` skeleton. The donor was
posed to the Tripo low-A pose before barycentric surface weight transfer;
inverse linear skinning returns the new mesh to the original native bind pose.
Bone hierarchy/order and native bind matrices are preserved. High LODs use at
most four normalized weights per vertex, lower LODs two. No unweighted vertices.
Head/hair primarily follow head_0; facial performance is not authored.

The authored lotus sword is a **separate static prop**, attached through the
VMD slot and attach_point `weapon_2`. The Blender Child Of constraint previews
that attachment; static export happens before adding the preview constraint.
Its material is baked to an atlas. This work does not add or verify sword FX.

## Materials

- Body maps: 2048². Sword colour/material atlas: 1024²; normal/mask: 512².
- Base colour BC7 sRGB; material map BC7 with R metallic, G roughness.
- Normal converted to the add-on's WH3 orange layout, BC3, with DirectX Y.
- Full mip chains. Mask zero disables faction recolouring/emission for now.
- Weighted4/weighted2 body materials and rigid sword material, emission strength
  zero. The Blender preview is not proof of the final WH3 shader appearance.

## Verification and remaining work

Binary checks cover RMV2 v8, four LODs, indices, finite coordinates, bone limits,
weight sums, DDS dimensions/mips and the VMD/material/texture dependency graph.
The actual exported RMV2 is imported back and compared to Blender skinning at
12 poses: first/middle/last of stand, run, attack and spell cast. The roundtrip
report records the export SHA256 so a stale test cannot authorize packaging.
The pack is extracted again and all 16 payload hashes must match.

Final local build: 12/12 sampled export comparisons passed; largest position
difference 0.002426 scene units (about 2.43 mm if one unit is one metre).
All 16 extracted pack payloads match their source hashes. Original FBX and all
five source texture hashes still match intake. Final pack SHA256:
`ba70f79318017e05aecdf6d5cb9c41d4e8b09fdd84ce36985caf58ef795297d3`.

These checks prove file consistency, **not anatomical or garment quality**.
The Tripo mesh has fused/intersecting cloth, pants and armour surfaces. A
continuous leg/cloth weight field avoids opening artificial ankle seams, but
the robe still compresses, stretches and clips in deep locomotion poses. Broad
shoulder armour and remaining finger intersections also need closer pose review. Further cleanup must
separate garment surfaces deliberately, repair hidden geometry and refine
weights; sampled edge-stretch diagnostics remain warnings, not a passed visual
quality gate. No claim is made that all native animations have been reviewed.

No files have been installed into the game/Workshop, no campaign/save has been
changed and no WH3 runtime or FX test has been performed.

## Rebuild order

Use paths from `config/local.json`, not guessed executables:

1. Python `tools/Convert-Huyen-Ve-Textures.py`.
2. Blender background `--python-exit-code 1 --python tools/Build-Huyen-Ve-Model.py`.
3. Blender background `--python-exit-code 1 --python tools/Verify-Huyen-Ve-Roundtrip.py`.
4. Blender background `--python-exit-code 1 --python tools/Validate-Huyen-Ve-Grip.py`.
5. Blender background `--python-exit-code 1 --python tools/Prepare-Huyen-Ve-Attack-Preview.py`.
6. PowerShell `tools/Build-Huyen-Ve-Model-Pack.ps1` (generates graph, validates,
   packs and verifies extracted payloads). It refuses to overwrite an existing
   pack; preserve prior local outputs explicitly before rebuilding.

Native donor/animation files must already exist under ignored `reference/local/`.
Do not redistribute the private reference scene or CA reference assets.
