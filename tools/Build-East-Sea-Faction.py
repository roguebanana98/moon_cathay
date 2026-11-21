"""Private Empire faction add-on; preserves the current r8 campaign baseline."""
import csv,hashlib,importlib.util,json,lzma,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
S=json.loads((R/'src/campaign/east-sea-charter.json').read_text());F=S['faction_key']
O=R/'build/east-sea-faction';O.mkdir(exist_ok=True)
BASE=Path(C['game'])/'data/mc_huyen_ve_v25_r8_longvi_city.pack'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='5edf3d2dc32d307ab0184360aa4e60b916a764b9ce8fbc8a178295b36105f087', 'Campaign baseline changed; inspect before rebuilding'
N=R/'reference/local/lord-vanilla/db'
files=[]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],row)) for row in a[2:]]
def native(t):return read(N/(t+'_tables/data__.tsv'))
def write(t,head,rows):
 h,m=head;p='db/'+t+'_tables/edh_east_sea_charter';m=m.copy();m[0]=';'.join(m[0].split(';')[:2]+[p])
 dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[row[k] for k in h] for row in rows])
 files.append(p)
h,rows=native('factions');row=dict(next(r for r in rows if r['key']=='wh_main_emp_nordland'))
_,current=read(R/'reference/local/edh-faction-current/db/factions_tables/zzz_mixu_startpos.tsv')
slot=next(r for r in current if r['key']==F)
assert slot['subculture']=='wh_main_sc_emp_empire'
row.update(key=F,index=slot['index'],uniform_colour_primary='1F3A61',uniform_colour_secondary='B08D57',uniform_colour_tertiary='EEE6D3',banner_colour_primary='1F3A61',banner_colour_secondary='B08D57',banner_colour_tertiary='EEE6D3',primary_colour='1F3A61',primary_colour_hex='1F3A61')
write('factions',h,[row])
# Ordinary Empire infrastructure/roster/character rights, without named vanilla LLs.
copied={}
for t in ['faction_agent_permitted_subtypes','faction_to_faction_groups_junctions','faction_to_mercenary_set_junctions','battle_siege_vehicle_permissions','climbing_ladders_meshes_definitions','faction_rebellion_units_junctions','units_to_exclusive_faction_permissions','faction_set_items','faction_factionwide_recruitment_unit_exclusions_set_junctions']:
 h,rs=native(t);selected=[]
 for r in rs:
  if 'wh_main_emp_nordland' in r.values():selected.append({k:(F if v=='wh_main_emp_nordland' else v) for k,v in r.items()})
 if t=='faction_set_items':
  selected=[r for r in selected if r['set']=='wh3_dlc27_all_regular_factions']
  for i,r in enumerate(selected):r['id']=str(1986111001+i)
 if selected:write(t,h,selected)
 copied[t]=len(selected)
# Localized screen name used by the existing startpos slot; no source assets.
p='text/db/edh_east_sea_charter.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'',''],['factions_screen_name_'+F,S['display_name'],'true'],['factions_screen_adjective_'+F,'East Sea Charter','true']])
files.append(p)
# Steam updated MIXER during QA on Nov 10 01:11 local. Its 35 restored army
# definitions now satisfy all 301 reinforcement rows. Do not ship the obsolete
# v1 empty-table compatibility override against the corrected dependency.

# The MIXER placeholder has an intentionally empty technology set and black flag.
# Replace only these two cached records with the already-installed Empire data.
raw=(O/'base.raw.esf').read_bytes();d=b.Document(raw);root,_=d.decode(16)
factions={n['groups'][0][1]:n for n in b.walk(root) if n['name']=='FACTION'}
target=factions[F];donor=factions['wh_main_emp_nordland']
regions=[n for n in b.walk(root) if n['name']=='REGION' and n['groups'][0][8]==target['groups'][0][0]]
assert not regions,'Reserved faction already owns territory'
def child(n,name):return next(v for v in n['groups'][0] if isinstance(v,dict) and v.get('name')==name)
patches={};changes=[]
for name in ['FACTION_TECHNOLOGY_MANAGER','FACTION_FLAG_AND_COLOURS']:
 a=child(target,name);z=child(donor,name)
 _,_,body,end,_,_=d.header(z['offset'])
 patches[a['offset']]=d.record(a['offset'],raw[body:end])
 changes.append(name)
