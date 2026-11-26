"""Private Xiao source inspection, original LOD0 geometry and textures."""
import bpy,addon_utils,sys,json,subprocess,ast,re,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/deer-miao';O=R/'build/deer-miao-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'deer-miao-preview.blend'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
converted={};missing=[];audit=[]
def material_tree(path):
    tree=ET.Element('material')
    for slot,source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',Path(path).read_text()):
        tx=ET.SubElement(tree,'texture');ET.SubElement(tx,'slot').text=slot;ET.SubElement(tx,'source').text=source
    return tree
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text().replace('ET.parse(D/matpath)', 'material_tree(D/matpath)'))
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws','label','root']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'<preview helpers>','exec'))
bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='DEER24 Miao Ying | native humanoid01e';rig.animation_data_clear()
for bone in rig.pose.bones:bone.matrix_basis.identity()
base='variantmeshes/wh_variantmodels/hu1e/cth/cth_storm_miaoying/'
meshes=import_ws(base+'cth_storm_miaoying_reskin.wsmodel',rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
old=set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(D/(base+'cth_storm_miaoying_xiong_reskin.rigid_model_v2')),build_materials=False,import_all_lods=False,attach_armature=True)
from io_scene_rmv2 import rmv2_format as rf
props=[o for o in bpy.data.objects if o not in old and o.type=='MESH']
col=next(c for o in props for c in o.users_collection if 'lod0' in c.name)
for obj,part in zip([o for o in col.objects if o.type=='MESH'],rf.load((D/(base+'cth_storm_miaoying_xiong_reskin.rigid_model_v2')).read_bytes()).lods[0].models):
 pairs=[(typ,png(path)) for typ,path in part.material.textures if typ in [27,1,29]]
 mat=materials.build_material(part.material.model_name,[(t,p) for t,p in pairs if p],'TRANSPARENT',str(O))
 obj.data.materials.clear();obj.data.materials.append(mat)
rig.hide_set(True)
assert not missing,missing
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
target=Vector((0,0,1.05));orientation=Vector((-.25,8,-1.1)).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=target;sp.region_3d.view_distance=3.5;sp.region_3d.view_rotation=orientation;sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),parts=audit,missing_textures=missing,game_modified=False),indent=2))
print('DEER_MIAO_PREVIEW_READY',flush=True)

