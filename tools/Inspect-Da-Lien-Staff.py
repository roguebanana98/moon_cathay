"""Inspect staff geometry islands in the latest appearance scene."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/da-lien-moon-staff';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/da-lien-skin-warm/da-lien-skin-warm.blend'))
obj=bpy.data.objects['Neferata_Staff'];me=obj.data
parent=list(range(len(me.vertices)))
def root(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
def union(a,b):
    a=root(a);b=root(b)
    if a!=b:parent[b]=a
for edge in me.edges:union(*edge.vertices)
same={}
for v in me.vertices:
    key=tuple(round(x,5) for x in v.co)
    if key in same:union(v.index,same[key])
    else:same[key]=v.index
groups={}
for v in me.vertices:groups.setdefault(root(v.index),[]).append(v.index)
rows=[]
for ids in sorted(groups.values(),key=len,reverse=True):
    ps=[me.vertices[i].co for i in ids]
    rows.append({'id':min(ids),'vertices':len(ids),'min':[min(p[a] for p in ps) for a in range(3)],'max':[max(p[a] for p in ps) for a in range(3)],'vertex_ids':ids})
data={'object':obj.name,'matrix':[list(row) for row in obj.matrix_world],
      'constraints':[(c.type,c.subtarget) for c in obj.constraints],
      'groups':rows,'bounds':[[min(v.co[a] for v in me.vertices) for a in range(3)],[max(v.co[a] for v in me.vertices) for a in range(3)]]}
(O/'staff-islands.json').write_text(json.dumps(data,indent=2))
print(json.dumps({k:v for k,v in data.items() if k!='groups'}))
print(json.dumps([{k:v for k,v in row.items() if k!='vertex_ids'} for row in rows],separators=(',',':')))
