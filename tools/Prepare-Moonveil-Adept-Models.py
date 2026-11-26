"""Namespace four original Element Bender appearances, preserving geometry/LODs."""
import ast,csv,json,re,struct,subprocess,sys,shutil,hashlib
from pathlib import Path
from lxml import etree as E
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moonveil-v24';O.mkdir(exist_ok=True);D=R/'reference/local/element-benders'
SOURCE=Path(C['workshop'])/'3836052402/@taolu_cth_esoteric_masters.pack';GAME=Path(C['game'])/'data';G='variantmeshes/wh_variantmodels/mc_moonveil_adept'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
indexes={};missing=set();aliases={};tree=ast.parse((R/'tools/Prepare-WWD-All-Lords.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['norm','index','extract','resolve','xml']],type_ignores=[]),'<asset resolver>','exec'))
mapped={};files=set();ws_audit=[]
def put(path,data):
 p=O/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);files.add(path)
def copy_asset(path):
 path=norm(path)
 if path in mapped:return mapped[path]
 if Path(path).name=='null.rigid_model_v2':return path
 assert not resolve([path],'texture' if path.endswith('.dds') else 'model'),path
 target=G+'/assets/'+hashlib.sha256(path.encode()).hexdigest()[:10]+'_'+Path(path).name;mapped[path]=target
 if path.endswith(('.variantmeshdefinition','.wsmodel','.xml.material')):
  root=xml(D/path)
  for node in root.iter():
   for attribute in ['model','definition']:
    if node.get(attribute):node.set(attribute,copy_asset(node.get(attribute)))
   if str(node.tag).lower() in ['geometry','material'] and node.text and node.text.strip():node.text=copy_asset(node.text)
   elif str(node.tag).lower()=='source' and node.text and node.text.lower().endswith('.dds'):node.text=copy_asset(node.text)
  put(target,E.tostring(root,encoding='UTF-8'))
  if path.endswith('.wsmodel'):
   model=rf.load((O/root.findtext('geometry')).read_bytes());assert model.skeleton_name=='humanoid01e',path;assert len(model.lods)==4,path
   expected={(i,j) for i,l in enumerate(model.lods) for j,_ in enumerate(l.models)};actual={(int(x.get('lod_index')),int(x.get('part_index'))) for x in root.findall('.//material')};assert expected<=actual,(path,expected-actual)
   ws_audit.append(dict(source=path,wsmodel=target,skeleton=model.skeleton_name,lods=len(model.lods),lod_parts=[len(l.models) for l in model.lods]))
 else:put(target,(D/path).read_bytes())
 return target
def first_components(root):
 out=[]
 def walk(node):
  if str(node.tag).upper()=='VARIANT_MESH_REFERENCE':walk(E.parse(O/node.get('definition')).getroot());return
  if str(node.tag).upper()=='VARIANT_MESH' and node.get('model'):out.append(node.get('model'))
  choices=[x for x in node if str(x.tag).upper() in ['VARIANT_MESH','VARIANT_MESH_REFERENCE']]
  for x in node:
   if x not in choices or x==choices[0]:walk(x)
 walk(root);return out
models=[]
for palette,source in [('white','cth_air_bender'),('black','cth_earth_bender'),('blue','cth_water_bender'),('red','cth_fire_bender')]:
 key='mc_moonveil_adept_'+palette;root=xml(D/('variantmeshes/variantmeshdefinitions/'+source+'.variantmeshdefinition'))
 # Only visible body/head; source limb-stump options are native blood-pack parts.
 for child in list(root):
  if str(child.tag).upper()=='SLOT' and child.get('name') not in ['body','head']:root.remove(child)
 for node in root.iter():
  for attribute in ['model','definition']:
   if node.get(attribute):node.set(attribute,copy_asset(node.get(attribute)))
 path='variantmeshes/variantmeshdefinitions/'+key+'.variantmeshdefinition';put(path,E.tostring(root,encoding='UTF-8'));models.append(dict(key=key,palette=palette,source=source,vmd=path,representative=first_components(root)))
assert not missing
report=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),models=models,files=sorted(files),geometry_audit=ws_audit,geometry_textures_unchanged=True,dependency_count=len(mapped))
(O/'models.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('MOONVEIL_MODELS_READY',len(models),len(files),len(ws_audit),flush=True)
