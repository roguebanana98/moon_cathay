"""Private v16 graphics integration using original mod LODs; no deploy."""
import sys,json,hashlib,importlib.util,copy,subprocess,shutil,xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/huyen-ve-v16-approved';D=R/'reference/local/pandalorian-yuan-bo';P=D/'variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human';BASE='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve_v2';G=O/BASE;G.mkdir(parents=True,exist_ok=True)
s=importlib.util.spec_from_file_location('rf',R.parent/'tooling/model-workbench/addon-source/rmv2_format.py');rf=importlib.util.module_from_spec(s);sys.modules['rf']=rf;s.loader.exec_module(rf)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
def xmlwrite(tree,path):path.parent.mkdir(parents=True,exist_ok=True);E.indent(tree,space='  ');tree.write(path,encoding='utf-8',xml_declaration=False)
# Only visible appearance is approved; hidden backups never enter exported model.
approval=json.loads((R/'build/huyen-ve-model-v2/approved-model.json').read_text());assert sha(approval['approved_scene'])==approval['sha256']
f=rf.load((P/'cth_dragon_jade_human_01.rigid_model_v2').read_bytes());original=copy.deepcopy(f);ws=E.parse(P/'cth_dragon_jade_human_01.wsmodel');wsrefs={(int(x.get('lod_index')),int(x.get('part_index'))):x.text.replace('\\','/').lower() for x in ws.findall('.//material')}
T=G/'tex';T.mkdir(exist_ok=True);tmp=O/'texture-input';tmp.mkdir(exist_ok=True)
Image.new('RGBA',(16,16),(0,0,0,0)).save(tmp/'neutral_mask.png')
run([C['texconv'],'-nologo','-y','-m','0','-f','BC3_UNORM','-o',T,tmp/'neutral_mask.png'])
run([C['texconv'],'-nologo','-y','-srgb','-w','1024','-h','1024','-m','0','-f','BC7_UNORM_SRGB','-o',T,R/'build/huyen-ve-model-v2/face-clean-shaven.png'])
textures={};mats={};rows=[];newws=E.Element('model',version='1');E.SubElement(newws,'geometry').text=BASE+'/mc_huyen_ve_body.rigid_model_v2';wm=E.SubElement(newws,'materials')
def texture(path):
 path=path.replace('\\','/').lower()
 if path.startswith('commontextures/'):return path
 if path=='mask_path':return BASE+'/tex/neutral_mask.dds'
 if path in textures:return textures[path]
 source=D/path;assert source.is_file(),source
 dest=BASE+'/tex/'+hashlib.sha256(path.encode()).hexdigest()[:10]+'_'+source.name
 if source.name=='face_a.dds':dest=BASE+'/tex/face-clean-shaven.dds'
 else:(O/dest).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,O/dest)
 textures[path]=dest;return dest
