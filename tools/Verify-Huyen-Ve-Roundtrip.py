"""Compare the exported game mesh to its source rig across native animation poses."""
import bpy,addon_utils,json,hashlib
from pathlib import Path
from mathutils.kdtree import KDTree
import numpy as np
R=Path(__file__).resolve().parents[1];OUT=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'huyen-ve-rigged-prototype.blend'));addon_utils.enable('io_scene_rmv2')
original=bpy.data.objects['mc_huyen_ve_body_lod0'];rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
original.hide_set(False)
before=set(bpy.data.objects)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
path=OUT/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_body.rigid_model_v2'
assert bpy.ops.import_scene.rmv2(filepath=str(path),import_all_lods=True,texture_root=str(OUT))=={'FINISHED'}
loaded=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(loaded)==4
actual=max(loaded,key=lambda o:len(o.data.polygons))
kd=KDTree(len(original.data.vertices))
for v in original.data.vertices:kd.insert(v.co,v.index)
kd.balance();matches=[kd.find(v.co) for v in actual.data.vertices]
assert max(m[2] for m in matches)<.001,max(m[2] for m in matches)
indices=np.array([m[1] for m in matches]);errors={}
for name in ['stand','run','attack','cast']:
    rig.animation_data.action=bpy.data.actions['QA_'+name];a,b=map(int,rig.animation_data.action.frame_range)
    rows=[]
    for frame in sorted({a,(a+b)//2,b}):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        one=original.evaluated_get(dg);two=actual.evaluated_get(dg);m1=one.to_mesh();m2=two.to_mesh()
        p1=np.array([list(v.co) for v in m1.vertices]);p2=np.array([list(v.co) for v in m2.vertices])
        d=np.linalg.norm(p1[indices]-p2,axis=1);assert np.isfinite(d).all()
        rows.append(dict(frame=frame,max_error=float(d.max()),p99_error=float(np.percentile(d,99))))
        assert d.max()<.02,(name,frame,float(d.max()))
        one.to_mesh_clear();two.to_mesh_clear()
    errors[name]=rows
report=dict(status='passed',rmv2_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rig_bones=len(rig.data.bones),lod_count=len(loaded),
    largest_bind_position_error=max(m[2] for m in matches),animation_quantization_errors=errors,
    scope='Exported RMV2 vs Blender skinning on 12 native animation poses; no WH3 runtime claim')
(OUT/'roundtrip-validation.json').write_text(json.dumps(report,indent=2))
print('ROUNDTRIP',json.dumps(report))
