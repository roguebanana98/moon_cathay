"""Run in the live Blender scene: hide only the long red/gold center strip."""
import bpy,bmesh,json
from pathlib import Path
O=Path('D:/Warhammer3_Modding/moon_cathay/build/alchemist-11-no-back-cape')
assert 'Model 11 | Original outfit without back cape' in bpy.data.objects
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-center-strip-live.blend'),copy=True)
ob=bpy.data.objects['Model 11 | Original outfit without back cape'];me=ob.data
parent=list(range(len(me.vertices)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for e in me.edges:
    a,b=map(find,e.vertices);parent[b]=a
components={}
for v in me.vertices:components.setdefault(find(v.index),[]).append(v.index)
matches=[]
for ids in components.values():
    vs=[me.vertices[i] for i in ids]
    if min(v.co.z for v in vs)<.2 and max(v.co.z for v in vs)>1.0 and max(abs(v.co.x) for v in vs)<.11:
        matches.append(ids)
assert len(matches)==1,[(len(x)) for x in matches]
strip=set(matches[0]);assert len(strip)==23
backup=ob.copy();backup.data=me.copy();backup.name='HIDDEN | Long red gold center strip'
for col in ob.users_collection:col.objects.link(backup)
bm=bmesh.new();bm.from_mesh(backup.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in strip],context='VERTS');bm.to_mesh(backup.data);bm.free()
backup.hide_set(True);backup.hide_render=True
ob.data=me.copy();bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in strip],context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
assert len(backup.data.polygons)==21
ob['outfit']='Original model 11, back cape and long center strip hidden; other robe panels retained.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-no-cape-no-center-strip.blend'),compress=True)
(O/'center-strip-report.json').write_text(json.dumps({'hidden_vertices':23,'hidden_faces':21,'hidden_object':backup.name,'other_panels_retained':True,'deployment':False},indent=2))
print('CENTER_STRIP_HIDDEN')
