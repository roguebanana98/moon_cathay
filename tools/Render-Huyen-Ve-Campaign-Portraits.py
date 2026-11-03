"""Render private UI portraits directly from the approved Huyen Ve model."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v17-campaign';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/huyen-ve-v16-approved/huyen-ve-v16-animation-review.blend'))
rig=bpy.data.objects['humanoid01e_NATIVE_BIND'];actions=[a for a in bpy.data.actions if 'sword_stand' in str(a.get('native_path',''))];assert actions
rig.animation_data.action=actions[0];rig.animation_data.action_slot=actions[0].slots[0];bpy.context.scene.frame_set(0)
for ob in bpy.data.objects:
 if 'sword' in ob.name.lower():ob.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=64;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
cam=scene.camera;cam.data.type='ORTHO';outputs=[]
for internal,size,target,scale in [
 ('ui/portraits/units/no_culture/mc_huyen_ve_0.png',(60,130),(0,0,1.30),1.12),
 ('ui/portraits/faction_leaders/mc_huyen_ve_0.png',(85,115),(0,0,1.47),.83),
 ('ui/portraits/portholes/no_culture/mc_huyen_ve_0.png',(300,164),(0,0,1.48),1.10),
 ('ui/units/icons/mc_huyen_ve.png',(104,208),(0,0,1.28),1.14)]:
 target=Vector(target);cam.location=target+Vector((.25,-4,.1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 scene.render.resolution_x,scene.render.resolution_y=size;p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);outputs.append({'file':internal,'size':size})
(O/'portrait-render-report.json').write_text(json.dumps({'source':'approved v16 exported model and native stand clip','images':outputs},indent=2))
