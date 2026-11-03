"""Static VMD prop export: do not serialize a second bone attachment."""
import bpy,addon_utils,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/huyen-ve-animation-integration'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-all-animations.blend'))
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
rig=bpy.data.objects['humanoid01e_HuyenVe'];rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis.identity()
for i in range(4):
 o=bpy.data.objects['mc_huyen_ve_sword_lod'+str(i)];o.constraints[0].mute=True;o.constraints[0].target=None
bpy.context.view_layer.update()
def find(layer):
 if layer.collection.name=='mc_huyen_ve_sword':return layer
 for child in layer.children:
  found=find(child)
  if found:return found
bpy.context.view_layer.active_layer_collection=find(bpy.context.view_layer.layer_collection)
bpy.ops.object.select_all(action='DESELECT');o=bpy.data.objects['mc_huyen_ve_sword_lod0'];o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
assert bpy.ops.export_scene.rmv2(filepath=str(O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_sword.rigid_model_v2'),source='COLLECTION',skeleton_name='',auto_lods=False,apply_modifiers=True)=={'FINISHED'}
# No scene save: live preview constraints remain intact in the deliverable.
