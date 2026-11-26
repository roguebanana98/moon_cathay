"""Private Da Anh appearance with Moonshadow sword/handbow retarget trial."""
import bpy,addon_utils,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-moonshadow-animation-trial';D=R/'reference/local/khainite-weapons'
SOURCE=R/'assets/working/da-anh/da-anh-legendary-hero.blend';OUT=O/'da-anh-moonshadow-dagger-handbow-trial.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.render.fps=30
rig=bpy.data.objects['Da Anh | Native humanoid01e'];body=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get() and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
oldleft=bpy.data.objects['Death Squad knife | hand_left'];oldleft.hide_set(True);oldleft.hide_render=True
knife=bpy.data.objects['Death Squad knife | hand_right']
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/humanoid01d.anim'))
donor=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');donor.name='REFERENCE Moonshadow Assassin native humanoid01d'
rig.animation_data_clear();rig.data.pose_position='POSE'
for b in rig.pose.bones:b.matrix_basis.identity();b.rotation_mode='QUATERNION'
clips=json.loads((O/'clips.json').read_text())
bpy.context.view_layer.objects.active=donor;donor.select_set(True)
import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01d/hands/hu1d_hand_pose_grip.anim'),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
scene.frame_set(0);bpy.context.view_layer.update()
grip_relative={b.name:donor.pose.bones['hand_left' if '_left_' in b.name else 'hand_right'].matrix.inverted()@b.matrix for b in donor.pose.bones if b.name.startswith(('finger_','thumb_'))}
target_rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
source_rest={b.name:b.matrix_local.copy() for b in donor.data.bones}
local_rest={b.name:(target_rest[b.parent.name].inverted()@target_rest[b.name] if b.parent else target_rest[b.name]) for b in rig.data.bones}
mapping={name:name for name in target_rest if name in source_rest}
aliases={'head_0':'head','eyebrows_0':'eyebrow_0','jaw_0':'jaw',
    'eyelid_left_0':'eyelid_upper_left_0','eyelid_right_0':'eyelid_upper_right_0',
    'shoulderpad_left_0':'shoulder_pad_left','shoulderpad_right_0':'shoulder_pad_right',
    'skirt_front_center_0':'cingulum_front_0','skirt_front_center_1':'cingulum_front_1',
    'skirt_back_left_0':'skirt_back_0','skirt_back_left_1':'skirt_back_1',
    'skirt_back_right_0':'skirt_back_0','skirt_back_right_1':'skirt_back_1'}
mapping.update({k:v for k,v in aliases.items() if k in target_rest and v in source_rest and not k.startswith('skirt_')})
matched=set(mapping)
ordered=[]
def addbone(b):
    ordered.append(b)
    for child in b.children:addbone(child)
for b in rig.data.bones:
    if b.parent is None:addbone(b)
height=lambda bones:max(m.translation.z for m in bones.values())-min(m.translation.z for m in bones.values())
height_scale=height(target_rest)/height(source_rest)
actions=[];demo={name:dict(location=[],rotation=[]) for name in target_rest};demo_frames=[];segments=[];cursor=1

def make_action(name,frames,data):
    action,fcurves=import_anim._new_action_fcurves(rig,name);action.use_fake_user=True
    for bone in ordered:
        pb=rig.pose.bones[bone.name]
        import_anim._fill_fcurves(fcurves,pb.path_from_id('location'),3,data[bone.name]['location'],frames,bone.name)
        import_anim._fill_fcurves(fcurves,pb.path_from_id('rotation_quaternion'),4,data[bone.name]['rotation'],frames,bone.name)
    return action

for clip in clips:
    bpy.ops.object.select_all(action='DESELECT');donor.hide_set(False);donor.select_set(True);bpy.context.view_layer.objects.active=donor
    # Force an exact donor target; the public operator deliberately auto-selects
    # by current collection and can choose the wrong rig in a multi-model scene.
    imported,stats,warnings=import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
    assert imported==donor
    native=donor.animation_data.action;native.name='SOURCE '+clip['label'];native.use_fake_user=True
    first,last=map(int,native.frame_range);frames=list(range(first,last+1))
    data={name:dict(location=[],rotation=[]) for name in target_rest};previous={}
    rig.animation_data_clear()
    for frame in frames:
        scene.frame_set(frame);bpy.context.view_layer.update();world={}
        for bone in ordered:
            name=bone.name;rest=target_rest[name];relative=local_rest[name]
            parent_pose=world[bone.parent.name] if bone.parent else Matrix.Identity(4)
            pos=(parent_pose@relative).translation
            if name in matched:
                source_name=mapping[name];source=donor.pose.bones[source_name].matrix
                if source_name in grip_relative:
                    source=donor.pose.bones['hand_left' if '_left_' in source_name else 'hand_right'].matrix@grip_relative[source_name]
                rotation=source.to_quaternion()@source_rest[source_name].to_quaternion().inverted()@rest.to_quaternion()
                # Keep root motion in place for inspection; retain vertical bounce.
                if bone.parent is None:
                    delta=source.translation-source_rest[source_name].translation
                    pos.z+=delta.z*height_scale
                desired=Matrix.LocRotScale(pos,rotation,None)
                basis=relative.inverted()@parent_pose.inverted()@desired
            else:
                # Extra Cathay cloth/face bones follow their own native hierarchy.
                basis=Matrix.Identity(4)
            loc=basis.translation;rot=basis.to_quaternion();rot.normalize()
            if name in previous and rot.dot(previous[name])<0:rot.negate()
            previous[name]=rot.copy()
            world[name]=parent_pose@relative@Matrix.LocRotScale(loc,rot,None)
            data[name]['location'].append(tuple(loc));data[name]['rotation'].append(tuple(rot))
    action=make_action('MW '+clip['label'],frames,data)
    action['source_clip']=clip['path'];action['retarget']='rest-corrected global rotations, target bind lengths, in-place root'
    action['preview_frame_end']=last
    actions.append(dict(action=action.name,label=clip['label'],frames=[first,last],source=clip['path']))
    # Repeat locomotion for a useful visual loop; separate other clips by markers.
    repeats=3 if clip['label'].startswith(('02','03')) else 1
    start=cursor
    for repeat in range(repeats):
        for index,f in enumerate(frames):
            demo_frames.append(cursor);cursor+=1
            for name in target_rest:
                demo[name]['location'].append(data[name]['location'][index])
                q=Quaternion(data[name]['rotation'][index])
                if demo[name]['rotation'][-1:] and q.dot(Quaternion(demo[name]['rotation'][-1]))<0:q.negate()
                demo[name]['rotation'].append(tuple(q))
    segments.append(dict(label=clip['label'],start=start,end=cursor-1))
    print('BAKED',clip['label'],len(frames),'frames',flush=True)

