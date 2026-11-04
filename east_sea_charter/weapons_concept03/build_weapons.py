import bpy, math, os, json
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection' and c.users == 0: bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.cycles.use_denoising=True
scene.render.resolution_x=2200; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22)
scene.view_settings.view_transform='AgX'

def mat(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    return m
steel=mat('Steel | polished blade',(.48,.57,.64),.88,.24)
edge=mat('Steel | honed edge',(.75,.82,.85),.92,.2)
gold=mat('Brass | gilded bronze',(.56,.32,.075),.8,.3)
darkgold=mat('Bronze | recessed patina',(.17,.105,.039),.73,.48)
navy=mat('Indigo | enamel',(.014,.034,.075),.4,.32)
leather=mat('Indigo | leather',(.023,.039,.062),0,.72)
wood=mat('Blackwood',(.026,.017,.012),0,.38)
backwood=mat('Shield | rear timber',(.15,.075,.033),0,.65)
jade=mat('Jade | inset gems',(.035,.44,.28),.25,.23)
black=mat('Mouth | dark recess',(.012,.008,.006),0,.7)
cloth=mat('Indigo | staff ribbon',(.025,.075,.18),0,.85)
ground=mat('Backdrop',(.11,.13,.16),0,.85)
assets={}; active=None

def setup(name,x):
    global active
    coll=bpy.data.collections.new(name); scene.collection.children.link(coll)
    root=bpy.data.objects.new(name+' | ROOT',None); coll.objects.link(root); root.location=(x,0,0)
    root['purpose']='Editable concept mesh; metre scale. Grip/root not yet matched to vanilla skeleton.'
    assets[name]=(coll,root); active=name

def finish(o,name,m):
    o.name=name
    coll,root=assets[active]
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o); o.parent=root
    if m: o.data.materials.append(m)
    return o

