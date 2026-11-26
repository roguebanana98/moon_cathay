"""Place actual handbow pistol grip inside Da Anh's left palm."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-moonshadow-animation-trial';SOURCE=O/'da-anh-moonshadow-dagger-handbow-trial.blend';OUT=O/'da-anh-moonshadow-handbow-grip-fixed.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;rig=bpy.data.objects['Da Anh | Native humanoid01e'];ob=bpy.data.objects['Moonshadow Assassin handbow | Da Anh']
scene.frame_set(370);bpy.context.view_layer.update();hand=rig.pose.bones['hand_left'];inv=hand.matrix.inverted()
palm=sum((inv@rig.pose.bones['finger_'+f+'_left_'+str(n)].head for f in ['index','ring'] for n in [0,2]),Vector())/4;palm.y-=.003
handle=Vector((.16,.09,-.025));before=ob.matrix_basis.copy();fixed=before.copy();fixed.translation=palm-fixed.to_3x3()@handle;ob.matrix_basis=fixed
ob['handle_midpoint']=list(handle);ob['palm_target']=list(palm);ob['fitting']='Actual curved pistol grip, replacing inherited receiver/prop origin alignment'
checks=[]
for f in (1,75,170,220,270,320,350,370,394,420,442):
 scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();actual=ob.evaluated_get(dg).matrix_world@handle;expected=rig.matrix_world@hand.matrix@palm;err=(actual-expected).length;assert err<1e-4;checks.append(dict(frame=f,error=err))
scene.frame_set(370);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,-.1,1.25);sp.region_3d.view_distance=2.2;sp.region_3d.view_rotation=Vector((-.5,8,-.3)).to_track_quat('-Z','Y')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'handbow-grip-fix.json').write_text(json.dumps(dict(scene=str(OUT),before=[list(r) for r in before],after=[list(r) for r in fixed],handle=list(handle),palm=list(palm),checks=checks,game_modified=False),indent=2))
# Render close fitting from the same two views used for diagnosis.
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.film_transparent=False;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for l in [o for o in bpy.data.objects if o.type=='LIGHT']:l.hide_render=False
world=rig.matrix_world@hand.matrix;camd=bpy.data.cameras.new('Fit inspect');cam=bpy.data.objects.new('Fit inspect',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.ortho_scale=.65
for label,offset in [('front',Vector((0,-2,.2))),('side',Vector((2,0,.2)))]:
 target=world.translation;cam.location=target+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/('bow-grip-after-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('HANDBOW_GRIP_FIXED',flush=True)
