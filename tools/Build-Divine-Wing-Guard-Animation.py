"""Separate Blender review: retarget real flight clips, native sword combat.

Does not export animation or alter source meshes/weights/game files. A native
16c donor drives the Cathay body through rest-pose-corrected rotation retargeting;
wing/feather channels remain native on their own original rig.
"""
import bpy
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/divine-wing-guard-animation';D=R/'reference/local/divine-wing-guard'
SOURCE=R/'build/divine-wing-guard-preview/divine-wing-guard-preview-packed.blend'
OUT=O/'divine-wing-guard-animation-review-v2.blend'
assert not OUT.exists() or '--rebuild-review' in sys.argv,'Preserve existing review'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert not bpy.data.filepath,'Use a fresh background process'
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon'
spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)])
addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_anim
sys.path.insert(0,str(R/'tools'))
from HuyenVeAnimationPreview import complete_preview_channels
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;plan=json.loads((O/'clips.json').read_text())
body=bpy.data.objects['Divine Wing Guard | Jade Warrior native rig']
wing=bpy.data.objects['Divine Wing Guard | original angel wing rig']
body_meshes=list(bpy.data.collections['01 | Jade Warriors - original armour'].objects)
wing_meshes=list(bpy.data.collections['02 | White angel wings - preview assembly'].objects)
visible=[o for o in body_meshes+wing_meshes if o.type=='MESH']
geometry_hash=lambda: hashlib.sha256(json.dumps([(o.name,[list(v.co) for v in o.data.vertices],
  [[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]) for o in visible],sort_keys=True).encode()).hexdigest()
geometry_before=geometry_hash()
scene.frame_set(1);bpy.context.view_layer.update()

# Preserve the native sword/shield grip sampled in the approved static assembly.
for ob in body_meshes:
    role='sword' if '| sword |' in ob.name else 'shield' if '| shield |' in ob.name else None
    if not role:continue
    hand='hand_right' if role=='sword' else 'hand_left'
    grip=(body.matrix_world@body.pose.bones[hand].matrix).inverted()@ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
    for con in list(ob.constraints):ob.constraints.remove(con)
    ob.parent=None;ob.matrix_basis=grip
    con=ob.constraints.new('CHILD_OF');con.name='Review: preserve original native hand grip';con.target=body;con.subtarget=hand;con.inverse_matrix=Matrix.Identity(4)
    ob['review_hand_grip']=[list(row) for row in grip]

source_col=bpy.data.collections.new('91 | Native animation donor - hidden');scene.collection.children.link(source_col)
donor=wing.copy();donor.data=wing.data.copy();donor.name='NATIVE SOURCE | humanoid16c flight';source_col.objects.link(donor)
for con in list(donor.constraints):donor.constraints.remove(con)
donor.matrix_world=Matrix.Identity(4);donor.animation_data_clear();donor.hide_set(False);donor.hide_render=True

for rig in [body,wing,donor]:
    rig.hide_set(False)
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.matrix_basis.identity()
body.animation_data_clear();wing.animation_data_clear()
trest={b.name:b.matrix_local.copy() for b in body.data.bones}
srest={b.name:b.matrix_local.copy() for b in donor.data.bones}
mapping={n:n for n in set(trest)&set(srest)}
mapping.update({'head_0':'head','jaw_0':'jaw','eyelid_left_0':'eyelid_upper_left_0','eyelid_right_0':'eyelid_upper_right_0'})
mapped=set(mapping)
assert all(n in mapped for n in ['root','spine_0','spine_1','spine_2','hand_left','hand_right'])
warnings=[];stored=[]

def select(rig):
    bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig

def load(rig,path):
    rig.animation_data_clear()
    for b in rig.pose.bones:b.matrix_basis.identity()
    select(rig)
    imported,stats,issues=import_anim.import_file(bpy.context,str(D/path),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0))
    assert imported==rig
    warnings.extend(dict(path=path,message=w) for w in issues)
    action=rig.animation_data.action;complete_preview_channels(action,rig);action.use_fake_user=True
    return action,tuple(map(int,action.frame_range))

def wing_channel(name):
    return name.startswith(('wing_','feather_','clav_','neck_'))

def snapshot(rig):
    return {p.name:dict(location=tuple(p.location),rotation=tuple(p.rotation_quaternion),scale=tuple(p.scale)) for p in rig.pose.bones}