hidden={'huzi','facial hair','wokou_hair','ogr_hunter_torso_03_submesh_0'}
for li,lod in enumerate(f.lods):
 kept=[];partrows=[]
 for pi,m in enumerate(lod.models):
  name=m.material.model_name
  if name in hidden:continue
  mesh=m.mesh
  if name=='cth_dragon_iron_human_body_01_su':
   tri=mesh.indices.reshape(-1,3);mask=mesh.positions[:,1]<.7;assert np.all(np.all(mask[tri],axis=1)|np.all(~mask[tri],axis=1)),('cross-boundary face',li)
   tri=tri[np.all(mask[tri],axis=1)];ids=np.unique(tri);remap=np.full(mesh.vertex_count,-1,dtype=np.int32);remap[ids]=np.arange(len(ids));oldn=mesh.vertex_count
   raw=np.frombuffer(mesh.raw_block,dtype=np.uint8).reshape(oldn,-1)[ids].copy().tobytes()
   for field,value in vars(mesh).copy().items():
    if isinstance(value,np.ndarray) and field!='indices' and len(value)==oldn:setattr(mesh,field,value[ids].copy())
   mesh.raw_block=raw;mesh.indices=remap[tri].astype(np.uint16).ravel();m.bbox_min=m.bbox_max=None
  ref=wsrefs[li,pi]
  if ref not in mats:
   tree=E.parse(D/ref)
   for t in tree.findall('.//texture/source'):
    if t.text:t.text=texture(t.text)
   newref=BASE+'/materials/'+hashlib.sha256(ref.encode()).hexdigest()[:10]+'_'+Path(ref).name;mats[ref]=newref;xmlwrite(tree,O/newref)
  newref=mats[ref];tree=E.parse(O/newref);slots={t.findtext('slot'):t.findtext('source') for t in tree.findall('.//texture')}
  types={27:'t_xml_base_colour',1:'t_xml_normal',3:'t_xml_mask',29:'t_xml_material_map'}
  m.material.textures=[(typ,slots[slot]) for typ,slot in types.items() if slot in slots]
  E.SubElement(wm,'material',part_index=str(len(kept)),lod_index=str(li)).text=newref
  kept.append(m);partrows.append({'source_part':pi,'name':name,'vertices':mesh.vertex_count,'triangles':len(mesh.indices)//3})
 lod.models=kept;rows.append({'lod':li,'distance':lod.camera_distance,'parts':partrows,'triangles':sum(x['triangles'] for x in partrows)})
body=G/'mc_huyen_ve_body.rigid_model_v2';body.write_bytes(rf.save(f));xmlwrite(E.ElementTree(newws),G/'mc_huyen_ve_body.wsmodel');check=rf.load(body.read_bytes())
assert check.skeleton_name=='humanoid01e' and len(check.lods)==4
for li,lod in enumerate(check.lods):
 assert lod.camera_distance==original.lods[li].camera_distance
 for m,row in zip(lod.models,rows[li]['parts']):
  source=original.lods[li].models[row['source_part']];sm=source.mesh
  if m.material.model_name=='cth_dragon_iron_human_body_01_su':
   ids=np.unique(sm.indices.reshape(-1,3)[np.all((sm.positions[:,1]<.7)[sm.indices.reshape(-1,3)],axis=1)])
  else:ids=np.arange(sm.vertex_count)
  for attr in ['positions','normals','tangents','binormals','uv0','bone_indices','bone_weights']:assert np.array_equal(getattr(m.mesh,attr),getattr(sm,attr)[ids]),(li,m.material.model_name,attr)
  assert np.isfinite(m.mesh.positions).all();assert m.mesh.bone_indices.max()<96
# Existing v15 sword and battle/campaign DB links remain intact.
vmd=E.parse(R/'build/huyen-ve-animation-integration/variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition');vmd.find("./SLOT[@name='body']/VARIANT_MESH").set('model',BASE+'/mc_huyen_ve_body.wsmodel');xmlwrite(vmd,O/'variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition')
files=sorted(p.relative_to(O).as_posix() for p in (O/'variantmeshes').rglob('*') if p.is_file())
for path in files:
 if path.endswith(('.material','.wsmodel')):
  for t in E.parse(O/path).iter():
   if t.tag in ['source','geometry','material'] and t.text and t.text.strip():assert t.text.startswith('commontextures/') or (O/t.text).is_file(),(path,t.text)
report={'status':'native_LODs_reused_binary_verified','approval_sha256':approval['sha256'],'source_model_sha256':sha(P/'cth_dragon_jade_human_01.rigid_model_v2'),'body_sha256':sha(body),'lods':rows,'vertex_channels_bit_identical_to_native':True,'hidden_parts_removed':sorted(hidden)+['iron waist and arms'],'files':files,'sword':'v15 lotus sword retained; new body grip review pending','runtime_verified':False}
(O/'graphics-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'lods':[{'lod':r['lod'],'triangles':r['triangles']} for r in rows],'files':len(files),'body_sha256':report['body_sha256']},indent=2))



