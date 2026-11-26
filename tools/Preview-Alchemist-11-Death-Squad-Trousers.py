"""Fit actual Death Squad trousers, retaining their UVs, folds and cuff cords."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-death-squad-trousers'
bpy.ops.wm.open_mainfile(filepath=str(R/'build/alchemist-11-short-outfit/alchemist-11-short-outfit-animation.blend'))
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG'];legs=bpy.data.objects['wef_wardancers_legs_01_submesh_1.003']
with bpy.data.libraries.load(str(R/'build/cathay-ror-preview/dark-society-death-squad-models.blend'),link=False) as (src,dst):
    dst.objects=['cth_peasant_body_03_submesh_0_su']
ob=dst.objects[0];source_rig=next(m.object for m in ob.modifiers if m.type=='ARMATURE')
source_rest={b.name:b.matrix_local.copy() for b in source_rig.data.bones}
rows=json.loads((O/'donor-components.json').read_text())
keys={110,496,0,90,326}
keys.update(r['key'] for r in rows if r['min'][2]>.34 and r['max'][2]<.47 and r['weights'][0][0].startswith('lowerleg_'))
me=ob.data;parents=list(range(len(me.vertices)))
def find(i):
    while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
    return i
for e in me.edges:
    a,b=map(find,e.vertices);parents[b]=a
keep={v.index for v in me.vertices if find(v.index) in keys}
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(me);bm.free()
aliases={'skirt_back_1':'skirt_back_left_1','skirt_back_2':'skirt_back_right_1'}
mapping={g.name:(g.name if g.name in rig.data.bones else aliases.get(g.name,'root')) for g in ob.vertex_groups}
# Correct each retained vertex from donor bind space into target bind space.
for v in me.vertices:
    old=v.co.copy();new=Vector();total=0
    for g in v.groups:
        name=ob.vertex_groups[g.group].name;target=mapping[name]
        new+=(rig.data.bones[target].matrix_local@source_rest[name].inverted()@old)*g.weight;total+=g.weight
    if total:v.co=new/total
for group in list(ob.vertex_groups):
    target=mapping[group.name]
    if target!=group.name:
        dest=ob.vertex_groups.get(target) or ob.vertex_groups.new(name=target)
        for v in me.vertices:
            for g in list(v.groups):
                if g.group==group.index:dest.add([v.index],g.weight,'ADD')
        ob.vertex_groups.remove(group)
ob.name='Model 11 | Death Squad cloth trousers and tied cuffs'
for col in legs.users_collection:col.objects.link(ob)
ob.parent=legs.parent;ob.matrix_parent_inverse=legs.matrix_parent_inverse.copy();ob.matrix_basis=legs.matrix_basis.copy()
for m in ob.modifiers:
    if m.type=='ARMATURE':m.object=rig
ob.hide_set(False);ob.hide_render=False
legs.hide_set(True);legs.hide_render=True
ob['donor']='Dark Society Death Squad / cth_ninja_ds; actual cloth, cuff ropes and UVs retained'
ob['fit']='Per-weight source-bind to target-bind correction; existing target skeleton unchanged'
report={'output':'alchemist-11-death-squad-trousers.blend','components':sorted(keys),'vertices':len(me.vertices),'faces':len(me.polygons),'samples':[],'deployment':False}
poses=[]
for frame in (1,75,160,264,320,410):
    bpy.context.scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
    points=[tuple(v.co) for v in mesh.vertices];assert all(math.isfinite(c) for p in points for c in p)
    poses.append(points);report['samples'].append({'frame':frame,'finite':True});ev.to_mesh_clear()
assert any(sum((a-b)**2 for a,b in zip(p,q))>1e-6 for p,q in zip(poses[0],poses[3]))
bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_rotation=Quaternion((.8001,.5599,-.1222,-.1746));sp.region_3d.view_distance=3.0
            sp.region_3d.view_location=rig.matrix_world.translation+Vector((0,0,.9))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/report['output']),compress=True)
(O/'fit-report.json').write_text(json.dumps(report,indent=2));print('DEATH_SQUAD_TROUSERS_OK',report)
