import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives'
bpy.ops.wm.open_mainfile(filepath=str(O/'celestial-concubine-01-head-01-dual-knives.blend'))
rig=bpy.data.objects['Body_01_native_humanoid01e'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for side in ['right','left']:
 inv=(rig.matrix_world@rig.pose.bones['hand_'+side].matrix).inverted();print('SIDE',side)
 for ob in rig.parent.children_recursive:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh()
  for group in ['hand_'+side,'finger_index_'+side+'_0','finger_index_'+side+'_1','finger_index_'+side+'_2','finger_ring_'+side+'_0','finger_ring_'+side+'_1','finger_ring_'+side+'_2','thumb_'+side+'_1']:
   vg=ob.vertex_groups.get(group)
   if not vg:continue
   ids=[v.index for v in ob.data.vertices if any(g.group==vg.index and g.weight>.5 for g in v.groups)]
   pts=[inv@ev.matrix_world@me.vertices[i].co for i in ids]
   if pts:print(ob.name,group,len(pts),'mean',list(sum(pts,Vector())/len(pts)),'bounds',[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)])
  ev.to_mesh_clear()
 for b in rig.pose.bones:
  if b.name.startswith(('finger_','thumb_')) and '_'+side+'_' in b.name:print('BONE',b.name,list(inv@rig.matrix_world@b.head))
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('Death Squad knife'):
  print('KNIFE',ob.name,'local',[list(r) for r in ob.matrix_basis],'bounds',[[min(v.co[i] for v in ob.data.vertices),max(v.co[i] for v in ob.data.vertices)] for i in range(3)])
