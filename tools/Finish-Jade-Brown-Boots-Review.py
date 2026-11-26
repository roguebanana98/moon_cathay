import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-animation-review'
bpy.ops.wm.open_mainfile(filepath=str(O/'jade-warrior-brown-boots-animation-review.blend'))
body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('source_geometry','').endswith('beitingsheshou5.rigid_model_v2') and o.get('source_part_index')==0)
for mat in body.data.materials:
 for n in mat.node_tree.nodes:
  if n.type=='VALTORGB' and abs(n.color_ramp.elements[0].color[0]-.040)<1e-5 and abs(n.color_ramp.elements[1].color[0]-.095)<1e-5:
   n.color_ramp.elements[0].color=(.012,.006,.0038,1);n.color_ramp.elements[1].color=(.030,.015,.009,1)
scene=bpy.context.scene;scene.frame_set(1);OUT=O/'jade-warrior-brown-boots-animation-review-v2.blend'
assert not OUT.exists();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
cam=scene.camera;target=Vector((0,0,.15));cam.location=(.75,-1.7,.43);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.65
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.filepath=str(O/'brown-boots-final.png');bpy.ops.render.render(write_still=True)
report=json.loads((O/'review-report.json').read_text());report['scene']=str(OUT);report['toe_colour']='Dark brown matched closer to boot leather; v2 supersedes lighter v1';(O/'review-report.json').write_text(json.dumps(report,indent=2))
