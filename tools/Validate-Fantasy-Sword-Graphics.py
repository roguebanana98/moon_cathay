"""Complete the material graph and check the exact exported sword payloads."""
import ast,hashlib,importlib.util,json,struct,sys,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-fantasy-longsword'
s=importlib.util.spec_from_file_location('rf',R.parent/'tooling/model-workbench/addon-source/rmv2_format.py');rf=importlib.util.module_from_spec(s);sys.modules['rf']=rf;s.loader.exec_module(rf)
P='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/'
model=P+'mc_huyen_ve_sword.rigid_model_v2';material=P+'materials/mc_huyen_ve_sword_rigid.xml.material'
files=json.loads((O/'texture-conversion.json').read_text())['files']
tree=E.parse(O/'old'/material)
for t in tree.findall('.//texture'):
 slot=t.findtext('slot')
 for token in ['base_colour','material_map','normal','mask']:
  if slot=='t_xml_'+token:t.find('source').text=next(p for p in files if p.endswith('_'+token+'.dds'))
for p in tree.findall('.//param'):
 if p.findtext('name')=='emissive_strength':p.find('value').text='0'
target=O/material;target.parent.mkdir(parents=True,exist_ok=True);E.indent(tree,space='  ');tree.write(target,encoding='utf-8')
f=rf.load((O/model).read_bytes());assert f.skeleton_name=='' and len(f.lods)==4
rows=[]
for i,lod in enumerate(f.lods):
 assert len(lod.models)==1 and lod.camera_distance==[10,20,30,10000][i]
 m=lod.models[0];assert m.mesh.raw_format==rf.VF_STATIC and m.material.matrix_index==-1 and m.material.parent_matrix_index==-1
 assert m.mesh.vertex_count<65536 and int(m.mesh.indices.max())<m.mesh.vertex_count
 for channel in ['positions','normals','tangents','binormals','uv0']:assert np.isfinite(getattr(m.mesh,channel)).all()
 assert all((O/path).is_file() for _,path in m.material.textures)
 assert {p for _,p in m.material.textures}==set(files)
 rows.append(dict(lod=i,vertices=m.mesh.vertex_count,triangles=len(m.mesh.indices)//3,distance=lod.camera_distance))
for p in files:
 b=(O/p).read_bytes();assert b[:4]==b'DDS ';height,width=struct.unpack_from('<II',b,12);mips=struct.unpack_from('<I',b,28)[0]
 assert (width,height)==((128,128) if '_mask.' in p else (2048,2048)) and mips>1
for node in tree.findall('.//texture/source'):
 assert node.text.startswith('commontextures/') or (O/node.text).is_file(),node.text
intake=json.loads((O/'intake.json').read_text());assert hashlib.sha256(Path(intake['source']).read_bytes()).hexdigest()==intake['source_sha256']
files=[model,material]+files
report=dict(status='exported_graphics_passed',files=files,sha256={p:hashlib.sha256((O/p).read_bytes()).hexdigest() for p in files},lods=rows,static_prop=True,secondary_bone_binding=False,source_unchanged=True,game_runtime_verified=False)
(O/'graphics-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
