import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Endo_Damsel_All_4_Variants.blend'))
changed=[]
for obj in bpy.data.objects:
    if obj.type!='MESH' or ' | body | ' not in obj.name:continue
    for mat in obj.data.materials:
        nodes=mat.node_tree.nodes
        base=next(n for n in nodes if n.type=='TEX_IMAGE' and n.name=='BaseColour')
        shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        mat.node_tree.links.new(base.outputs['Color'],shader.inputs['Base Color'])
        mat['preview_colour_mode']='Original base-colour texture, no faction tint'
        changed.append(mat.name)
scene=bpy.context.scene
scene['preview_colour_mode']='Original white clothing textures; faction tint bypassed on body materials only.'
path=R/'Endo_Damsel_White_Outfits.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print('WHITE_OUTFITS_READY',len(changed),'body materials',str(path))
