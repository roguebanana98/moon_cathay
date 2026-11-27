"""Render a side close-up from our generated review scene, without saving it."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-v36-zhao-jade'
for kind in ['warhorse','jade_longma']:
 bpy.ops.wm.open_mainfile(filepath=str(O/('zhao-'+kind+'-review.blend')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith('humanoid01e'))
 # Keep the existing review placement. Two-rig flight alignment is not an
 # engine placement proof and must not be "fixed" by a guessed root rotation.
 head=rig.pose.bones.get('head') or rig.pose.bones.get('head_0')
 target=rig.matrix_world@(head.head if head else Vector((0,0,1.6)))
 cam=bpy.context.scene.camera;cam.location=target+Vector((5,-1,1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
 bpy.context.scene.render.filepath=str(O/('zhao-'+kind+'-rider-side.png'));bpy.ops.render.render(write_still=True)
 print(kind,'HEAD',list(target),flush=True)
