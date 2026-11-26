"""Bake a rest-corrected humanoid01d -> humanoid01e preview, never a game pack."""
import bpy,addon_utils,sys,json,hashlib,struct,math
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/moonshadow-animation-preview';D=R/'reference/local/khainite-weapons'
SOURCE=R/'assets/working/moonshadow-assassin/alchemist-11-working.blend'
OUT=O/'alchemist-11-animation-review-v2.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
root=bpy.data.objects['VARIANT 11'];rig=next(o for o in root.children_recursive if o.type=='ARMATURE')
body=[o for o in root.children_recursive if o.type=='MESH']
donor=bpy.data.objects['REFERENCE Khainite prop attachment frames']
def meshhash(ob):
    return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in ob.data.vertices)).hexdigest()
def bindhash():
    return hashlib.sha256(json.dumps([(b.name,b.parent.name if b.parent else None,[list(row) for row in b.matrix_local]) for b in rig.data.bones]).encode()).hexdigest()
before={o.name:meshhash(o) for o in body};bind_before=bindhash()
hidden={o.name:o.hide_get() for o in bpy.data.objects}
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
clips=json.loads((O/'clips.json').read_text())
scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
rig.animation_data_clear();rig.data.pose_position='POSE'
for pb in rig.pose.bones:pb.matrix_basis.identity();pb.rotation_mode='QUATERNION'
target_rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
source_rest={b.name:b.matrix_local.copy() for b in donor.data.bones}
local_rest={b.name:(target_rest[b.parent.name].inverted()@target_rest[b.name] if b.parent else target_rest[b.name]) for b in rig.data.bones}
mapping={name:name for name in target_rest if name in source_rest}
aliases={'head_0':'head','eyebrows_0':'eyebrow_0',
    'eyelid_left_0':'eyelid_upper_left_0','eyelid_right_0':'eyelid_upper_right_0',
    'shoulderpad_left_0':'shoulder_pad_left','shoulderpad_right_0':'shoulder_pad_right',
    'skirt_front_center_0':'cingulum_front_0','skirt_front_center_1':'cingulum_front_1',
    'skirt_back_left_0':'skirt_back_0','skirt_back_left_1':'skirt_back_1',
    'skirt_back_right_0':'skirt_back_0','skirt_back_right_1':'skirt_back_1'}
mapping.update({k:v for k,v in aliases.items() if k in target_rest and v in source_rest})
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

# Verify evaluated mesh displacement, valid bone transforms and prop attachment
# across meaningful frame changes. This cannot establish engine animation lookup.
checks=[]
visible=[o for o in body if not o.hide_get()];assert visible
probe=max(visible,key=lambda o:len(o.data.vertices))
for segment in segments:
    sample=sorted({segment['start'],(segment['start']+segment['end'])//2,segment['end']})
    samples=[]
    for frame in sample:
        scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        ev=probe.evaluated_get(dg);mesh=ev.to_mesh()
        points=np.array([tuple(ev.matrix_world@v.co) for v in mesh.vertices]);ev.to_mesh_clear()
        assert np.isfinite(points).all();samples.append(points)
        for name in ['Khainite dagger 01 | hand_right','Khainite handbow | hand_left']:
            anchor=bpy.data.objects[name];con=next(c for c in anchor.constraints if c.type=='COPY_TRANSFORMS')
            expected=rig.matrix_world@rig.pose.bones[con.subtarget].matrix
            actual=anchor.evaluated_get(dg).matrix_world
            assert max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))<1e-4
    motion=max(float(np.linalg.norm(p-samples[0],axis=1).max()) for p in samples[1:])
    assert motion>.00001,(segment['label'],motion)
    checks.append(dict(label=segment['label'],sampled_frames=sample,max_vertex_motion=motion))
assert before=={o.name:meshhash(o) for o in body};assert bind_before==bindhash()
assert all(o.hide_get()==hidden[o.name] for o in body)
rig.animation_data.action=master;rig.animation_data.action_slot=master.slots[0]
scene.frame_set(segments[2]['start']);bpy.context.view_layer.update()
rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
rig.show_in_front=False
target=Vector((0,0,1.1))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=3.9
            sp.region_3d.view_rotation=Vector((.4,-5,.5)).to_track_quat('Z','Y')
            # Use the existing frontal fitting camera's orientation.
            sp.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
            sp.region_3d.view_perspective='ORTHO'
notes=bpy.data.texts.new('ANIMATION REVIEW - READ ME');notes.write('PREVIEW ONLY. Original editable source remains unchanged. Retargeted Khainite 01d clips onto native 01e bind/weights. Root motion suppressed for viewing. Extra unmatched Cathay cloth bones follow native parent hierarchy; no cloth simulation. Long coat/shoulder clipping and hand/prop alignment need visual review. Timeline markers identify eight motions. Space plays the whole sequence; select MW actions in Action Editor for individual loops. No engine integration/runtime claims.\n'+json.dumps(segments,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report=dict(scene=str(OUT),source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    matched_bones=len(matched),target_bones=len(target_rest),source_bones=len(source_rest),
    target_only_bones=sorted(set(target_rest)-matched),donor_only_bones=sorted(set(source_rest)-set(mapping.values())),bone_aliases=aliases,
    actions=actions,timeline=segments,total_frames=scene.frame_end,checks=checks,
    body_geometry_unchanged=True,target_bind_unchanged=True,mesh_visibility_preserved=True,
    root_motion='in-place preview',extra_cloth='unmatched native hierarchy, no simulation',game_modified=False,runtime_verified=False)
(O/'animation-preview.json').write_text(json.dumps(report,indent=2))
print('ANIMATION_REVIEW_READY',str(OUT),flush=True)
