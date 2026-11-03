"""Undo the concept03-only sword placement for native Yuan Bo hands."""
import sys,json,importlib.util,copy,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v16-approved';V=R/'build/huyen-ve-animation-integration';s=importlib.util.spec_from_file_location('rf',R.parent/'tooling/model-workbench/addon-source/rmv2_format.py');rf=importlib.util.module_from_spec(s);sys.modules['rf']=rf;s.loader.exec_module(rf)
internal='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_sword.rigid_model_v2';f=rf.load((V/internal).read_bytes());old=copy.deepcopy(f)
delta=np.array([-.0252098087,-.0113643212,-.0738133043],dtype=np.float32)
for l in f.lods:
 for m in l.models:m.mesh.positions+=delta;m.mesh.raw_block=None;m.bbox_min=m.bbox_max=None
p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(rf.save(f));check=rf.load(p.read_bytes());errors=[]
for a,b in zip(check.lods,old.lods):
 assert a.camera_distance==b.camera_distance
 for m,n in zip(a.models,b.models):
  err=float(np.max(np.abs(m.mesh.positions-(n.mesh.positions+delta))));assert err<.001;errors.append(err)
  assert np.array_equal(m.mesh.indices,n.mesh.indices)
(O/'sword-native-fit.json').write_text(json.dumps({'status':'passed','reason':'Remove concept03 manual offset; restore lotus sword to native attachment alignment','blender_translation':[.0252098087,.0738133043,-.0113643212],'roundtrip_max_position_error':max(errors),'sword_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lod_count':4},indent=2));print('SWORD_NATIVE_FIT_OK',max(errors))
