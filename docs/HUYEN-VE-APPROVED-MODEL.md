# Huyen Ve — approved appearance

Current status note (2026-11-03): the fixed v16 appearance/animation is inherited
by v17, v18 and the latest recorded deployed private test pack v19. The statements
below that v16 itself had not been deployed describe the original v16 build stage,
not the status of its integrated descendants. Runtime confirmation is still pending.
See [current Lord status](LEGENDARY-LORD.md).

User approved the current Blender appearance on 2026-11-03 (Asia/Saigon).
This supersedes the concept03/Tripo body as the selected appearance for future integration.

Approved snapshot: `build/huyen-ve-model-v2/huyen-ve-approved-20261103.blend`.
Machine-readable visibility list and SHA-256: `build/huyen-ve-model-v2/approved-model.json`.

Source: installed Workshop mod 3468491534, **Yuan Bo Reskin & Buff + Jade Court flag change**.
Use the original uncut head/neck and native humanoid01e rig with the clean-shaven face texture.
Keep the two iron-human leg pieces visible; waist and both arm pieces are hidden.
Other visibility choices are recorded in the manifest. Hidden objects and the original
combined backup remain available for editing and must be excluded from game export.

The private Blender snapshot contains reference-derived assets and stays in ignored build/.
Private integration completed in `build/huyen-ve-v16-approved/`:

**Runtime animation fix (2026-11-03): use `mc_huyen_ve_v16_native_anim_fix.pack`.**
The earlier v15 and intermediate `mc_huyen_ve_v16_approved_model.pack` pointed
`land_units.man_animation` to `mc_huyen_ve_human` without a compiled runtime
BIN/ANIMPACK for that key. Their JSON/TXT animation table does not supply that
runtime database. This is a confirmed packaging defect consistent with the
user's report of an in-game T-pose; final engine confirmation is pending.
The fixed pack uses `hu1e_dlc24_yuan_bo_dragon_jade` directly. Its native runtime
BIN was verified inside installed `animation_tables.animpack` and
`animation_tables__.animpack`. The unused custom animation DB row/TXT are removed.
Only `man_animation` changes in the land-unit row; all model assets remain
byte-identical to the intermediate v16. See `runtime-animation-fix.json` and
`native-animation-runtime-audit.json`.

Do not deploy the intermediate v16 or claim Blender clip playback proves the
engine lookup works. `Build-Huyen-Ve-Approved-Pack.py` now always calls
`Fix-Huyen-Ve-Runtime-Animation-Link.py` before completion. Run
`Verify-Huyen-Ve-Actual-Motion.py` as well: it checks actual evaluated vertex
displacement across frames, rather than finite coordinates alone. Preview actions
must have fake users so all 89 survive saving/reopening the Blender file.

- Pack: `mc_huyen_ve_v16_approved_model.pack`, built over the existing v15 pack.
- Original mod LODs reused: 69,142 / 32,980 / 23,477 / 14,859 triangles after
  excluding disabled parts. Native transition distances remain 20 / 80 / 100 / 10000.
- All retained positions, normals, tangents, binormals, UV0, bone indices and
  weights were checked exactly equal to the native source after RMV2 write/read.
  Original head/neck geometry remains uncut at every LOD.
- Clean-shaven texture converted to 1024 DDS with mipmaps and explicit sRGB input/output.
  Empty donor MASK_PATH placeholders replaced with a neutral, non-emissive mask.
- Lotus sword retains four LODs; the old concept03-only placement offset is removed
  to fit native Yuan Bo hands. Sword position roundtrip error is under 0.001 game units.
- 89 animation actions checked at 259 sampled poses on exported LOD0. All deformations
  were finite and sword attachment matched weapon_2. This is data validation, not
  exhaustive visual clipping or in-game verification.
- 77 graphics payloads checked against actual pack bytes. All non-graphics entries,
  including DB, startpos and animation tables, remain byte-identical to v15.
  RPFM diagnostics introduce no changed/new findings compared with v15.

Reports: `graphics-validation.json`, `animation-validation.json`,
`sword-native-fit.json`, and `pack-validation.json` in that build directory.
Review scene: `huyen-ve-v16-animation-review.blend` (Blender 5.2.3).

Rebuild order: `Build-Huyen-Ve-Approved-Graphics.py`,
`Prepare-Huyen-Ve-Native-Sword-Fit.py`, `Verify-Huyen-Ve-Approved-Animations.py`
(Blender 5.2.3 with prepared add-on), `Build-Huyen-Ve-Approved-Pack.py`, then
RPFM diagnose and `Validate-Huyen-Ve-Approved-Diagnostics.py`.
Pack creation refuses overwriting an existing v16 file.

Existing v15 deployment is unchanged. The fixed v16 still requires in-game review; it has
not been copied to game/Workshop or published. The donor mod's buffs and flag
changes were not imported.
