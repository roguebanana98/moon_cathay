"""Native 01e animation review, no retarget and no game changes."""
import bpy,addon_utils,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-animation';D=R/'reference/local/celestial-concubines'
SOURCE=R/'build/celestial-concubines-preview/celestial-concubines-model-comparison.blend';OUT=O/'celestial-concubines-animation-review.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
scene=bpy.context.scene;scene.render.fps=30
rigs=[bpy.data.objects['Body_%02d_native_humanoid01e'%i] for i in range(1,4)]
for ob in bpy.data.objects:ob.hide_set(True);ob.hide_render=True
roots=[r.parent for r in rigs]
for root in roots:
 for ob in [root]+list(root.children_recursive):ob.hide_set(False);ob.hide_render=False
propmeshes=[]
for rig in rigs:
 for name,bone in [('SWORD','weapon_2'),('SHIELD','weapon_3')]:
  for src in bpy.data.objects[name].children_recursive:
   if src.type!='MESH':continue
   ob=src.copy();ob.data=src.data;scene.collection.objects.link(ob);ob.parent=None;ob.matrix_world=Matrix.Identity(4)
   for con in list(ob.constraints):ob.constraints.remove(con)
   con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=bone
   ob.hide_set(False);ob.hide_render=False;ob.name=rig.name+' '+name;propmeshes.append(ob)
rig=rigs[0];rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01e/sword_and_bow/hands/hu1e_hand_pose_grip.anim'),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
scene.frame_set(0);bpy.context.view_layer.update()
grp={b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in rig.pose.bones if b.name.startswith(('finger_','thumb_'))}
frames=[];poses={b.name:dict(loc=[],rot=[],scale=[]) for b in rig.pose.bones};cursor=1;segments=[];checks=[]
for clip in json.loads((O/'clips.json').read_text()):
 import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
 action=rig.animation_data.action;action.name='CC SOURCE '+clip['label'];action.use_fake_user=True
 first,last=map(int,action.frame_range);start=cursor
 for repeat in range(3 if clip['label'].startswith(('02','03')) else 1):
  for f in range(first,last+1):
   scene.frame_set(f);bpy.context.view_layer.update();frames.append(cursor);cursor+=1
   for b in rig.pose.bones:
    loc,rot,scale=grp.get(b.name,(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()))
    # Keep locomotion centered in each comparison column.
    if b.name=='animroot':loc=loc.copy();loc.x=0;loc.y=0
    if poses[b.name]['rot'] and rot.dot(__import__('mathutils').Quaternion(poses[b.name]['rot'][-1]))<0:rot=-rot
    poses[b.name]['loc'].append(tuple(loc));poses[b.name]['rot'].append(tuple(rot));poses[b.name]['scale'].append(tuple(scale))
 segments.append(dict(label=clip['label'],start=start,end=cursor-1))
 print('IMPORTED',clip['label'],flush=True)
master,fc=import_anim._new_action_fcurves(rig,'CC 00 Native sword shield review');master.use_fake_user=True
for b in rig.pose.bones:
 for prop,key,count in [('location','loc',3),('rotation_quaternion','rot',4),('scale','scale',3)]:import_anim._fill_fcurves(fc,b.path_from_id(prop),count,poses[b.name][key],frames,b.name)
for r in rigs:r.animation_data_create();r.animation_data.action=master;r.animation_data.action_slot=master.slots[0];r.hide_set(True)
for m in list(scene.timeline_markers):scene.timeline_markers.remove(m)
for seg in segments:scene.timeline_markers.new(seg['label'],frame=seg['start'])
scene.frame_start=1;scene.frame_end=cursor-1
for seg in segments:
 for frame in sorted({seg['start'],(seg['start']+seg['end'])//2,seg['end']}):
  scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for root in roots:
   for ob in root.children_recursive:
    if ob.type!='MESH':continue
    ev=ob.evaluated_get(dg);mesh=ev.to_mesh();p=np.array([tuple(v.co) for v in mesh.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all()
  for ob in propmeshes:
   con=ob.constraints[0];expected=con.target.matrix_world@con.target.pose.bones[con.subtarget].matrix
   assert max(abs(ob.evaluated_get(dg).matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-4
  checks.append(frame)
scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=(0,0,1);sp.region_3d.view_distance=7;sp.region_3d.view_rotation=Vector((-.2,8,-.5)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'animation-review.json').write_text(json.dumps(dict(scene=str(OUT),animation_set='hu1e_sword_and_shield',retargeted=False,models=3,timeline=segments,sampled_frames=checks,game_modified=False),indent=2))
print('CONCUBINES_ANIMATION_READY',flush=True)
