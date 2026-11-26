# Moonshadow Assassin v7 appearance integration

The user explicitly requested game integration of the four approved appearances
on 2026-11-21. Installed and enabled:

`F:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data/mc_moonshadow_heroes_v7_appearance.pack`

V6 `mc_moonshadow_heroes_v6_celestial_tower.pack` remains on disk, disabled.
Launcher backup and deployed SHA are recorded in
`build/moonshadow-v7-appearance/deployment.json`.

## Appearance and runtime binding

Four whole-body variants pair the approved common outfit with faces 08, 11,
03 and 12. Battle variant `mc_moonshadow_assassin` includes all four. Four
campaign art rows select individual uniforms/VMDs and matching portrait variants.
The original generic art ID maps to face 08, allowing existing characters to
resolve an updated appearance. Other faces can be selected for new characters.
Actual campaign art-selection/persistence has not been engine-tested.

Right-hand Death Squad knife and left-hand Khainite handbow are exported as
static props attached once through VMD `be_prop_1` / `be_prop_5`. Baked prop
offsets reproduce the approved grip in the native standing pose. The old test
Blender hand-anchor constraints are not relied on by the game.

All meshes use the genuine native 83-bone `humanoid01d` index order. Existing
`hu1d_elf_sword_and_handbow` battle and
`cam_hero_hu1d_elf_sword_and_handbow` campaign lookup keys remain unchanged.
No custom animation lookup or source-only animation table is introduced.

The exported rest geometry is a runtime derivative, not an overwrite of the
approved 01e Blender files. It is fitted to their evaluated approved standing
surface, then inverse-skinned into the native 01d bind using mapped, normalized
top-four weights. Corner normals are inverse-skinned too. This avoids changing
the hood/robe silhouette through incompatible bone-rest/cosmetic axes. The hood
uses the head bone; the short robe uses a continuous waist/root field with a
small thigh blend at the hem rather than unrelated Elf cloak pivots.

Earlier direct-rest-matrix trials distorted the hood and robe and were rejected;
they were never deployed. Current export is the final inverse-skin fit.

## Assets

- Four body/head RMVs and two prop RMVs, each with four decreasing LODs.
- 33 self-contained DDS maps, including baked black hood and charcoal ornament.
- Five VMDs (four individual campaign appearances and one mixed battle variant).
- New rendered unit card, minspec porthole and four campaign portrait choices.

The game assets do not require enabling the donor Workshop appearance packs.
Original source/reference/native/Workshop assets were not changed.

## Validation and limits

`pack-validation.json` records RPFM DB round trips, all model/texture paths,
skeleton headers, bone-index ranges, normalized weights and LOD counts. There
are zero blocking diagnostics; schema metadata warnings remain. Only six
existing appearance/UI entries differ from v6. Added entries are appearance
links/assets; recruitment, skills, stats, localization, spawn Lua and Da Anh
payloads are unchanged.

`roundtrip-animation-check.json` records reimport of all four actual exported
LOD0 RMVs against the native rig and eight native clips, sampled at three
frames each (96 poses). File hashes tie the checks to the exported geometry.
The meshes deform and do not remain static in those checks. This does not prove
the game runtime or establish every possible animation/collision is clean.
Finger closure and cloth may still need visual refinement during engine tests.

No game was launched and no saves were modified. Reload the campaign to test
existing Moonshadow Assassins and recruit additional ones to inspect all faces.
Da Anh deliberately keeps its previous appearance.

Source scripts:
`Export-Moonshadow-Appearances.py`, `Check-Moonshadow-Export-Roundtrip.py`,
`Render-Moonshadow-Game-Cards.py`, `Build-Moonshadow-Appearance-Pack.py`,
`Deploy-Moonshadow-Appearance.py` under `tools/`.

All authoritative build reports are under `build/moonshadow-v7-appearance/`.
The approved editable appearance checkpoint remains
`build/moonshadow-assassin-final/moonshadow-assassin-final.blend`.
