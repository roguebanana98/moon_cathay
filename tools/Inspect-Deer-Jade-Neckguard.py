import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-reskin-gallery/deer24-jade-warriors-reskin-gallery.blend'))
report=[]
for col in bpy.data.collections:
 if col.name.startswith(('05 |','06 |')):
  for ob in col.objects:
   if ob.type!='MESH':continue
   points=[v.co for v in ob.data.vertices]
   report.append(dict(collection=col.name,name=ob.name,part=ob.get('source_part_index'),source=ob.get('source_geometry'),vertices=len(points),bounds=[[min(v[a] for v in points),max(v[a] for v in points)] for a in range(3)]))
(R/'build/deer-jade-reskin-gallery/neckguard-audit.json').write_text(json.dumps(report,indent=2))
from mathutils import Vector
scene=bpy.context.scene
col=bpy.data.collections['06 | beitingsheshou_lancer']
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE' and 'JADE 06' in o.name)
arm.location.x=0
for ob in scene.objects:
 if ob.type in {'MESH','FONT'}:ob.hide_render=ob not in list(col.objects)
target=Vector((0,0,1.52));scene.camera.location=(2,3,1.95);scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=.95
scene.render.resolution_x=1000;scene.render.resolution_y=1000
scene.render.filepath=str(R/'build/deer-jade-reskin-gallery/model06-back.png');bpy.ops.render.render(write_still=True)
ob=next(o for o in col.objects if o.get('source_part_index')==5)
adj={v.index:set() for v in ob.data.vertices}
for e in ob.data.edges: a,b=e.vertices;adj[a].add(b);adj[b].add(a)
unseen=set(adj);comps=[]
while unseen:
 todo=[unseen.pop()];ids=set(todo)
 while todo:
  v=todo.pop()
  for n in adj[v]&unseen:unseen.remove(n);ids.add(n);todo.append(n)
 pts=[ob.data.vertices[i].co for i in ids]
 comps.append(dict(ids=sorted(ids),count=len(ids),bounds=[[min(v[a] for v in pts),max(v[a] for v in pts)] for a in range(3)]))
(R/'build/deer-jade-reskin-gallery/donor-neck-components.json').write_text(json.dumps(comps,indent=2))
