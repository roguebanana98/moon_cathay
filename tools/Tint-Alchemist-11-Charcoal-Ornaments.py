"""Reversible charcoal tint of gold garment ornament; preserve skin and face mask."""
import bpy,json
from pathlib import Path
O=Path('D:/Warhammer3_Modding/moon_cathay/build/alchemist-11-no-back-cape')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-charcoal-ornaments-live.blend'),copy=True)
changed=[]
for ob in bpy.data.objects['VARIANT 11'].children_recursive:
    if ob.type!='MESH' or ob.hide_get():continue
    for slot in ob.material_slots:
        original=slot.material
        if not original or not original.use_nodes:continue
        tex=next((n for n in original.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'cth_alchemist_body_01_base_colour' in n.image.name),None)
        if not tex:continue
        mat=original.copy();mat.name='CHARCOAL ORNAMENT | '+original.name;slot.material=mat
        nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and 'cth_alchemist_body_01_base_colour' in n.image.name)
        def calc(op,a,b):
            n=nt.nodes.new('ShaderNodeMath');n.operation=op
            for i,x in enumerate((a,b)):
                if isinstance(x,(float,int)):n.inputs[i].default_value=x
                else:nt.links.new(x,n.inputs[i])
            return n.outputs[0]
        hsv=nt.nodes.new('ShaderNodeSeparateColor');hsv.mode='HSV';nt.links.new(tex.outputs['Color'],hsv.inputs[0])
        mask=calc('MULTIPLY',calc('GREATER_THAN',hsv.outputs[0],.055),calc('LESS_THAN',hsv.outputs[0],.19))
        mask=calc('MULTIPLY',mask,calc('GREATER_THAN',hsv.outputs[1],.18))
        mask=calc('MULTIPLY',mask,calc('GREATER_THAN',hsv.outputs[2],.045))
        if ob.data.attributes.get('preview_preserve_hands'):
            attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name='preview_preserve_hands'
            mask=calc('MULTIPLY',mask,calc('SUBTRACT',1,attr.outputs['Fac']))
        bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],bw.inputs[0])
        dark=calc('MULTIPLY',bw.outputs[0],.095)
        base=bsdf.inputs['Base Color'];old=base.links[0].from_socket
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.label='Gold embroidery to near-black charcoal'
        nt.links.new(mask,mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(dark,mix.inputs[2]);nt.links.new(mix.outputs[0],base)
        for name,value in [('Metallic',.12),('Roughness',.7)]:
            socket=bsdf.inputs[name];previous=socket.links[0].from_socket if socket.is_linked else socket.default_value
            result=calc('ADD',calc('MULTIPLY',previous,calc('SUBTRACT',1,mask)),calc('MULTIPLY',mask,value))
            nt.links.new(result,socket)
        changed.append({'object':ob.name,'material':mat.name})
assert changed
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-charcoal-ornaments.blend'),compress=True)
(O/'charcoal-ornaments-report.json').write_text(json.dumps({'changes':changed,'face_mask_unchanged':True,'geometry_modified':False,'texture_pixels_modified':False},indent=2))
print('CHARCOAL_ORNAMENTS_OK')
