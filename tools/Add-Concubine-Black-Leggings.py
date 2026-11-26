"""Opaque fitted black leg fabric on existing skin surface, preserving rig/shape."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';SOURCE=O/'celestial-concubine-01-dual-knives-grip-fixed.blend';OUT=O/'celestial-concubine-01-black-leggings.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));body=bpy.data.objects['Iron_Body'];rig=bpy.data.objects['Body_01_native_humanoid01e']
backup=body.copy();backup.data=body.data.copy();backup.name='BACKUP | Original exposed leg skin';bpy.context.scene.collection.objects.link(backup);backup.hide_set(True);backup.hide_render=True
body.data=body.data.copy()
mat=bpy.data.materials.new('Black fitted leg fabric');mat.use_nodes=True;mat.diffuse_color=(.008,.009,.012,1)
nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.006,.007,.01,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.88
bs.inputs['Specular IOR Level'].default_value=.22
tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=240;tex.inputs['Detail'].default_value=2
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00035;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
index=len(body.data.materials);body.data.materials.append(mat);changed=[]
for face in body.data.polygons:
 # Waist edge stays concealed beneath the existing corset and hip armour.
 if max(body.data.vertices[i].co.z for i in face.vertices)<1.055:
  face.material_index=index;changed.append(face.index)
assert changed
body['leg_cover']='Black fitted opaque fabric from hidden waist edge into existing leg armour; native skin surface and bone weights preserved.'
scene=bpy.context.scene;scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,0,.95);sp.region_3d.view_distance=2.8;sp.region_3d.view_rotation=Vector((-.5,8,-.3)).to_track_quat('-Z','Y');sp.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'black-leggings.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),fabric_faces=len(changed),geometry_unchanged=True,weights_unchanged=True,knives_unchanged=True,original_skin_backup=backup.name,game_modified=False),indent=2))
print('BLACK_LEGGINGS_READY',len(changed),flush=True)
