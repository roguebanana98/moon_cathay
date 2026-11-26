import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-dao-edge-corrected/jade-model05-dao-correct-cutting-edge.blend'))
out=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and 'beitingsheshou5.rigid_model_v2' in ob.get('source_geometry',''):
  pts=[dict(index=v.index,co=list(v.co),groups=[(ob.vertex_groups[g.group].name,g.weight) for g in v.groups]) for v in ob.data.vertices if v.co.z<.20]
  if pts:out.append(dict(name=ob.name,part=ob.get('source_part_index'),points=pts))
(R/'build/deer-jade-model05-dao-edge-corrected/boot-audit.json').write_text(json.dumps(out))
