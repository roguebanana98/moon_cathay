"""Read-only intake of the user-provided FBX; write a separate review scene."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'assets/authored/fantasy longsword 3d model';O=R/'build/huyen-ve-fantasy-longsword';O.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
fbx=next(A.glob('*.fbx'));bpy.ops.import_scene.fbx(filepath=str(fbx))
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append(dict(name=o.name,vertices=len(o.data.vertices),triangles=sum(len(p.vertices)-2 for p in o.data.polygons),dimensions=list(o.dimensions),matrix=[list(x) for x in o.matrix_world],bounds_min=[min(v[i] for v in pts) for i in range(3)],bounds_max=[max(v[i] for v in pts) for i in range(3)],materials=[m.name for m in o.data.materials],uv_layers=len(o.data.uv_layers)))
report=dict(source=str(fbx),source_sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),meshes=rows,images=[dict(name=i.name,path=i.filepath,size=list(i.size)) for i in bpy.data.images])
(O/'intake.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source-review.blend'))
print('SWORD_INTAKE',json.dumps(report))
