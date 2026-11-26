"""Keep current warrior and add a same-scale native/new sword comparison."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-dao-comparison';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-native-and-custom-dao-comparison.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-dao-native-thickness/jade-model05-dao-native-thickness.blend'))
scene=bpy.context.scene;dao=bpy.data.objects['Jade Warrior | reference ring-pommel dao']
native=next(o for o in scene.objects if o.type=='MESH' and o.get('source_geometry','').endswith('/cth_jade_warrior_sword_1h_01.rigid_model_v2'))
col=bpy.data.collections.new('COMPARE | Native and custom dao | same scale');scene.collection.children.link(col)
# Display broad sides towards -Y, with blade tips up. Grip centres align in Z.
rotation=Matrix.Rotation(math.pi/2,4,'X')@Matrix.Rotation(math.pi/2,4,'Z')
rotation=Matrix.Rotation(math.pi,4,'Y')@rotation
copies=[]
for source,x,name in [(native,1.03,'ORIGINAL | Jade Warrior native dao'),(dao,1.46,'CUSTOM | Reference dao | native thickness')]:
 ob=source.copy();ob.data=source.data.copy();ob.animation_data_clear();ob.parent=None;ob.constraints.clear();col.objects.link(ob)
 ob.name=name;ob.hide_render=False;ob.hide_set(False)
 # Explicit orientation: local -X points up; local Y points right; Z faces viewer.
 orientation=Matrix(((0,1,0,0),(0,0,1,0),(-1,0,0,0),(0,0,0,1)))
 grip=Vector((.372306287,.010363951,0));anchor=Vector((x,-.05,.55))
 ob.matrix_world=Matrix.Translation(anchor)@orientation@Matrix.Translation(-grip)
 ob['comparison_scale']=1.0;copies.append(ob)
mat=bpy.data.materials.new('Comparison captions');mat.use_nodes=True;s=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in s.inputs:s.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in s.inputs:s.inputs['Emission Strength'].default_value=.7
for text,x in [('ORIGINAL',1.03),('CUSTOM',1.46)]:
 cv=bpy.data.curves.new(text,'FONT');cv.body=text;cv.size=.065;cv.align_x='CENTER';cv.materials.append(mat)
 ob=bpy.data.objects.new(text,cv);col.objects.link(ob);ob.location=(x,-.11,.13);ob.rotation_euler=(math.pi/2,0,0)
target=Vector((.53,0,1.03));cam=scene.camera;cam.location=(.53,-5.5,1.30);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.60
scene.render.resolution_x=1500;scene.render.resolution_y=1250
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=target;sp.region_3d.view_distance=4.5;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.object.select_all(action='DESELECT');copies[0].select_set(True);bpy.context.view_layer.objects.active=copies[0]
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'native-custom-dao-comparison.png');bpy.ops.render.render(write_still=True)
(O/'comparison-report.json').write_text(json.dumps(dict(scene=str(OUT),original= copies[0].name,custom=copies[1].name,same_scale=True,grip_centres_aligned=True,character_and_held_weapon_unchanged=True,game_integrated=False),indent=2))
print('COMPARISON_READY',OUT,flush=True)
