# Agents of the Moon — approved Jade Warrior reskin

Approved by the user on 26 November 2026. This regular Jade Warrior reskin is
separate from Divine Wing Guard.

**Current combined candidate: v37, installed and enabled**,
`mc_moonshadow_heroes_v37_zhao_cb_fix.pack`, SHA256
`da1d0ffe06b5ea210b55e1941bc43ed609dcbfda2680bc84209e8a4b1d2df2c1`.
It retains all approved Jade v2 payloads byte-for-byte and the Zhao redesign from
v36. Only two Zhao Custom Battle DB payloads changed in v37. V36 and standalone
Jade v1/v2 are disabled; existing files are preserved. Runtime confirmation is
pending and the user will test. The Moon-only Onyx hiding patch runs alongside.
The requested Git backup contains source/docs only, with no new models or packs.

The v2 family addon remains a separate preserved build; see its section below.

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
Authoritative portable checkpoints are now stored directly in ordinary Git in
`assets/working/moon-jade-warriors/`: `moon-jade-warriors-working.blend` (seven
variants), `moon-jade-warrior-animation-review.blend` (single model) and
`moon-jade-exported-assets-review.blend` (actual game-asset reimport). Exact hashes
and byte counts are in adjacent `checkpoint.json`. The user subsequently requested
avoiding unnecessary LFS; these scenes and the pack need no LFS download at the
current revision. Historical LFS objects have not been purged from GitHub storage.
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
was initially the **sword-and-shield** variant. V2 extends the approved human
body/head appearance to halberd, two crossbow units and Jade Lancers while keeping
their native equipment, shields and horse.

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

## V2 — shared human appearance for the entire Jade family

User requested the other four Jade unit types share the newly approved person
model. Built **mc_moon_jade_warriors_reskin_v2_family.pack**, 99,709,378 bytes,
SHA256 `9d711a7f571501f3c67a80b4f6d68da1b453f2a20d29c7e8e8248ddb68ba3ee1`.
Installed beside retained v1 in game data and copied to
`dist/moon-jade-warriors-reskin-v2/`. Enable **v2 and disable v1** in the launcher;
v2 is self-contained and includes v1. Launcher was not edited and game not run.

All five Moon-only unit appearances now use exactly the same exported common
body05, rear neckguard, normal brown boot toes and seven head choices:

| Unit | Key | Equipment |
|---|---|---|
| Jade Warriors | `wh3_main_cth_inf_jade_warriors_0` | Approved v1 custom dao and round 陳 shield retained |
| Jade Warriors (Halberds) | `wh3_main_cth_inf_jade_warriors_1` | Native halberd |
| Jade Warrior Crossbowmen | `wh3_main_cth_inf_jade_warrior_crossbowmen_0` | Native crossbow, bolt and sidearm |
| Jade Warrior Crossbowmen (Shields) | `wh3_main_cth_inf_jade_warrior_crossbowmen_1` | Native crossbow, bolt, sidearm and shield |
| Jade Lancers | `wh3_main_cth_cav_jade_lancers_0` | Native lance, shield and heavy horse |

Only the **human body/head slots** are replaced for the four new types. Their
native VMD equipment choices, attachment points, metadata and blood-stump slots
are retained. All four existing man-animation profiles use `humanoid01e`; profiles,
stats, mounts, recruitment and other factions are untouched. Do not interpret
the shared-person request as approval to replace these four types' weapons or
shields with the sword-and-shield unit's custom equipment.

V2 changes exactly two existing DB payloads (five Moon unit-variant rows plus
five private variant definitions) and adds four private VMDs. **Every other v1
payload remains byte-identical**, including all body/head meshes, four LODs,
textures, dao/shield and the original sword-and-shield VMD. IEE remains the only
declared mod dependency; DEER24 source pack is not required.

Validation: reimported shipped common human assets with native equipment; 18 native
clips at 54 representative frames including all seven head meshes. Inspected
halberd, crossbow, shielded crossbow and full heavy-horse/rider renders. Rider
clips use mount-root-relative coordinates, so the Blender presentation adds the
horse root translation; engine positioning is unmodified. Numerical checks and
sampled renders do not prove complete reload/bow-mechanism playback, absence of
all riding/clothing clipping, or game runtime safety. Native equipment animation
mechanics remain unchanged. RPFM DB roundtrip, exact v1-payload audit and **zero
diagnostic results** passed.

Reports/previews and four complete review scenes are local in
`build/moon-jade-reskin-v2/`. Source manifest updated; no new LFS rules or uploads.
The pack remains below GitHub's regular-file hard limit. Build tools:
`Prepare-Moon-Jade-Family-V2.py`, `Review-Moon-Jade-Family-V2.py`,
`Build-Moon-Jade-Family-V2.py`, `Install-Moon-Jade-Family-V2.py`.
