import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-moonshadow-animation-trial';bpy.ops.wm.open_mainfile(filepath=str(O/'da-anh-moonshadow-dagger-handbow-trial.blend'))
ob=bpy.data.objects['Moonshadow Assassin handbow | Da Anh'];rig=bpy.data.objects['Da Anh | Native humanoid01e'];me=ob.data
par=list(range(len(me.vertices)))
def find(i):
 while par[i]!=i:par[i]=par[par[i]];i=par[i]
 return i
for e in me.edges:
 a,b=map(find,e.vertices);par[b]=a
parts={}
for v in me.vertices:parts.setdefault(find(v.index),[]).append(v)
print('MATRIX',[list(r) for r in ob.matrix_basis]);print('PARTS')
for k,vs in sorted(parts.items(),key=lambda x:-len(x[1])):
 if len(vs)>10:print(k,len(vs),[[round(min(v.co[i] for v in vs),5),round(max(v.co[i] for v in vs),5)] for i in range(3)])
scene=bpy.context.scene;scene.frame_set(370);bpy.context.view_layer.update()
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.film_transparent=False;scene.world.color=(.12,.12,.12);scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for l in [o for o in bpy.data.objects if o.type=='LIGHT']:l.hide_render=False
hand=rig.matrix_world@rig.pose.bones['hand_left'].matrix
print('PALM_BONE_WORLD',list(hand.translation))
for name in ['finger_index_left_0','finger_index_left_2','finger_ring_left_0','finger_ring_left_2']:
 print(name,list(hand.inverted()@rig.matrix_world@rig.pose.bones[name].head))
camd=bpy.data.cameras.new('Grip inspect');cam=bpy.data.objects.new('Grip inspect',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.ortho_scale=.65
for label,offset in [('front',Vector((0,-2,.2))),('side',Vector((2,0,.2)))]:
 target=hand.translation;cam.location=target+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/('bow-grip-before-'+label+'.png'));bpy.ops.render.render(write_still=True)
