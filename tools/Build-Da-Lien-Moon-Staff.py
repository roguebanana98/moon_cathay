"""Replace the goblet head with an authored silver crescent, preserving the staff shaft."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];O=R/'build/da-lien-moon-staff'
SOURCE=R/'build/da-lien-skin-warm/da-lien-skin-warm.blend';DEST=O/'da-lien-moon-staff.blend'
assert not DEST.exists(),'Protect an existing edited scene'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
staff=bpy.data.objects['Neferata_Staff'];me=staff.data
def mesh_sig(obj):
    m=obj.data
    return hashlib.sha256(repr([[(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in m.vertices],
        [tuple(p.vertices) for p in m.polygons],[[tuple(x.uv) for x in uv.data] for uv in m.uv_layers],
        [tuple(n.vector) for n in m.corner_normals],[tuple(row) for row in obj.matrix_world],
        [s.material.name if s.material else None for s in obj.material_slots]]).encode()).hexdigest()
other_before={o.name:mesh_sig(o) for o in bpy.data.objects if o.type=='MESH' and o!=staff}
groups=json.loads((O/'staff-islands.json').read_text())['groups']
head=[g for g in groups if g['min'][0]<-1.20]
remove={i for g in head for i in g['vertex_ids']}
assert remove and len(remove)<len(me.vertices)*.8
old_coords=[tuple(v.co) for v in me.vertices]
old_normals=[tuple(n.vector) for n in me.corner_normals]
old_uvs={uv.name:[tuple(x.uv) for x in uv.data] for uv in me.uv_layers}
old_faces=[tuple(p.vertices) for p in me.polygons]
assert all(all(i in remove for i in f) or not any(i in remove for i in f) for f in old_faces)
expected=[f for f in old_faces if not any(i in remove for i in f)]
before={'vertices':len(me.vertices),'faces':len(me.polygons)}
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
vi=bm.verts.layers.int.new('dl_staff_original_vertex');li=bm.loops.layers.int.new('dl_staff_original_loop')
for v in bm.verts:v[vi]=v.index
for f in bm.faces:
    for loop,idx in zip(f.loops,me.polygons[f.index].loop_indices):loop[li]=idx
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v[vi] in remove],context='VERTS')
bm.to_mesh(me);bm.free();me.update()
vm=[x.value for x in me.attributes['dl_staff_original_vertex'].data]
lm=[x.value for x in me.attributes['dl_staff_original_loop'].data]
assert set(vm)==set(range(len(old_coords)))-remove
assert all(tuple(v.co)==old_coords[vm[v.index]] for v in me.vertices)
assert [tuple(vm[i] for i in p.vertices) for p in me.polygons]==expected
for uv in me.uv_layers:assert all(tuple(x.uv)==old_uvs[uv.name][lm[i]] for i,x in enumerate(uv.data))
normal_error=max(abs(n.vector[a]-old_normals[lm[i]][a]) for i,n in enumerate(me.corner_normals) for a in range(3))
assert normal_error==0,normal_error
me.attributes.remove(me.attributes['dl_staff_original_vertex']);me.attributes.remove(me.attributes['dl_staff_original_loop'])
staff['da_lien_staff_edit']='Original goblet assembly removed; original shaft and tassel retained'
collection=bpy.data.collections.new('Da Lien - Moon Staff Head');bpy.context.scene.collection.children.link(collection)
def mat(name,color,metallic,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
    return m
silver=mat('Da Lien | Moon Silver',(.63,.72,.79),.80,.26)
gold=mat('Da Lien | Moon Gold Rim',(.64,.39,.12),.78,.26)
enamel=mat('Da Lien | Staff Wine Enamel',(.16,.012,.025),.25,.26)
def attach(obj):
    for col in list(obj.users_collection):col.objects.unlink(obj)
    collection.objects.link(obj)
    c=obj.constraints.new('COPY_TRANSFORMS');c.target=staff.constraints[0].target;c.subtarget=staff.constraints[0].subtarget
    # All new head vertices are authored in the original prop's local coordinates.
    obj['native_attachment']='be_prop_5'
def bevel(obj,amount=.003):
    m=obj.modifiers.new('Soft gold edge','BEVEL');m.width=amount;m.segments=3;m.material=1
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=m.name);obj.select_set(False)
# Upturned crescent in the local X/Z plane; -X is the staff's upper end.
outer=.20;inner=.18;offset=.07;center=-1.64;depth=.032
inter=(outer*outer-inner*inner+offset*offset)/(2*offset)
alpha=math.asin(inter/outer);beta=math.asin((inter-offset)/inner)
n=64
outline=[]
for i in range(n+1):
    t=alpha+(-math.pi-2*alpha)*i/n
    outline.append((outer*math.cos(t),outer*math.sin(t)))
for i in range(1,n):
    t=(math.pi-beta)+(math.pi+2*beta)*i/n
    outline.append((inner*math.cos(t),offset+inner*math.sin(t)))
verts=[]
for y in (-depth/2,depth/2):
    verts.extend([(center-v,y,h) for h,v in outline])
count=len(outline);planar=[Vector((x,z,0)) for x,z in outline]
tris=tessellate_polygon([planar]);lookup={tuple(p):i for i,p in enumerate(planar)}
faces=[];mats=[]
for tri in tris:
    ids=[p if isinstance(p,int) else lookup[tuple(p)] for p in tri]
    faces.append(tuple(reversed(ids)));mats.append(0)
    faces.append(tuple(i+count for i in ids));mats.append(0)
for i in range(count):faces.append((i,(i+1)%count,(i+1)%count+count,i+count));mats.append(1)
mesh=bpy.data.meshes.new('Da Lien Authored Crescent');mesh.from_pydata(verts,[],faces);mesh.update()
# Recalculate outward normals on the closed solid before beveling.
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
moon=bpy.data.objects.new('Da_Lien_Moon_Crescent',mesh);collection.objects.link(moon)
mesh.materials.append(silver);mesh.materials.append(gold)
for p,idx in zip(mesh.polygons,mats):p.material_index=idx
uv=mesh.uv_layers.new(name='Moon_Planar_UV')
for loop in mesh.loops:
    co=mesh.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((co.z+outer)/(outer*2),(-(co.x-center)+outer)/(outer*2))
bpy.ops.object.select_all(action='DESELECT');bevel(moon,.003);attach(moon)
def cone(name,x,depth,r1,r2,material):
    bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=r1,radius2=r2,depth=depth,location=(x,0,0),rotation=(0,math.pi/2,0))
    ob=bpy.context.object;ob.name=name;ob.data.materials.append(material);ob.data.materials.append(gold)
    # Bake placement into mesh while retaining the exact shared native bone transform.
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bevel(ob,.002);attach(ob)
    return ob
cone('Da_Lien_Moon_Neck',-1.305,.27,.020,.029,enamel)
cone('Da_Lien_Moon_Lower_Clasp',-1.188,.035,.031,.031,gold)
cone('Da_Lien_Moon_Upper_Clasp',-1.432,.032,.028,.024,gold)
bpy.context.view_layer.update()
for ob in collection.objects:
    if ob.type=='MESH':
        bm=bmesh.new();bm.from_mesh(ob.data)
        assert not any(not e.is_manifold for e in bm.edges),(ob.name,'Non-manifold new head')
        bm.free()
assert all(mesh_sig(bpy.data.objects[name])==sig for name,sig in other_before.items()),'Another model part/material changed'
assert len(bpy.data.objects['Neferata_Outfit_Sleeves_Collar'].data.vertices)==29387
assert bpy.data.objects['Neferata_Body'].data.materials[0].node_tree.nodes.get('DL_Subtle_Human_Skin')
bpy.ops.object.select_all(action='DESELECT');moon.select_set(True);bpy.context.view_layer.objects.active=moon
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.overlay.show_overlays=False;sp.shading.type='MATERIAL'
            sp.region_3d.view_location=(.1,0,1.18);sp.region_3d.view_distance=3.4
            sp.region_3d.view_rotation=Vector((0,-1,.10)).to_track_quat('Z','Y');sp.region_3d.view_perspective='ORTHO'
report={'source_scene':str(SOURCE),'output_scene':str(DEST),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'old_staff_before':before,'old_staff_after':{'vertices':len(me.vertices),'faces':len(me.polygons)},
 'removed_goblet_vertices':len(remove),'removed_islands':[g['id'] for g in head],
 'retained_shaft_coordinates_uv_normals_faces_exact':True,'other_meshes_materials_unchanged':other_before,
 'new_objects':[o.name for o in collection.objects],'design':'Upturned silver crescent with gold bevel, wine enamel neck and gold clasps',
 'crescent_width':2*math.sqrt(outer*outer-inter*inter),'native_attachment':'be_prop_5',
 'skin_tint_and_collar_removal_preserved':True,'game_pack_changed':False,'runtime_verified':False}
bpy.ops.wm.save_as_mainfile(filepath=str(DEST));report['output_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest()
(O/'moon-staff-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='other_meshes_materials_unchanged'},indent=2))
