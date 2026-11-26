"""Hide the two red shoulder assemblies in the current live model 11 scene."""
import bpy,bmesh,json
from pathlib import Path
O=Path('D:/Warhammer3_Modding/moon_cathay/build/alchemist-11-no-back-cape')
ob=bpy.data.objects['Model 11 | Original outfit without back cape']
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-red-shoulders-live.blend'),copy=True)
me=ob.data;parent=list(range(len(me.vertices)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for e in me.edges:
    a,b=map(find,e.vertices);parent[b]=a
components={}
for v in me.vertices:components.setdefault(find(v.index),[]).append(v.index)
sides={'left':set(),'right':set()};counts={'left':0,'right':0}
for ids in components.values():
    names={ob.vertex_groups[g.group].name for i in ids for g in me.vertices[i].groups if g.weight>1e-5}
    for side in sides:
        if names=={'shoulderpad_'+side+'_0'}:
            sides[side].update(ids);counts[side]+=1
assert all(len(ids)>100 for ids in sides.values()),counts
def subset(mesh,keep):
    bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(mesh);bm.free();mesh.update()
report={}
for side,ids in sides.items():
    backup=ob.copy();backup.data=me.copy();backup.name='HIDDEN | Red shoulder armour '+side
    for col in ob.users_collection:col.objects.link(backup)
    subset(backup.data,ids);backup.hide_set(True);backup.hide_render=True
    report[side]={'vertices':len(ids),'faces':len(backup.data.polygons),'components':counts[side],'object':backup.name}
removed=sides['left']|sides['right'];before=len(me.polygons)
ob.data=me.copy();subset(ob.data,set(range(len(me.vertices)))-removed)
assert before-len(ob.data.polygons)==sum(r['faces'] for r in report.values())
ob['shoulders']='Red shoulder armour assemblies hidden separately; gold upper-arm caps and sleeves retained.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-no-cape-no-center-strip-no-red-shoulders.blend'),compress=True)
(O/'red-shoulders-report.json').write_text(json.dumps(report,indent=2))
print('RED_SHOULDERS_HIDDEN',report)