def retarget():
    source={b.name:b.matrix.copy() for b in donor.pose.bones}
    desired={}
    for pb in body.pose.bones:
        name=pb.name;parent=pb.parent.name if pb.parent else None
        target_rest=trest[name]
        local_rest=trest[parent].inverted()@target_rest if parent else target_rest
        parent_pose=desired[parent] if parent else Matrix.Identity(4)
        if name in mapped:
            src=mapping[name]
            global_rotation=source[src].to_quaternion()@srest[src].to_quaternion().inverted()@target_rest.to_quaternion()
            source_parent=donor.data.bones[src].parent
            if source_parent:
                sn=source_parent.name
                source_local=source[sn].inverted()@source[src]
                rest_local=srest[sn].inverted()@srest[src]
                offset=source_local.translation-rest_local.translation
                offset=srest[sn].to_quaternion()@offset
                if parent:offset=trest[parent].to_quaternion().inverted()@offset
                position=parent_pose@(local_rest.translation+offset)
            else:
                position=target_rest.translation+source[src].translation-srest[src].translation
                position.x=0;position.y=0 # stationary review, retain vertical source movement
            goal=Matrix.LocRotScale(position,global_rotation,Vector((1,1,1)))
        else:
            goal=parent_pose@local_rest
        desired[name]=goal
        local_pose=parent_pose.inverted()@goal
        pb.matrix_basis=local_rest.inverted()@local_pose

_,ground_range=load(donor,plan['ground_wing_pose'])
scene.frame_set(ground_range[0]);bpy.context.view_layer.update()
ground_wing={p.name:p.matrix_basis.copy() if wing_channel(p.name) else Matrix.Identity(4) for p in donor.pose.bones}
donor.animation_data_clear()

for clip in plan['clips']:
    rig=donor if clip['rig']=='humanoid16c' else body
    action,(first,last)=load(rig,clip['path']);action.name='NATIVE | '+clip['label']
    frames=[]
    for f in range(first,last+1):
        scene.frame_set(f);bpy.context.view_layer.update()
        if rig==donor:retarget()
        else:
            for pb in body.pose.bones:
                if pb.parent is None:
                    pose=pb.matrix.copy();pose.translation.x=0;pose.translation.y=0
                    pb.matrix_basis=pb.bone.matrix_local.inverted()@pose
        for pb in wing.pose.bones:
            pb.matrix_basis=(donor.pose.bones[pb.name].matrix_basis.copy() if wing_channel(pb.name) else Matrix.Identity(4)) if rig==donor else ground_wing[pb.name]
        for arm in [body,wing]:
            assert all(math.isfinite(v) for p in arm.pose.bones for row in p.matrix_basis for v in row),(clip['label'],f)
        bpy.context.view_layer.update()
        frames.append(dict(body=snapshot(body),wing=snapshot(wing),root_z=body.pose.bones['animroot'].matrix.translation.z,
                           pelvis_z=body.pose.bones['root'].matrix.translation.z))
    stored.append(dict(**clip,first=first,last=last,frames=frames))
    rig.animation_data_clear()
    print('NATIVE_CLIP_SAMPLED',clip['label'],len(frames),flush=True)

# Bake every channel so switching phases cannot leave stale poses on either rig.
data={arm.name:{p.name:dict(location=[],rotation=[],scale=[]) for p in arm.pose.bones} for arm in [body,wing]}
segments=[];cursor=1;altitudes=[]
for clip in stored:
    n=len(clip['frames']);duration=clip.get('duration',n+15)
    segments.append({k:v for k,v in clip.items() if k not in ['frames']}|dict(start=cursor,end=cursor+duration-1,native_frames=n))
    for i in range(duration):
        index=i%n if clip['mode']=='loop' else min(i,n-1)
        sample=clip['frames'][index]
        for role,arm in [('body',body),('wing',wing)]:
            for name,target in data[arm.name].items():
                for channel in ['location','rotation','scale']:target[channel].append(sample[role][name][channel])
        native_z=sample['root_z'];flight_height=3.0
        if clip['mode']=='takeoff':
            first_z=clip['frames'][0]['pelvis_z'];last_z=clip['frames'][-1]['pelvis_z'];pz=sample['pelvis_z']
            desired_z=first_z+flight_height*(pz-first_z)/(last_z-first_z)
            altitude=desired_z-pz
        elif clip['mode']=='landing':
            first_z=clip['frames'][0]['pelvis_z'];last_z=clip['frames'][-1]['pelvis_z'];pz=sample['pelvis_z']
            ground_z=last_z-clip['frames'][-1]['root_z']
            desired_z=ground_z+flight_height*(pz-last_z)/(first_z-last_z)
            altitude=desired_z-pz
        else:
            altitude=flight_height if clip['mode']=='airattack' or clip['label'] in ['02 FLIGHT','03 HOVER'] else 0
        altitudes.append(altitude)
    cursor+=duration
