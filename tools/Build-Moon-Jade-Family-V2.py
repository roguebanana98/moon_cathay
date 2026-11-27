"""Extend v1 to all five Jade unit types, replacing only human body/head slots."""
import csv,json,copy,hashlib,struct,subprocess,shutil,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-jade-reskin-v2';D=R/'reference/local/moon-jade-expanded'
BASE=R/'releases/moon-jade-warriors-reskin-v1/mc_moon_jade_warriors_reskin_v1.pack';PACK=O/'mc_moon_jade_warriors_reskin_v2_family.pack';assert not PACK.exists()
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='3809a4b684c0e9b3f3b1183ed9fb1d799bb7a05195bf8e91deb675932b02952e'
M=json.loads((O/'native-review-assets.json').read_text());review=json.loads((O/'family-review.json').read_text());assert review['status']=='passed'
def unpack(path):
 raw=Path(path).read_bytes();assert raw[:4]==b'PFH5';_,dc,ds,fc,fs,_=struct.unpack_from('<6I',raw,4);pos=28+ds;end=pos+fs;entries=[]
 for _ in range(fc):
  size,comp=struct.unpack_from('<IB',raw,pos);pos+=5;assert comp==0;stop=raw.index(0,pos);name=raw[pos:stop].decode().replace('\\','/');pos=stop+1;entries.append((name,size))
 assert pos==end;result={}
 for name,size in entries:result[name]=raw[pos:pos+size];pos+=size
 assert pos==len(raw);return result
def cli(*args):
 p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True,encoding='utf-8')
 with (O/'pack-build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
 assert p.returncode==0,p.stdout+p.stderr
 return p.stdout
def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
N=R/'reference/local/moon-jade-native/db';native_uv=read(N/'unit_variants_tables/data__.tsv')[1];native_vars=read(N/'variants_tables/data__.tsv')[1];people='variantmeshes/wh_variantmodels/mc_moon_jade_reskin/'
db={};v1db=R/'build/moon-jade-reskin-v1/pack-roundtrip/db'
if not v1db.exists():cli('pack','extract','-p',BASE,'-t',C['schema'],'-F','db;'+str(R/'build/moon-jade-reskin-v1/pack-roundtrip'))
for name in ['unit_variants','variants']:
 path=next((v1db/(name+'_tables')).glob('*.tsv'));db[name]=read(path)
vmds=[];slot_checks=[]
for key,unit in M['units'].items():
 root=ET.parse(D/unit['native_vmd']).getroot();before={s.get('name'):ET.tostring(s) for s in root.findall('SLOT')}
 for name,choices in [('body',['body']),('head',['head_%02d'%i for i in range(1,8)])]:
  slot=next(s for s in root.findall('SLOT') if s.get('name')==name);template=slot.find('VARIANT_MESH');metadata=[copy.deepcopy(n) for n in template.findall('META_DATA')]
  for child in list(slot):slot.remove(child)
  for choice in choices:
   node=ET.SubElement(slot,'VARIANT_MESH',model=people+choice+'.rigid_model_v2')
   for md in metadata:node.append(copy.deepcopy(md))
 for slot in root.findall('SLOT'):
  if slot.get('name') not in ['body','head']:assert ET.tostring(slot)==before[slot.get('name')],(key,slot.get('name'))
 variant='mc_moon_jade_'+key;internal='variantmeshes/variantmeshdefinitions/'+variant+'.variantmeshdefinition';path=O/internal;path.parent.mkdir(parents=True,exist_ok=True);ET.indent(root);path.write_bytes(ET.tostring(root,encoding='utf-8'));vmds.append(internal)
 donor=next(r for r in native_uv if r['unit']==unit['unit'] and not r['faction']);uv=dict(donor,faction='cr_cth_agents_of_the_moon',name=variant,variant=variant);db['unit_variants'][1].append(uv)
 var=next(r for r in native_vars if r['variant_name']==donor['variant']).copy();var.update(variant_name=variant,variant_filename=variant,low_poly_filename='',super_low_poly_filename='');db['variants'][1].append(var)
 slot_checks.append(dict(key=key,unit=unit['unit'],variant=variant,native_equipment_stumps_and_attachments_exact=True,body='body.rigid_model_v2',head_options=7))
dbfiles=[]
for name,(headers,rows) in db.items():
 assert len(rows)==5
 internal='db/'+name+'_tables/zz_mc_moon_jade_reskin';headers=copy.deepcopy(headers);headers[1][0]=';'.join(headers[1][0].split(';')[:2]+[internal]);path=O/(internal+'.tsv');path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows(headers+[[row[k] for k in headers[0]] for row in rows])
 dbfiles.append(internal)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles]);cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in vmds])
before=unpack(BASE);after=unpack(PACK);changed=[p for p in before if before[p]!=after[p]];added=sorted(set(after)-set(before));assert set(changed)==set(dbfiles);assert set(added)==set(vmds)
assert all(before[p]==after[p] for p in before if p not in dbfiles);assert all(after[p]==(O/p).read_bytes() for p in vmds)
roundtrip=O/'pack-roundtrip';roundtrip.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(roundtrip))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(roundtrip/(p+'.tsv'))[1]
report=dict(pack=str(PACK),bytes=PACK.stat().st_size,sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_payloads=changed,added_payloads=added,all_v1_model_texture_and_sword_shield_assets_identical=True,units=slot_checks,total_units=5,head_options_per_unit=7,native_equipment_and_horse_unchanged=True,gameplay_stats_recruitment_animations_unchanged=True,Moon_faction_only=True,roundtrip_DB_equal=True,game_runtime_verified=False,enabled_in_launcher=False,deployed_to_data=False)
(O/'pack-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
