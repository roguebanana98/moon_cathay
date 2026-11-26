"""Apply generated Chen shield atlas to a separate model05 preview."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-chen-shield';O.mkdir(parents=True,exist_ok=True)
OUT=O/'deer24-model05-neckguard06-chen-shield.blend'
atlas=O/'shield-chen-base-colour.png'
shutil.copy2(r'C:\Users\Admin\.codex\generated_images\01a2159c-d79e-7993-b80f-55fc081168a4\exec-ffa32b92-da9c-4817-b485-75bc3b9d1b40.png',atlas)
shutil.copy2(r'C:\Users\Admin\AppData\Local\Temp\codex-clipboard-cb20cd3b-dc4f-40ea-be16-419f920fd95d.png',O/'chen-calligraphy-reference.png')
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-neckguard/deer24-model05-neckguard06.blend'))
scene=bpy.context.scene
shield=next(o for o in scene.objects if o.type=='MESH' and 'shield' in o.get('source_geometry',''))
mat=shield.data.materials[0].copy();mat.name='Model05 | painted Chen shield';shield.data.materials[0]=mat
tree=mat.node_tree;bsdf=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
old=bsdf.inputs['Base Color'].links[0].from_socket
tex=tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(atlas));tex.image.pack();tex.label='陳 | user calligraphy in red'
# Restrict generated colour to the three circular front-face UV islands.
uv=tree.nodes.new('ShaderNodeTexCoord');sep=tree.nodes.new('ShaderNodeSeparateXYZ');tree.links.new(uv.outputs['UV'],sep.inputs[0])
def mathnode(op,a,b):
 n=tree.nodes.new('ShaderNodeMath');n.operation=op
 for i,v in enumerate([a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:tree.links.new(v,n.inputs[i])
 return n.outputs[0]
# Native shield front UV is rotated 180 degrees relative to its upright silhouette.
index=mathnode('ROUND',mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['X'],.166),.335),0)
centerx=mathnode('ADD',mathnode('MULTIPLY',index,.335),.166)
newx=mathnode('SUBTRACT',mathnode('MULTIPLY',centerx,2),sep.outputs['X'])
newy=mathnode('SUBTRACT',.572,sep.outputs['Y'])
combine=tree.nodes.new('ShaderNodeCombineXYZ');tree.links.new(newx,combine.inputs['X']);tree.links.new(newy,combine.inputs['Y']);tree.links.new(combine.outputs[0],tex.inputs['Vector'])
masks=[]
for cx in [.166,.501,.836]:
 sub=tree.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';tree.links.new(uv.outputs['UV'],sub.inputs[0]);sub.inputs[1].default_value=(cx,.286,0)
 scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';tree.links.new(sub.outputs[0],scale.inputs[0]);scale.inputs[1].default_value=(1,0.5,0)
 length=tree.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';tree.links.new(scale.outputs[0],length.inputs[0])
 less=tree.nodes.new('ShaderNodeMath');less.operation='LESS_THAN';tree.links.new(length.outputs['Value'],less.inputs[0]);less.inputs[1].default_value=.14;masks.append(less.outputs[0])
mask=masks[0]
for value in masks[1:]:
 add=tree.nodes.new('ShaderNodeMath');add.operation='MAXIMUM';tree.links.new(mask,add.inputs[0]);tree.links.new(value,add.inputs[1]);mask=add.outputs[0]
mix=tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';tree.links.new(mask,mix.inputs[0]);tree.links.new(old,mix.inputs[1]);tree.links.new(tex.outputs['Color'],mix.inputs[2]);tree.links.new(mix.outputs[0],bsdf.inputs['Base Color'])
# Suppress old faction emblem's surface relief/material pattern on painted wood.
for name,value in [('Metallic',0.0),('Roughness',.68)]:
 socket=bsdf.inputs[name];prior=socket.links[0].from_socket if socket.is_linked else None
 if prior:
  blend=tree.nodes.new('ShaderNodeMixRGB');tree.links.new(mask,blend.inputs[0]);tree.links.new(prior,blend.inputs[1]);blend.inputs[2].default_value=(value,value,value,1);tree.links.new(blend.outputs[0],socket)
normal=next((n for n in tree.nodes if n.type=='NORMAL_MAP'),None)
if normal:
 inv=tree.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;tree.links.new(mask,inv.inputs[1]);tree.links.new(inv.outputs[0],normal.inputs['Strength'])
target=Vector((0,0,1.12));cam=scene.camera;cam.location=(1.4,-3.8,1.8);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.85
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=target;sp.region_3d.view_distance=3.6;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.object.select_all(action='DESELECT');shield.select_set(True);bpy.context.view_layer.objects.active=shield
shield['shield_emblem']='陳, reference supplied by user; red painted preview'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'chen-shield-preview.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),texture=str(atlas),glyph='陳',tool='built-in image_gen',prompt='Replace three green shield-face maze emblems with red 陳 from user calligraphy; preserve UV atlas layout and surrounding parts.',outside_face_uses_original_material=True,geometry_unchanged=True,game_integrated=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('CHEN_SHIELD_READY',OUT)
