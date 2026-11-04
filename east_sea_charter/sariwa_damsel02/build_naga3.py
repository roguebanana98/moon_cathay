import bpy,bmesh,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Sariwa_Damsel02_Textile_v1.blend'))
scene=bpy.context.scene;scene.frame_set(1)
staff=next(o for o in bpy.data.objects if o.type=='MESH' and 'Sariwa | weapon_5' in o.name)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith('Sariwa'))
def digest(obj):
    return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in obj.data.vertices)).hexdigest()
protected={o.name:digest(o) for o in bpy.data.objects if o.type=='MESH' and o!=staff}
original_grip=sorted(tuple(v.co) for v in staff.data.vertices if v.co.x>-.89)
source_vertex_count=len(staff.data.vertices)
bm=bmesh.new();bm.from_mesh(staff.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
    plane_co=Vector((-.895,0,0)),plane_no=Vector((1,0,0)),clear_inner=True,clear_outer=False)
bm.to_mesh(staff.data);bm.free();staff.data.update()
assert sorted(tuple(v.co) for v in staff.data.vertices if v.co.x>-.89)==original_grip
staff['head_replaced']='Native orb removed above local x=-0.895; lower shaft and grip unchanged'
up=Vector((-1,0,0));origin=Vector((-.895,0,0))
front=staff.matrix_world.to_3x3().inverted()@Vector((0,-1,0));front-=up*front.dot(up);front.normalize()
right=up.cross(front).normalized()
def local(p):return origin+right*p[0]+front*p[1]+up*p[2]
def mat(name,color,metal=.0,rough=.4,glow=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if glow:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=glow
    return m
bronze=mat('Naga | aged bronze',(.30,.16,.055),.78,.33)
gold=mat('Naga | polished bronze ridges',(.56,.34,.11),.82,.28)
patina=mat('Naga | deep green patina',(.025,.105,.075),.55,.48)
dark=mat('Naga | mouth recess',(.018,.013,.008),.3,.55)
jade=mat('Naga | luminous jade eyes',(.025,.58,.30),.2,.2,1.8)
fang=mat('Naga | ivory fang inlay',(.63,.57,.36),.35,.3)
parts=[]
def finish(obj,name,material):
    obj.name=name;obj.data.materials.append(material);parts.append(obj)
    if obj.type=='MESH':
        for poly in obj.data.polygons:poly.use_smooth=True
    return obj
def ellipsoid(name,p,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(0,0,0))
    o=bpy.context.object
    for v in o.data.vertices:v.co=local((p[0]+v.co.x*scale[0],p[1]+v.co.y*scale[1],p[2]+v.co.z*scale[2]))
    return finish(o,name,material)
def line(name,pts,radius,material):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=5;cu.bevel_depth=radius;cu.bevel_resolution=1
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for bp,p in zip(sp.bezier_points,pts):bp.co=local(p);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);return finish(o,name,material)
def ring(name,h,r,wire,material):
    pts=[(r*math.cos(a*math.tau/24),r*math.sin(a*math.tau/24),h) for a in range(25)]
    return line(name,pts,wire,material)
