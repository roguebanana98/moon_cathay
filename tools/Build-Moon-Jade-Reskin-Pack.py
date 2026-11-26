"""Standalone faction-scoped appearance pack, no gameplay overrides."""
import csv,json,hashlib,subprocess,struct,copy
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-jade-reskin-v1'
P=O/'mc_moon_jade_warriors_reskin_v1.pack';N=R/'reference/local/moon-jade-native/db';F='cr_cth_agents_of_the_moon';UNIT='wh3_main_cth_inf_jade_warriors_0';KEY='mc_moon_jade_warriors_reskin'
assert not P.exists(),'Preserve completed pack'
E=json.loads((O/'export-report.json').read_text());V=json.loads((O/'roundtrip-review.json').read_text());assert V['status']=='passed'
assert hashlib.sha256(Path(E['source']).read_bytes()).hexdigest()==E['source_sha256']
def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],row)) for row in a[2:]]
def cli(*args):
 p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True,encoding='utf-8')
 with (O/'pack-build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
 assert p.returncode==0,p.stdout+p.stderr
 return p.stdout
assert any(r['key']==F for p in (R/'reference/local/moon-jade-iee/db/factions_tables').glob('*.tsv') for r in read(p)[1])
tables={};h,rows=read(N/'unit_variants_tables/data__.tsv');native=next(r for r in rows if r['unit']==UNIT and not r['faction']);row=dict(native,faction=F,name=KEY,variant=KEY);tables['unit_variants']=([h[0],h[1]],[row])
h,rows=read(N/'variants_tables/data__.tsv');row=next(r for r in rows if r['variant_name']==native['variant']).copy();row.update(variant_name=KEY,variant_filename=KEY,low_poly_filename='',super_low_poly_filename='');tables['variants']=(h,[row])
dbfiles=[]
for name,(header,rows) in tables.items():
 internal='db/'+name+'_tables/zz_mc_moon_jade_reskin';p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True);head=copy.deepcopy(header);head[1][0]=';'.join(head[1][0].split(';')[:2]+[internal])
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows(head+[[r[k] for k in head[0]] for r in rows])
 dbfiles.append(internal)
models={m['key']:m for m in E['models']};root=ET.Element('VARIANT_MESH')
for slot_name,keys,attach,metadata in [('body',['body'],None,'audio_armour_type:plate'),('head',['head_%02d'%i for i in range(1,8)],None,'audio_entity_type:wh3_cth_human_male'),('weapon_2',['dao'],'weapon_2','audio_melee_weapon_type:sword'),('weapon_3',['shield'],'weapon_3','audio_shield_type:wood')]:
 slot=ET.SubElement(root,'SLOT',name=slot_name,**({'attach_point':attach} if attach else {}))
 for key in keys:
  node=ET.SubElement(slot,'VARIANT_MESH',model=models[key]['path']);ET.SubElement(node,'META_DATA').text=metadata
for name in ['weapon_1','weapon_4','weapon_5']:ET.SubElement(root,'SLOT',name=name,attach_point=name)
internal='variantmeshes/variantmeshdefinitions/'+KEY+'.variantmeshdefinition';p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);ET.indent(root);p.write_bytes(ET.tostring(root,encoding='utf-8'))
assets=[internal]+[m['path'] for m in E['models']]+sorted(E['textures'])
assert len(set(assets))==len(assets)
for asset in assets:assert (O/asset).is_file(),asset
cli('pack','create','-p',P)
cli('pack','add','-p',P,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
for start in range(0,len(assets),24):cli('pack','add','-p',P,'-f',*[str(O/p)+';'+p for p in assets[start:start+24]])
cli('pack','add-dependency-pack','-p',P,'-d','!cr_immortal_empires_expanded.pack')
roundtrip=O/'pack-roundtrip';roundtrip.mkdir(exist_ok=True);cli('pack','extract','-p',P,'-t',C['schema'],'-F','db;'+str(roundtrip))
for internal in dbfiles:assert read(O/(internal+'.tsv'))[1]==read(roundtrip/(internal+'.tsv'))[1]
raw=P.read_bytes();assert raw[:4]==b'PFH5';_,dc,ds,fc,fs,_=struct.unpack_from('<6I',raw,4);pos=28+ds;end=pos+fs;entries=[]
for _ in range(fc):
 size,compression=struct.unpack_from('<IB',raw,pos);pos+=5;assert compression==0;stop=raw.index(0,pos);name=raw[pos:stop].decode().replace('\\','/');pos=stop+1;entries.append((name,size))
assert pos==end;payloads={}
for name,size in entries:payloads[name]=raw[pos:pos+size];pos+=size
assert pos==len(raw)
for asset in assets:assert payloads[asset]==(O/asset).read_bytes(),asset
assert {k for k in payloads if k.startswith('db/')}==set(dbfiles)
assert not any(k.startswith(('script/','ui/','animations/')) for k in payloads)
assert all(k.startswith(('db/','variantmeshes/')) or k.endswith('.rpfm_reserved') for k in payloads)
report=dict(pack=str(P),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),payloads=len(payloads),faction=F,unit=UNIT,head_options=7,db_tables={k:len(v[1]) for k,v in tables.items()},dependencies=['!cr_immortal_empires_expanded.pack'],all_assets_private_namespace=True,native_gameplay_unchanged=True,source_pack_not_required=True,game_runtime_verified=False,deployed=False,roundtrip_db_equal=True,payload_bytes_equal=True)
(O/'pack-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
