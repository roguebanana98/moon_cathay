import os, math
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE/'v2'
OUT.mkdir(exist_ok=True)
source=(BASE/'build_weapons.py').read_text()
source=source.replace("OUT = os.path.dirname(os.path.abspath(__file__))", "OUT = "+repr(str(OUT)))
prefix=source.split('# Convert construction curves')[0]
exec(compile(prefix, str(BASE/'build_weapons.py'),'exec'))

def remove_matching(coll, labels):
    for ob in list(assets[coll][0].objects):
        if any(label in ob.name for label in labels): bpy.data.objects.remove(ob,do_unlink=True)

def leaf(name,a,b,width,depth,material):
    # Curved lenticular relief with a raised central ridge, tapered tip and closed back.
    a,b=Vector(a),Vector(b); axis=b-a; n=Vector((-axis.z,0,axis.x)).normalized()
    vertices=[]; count=12
    for j in range(count+1):
        t=j/count; c=a+axis*t
        w=width*(math.sin(math.pi*t)**.8)
        vertices.extend([tuple(c-n*w),tuple(c+Vector((0,-depth*math.sin(math.pi*t),0))),tuple(c+n*w)])
    faces=[]
    for j in range(count):
        k=j*3
        faces.extend([(k,k+3,k+4,k+1),(k+1,k+4,k+5,k+2),(k+2,k+5,k+3,k)])
    ob=mesh(name,vertices,faces,material)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def scroll(name,x,y,z,sx,sz,material=gold):
    for side in [-1,1]:
        pts=[]
        for j in range(48):
            t=j/47; ang=t*math.pi*2*1.25; r=1-t*.84
            pts.append((x+side*sx*(.45+r*.55*math.cos(ang)),y,z+sz*(t-.45)+sz*.22*r*math.sin(ang)))
        line(name,pts,.0012,material)

# Replace stick-like feathers with overlapping broad, domed feather layers.
active='EDH_Heinrich_Shield'
remove_matching(active,['eagle wing feather','feather quill','eagle breast','eagle tail','sun ray'])
for s in [-1,1]:
    for i in range(10):
        a=(s*(.027+i*.005),-.091,1.30+i*.012)
        b=(s*(.155+i*.010),-.092,1.27+i*.026)
        leaf('Shield | primary flight feather',a,b,.012,.004,gold)
        line('Shield | fine feather rachis',[a,b],.00065,darkgold)
    for row in range(3):
        for i in range(7):
            x=s*(.035+i*.022); z=1.325+i*.022-row*.017
            leaf('Shield | overlapping wing covert',(x,-.101-row*.002,z),(x+s*.037,-.101-row*.002,z+.029),.010,.004,gold)
    for i in range(3):
        leaf('Shield | tail plume',(s*.008,-.095,1.26),(s*(.012+i*.015),-.095,1.165+i*.007),.009,.003,gold)
sphere('Shield | sculpted eagle torso',(0,-.094,1.32),(.034,.018,.071),gold)
for row in range(7):
    for col in range(3):
        x=(col-1)*.016;z=1.27+row*.014
        leaf('Shield | breast plumage',(x,-.112,z+.017),(x,-.112,z),.008,.002,gold)
for i in range(16):
    ang=i*math.tau/16
    a=(math.sin(ang)*.036,-.085,1.62+math.cos(ang)*.036)
    b=(math.sin(ang)*(.075 if i%2==0 else .058),-.085,1.62+math.cos(ang)*(.075 if i%2==0 else .058))
    leaf('Shield | pointed solar ray',a,b,.005,.002,gold)
# Inset border and restrained star field.
line('Shield | inner gold pinstripe',[(x*.945,shield_y(x*.945)-.006,1.22+(z-1.22)*.955) for x,z in outline+[outline[0]]],.002,gold,True)
for s in [-1,1]:
    for i in range(5):
        x=s*(.12+i*.025);z=1.55-i*.052
        for dx,dz in [(.004,0),(0,.004)]:
            line('Shield | enamel star',[(x-dx,shield_y(x)-.008,z-dz),(x+dx,shield_y(x)-.008,z+dz)],.0008,gold)
    line('Shield | lower vine',[(s*.012,-.074,.70),(s*.035,-.074,.80),(s*.065,-.074,.91),(s*.09,-.074,1.02)],.002,gold)
    for i in range(5):
        z=.78+i*.043;x=s*(.025+i*.012)
        leaf('Shield | vine leaf',(x,-.076,z),(x+s*.025,-.076,z+.028),.007,.002,gold)
