"""Restore model 11, removing only the separate back cape islands."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-no-back-cape';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/alchemist-11-short-outfit/before-short-live.blend'))
ob=bpy.data.objects['cth_alchemist_body_01_submesh_0'];original=len(ob.data.polygons)
rows=json.loads((R/'build/alchemist-11-short-outfit/cloth-components.json').read_text())[1]['components']
chosen=[c for c in rows if c['dominant_weights'][0][0].startswith('cape_') and c['min'][2]<.9]
assert len(chosen)==2
keys={c['component'] for c in chosen};parent=list(range(len(ob.data.vertices)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for e in ob.data.edges:
    a,b=map(find,e.vertices);parent[b]=a
removed={v.index for v in ob.data.vertices if find(v.index) in keys}
backup=ob.copy();backup.data=ob.data.copy();backup.name='BACKUP | Model 11 complete original with cape'
for col in ob.users_collection:col.objects.link(backup)
backup.hide_set(True);backup.hide_render=True
ob.data=ob.data.copy();ob.name='Model 11 | Original outfit without back cape'
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in removed],context='VERTS');bm.to_mesh(ob.data);bm.free()
assert original-len(ob.data.polygons)==638
assert not bpy.data.objects['wef_wardancers_legs_01_submesh_1.003'].hide_get()
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG'];bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='CONSOLE':area.type='VIEW_3D'
bpy.ops.file.pack_all();target=O/'alchemist-11-original-outfit-no-back-cape.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(target));rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_distance=3.0;sp.region_3d.view_location=rig.matrix_world.translation+Vector((0,0,.9))
            sp.region_3d.view_rotation=Quaternion((.8001,.5599,-.1222,-.1746))
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(O/'cape-only-report.json').write_text(json.dumps({'source':'before-short-live.blend','removed_components':chosen,'removed_faces':638,'original_lower_robe_restored':True,'native_legs_restored':True,'custom_trousers_present':False,'deployment':False},indent=2))
print('CAPE_ONLY_OK')
