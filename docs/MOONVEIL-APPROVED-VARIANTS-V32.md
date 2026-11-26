# Moonveil Adept approved appearances - 2026-11-24

User selected gallery models 02,06,10,14 from moonveil-black-all-bodies-heads.blend. Exact pinned pairs:

| Gallery | Body | Head | Retained appearance ID |
| --- | --- | --- | --- |
| 02 | black body01 | black head2 | mc_moonveil_adept_white |
| 06 | black body03 | black head2 | mc_moonveil_adept_black |
| 10 | black body01a | black head2 | mc_moonveil_adept_blue |
| 14 | black body03a | black head2 | mc_moonveil_adept_red |

These are four clothing/body variants with the SAME selected head2, not four different faces. Appearance IDs retain old palette suffixes for compatibility with existing campaign art/uniform IDs. Each VMD now has exactly one body and one head, so unselected body/head options cannot be randomly chosen. The existing root VMD and four artsets still distribute the four approved appearances.

Built directly on active v30. Rejected v31 is not a dependency and remains undeployed. Only four appearance VMDs and their portrait/card PNGs are replaced. Meshes, texture DDS, materials, bones, weights, four LODs, native Alchemist animations, all DB/script/localization payloads, stats, skills, mounts and recruitment remain unchanged. v30 building preview permissions and v29 general recruitment tabs are preserved byte-for-byte. Selected variants apply to battle/campaign and native mounted uniforms through the unchanged appearance IDs.

Blender review covers idle/walk/run/attack/casting and native mounted rider samples, finite deformation and nonzero motion. Portraits rerendered from each exact selected pair. A dedicated editable approved scene is saved at build/moonveil-v32-approved-variants/moonveil-approved-02-06-10-14.blend; the original 16-model gallery is unchanged. Static checks are not game-runtime confirmation.

Build/validation reports: build/moonveil-v32-approved-variants. Tools: Prepare-Moonveil-Approved-Variants.py, Review-Moonveil-Approved-Variants.py, Save-Moonveil-Approved-Scene.py, Build-Moonveil-Approved-Variant-Pack.py, Deploy-Moonveil-Approved-Variants.py. DB extraction: reference/local/moon-v32-roundtrip/db. No Workshop/native pack or save modification; private local derivative only.