def mesh(name,vs,fs,m,bevel=0):
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update()
    o=bpy.data.objects.new(name,me); scene.collection.objects.link(o); finish(o,name,m)
    if bevel:
        b=o.modifiers.new('Manufactured edge bevel','BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def sphere(name,p,s,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=p)
    o=bpy.context.object; o.scale=s; finish(o,name,m)
    for f in o.data.polygons: f.use_smooth=True
    return o

def cyl(name,p,r,d,m,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d,location=p)
    o=finish(bpy.context.object,name,m)
    b=o.modifiers.new('Rim bevel','BEVEL'); b.width=min(.002,r*.12); b.segments=2
    return o

def line(name,pts,r,m,sharp=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12
    cu.bevel_depth=r; cu.bevel_resolution=2
    if sharp:
        sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
        for b,p in zip(sp.points,pts):b.co=(*p,1)
    else:
        sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
        for b,p in zip(sp.bezier_points,pts): b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob); finish(ob,name,m); return ob

def prism(name,poly,depth,m):
    n=len(poly); vs=[(x,y,z) for y in [-depth/2,depth/2] for x,z in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,m,.002)

def torus(name,p,major,minor,m,rot=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=p,major_radius=major,minor_radius=minor)
    o=finish(bpy.context.object,name,m)
    if rot:o.rotation_euler=rot
    return o

def blade(name,z,length,width):
    # Four-sided diamond sections give real ridge and honed bevels on both faces.
    vs=[]
    for h,w,t in [(z,width,.008),(z+length*.78,width*.78,.006),(z+length*.94,width*.38,.003),(z+length,.0002,.0001)]:
        vs += [(-w/2,0,h),(0,-t,h),(w/2,0,h),(0,t,h)]
    fs=[(3,2,1,0)]
    for j in range(3):
        for i in range(4):fs.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
    fs.append((12,13,14,15)); o=mesh(name,vs,fs,steel)
    o.data.materials.append(edge)
    for i,f in enumerate(o.data.polygons):f.material_index=int(i%4 in (1,2))
    return o

def sword(prefix,z,blade_len,width,ornate=False):
    # Display point down; rotate complete assembly after construction.
    start=set(bpy.data.objects)
    blade(prefix+' | diamond blade',.24,blade_len,width)
    cyl(prefix+' | leather grip',(0,0,.125),.018,.18,leather)
    for k in range(12):
        torus(prefix+' | grip binding %02d'%k,(0,0,.045+k*.014),.018,.0017,gold if k in (0,11) else navy)
    cyl(prefix+' | grip collar',(0,0,.225),.024,.019,gold)
    sphere(prefix+' | pommel',(0,0,.012),(.034,.021,.033),gold)
    sphere(prefix+' | pommel jade',(0,-.02,.012),(.016,.006,.019),jade)
    poly=[(-.135,.245),(-.12,.27),(-.075,.256),(-.028,.253),(0,.28),(.028,.253),(.075,.256),(.12,.27),(.135,.245),(.12,.231),(.04,.238),(0,.205),(-.04,.238),(-.12,.231)]
    prism(prefix+' | crossguard',poly,.027,gold)
    if ornate:
        for side in (-1,1):
            for j in range(5):
                x=side*(.04+j*.018)
                p=[(x,-.019,.245),(x+side*.014,-.02,.233-j*.004),(x+side*.02,-.018,.252)]
                line(prefix+' | eagle guard feather',p,.003,darkgold)
        sphere(prefix+' | guard gem',(0,-.019,.248),(.014,.006,.017),jade)
    else:
        line(prefix+' | naga guard engraving',[(-.11,-.016,.247),(-.06,-.018,.249),(0,-.019,.23),(.06,-.018,.249),(.11,-.016,.247)],.0025,darkgold)
    # Transform actual vertices so object origins remain consistent at root.
    for o in set(bpy.data.objects)-start:
        o.location.z=z-o.location.z
        o.rotation_euler.y+=math.pi
    return

setup('EDH_Heinrich_Sword',-1.35)
sword('Heinrich',1.7,.91,.082,True)

setup('EDH_Heinrich_Shield',-.55)
outline=[(0,1.77),(.30,1.59),(.28,1.08),(.19,.80),(0,.58),(-.19,.80),(-.28,1.08),(-.30,1.59)]
centerz=1.25
def shield_y(x):return -.065+(.055*(abs(x)/.30)**2)
vs=[(0,-.068,centerz)]+[(x,shield_y(x),z) for x,z in outline]
vs += [(0,.025,centerz)]+[(x,shield_y(x)+.052,z) for x,z in outline]
fs=[]
for i in range(8):
    a=i+1;b=(i+1)%8+1;fs.extend([(0,b,a),(9,a+9,b+9),(a,b,b+9,a+9)])
mesh('Shield | convex enamel shell',vs,fs,navy,.003)
line('Shield | solid brass perimeter',[(x,shield_y(x)-.005,z) for x,z in outline+[outline[0]]],.014,gold,sharp=True)
for i,(x,z) in enumerate(outline):
    nx,nz=outline[(i+1)%8]
    for t in (.15,.4,.65,.9):
        xx=x*(1-t)+nx*t; zz=z*(1-t)+nz*t
        sphere('Shield | perimeter rivet',(xx,shield_y(xx)-.017,zz),(.006,.004,.006),gold)
# Raised eagle-on-rock emblem: layered feather geometry, visible in silhouette.
for s in (-1,1):
    for i in range(8):
        root=Vector((s*(.025+i*.001),1.31-i*.004))
        tip=Vector((s*(.215-i*.009),1.51-i*.034))
        axis=(tip-root).normalized(); perp=Vector((-axis.y,axis.x))*.012
        p=[tuple(root-perp),tuple(tip-perp*.15),tuple(tip+perp*.15),tuple(root+perp)]
        o=prism('Shield | eagle wing feather',p,.009,gold);o.location.y=-.087-i*.001
        line('Shield | feather quill',[(root.x,-.094-i*.001,root.y),(tip.x,-.094-i*.001,tip.y)],.0015,darkgold)
    for i in range(3):
        line('Shield | eagle talon',[(s*.025,-.085,1.19),(s*.04,-.085,1.15),(s*(.045+i*.008),-.085,1.145)],.004,gold)
sphere('Shield | eagle breast',(0,-.085,1.30),(.046,.015,.094),gold)
line('Shield | eagle neck',[(0,-.086,1.36),(.006,-.086,1.41),(.027,-.086,1.43)],.018,gold)
sphere('Shield | eagle head',(.024,-.086,1.435),(.022,.015,.02),gold)
o=prism('Shield | eagle beak',[(.03,1.445),(.06,1.434),(.033,1.425)],.018,gold);o.location.y=-.086
sphere('Shield | eagle eye',(.025,-.102,1.442),(.003,.002,.003),black)
for i in range(5):
    x=(i-2)*.014;o=prism('Shield | eagle tail',[(0,1.25),(x-.007,1.16),(x+.007,1.16)],.007,gold);o.location.y=-.085
for x,z,s in [(-.055,1.09,.05),(.025,1.08,.065),(0,1.13,.045)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=s,location=(x,-.08,z));o=finish(bpy.context.object,'Shield | heraldic rock',darkgold);o.scale.y=.25
# Sun at top.
sphere('Shield | sun disc',(0,-.08,1.62),(.033,.01,.033),gold)
for i in range(12):
    a=i*math.tau/12
    line('Shield | sun ray',[(math.sin(a)*.042,-.08,1.62+math.cos(a)*.042),(math.sin(a)*.061,-.08,1.62+math.cos(a)*.061)],.003,gold)
# Functional rear construction.
for x in [-.19,-.095,0,.095,.19]:
    line('Shield | timber rear rib',[(x,.035,1.02),(x,.035,1.53)],.032,backwood)
for z in [1.12,1.42]:
    line('Shield | rear cross brace',[(-.24,.07,z),(.24,.07,z)],.014,darkgold)
line('Shield | hand grip',[(-.095,.085,1.30),(-.095,.14,1.30),(.035,.14,1.30),(.035,.085,1.30)],.018,leather)
line('Shield | forearm strap',[(.08,.08,1.15),(.08,.18,1.22),(.08,.18,1.37),(.08,.08,1.43)],.023,leather)

setup('EDH_Sariwa_Naga_Staff',.25)
cyl('Staff | blackwood shaft',(0,0,1.0),.021,1.85,wood)
for z in [.10,.15,.60,.88,1.16,1.73,1.80]:
    cyl('Staff | engraved bronze ferrule',(0,0,z),.027,.035,gold)
    for dz in [-.012,.012]:torus('Staff | ferrule lip',(0,0,z+dz),.028,.0025,darkgold)
cyl('Staff | reinforced grip',(0,0,.98),.024,.25,leather)
for k in range(18):torus('Staff | grip braid',(0,0,.865+k*.013),.024,.0015,gold)
sphere('Staff | crown socket',(0,0,1.82),(.065,.04,.055),gold)
for idx,(x,z) in enumerate([(-.205,1.99),(-.115,2.095),(0,2.16),(.115,2.095),(.205,1.99)]):
    pts=[(0,0,1.81),(x*.60,.007,1.86),(x,.005,z-.10),(x,0,z-.025)]
    line('Naga %d | curved neck'%idx,pts,.019,gold)
    # Elliptical cobra hood, separate layered front inset.
    sphere('Naga %d | hood'%idx,(x,.008,z-.027),(.039,.019,.060),gold)
    sphere('Naga %d | hood inset'%idx,(x,-.01,z-.027),(.029,.006,.047),darkgold)
    sphere('Naga %d | head'%idx,(x,-.014,z+.011),(.025,.031,.023),gold)
    sphere('Naga %d | snout'%idx,(x,-.043,z+.004),(.022,.019,.011),gold)
    line('Naga %d | mouth slit'%idx,[(x-.017,-.052,z-.001),(x,-.059,z-.002),(x+.017,-.052,z-.001)],.002,black)
    for s in (-1,1):
        sphere('Naga %d | jade eye'%idx,(x+s*.02,-.031,z+.017),(.006,.007,.005),jade)
        for j in range(4):
            line('Naga %d | hood scale'%idx,[(x+s*.014,-.014,z-.064+j*.017),(x+s*.027,-.014,z-.05+j*.017)],.002,gold)
    for j in range(6):
        # Ventral bronze plates under each snake neck.
        p=Vector(pts[1]).lerp(Vector(pts[2]),j/6)
        line('Naga %d | neck ventral plate'%idx,[(p.x-.012,-.017,p.z),(p.x+.012,-.017,p.z)],.0025,darkgold)
for s in (-1,1):
    line('Staff | bell suspension',[(s*.06,0,1.81),(s*.09,0,1.72)],.003,gold)
    sphere('Staff | bronze bell',(s*.09,0,1.70),(.021,.021,.025),gold)
    sphere('Staff | bell opening',(s*.09,-.002,1.682),(.014,.016,.005),black)
    v=[(s*.065,-.008,1.78),(s*.085,-.008,1.78),(s*.105,-.013,1.52),(s*.08,-.012,1.54)]
    ribbon=mesh('Staff | blue textile ribbon',v,[(0,1,2,3)],cloth)
    mod=ribbon.modifiers.new('Ribbon thickness','SOLIDIFY');mod.thickness=.0015
torus('Staff | crown jade collar',(0,0,1.82),.05,.006,jade)

setup('EDH_Sariwa_Sword',.95)
sword('Sariwa',1.62,.72,.048,False)

setup('EDH_Sariwa_Scabbard',1.40)
prism('Scabbard | leather shell',[(-.03,1.39),(.03,1.39),(.026,.76),(0,.66),(-.026,.76)],.029,leather)
prism('Scabbard | bronze mouth',[(-.034,1.40),(.034,1.40),(.034,1.31),(-.034,1.31)],.035,gold)
prism('Scabbard | bronze chape',[(-.028,.83),(.028,.83),(.024,.75),(0,.665),(-.024,.75)],.033,gold)
for z in [1.37,1.34,.79,.76]:
    line('Scabbard | engraved chevron',[(-.021,-.020,z),(0,-.021,z-.014),(.021,-.020,z)],.002,darkgold)
for z in [1.30,1.12]:
    torus('Scabbard | belt suspension ring',(.044,0,z),.017,.004,gold,(math.pi/2,0,0))
    line('Scabbard | belt hanger',[(.045,0,z),(.080,.005,z+.10),(.115,.005,z+.10)],.008,leather)

# Convert construction curves and modifiers to editable, UV-unwrapped meshes.
stats={}
for name,(coll,root) in assets.items():
    objs=[o for o in coll.objects if o.type in {'MESH','CURVE'}]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs)
    stats[name]={'parts':len(objs),'triangles':tris,'uv':'UVMap smart unwrap; materials not baked'}
    # Each exported model is centred at its root, independent of display layout.
    x=root.location.x;root.location.x=0
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,name+'.glb'),use_selection=True,export_format='GLB',export_cameras=False,export_lights=False)
    root.location.x=x

