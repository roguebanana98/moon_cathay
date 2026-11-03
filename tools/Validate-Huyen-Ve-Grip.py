"""Sample the complete attack clip; report surface proximity, not visual quality."""
import bpy,json
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-rigged-prototype.blend'))
rig=bpy.data.objects['humanoid01e_HuyenVe'];body=bpy.data.objects['mc_huyen_ve_body_lod0'];sword=bpy.data.objects['mc_huyen_ve_sword_lod0']
rig.animation_data.action=bpy.data.actions['QA_attack'];rows=[];attachment_error=0
indices={side:[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('hand_'+side,'finger_index_'+side,'finger_ring_'+side,'thumb_'+side)))>.75] for side in ['left','right']}
for frame in range(63):
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 obj=body.evaluated_get(dg);mesh=obj.to_mesh();points=np.array([list(v.co) for v in mesh.vertices]);assert np.isfinite(points).all()
 inv=rig.pose.bones['weapon_2'].matrix.inverted();se=sword.evaluated_get(dg)
 local=inv@se.matrix_world;attachment_error=max(attachment_error,max(abs(local[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4)))
 contact={}
 for side,ids in indices.items():
  p=np.array([list(inv@mesh.vertices[i].co) for i in ids]);p=p[(p[:,0]>-.15)&(p[:,0]<.18)]
  distance=np.abs(np.sqrt((p[:,1]-.020)**2+p[:,2]**2)-.01885)
  contact[side]={'nearest_surface_gap':float(distance.min()) if len(distance) else None,'vertices_within_6mm':int((distance<.006).sum())}
 rows.append({'frame':frame,'contact':contact});obj.to_mesh_clear()
assert attachment_error<1e-4
assert all(row['contact']['right']['nearest_surface_gap'] is not None and row['contact']['right']['nearest_surface_gap']<.015 for row in rows)
assert rows[20]['contact']['left']['nearest_surface_gap']<.015
report=dict(status='passed',frames=63,max_attachment_matrix_error=attachment_error,
 right_max_nearest_surface_gap=max(row['contact']['right']['nearest_surface_gap'] for row in rows),two_hand_pose=rows[20],
 scope='Finite deformation and rigid weapon_2 attachment over attack frames 0-62; surface proximity is not a penetration or visual-quality test',samples=rows)
(O/'grip-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'}))
