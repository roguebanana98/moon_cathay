"""A subtle, reversible skin-material tint in the native Blender scene."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SOURCE=R/'build/da-lien-collar-edit/da-lien-collar-removed.blend'
O=R/'build/da-lien-skin-warm';O.mkdir(parents=True,exist_ok=True)
DEST=O/'da-lien-skin-warm.blend'
assert not DEST.exists(),'Preserve an existing edited scene'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
def mesh_sig(obj):
    m=obj.data
    data=[[(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in m.vertices],
          [tuple(p.vertices) for p in m.polygons],
          [[tuple(x.uv) for x in uv.data] for uv in m.uv_layers],
          [tuple(n.vector) for n in m.corner_normals],
          [tuple(row) for row in obj.matrix_world]]
    return hashlib.sha256(repr(data).encode()).hexdigest()
mesh_before={o.name:mesh_sig(o) for o in bpy.data.objects if o.type=='MESH'}
other_slots={o.name:[s.material.name if s.material else None for s in o.material_slots]
             for o in bpy.data.objects if o.type=='MESH' and o.name!='Neferata_Body'}
body=bpy.data.objects['Neferata_Body'];assert len(body.material_slots)==1
original=body.material_slots[0].material
material=original.copy();material.name='Da Lien | Warm Human Skin'
body.data.materials[0]=material
tree=material.node_tree
bsdf=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
base=bsdf.inputs['Base Color'];assert len(base.links)==1
source_socket=base.links[0].from_socket
tint=tree.nodes.new('ShaderNodeMixRGB');tint.name='DL_Subtle_Human_Skin';tint.label='Subtle warm rose skin - reversible'
tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1.0
# Linear-light multiplication: warm the pale diffuse gently; keep texture detail.
tint.inputs[2].default_value=(0.98,0.85,0.80,1.0)
tint.location=(bsdf.location.x-220,bsdf.location.y+220)
tree.links.new(source_socket,tint.inputs[1]);tree.links.new(tint.outputs[0],base)
material['da_lien_skin_tint']='Slightly warm/rosy human skin; source images unchanged'
assert mesh_before=={o.name:mesh_sig(o) for o in bpy.data.objects if o.type=='MESH'}
assert all([s.material.name if s.material else None for s in bpy.data.objects[name].material_slots]==slots for name,slots in other_slots.items())
assert len(bpy.data.objects['Neferata_Outfit_Sleeves_Collar'].data.vertices)==29387,'Preserve removed collar'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
report={'source_scene':str(SOURCE),'output_scene':str(DEST),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'edited_object':body.name,
 'original_material':original.name,'edited_material':material.name,'linear_rgb_multiplier':[0.98,0.85,0.80],
 'method':'Native Blender shader tint; source/packed texture pixels not changed',
 'geometry_uv_normals_weights_unchanged':True,'other_mesh_materials_unchanged':True,
 'collar_removal_preserved':True,'game_pack_changed':False,'runtime_verified':False}
(O/'skin-warm-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
