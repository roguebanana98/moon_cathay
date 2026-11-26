"""Portraits from the user-approved native-pivot sword trial; no source edits."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-v34-yuan-bo-lord';O.mkdir(exist_ok=True);P=O/'renders';P.mkdir(exist_ok=True)
SOURCE=R/'build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-grip-fixed.blend'
assert SOURCE.exists();before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.frame_set(1)
cam=scene.camera;scene.cycles.samples=16;scene.render.resolution_percentage=100
for kind,z,scale,size in [('body',1.05,2.8,(512,768)),('head',1.66,.72,(512,512))]:
    cam.location=(.3,-6,z+.15);cam.rotation_euler=(Vector((0,0,z))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(P/('mc_mooncourt_lord_'+kind+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before
(O/'portrait-review.json').write_text(json.dumps(dict(source=str(SOURCE),source_sha256=before,source_unchanged=True,approved_pivot_preserved=True,rendered=['body','head']),indent=2))
print('APPROVED_YUAN_BO_LORD_PORTRAITS_READY',flush=True)