scroll('Shield | lower filigree',0,-.08,.91,.036,.18)

# Finer sword fittings: curved guards, layered acanthus leaves and blade inlay.
for active,top,ornate in [('EDH_Heinrich_Sword',1.7,True),('EDH_Sariwa_Sword',1.62,False)]:
    remove_matching(active,['crossguard','eagle guard feather','naga guard engraving','grip binding'])
    z=top-.245
    for side in [-1,1]:
        line('Sword | swept guard',[(side*.014,0,z),(side*.050,0,z+.006),(side*.09,0,z+.016),(side*.126,0,z+.005)],.009,gold)
        sphere('Sword | guard terminal',(side*.126,0,z+.005),(.010,.009,.011),gold)
        for i in range(4):
            x=side*(.030+i*.022)
            leaf('Sword | acanthus guard relief',(x,-.010,z),(x+side*.018,-.010,z+.021),.006,.003,gold)
        leaf('Sword | langet',(side*.018,-.009,z+.01),(0,-.009,z-.07),.012,.004,gold)
        line('Sword | blade hairline inlay',[(side*(.007+.002*math.sin(i*.16)),-.0085, z-.08-i*.004) for i in range(48)],.00055,gold)
    sphere('Sword | guard bezel',(0,-.014,z+.005),(.020,.006,.022),darkgold)
    sphere('Sword | inset jade',(0,-.020,z+.005),(.012,.003,.014),jade)
    for direction in [-1,1]:
        pts=[]
        for i in range(220):
            t=i/219;a=direction*t*math.tau*9
            pts.append((.0183*math.cos(a),.0183*math.sin(a),top-.208+t*.162))
        line('Sword | crossed fine grip wire',pts,.00065,gold)
    for side in [-1,1]:
        leaf('Sword | pommel crown',(side*.02,-.006,top-.025),(side*.025,-.006,top+.020),.008,.003,gold)

# Scabbard uses continuous engraved panels instead of thick chevrons.
active='EDH_Sariwa_Scabbard'
remove_matching(active,['engraved chevron','belt hanger'])
for z in [1.355,.775]:scroll('Scabbard | chased scroll',0,-.020,z,.022,.065,darkgold)
for s in [-1,1]:
    line('Scabbard | edge piping',[(s*.023,-.017,1.30),(s*.021,-.017,.84)],.0012,gold)
    for i in range(7):
        leaf('Scabbard | floral inlay',(0,-.018,.86+i*.058),(s*.012,-.018,.881+i*.058),.003,.001,gold)
for z in [1.30,1.12]:
    prism('Scabbard | suspension tab',[(.026,z+.014),(.051,z+.014),(.051,z-.014),(.026,z-.014)],.024,gold)

# Turn the outer serpents outward to echo the spreading naga crown.
active='EDH_Sariwa_Naga_Staff'
for idx,(x,z) in enumerate([(-.205,1.99),(-.115,2.095),(0,2.16),(.115,2.095),(.205,1.99)]):
    from mathutils import Matrix
    angle={0:-.65,1:-.4,2:0,3:.4,4:.65}[idx]
    pivot=Vector((x,0,z-.07)); rot=Matrix.Rotation(angle,4,'Y')
    for o in list(assets[active][0].objects):
        if o.name.startswith('Naga %d |'%idx) and not any(k in o.name for k in ['curved neck','ventral']):
            o.matrix_basis=Matrix.Translation(pivot)@rot@Matrix.Translation(-pivot)@o.matrix_basis
    for j in range(4):
        leaf('Staff | crown scale',(x,-.023,z-.055+j*.014),(x,-.023,z-.035+j*.014),.007,.002,gold)
remove_matching(active,['crown jade collar','bell suspension','bronze bell','bell opening'])
for i in range(8):
    a=i*math.tau/8
    leaf('Staff | lotus socket petal',(.035*math.cos(a),.025*math.sin(a),1.79),(.060*math.cos(a),.04*math.sin(a),1.85),.013,.003,gold)

# Use deeper patinated metal and tighter highlight lighting.
gold.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.43,.245,.065,1)
gold.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.34
scene.cycles.samples=32
tail=source[source.index('# Convert construction curves'):]
tail=tail.replace("[(front,'weapons_front.png'),(back,'weapons_back.png'),(beauty,'weapons_materials.png')]","[(front,'weapons_front.png')]")
exec(compile(tail,str(BASE/'build_weapons.py'),'exec'))
