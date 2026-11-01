"""Run using the dedicated portable Blender: enable add-on and smoke-test donor imports."""
import json
from pathlib import Path
import addon_utils
import bpy

root = Path(__file__).resolve().parents[1]
reference = root / 'reference/local/yuan-bo-model'
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_rmv2', default_set=True, persistent=True)
assert 'io_scene_rmv2' in bpy.context.preferences.addons
bpy.context.preferences.addons['io_scene_rmv2'].preferences.texture_root = str(reference)
bpy.ops.wm.save_userpref()
assert bpy.ops.import_scene.tw_anim(filepath=str(reference/'animations/skeletons/humanoid01e.anim')) == {'FINISHED'}
rigs = [x for x in bpy.data.objects if x.type == 'ARMATURE']
assert len(rigs) == 1 and len(rigs[0].data.bones) == 96
body = reference/'variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.rigid_model_v2'
assert bpy.ops.import_scene.rmv2(filepath=str(body), import_all_lods=True, texture_root=str(reference)) == {'FINISHED'}
body_meshes = [x for x in bpy.data.objects if x.type == 'MESH']
assert len(body_meshes) == 7
assert sum(len(x.data.polygons) for x in body_meshes) == 53407
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None
sword = reference/'variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.rigid_model_v2'
assert bpy.ops.import_scene.rmv2(filepath=str(sword), import_all_lods=True, attach_armature=False, texture_root=str(reference)) == {'FINISHED'}
sword_meshes = [x for x in bpy.data.objects if x.type == 'MESH' and x not in body_meshes]
assert len(sword_meshes) == 4
assert sum(len(x.data.polygons) for x in sword_meshes) == 1946
report = dict(blender=bpy.app.version_string, addon='io_scene_rmv2 1.22.3',
              addon_enabled=True, skeleton_bones=96, body_meshes=7, sword_meshes=4,
              body_all_lod_triangles=53407, sword_all_lod_triangles=1946,
              images=[dict(name=x.name, size=list(x.size), has_data=x.has_data) for x in bpy.data.images],
              scope='Headless import test only; no game deployment or assembled scene saved')
(root/'reports/model-tools-blender-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('MODEL_TOOLCHAIN_IMPORT_OK', json.dumps(report))
