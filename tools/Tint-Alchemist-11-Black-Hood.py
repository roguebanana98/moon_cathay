"""Reversible fabric tint on the live model's separate hood mesh only."""
import bpy,json
from pathlib import Path
O=Path('D:/Warhammer3_Modding/moon_cathay/build/alchemist-11-no-back-cape')
ob=bpy.data.objects['def_Khanite_assassin_head_02_sub']
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-black-hood-live.blend'),copy=True)
changes=[]
for slot in ob.material_slots:
    original=slot.material;mat=original.copy();mat.name='Model 11 | Black hood cloth';slot.material=mat
    nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    base=bsdf.inputs['Base Color'];source=base.links[0].from_socket if base.is_linked else None
    tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
    tint.label='Black hood tint - retain original fabric detail';tint.inputs[2].default_value=(.025,.025,.025,1)
    if source:nt.links.new(source,tint.inputs[1])
    else:tint.inputs[1].default_value=base.default_value
    nt.links.new(tint.outputs[0],base)
    for name,value in [('Metallic',0),('Roughness',.82)]:
        for link in list(bsdf.inputs[name].links):nt.links.remove(link)
        bsdf.inputs[name].default_value=value
    changes.append({'original':original.name,'new':mat.name})
ob['hood_colour']='Black matte fabric; original textures and normals retained, mask/face untouched.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-black-hood.blend'),compress=True)
(O/'black-hood-report.json').write_text(json.dumps({'object':ob.name,'materials':changes,'geometry_modified':False,'texture_pixels_modified':False},indent=2))
print('BLACK_HOOD_OK')
