"""Reference-inspired ring-pommel dao for the current editable Jade Warrior."""
import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-reference-dao';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-round-chen-shield-reference-dao.blend'
SOURCE=R/'build/deer-jade-model05-round-shield/deer24-model05-round-chen-shield.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
old=next(o for o in scene.objects if o.type=='MESH' and 'sword' in o.get('source_geometry',''))
arm=old.constraints[0].target;basis=old.matrix_basis.copy()
col=bpy.data.collections.new('EDIT | Reference ring-pommel dao');scene.collection.children.link(col)
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
 return m
steel=material('Dao | satin silver steel',(.48,.52,.57),.82,.31)
edge=material('Dao | polished cutting bevel',(.65,.69,.73),.85,.23)
iron=material('Dao | dark iron fittings',(.065,.073,.082),.8,.36)
wood=material('Dao | reddish brown wood grip',(.15,.043,.022),0,.53)
tree=wood.node_tree;shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
tex=tree.nodes.new('ShaderNodeTexCoord');scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(3,100,100);tree.links.new(tex.outputs['Object'],scale.inputs[0])
noise=tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=2;tree.links.new(scale.outputs[0],noise.inputs['Vector'])
ramp=tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.055,.014,.008,1);ramp.color_ramp.elements[1].color=(.24,.085,.042,1);tree.links.new(noise.outputs['Fac'],ramp.inputs[0]);tree.links.new(ramp.outputs[0],shader.inputs['Base Color'])
parts=[]
def mesh(name,vs,fs,mats,indices=None,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob)
 for m in mats:me.materials.append(m)
 for i,p in enumerate(me.polygons):p.use_smooth=smooth;p.material_index=indices[i] if indices else 0
 parts.append(ob);return ob
# Cross sections follow the reference silhouette: straight narrow root,
# gradual widening, fuller forward third and a swept, tapered point.
# X is the native sword axis. The native grip centre stays x=.3723063.
guard=.255;cy=.010363951
sections=[(0,.019,-.018),(.12,.020,-.020),(.28,.021,-.025),(.44,.021,-.035),(.56,.019,-.049),(.65,.012,-.063),(.72,-.003,-.070),(.775,-.024,-.071),(.815,-.045,-.067),(.84,-.061,-.0615)]
knots=sections;sections=[]
for i in range(len(knots)-1):
 a=knots[max(0,i-1)];b=knots[i];c=knots[i+1];d=knots[min(len(knots)-1,i+2)]
 for j in range(5):
  t=j/5;row=[b[0]+(c[0]-b[0])*t]
  for axis in [1,2]:
   m0=(c[axis]-a[axis])/(c[0]-a[0]);m1=(d[axis]-b[axis])/(d[0]-b[0]);dx=c[0]-b[0]
   row.append((2*t**3-3*t*t+1)*b[axis]+(t**3-2*t*t+t)*dx*m0+(-2*t**3+3*t*t)*c[axis]+(t**3-t*t)*dx*m1)
  sections.append(row)
sections.append(knots[-1])
vs=[]
for s,spine,cut in sections:
 thickness=.0035*(1-.60*s/.84)*min(1,(.841-s)/.024)
 bevel=min(.013,(spine-cut)*.38)
 # Six points around a thin single-edged blade: spine, face, edge, face.
 for y,z in [(spine,thickness),(cut+bevel,thickness*.72),(cut,.00005),(cut,-.00005),(cut+bevel,-thickness*.72),(spine,-thickness)]:vs.append((guard-s,cy+y,z))
fs=[];mi=[]
for i in range(len(sections)-1):
 for j in range(6):fs.append((i*6+j,(i+1)*6+j,(i+1)*6+(j+1)%6,i*6+(j+1)%6));mi.append(1 if j in [1,2,3] else 0)
