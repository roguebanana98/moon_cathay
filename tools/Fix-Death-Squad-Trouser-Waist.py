"""Extend the real trouser waistband under the Alchemist torso, with spine weights."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-death-squad-trousers'
bpy.ops.wm.open_mainfile(filepath=str(O/'alchemist-11-death-squad-trousers-v3-calves.blend'))
ob=bpy.data.objects['Model 11 | Death Squad cloth trousers and tied cuffs']
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
unseen=set(bm.verts);main=set()
while unseen:
    seed=unseen.pop();component={seed};stack=[seed]
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            n=e.other_vert(v)
            if n in unseen:unseen.remove(n);component.add(n);stack.append(n)
    if len(component)>=200:main.update(component)
edges=[e for e in bm.edges if e.is_boundary and all(v in main and v.co.z>.95 for v in e.verts)]
assert len(edges)>=12,len(edges)
deform=bm.verts.layers.deform.verify()
groups={n:(ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n)).index for n in ('root','spine_0','spine_1')}
original_faces=len(bm.faces);added=0
for height,weights in [(1.005,{'root':.3,'spine_0':.65,'spine_1':.05}),(1.045,{'root':.05,'spine_0':.65,'spine_1':.3})]:
    result=bmesh.ops.extrude_edge_only(bm,edges=edges)
    new={v for v in result['geom'] if isinstance(v,bmesh.types.BMVert)}
    assert new
    for v in new:
        v.co.z=height
        # Tuck the upper edge inside the belt instead of flaring over the torso.
        if height>1.03:v.co.x*=.94;v.co.y=.025+(v.co.y-.025)*.94
        v[deform].clear()
        for name,w in weights.items():v[deform][groups[name]]=w
    edges=[e for e in bm.edges if e.is_boundary and all(v in new for v in e.verts)]
    added+=len(new)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(ob.data);bm.free();ob.data.update()
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
report={'new_vertices':added,'new_faces':len(ob.data.polygons)-original_faces,'top_z':1.045,'samples':[]}
for f in (1,75,160,265,320,410):
    bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh()
    assert all(math.isfinite(c) for v in me.vertices for c in v.co)
    report['samples'].append(f);ev.to_mesh_clear()
bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_distance=2.4
            sp.region_3d.view_location=rig.matrix_world.translation+Vector((0,0,1.0))
            sp.region_3d.view_rotation=Quaternion((.8001,.5599,-.1222,-.1746))
ob['waist_fix']='Low waistband tucked inside belt; top 1.045m, no high cloth panel over torso.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-death-squad-trousers-v5-low-waist.blend'),compress=True)
(O/'low-waist-report.json').write_text(json.dumps(report,indent=2));print('WAIST_FIX_OK',report)
