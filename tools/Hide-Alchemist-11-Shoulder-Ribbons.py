"""Hide only the paired patterned ribbons, including upper and lower layers."""
import bpy,bmesh,json
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');O=R/'build/alchemist-11-no-back-cape'
ob=bpy.data.objects['Model 11 | Original outfit without back cape']
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-shoulder-ribbons-live.blend'),copy=True)
rows=json.loads((R/'build/alchemist-11-short-outfit/cloth-components.json').read_text())[1]['components']
keys={2134,2158,2182,2204,2226,2250,2274,2296}
signatures={(r['vertices'],tuple(r['min']),tuple(r['max'])) for r in rows if r['component'] in keys}
assert len(signatures)==8
me=ob.data;parent=list(range(len(me.vertices)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for e in me.edges:
    a,b=map(find,e.vertices);parent[b]=a
components={}
for v in me.vertices:components.setdefault(find(v.index),[]).append(v.index)
sides={'left':set(),'right':set()};matched=0
for ids in components.values():
    vs=[me.vertices[i] for i in ids]
    signature=(len(ids),tuple(min(v.co[j] for v in vs) for j in range(3)),tuple(max(v.co[j] for v in vs) for j in range(3)))
    if signature in signatures:
        side='left' if sum(v.co.x for v in vs)>0 else 'right';sides[side].update(ids);matched+=1
assert matched==8,matched
def subset(mesh,keep):
    bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(mesh);bm.free();mesh.update()
report={}
for side,ids in sides.items():
    backup=ob.copy();backup.data=me.copy();backup.name='HIDDEN | Patterned shoulder ribbon '+side
    for col in ob.users_collection:col.objects.link(backup)
    subset(backup.data,ids);backup.hide_set(True);backup.hide_render=True
    report[side]={'vertices':len(ids),'faces':len(backup.data.polygons),'object':backup.name}
removed=sides['left']|sides['right'];before=len(me.polygons)
ob.data=me.copy();subset(ob.data,set(range(len(me.vertices)))-removed)
assert before-len(ob.data.polygons)==168
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-no-shoulder-ribbons.blend'),compress=True)
(O/'shoulder-ribbons-report.json').write_text(json.dumps(report,indent=2));print('SHOULDER_RIBBONS_HIDDEN')
