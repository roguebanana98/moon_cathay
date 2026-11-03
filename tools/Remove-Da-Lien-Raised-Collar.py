"""Remove only the raised rear-collar assembly from a preserved live scene copy."""
import bpy,bmesh,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/da-lien-collar-edit'
SOURCE=O/'da-lien-before-collar-edit-live.blend';DEST=O/'da-lien-collar-removed.blend'
assert not DEST.exists(),'Protect user-edited output'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
target=bpy.data.objects['Neferata_Outfit_Sleeves_Collar'];me=target.data
assert not me.shape_keys,'Do not discard shape keys'
islands=json.loads((O/'collar-islands.json').read_text())['groups']
# Visually identified collar shell, lining, gold trim and attached decoration.
# The necklace/choker and both sleeves are separate islands and are retained.
approved={32737,29387,40477,40207,42019,37399,37787,38175,39043,39431,39819,36919,38563,37161,38805}
parts=[g for g in islands if g['id'] in approved]
assert len(parts)==len(approved)
assert all(g['min'][2]>1.30 and g['max'][2]>1.50 for g in parts)
remove=set(i for g in parts for i in g['vertex_ids'])
def vertex_sig(v):
    return (tuple(v.co),tuple((g.group,g.weight) for g in v.groups))
def mesh_sig(obj):
    m=obj.data
    content=[[(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in m.vertices],
             [tuple(p.vertices) for p in m.polygons],
             [[tuple(x.uv) for x in uv.data] for uv in m.uv_layers],
             [tuple(n.vector) for n in m.corner_normals],
             [list(row) for row in obj.matrix_world],
             [(a.name,a.type) for a in obj.modifiers],
             [s.material.name if s.material else None for s in obj.material_slots]]
    return hashlib.sha256(repr(content).encode()).hexdigest()
others={o.name:mesh_sig(o) for o in bpy.data.objects if o.type=='MESH' and o!=target}
rigs={o.name:([ (b.name,tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in o.data.bones],
               [(p.name,[tuple(row) for row in p.matrix_basis]) for p in o.pose.bones]) for o in bpy.data.objects if o.type=='ARMATURE'}
old_vertices=[vertex_sig(v) for v in me.vertices]
old_uvs={uv.name:[tuple(x.uv) for x in uv.data] for uv in me.uv_layers}
old_normals=[tuple(n.vector) for n in me.corner_normals]
old_faces=[tuple(p.vertices) for p in me.polygons]
expected_faces=[f for f in old_faces if not any(i in remove for i in f)]
assert all(all(i in remove for i in f) or not any(i in remove for i in f) for f in old_faces),'Selection crosses retained geometry'
before={'vertices':len(me.vertices),'faces':len(me.polygons)}
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
vi=bm.verts.layers.int.new('dl_original_vertex');li=bm.loops.layers.int.new('dl_original_loop')
for v in bm.verts:v[vi]=v.index
for face in bm.faces:
    for loop,idx in zip(face.loops,me.polygons[face.index].loop_indices):loop[li]=idx
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v[vi] in remove],context='VERTS')
bm.to_mesh(me);bm.free();me.update()
vm=[x.value for x in me.attributes['dl_original_vertex'].data]
lm=[x.value for x in me.attributes['dl_original_loop'].data]
assert set(vm)==set(range(len(old_vertices)))-remove
assert all(vertex_sig(v)==old_vertices[vm[v.index]] for v in me.vertices),'Retained coordinates or skin weights changed'
assert [tuple(vm[i] for i in p.vertices) for p in me.polygons]==expected_faces,'Retained faces/order changed'
for uv in me.uv_layers:
    assert all(tuple(x.uv)==old_uvs[uv.name][lm[i]] for i,x in enumerate(uv.data)),'Retained UV changed'
normal_error=max(abs(n.vector[a]-old_normals[lm[i]][a]) for i,n in enumerate(me.corner_normals) for a in range(3))
if normal_error>2e-6:
    me.normals_split_custom_set([old_normals[i] for i in lm]);me.update()
    normal_error=max(abs(n.vector[a]-old_normals[lm[i]][a]) for i,n in enumerate(me.corner_normals) for a in range(3))
# Blender re-encodes custom split normals; tolerate only sub-millithreshold rounding.
assert normal_error<0.001,normal_error
me.attributes.remove(me.attributes['dl_original_vertex']);me.attributes.remove(me.attributes['dl_original_loop'])
assert all(mesh_sig(bpy.data.objects[name])==sig for name,sig in others.items()),'Another mesh changed'
for name,(bones,poses) in rigs.items():
    rig=bpy.data.objects[name]
    assert bones==[(b.name,tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in rig.data.bones]
    assert poses==[(p.name,[tuple(row) for row in p.matrix_basis]) for p in rig.pose.bones]
me['da_lien_collar_edit']='Raised rear collar shell, lining, trim and attached decoration removed; sleeves/choker preserved'
bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type=='CONSOLE':area.type='VIEW_3D'
        if area.type=='VIEW_3D':
            sp=next((s for s in area.spaces if s.type=='VIEW_3D'),None)
            if sp is None:continue
            sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=(0,0,1.0);sp.region_3d.view_distance=2.8
            sp.region_3d.view_rotation=Vector((0,-1,.12)).to_track_quat('Z','Y');sp.region_3d.view_perspective='ORTHO'
report={'source_scene':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'output_scene':str(DEST),'target':target.name,'removed_islands':sorted(approved),
 'before':before,'after':{'vertices':len(me.vertices),'faces':len(me.polygons)},
 'removed_vertices':len(remove),'removed_faces':before['faces']-len(me.polygons),
 'retained_coordinates_weights_uv_faces_verified':True,'retained_normals_max_error':normal_error,
 'other_meshes_unchanged':others,'rig_bones_and_pose_unchanged':True,
 'game_pack_changed':False,'runtime_verified':False}
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report['output_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest()
(O/'collar-removal-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='other_meshes_unchanged'},indent=2))
