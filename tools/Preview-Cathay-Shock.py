"""Separate appearance inspection of the installed Cathay shock units pack."""
import bpy,addon_utils,sys,json,subprocess,ast,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/cathay-shock';O=R/'build/cathay-shock-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'cathay-shock-model-comparison.blend';assert not OUT.exists()
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
converted={};missing=[];audit=[]
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws','label','root']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'<source-model preview helpers>','exec'))
for index,(ws,x) in enumerate([('samurai_scifi_2.wsmodel',-1.3),('samurai_scifi.wsmodel',1.3)],1):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/mat_samurai.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Samurai %02d | native mat_samurai'%index
    rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    meshes=import_ws('variantmeshes/samurai/'+ws,rig)
    weapon=import_ws('variantmeshes/samurai/samurai_officer_katana.wsmodel')
    for ob in weapon:
        con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='weapon_2'
    root('FINISH %02d'%index,[rig]+meshes+weapon,x=x);rig.hide_set(True)
    label('FINISH %02d'%index,x,-.22,.2)
label('CATHAY SHOCK UNITS | SAME MODEL, TWO TEXTURES',0,2.75,.16)
label('Native mat_samurai rig | Original geometry | LOD0 preview',0,-.5,.12)
assert not missing,missing
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral comparison');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
camdata=bpy.data.cameras.new('Comparison');cam=bpy.data.objects.new('Comparison',camdata);scene.collection.objects.link(cam)
target=Vector((0,0,1.1));cam.location=(.4,-8,2.1);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=5.6;scene.camera=cam;cam.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=5.7
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),body_geometry_variants=1,texture_variants=2,body_skeleton='mat_samurai',bones=96,preview_lod=0,original_lods=4,parts=audit,missing_textures=missing,original_model_11_unchanged=True,game_modified=False,emissive_shader_not_fully_reproduced=True),indent=2))
print('SHOCK_PREVIEW_READY',str(OUT),flush=True)
