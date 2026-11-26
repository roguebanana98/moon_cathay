"""V26: faction-scoped recruitment adjustments and authored Vietnamese name bank."""
import ast,copy,csv,hashlib,json,re,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v26-recruitment-names';O.mkdir(exist_ok=True)
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/assault-v25-roundtrip';F='cr_cth_agents_of_the_moon';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v25_assault_campaign.pack';PACK=O/'mc_moonshadow_heroes_v26_recruitment_names.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='7c8aca0609149db94d5a01ac77aea31e7655c4882ca1dbe6be57b6e2821fa283'
T={};H={};original={};files=[];cache={};loc={}
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t]
def save(t,rs,header=None,path=None):
 p=path or 'db/'+t+'_tables/zzzzzz_mc_moon_campaign';h,meta=copy.deepcopy(header or native(t)[0]);meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 assert all(set(r)==set(h) for r in rs),(t,set(rs[0])-set(h))
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 files.append(p)
# Permission records disable recruitment only; keep native character definitions,
# native capacity effects and the replacement heroes' availability untouched.
p='db/faction_agent_permitted_subtypes_tables/zzzz_mc_moonveil';head,permissions=read(B/(p+'.tsv'));old_permissions=copy.deepcopy(permissions)
assert next(r for r in permissions if r['subtype']=='wh3_main_cth_alchemist')['mod_disabled']=='true'
assert not any(r['subtype']=='wh3_main_cth_astromancer' for r in permissions)
permissions.append(dict(agent='wizard',faction=F,subtype='wh3_main_cth_astromancer',mod_disabled='true'));save('faction_agent_permitted_subtypes',permissions,head,p)
assert permissions[:-1]==old_permissions and all(r['faction']==F for r in permissions)
# Both availability and its existing +1 capacity move, otherwise a tier2 unlock
# would still be unusable until the former tower supplied the first capacity.
p='db/building_effects_junction_tables/mc_moonshadow';head,building=read(B/(p+'.tsv'));original['buildings']=copy.deepcopy(building);assert len(building)==6
assert {r['building'] for r in building}=={'wh3_main_cth_magic_tower_'+str(i) for i in [1,2,3]}
templates={r['effect']:r for r in building if r['building']=='wh3_main_cth_magic_tower_1'};assert set(templates)=={'mc_moonshadow_recruitment','mc_moonshadow_capacity'}
targets=['wh3_main_cth_jade_barracks_2','wh3_main_cth_jade_barracks_3'];levels=native('building_levels')[1]
assert all(any(r['level_name']==b and r['chain']=='wh3_main_cth_jade_barracks' for r in levels) for b in targets)
building=[dict(r,building=b) for b in targets for r in templates.values()];save('building_effects_junction',building,head,p)
assert len(building)==4 and all(r['context_requirement']=='mc_moonshadow_owner' and r['value']=='1.0000' for r in building)
# Read the current effective IEE faction row, not a guessed vanilla faction or an
# old template, so flags/colours and unrelated faction settings are preserved.
refs=json.loads((R/'build/moon-v26-faction-records.json').read_text());assert len(refs)==1;source=refs[0];assert sha(source['pack'])==source['sha256'];head,factions=read(Path(source['tsv']));faction=next(r for r in factions if r['key']==F);old_faction=dict(faction)
data_path=R/'src/data/agents-of-the-moon-vietnamese-names.json';data=json.loads(data_path.read_text());group=data['name_group'];entries=data['entries'];assert data['faction']==F and data['display_order']==['family_name','forename']
assert not any(r['key']==group for r in native('names_groups')[1]);assert len({r['id'] for r in entries})==len(entries)
used={r['id'] for r in native('names')[1]}
used.update(r['id'] for p in (B/'db/names_tables').glob('*.tsv') for r in read(p)[1]);assert not used&{r['id'] for r in entries}
seen=set()
for r in entries:
 assert set(r)=={'id','type','gender','frequency','text'} and r['type'] in ['family_name','forename'] and r['gender'] in ['m','f','b'] and r['frequency']>0
 assert r['text'].isascii() and re.fullmatch('[A-Za-z]+(?: [A-Za-z]+)*',r['text']);key=(r['type'],r['gender'],r['text'].casefold());assert key not in seen;seen.add(key)
 loc['names_name_'+r['id']]=r['text']
