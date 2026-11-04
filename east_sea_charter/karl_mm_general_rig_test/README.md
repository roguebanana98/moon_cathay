# Karl Franz Reskin - MM on the Empire General rig

Local Blender compatibility test requested by the user. No game/workshop pack was modified.

- Source: installed Workshop item 3728324408, `Karl Franz Reskin - MM.pack`; SHA256 is recorded in `reference_manifest.json` and `test_report.json`.
- Original mod body: 25 LOD0 meshes, 26,320 triangles. Original geometry, UVs and skin weights retained.
- Native on-foot donor: `wh_main_emp_cha_general_0`. The installed `land_units` row resolves to `hu1_empire_sword_and_shield`, whose native animation table identifies skeleton `humanoid01`.
- Both the mod body and native General body RMV2 headers identify `humanoid01`; the shared skeleton has 72 bones. The mod's vertex groups resolve against those native bone indices, so no automatic reweight or bone remapping was needed for this test.
- Props: native `emp_general_sword_1h_01` and `emp_general_shield_01`. Their original VMD uses `be_prop_1` and `be_prop_2`. The Blender rigid constraints remove only the importer's cosmetic bone-axis rotation, leaving native prop transforms intact.
- Material overrides come from the mod's `.wsmodel` and XML material files. Used textures are embedded in the final blend (39 packed images). This is a Blender shader preview, not an exact reproduction of the game shader.

Open `Karl_MM_on_Empire_General_TEST.blend` and play frames 1–444. An NLA track sequences 8 labelled native clips: stand, idle, walk, run, three attacks and combat idle. The source action library is preserved. Show viewport overlays to inspect the stick armature.

`test_report.json` records nine sampled frames per clip: all evaluated mesh positions were finite and within broad sanity bounds; rigid sword/shield transforms matched native attachment matrices within 1e-4. This is not a complete collision/intersection test. Full original geometry was hashed before and after animation import and stayed unchanged.

`preview_idle.png` and `preview_attack.png` are actual Blender renders. `rig_probe.json` records native bones/model headers. Scripts and extracted references are retained for reproducibility. The tested scope is on-foot Blender preview; mounted variants, game export, lower LODs and in-game runtime are not tested.
