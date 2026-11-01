"""Authored concept-03 sword prototype. Run with portable Blender --background --python."""
import bpy
import json
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/authored/moon-warden/concept03-v1'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metal=0, rough=.4):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m

steel=material('Pale silver steel',(.56,.62,.69),.92,.26)
silver=material('Engraved silver fittings',(.38,.43,.49),.87,.3)
gold=material('Warm fine metal inlay',(.42,.30,.13),.8,.32)
leather=material('Navy wrapped grip',(.013,.026,.045),0,.65)
gem=material('Muted moonstone',(.12,.28,.30),.35,.2)
parts=[]

def mesh(name, verts, faces, mat):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat); parts.append(o)
    return o

def bevel(o,width=.0008):
    mod=o.modifiers.new('Small edge bevel','BEVEL'); mod.width=width; mod.segments=2
    return o

def orb(name,location,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=location)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    parts.append(o); return o

def cylinder(name, location, radius, depth, mat, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat); parts.append(o)
    return bevel(o)

def line(name, points, radius, mat):
    data=bpy.data.curves.new(name,'CURVE'); data.dimensions='3D'; data.bevel_depth=radius; data.bevel_resolution=2
    s=data.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.data.materials.append(mat); parts.append(o)
    return o

# Blade extends down -Z from guard origin; the grip center remains the model origin.
ring_specs=[(-.105,.023,.0045),(-.14,.023,.0042),(-.74,.019,.0035),(-.88,.011,.0025),(-.96,0,.0001)]
verts=[]
for z,w,t in ring_specs:verts.extend([(-w,0,z),(0,-t,z),(w,0,z),(0,t,z)])
faces=[(3,2,1,0)]
for i in range(len(ring_specs)-1):
    for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
faces.append(tuple(range(16,20)))
mesh('Double edged tapered diamond blade',verts,faces,steel)

cylinder('Navy leather grip',(0,0,.005),.0145,.184,leather)
for z in [-.091,.099]:cylinder('Silver grip collar',(0,0,z),.017,.012,silver)
for direction in [-1,1]:
    points=[]
    for i in range(257):
        t=i/256; a=direction*t*math.pi*2*8
        points.append((.0148*math.cos(a),.0148*math.sin(a),-.082+t*.174))
    line('Crossed silver grip bindings',points,.00075,gold)

# Curled guard branches shaped in the broad plane of the blade.
for side in [-1,1]:
    points=[]
    for i in range(41):
        t=i/40
        points.append((side*(.016+.078*t),0,-.093+.013*math.sin(t*math.pi*1.25)))
    line('Upturned lotus guard branch',points,.0065,silver)
    orb('Guard tip',(side*.094,0,-.102),(.008,.008,.008),silver)

def petal(name, cx, cz, angle, length, width, mat, y=-.008):
    # Convex lens-shaped leaf: center ridge and four outline points, front/back thickness.
    local=[(0,0),(width*.6,length*.38),(0,length),(-width*.6,length*.38)]
    def transform(x,z,yy):
        return (cx+x*math.cos(angle)+z*math.sin(angle), yy, cz-x*math.sin(angle)+z*math.cos(angle))
    v=[transform(x,z,y) for x,z in local]+[transform(0,length*.4,y-.005)]+[transform(x,z,y+.005) for x,z in local]
    f=[(i,(i+1)%4,4) for i in range(4)]+[(5,8,7,6)]+[(i,5+i,5+(i+1)%4,(i+1)%4) for i in range(4)]
    return bevel(mesh(name,v,f,mat),.0005)

for side in [-1,1]:
    for angle in [-.9,-.45,0,.45,.9]:petal('Lotus guard petal',0,-.112,angle,.047,.014,silver,y=side*.010)
    orb('Moonstone on lotus guard',(0,side*.016,-.084),(.011,.004,.011),gem)
    # Restrained decorative lines on upper blade, not a texture painted plane.
    for sign in [-1,1]:
        points=[(sign*(.004+.002*math.sin(i*.22)),side*.0047,-.15-i*.004) for i in range(55)]
        line('Blade silver scroll inlay',points,.00045,gold)

orb('Lotus pommel core',(0,0,.126),(.019,.013,.022),silver)
for a in [-.7,0,.7]:petal('Lotus pommel petal',0,.108,a,.043,.012,silver,y=-.007)
orb('Pommel moonstone',(0,-.014,.126),(.009,.003,.011),gem)

# Make all geometry exportable and add UVs. This is an editable prototype, not yet RMV2.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.convert(target='MESH')
parts=list(bpy.context.selected_objects)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=.015); bpy.ops.object.mode_set(mode='OBJECT')
for o in parts:o['asset_role']='separate_static_sword';o['concept']='approved 03'
bpy.ops.export_scene.gltf(filepath=str(OUT/'moon-warden-lotus-sword-v1.glb'),export_format='GLB',use_selection=True)

scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=900; scene.render.resolution_y=1300; scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Sword preview world');scene.world.color=(.22,.22,.22)
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((-.8,-1.2,.3),180,1.1),((.8,-.3,-.3),130,.8),((0,.7,.2),200,1)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,-.35))
bpy.ops.object.camera_add(location=(.15,-2,-.28)); cam=bpy.context.object; aim(cam,(0,0,-.40));cam.data.type='ORTHO';cam.data.ortho_scale=1.24;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'moon-warden-lotus-sword-v1-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'moon-warden-lotus-sword-v1.blend'))
bpy.ops.render.render(write_still=True)
report=dict(asset='Concept03 lotus sword prototype',date='2026-11-02',mesh_objects=len(parts),triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in parts),rigged=False,rmv2_exported=False,game_tested=False,notes='Authored geometry; grip center origin. Must align to donor weapon_2 before game export.')
(OUT/'sword-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
