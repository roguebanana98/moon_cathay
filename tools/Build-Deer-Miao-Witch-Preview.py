import bpy,addon_utils,sys,json,hashlib,struct,math,ast,subprocess
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/deer-miao-witch-preview';D=R/'reference/local/witch-elves'
SOURCE=R/'build/deer-miao-preview/deer-miao-preview.blend';OUT=O/'deer-miao-witch-elves-dual-knives.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');body=[o for o in bpy.data.objects if o.type=='MESH']
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim,materials,rmv2_format as rf
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/humanoid01b.anim'))
donor=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');donor.name='REFERENCE Witch Elves native humanoid01b'
clips=json.loads((O/'clips.json').read_text());scene=bpy.context.scene;scene.render.fps=30
rig.animation_data_clear();rig.data.pose_position='POSE'
for pb in rig.pose.bones:pb.matrix_basis.identity();pb.rotation_mode='QUATERNION'
bpy.context.view_layer.objects.active=donor;donor.select_set(True)
import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01b/hands/hu1b_hand_pose_grip.anim'),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
scene.frame_set(0);bpy.context.view_layer.update()
grip_relative={b.name:donor.pose.bones['hand_left' if '_left_' in b.name else 'hand_right'].matrix.inverted()@b.matrix for b in donor.pose.bones if b.name.startswith(('finger_','thumb_'))}
target_rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
source_rest={b.name:b.matrix_local.copy() for b in donor.data.bones}
local_rest={b.name:(target_rest[b.parent.name].inverted()@target_rest[b.name] if b.parent else target_rest[b.name]) for b in rig.data.bones}
mapping={name:name for name in target_rest if name in source_rest}
aliases={'head_0':'head','eyebrows_0':'eyebrow','jaw_0':'jaw',
    'eyelid_left_0':'eyelid_upper_left','eyelid_right_0':'eyelid_upper_right',
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


# Import the real two Death Squad knife meshes with original materials.
D=R/'reference/local/cathay-ror';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
converted={};missing=[];audit=[]
tree=ast.parse((R/'tools/Preview-Cathay-RoR-Ninjas.py').read_text())
basehelpers=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
exec(compile(ast.Module(body=[n for n in basehelpers.body if isinstance(n,ast.FunctionDef) and n.name=='png'],type_ignores=[]),'<texture helper>','exec'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='import_part'],type_ignores=[]),'<knife importer>','exec'))
donor.animation_data.action=bpy.data.actions['SOURCE 01 Stand'];donor.animation_data.action_slot=donor.animation_data.action.slots[0]
scene.frame_set(0);bpy.context.view_layer.update();weapons=[]
for name,hand,prop,handle,grip in [
 ('ninja_knife_1','hand_right','be_prop_1',Vector((.3226,0,0)),Vector((-.033,.115,-.005))),
 ('ninja_knife_2','hand_left','be_prop_5',Vector((.3226,-.023,0)),Vector((.033,.115,-.005)))]:
 parts=import_part(name)
 relative=donor.pose.bones[hand].matrix.inverted()@donor.pose.bones[prop].matrix
 anchor=bpy.data.objects.new('Death Squad | '+hand,None);scene.collection.objects.link(anchor)
 con=anchor.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=hand
 for ob in parts:
  local=relative@ob.matrix_world
  local.translation=grip-local.to_3x3()@handle
  ob.parent=anchor;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local
  ob.name='Death Squad knife | '+hand;ob['handle_midpoint']=list(handle);ob['palm_target']=list(grip)
  weapons.append(ob)
assert not missing,missing
rig.animation_data.action=master;rig.animation_data.action_slot=master.slots[0]
checks=[]
for segment in segments:
 sample=sorted({segment['start'],(segment['start']+segment['end'])//2,segment['end']});points=[]
 for frame in sample:
  scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for ob in body:
   ev=ob.evaluated_get(dg);mesh=ev.to_mesh();coords=np.array([tuple(ev.matrix_world@v.co) for v in mesh.vertices]);ev.to_mesh_clear();assert np.isfinite(coords).all()
  points.append(rig.pose.bones['hand_right'].matrix.translation.copy())
  for ob in weapons:
   hand='hand_right' if 'hand_right' in ob.name else 'hand_left'
   error=(ob.evaluated_get(dg).matrix_world@Vector(ob['handle_midpoint'])-rig.matrix_world@rig.pose.bones[hand].matrix@Vector(ob['palm_target'])).length
   assert error<1e-4,error
 checks.append(dict(label=segment['label'],frames=sample,hand_motion=max((p-points[0]).length for p in points)))
scene.frame_set(1);rig.hide_set(True);donor.hide_set(True);donor.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=(0,0,1);sp.region_3d.view_distance=3.5;sp.region_3d.view_rotation=Vector((-.3,8,-.6)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'
notes=bpy.data.texts.new('WITCH ELVES ANIMATION REVIEW');notes.write('Witch Elves native hu1b_elf_dual_sword retargeted to Cathay 01e. Timeline markers: stand, walk, run, attack1, attack3, jump. Space plays sequence. Original DEER24 appearance and mesh weights retained. Two original Death Squad knives, handle midpoint constrained to palm. Blender preview only; no mod update. Cloth/finger refinement may remain.\n'+json.dumps(segments,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'review-report.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),native_animation_set='hu1b_elf_dual_sword',matched_bones=len(matched),target_bones=len(target_rest),source_bones=len(source_rest),timeline=segments,checks=checks,game_modified=False),indent=2))
print('WITCH_REVIEW_READY',flush=True)