characters=list(b.walk(child(target,'CHARACTER_ARRAY')))
char=next(n for n in characters if n['name']=='CHARACTER')
details_id=char['groups'][0][1]
# Record native placeholder identity for the Lua preflight, rather than guessing.
(O/'placeholder-character.json').write_text(json.dumps(char,indent=2,default=lambda v:{'bytes':len(v)}))
identities=[n for n in b.walk(root) if n['name']=='CHARACTER_DETAILS' and n['groups'][0][4]==details_id]
assert len(identities)==1 and identities[0]['groups'][0][13]=='wh_main_emp_lord'
(O/'placeholder-details.json').write_text(json.dumps(identities,indent=2,default=lambda v:{'bytes':len(v)}))
edited=d.rewrite(patches)
source=R/'reference/local/edh-faction-base/campaigns/cr_combi_expanded/startpos.esf'
outer=b.Document(source.read_bytes());top,_=outer.decode(16)
c=next(n for n in b.walk(top) if n['name']=='COMPRESSED_DATA');payload,info=c['groups'][0][:2];length,props=info['groups'][0][:2]
assert lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE)==raw
prop=props[0];filters=[{'id':lzma.FILTER_LZMA1,'dict_size':int.from_bytes(props[1:5],'little'),'lc':prop%9,'lp':(prop//9)%5,'pb':prop//45}]
packed=lzma.compress(edited,format=lzma.FORMAT_RAW,filters=filters)
assert lzma.decompress(packed,format=lzma.FORMAT_RAW,filters=filters)==edited
encoded=outer.rewrite({outer.children(c['offset'])[0][0]:b'\x46'+b.var(len(packed))+packed,outer.children(info['offset'])[0][0]:b'\x08'+struct.pack('<I',len(edited))})
(O/'startpos.esf').write_bytes(encoded)
# Prove outside the two selected records and enclosing length headers is identical.
assert len(patches)==2
script='script/campaign/mod/edh_east_sea_charter_start.lua'
pack=O/'edh_east_sea_charter_faction_v2.pack'
def cli(*args):
 r=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
 with (O/'build.log').open('a',encoding='utf-8') as f:f.write(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
assert not pack.exists(), 'Keep existing builds; use a new revision'
cli('pack','create','-p',pack)
for dep in ['!b_mixer.pack','!cr_immortal_empires_expanded.pack',BASE.name]:cli('pack','add-dependency-pack','-p',pack,'-d',dep)
cli('pack','add','-p',pack,'-f',str(O/'startpos.esf')+';campaigns/cr_combi_expanded/startpos.esf','-f',str(R/'src'/script)+';'+script)
for p in files:cli('pack','add','-p',pack,'-t',C['schema'],'-f',str(O/(p+'.tsv'))+';'+p)
report=dict(pack=str(pack),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),faction=F,display_name=S['display_name'],placeholder_index=slot['index'],copied_rows=copied,files=files+[script,'campaigns/cr_combi_expanded/startpos.esf'],startpos_cached_records_changed=changes,base_pack_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),dependency_sha256={k:hashlib.sha256(Path(C[k]).read_bytes()).hexdigest() for k in ['mixer','iee','schema']},new_campaign_only=True,deployed=False,runtime_verified=False)
(O/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
cli('pack','extract','-p',pack,'-t',C['schema'],'-F','/;'+str(R/'reference/local/edh-faction-roundtrip'))
print(json.dumps(report,indent=2))
