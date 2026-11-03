import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-rigged-prototype.blend'))
rig=bpy.data.objects['humanoid01e_HuyenVe'];body=bpy.data.objects['mc_huyen_ve_body_lod0'];rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis.identity()
def point(name,direction):
 p=rig.pose.bones[name];bpy.context.view_layer.update();q=(p.tail-p.head).rotation_difference(Vector(direction));p.matrix=Matrix.Translation(p.head)@q.to_matrix().to_4x4()@Matrix.Translation(-p.head)@p.matrix;bpy.context.view_layer.update()
for side,s in [('left',1),('right',-1)]:
 point('upperarm_'+side,(s*.125,-.015,-.26));point('lowerarm_'+side,(s*.06,-.02,-.245));point('hand_'+side,(s*.025,-.01,-.09))
obj=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=obj.to_mesh()
rows=[]
for side,s in [('left',1),('right',-1)]:
 h=rig.pose.bones['hand_'+side];inv=h.matrix.inverted()
 pts=[mesh.vertices[v.index].co for v in body.data.vertices if v.co.x*s>.24 and sum(g.weight for g in v.groups if side in body.vertex_groups[g.group].name and body.vertex_groups[g.group].name.startswith(('hand','finger','thumb')))> .3]
 rows.append(dict(side=side,bones={p.name:{'head':list(p.head),'tail':list(p.tail),'hand_local':list(inv@p.head)} for p in rig.pose.bones if side in p.name and p.name.startswith(('hand','finger','thumb'))},points=[list(p) for p in pts],hand_local_points=[list(inv@p) for p in pts]))
obj.to_mesh_clear();(O/'hand-fit-probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{k:v for k,v in row.items() if k not in ['points','hand_local_points']} for row in rows]))
scene=bpy.context.scene;target=rig.pose.bones['hand_right'].head+Vector((0,0,-.08));cam=scene.camera;cam.location=target+Vector((0,-1,.1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.4
for p in rig.pose.bones:
 if 'right' in p.name and p.name.startswith(('hand','finger','thumb')):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.004,location=p.head)
for o in bpy.data.objects:
 if o.name.startswith('mc_huyen_ve_sword'):o.hide_render=True
scene.render.resolution_x=700;scene.render.resolution_y=900;scene.render.filepath=str(O/'hand_fit_before.png');bpy.ops.render.render(write_still=True)
