"""Da Anh alone starts with maximum Increase Mobility, without XP or free points."""
import ast,csv,copy,hashlib,json,shutil,subprocess,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/da-anh-v9-mobility';O.mkdir(parents=True,exist_ok=True);BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v8_da_anh.pack';PACK=O/'mc_moonshadow_heroes_v9_da_anh_mobility.pack'
s=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','unpack','cli','read']],type_ignores=[]),'<pack helpers>','exec'))
assert sha(BASE)=='37f3aa7a52438aca2ff56e439feb073d76135890dd5f3ad168036222695a26e6';assert not PACK.exists()
cli('pack','extract','-p',BASE,'-t',C['schema'],'-F','db;'+str(O/'base'))
N=R/'reference/local/lord-vanilla/db';Q=O/'base/db';SK='mc_da_anh_starting_mobility';DONOR='wh2_main_skill_all_hero_assist_army_increase_mobility';db=[]
def save(t,rows,h,internal):
 header,meta=copy.deepcopy(h);meta[0]=';'.join(meta[0].split(';')[:2]+[internal]);p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([header,meta]+[[r.get(k,'') for k in header] for r in rows])
 db.append(internal)
h,nodes=read(Q/'character_skill_nodes_tables/mc_moonshadow.tsv');before_nodes=copy.deepcopy(nodes);matches=[r for r in nodes if r['key'].startswith('mc_da_anh_') and r['character_skill_key']==DONOR];assert len(matches)==1
node=matches[0];node.update(character_skill_key=SK,points_on_creation='3');save('character_skill_nodes',nodes,h,'db/character_skill_nodes_tables/mc_moonshadow')
h,skills=read(N/'character_skills_tables/data__.tsv');row=next(r for r in skills if r['key']==DONOR).copy();row.update(key=SK,localised_name='Increase Mobility',localised_description='Da Anh begins with all three ranks of Increase Mobility. Embed her in an army to improve its campaign movement range.',unlocked_at_rank='0');save('character_skills',[row],h,'db/character_skills_tables/mc_da_anh_mobility')
h,details=read(N/'character_skill_level_details_tables/data__.tsv');template=next(r for r in details if r['skill_key']==DONOR);levels=[]
for rank in (1,2,3):
 row=template.copy();row.update(skill_key=SK,level=str(rank),unlocked_at_rank='0');levels.append(row)
save('character_skill_level_details',levels,h,'db/character_skill_level_details_tables/mc_da_anh_mobility')
h,effects=read(N/'character_skill_level_to_effects_junctions_tables/data__.tsv');effects=[dict(r,character_skill_key=SK) for r in effects if r['character_skill_key']==DONOR];assert {r['level']:r['value'] for r in effects}=={'1':'5.0000','2':'10.0000','3':'15.0000'};save('character_skill_level_to_effects_junctions',effects,h,'db/character_skill_level_to_effects_junctions_tables/mc_da_anh_mobility')
loc='text/db/mc_da_anh_mobility.loc';p=O/(loc+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+loc,'',''],['character_skills_localised_name_'+SK,'Increase Mobility','true'],['character_skills_localised_description_'+SK,'Da Anh begins with all three ranks of Increase Mobility. Embed her in an army to improve its campaign movement range.','true']])
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in db+[loc]])
before=unpack(BASE);after=unpack(PACK);changed=[p for p in before if before[p]!=after[p]];assert changed==['db/character_skill_nodes_tables/mc_moonshadow'],changed
assert set(after)==set(before)|set(db)|{loc}
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(O/'roundtrip'))
for p in db:assert read(O/(p+'.tsv'))[1]==read(O/('roundtrip/'+p+'.tsv'))[1]
new=read(O/'roundtrip/db/character_skill_nodes_tables/mc_moonshadow.tsv')[1]
assert [r for r in before_nodes if r['key']!=node['key']]==[r for r in new if r['key']!=node['key']]
assert next(r for r in new if r['key']==node['key'])['points_on_creation']=='3'
# Vanilla already uses points_on_creation=3 for fully granted starting skills.
assert any(r['points_on_creation']=='3' for r in read(N/'character_skill_nodes_tables/data__.tsv')[1])
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();d=json.loads(text[text.index('{'):]);blocking=[]
for g in d['results']:
 for kind,item in g.items():
  for issue in item.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=item.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),changed_entries=changed,new_entries=sorted(set(after)-set(before)),blocking_diagnostics=blocking,character='mc_da_anh',skill=SK,starting_rank=3,maximum_rank=3,rank_requirement=0,skill_effect_values=[5,10,15],normal_assassin_unchanged=True,all_appearance_assets_unchanged=True,spawn_lua_unchanged=True,new_campaign_required=True,retroactive_to_existing_characters=False,free_skill_points_granted=0,xp_granted=0,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not blocking