frames=list(range(1,cursor))
for arm in [body,wing]:
    arm.animation_data_clear()
    action,curves=import_anim._new_action_fcurves(arm,'DIVINE WING GUARD | '+('BODY RETARGET + NATIVE SWORD' if arm==body else 'NATIVE WING AND FEATHER REVIEW'))
    action.use_fake_user=True
    for name,channels in data[arm.name].items():
        pb=arm.pose.bones[name];previous=None
        for i,raw in enumerate(channels['rotation']):
            q=Quaternion(raw)
            if previous is not None and q.dot(previous)<0:q.negate()
            channels['rotation'][i]=tuple(q);previous=q
        for channel,property_name,components in [('location','location',3),('rotation','rotation_quaternion',4),('scale','scale',3)]:
            import_anim._fill_fcurves(curves,pb.path_from_id(property_name),components,channels[channel],frames,name)
    for fc in curves:
        for point in fc.keyframe_points:point.interpolation='LINEAR'

# Explicit presentation altitude substitutes for engine-controlled flight height.
root=bpy.data.objects.new('REVIEW ONLY | normalize engine flight altitude',None);scene.collection.objects.link(root)
body.parent=root
for frame,altitude in zip(frames,altitudes):
    root.location=(0,0,altitude);root.keyframe_insert(data_path='location',frame=frame)
root['not_native_animation']='Presentation-only 3m flight altitude; source takeoff/landing root-Z normalized to common endpoints, not exported. Native root XY removed.'

for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for segment in segments:scene.timeline_markers.new(segment['label'],frame=segment['start'])
scene.frame_start=1;scene.frame_end=cursor-1;scene.render.fps=30
if 'FRAME_DROP' in {i.identifier for i in scene.bl_rna.properties['sync_mode'].enum_items}:scene.sync_mode='FRAME_DROP'

def points(objects):
    dg=bpy.context.evaluated_depsgraph_get();result=[]
    for ob in objects:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();result.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    return result

checks=[];global_min=Vector((1e9,)*3);global_max=Vector((-1e9,)*3)
for segment in segments:
    samples=sorted({segment['start']+round(t*min(segment['native_frames']-1,segment['end']-segment['start'])) for t in [0,.25,.5,.75,1]})
    wing_samples=[];body_samples=[];attachment_errors=[]
    for f in samples:
        scene.frame_set(f);bpy.context.view_layer.update();pts=points(visible)
        assert all(math.isfinite(v) for p in pts for v in p),(segment['label'],f)
        low=Vector([min(p[i] for p in pts) for i in range(3)]);high=Vector([max(p[i] for p in pts) for i in range(3)])
        assert max(high-low)<12,(segment['label'],f,tuple(high-low))
        for i in range(3):global_min[i]=min(global_min[i],low[i]);global_max[i]=max(global_max[i],high[i])
        wing_samples.append(points(wing_meshes)[-1].copy());body_samples.append(points(body_meshes)[0].copy())
        for ob in body_meshes:
            if 'review_hand_grip' not in ob:continue
            con=next(c for c in ob.constraints if c.type=='CHILD_OF')
            expected=body.matrix_world@body.pose.bones[con.subtarget].matrix@Matrix(ob['review_hand_grip'])
            actual=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
            attachment_errors.append(max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4)))
    err=max(attachment_errors,default=0);assert err<1e-4,(segment['label'],err)
    checks.append(dict(label=segment['label'],sampled_frames=samples,finite=True,max_prop_matrix_error=err,
                       wing_vertex_motion=max((p-wing_samples[0]).length for p in wing_samples),
                       body_vertex_motion=max((p-body_samples[0]).length for p in body_samples)))
assert geometry_hash()==geometry_before,'Geometry or weights changed'

