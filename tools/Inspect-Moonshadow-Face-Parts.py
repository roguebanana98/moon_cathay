import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moonshadow-assassin-four-faces'
bpy.ops.wm.open_mainfile(filepath=str(O/'moonshadow-assassin-four-faces.blend'))
report=[]
for ob in bpy.data.objects:
    if not ob.name.startswith(('MSA 03 | Face','MSA 04 | Face')) or ob.type!='MESH':continue
    me=ob.data;parent=list(range(len(me.vertices)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for e in me.edges:
        a,b=map(find,e.vertices);parent[b]=a
    parts={}
    for v in me.vertices:parts.setdefault(find(v.index),[]).append(v.index)
    entries=[]
    for key,ids in parts.items():
        vs=[me.vertices[i] for i in ids];entries.append({'key':key,'verts':len(ids),'min':[min(v.co[j] for v in vs) for j in range(3)],'max':[max(v.co[j] for v in vs) for j in range(3)]})
    entries.sort(key=lambda r:-r['verts']);row={'object':ob.name,'components':entries};report.append(row)
    print(ob.name,[(e['key'],e['verts'],[round(x,3) for x in e['min']],[round(x,3) for x in e['max']]) for e in entries if e['verts']>30])
(O/'face-components.json').write_text(json.dumps(report,indent=2))
