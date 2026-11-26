import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives'
bpy.ops.wm.open_mainfile(filepath=str(O/'celestial-concubine-01-dual-knives-grip-fixed.blend'))
for ob in bpy.data.objects['Body_01_native_humanoid01e'].parent.children_recursive:
 if ob.type!='MESH':continue
 print('OBJECT',ob.name,'verts',len(ob.data.vertices),'mats',[m.name for m in ob.data.materials])
 parent=list(range(len(ob.data.vertices)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in ob.data.edges:
  a,b=map(find,e.vertices);parent[b]=a
 groups={}
 for v in ob.data.vertices:groups.setdefault(find(v.index),[]).append(v)
 for pts in sorted(groups.values(),key=len,reverse=True)[:18]:
  print('ISLAND',len(pts),'bounds',[[round(min(v.co[i] for v in pts),4),round(max(v.co[i] for v in pts),4)] for i in range(3)])
