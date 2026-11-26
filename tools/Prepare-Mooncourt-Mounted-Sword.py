"""Mounted-only hand anchor derived from the approved foot grip; all four LODs."""
import bpy,json,sys,copy
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-v35-moon-arts'
bpy.ops.wm.open_mainfile(filepath=str(R/'build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-grip-fixed.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
K=(rig.matrix_world@rig.pose.bones['hand_right'].matrix).inverted()@(rig.matrix_world@rig.pose.bones['weapon_2'].matrix)
assert abs(K.to_3x3().determinant()-1)<1e-4
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
source=R/'reference/local/yuan-bo-model/variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.rigid_model_v2'
m=rf.load(source.read_bytes());before=copy.deepcopy(m)
B=np.array([[-1,0,0],[0,0,-1],[0,1,0]],dtype=np.float64);G=np.linalg.inv(B)@np.array(K.to_3x3(),dtype=np.float64)@B
for lod in m.lods:
    for part in lod.models:
        p=np.array(part.material.pivot);pb=np.array(K)[:3,:3]@(B@p)+np.array(K.translation);part.material.pivot=tuple(np.linalg.inv(B)@pb)
        part.mesh.positions=(part.mesh.positions@G.T).astype(np.float32)
        for attr in ['normals','tangents','binormals']:
            a=getattr(part.mesh,attr,None)
            if a is not None and a.ndim==2 and a.shape[1]>=3:a[:,:3]=a[:,:3]@G.T
        part.bbox_min=None;part.bbox_max=None
geo='variantmeshes/wh_variantmodels/mc_mooncourt_lord/mounted_sword_hand.rigid_model_v2';dest=O/geo;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(rf.save(m));actual=rf.load(dest.read_bytes());assert len(actual.lods)==4
errors=[]
for old,new in zip(before.lods,actual.lods):
    assert len(old.models)==len(new.models)
    for a,b in zip(old.models,new.models):
        expected=(a.mesh.positions+np.array(a.material.pivot))@B.T@np.array(K.to_3x3()).T+np.array(K.translation)
        got=(b.mesh.positions+np.array(b.material.pivot))@B.T
        err=float(abs(expected-got).max());print('LOD_TRANSFORM_ERROR',err,'pivots',a.material.pivot,b.material.pivot,'first',expected[0].tolist(),got[0].tolist(),flush=True);assert err<.002;errors.append(err)
        assert np.array_equal(a.mesh.indices,b.mesh.indices) and np.array_equal(a.mesh.uv0,b.mesh.uv0)
v34=json.loads((R/'build/moon-v34-yuan-bo-lord/pack-validation.json').read_text());ws=ET.parse(R/'build/moon-v34-yuan-bo-lord'/v34['sword_wsmodel']).getroot();ws.find('geometry').text=geo
wspath='variantmeshes/wh_variantmodels/mc_mooncourt_lord/mounted_sword_hand.wsmodel';(O/wspath).write_bytes(ET.tostring(ws,encoding='utf8'))
root=ET.parse(R/'build/moon-v34-yuan-bo-lord/variantmeshes/variantmeshdefinitions/mc_mooncourt_lord.variantmeshdefinition').getroot();slot=root.find("SLOT[@name='weapon_2']");slot.set('attach_point','hand_right');slot.find('VARIANT_MESH').set('model',wspath)
vmd='variantmeshes/variantmeshdefinitions/mc_mooncourt_lord_mounted.variantmeshdefinition';(O/vmd).parent.mkdir(parents=True,exist_ok=True);(O/vmd).write_bytes(ET.tostring(root,encoding='utf8'))
(O/'mounted-sword.json').write_text(json.dumps(dict(files=[geo,wspath,vmd],vmd=vmd,variant='mc_mooncourt_lord_mounted',attachment='hand_right',weapon_to_hand_matrix=[list(r) for r in K],lods=4,max_position_errors=errors,original_foot_assets_unchanged=True,body_weights_unchanged=True,texture_uv_topology_unchanged=True),indent=2));print('MOUNTED_HAND_ANCHOR_READY',flush=True)