master=make_action('MW 00 REVIEW ALL - stand walk run attack aim fire',demo_frames,demo)
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for segment in segments:scene.timeline_markers.new(segment['label'],frame=segment['start'])
scene.frame_start=1;scene.frame_end=cursor-1
donor.hide_set(True);donor.hide_render=True



# Resolve the exact exported Moonshadow handbow against its real native standing
# prop frame, compensating the different hand rest axes and palm positions.
rig.animation_data.action=master;rig.animation_data.action_slot=master.slots[0]
donor.animation_data.action=bpy.data.actions['SOURCE 01 Stand'];donor.animation_data.action_slot=donor.animation_data.action.slots[0]
scene.frame_set(1);bpy.context.view_layer.update()
def palm(r,side):
 inv=r.pose.bones['hand_'+side].matrix.inverted()
 return sum((inv@r.pose.bones['finger_'+f+'_'+side+'_'+str(n)].head for f in ['index','ring'] for n in [0,2]),Vector())/4
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
before=set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(R/'build/moonshadow-v7-appearance/variantmeshes/wh_variantmodels/mc_moonshadow_assassin/handbow.rigid_model_v2'),build_materials=True,texture_root=str(R/'build/moonshadow-v7-appearance'),import_all_lods=False)
bows=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(bows)==1
hand='hand_left';native_rel=donor.pose.bones[hand].matrix.inverted()@donor.pose.bones['be_prop_5'].matrix
corr=rig.data.bones[hand].matrix_local.to_quaternion().inverted()@donor.data.bones[hand].matrix_local.to_quaternion()
source_grip=palm(donor,'left');target_grip=palm(rig,'left')
correction=corr.to_matrix().to_4x4();correction.translation=target_grip-corr@source_grip
anchor=bpy.data.objects.new('Moonshadow handbow | left hand attachment',None);scene.collection.objects.link(anchor)
c=anchor.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget=hand
for ob in bows:
 local=correction@native_rel@ob.matrix_world
 ob.parent=anchor;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local;ob.name='Moonshadow Assassin handbow | Da Anh';ob.hide_set(False);ob.hide_render=False
# Refit the existing identical Death Squad knife to the retargeted finger pose.
grip=palm(rig,'right');grip.y-=.003
local=knife.matrix_basis.copy();handle=Vector(knife['handle_midpoint']);local.translation=grip-local.to_3x3()@handle;knife.matrix_basis=local;knife['palm_target']=list(grip)
checks=[]
for seg in segments:
 motions=[]
 for f in sorted({seg['start'],(seg['start']+seg['end'])//2,seg['end']}):
  scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
  for ob in body:
   ev=ob.evaluated_get(dg);mesh=ev.to_mesh();p=np.array([tuple(ev.matrix_world@v.co) for v in mesh.vertices]);assert np.isfinite(p).all();pts.append(p);ev.to_mesh_clear()
  motions.append(np.concatenate(pts))
  expected=rig.matrix_world@rig.pose.bones[hand].matrix;actual=anchor.evaluated_get(dg).matrix_world
  assert max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-4
  error=(knife.evaluated_get(dg).matrix_world@handle-rig.matrix_world@rig.pose.bones['hand_right'].matrix@grip).length;assert error<1e-4
 delta=max(float(np.linalg.norm(p-motions[0],axis=1).max()) for p in motions[1:]);assert delta>1e-5
 checks.append(dict(label=seg['label'],motion=delta))
scene.frame_set(1);rig.hide_set(True);donor.hide_set(True);donor.hide_render=True
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.region_3d.view_location=(0,0,1.05);sp.region_3d.view_distance=3.2;sp.region_3d.view_rotation=Vector((-.5,8,-.4)).to_track_quat('-Z','Y')
notes=bpy.data.texts.new('DA ANH MOONSHADOW ANIMATION TRIAL');notes.write('PREVIEW ONLY. Approved Da Anh body/head/clothing preserved on humanoid01e. Eight Moonshadow Assassin native 01d sword-handbow clips retargeted with rest-axis correction. Same Death Squad right knife, left knife hidden and exact exported Moonshadow handbow added. Finger grip overlay, palm and rest-axis compensation applied. Native unmatched cloth/hair bones retain local bind. Clipping and hand alignment need visual review. No mod update; deployed v10 sword/shield setup remains unchanged.\n'+json.dumps(segments,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'trial-report.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),source_bones=len(source_rest),target_bones=len(target_rest),matched_bones=len(mapping),timeline=segments,checks=checks,sampled_poses=len(checks)*3,game_modified=False,runtime_verified=False),indent=2));print('DA_ANH_MOONSHADOW_TRIAL_READY',flush=True)
