"""Resolve the two original Assault mounts into a private, self-contained namespace."""
import ast,csv,json,re,struct,subprocess,sys,shutil,hashlib
from pathlib import Path
from lxml import etree as E
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v21-mounts';O.mkdir(exist_ok=True)
D=R/'reference/local/moon-general-mounts';D.mkdir(exist_ok=True);SOURCE=Path(C['workshop'])/'2789903784/DEER24Cathay.pack';GAME=Path(C['game'])/'data'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
indexes={};missing=set();aliases={}
tree=ast.parse((R/'tools/Prepare-WWD-All-Lords.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['norm','index','extract','resolve','xml','components']],type_ignores=[]),'<source asset resolver>','exec'))
def db(t):
 out=[]
 for p in (R/'reference/local/deer-wwd/base/db'/(t+'_tables')).glob('*.tsv'):
  a=list(csv.reader(p.open(encoding='utf8'),delimiter='\t',quoting=csv.QUOTE_NONE));out.extend(dict(zip(a[0],r)) for r in a[2:])
 return out
models=[];files=[];base='variantmeshes/wh_variantmodels/mc_general_mounts/'
for key,donor in [('mc_assault_warhorse','wh3_deer24_BAIMA'),('mc_assault_great_stag','wh3_deer24_jiuselu')]:
 variant=next(r for r in db('variants') if r['variant_name']==donor);comps=components('variantmeshes/variantmeshdefinitions/'+variant['variant_filename']+'.variantmeshdefinition');out_comps=[]
 for i,c in enumerate(comps):
  p=c['path'];assert not resolve([p]);ws=xml(D/p);geom=norm(ws.findtext('geometry'));assert not resolve([geom]);rmv=rf.load((D/geom).read_bytes())
  refs=ws.findall('.//material');matpaths={norm(x.text) for x in refs};assert not resolve(matpaths)
  # Keep original WS shader settings and all four source LODs. Only paths change.
  for j,matpath in enumerate(sorted(matpaths)):
   mt=xml(D/matpath)
   for source in mt.findall('.//source'):
    if not source.text or not source.text.lower().endswith('.dds'):continue
    tex=norm(source.text);assert not resolve([tex],'texture');dst=base+key+'/tex/'+hashlib.sha256(tex.encode()).hexdigest()[:12]+'.dds';(O/dst).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/tex,O/dst);files.append(dst);source.text=dst
   dst=base+key+('/material_%d_%d.xml.material'%(i,j));(O/dst).parent.mkdir(parents=True,exist_ok=True);(O/dst).write_bytes(E.tostring(mt,encoding='UTF-8'));files.append(dst)
   for ref in refs:
    if norm(ref.text)==matpath:ref.text=dst
  dst=base+key+('/mount_%d.rigid_model_v2'%i);(O/dst).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/geom,O/dst);files.append(dst);ws.find('geometry').text=dst
  dst=base+key+('/mount_%d.wsmodel'%i);(O/dst).write_bytes(E.tostring(ws,encoding='UTF-8'));files.append(dst);out_comps.append(dict(path=dst,attach=c['attach'],skeleton=rmv.skeleton_name,lods=len(rmv.lods)))
 root=E.Element('VARIANT_MESH')
 for i,c in enumerate(out_comps):
  slot=E.SubElement(root,'SLOT',name='mount_'+str(i))
  if c['attach']:slot.set('attach_point',c['attach'])
  E.SubElement(slot,'VARIANT_MESH',model=c['path'])
 dst='variantmeshes/variantmeshdefinitions/'+key+'.variantmeshdefinition';(O/dst).parent.mkdir(parents=True,exist_ok=True);(O/dst).write_bytes(E.tostring(root,encoding='UTF-8'));files.append(dst)
 models.append(dict(key=key,donor=donor,variant=variant,components=out_comps))
assert not missing,missing
(O/'mount-assets.json').write_text(json.dumps(dict(models=models,files=sorted(set(files)),source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()),indent=2));print('MOUNT_ASSETS_READY',len(set(files)),flush=True)
