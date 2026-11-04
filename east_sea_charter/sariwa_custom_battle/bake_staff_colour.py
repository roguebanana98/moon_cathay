import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'sariwa_damsel02/Sariwa_Damsel02_Naga3_v2.blend'))
staff=next(o for o in bpy.data.objects if o.type=='MESH' and 'Sariwa | weapon_5' in o.name)
bpy.ops.object.select_all(action='DESELECT');staff.select_set(True);bpy.context.view_layer.objects.active=staff
im=bpy.data.images.new('Staff private albedo',width=1024,height=1024,alpha=False);im.colorspace_settings.name='sRGB'
for mat in staff.data.materials:
    nodes=mat.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    emit=nodes.new('ShaderNodeEmission');emit.inputs['Strength'].default_value=1
    if bs.inputs['Base Color'].links:mat.node_tree.links.new(bs.inputs['Base Color'].links[0].from_socket,emit.inputs['Color'])
    else:emit.inputs['Color'].default_value=bs.inputs['Base Color'].default_value
    mat.node_tree.links.new(emit.outputs[0],out.inputs['Surface']);target=nodes.new('ShaderNodeTexImage');target.image=im;nodes.active=target
bpy.context.scene.cycles.samples=1;bpy.ops.object.bake(type='EMIT',margin=3,use_clear=True)
im.filepath_raw=str(R/'export/tex/edh_sariwa_staff_base_colour.png');im.file_format='PNG';im.save()
print('STAFF_ALBEDO_READY')
