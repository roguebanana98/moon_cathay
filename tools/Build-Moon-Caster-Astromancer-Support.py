"""V23: seven unmodified native Astromancer support skills for three moon casters."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess,unicodedata
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-casters-v23-astromancer-support';O.mkdir(exist_ok=True)
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moon-generals-v22-roundtrip';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v22_native_general_skills.pack';PACK=O/'mc_moonshadow_heroes_v23_caster_support.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='9770b6e5e89cfa4dd3f1983d2379a83e8b75feabcfeb1717270a60571e086f48'
T=defaultdict(list);cache={};loc={};files=[];mapping={};audit=[]
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t]
def rows(t):return native(t)[1]
def one(t,k,v):
 a=[r for r in rows(t) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def ascii_text(s):return unicodedata.normalize('NFKD',s.replace('\u2019',"'").replace('\u2018',"'").replace('\u2013','-').replace('\u2014','-')).encode('ascii','ignore').decode()
spec=[('attuned_to_the_elements','Attuned to the Moon'),('martial_interests','Martial Discipline'),('master_advisor','Counsel of the Moon'),('celestial_syphon','Lunar Conduit'),('astromantic_ward','Moonlit Warding'),('heavenly_bonds','Moonbound Beasts'),('peerless_astromancy','Mastery of the Moon')]
for suffix,name in spec:
 old='wh3_cp1_skill_cth_astromancer_'+suffix;new='mc_moon_caster_support_'+suffix;mapping[old]=new;skill=one('character_skills','key',old)
 T['character_skills'].append(dict(skill,key=new,localised_name=name,localised_description=ascii_text(skill['localised_description'])));loc['character_skills_localised_name_'+new]=name
 for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key'),('character_skills_to_level_reached_criterias','character_skill')]:T[t].extend(dict(r,**{field:new}) for r in rows(t) if r[field]==old)
 audit.append(dict(native_skill=old,skill=new,name=name))
native_nodes={r['key']:r for r in rows('character_skill_nodes')};items=[r for r in rows('character_skill_node_set_items') if r['set']=='wh3_main_skill_node_set_cth_astromancer' and r['mod_disabled']=='false'];selected=[native_nodes[r['item']] for r in items if native_nodes[r['item']]['character_skill_key'] in mapping];assert len(selected)==7
all_existing_nodes={r['key']:r for p in (B/'db/character_skill_nodes_tables').glob('*.tsv') for r in read(p)[1]};existing_items=[r for p in (B/'db/character_skill_node_set_items_tables').glob('*.tsv') for r in read(p)[1]]
casters=['mc_pyromancer','mc_tidecaller','mc_astral_weaver'];checks=[]
for s in casters:
 old_items=[r for r in existing_items if r['set']==s+'_skills' and r['mod_disabled']=='false'];oldnodes=[all_existing_nodes[r['item']] for r in old_items];occupied={(r['indent'],r['tier']) for r in oldnodes if r['visible_in_ui']=='true'}
 assert len(old_items)==41 and not any(r['character_skill_key'] in mapping for r in oldnodes)
 nm={r['key']:s+'_support_node_'+str(i) for i,r in enumerate(selected)}
 for node in selected:
  assert (node['indent'],node['tier']) not in occupied
  out=dict(node,key=nm[node['key']],character_skill_key=mapping[node['character_skill_key']]);T['character_skill_nodes'].append(out);T['character_skill_node_set_items'].append(dict(set=s+'_skills',item=out['key'],mod_disabled='false'))
 for link in rows('character_skill_node_links'):
  if link['parent_key'] in nm and link['child_key'] in nm:T['character_skill_node_links'].append(dict(link,parent_key=nm[link['parent_key']],child_key=nm[link['child_key']]))
 for lock in rows('character_skill_nodes_skill_locks'):
  if lock['character_skill_node'] in nm:
   assert lock['character_skill'] in mapping;T['character_skill_nodes_skill_locks'].append(dict(lock,character_skill=mapping[lock['character_skill']],character_skill_node=nm[lock['character_skill_node']]))
 # Removing Heavens-only cooldown leaves two available alternatives for the
 # original 2-of-3 capstone prerequisite. Keep threshold2, requiring both.
 for node in T['character_skill_nodes'][-7:]:
  incoming=[l for l in T['character_skill_node_links'] if l['child_key']==node['key'] and l['link_type']=='SUBSET_REQUIRED'];assert len(incoming)>=int(node['required_num_parents'])
 checks.append(dict(subtype=s,before_nodes=len(old_items),after_nodes=len(old_items)+7,new_nodes=7,new_links=sum(r['child_key'].startswith(s+'_') for r in T['character_skill_node_links']),exclusive_locks=sum(r['character_skill_node'].startswith(s+'_') for r in T['character_skill_nodes_skill_locks'])))
assert len(T['character_skill_nodes'])==21 and len(T['character_skill_node_set_items'])==21 and len(T['character_skill_node_links'])==12 and len(T['character_skill_nodes_skill_locks'])==18
for old,new in mapping.items():
 out=next(r for r in T['character_skills'] if r['key']==new);src=one('character_skills','key',old);assert {k:v for k,v in out.items() if k not in ('key','localised_name','localised_description')}=={k:v for k,v in src.items() if k not in ('key','localised_name','localised_description')}
 for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key'),('character_skills_to_level_reached_criterias','character_skill')]:assert [dict(r,**{field:old}) for r in T[t] if r[field]==new]==[r for r in rows(t) if r[field]==old]
assert not any('flow_of_azyr' in str(r) or 'ability_cooldown_lore_of_heavens' in str(r) for rs in T.values() for r in rs)
for t,rs in T.items():
 if not rs:continue
 h,meta=copy.deepcopy(native(t)[0]);p='db/'+t+'_tables/mc_moon_caster_support';meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(set(r)==set(h) for r in rs),t
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 files.append(p)
p='text/db/mc_moon_caster_support.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
assert all(v.isascii() for v in loc.values()) and all(r['localised_description'].isascii() for r in T['character_skills'])
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p);before=unpack(BASE);assert not set(files)&set(before);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files]);after=unpack(PACK)
assert set(after)==set(before)|set(files) and all(after[p]==b for p,b in before.items())
check=R/'reference/local/moon-casters-v23-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,existing_payloads_unchanged=True,native_mechanics_icons_rank_gates_exact=True,native_exclusive_choices_preserved=True,capstone_reachable_without_heavens_skill=True,no_new_abilities_or_phases=True,skill_points_per_level_unchanged=True,seven_support_skills_per_caster=True,casters=checks,skills=audit,new_files=files,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in v if k not in ('new_files','skills')},indent=2));assert not blocking
