"""Inspect geometric islands without altering the live-snapshot scene."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/da-lien-collar-edit'
bpy.ops.wm.open_mainfile(filepath=str(O/'da-lien-before-collar-edit-live.blend'))
obj=bpy.data.objects['Neferata_Outfit_Sleeves_Collar'];me=obj.data
parents=list(range(len(me.vertices)))
def root(i):
    while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
    return i
def union(a,b):
    a=root(a);b=root(b)
    if a!=b:parents[b]=a
for edge in me.edges:union(*edge.vertices)
same={}
for v in me.vertices:
    key=tuple(round(c,5) for c in v.co)
    if key in same:union(v.index,same[key])
    else:same[key]=v.index
groups={}
for v in me.vertices:groups.setdefault(root(v.index),[]).append(v.index)
rows=[]
for ids in sorted(groups.values(),key=len,reverse=True):
    ps=[me.vertices[i].co for i in ids]
    rows.append({'id':min(ids),'vertices':len(ids),'min':[min(p[a] for p in ps) for a in range(3)],'max':[max(p[a] for p in ps) for a in range(3)],'vertex_ids':ids})
(O/'collar-islands.json').write_text(json.dumps({'object':obj.name,'groups':rows},indent=2))
print(json.dumps([{k:v for k,v in row.items() if k!='vertex_ids'} for row in rows],indent=2))
