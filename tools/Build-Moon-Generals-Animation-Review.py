"""Bake native clips, including constant pose channels, into a labelled review."""
import bpy,addon_utils,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/moon-generals-preview';D=R/'reference/local/wwd-all-lords'
SOURCE=O/'moon-generals-assault-polearm-connected.blend';OUT=O/'moon-generals-animation-review-v3.blend'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
spec=json.loads((O/'animation-review-clips.json').read_text(encoding='utf8'))
scene=bpy.context.scene;scene.render.fps=30
rigs={label:next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith(label)) for label in spec['clips']}
weapons={label:[o for o in bpy.data.collections['Weapons | '+label+' General'].objects if o.type=='MESH' and not o.hide_get()] for label in rigs}
baseline={o.name:tuple(tuple(v.co) for v in o.data.vertices) for group in weapons.values() for o in group}
stored={};checks=[]
for label,rig in rigs.items():
    stored[label]=[]
    body=max([o for o in rig.parent.children if o.type=='MESH' and not o.hide_get() and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)],key=lambda o:len(o.data.vertices))
    for clip in spec['clips'][label]:
        bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
        rig.animation_data_clear()
        for bone in rig.pose.bones:bone.matrix_basis.identity();bone.rotation_mode='QUATERNION'
        imported,_,grip_warnings=import_anim.import_file(bpy.context,str(D/spec['grips'][label]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
        assert imported==rig and not grip_warnings,grip_warnings
        scene.frame_set(0);bpy.context.view_layer.update()
        imported,_,warnings=import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
        assert imported==rig and not warnings,warnings
        action=rig.animation_data.action;action.name=label+' | SOURCE '+clip['label'];action.use_fake_user=True
        first,last=map(int,action.frame_range);frames=list(range(first,last+1))
        data={b.name:dict(location=[],rotation=[],scale=[]) for b in rig.pose.bones};previous={}
        sample_frames={first,last,first+(last-first)//4,first+(last-first)//2,first+3*(last-first)//4}
        origin={};minimum_grip=[];body_points=[];max_attachment_error=0
        bone_name='be_prop_0' if label=='Assault' else 'weapon_1'
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update()
            for bone in rig.pose.bones:
                basis=bone.matrix_basis.copy()
                if bone.parent is None:
                    pose=bone.matrix.copy()
                    if bone.name not in origin:origin[bone.name]=pose.translation.copy()
                    pose.translation.x=0;pose.translation.y=0
                    basis=bone.bone.matrix_local.inverted()@pose
                loc,rot,scale=basis.decompose();rot.normalize()
                if bone.name in previous and rot.dot(previous[bone.name])<0:rot.negate()
                previous[bone.name]=rot.copy()
                data[bone.name]['location'].append(tuple(loc));data[bone.name]['rotation'].append(tuple(rot));data[bone.name]['scale'].append(tuple(scale))
            if frame in sample_frames:
                assert all(math.isfinite(v) for bone in rig.pose.bones for row in bone.matrix for v in row)
                dg=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(dg)
                points=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
                assert all(math.isfinite(v) for p in points for v in p)
                span=max(max(p[k] for p in points)-min(p[k] for p in points) for k in range(3));assert span<5,(label,clip['label'],span)
                body_points.append(tuple(points[len(points)//3]))
                weapon_frame=rig.matrix_world@rig.pose.bones[bone_name].matrix
                for ob in weapons[label]:
                    rel=weapon_frame.inverted()@ob.evaluated_get(dg).matrix_world
                    err=max(abs(rel[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))
                    max_attachment_error=max(max_attachment_error,err)
                distances=[]
                for hand in ['hand_left','hand_right']:
                    pb=rig.pose.bones[hand]
                    point=weapon_frame.inverted()@rig.matrix_world@((pb.head+pb.tail)*.5)
                    sy=.02337646484375 if label=='Assault' else 0
                    sz=-.0023 if label=='Assault' else 0
                    distances.append(math.hypot(point.y-sy,point.z-sz)*rig.parent.scale.x)
                minimum_grip.append(min(distances))
        assert max_attachment_error<1e-4,(label,clip,max_attachment_error)
        motion=max((Vector(p)-Vector(body_points[0])).length for p in body_points)
        if clip['label']!='Idle':assert motion>.005,(label,clip['label'],motion)
        checks.append(dict(model=label,clip=clip['label'],path=clip['path'],frames=len(frames),sampled_poses=len(sample_frames),body_motion_metres=motion,
                           max_weapon_frame_error=max_attachment_error,max_nearest_hand_axis_distance_m=max(minimum_grip),finite=True,warnings=warnings))
        stored[label].append(dict(label=clip['label'],source=clip['path'],first=first,last=last,data=data))
        print('CLIP_VERIFIED',label,clip['label'],len(frames),flush=True)

segments=[];cursor=1
for index,label in enumerate([c['label'] for c in spec['clips']['Assault']]):
    duration=120 if index<4 else max(stored[m][index]['last']-stored[m][index]['first']+1 for m in rigs)
    segments.append(dict(label=label,start=cursor,end=cursor+duration-1));cursor+=duration

for label,rig in rigs.items():
    all_data={name:dict(location=[],rotation=[],scale=[]) for name in rig.pose.bones.keys()}
    frames=list(range(1,cursor));previous={}
    for index,segment in enumerate(segments):
        native=stored[label][index];length=native['last']-native['first']+1
        for frame in range(segment['end']-segment['start']+1):
            source_index=frame%length if index<4 else min(frame,length-1)
            for name,target in all_data.items():
                for channel in ['location','scale']:target[channel].append(native['data'][name][channel][source_index])
                q=list(native['data'][name]['rotation'][source_index])
                if name in previous and sum(a*b for a,b in zip(q,previous[name]))<0:q=[-v for v in q]
                target['rotation'].append(q);previous[name]=q
    rig.animation_data_clear()
    action,curves=import_anim._new_action_fcurves(rig,label+' General | NATIVE REVIEW - ALL BONES');action.use_fake_user=True
    for name,values in all_data.items():
        pb=rig.pose.bones[name]
        import_anim._fill_fcurves(curves,pb.path_from_id('location'),3,values['location'],frames,name)
        import_anim._fill_fcurves(curves,pb.path_from_id('rotation_quaternion'),4,values['rotation'],frames,name)
        import_anim._fill_fcurves(curves,pb.path_from_id('scale'),3,values['scale'],frames,name)
    for fc in curves:
        for point in fc.keyframe_points:point.interpolation='LINEAR'
    rig.hide_set(True)

for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for s in segments:scene.timeline_markers.new(s['label'].upper(),frame=s['start'])
scene.frame_start=1;scene.frame_end=cursor-1
scene.sync_mode='FRAME_DROP'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.overlay.show_extras=False;sp.overlay.show_floor=False
            sp.region_3d.view_location=Vector((0,0,1.2));sp.region_3d.view_distance=7.5
            sp.region_3d.view_rotation=Vector((3,12,-.5)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'

def caption(text,x,z,size):
    curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.align_x='CENTER';curve.size=size
    ob=bpy.data.objects.new(text,curve);scene.collection.objects.link(ob);ob.location=(x,-.8,z);ob.rotation_euler=(math.pi/2,0,0)
    mat=bpy.data.materials.get('Animation review captions')
    if not mat:
        mat=bpy.data.materials.new('Animation review captions');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value=(.9,.9,.9,1);bs.inputs['Emission Color'].default_value=(.9,.9,.9,1);bs.inputs['Emission Strength'].default_value=.6
    curve.materials.append(mat);return ob
caption('ASSAULT GENERAL',-1.65,-.35,.15);caption('BASTION GENERAL',1.65,-.35,.15)
for segment in segments:
    ob=caption(segment['label'].upper(),0,3.2,.20)
    for f,scale in [(0,0),(segment['start'],1),(segment['end']+1,0)]:
        ob.scale=(scale,)*3;ob.keyframe_insert(data_path='scale',frame=f)
    action=ob.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            bag=strip.channelbag(ob.animation_data.action_slot)
            if bag:
                for fc in bag.fcurves:
                    for point in fc.keyframe_points:point.interpolation='CONSTANT'

scene.frame_set(segments[4]['start']);bpy.context.view_layer.update()
for group in weapons.values():
    for ob in group:assert baseline[ob.name]==tuple(tuple(v.co) for v in ob.data.vertices)
notes=bpy.data.texts.new('ANIMATION REVIEW - READ ME')
notes.write('Native rig clips, including hand grip and constant bone channels, baked to a single review timeline. '
            'Locomotion loops for120frames. Attacks play once at native timing; shorter character clip holds its ending pose '
            'until the shared segment ends. Root XY movement removed for stationary comparison. No game export or engine test.\n'+json.dumps(segments,indent=2))
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report=dict(scene=str(OUT),source=str(SOURCE),segments=segments,checks=checks,sampled_poses=sum(x['sampled_poses'] for x in checks),geometry_unchanged=True,engine_tested=False)
(O/'animation-review-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('MOON_GENERALS_ANIMATION_REVIEW_READY',cursor-1,flush=True)
