"""Add a frontend-only early rescue prototype to the undeployed chapter-1 candidate."""
import ast,csv,hashlib,json,shutil,struct,subprocess
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/da-lien-v24-check/db'
O=R/'build/huyen-ve-v25-rescue-prototype';O.mkdir(exist_ok=True)
BASE=R/'build/huyen-ve-v25-quest-candidate/mc_huyen_ve_v25_quest_chapter1_candidate.pack'
PACK=O/'mc_huyen_ve_v25_rescue_prototype_v4.pack'
S=json.loads((R/'src/campaign/huyen-ve-rescue-battle.json').read_text());KEY=S['key'];T=defaultdict(list);files=[]
def read_path(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
cache={}
def native(t):
    if t not in cache:cache[t]=read_path(N/(t+'_tables/data__.tsv'))
    return cache[t]
def one(t,col,key):
    a=[x for x in native(t)[1] if x[col]==key];assert len(a)==1,(t,key);return dict(a[0])
def existing(t):return [r for p in (B/(t+'_tables')).glob('*.tsv') for r in read_path(p)[1]]
def write(t,rs):
    (h,m),_=native(t);m=m.copy();p='db/'+t+'_tables/mc_huyen_ve_rescue';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
basebattle=one('battle_set_pieces','battle_name',S['native_map_donor'])
battle=dict(basebattle,battle_name=KEY,battle_script='script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua',teleport_cost='0',battle_environment_audio='',culture='wh3_main_cth_cathay')
T['battle_set_pieces']=[battle]
T['scripted_objectives']=[dict(key=k,icon_path='') for k in
    ['mc_rescue_defeat_besiegers','mc_rescue_protect_da_lien']]
army_donors=S['native_army_donors']
for side,donor in army_donors.items():
    a=one('battle_set_piece_armies','army_name',donor)
    a.update(army_name=KEY+'_'+side,faction=S[side]['faction'],use_default_deployment_zones='true')
    assert a['is_reinforcement_army']=='false',side
    T['battle_set_piece_armies'].append(a)
    T['battle_set_piece_armies_junctions'].append(dict(army_name=a['army_name'],battle_name=KEY))
allmain={x['unit'] for x in native('main_units')[1]}|{'mc_da_lien_human','mc_moon_warden_human'}
for side,units in [('player',S['player']['frontend_units']),('allies',S['allies']['units']),('enemies',S['enemies']['units'])]:
    for i,(unit,count) in enumerate(units):
        assert unit in allmain,unit
        name=KEY+'_'+side+'_unit_'+str(i)
        T['battle_set_piece_armies_units'].append(dict(unit_name=name,unit_level='0',unit_type=unit,percentage_num_men='100',percentage_num_health='100',reduce_max_number='false'))
        T['battle_set_piece_armies_units_junctions'].append(dict(army_name=KEY+'_'+side,unit_name=name,script_name={'player':'mc_rescue_player','allies':'mc_rescue_escort','enemies':'mc_rescue_besiegers'}[side],number_of_unit=str(count)))
chars=existing('battle_set_piece_armies_characters')
player=dict(next(x for x in chars if x['character_name']=='mc_moon_warden_human'),character_name=KEY+'_player_lord',character_level='8',skillset=KEY+'_player_skills')
da_lien=dict(next(x for x in chars if x['character_name']=='mc_da_lien_human'),character_name=KEY+'_da_lien',character_level='5',skillset=KEY+'_da_lien_skills')
escort=dict(one('battle_set_piece_armies_characters','character_name','wh3_cp1_cth_cha_qb_lord_magistrate'),character_name=KEY+'_escort_lord',skillset='')
enemy=dict(one('battle_set_piece_armies_characters','character_name','wh_main_chs_cha_chaos_lord_0'),character_name=KEY+'_enemy_lord',character_level='2',skillset='')
T['battle_set_piece_armies_characters']=[player,da_lien,escort,enemy]
T['battle_set_piece_armies_characters_junctions']=[dict(army_name=KEY+'_'+side,character_name=c['character_name'],script_name=label) for c,side,label in [(player,'player','mc_rescue_player'),(da_lien,'allies','mc_da_lien_proxy'),(escort,'allies','mc_rescue_escort'),(enemy,'enemies','mc_rescue_besiegers')]]
skill=KEY+'_base_magic';donor=one('character_skills','key','wh3_main_skill_all_dummy_agent_actions_cth_alchemist')
donor.update(key=skill,localised_name='Rescue Spell Preset',localised_description='Base spells for the early rescue battle only.')
T['character_skills']=[donor]
T['character_skill_level_details']=[dict(campaign_key='',faction_key='',level='1',skill_key=skill,subculture_key='',image_path='x',unlocked_at_rank='0')]
T['character_skill_level_to_effects_junctions']=[dict(character_skill_key=skill,effect_key=e,level='1',effect_scope='character_to_character_own',value='1.0000') for e in ['wh3_main_effect_ability_enable_blossom_wind','wh_dlc05_effect_ability_enable_earth_blood','wh_dlc05_effect_ability_enable_flesh_to_stone']]
T['battle_set_piece_armies_characters_skillsets']=[dict(key=KEY+'_player_skills'),dict(key=KEY+'_da_lien_skills')]
T['battle_set_piece_armies_characters_skillsets_skills']=[dict(skill=k,skillset_key=KEY+'_player_skills',sort_order=str(i)) for i,k in enumerate(['mc_moon_warden_magic_breath','mc_moon_warden_magic_earth'])]+[dict(skill=skill,skillset_key=KEY+'_da_lien_skills',sort_order='0')]
T['battle_set_piece_armies_characters_items']=[dict(character_item='mc_da_lien_crimson_moonstone',character_name=da_lien['character_name'])]
group=one('battle_set_piece_frontend_groups','key','wh3_dlc24_cth_cha_yuan_bo');group.update(key='mc_moon_warden_human',sort_order='180')
T['battle_set_piece_frontend_groups']=[group]
T['battle_set_piece_frontend_groups_to_characters']=[dict(character=player['character_name'],frontend_group=group['key'])]
for t,rs in T.items():write(t,rs)
loc=[['battle_set_pieces_localised_name_'+KEY,'The Last Moonwatcher','true'],['battle_set_pieces_localised_description_'+KEY,'Rescue Da Lien from a Chaos warband. Defeat the besiegers and keep her alive. Early-game battle prototype.','true'],['scripted_objectives_localised_description_mc_rescue_defeat_besiegers','Defeat the Chaos besiegers.','true'],['scripted_objectives_localised_description_mc_rescue_protect_da_lien','Keep Da Lien alive.','true'],['character_skills_localised_name_'+skill,'Rescue Spell Preset','true'],['character_skills_localised_description_'+skill,'Base Blossom Wind, Earth Blood and Flesh to Stone.','true']]
import re
script=(R/'src/script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua').read_text()
objective_keys=set(re.findall(r'set_objective_on_message\("[^"]+", "([^"]+)"',script))
assert objective_keys=={r['key'] for r in T['scripted_objectives']}
assert all('scripted_objectives_localised_description_'+k in {r[0] for r in loc} for k in objective_keys)
p='text/db/mc_huyen_ve_rescue.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)
p='script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,dest);files.append(p)
# Native all_scripted.lua checks this marker to enable per-session script logs.
# Scoped to the temporary QA pack; never copy into the stable release.
p='script/enable_console_logging';dest=O/p;dest.write_text('quest prototype QA only\n');files.append(p)
assert not PACK.exists();shutil.copy2(BASE,PACK)
for p in files:
    tab=p.startswith('db/') or p.endswith('.loc');args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK)]
    if tab:args+=['-t',C['schema']]
    subprocess.run(args+['-f',str(O/(p+('.tsv' if tab else '')))+';'+p],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(BASE);after=unpack(PACK);assert not set(before)&set(files) and set(after)==set(before)|set(files) and all(after[p]==b for p,b in before.items())
check=R/'reference/local/huyen-ve-rescue-check';check.mkdir(exist_ok=True)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(PACK),'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)],check=True,stdout=subprocess.DEVNULL)
for p in files:
    if p.startswith('db/') or p.endswith('.loc'):assert read_path(O/(p+'.tsv'))[1]==read_path(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(BASE.parent/'diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');metadata=[];blocking=[]
for path,rs in new.items():
    if old.get(path)==rs:continue
    for row in rs:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in row['cells_affected']):metadata.append(dict(path=path,report=row))
        else:blocking.append(dict(path=path,report=row))
(O/'diagnostics-review.json').write_text(json.dumps(dict(metadata=metadata,blocking=blocking),indent=2));assert not blocking,blocking
v=dict(status='rescue_frontend_prototype_static_checks_passed',pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),files=files,prior_payloads_unchanged=True,new_blocking_diagnostics=0,metadata_warnings=len(metadata),campaign_entry_enabled=False,deployed=False,runtime_verified=False,readiness_gates=S['readiness_gates'])
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
