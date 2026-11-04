import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Endo_Damsel_All_4_Variants.blend'))
for o in bpy.data.objects:
    if o.type=='MESH' and 'body' in o.name:
        print('BODY',o.name,'UV',[(u.name,tuple(u.data[0].uv)) for u in o.data.uv_layers])
        for m in o.data.materials:
            print('MAT',m.name)
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE':print('IMAGE',n.name,n.image.name if n.image else None,list(n.image.size) if n.image else None)
