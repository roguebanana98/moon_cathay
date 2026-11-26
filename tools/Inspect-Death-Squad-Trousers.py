import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-death-squad-trousers';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/cathay-ror-preview/dark-society-death-squad-models.blend'))
ob=bpy.data.objects['cth_peasant_body_03_submesh_0_su'];me=ob.data
parent=list(range(len(me.vertices)))
def find(x):
    while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
    return x
for e in me.edges:
    a,b=map(find,e.vertices);parent[b]=a
groups={}
for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
rows=[]
for k,ids in groups.items():
    pts=[me.vertices[i].co for i in ids];w={}
    for i in ids:
        for g in me.vertices[i].groups:
            n=ob.vertex_groups[g.group].name;w[n]=w.get(n,0)+g.weight
    rows.append(dict(key=k,count=len(ids),min=[min(v[j] for v in pts) for j in range(3)],max=[max(v[j] for v in pts) for j in range(3)],weights=sorted(w.items(),key=lambda a:-a[1])[:5]))
rows.sort(key=lambda a:-a['count']);(O/'donor-components.json').write_text(json.dumps(rows,indent=2))
for row in rows:
    if row['min'][2]<1.1 and row['max'][2]>.4:print(row)
print('RIG',[(b.name,tuple(b.head_local)) for b in next(m.object for m in ob.modifiers if m.type=='ARMATURE').data.bones if any(s in b.name for s in ['upperleg','lowerleg','foot','root'])])
