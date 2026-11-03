"""Compare actual game exports to the approved rig over every integrated clip."""
import bpy,addon_utils,sys,json,hashlib
from pathlib import Path
from mathutils.kdtree import KDTree
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/huyen-ve-animation-integration'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-all-animations.blend'))
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
report=json.loads((O/'scene-integration-report.json').read_text());rig=bpy.data.objects['humanoid01e_HuyenVe'];original=bpy.data.objects['mc_huyen_ve_body_lod0'];sword=bpy.data.objects['mc_huyen_ve_sword_lod0']
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
before=set(bpy.data.objects);body_path=O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_body.rigid_model_v2'
assert bpy.ops.import_scene.rmv2(filepath=str(body_path),import_all_lods=True,build_materials=False)=={'FINISHED'}
loaded=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(loaded)==4
actual=max(loaded,key=lambda o:len(o.data.polygons))
kd=KDTree(len(original.data.vertices))
for v in original.data.vertices:kd.insert(v.co,v.index)
kd.balance();matches=[kd.find(v.co) for v in actual.data.vertices];bind_error=max(row[2] for row in matches);assert bind_error<.001
indices=np.array([row[1] for row in matches]);rows=[];maximum=0
for item in report['actions']:
    action=bpy.data.actions[item['action']];rig.animation_data.action=action
    if hasattr(action,'slots'):rig.animation_data.action_slot=action.slots[0]
    samples=[]
    for frame in item['sampled_frames']:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();one=original.evaluated_get(dg);two=actual.evaluated_get(dg);m1=one.to_mesh();m2=two.to_mesh()
        p1=np.array([list(v.co) for v in m1.vertices]);p2=np.array([list(v.co) for v in m2.vertices]);assert np.isfinite(p1).all() and np.isfinite(p2).all()
        error=np.linalg.norm(p1[indices]-p2,axis=1);assert float(error.max())<.02,(item['action'],frame,float(error.max()))
        maximum=max(maximum,float(error.max()));samples.append({'frame':frame,'max_error':float(error.max()),'p99_error':float(np.percentile(error,99))});one.to_mesh_clear();two.to_mesh_clear()
    rows.append({'action':item['action'],'native_path':item['native_path'],'samples':samples})
# The sword must remain a static prop; compare every exported LOD position
# to the approved, baked local coordinates used by weapon_2.
before=set(bpy.data.objects);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
sword_path=body_path.with_name('mc_huyen_ve_sword.rigid_model_v2')
assert bpy.ops.import_scene.rmv2(filepath=str(sword_path),import_all_lods=True,build_materials=False)=={'FINISHED'}
props=sorted([o for o in bpy.data.objects if o not in before and o.type=='MESH'],key=lambda o:-len(o.data.polygons));assert len(props)==4
sword_errors=[]
for i,prop in enumerate(props):
    source=bpy.data.objects['mc_huyen_ve_sword_lod'+str(i)];tree=KDTree(len(source.data.vertices))
    for v in source.data.vertices:tree.insert(v.co,v.index)
    tree.balance();error=max(tree.find(v.co)[2] for v in prop.data.vertices);assert error<.001;sword_errors.append(error)
result={'status':'passed','clip_count':len(rows),'sampled_pose_count':sum(len(row['samples']) for row in rows),'body_bind_max_error':bind_error,'body_deformed_max_error':maximum,
 'sword_lod_local_max_errors':sword_errors,'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [body_path,sword_path]},'clips':rows,
 'scope':'Actual exported RMV2 vs Blender rig on every integrated clip at start/middle/end; not a visual clipping or WH3 runtime test'}
(O/'animation-roundtrip-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='clips'}))
