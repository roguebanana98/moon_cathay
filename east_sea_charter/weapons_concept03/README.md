# East Sea Charter — Concept 03 weapon meshes

Built in Blender 4.5.15 LTS using `build_weapons.py`. The approved image is included as `concept03_reference.png`.

## Deliverables

- `EDH_concept03_weapons.blend`: five named asset collections, editable component meshes, metallic/roughness materials, UVs, three orthographic/inspection cameras and a studio lighting collection.
- `EDH_Heinrich_Sword.glb`: broad, diamond-section steel blade, bronze guard, indigo grip, jade inset.
- `EDH_Heinrich_Shield.glb`: convex thick shield, indigo enamel, brass border and rivets, raised eagle/rock/sun emblem, timber-backed braces, hand grip and forearm strap.
- `EDH_Sariwa_Naga_Staff.glb`: blackwood shaft, five bronze cobra heads with jade eyes, grip, ferrules, bells and blue ribbons.
- `EDH_Sariwa_Sword.glb`: slender double-edged sword with bronze guard and jade pommel.
- `EDH_Sariwa_Scabbard.glb`: separate indigo scabbard with bronze mouth/chape and suspension fittings.
- `weapons_front.png`, `weapons_back.png`, `weapons_materials.png`: actual Blender renders of these meshes.
- `mesh_inventory.json`: component and triangle counts per asset.

## Editing and production status

These are a first editable 3D interpretation of the approved concept, with simplified ornament. They are not final sculpted or game-ready assets. Dimensions use metres; the staff is approximately 2.2 m long. Each collection has a named root empty. In the blend, roots are offset horizontally for inspection; each GLB is exported centred on its own root.

Construction curves and bevels have been converted to meshes. Components remain separate for editing. Meshes have a smart UV unwrap; materials are assigned per component. These are not a single packed texture atlas and no baked game texture maps are supplied.

Before WH3 deployment: refine ornament against the reference, retopologize/merge where appropriate, pack UVs and bake texture maps, make LODs, align weapon grip axes and dimensions against actual Empire Captain / Bretonnian Damsel assets, assign attachment/bone weights as required, export through the WH3 model pipeline, and check animations in game. No vanilla game files have been modified.

## Rebuild

Run Blender in background mode with `--python build_weapons.py`. The script rebuilds its scene and rewrites only the deliverables in this folder. Preserve manual mesh edits in a separate versioned blend before rebuilding.
