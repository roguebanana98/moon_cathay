"""Blender-only sword swap preview. Preserve source FBX and approved hero scene."""
import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-fantasy-longsword'
source=R/'build/huyen-ve-v16-approved/huyen-ve-v16-animation-review.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));rig=bpy.data.objects['humanoid01e_NATIVE_BIND']
old_swords=[o for o in bpy.data.objects if o.type=='MESH' and 'mc_huyen_ve_sword' in o.name]
for o in old_swords:o.hide_set(True);o.hide_render=True
with bpy.data.libraries.load(str(O/'source-review.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n.startswith('tripo_node_')]
assert len(dst.objects)==1
sword=dst.objects[0];bpy.context.scene.collection.objects.link(sword)
sword.name='HuyenVe_Fantasy_Longsword_PREVIEW';mesh=sword.data
pts=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get('co',pts.ravel())
world=np.array(sword.matrix_world);pts=pts@world[:3,:3].T+world[:3,3]
# FBX: blade points toward -Z; handle spans Z .735-.89. Match the old weapon_2
# grip centre and blade length using a single uniform scale, preserving proportions.
grip=np.array([-.00005,0,.815]);scale=1.2832832336425781/.815
v=(pts-grip)*scale
v=np.stack([v[:,2],v[:,0]-.0154,v[:,1]+.025],axis=1)
mesh.vertices.foreach_set('co',v.astype(np.float32).ravel());mesh.update()
sword.parent=None;sword.matrix_world=Matrix.Identity(4)
for c in list(sword.constraints):sword.constraints.remove(c)
c=sword.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget='weapon_2'
sword['preview_only']=True;sword['source_grip_xyz']=list(grip);sword['uniform_scale']=scale
# Explicit PBR links for the supplied 4K texture set.
folder=next((R/'assets/authored/fantasy longsword 3d model').glob('*.fbm'))
mat=bpy.data.materials.new('Fantasy_Longsword_User_PBR');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
out=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled');links.new(shader.outputs['BSDF'],out.inputs['Surface'])
for suffix,input_name in [('basecolor','Base Color'),('metallic','Metallic'),('roughness','Roughness'),('normal','Normal')]:
 path=next(p for p in folder.iterdir() if p.stem.endswith('_'+suffix))
 image=bpy.data.images.load(str(path),check_existing=True)
 if suffix!='basecolor':image.colorspace_settings.name='Non-Color'
 tex=nodes.new('ShaderNodeTexImage');tex.image=image
 if suffix=='normal':
  normal=nodes.new('ShaderNodeNormalMap');links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
 else:links.new(tex.outputs['Color'],shader.inputs[input_name])
sword.data.materials.clear();sword.data.materials.append(mat)
actions={}
for tag,token in [('stand','/stand/hu1e_dlc24_yuan_bo_sword_stand_01.anim'),('attack','sword_attack_01.anim'),('run','sword_run')]:
 choices=[a for a in bpy.data.actions if token in str(a.get('native_path',''))];assert choices,tag
 actions[tag]=choices[0]
rig.animation_data_create();rows=[]
for tag,action in actions.items():
 rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
 lo,hi=map(int,action.frame_range)
 for frame in sorted({lo,(lo+hi)//2,hi}):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
  actual=sword.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
  expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix
  error=max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4));assert error<1e-5
  rows.append(dict(clip=tag,frame=frame,attachment_error=error))
scene=bpy.context.scene;stand=actions['stand'];rig.animation_data.action=stand;rig.animation_data.action_slot=stand.slots[0]
scene.frame_start=int(stand.frame_range[0]);scene.frame_end=int(stand.frame_range[1]);scene.frame_set(scene.frame_start)
rig.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');sword.select_set(True);bpy.context.view_layer.objects.active=sword
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False
   space.region_3d.view_location=Vector((0,0,1.1));space.region_3d.view_distance=3.8
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file and Path(bpy.path.abspath(image.filepath)).is_file():image.pack()
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
camera=scene.camera;assert camera
camera.location=(3,-5,2.5);camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.4
scene.render.filepath=str(O/'huyen-ve-fantasy-sword-preview.png')
path=O/'huyen-ve-fantasy-sword-preview.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report=dict(status='blender_preview_ready',scene=str(path),source_scene_unchanged=True,original_sword_hidden_preserved=True,
 uniform_scale=scale,source_grip=list(grip),vertices=len(mesh.vertices),triangles=sum(len(p.vertices)-2 for p in mesh.polygons),
 attachment_checks=rows,clips={k:a.name for k,a in actions.items()},game_pack_changed=False,runtime_verified=False,
 note='Source geometry retained at full detail; grip/guard proportions require user visual approval before any export.')
(O/'preview-validation.json').write_text(json.dumps(report,indent=2))
bpy.ops.render.render(write_still=True)
