import bpy,sys,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
sys.path.insert(0,str(R/'tools'))
from HuyenVePreview import prepare_preview
path=O/'huyen-ve-rigged-prototype.blend'
backup=O/'huyen-ve-rigged-prototype-before-texture-fix.blend'
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
report=prepare_preview(O)
bpy.ops.wm.save_as_mainfile(filepath=str(path))
# Reopen the saved file to check the actual persisted state.
bpy.ops.wm.open_mainfile(filepath=str(path))
used=[n.image for m in bpy.data.materials if m.use_nodes and m.name.startswith('mc_huyen_ve') for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
assert len(used)==8 and all(i.packed_file and min(i.size)>0 for i in used)
assert all(a.spaces.active.shading.type=='MATERIAL' for s in bpy.data.screens for a in s.areas if a.type=='VIEW_3D')
report['reopen_verified']=True
(O/'preview-fix-report.json').write_text(json.dumps(report,indent=2))
# Render the saved scene with the embedded PNGs as a visual check.
bpy.context.scene.render.filepath=str(O/'qa_textured.png')
bpy.ops.render.render(write_still=True)
print(json.dumps(report))
