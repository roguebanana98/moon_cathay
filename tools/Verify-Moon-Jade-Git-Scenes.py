"""Read-only reopen of the exact backed-up Blender files."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'assets/working/moon-jade-warriors';report=[]
for row in json.loads((A/'checkpoint.json').read_text())['files']:
 p=R/row['path']
 if p.suffix!='.blend':continue
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 bpy.ops.wm.open_mainfile(filepath=str(p))
 external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
 linked=[id.name for id in bpy.data.user_map() if id.library]
 assert not external and not linked,(p,external,linked)
 report.append(dict(path=row['path'],packed_images=sum(bool(im.packed_file) for im in bpy.data.images),external_images=external,linked_ids=linked,objects=len(bpy.context.scene.objects),frame=bpy.context.scene.frame_current,markers=len(bpy.context.scene.timeline_markers),sha256=row['sha256']))
(A/'reports/portable-scenes.json').write_text(json.dumps(report,indent=2));print('PORTABLE_JADE_SCENES_VERIFIED',len(report),flush=True)
