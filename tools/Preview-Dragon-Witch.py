"""Separate Dragon Witch source preview, no mod changes."""
import bpy,addon_utils,sys,json,subprocess,ast,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/dragon-witch';O=R/'build/dragon-witch-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'dragon-witch-preview.blend'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
converted={};missing=[];audit=[]
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws','label','root']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'<preview helpers>','exec'))
bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
original_png=png
def png(path):return original_png(path.replace('longv_weapon_', 'hongye_weapon_'))
rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Dragon Witch | humanoid01e native reference'
rig.animation_data_clear()
for bone in rig.pose.bones:bone.matrix_basis.identity()
meshes=import_ws('variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_storm_human_wv/torso_01.wsmodel',rig)
rig.hide_set(True)
weapon=import_ws('variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_celestial_guard_halberd_2h_04.wsmodel')
points=[ob.matrix_world@Vector(v) for ob in weapon for v in ob.bound_box]
center=(Vector([min(p[k] for p in points) for k in range(3)])+Vector([max(p[k] for p in points) for k in range(3)]))/2
root('Halberd | separate source prop',weapon).location=Vector((1.5,0,1.1))-center
assert not missing,missing
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
target=Vector((.35,0,1.05));direction=Vector((.25,-8,1.3));orientation=(-direction).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=target;sp.region_3d.view_distance=4.7
   sp.region_3d.view_rotation=orientation;sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),parts=audit,missing_textures=missing,game_modified=False),indent=2))
print('DRAGON_WITCH_READY',flush=True)

