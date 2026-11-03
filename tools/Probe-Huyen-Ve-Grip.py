import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-rigged-prototype.blend'))
rig=bpy.data.objects['humanoid01e_HuyenVe'];body=bpy.data.objects['mc_huyen_ve_body_lod0'];sword=bpy.data.objects['mc_huyen_ve_sword_lod0']
scene=bpy.context.scene;camera=scene.camera
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'before'
rows=[]
for clip,frames in [('stand',[1]),('attack',[0,20,31,42])]:
 rig.animation_data.action=bpy.data.actions['QA_'+clip]
 for frame in frames:
  scene.frame_set(frame);bpy.context.view_layer.update()
  inv=rig.pose.bones['weapon_2'].matrix.inverted()
  obj=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=obj.to_mesh()
  sets={}
  for group in ['hand_right','finger_index_right_0','finger_ring_right_0','thumb_right_1']:
   indices=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if body.vertex_groups[g.group].name==group)>.45]
   pts=[inv@mesh.vertices[i].co for i in indices]
   sets[group]={'count':len(pts),'mean':list(sum(pts,Vector())/len(pts)) if pts else None}
  rows.append(dict(clip=clip,frame=frame,mesh=sets,bones={n:list(inv@rig.pose.bones[n].head) for n in ['hand_right','finger_index_right_0','finger_ring_right_0','thumb_right_1']}))
  obj.to_mesh_clear()
  if (clip,frame) in [('stand',1),('attack',20)]:
   target=rig.pose.bones['weapon_2'].matrix@Vector((-.035,-.015,.025))
   camera.location=target+Vector((.7,-1,.5));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.48
   scene.render.resolution_x=850;scene.render.resolution_y=850;scene.cycles.samples=16
   scene.render.filepath=str(O/f'grip_{label}_{clip}.png');bpy.ops.render.render(write_still=True)
(O/f'grip-probe-{label}.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
