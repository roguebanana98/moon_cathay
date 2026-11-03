import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-rigged-prototype.blend'))
result={'images':[dict(name=i.name,path=i.filepath,exists=Path(bpy.path.abspath(i.filepath)).is_file(),packed=bool(i.packed_file),size=list(i.size),source=i.source) for i in bpy.data.images if i.source=='FILE'],
'viewports':[dict(screen=s.name,shading=a.spaces.active.shading.type) for s in bpy.data.screens for a in s.areas if a.type=='VIEW_3D'],
'materials':[{ 'name':m.name,'nodes':[(n.name,n.type,n.image.name if n.type=='TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes]} for m in bpy.data.materials if m.use_nodes and m.name.startswith('mc_huyen_ve')]}
(O/'preview-inspection.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
