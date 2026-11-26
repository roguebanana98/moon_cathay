import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-short-outfit'
bpy.ops.wm.open_mainfile(filepath=str(O/'before-short-live.blend'))
root=bpy.data.objects['VARIANT 11'];rig=next(o for o in root.children_recursive if o.type=='ARMATURE')
report=[]
for ob in root.children_recursive:
    if ob.type!='MESH' or ob.hide_get():continue
    mesh=ob.data;parent=list(range(len(mesh.vertices)))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for edge in mesh.edges:
        a,b=map(find,edge.vertices);parent[b]=a
    groups={}
    for polygon in mesh.polygons:groups.setdefault(find(polygon.vertices[0]),[]).append(polygon.index)
    components=[]
    for key,faces in groups.items():
        ids=sorted({v for f in faces for v in mesh.polygons[f].vertices});pts=[mesh.vertices[v].co for v in ids]
        lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];weights={}
        for i in ids:
            for g in mesh.vertices[i].groups:
                name=ob.vertex_groups[g.group].name;weights[name]=weights.get(name,0)+g.weight
        components.append(dict(component=key,vertices=len(ids),faces=len(faces),min=lo,max=hi,dominant_weights=sorted(weights.items(),key=lambda p:-p[1])[:4]))
    components.sort(key=lambda c:-c['faces']);row=dict(object=ob.name,total_faces=len(mesh.polygons),components=components);report.append(row)
    print('MESH',ob.name,'faces',len(mesh.polygons),'components',len(components))
    for c in components[:15]:print(json.dumps(c))
(O/'cloth-components.json').write_text(json.dumps(report,indent=2))
