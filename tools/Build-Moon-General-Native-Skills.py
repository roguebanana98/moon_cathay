"""V22: six native skills per general; private names, one native Assault swap."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v22-native-skills';O.mkdir(exist_ok=True)
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moon-generals-v20-roundtrip';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v21_general_mounts.pack';PACK=O/'mc_moonshadow_heroes_v22_native_general_skills.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='52f5d8a84b392074c6f135233aaea386a1c52a5f1dbc78b02d1b903ccd246aa2'
T=defaultdict(list);H={};paths={};cache={};loc={};maps={};sources={};files=[]
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t]
def one(t,k,v):
 a=[r for r in native(t)[1] if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def load(t):
 p='db/'+t+'_tables/zzzz_mc_moon_generals';H[t],T[t]=read(B/(p+'.tsv'));paths[t]=p
for t in ['character_skill_nodes','character_skill_nodes_skill_locks','battle_set_piece_armies_characters']:load(t)
original=copy.deepcopy(T)
names=['Lunar Command','Moonlit Bulwark','Might of the Moon','Moonfall Charge','Lunar Impact','Unyielding Advance']
deadly='wh_main_skill_all_all_self_deadly_onslaught';ability='wh_main_character_abilities_deadly_onslaught'
for s in ['mc_assault_general','mc_bastion_general']:
 maps[s]={};sources[s]={}
 for i,name in enumerate(names,1):
  old='wh3_dlc24_skill_cth_celestial_general_unique_'+str(i);donor=deadly if s=='mc_assault_general' and i==2 else old;key=s+'_native_skill_'+str(i);name='Moonlit Onslaught' if donor==deadly else name
  skill=one('character_skills','key',donor);T['character_skills'].append(dict(skill,key=key,localised_name=name));loc['character_skills_localised_name_'+key]=name;maps[s][old]=key;sources[s][key]=donor
  for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key'),('character_skills_to_level_reached_criterias','character_skill')]:
   T[t].extend(dict(r,**{field:key}) for r in native(t)[1] if r[field]==donor)
  nodes=[r for r in T['character_skill_nodes'] if r['key'].startswith(s+'_') and r['character_skill_key']==old];assert len(nodes)==1,(s,old);nodes[0]['character_skill_key']=key
 # Existing native mutually exclusive Bulwark/Hammer/Comet choice is retained.
 for r in T['character_skill_nodes_skill_locks']:
  if r['character_skill_node'].startswith(s+'_'):r['character_skill']=maps[s].get(r['character_skill'],r['character_skill'])
 # Match ordinary native CG custom-battle setup; no pregranted yellow stats or
 # all three mutually exclusive campaign specializations at once.
 donor_cb=one('battle_set_piece_armies_characters','character_name','wh3_dlc24_cth_cha_celestial_general_yang')
 char=next(r for r in T['battle_set_piece_armies_characters'] if r['agent_subtype']==s);char.update(skillset=donor_cb['skillset'],character_level=donor_cb['character_level'])
for u in ['mc_assault_general_human','mc_assault_general_warhorse','mc_assault_general_great_stag']:
 T['land_units_to_unit_abilites_junctions'].append(dict(ability=ability,land_unit=u,culture='*'))
# Test exact mechanics/icon equality with donors, with only skill keys/names aliased.
for s,mapping in sources.items():
 assert len(mapping)==6
 for key,donor in mapping.items():
  out=next(r for r in T['character_skills'] if r['key']==key);src=one('character_skills','key',donor)
  assert {k:v for k,v in out.items() if k not in ('key','localised_name')}=={k:v for k,v in src.items() if k not in ('key','localised_name')}
  for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key'),('character_skills_to_level_reached_criterias','character_skill')]:
   assert [dict(r,**{field:donor}) for r in T[t] if r[field]==key]==[r for r in native(t)[1] if r[field]==donor]
assert len(T['character_skill_nodes'])==len(original['character_skill_nodes'])
for old,new in zip(original['character_skill_nodes'],T['character_skill_nodes']):assert {k:v for k,v in old.items() if k!='character_skill_key'}=={k:v for k,v in new.items() if k!='character_skill_key'}
assert len(T['character_skill_nodes_skill_locks'])==len(original['character_skill_nodes_skill_locks'])==12
assert all(r['character_skill'] in sources['mc_assault_general' if r['character_skill_node'].startswith('mc_assault_general_') else 'mc_bastion_general'] for r in T['character_skill_nodes_skill_locks'])
for t,rs in T.items():
 if not rs:continue
 h,meta=copy.deepcopy(H.get(t) or native(t)[0]);p=paths.get(t,'db/'+t+'_tables/zzzz_mc_moon_general_native_skills');meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(set(r)==set(h) for r in rs),t
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 files.append(p)
p='text/db/mc_moon_general_native_skills.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(v.isascii() for v in loc.values())
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p);before=unpack(BASE);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files]);after=unpack(PACK)
changed=[p for p in before if before[p]!=after[p]];assert set(changed)==set(paths.values());assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items() if p not in changed)
# Ability/phase/effect definitions, all meshes, textures and five mounts untouched.
assert all(not any(x in p for x in ['/unit_abilities_tables/','/unit_special_abilities_tables/','/special_ability','/effects_tables/']) for p in files)
check=R/'reference/local/moon-generals-v22-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,six_native_skills_per_lord=True,native_skill_mechanics_and_icons_exact=True,native_exclusive_choices_preserved=True,custom_battle_matches_native_cg_setup=True,no_new_abilities_or_phases=True,appearance_mounts_other_heroes_unchanged=True,changed_entries=changed,skill_sources=sources,skill_names=loc,assault_replacement=deadly,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in v if k not in ('skill_sources','skill_names')},indent=2));assert not blocking