stage=bpy.data.collections.new('PRESENTATION | cameras lights ground');scene.collection.children.link(stage)
def stage_obj(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    stage.objects.link(o)

bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));o=bpy.context.object;o.name='Studio floor';o.data.materials.append(ground);stage_obj(o)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((-3,-4,6),950,5),((4,-2,4),750,4),((0,3,5),1100,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1));stage_obj(o)
def camera(name,loc,target,scale):
    bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.data.type='ORTHO';o.data.ortho_scale=scale;aim(o,target);stage_obj(o);return o
front=camera('CAM | front orthographic',(0,-8,1.15),(0,0,1.15),3.75)
back=camera('CAM | rear orthographic',(0,8,1.15),(0,0,1.15),3.75)
beauty=camera('CAM | material inspection',(3.4,-8,3.6),(0,0,1.12),3.95)
scene.camera=front
scene.render.image_settings.file_format='PNG'
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_distance=4
        a.spaces.active.region_3d.view_location=(0,0,1.1)
        a.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'EDH_concept03_weapons.blend'))
with open(os.path.join(OUT,'mesh_inventory.json'),'w') as f:json.dump(stats,f,indent=2)
for cam,filename in [(front,'weapons_front.png'),(back,'weapons_back.png'),(beauty,'weapons_materials.png')]:
    scene.camera=cam;scene.render.filepath=os.path.join(OUT,filename);bpy.ops.render.render(write_still=True)
print('BUILD_COMPLETE',json.dumps(stats))
