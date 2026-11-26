import bpy,json,numpy as np,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/zhao-yuan-bo-preview'
bpy.ops.wm.open_mainfile(filepath=str(O/'zhao-yuan-bo-sword-animation-trial.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');sw=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Yuan Bo sword'))
bpy.context.scene.frame_set(341);bpy.context.view_layer.update();W=(rig.matrix_world@rig.pose.bones['weapon_2'].matrix);inv=W.inverted()
result={'sword_bounds':[[min(v.co[i] for v in sw.data.vertices),max(v.co[i] for v in sw.data.vertices)] for i in range(3)],'bones':{},'hands':[]}
for b in rig.pose.bones:
 if any(x in b.name for x in ['hand','finger','weapon_2']):result['bones'][b.name]={'head_in_weapon':list(inv@(rig.matrix_world@b.head)),'tail_in_weapon':list(inv@(rig.matrix_world@b.tail))}
for ob in bpy.data.collections['01 | Zhao Yixuan original body'].objects:
 if ob.type!='MESH':continue
 groups={g.index:g.name for g in ob.vertex_groups};ids=[v.index for v in ob.data.vertices if sum(g.weight for g in v.groups if groups[g.group]=='hand_right')>.6]
 if ids:
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();p=np.array([list(inv@(ev.matrix_world@me.vertices[i].co)) for i in ids]);ev.to_mesh_clear();result['hands'].append({'object':ob.name,'count':len(ids),'mean_in_weapon':p.mean(axis=0).tolist(),'bounds':np.stack([p.min(axis=0),p.max(axis=0)]).tolist()})
bm=bmesh.new();bm.from_mesh(sw.data);seen=set();parts=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);comp=[]
 while todo:
  a=todo.pop();comp.append(a)
  for e in a.link_edges:
   n=e.other_vert(a)
   if n not in seen:seen.add(n);todo.append(n)
 p=np.array([tuple(v.co) for v in comp]);parts.append({'count':len(comp),'bounds':np.stack([p.min(axis=0),p.max(axis=0)]).tolist(),'mean':p.mean(axis=0).tolist()})
result['sword_components']=sorted(parts,key=lambda x:-x['count']);(O/'grip-analysis.json').write_text(json.dumps(result,indent=2));print('GRIP_ANALYZED')