# Simple reference ground to make the landing/altitude clear.
stage=bpy.data.collections.new('05 | Animation review stage');scene.collection.children.link(stage)
ground_mesh=bpy.data.meshes.new('Reference ground');ground_mesh.from_pydata([(-6,-6,-.04),(6,-6,-.04),(6,6,-.04),(-6,6,-.04)],[],[(0,1,2,3)]);ground_mesh.update()
ground=bpy.data.objects.new('Ground reference - preview only',ground_mesh);stage.objects.link(ground)
mat=bpy.data.materials.new('Review ground');mat.use_nodes=True
shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=(.075,.09,.11,1);shader.inputs['Roughness'].default_value=.9;ground.data.materials.append(mat)

cam=scene.camera;center=Vector((0,0,1.2));cam.rotation_euler=Vector((-3,10,-1.5)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=5.7
for frame in frames:
    scene.frame_set(frame);bpy.context.view_layer.update()
    z=(body.matrix_world@body.pose.bones['root'].matrix).translation.z
    cam.location=Vector((3,-10,z+1.8));cam.keyframe_insert(data_path='location',frame=frame)

caption_mat=bpy.data.materials.new('Review captions');caption_mat.use_nodes=True
nodes=caption_mat.node_tree.nodes;nodes.clear();em=nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.85,.92,1,1);output=nodes.new('ShaderNodeOutputMaterial');caption_mat.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
def caption(text,y,size):
    curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.align_x='CENTER';curve.size=size
    ob=bpy.data.objects.new(text,curve);stage.objects.link(ob);ob.parent=cam;ob.location=(0,y,-1);curve.materials.append(caption_mat);return ob
caption('DIVINE WING GUARD | BLENDER REVIEW',2.15,.13)
for segment in segments:
    ob=caption(segment['label'],-2.15,.16)
    for f,s in [(0,0),(segment['start'],1),(segment['end']+1,0)]:
        ob.scale=(s,)*3;ob.keyframe_insert(data_path='scale',frame=f)
    a=ob.animation_data.action
    for layer in a.layers:
        for strip in layer.strips:
            bag=strip.channelbag(ob.animation_data.action_slot)
            if bag:
                for fc in bag.fcurves:
                    for pt in fc.keyframe_points:pt.interpolation='CONSTANT'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False
            space.region_3d.view_location=center;space.region_3d.view_distance=cam.data.ortho_scale*1.2;space.region_3d.view_rotation=cam.rotation_euler.to_quaternion();space.region_3d.view_perspective='CAMERA'
for rig in [body,wing,donor]:rig.hide_set(True)
source_col.hide_render=True;source_col.hide_viewport=True
root.hide_set(True)
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:image.pack()
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
notes=bpy.data.texts.new('ANIMATION REVIEW - READ ME')
notes.write('BLENDER PREVIEW ONLY. Flight/takeoff/landing/air attack use real native humanoid16c clips retargeted to the Jade Warrior body; wing/feather channels use the native source rig. Ground attacks use native humanoid01e sword/shield clips.\n'
            'Body/wing rigs remain separate. This montage is NOT a game animation export. Presentation normalizes takeoff/landing character-height endpoints to a common 3m engine flight altitude; root XY removed. Camera follows pelvis height. Air attack donor uses spear choreography with the current sword grip. Folded feathers can overlap near shoulders during ground combat; inspect before any future export.\n'+json.dumps(segments,indent=2))
scene['preview_only']=True;scene['game_integrated']=False
scene.frame_set(segments[1]['start']+15);bpy.context.view_layer.update();select(body);body.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.cycles.samples=16
render_frames={'flight':segments[1]['start']+25,'landing':segments[4]['start']+max(1,segments[4]['native_frames']//2),'combat':segments[6]['start']+max(1,segments[6]['native_frames']//2)}
for label,frame in render_frames.items():
    scene.frame_set(frame);scene.render.filepath=str(O/('review-'+label+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
report=dict(scene=str(OUT),source=str(SOURCE),source_sha256=source_hash,source_unchanged=True,
            segments=segments,checks=checks,warnings=warnings,mapped_body_bones=len(mapped),
            geometry_and_weights_unchanged=True,packed_images=sum(bool(i.packed_file) for i in bpy.data.images),
            separate_rigs=True,body_retargeted=True,flight_altitude_presentation_only=True,flight_height_m=3,root_z_endpoints_normalized=True,root_xy_removed=True,
            air_attack_spear_source_with_sword_grip=True,game_exported=False,game_modified=False,runtime_verified=False,render_frames=render_frames)
(O/'animation-review-report.json').write_text(json.dumps(report,indent=2))
print('DIVINE_WING_GUARD_ANIMATION_REVIEW_READY',cursor-1,flush=True)
