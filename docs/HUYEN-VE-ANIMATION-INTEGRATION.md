# Huyen Ve — model and animation integration v15

Historical v15 integration record. The user later reported an in-game T-pose;
fixed v16 corrected the missing custom runtime animation lookup and changed to
the approved appearance. Latest recorded private deployment v19 inherits this
fix. Do not select v15 or the intermediate unfixed v16 as the current test pack.
See [current Lord status](LEGENDARY-LORD.md) and
[approved appearance/animation fix](HUYEN-VE-APPROVED-MODEL.md).

Local integration completed 2026-11-02. Later the same day, the user explicitly
authorized test deployment. v15 was copied into the configured WH3 data folder,
hash verified, enabled at the previous v14 load-order position, and v14 disabled
while its file was preserved. IEE/MIXER/MCT and all other launcher entries are
unchanged. No Workshop/native pack/save edits or game runtime verification.

Deployment record: `build/huyen-ve-deployment/latest.json`. Launcher backup:
`build/huyen-ve-deployment/20261102-230047/20190104-moddata.dat`. To roll back,
disable v15 and enable v14 in the launcher; enable only one integrated version.
The launcher was requested through Steam for the user's Custom Battle test.

Viewer UI: `build/huyen-ve-animation-integration/huyen-ve-animation-browser.blend`
has an expanded native Action Editor below the 3D viewport, with the rig
selected. Click the action datablock dropdown beside the HV_* name, search or
scroll, choose a clip, then Space to play/pause. The live session includes an
automatic frame-range/FPS handler, tested by switching ATTACK_1 (end 62) to
DEATH_STAND_1 (end 116). This handler is session-only; it is enabled by running
`tools/Open-Huyen-Ve-Animation-Browser.py` inside Blender. Reopening the blend
preserves the Action Editor layout but does not automatically execute Python.
No security preferences were changed. The browser file only changes viewing
layout/action selection; the pack and model geometry are untouched.

Use `build/huyen-ve-animation-integration/mc_huyen_ve_v15_model_animations.pack`
as the integrated successor to v14 when testing; enable one integrated version.
It retains v14's equipment, abilities, localization, scripts and campaign
startpos. The change selects the new authored model and its native animation
set in battle and campaign, including the campaign 3D porthole uniform link.

The authored source is **the original hands**, from
`huyen-ve-user-sword-placement-20261102-211120.blend`, captured from the user's
live `huyen-ve-before-hand-fix.blend`. The rejected rebuilt-hand/grip-fixed
scene is not used. Body vertex positions, skin weights and all 96 native bone
bind matrices/hierarchy were hashed before/after and remain unchanged.

The approved sword object delta (-0.0252098087, -0.0738133043, +0.0113643212)
is baked into static prop vertices and carried to all four sword LODs. Its
object transform becomes identity without changing the approved placement.
VMD still attaches the separate sword to weapon_2. Static RMV2 matrix_index is
-1, preventing a second bone attachment from being serialized. The body keeps
four LODs at 24k/14k/8k/4k triangles. Embedded PNGs from the approved snapshot
were used to recreate the DDSs; intermediate textures from rejected revisions
were not reused.

## Animation graph

- Custom battle table `mc_huyen_ve_human`, skeleton `humanoid01e`, preserves the
  original ordered fragment references `hu1e_cathey_base` and
  `hu1e_dlc24_yuan_bo_dragon_jade`.
- Those fragments define 83 effective battle slots, including locomotion,
  attacks, defence, reactions, knockback/get-up, death, spell casting, idles,
  and pose/porthole entries. Native event/audio metadata references are kept.
- Campaign keeps `cam_lord_hu1e_dlc24_yuan_bo_dragon_jade`; the custom campaign
  uniform resolves to the authored variant rather than Yuan Bo's old body.
- The local Blender library contains **89 referenced clip/pose assets** from
  the donor graph and campaign table. Some are static or overlay poses rather
  than standalone full-body motions. Source animations are not retimed or
  rewritten. Native clips, fragments and campaign bins remain game references,
  rather than copied into the mod pack.
