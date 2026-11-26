import bpy,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-moonshadow-animation-trial';D=R/'reference/local/khainite-weapons'
bpy.ops.wm.open_mainfile(filepath=str(O/'da-anh-moonshadow-dagger-handbow-trial.blend'));scene=bpy.context.scene;rig=bpy.data.objects['Da Anh | Native humanoid01e'];donor=bpy.data.objects['REFERENCE Moonshadow Assassin native humanoid01d'];old=bpy.data.objects['Moonshadow Assassin handbow | Da Anh'];old.hide_set(True);old.hide_render=True
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'));import addon_utils;addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
bpy.ops.object.select_all(action='DESELECT');donor.hide_set(False);donor.select_set(True);bpy.context.view_layer.objects.active=donor
original_action=donor.animation_data.action
import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01d/hands/hu1d_hand_pose_grip.anim'),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});scene.frame_set(0)
grips={b.name:b.matrix_basis.copy() for b in donor.pose.bones if b.name.startswith(('finger_','thumb_'))}
donor.animation_data.action=original_action;donor.animation_data.action_slot=original_action.slots[0];scene.frame_set(1)
for n,m in grips.items():donor.pose.bones[n].matrix_basis=m
bpy.context.view_layer.update()
def palm(r):
 inv=r.pose.bones['hand_left'].matrix.inverted()
 return sum((inv@r.pose.bones['finger_'+f+'_left_'+str(n)].head for f in ['index','ring'] for n in [0,2]),Vector())/4
sourcep=palm(donor);targetp=palm(rig);hand='hand_left';relative=donor.pose.bones[hand].matrix.inverted()@donor.pose.bones['be_prop_5'].matrix
correction=(rig.data.bones[hand].matrix_local.to_quaternion().inverted()@donor.data.bones[hand].matrix_local.to_quaternion()).to_matrix().to_4x4();correction.translation=targetp-correction.to_3x3()@sourcep
ws=D/'variantmeshes/wh_variantmodels/hu1d/def/def_props/def_assassin_bow_1h_01_rigid.wsmodel';geometry=ET.parse(ws).findtext('geometry').replace('\\','/').lower()
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None;before=set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(D/geometry),build_materials=True,texture_root=str(D),import_all_lods=False)
meshes=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(meshes)==1
ob=meshes[0];ob.data.materials.clear();ob.data.materials.append(old.data.materials[0]);ob.name='Da Anh handbow | corrected native grip';local=correction@relative@ob.matrix_world;handle=ob.matrix_world.inverted()@relative.inverted()@sourcep
ob.parent=old.parent;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local
ob['handle_midpoint']=list(handle);ob['palm_target']=list(targetp);ob['source']='Original native Khainite handbow, replacing incorrectly offset exported donor geometry'
donor.hide_set(True);donor.hide_render=True;checks=[]
for f in (1,75,170,220,270,320,350,370,394,420,442):
 scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();actual=ob.evaluated_get(dg).matrix_world@handle;expected=rig.matrix_world@rig.pose.bones[hand].matrix@targetp;err=(actual-expected).length;assert err<1e-4;checks.append(dict(frame=f,error=err))
scene.frame_set(370);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,-.1,1.25);sp.region_3d.view_distance=2.2
scene.frame_start=1;scene.frame_end=442
bpy.ops.file.pack_all();OUT=O/'da-anh-moonshadow-handbow-native-grip-fixed.blend';bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'handbow-native-grip-fix.json').write_text(json.dumps(dict(scene=str(OUT),native_model=geometry,handle=list(handle),palm=list(targetp),matrix=[list(r) for r in local],checks=checks,game_modified=False),indent=2))
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.film_transparent=False;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for l in [o for o in bpy.data.objects if o.type=='LIGHT']:l.hide_render=False
world=rig.matrix_world@rig.pose.bones[hand].matrix;camd=bpy.data.cameras.new('Grip inspect');cam=bpy.data.objects.new('Grip inspect',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.ortho_scale=.65
for label,offset in [('front',Vector((0,-2,.2))),('side',Vector((2,0,.2)))]:
 target=world.translation;cam.location=target+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/('bow-native-grip-after-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('NATIVE_BOW_GRIP_READY',flush=True)


