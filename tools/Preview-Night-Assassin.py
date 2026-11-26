"""Private Night Assassin source inspection, original LOD0 geometry and textures."""
import bpy,addon_utils,sys,json,subprocess,ast,re,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/night-assassin';O=R/'build/night-assassin-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'night-assassin-preview.blend'
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
for i,x in enumerate([-2.4,-.8,.8,2.4],1):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/khainite-weapons/animations/skeletons/humanoid01d.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Night Assassin %02d | native humanoid01d'%i
    rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    base='variantmeshes/wh_variantmodels/hu1d/def/def_khanite_assassin/'
    meshes=[]
    for kind,n in [('head',i),('torso',i),('legs',1+(i-1)%2)]:
        meshes+=import_ws(base+'def_khanite_assassin_'+kind+'_%02d.wsmodel'%n,rig)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/khainite-weapons/animations/battle/humanoid01d/sword_and_handbow/stand/hu1d_def_swha_stand_01.anim'))
    props=[];base='variantmeshes/wh_variantmodels/hu1d/def/def_props/'
    for ws,bone in [('def_khanite_assassin_dagger_01.wsmodel','be_prop_1'),('def_assassin_bow_1h_01_rigid.wsmodel','be_prop_5')]:
        part=import_ws(base+ws)
        for ob in part:
            con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=bone
        props+=part
    root('VARIANT %02d'%i,[rig]+meshes+props,x=x);rig.hide_set(True)
    label('VARIANT %02d'%i,x,-.2,.15)
bpy.context.scene.frame_set(0)
assert not missing,missing
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
target=Vector((0,0,1.0));orientation=Vector((-.25,8,-1.1)).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=target;sp.region_3d.view_distance=9.0;sp.region_3d.view_rotation=orientation;sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),parts=audit,missing_textures=missing,game_modified=False),indent=2))
print('NIGHT_ASSASSIN_PREVIEW_READY',flush=True)

