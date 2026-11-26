import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-no-back-cape'
bpy.ops.wm.open_mainfile(filepath=str(O/'alchemist-11-death-squad-knife.blend'))
ob=bpy.data.objects['Death Squad knife 01'];me=ob.data
parent=list(range(len(me.vertices)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for e in me.edges:
    a,b=map(find,e.vertices);parent[b]=a
parts={}
for v in me.vertices:parts.setdefault(find(v.index),[]).append(v)
for ids in parts.values():print('PART',len(ids),'min',[round(min(v.co[j] for v in ids),4) for j in range(3)],'max',[round(max(v.co[j] for v in ids),4) for j in range(3)])
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
print('NEW_MATRIX',[list(r) for r in ob.matrix_local])
old=next(o for o in bpy.data.objects['Khainite dagger 01 | hand_right'].children_recursive if o.type=='MESH')
print('OLD_MATRIX',[list(r) for r in old.matrix_local])
print('OLD_BOUNDS', [min(v.co[j] for v in old.data.vertices) for j in range(3)],[max(v.co[j] for v in old.data.vertices) for j in range(3)])
body=bpy.data.objects['Model 11 | Original outfit without back cape'];inv=rig.data.bones['hand_right'].matrix_local.inverted()
ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated=ev.to_mesh();inv=rig.pose.bones['hand_right'].matrix.inverted()
for name in ('hand_right','finger_ring_right_0','finger_ring_right_1','finger_ring_right_2','thumb_right_0','thumb_right_1','thumb_right_2'):
    g=body.vertex_groups.get(name)
    ids=[v for v in body.data.vertices if g and any(x.group==g.index and x.weight>.5 for x in v.groups)]
    pts=[inv@evaluated.vertices[v.index].co for v in ids]
    print('HAND_GROUP',name,len(pts),'mean',tuple(sum(pts,Vector())/len(pts)) if pts else None)