- Blender HV_* previews include constant identity keys for channels omitted
  by a clip, preventing pose values from a previously selected action from
  leaking into the next preview. Native keyed channels and game assets are
  unchanged; partial pose layering still belongs to the game graph.
- 17 pre-existing native metadata paths were not found in the direct native
  pack indexes consulted. They are recorded in the manifest and left exactly
  as the native graph specifies; this audit does not establish their absence
  from engine resources or nested containers. All referenced .anim clips and
  core table/fragment/bin files resolved.

## Deliverables and checks

All generated deliverables are under ignored `build/huyen-ve-animation-integration/`:

- `huyen-ve-all-animations.blend`: packed textures, original approved body,
  all 89 HV_* actions, index in Blender Text datablock
  `HUYEN VE - ANIMATION INDEX`. Select `humanoid01e_HuyenVe`, open Dope Sheet →
  Action Editor, choose an HV_* action. Action custom properties give source
  path, native slots, FPS and end frame. Initial action is ATTACK_1; viewport
  follows root. A partial pose needs its native game layering context.
- `mc_huyen_ve_v15_model_animations.pack`: 107 payloads, including 20 additions
  over v14. Only three existing DB payloads change: unit animation table,
  unit variant and campaign uniform links. Every other existing payload is
  byte-identical; within those three rows only the documented link fields
  change. Native stats, abilities, equipment and startpos are unchanged.
- `animation-set-manifest.json`, `scene-integration-report.json`,
  `animation-roundtrip-validation.json`, `integration-links.json`,
  `export-validation.json`, `pack-validation.json`, `pack-manifest.json` and
  `diagnostics.txt`: dependency inventory, source preservation, actual-export
  checks, DB graph and final pack evidence.

The actual body RMV2 was imported back and compared against the authoring rig
at start/middle/end of every clip/pose: **259 distinct sampled poses**, maximum
deformed position difference about **0.00342 scene units**. The actual static
sword export was compared against every authored LOD. RPFM diagnostics have
zero new/changed diagnostic groups relative to v14; 12 existing groups remain.
All added non-DB payloads and all extracted DB rows match prepared outputs.

Pack SHA256: `208050cfcd59f7c7f5ad5dfd7ef619d18883681f271e215bfb7bff5086176fd6`.

These checks verify integration/file consistency, not perfect hand closure,
garment collision, events, FX or every transition in game. The original Tripo
hand/robe quality remains as approved for this step. No hand reconstruction
or animation-key edits are part of this integration. Runtime battle, campaign,
porthole and LOD review remain necessary before a release-quality claim.

## Rebuild

Use `blender_authoring` (the existing Blender 5.2 installation) and Python/
RPFM/texconv paths in `config/local.json`. Preserve prior generated packs; the
pack builder refuses to overwrite an existing v15 artifact. Native reference
DBs and pack indexes are under ignored `reference/local/`.

1. Python `tools/Audit-Huyen-Ve-Animation-Set.py` resolves/extracts references.
2. Blender background `--python-exit-code 1 --python tools/Build-Huyen-Ve-Animation-Scene.py`.
3. Python `tools/Prepare-Huyen-Ve-Model-Graph.py` with the integration output
   directory as its argument, then `tools/Validate-Huyen-Ve-Model.py` with that
   same argument.
4. Python `tools/Prepare-Huyen-Ve-Animation-Links.py`.
5. Blender background `--python-exit-code 1 --python tools/Verify-Huyen-Ve-Animation-Roundtrip.py`.
6. PowerShell `tools/Build-Huyen-Ve-Animation-Pack.ps1`.

`tools/Export-Huyen-Ve-Static-Sword.py` is an optional re-export-only repair
helper; the main scene builder already removes the preview constraint target
while exporting so that matrix_index remains -1. The earlier
`Build-Huyen-Ve-Model.py` rebuilt rejected hands and is now explicitly gated as
an experimental legacy generator; it is not the current build pipeline.
