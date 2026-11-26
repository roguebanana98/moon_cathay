# Agents of the Moon — approved Jade Warrior reskin

Approved by the user on 26 November 2026. This is the separate regular Jade
Warrior reskin project, not Divine Wing Guard and not the deferred Zhao work.

## Approved appearance

- DEER24 Jade Warriors Reskin body option **05**, preserving its current armour,
  clothing and colours. Source Workshop item `2965749119`, pack
  `@DEER24JadeWarriorRESKIN2.pack`.
- Existing model05 helmet, plus the **rear neckguard only** from option06.
- Round shield with the user's red calligraphic **陳** replacing the original motif.
- Reference-inspired long dao: brown wooden handle, small dark disc guard, ring
  pommel. Corrected cutting edge on the same side as the native Jade sword;
  opposite side is a flat blunt spine, approximately **9.4437 mm** thick along
  most of the blade, tapering into its point. Preserve native grip pivot.
- Flattened, shortened boot toes, painted brown to match the boot leather.
- All **seven original DEER head options** (`beitingsheshouh1` through `h7`),
  preserving source faces, facial hair and hair. These are source head options,
  not a claim of seven different face geometries. No other body/helmet variants.
  Head07's covered upper scalp/hair is tucked inside the helmet to prevent two
  visible hair spikes; its visible face, moustache and skin weights are retained.

## Editable checkpoints

The user explicitly requested Git backup of models and mod after the build.
Authoritative portable checkpoints are now tracked through Git LFS in
`assets/working/moon-jade-warriors/`: `moon-jade-warriors-working.blend` (seven
variants), `moon-jade-warrior-animation-review.blend` (single model) and
`moon-jade-exported-assets-review.blend` (actual game-asset reimport). Exact hashes
and byte counts are in adjacent `checkpoint.json`. Run `git lfs pull` after clone.
The completed pack is tracked at
`releases/moon-jade-warriors-reskin-v1/mc_moon_jade_warriors_reskin_v1.pack`.

Historical local build paths below remain ignored:

- `build/moon-jade-approved-variants/approved-single-model-animation-checkpoint.blend`:
  exact copy of the final approved single-model animation scene.
- `build/moon-jade-approved-variants/moon-jade-warriors-approved-seven-variants-v2.blend`:
  seven complete editable character variants with native humanoid01e rig,
  current equipment and shared eight-stage animation review.
- `build/moon-jade-approved-variants/approved-variants-report.json`: source hash,
  variant keys, source head mapping, validation and image packing metadata.
- `build/moon-jade-approved-variants/moon-jade-seven-variants.png` and
  `face-01.png` through `face-07.png`: appearance review renders.
  `face-07-helmet-fit.png` supersedes the initial head07 close-up.

Open the complete scene; preserve hidden originals, comparison objects and studio
flags. Continue from these checkpoints; do not regenerate over user edits. The
original live review and every prior scene remain untouched. Git backup is
explicitly authorized for these model checkpoints and the completed mod pack;
raw native/Workshop extracts and machine-specific caches remain ignored.

## Animation review

Eight native sword/shield stages, frames **1–630**: idle 1–120, walk 121–240,
run 241–360, charge 361–450, attackA 451–486, attackB 487–548,
jump attack 549–586, defend 587–630. Root horizontal travel is removed for
stationary Blender presentation. This montage must not be exported as native
game animation. Finite mesh samples and inspected renders do not prove absence
of clipping in every frame or in the game.

## Integration scope and current status

Intended for **Agents of the Moon only**. Do not globally replace Cathay's native
Jade Warrior model paths or alter other factions. The current approved equipment
is the **sword-and-shield** variant; halberd, crossbow and cavalry equipment have
not been adapted or reviewed as part of this appearance family.

## Standalone mod built — 26 November 2026

The user subsequently requested creating the mod. Built
`mc_moon_jade_warriors_reskin_v1.pack`, **99,690,815 bytes**, SHA256
`3809a4b684c0e9b3f3b1183ed9fb1d799bb7a05195bf8e91deb675932b02952e`.

Installed into the verified game's `data` directory and copied to
`dist/moon-jade-warriors-reskin-v1/`. **Launcher unchanged; mod not enabled;
game not launched and runtime appearance unverified.** Enable this pack with IEE
and its existing dependencies. The pack declares
`!cr_immortal_empires_expanded.pack`; the original DEER24 pack is not required.
Load after another mod if that mod also overrides Moon's Jade Warrior appearance.

Exactly one faction-scoped `unit_variants` row for
`cr_cth_agents_of_the_moon` + `wh3_main_cth_inf_jade_warriors_0`, and one private
`variants` definition. Native unit card and scale retained. No land/main-unit,
stats, recruitment, skill, script, animation or other-faction overrides. This is
a separate addon; it does not require reconstructing or rewriting missing v34.

Private namespace `variantmeshes/wh_variantmodels/mc_moon_jade_reskin` contains
common body, seven coherent head options, dao and shield, each with **four LODs**.
The private VMD selects the seven heads and attaches dao/shield to native
`weapon_2`/`weapon_3`; original prop material pivots are retained. Source procedural
colours/PBR and boot paint were baked to DDS; explicit sRGB input prevents double
gamma in base colour. Shield normal bake removes the old motif relief. Lower LOD
decimation can merge influences: exporter retains the four strongest weights and
renormalizes, as recorded in `export-report.json`.

Validation: actual RMV2/DDS reimport, all seven heads sampled through eight native
sword/shield clips at 24 poses, finite evaluated meshes and verified prop pivots;
actual export full-body/head renders inspected. RPFM DB roundtrip and packaged
payload byte equality passed. **RPFM diagnostics returned zero results**. These
checks do not prove in-game animation/clipping safety. User should inspect the
long dao handle, shield, neckguard and shoes in combat after enabling.

Reports and actual exported model review:
`build/moon-jade-reskin-v1/`; portable distribution instructions in
`dist/moon-jade-warriors-reskin-v1/README.txt`. Build tools:
`Export-Moon-Jade-Reskin.py`, `Correct-Moon-Jade-DDS-Colour.py`,
`Review-Moon-Jade-Exported-Assets.py`, `Build-Moon-Jade-Reskin-Pack.py`,
`Install-Moon-Jade-Reskin-Pack.py`. Do not overwrite approved source scenes.
