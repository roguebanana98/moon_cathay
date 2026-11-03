import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'huyen-ve-rigged-prototype.blend'))
for im in bpy.data.images:
 if 'mask.dds' in im.name or 'base_colour.dds' in im.name:print('TEXTURE',im.name,im.colorspace_settings.name,im.alpha_mode,list(im.pixels[:4]))
body=bpy.data.objects['mc_huyen_ve_body_lod0'];rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
results={}
rig.animation_data.action=bpy.data.actions['QA_stand'];bpy.context.scene.frame_set(21);bpy.context.view_layer.update()
de=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=de.to_mesh()
for side in ['left','right']:
 pts=[me.vertices[v.index].co.copy() for v in body.data.vertices if sum(g.weight for g in v.groups if body.vertex_groups[g.group].name=='hand_'+side)>.5]
 print('HAND',side,'count',len(pts),'centroid',list(sum(pts,__import__('mathutils').Vector())/len(pts)) if pts else [],'bone',list(rig.pose.bones['hand_'+side].head),'fingers',list(rig.pose.bones['finger_index_'+side+'_0'].head))
de.to_mesh_clear()
for name in ['stand','run','attack','cast']:
 rig.animation_data.action=bpy.data.actions['QA_'+name];bpy.context.scene.frame_set(int(sum(rig.animation_data.action.frame_range)/2));bpy.context.view_layer.update()
 obj=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=obj.to_mesh();edges=[]
 for e in body.data.edges:
  a,b=e.vertices;rest=(body.data.vertices[a].co-body.data.vertices[b].co).length;d=(me.vertices[a].co-me.vertices[b].co).length
  if rest>.004:edges.append((d/rest,a,b,rest,d))
 rows=[]
 for ratio,a,b,rest,posed in sorted(edges,reverse=True)[:12]:
  rows.append(dict(ratio=ratio,rest=rest,posed=posed,vertices=[dict(id=i,co=list(body.data.vertices[i].co),weights={body.vertex_groups[g.group].name:g.weight for g in body.data.vertices[i].groups}) for i in [a,b]]))
 results[name]=rows;obj.to_mesh_clear()
(OUT/'deform-probe.json').write_text(json.dumps(results,indent=2))
for name,rows in results.items():print(name,json.dumps(rows[:2]))
