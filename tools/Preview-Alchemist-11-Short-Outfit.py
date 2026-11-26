"""Make a reversible local outfit trial from the user's live animation snapshot."""
import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-short-outfit'
bpy.ops.wm.open_mainfile(filepath=str(O/'before-short-live.blend'))
ob=bpy.data.objects['cth_alchemist_body_01_submesh_0']; original_faces=len(ob.data.polygons)
parent=list(range(len(ob.data.vertices)))
def find(x):
    while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
    return x
for e in ob.data.edges:
    a,b=map(find,e.vertices);parent[b]=a
components=json.loads((O/'cloth-components.json').read_text())[1]['components']
chosen=[c for c in components if c['min'][2]<.9 and c['dominant_weights'][0][0].startswith(('cape_','skirt_'))]
keys={c['component'] for c in chosen}
removed={v.index for v in ob.data.vertices if find(v.index) in keys}
assert removed and sum(c['faces'] for c in chosen)<original_faces/4
backup=ob.copy();backup.data=ob.data.copy();backup.name='BACKUP | Model 11 original long outfit'
for col in ob.users_collection:col.objects.link(backup)
backup.hide_set(True);backup.hide_render=True
backup['restore']='Hide short outfit object and unhide this original to restore all cloth.'
ob.data=ob.data.copy();ob.name='Model 11 | Short outfit'
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in removed],context='VERTS')
bm.to_mesh(ob.data);bm.free();ob.data.update()
assert original_faces-len(ob.data.polygons)==sum(c['faces'] for c in chosen)
bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='CONSOLE':area.type='VIEW_3D'
bpy.ops.file.pack_all()
report={'source':'before-short-live.blend','output':'alchemist-11-short-outfit-animation.blend','removed_components':chosen,'original_faces':original_faces,'kept_faces':len(ob.data.polygons),'backup':backup.name,'animation_actions':[a.name for a in bpy.data.actions if a.name.startswith('MW')],'deployment':False}
(O/'short-outfit-report.json').write_text(json.dumps(report,indent=2))
target=O/report['output'];bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
# Reopen so a console-to-3D conversion has an actual SpaceView3D.
bpy.ops.wm.open_mainfile(filepath=str(target))
from mathutils import Quaternion
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.overlay.show_overlays=False
            space.shading.type='MATERIAL'
            space.region_3d.view_rotation=Quaternion((0.8001,0.5599,-0.1222,-0.1746))
            space.region_3d.view_distance=3.3
            # Preserve the source scene's model location, adjusting only height.
            rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
            space.region_3d.view_location=rig.matrix_world.translation+__import__('mathutils').Vector((0,0,.9))
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
print('SHORT_OUTFIT_OK',original_faces,report['kept_faces'],len(chosen))
