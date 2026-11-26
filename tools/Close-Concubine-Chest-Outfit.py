"""Add a continuous fitted outer shirt front across both chest openings."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';SOURCE=O/'celestial-concubine-01-no-gold-ornaments.blend';OUT=O/'celestial-concubine-01-closed-chest-outfit.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));body=bpy.data.objects['Iron_Body'];me=body.data
keep=set()
for p in me.polygons:
 c=p.center
 if 1.105<c.z<1.415 and abs(c.x)<.185 and c.y<-.015 and p.normal.y<.15:keep.update(p.vertices)
# Retain only the selected front faces, including the exact original weights/UV.
panel=body.copy();panel.data=me.copy();panel.name='Outer shirt | continuous closed chest'
for col in body.users_collection:col.objects.link(panel)
bm=bmesh.new();bm.from_mesh(panel.data);bm.faces.ensure_lookup_table()
remove=[f for f in bm.faces if not (1.105<f.calc_center_median().z<1.415 and abs(f.calc_center_median().x)<.185 and f.calc_center_median().y<-.015 and f.normal.y<.15)]
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(panel.data);bm.free();panel.data.update()
for v in panel.data.vertices:v.co+=v.normal*.0015
panel.data.materials.clear();mat=bpy.data.materials.new('Outer shirt | woven charcoal');mat.use_nodes=True;mat.diffuse_color=(.032,.035,.04,1)
nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.84;bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.2
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;noise.inputs['Detail'].default_value=3
mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.017,.019,.023,1);mix.inputs[2].default_value=(.045,.048,.055,1);nt.links.new(noise.outputs['Fac'],mix.inputs[0]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00025;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
panel.data.materials.append(mat)
for p in panel.data.polygons:p.material_index=0;p.use_smooth=True
panel.hide_set(False);panel.hide_render=False
scene=bpy.context.scene;scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,0,1.13);sp.region_3d.view_distance=2.4
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'closed-chest.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),outer_shirt=panel.name,faces=len(panel.data.polygons),native_weights_preserved=True,game_modified=False),indent=2))
print('CLOSED_CHEST_READY',len(panel.data.polygons),flush=True)
