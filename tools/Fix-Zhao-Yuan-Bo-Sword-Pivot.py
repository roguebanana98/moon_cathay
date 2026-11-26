"""Restore the native RMV2 prop pivot that COPY_TRANSFORMS suppressed."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Matrix, Vector
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/zhao-yuan-bo-preview'
SOURCE=O/'zhao-yuan-bo-sword-animation-trial.blend'
OUT=O/'zhao-yuan-bo-sword-grip-fixed.blend'
assert not OUT.exists(),'Preserve completed grip review'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
sword=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Yuan Bo sword'))
def body_hash():
    return hashlib.sha256(json.dumps([(o.name,[(tuple(v.co),[(o.vertex_groups[g.group].name,g.weight) for g in v.groups]) for v in o.data.vertices]) for o in bpy.data.collections['01 | Zhao Yixuan original body'].objects if o.type=='MESH']).encode()).hexdigest()
body_before=body_hash();sword_before=hashlib.sha256(np.array([tuple(v.co) for v in sword.data.vertices]).tobytes()).hexdigest()
pivot=sword.matrix_basis.copy()
assert abs(pivot.translation.x-(-.4833669066429138))<1e-6
for c in list(sword.constraints):sword.constraints.remove(c)
c=sword.constraints.new('CHILD_OF');c.name='Native weapon_2 with original RMV2 pivot';c.target=rig;c.subtarget='weapon_2';c.inverse_matrix=Matrix.Identity(4)
sword['grip_fix']='Restore original RMV2 material pivot; no guessed mesh/hand adjustment.'
scene=bpy.context.scene;rows=[]
# Source handle is the long narrow connected island, mesh-local X .3396..6869.
# Primary grasp is near the guard at mesh-local X .44, now weapon-local X -.0434.
handle=Vector((.44,0,0));canonical=Vector((-.4833669066429138,-.002123884856700897,-.0019782138988375664))
assert (pivot.translation-canonical).length<1e-6
for frame in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    actual=sword.evaluated_get(dg).matrix_world;expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix@pivot
    error=max(abs(actual[a][b]-expected[a][b]) for a in range(4) for b in range(4));assert error<1e-4
    # Check that a point ON THE HANDLE lies by the gripping finger bones,
    # rather than only checking attachment at the prop origin.
    index=rig.matrix_world@rig.pose.bones['finger_index_right_0'].head
    ring=rig.matrix_world@rig.pose.bones['finger_ring_right_0'].head
    palm=(index+ring)*.5
    gap=(actual@handle-palm).length
    if frame in [1,44,67,84,115,147,185,226,250,275,308,341]:rows.append(dict(frame=frame,native_attachment_error=error,handle_to_knuckle_midpoint=gap))
    assert gap<.14,(frame,gap)
assert body_hash()==body_before
assert hashlib.sha256(np.array([tuple(v.co) for v in sword.data.vertices]).tobytes()).hexdigest()==sword_before
scene.cycles.samples=16
cam=scene.camera
for label,frame,position,target,scale in [
    ('grip-side',341,(4,-.1,1.25),(0,0,1.15),1.9),
    ('attack',115,(3,-6,2),(0,0,1.1),3.4),
    ('casting',308,(3,-6,2),(0,0,1.1),3.4),
]:
    scene.frame_set(frame);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    scene.render.filepath=str(O/('fixed-'+label+'.png'));bpy.ops.render.render(write_still=True)
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_location=Vector((0,0,1));sp.region_3d.view_distance=3.4;sp.region_3d.view_rotation=Vector((-2,8,-.7)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'
bpy.data.texts.new('GRIP FIX - ORIGINAL RMV2 PIVOT').write('Original trial COPY_TRANSFORMS suppressed the RMV2 material pivot, putting the blade in the hand. CHILD_OF with identity inverse now preserves the original pivot in matrix_basis. Native pivot in Blender: (-0.4833669,-0.0021239,-0.0019782). No body/hand/weight/sword vertex edits. This is a preview fix, not a game pack change. SPACE plays all clips.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'grip-fix-report.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),cause='COPY_TRANSFORMS discarded RMV2 material pivot',original_pivot_restored=list(pivot.translation),all_341_frames_checked=True,handle_checks=rows,body_hands_weights_unchanged=True,sword_vertices_unchanged=True,game_modified=False,runtime_verified=False),indent=2))
print('ZHAO_SWORD_PIVOT_FIXED',OUT,flush=True)