counts=dict(surnames=sum(r['type']=='family_name' for r in entries),male_given_names=sum(r['type']=='forename' and r['gender']=='m' for r in entries),female_given_names=sum(r['type']=='forename' and r['gender']=='f' for r in entries),unisex_given_names=sum(r['type']=='forename' and r['gender']=='b' for r in entries),records=len(entries))
assert all(data['statistics'][k]==v for k,v in counts.items())
faction=dict(faction,name_group=group);assert {k:v for k,v in faction.items() if k!='name_group'}=={k:v for k,v in old_faction.items() if k!='name_group'};save('factions',[faction],head)
save('names_groups',[dict(key=group)])
save('names',[dict(id=r['id'],names_group=group,type=r['type'],gender=r['gender'],frequency=str(r['frequency'])) for r in entries])
orders=[]
for language in ['', 'cn','kr','zh']:
 for i,kind in enumerate(['family_name','forename','clan_name','other']):orders.append(dict(order=str(i),type=kind,name_group=group,optional_language=language))
save('name_orders',orders)
# The eight authored regular subtypes explicitly select the new group. Native
# human subtypes with blank overrides inherit the faction's group; fixed named
# characters and native nonhuman subtype-specific name groups are not rewritten.
renamed=[];changed_subtype_tables=[]
for path in (B/'db/agent_subtypes_tables').glob('*.tsv'):
 header,rs=read(path);old=copy.deepcopy(rs)
 for r in rs:
  if r['auto_generate']=='true' and (r['key'].startswith('mc_') or r['key']=='Luke_cth_master_engineer'):
   r['names_group']=group;renamed.append(r['key'])
 if rs!=old:
  p=path.relative_to(B).as_posix()[:-4];save('agent_subtypes',rs,header,p);changed_subtype_tables.append(p)
  for a,b in zip(old,rs):assert {k:v for k,v in a.items() if k!='names_group'}=={k:v for k,v in b.items() if k!='names_group'}
assert set(renamed)=={'mc_assault_general','mc_bastion_general','mc_pyromancer','mc_tidecaller','mc_astral_weaver','mc_moonveil_adept','mc_moonshadow_assassin','Luke_cth_master_engineer'}
p='text/db/mc_moon_vietnamese_names.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p);before=unpack(BASE);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files]);after=unpack(PACK)
changed=[p for p in before if after[p]!=before[p]];assert set(changed)==set(changed_subtype_tables)|{'db/building_effects_junction_tables/mc_moonshadow','db/faction_agent_permitted_subtypes_tables/zzzz_mc_moonveil'}
assert set(after)==set(before)|set(files);assert all(after[p]==b for p,b in before.items() if p not in changed)
assert all(after[p]==b for p,b in before.items() if p.startswith(('script/','variantmeshes/','ui/','db/character_skill')))
check=R/'reference/local/moon-v26-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group_result in diag['results']:
 for kind,g in group_result.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,faction=F,native_astromancer_alchemist_recruitment_disabled=True,assassin_buildings=targets,assassin_capacity_per_building=1,tower_assassin_effects_removed=True,native_buildings_stats_costs_unchanged=True,name_group=group,name_statistics=data['statistics'],name_dataset=str(data_path),name_dataset_sha256=sha(data_path),custom_subtypes_with_private_names=renamed,faction_source=source,other_faction_fields_unchanged=True,fixed_named_characters_unchanged=True,models_skills_campaign_scripts_unchanged=True,changed_entries=changed,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in v if k not in ('faction_source','changed_entries')},indent=2));assert not blocking