fs.extend([tuple(range(5,-1,-1)),tuple((len(sections)-1)*6+j for j in range(6))]);mi.extend([0,0])
blade=mesh('Dao | long gently curved blade',vs,fs,[steel,edge],mi)
def cylinder(name,start,end,ry,rz,mat,n=32):
 vs=[(x,cy+ry*math.cos(i*2*math.pi/n),rz*math.sin(i*2*math.pi/n)) for x in [start,end] for i in range(n)]
 fs=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(n-1,-1,-1)),tuple(n+i for i in range(n))]
 return mesh(name,vs,fs,[mat],smooth=True)
cylinder('Dao | compact oval disc guard',guard-.004,guard+.007,.040,.027,iron)
cylinder('Dao | blade-root ferrule',guard-.017,guard-.004,.022,.0075,iron)
cylinder('Dao | long wood handle',guard+.008,.590,.0145,.0125,wood)
cylinder('Dao | guard-side grip collar',guard+.007,guard+.023,.0157,.0137,iron)
cylinder('Dao | pommel collar',.578,.601,.0158,.0138,iron)
# Ring lies in the blade plane, with a solid junction into the wooden grip.
ringx=.624;major=.025;minor=.0055;n=48;m=12
vs=[]
for i in range(n):
 a=i*2*math.pi/n
 for j in range(m):
  b=j*2*math.pi/m;rr=major+minor*math.cos(b);vs.append((ringx+rr*math.cos(a),cy+rr*math.sin(a),minor*math.sin(b)))
fs=[(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m) for i in range(n) for j in range(m)]
mesh('Dao | open ring pommel',vs,fs,[iron],smooth=True)
# Join into one rigid prop; keep the imported weapon pivot and native attachment.
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=blade;bpy.ops.object.join();dao=blade;dao.name='Jade Warrior | reference ring-pommel dao';dao.matrix_basis=basis
for original in old.constraints:
 con=dao.constraints.new(original.type)
 con.target=original.target;con.subtarget=original.subtarget;con.inverse_matrix=original.inverse_matrix.copy()
dao['reference']='User photo: long plain curved blade, small dark guard, long brown grip and open ring pommel'
dao['preview_only']=True
old.hide_render=True;old.hide_set(True);old.name='SOURCE | original Jade sword | preserved hidden'
scene.frame_set(1);bpy.context.view_layer.update()
# Verify the imported native pivot and point inside the wooden grip coincide.
native_frame=arm.matrix_world@arm.pose.bones['weapon_2'].matrix
grip_local=Vector((.372306287,.010363951,0))
grip_error=((dao.matrix_world@grip_local)-native_frame.translation).length
assert grip_error<1e-5,grip_error
assert all(math.isfinite(c) for v in dao.data.vertices for c in v.co)
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
# Main preview at the same angle as the approved shield scene.
bpy.ops.object.select_all(action='DESELECT');dao.select_set(True);bpy.context.view_layer.objects.active=dao
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'jade-reference-dao-preview.png');bpy.ops.render.render(write_still=True)
# Isolated profile render uses the same mesh. Temporary studio only, not saved.
for ob in scene.objects:
 if ob.type in ['MESH','FONT']:ob.hide_render=ob!=dao
dao.constraints.clear();dao.matrix_basis.identity()
cam=scene.camera;target=Vector((.03,cy,0));cam.location=(.03,cy,3);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.38
scene.render.resolution_x=1600;scene.render.resolution_y=460
scene.render.filepath=str(O/'dao-profile.png');bpy.ops.render.render(write_still=True)
reference=Path(r'C:\Users\Admin\AppData\Local\Temp\codex-clipboard-8b27ba88-4aa1-4b3b-a82e-6a0b9b61a24d.png')
if reference.exists():shutil.copy2(reference,O/'user-dao-reference.png')
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),reference='user-dao-reference.png',blade_length_m=.84,wood_grip_length_m=.327,overall_length_m=1.24,native_pivot_retained=True,native_grip_center_error=grip_error,body_shield_neckguard_unchanged=True,original_sword_preserved_hidden=True,game_integrated=False,animation_runtime_tested=False),indent=2))
print('REFERENCE_DAO_READY',OUT,flush=True)
