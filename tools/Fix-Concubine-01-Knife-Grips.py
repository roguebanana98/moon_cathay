"""Fit each handle to the actual current 01 hand geometry and knuckle axis."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives'
SOURCE=O/'celestial-concubine-01-head-01-dual-knives.blend';OUT=O/'celestial-concubine-01-dual-knives-grip-fixed.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;rig=bpy.data.objects['Body_01_native_humanoid01e']
scene.frame_set(1);bpy.context.view_layer.update();report=[]
for side in ['right','left']:
 ob=bpy.data.objects['Death Squad knife | hand_'+side]
 inv=rig.pose.bones['hand_'+side].matrix.inverted()
 knuckles=[inv@rig.pose.bones['finger_'+f+'_'+side+'_0'].head for f in ['index','ring']]
 curls=[inv@rig.pose.bones['finger_'+f+'_'+side+'_2'].head for f in ['index','ring']]
 # Grip cavity is halfway from palm knuckles to curled fingertips; the
 # long handle axis runs across the palm from index side toward ring side.
 grip=(sum(knuckles,Vector())+sum(curls,Vector()))*.25
 grip.y-=.003
 xaxis=(knuckles[1]-knuckles[0]).normalized()
 yaxis=Vector((0,1,0));yaxis=(yaxis-xaxis*yaxis.dot(xaxis)).normalized()
 zaxis=xaxis.cross(yaxis).normalized();rot=Matrix((xaxis,yaxis,zaxis)).transposed()
 handle=Vector(ob['handle_midpoint']);local=rot.to_4x4();local.translation=grip-rot@handle
 before=ob.matrix_basis.copy();ob.matrix_basis=local;ob['palm_target']=list(grip)
 report.append(dict(hand=side,palm_target=list(grip),handle_axis=list(xaxis),before=[list(r) for r in before],after=[list(r) for r in local]))
checks=[]
for frame in (1,50,100,160,220,280,336):
 scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for side in ['right','left']:
  ob=bpy.data.objects['Death Squad knife | hand_'+side]
  actual=ob.evaluated_get(dg).matrix_world@Vector(ob['handle_midpoint']);expected=rig.matrix_world@rig.pose.bones['hand_'+side].matrix@Vector(ob['palm_target'])
  error=(actual-expected).length;assert error<1e-4
  checks.append(dict(frame=frame,hand=side,error=error))
scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,0,.95);sp.region_3d.view_distance=2.4;sp.region_3d.view_rotation=Vector((-.5,8,-.1)).to_track_quat('-Z','Y')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'grip-fix-report.json').write_text(json.dumps(dict(scene=str(OUT),hands=report,checks=checks,animation_unchanged=True,game_modified=False),indent=2))
print('GRIPS_FIXED',flush=True)
