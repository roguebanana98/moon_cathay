import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-approved-variants'
bpy.ops.wm.open_mainfile(filepath=str(O/'moon-jade-warriors-approved-seven-variants.blend'))
libs=[dict(name=l.name,filepath=l.filepath,users=l.users) for l in bpy.data.libraries]
ids=[dict(name=id.name,type=type(id).__name__,library=id.library.filepath) for id in bpy.data.user_map() if id.library]
meshes=[dict(name=o.name,part=o.get('source_part_index'),part_name=o.get('source_part_name'),vertices=len(o.data.vertices),bounds=[[min(v.co[a] for v in o.data.vertices),max(v.co[a] for v in o.data.vertices)] for a in range(3)]) for o in bpy.data.collections['VARIANT 07 | approved body05 + DEER head07'].objects if o.type=='MESH' and 'beitingsheshouh7' in o.get('source_geometry','')]
(O/'portability-audit.json').write_text(json.dumps(dict(libraries=libs,linked_ids=ids,head07=meshes),indent=2))
