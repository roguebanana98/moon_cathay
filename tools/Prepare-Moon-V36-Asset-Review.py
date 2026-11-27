"""Extract the recovered Zhao and native rider review assets into ignored reference."""
import ast,csv,json,re,struct,sys,xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-v36-zhao-jade';D=R/'reference/local/moon-v36-asset-review';D.mkdir(parents=True,exist_ok=True)
GAME=Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data');A=SimpleNamespace(angels=R/'mc_moonshadow_heroes_v35_moon_arts.pack',game=GAME.parent)
indexes={};provenance={};aliases={}
tree=ast.parse((R/'tools/Prepare-Divine-Wing-Guard-Preview.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['norm','index','resolve','xml']],type_ignores=[]),'<asset resolver>','exec'))
import subprocess
sys.path.insert(0,str(Path(C['rpfm']).parent.parent/'rmv2-addon'));import rmv2_format as rf
def extract(pack,paths):
 for start in range(0,len(paths),20):subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f',*[p+';'+str(D) for p in paths[start:start+20]]],check=True,stdout=subprocess.DEVNULL)
vmd='variantmeshes/variantmeshdefinitions/mc_mooncourt_lord.variantmeshdefinition';resolve([vmd])
textures=set();models={}
def model(path):
 path=norm(path)
 if path in models:return path
 resolve([path]);ws=xml(path);geo=norm(ws.findtext('geometry'));resolve([geo]);rm=rf.load((D/geo).read_bytes())
 matrefs={int(x.get('part_index')):norm(x.text) for x in ws.findall('.//material') if x.get('lod_index')=='0'};resolve(matrefs.values());parts=[]
 for i,p in enumerate(rm.lods[0].models):
  pairs=[(int(t),norm(tx)) for t,tx in p.material.textures if int(t) in [0,1,3,27,29] and tx.lower().endswith('.dds')]
  if i in matrefs:
   pairs=[]
   for tx in xml(matrefs[i]).findall('.//texture'):
    typ={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29,'t_xml_specular':3}.get(tx.findtext('slot'))
    if typ is not None:pairs.append((typ,norm(tx.findtext('source'))))
  textures.update(p for _,p in pairs);parts.append(dict(textures=pairs,material=matrefs.get(i,''),pivot=list(p.material.pivot)))
 models[path]=dict(path=path,geometry=geo,parts=parts,skeleton=rm.skeleton_name,lods=len(rm.lods));return path
zhao=[]
for slot in xml(vmd).findall('SLOT'):
 for mesh in slot.findall('VARIANT_MESH'):
  if mesh.get('model'):zhao.append(dict(slot=slot.get('name'),attach=slot.get('attach_point'),model=model(mesh.get('model'))))
mounts={}
def native_rows(t):
 p=R/'reference/local/zhao-shugengan-comparison-20261126/native/db'/(t+'_tables/data__.tsv');a=list(csv.reader(p.open(encoding='utf-8-sig'),delimiter='\t'));return [dict(zip(a[0],x)) for x in a[2:]]
for suffix,key in [('warhorse','wh3_main_cth_mnt_horse_hero'),('jade_longma','wh3_main_cth_mnt_jade_longma_hero')]:
 m=next(r for r in native_rows('mounts') if r['key']==key);v=next(r for r in native_rows('variants') if r['variant_name']==m['variant']);path='variantmeshes/variantmeshdefinitions/'+v['variant_filename']+'.variantmeshdefinition';resolve([path]);entries=[]
 for slot in xml(path).findall('SLOT'):
  variants=[x for x in slot.findall('VARIANT_MESH') if x.get('model')]
  if variants:entries.append(dict(slot=slot.get('name'),attach=slot.get('attach_point'),model=model(variants[0].get('model'))))
 mounts[suffix]=dict(entries=entries,animation=m['animation'],skeleton=models[entries[0]['model']]['skeleton'])
resolve(textures,'texture')
packs=['animations/database/battle/bin/animation_tables'+suffix+'.animpack' for suffix in ['','__','__3']];extract(GAME/'anim.pack',packs)
bins={}
for p in packs:
 raw=(D/p).read_bytes();pos=4
 for _ in range(struct.unpack_from('<I',raw)[0]):
  size=struct.unpack_from('<H',raw,pos)[0];pos+=2;key=raw[pos:pos+size].decode();pos+=size;n=struct.unpack_from('<I',raw,pos)[0];pos+=4;bins[Path(key).stem]=raw[pos:pos+n];pos+=n
profiles={'foot':'hu1e_dlc24_yuan_bo_dragon_jade','warhorse':'hu1e_hr1_warhorse_mage_lord','jade_longma':'hu1e_wh3_cathay_hr1_longma_mage_lord'}
allclips=set(json.loads((O/'native-animation-index.json').read_text()));clips={};runtime={}
for kind,profile in profiles.items():
 assert profile in bins,profile
 paths=sorted(set(x.decode() for x in re.findall(rb'animations/[a-zA-Z0-9_./ -]+?\.anim',bins[profile])))
 runtime[profile]=paths
 if kind=='foot':
  selected=[]
  for tag in ['sword_stand_01','sword_walk_02','sword_run_02','sword_attack_01','sword_attack_02','sword_spell_cast_short_01','sword_spell_cast_medium_01']:
   selected.append(next(x for x in paths if '/yuan_bo_human/' in x and x.endswith(tag+'.anim')))
 else:
  selected=[];part='/rider/'+('warhorse' if kind=='warhorse' else 'longma')+'/shugengan/'
  preferred=[p for p in paths if part in p]
  for group,tag in [('stand','stand_01'),('locomotion','walk_01'),('attacks','attack_01'),('spellcasting','cast_fwd_short_01')]:
   choices=[p for p in preferred if '/'+group+'/' in p and p.endswith(tag+'.anim')]
   if not choices:choices=[p for p in paths if '/shugengan/' in p and '/'+group+'/' in p and p.endswith(tag+'.anim')]
   assert choices,(kind,group);selected.append(choices[0])
 clips[kind]=selected
extract(GAME/'anim2.pack',sorted(set(p for v in clips.values() for p in v)|{'animations/skeletons/humanoid01e.anim'}))
for suffix,m in mounts.items():
 resolve(['animations/skeletons/'+m['skeleton']+'.anim'],'animation')
 # Presentation of the whole mount uses native matching idle only.
 if suffix=='warhorse':m['idle']='animations/battle/horse01/stand/hr1_stand_01.anim'
 else:m['idle']='animations/battle/horse01/stand/hr1_fly_stand_02.anim'
 resolve([m['idle']],'animation')
report=dict(reference=str(D),models=models,zhao=zhao,foot_vmd=vmd,mounts=mounts,clips=clips,runtime_profiles=runtime,aliases=aliases,provenance=provenance)
(O/'asset-review-input.json').write_text(json.dumps(report,indent=2));print('Prepared Zhao',len(models),'models and',sum(map(len,clips.values())),'native runtime profile clips',flush=True)