ellipsoid('Naga | socket',(0,0,.014),(.038,.028,.035),bronze)
for h in [0,.021,.04]:ring('Naga | collar moulding',h,.027,.003,gold)
ring('Naga | jade collar',.024,.031,.0028,jade)
hood_outline=[(0,.081),(.022,.059),(.046,.030),(.048,.002),(.035,-.035),(.017,-.061),(0,-.073),(-.017,-.061),(-.035,-.035),(-.048,.002),(-.046,.030),(-.022,.059)]
for index,(u,h,lean) in enumerate([(-.145,.235,-.23),(0,.300,0),(.145,.235,.23)],1):
    # Each hood and face have a local frame, fanned away from the central head.
    def p(x,v,z):
        return (u+x*math.cos(lean)+z*math.sin(lean),v,h-x*math.sin(lean)+z*math.cos(lean))
    line(f'Naga {index} | rising neck',[(0,0,.015),(u*.32,-.004,.065),(u*.82,-.008,h-.105),p(0,-.004,-.045)],.016,bronze)
    # Convex cast cobra hood, closed shell with a raised central spine.
    verts=[local(p(0,.014,-.005))]+[local(p(x,.002,z)) for x,z in hood_outline]
    verts += [local(p(0,-.014,-.005))]+[local(p(x,-.010,z)) for x,z in hood_outline]
    n=len(hood_outline);back=n+1;faces=[]
    for i in range(n):
        a=i+1;b=(i+1)%n+1;faces.extend([(0,a,b),(back,b+back,a+back),(a,a+back,b+back,b)])
    me=bpy.data.meshes.new(f'Naga {index} hood');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(f'Naga {index} | flared cobra hood',me);scene.collection.objects.link(ob);finish(ob,ob.name,bronze)
    line(f'Naga {index} | hood border',[p(x,.009,z) for x,z in hood_outline+[hood_outline[0]]],.0025,gold)
    for sign in [-1,1]:
        for j in range(4):
            z=-.043+j*.017
            line(f'Naga {index} | engraved hood scale',[p(sign*.011,.016,z-.007),p(sign*.030,.014,z),p(sign*.040,.010,z+.010)],.0015,patina)
    # Angular snake skull and a projecting, flattened snout rather than round faces.
    skull=[]
    for depth,width,top,bottom in [(.004,.019,.042,.012),(.032,.027,.050,.013),(.078,.017,.033,.017)]:
        for x,z in [(-width,bottom),(-width,top-.009),(-width*.5,top),(width*.5,top),(width,top-.009),(width,bottom),(width*.5,bottom-.003),(-width*.5,bottom-.003)]:
            skull.append(local(p(x,depth,z)))
    faces=[tuple(range(7,-1,-1)),tuple(range(16,24))]
    for j in range(2):
        for k in range(8):faces.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
    me=bpy.data.meshes.new(f'Naga {index} snake skull');me.from_pydata(skull,[],faces);me.update()
    ob=bpy.data.objects.new(f'Naga {index} | tapered serpent skull',me);scene.collection.objects.link(ob);finish(ob,ob.name,bronze)
    bevel=ob.modifiers.new('Soft cast edges','BEVEL');bevel.width=.002;bevel.segments=2
    ellipsoid(f'Naga {index} | lower jaw',p(0,.045,.007),(.016,.033,.004),bronze)
    line(f'Naga {index} | mouth cleft',[p(-.016,.077,.014),p(0,.081,.013),p(.016,.077,.014)],.0013,dark)
    for sign in [-1,1]:
        ellipsoid(f'Naga {index} | jade eye',p(sign*.025,.035,.040),(.0038,.006,.0028),jade)
        line(f'Naga {index} | brow',[p(sign*.020,.025,.047),p(sign*.027,.034,.045),p(sign*.022,.048,.038)],.0017,gold)
        line(f'Naga {index} | short fang',[p(sign*.011,.065,.014),p(sign*.011,.068,.007)],.0011,fang)
    line(f'Naga {index} | forehead crest',[p(0,.009,.045),p(0,.018,.057),p(0,.037,.050)],.0025,gold)
    for sign in [-1,1]:ellipsoid(f'Naga {index} | nostril',p(sign*.007,.079,.028),(.002,.001,.001),dark)
    # Ventral plates follow the visible lower neck.
    for j in range(5):
        t=(j+1)/6;cx=u*.82*t;cz=.055+(h-.15)*t
        line(f'Naga {index} | neck plate',[(cx-.010,.014,cz),(cx,.017,cz-.002),(cx+.010,.014,cz)],.0017,gold)
# Convert sculptural construction pieces into one editable, UV-mapped prop mesh.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
bpy.ops.object.join();crown=bpy.context.object;crown.name='Sariwa | Naga three-head crown'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
crown.parent=staff;crown.matrix_parent_inverse=Matrix.Identity(4);crown.matrix_basis=Matrix.Identity(4)
crown['native_attachment']='be_prop_5 via unchanged staff parent';crown['heads']=3
crown['design']='Bronze three-headed Naga, central head raised, jade eyes, patina scale engravings'
assert protected=={o.name:digest(o) for o in bpy.data.objects if o.type=='MESH' and o not in (staff,crown)}
# Verify the new crown follows the existing prop bone at several test rotations.
bone=rig.pose.bones['be_prop_5'];mode=bone.rotation_mode;q=bone.rotation_quaternion.copy()
bone.rotation_mode='QUATERNION';positions=[];errors=[]
for angle in [0,.25,-.25]:
    bone.rotation_quaternion=q@Quaternion((0,0,1),angle);bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();a=crown.evaluated_get(dg).matrix_world;b=staff.evaluated_get(dg).matrix_world
    errors.append(max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)));positions.append(tuple(a@origin))
bone.rotation_quaternion=q;bone.rotation_mode=mode;bpy.context.view_layer.update()
assert max(errors)<1e-5 and positions[1]!=positions[2]
scene['staff_design']='Naga 3 heads; original shaft, grip and be_prop_5 constraint retained'
scene['scope']='Blender model update only; game pack not deployed'
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=scene.camera;cam.data.ortho_scale=3.15
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.region_3d.view_distance=3.55;s.overlay.show_overlays=False
bpy.ops.object.select_all(action='DESELECT')
path=R/'Sariwa_Damsel02_Naga3_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
report={'blend':str(path),'naga_heads':3,'crown_vertices':len(crown.data.vertices),'crown_triangles':sum(len(p.vertices)-2 for p in crown.data.polygons),
    'native_staff_vertices_before':source_vertex_count,'lower_shaft_and_grip_unchanged':True,'other_meshes_unchanged':True,
    'native_constraint_bone':staff.constraints[0].subtarget,'attachment_test_max_error':max(errors),'eyes':'6 jade eyes',
    'uv_unwrapped':bool(crown.data.uv_layers),'game_deployed':False}
(R/'naga3_report.json').write_text(json.dumps(report,indent=2))
scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1600
scene.render.filepath=str(R/'Sariwa_Naga3_full_v2.png');bpy.ops.render.render(write_still=True)
target=staff.matrix_world@local((0,.015,.18))
cam.location=target+Vector((.22,-1.5,.12));aim(cam,target);cam.data.ortho_scale=.49
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.filepath=str(R/'Sariwa_Naga3_detail_v2.png');bpy.ops.render.render(write_still=True)
print('NAGA3_READY',json.dumps(report),flush=True)
