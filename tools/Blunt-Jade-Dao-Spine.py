"""Keep a full-thickness, flat unsharpened spine on the custom dao."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-dao-flat-spine';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-dao-flat-thick-spine.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-dao-comparison/jade-model05-native-and-custom-dao-comparison.blend'))
scene=bpy.context.scene
targets=[bpy.data.objects['Jade Warrior | reference ring-pommel dao'],bpy.data.objects['CUSTOM | Reference dao | native thickness']]
mat=bpy.data.materials.new('Dao | flat unsharpened spine');mat.use_nodes=True
shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=(.32,.36,.40,1);shader.inputs['Metallic'].default_value=.8;shader.inputs['Roughness'].default_value=.39
half=.009443722665309906/2
for ob in targets:
 ob.data=ob.data.copy();me=ob.data
 # First 276 vertices are 46 six-point blade cross-sections from the source model.
 for k in range(46):
  s=.255-me.vertices[k*6].co.x
  tip=max(.012,min(1,(.84-s)/.09))
  thickness=half*tip
  for j in [0,1,4,5]:me.vertices[k*6+j].co.z=thickness*([1,.92,-.92,-1][[0,1,4,5].index(j)])
  # Keep only the cutting edge thin; spine top and bottom remain far apart.
  me.vertices[k*6+2].co.z=.00005;me.vertices[k*6+3].co.z=-.00005
 spine_index=len(me.materials);me.materials.append(mat)
 for p in me.polygons:
  if all(i<276 for i in p.vertices) and len(p.vertices)==4 and {i%6 for i in p.vertices}=={0,5}:
   p.material_index=spine_index;p.use_smooth=False
 me.update();ob['spine']='Flat unsharpened back, full native thickness until the final tip transition'
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');targets[1].select_set(True);bpy.context.view_layer.objects.active=targets[1]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'flat-spine-comparison.png');bpy.ops.render.render(write_still=True)
# Angled isolated detail of the actual finished blade's thick spine.
from mathutils import Vector
dao=targets[1]
for ob in scene.objects:
 if ob.type in ['MESH','FONT']:ob.hide_render=ob!=dao
dao.constraints.clear();dao.matrix_basis.identity()
target=Vector((.03,.01036,0));cam=scene.camera;cam.location=(.03,.95,1.25);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.38
scene.render.resolution_x=1600;scene.render.resolution_y=500;scene.render.filepath=str(O/'dao-flat-spine-detail.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),flat_spine_thickness_m=half*2,full_thickness_until_blade_distance_m=.75,cutting_edge_sharp=True,original_native_dao_unchanged=True,held_and_comparison_dao_updated=True,game_integrated=False),indent=2))
print('FLAT_SPINE_READY',OUT,flush=True)
