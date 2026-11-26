"""Restore the original lower-leg bridge between donor cuffs and native boots."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-death-squad-trousers'
bpy.ops.wm.open_mainfile(filepath=str(O/'alchemist-11-death-squad-trousers.blend'))
source=bpy.data.objects['wef_wardancers_legs_01_submesh_1.003']
calves=source.copy();calves.data=source.data.copy();calves.name='Model 11 | Restored native lower legs'
for col in source.users_collection:col.objects.link(calves)
bm=bmesh.new();bm.from_mesh(calves.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>.49],context='VERTS')
bm.to_mesh(calves.data);bm.free();calves.data.update()
calves.hide_set(False);calves.hide_render=False
calves['purpose']='Retain native calf/stocking geometry between donor trouser cuff and native boot. Upper cut is concealed inside trousers.'
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG'];report={'vertices':len(calves.data.vertices),'faces':len(calves.data.polygons),'upper_cut_z':.49,'frames':[]}
assert len(calves.data.polygons)>0
for f in (1,75,160,265,320,410):
    bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=calves.evaluated_get(dg);me=ev.to_mesh()
    assert all(math.isfinite(x) for v in me.vertices for x in v.co)
    report['frames'].append(f);ev.to_mesh_clear()
bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_distance=2.8
            sp.region_3d.view_rotation=Quaternion((.8001,.5599,-.1222,-.1746))
            sp.region_3d.view_location=rig.matrix_world.translation+Vector((0,0,.9))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-death-squad-trousers-v3-calves.blend'),compress=True)
(O/'calf-fix-report.json').write_text(json.dumps(report,indent=2));print('CALF_FIX_OK',report)
