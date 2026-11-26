"""Lower upturned shoe tips without touching rig, weights, sole ground level."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-normal-boots';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-normal-boot-toes.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-dao-edge-corrected/jade-model05-dao-correct-cutting-edge.blend'))
scene=bpy.context.scene
body=next(o for o in scene.objects if o.type=='MESH' and o.get('source_geometry','').endswith('beitingsheshou5.rigid_model_v2') and o.get('source_part_index')==0)
body.data=body.data.copy();changed=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
for v in body.data.vertices:
 x,y,z=v.co
 if z>.15:continue
 forward=(abs(x)-.10)*.28-(y-.04)*.96
 influence=smooth((forward-.115)/.075)*(1-smooth((z-.105)/.045))
 if influence<=0:continue
 old=list(v.co)
 # Flatten upward hook; retain a small normal toe clearance above the sole.
 v.co.z=max(.006,z-.047*influence)
 # Shorten elongated toe tips slightly along each boot's own forward direction.
 v.co.x-=math.copysign(.0045*influence,x);v.co.y+=.015*influence
 changed.append(dict(index=v.index,before=old,after=list(v.co)))
assert changed and any(p['before'][0]<0 for p in changed) and any(p['before'][0]>0 for p in changed)
body.data.update();body['boot_edit']='Upturned toes lowered and shortened; original weights, UVs and native rig retained'
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'normal-boots-full-preview.png');bpy.ops.render.render(write_still=True)
target=Vector((0,0,.15));cam=scene.camera;cam.location=(.75,-1.7,.43);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.65
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.filepath=str(O/'normal-boots-detail.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),changed_boot_vertices=len(changed),left_and_right=True,rig_weights_uv_unchanged=True,other_geometry_unchanged=True,game_integrated=False,changes=changed),indent=2))
print('NORMAL_BOOTS_READY',OUT,flush=True)
