import bpy
from pathlib import Path
R=Path.cwd();O=R/'build/celestial-concubines-dual-knives';bpy.ops.wm.open_mainfile(filepath=str(O/'celestial-concubine-01-closed-chest-outfit.blend'))
ob=bpy.data.objects['Outer shirt | continuous closed chest'];mat=bpy.data.objects['IronWarriors_01'].data.materials[0].copy();mat.name='Outer shirt | matching original cloth';ob.data.materials.clear();ob.data.materials.append(mat)
# Reuse a plain cloth area from the original outfit atlas, inside its red border.
uv=ob.data.uv_layers.active
for p in ob.data.polygons:
 for i in p.loop_indices:
  co=ob.data.vertices[ob.data.loops[i].vertex_index].co
  uv.data[i].uv=(.53+min(1,max(0,(co.x+.185)/.37))*.13,.06+min(1,max(0,(co.z-1.105)/.31))*.05)
for p in ob.data.polygons:p.material_index=0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'celestial-concubine-01-closed-chest-textured.blend'),compress=True)
