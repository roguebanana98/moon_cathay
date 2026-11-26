"""Private v12: faction-local English skills and Da Anh's two signature abilities.

Builds on installed v11; never edits native records, appearance, Lua or saves.
"""
import ast, copy, csv, hashlib, json, re, shutil, struct, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O = R/'build/moonshadow-v12-moon-skills'
O.mkdir(parents=True, exist_ok=True)
BASE = Path(C['game'])/'data/mc_moonshadow_heroes_v11_da_anh_handbow.pack'
PACK = O/'mc_moonshadow_heroes_v12_moon_skills.pack'
B = R/'reference/local/moonshadow-v12-base'
N = R/'reference/local/lord-vanilla/db'
if PACK.exists():
    assert '--rebuild' in sys.argv and not (Path(C['game'])/'data'/PACK.name).exists(), 'Preserve installed candidate'
    assert not (O/'deployment.json').exists(), 'Preserve deployed build'
    PACK.unlink()
helpers = ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in ('sha','unpack','cli','read')], type_ignores=[]), '<helpers>', 'exec'))
assert sha(BASE) == '7ed15a7ea89b7cfab44c0096709a7887a872953d4973a985177ff1c9572b40cb'

cache = {}
def native(t):
    if t not in cache: cache[t] = read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def one(t, field, value):
    rows = [dict(x) for x in native(t)[1] if x[field] == value]
    assert len(rows) == 1, (t, field, value, len(rows))
    return rows[0]
tables = {}
headers = {}
def base(t):
    headers[t], tables[t] = read(B/('db/'+t+'_tables/mc_moonshadow.tsv'))
    return tables[t]
for t in ('character_skills','character_skill_level_details','character_skill_level_to_effects_junctions',
          'character_skill_nodes','character_skill_nodes_skill_locks','character_skill_node_links',
          'character_skill_node_set_items','land_units_to_unit_abilites_junctions'):
    base(t)
original = copy.deepcopy(tables)
loc = {}
def localize(kind, key, value):
    assert value.isascii() and '\n' not in value and '\t' not in value
    loc[kind+'_'+key] = value

# Native mechanics and rank requirements are copied verbatim; only our nodes use clones.
renames = [
 ('wh2_main_skill_def_spy_unbreakable','Moonbound Oath','The oath sworn beneath the moon cannot be broken.'),
 ('wh2_main_skill_def_generic_ward_of_khaine','Lunar Aegis','The hidden servants of the moon endure where others fall.'),
 ('wh2_main_skill_all_immortality_hero','Eternal Vigil','A wounded shadow returns to continue the vigil.'),
 ('wh3_main_skill_all_mentor_hero','Teachings of the Moon','Pass the lessons of the hidden path to the next generation.'),
 ('wh2_main_skill_def_spy_poison_1','Moonshade Venom','A subtle poison clouds the senses before the blade strikes.'),
 ('wh2_main_skill_def_spy_poison_2','Heartseeker Venom','A carefully prepared toxin brings even mighty prey low.'),
 ('wh2_main_skill_def_spy_poison_3','Night Lotus','The night lotus conceals a deadly secret within its petals.'),
 ('wh2_main_skill_def_combat_dance_of_death','Moonblade Dance','Each measured step carries the blade past an enemy guard.'),
 ('wh_main_skill_all_spy_self_gutter_fighter_2','Close-Quarters Training','The hidden blade is honed in alleys and narrow passages.'),
 ('wh_main_skill_all_spy_self_elusive','Elusive Shadow','An elusive shadow offers no easy target.'),
 ('wh_main_skill_all_spy_self_precise_2','Measured Strikes','Patience turns the smallest opening into a decisive strike.'),
 ('wh_main_skill_all_spy_self_survivalist_2','Twilight Endurance','Long nights in hostile territory harden body and resolve.'),
 ('wh2_main_skill_def_spy_shroud_of_darkness','Mantle of the Moon','Move unseen beneath the mantle of the moon.'),
 ('wh_main_skill_all_spy_self_fleet-footed','Silent Footsteps','A swift and silent approach leaves little chance of escape.'),
 ('wh_main_skill_all_spy_self_opportunist','Exploit the Opening','Strike when the enemy is least prepared.'),
 ('wh_main_skill_all_spy_self_counter-striker_2','Reprisal','A failed enemy strike invites a swift reply.'),
 ('wh_main_skill_all_spy_self_bloody_blade','Moonforged Blade','A blade kept ready for the final moment.'),
 ('wh2_main_skill_skv_trophy_heads_assassin','Moonshadow Execution','Weaken a chosen enemy before delivering the killing blow.'),
 ('wh2_main_skill_def_assassin_missile_range_hawk_eyed','Moonlit Sight','Even distant prey cannot escape a patient gaze.'),
 ('wh_dlc05_skill_wef_general_personal_buff_missile_damage','Moonpiercer Bolts','Carefully prepared bolts pierce through the enemy defences.'),
 ('wh2_main_skill_def_combat_deadeye','Unerring Aim','A steady hand guides every shot towards its mark.'),
 ('wh2_main_skill_all_hero_assist_army_increase_mobility','Hidden Paths','Lead the army along concealed routes through hostile lands.'),
 ('wh2_main_skill_all_hero_hinder_settlement_assault_garrison','Sabotage the Watch','Strike the watch before the garrison can sound the alarm.'),
 ('wh2_main_skill_all_hero_hinder_agent_assassinate','Silent Elimination','Remove an enemy agent with a single unseen strike.'),
 ('wh2_main_skill_all_hero_hinder_army_assault_units','Strike from the Shadows','Harass enemy soldiers before they reach the battlefield.'),
 ('wh2_main_skill_all_hero_reduce_action_cost','Covert Preparation','Careful preparation reduces the cost of covert operations.'),
 ('wh2_main_skill_all_hero_hinder_settlement_damage_building','Sabotage the Foundations','Quietly undermine the structures that support the enemy.'),
]
mapping = {old:'mc_moon_skill_'+re.sub('[^a-z0-9]+','_',name.lower()).strip('_') for old,name,_ in renames}
assert len(mapping) == len(set(mapping.values())) == 27
visible_native = {r['character_skill_key'] for r in tables['character_skill_nodes'] if r['visible_in_ui']=='true' and not r['character_skill_key'].startswith('mc_')}
assert visible_native == set(mapping), visible_native ^ set(mapping)
for old, name, desc in renames:
    key = mapping[old]
    assert not any(r['key']==key for r in native('character_skills')[1])
    row = one('character_skills','key',old)
    row.update(key=key, localised_name=name, localised_description=desc)
    tables['character_skills'].append(row)
    for t, field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key')]:
        tables[t].extend(dict(r, **{field:key}) for r in native(t)[1] if r[field]==old)
    localize('character_skills_localised_name',key,name)
    localize('character_skills_localised_description',key,desc)
for row in tables['character_skill_nodes']:
    row['character_skill_key'] = mapping.get(row['character_skill_key'],row['character_skill_key'])
for row in tables['character_skill_nodes_skill_locks']:
    row['character_skill'] = mapping.get(row['character_skill'],row['character_skill'])

TROPHY = 'wh2_main_character_abilities_assassins_trophy'
ONSLAUGHT = 'wh_main_character_abilities_deadly_onslaught'
PREY = 'mc_da_anh_moonlit_prey'
LAST = 'mc_da_anh_last_shadow_ability'
def ability(key, name, donor, seconds, cooldown, uid, stats, tooltip):
    effect = key+'_enable'
    for t in ('unit_abilities','unit_special_abilities','special_ability_phases',
              'special_ability_to_special_ability_phase_junctions','special_ability_phase_stat_effects',
              'effects','effect_bonus_value_unit_ability_junctions'):
        tables.setdefault(t, [])
    assert not any(r['unique_id']==str(uid) for r in native('unit_special_abilities')[1])
    a = one('unit_abilities','key',donor)
    a.update(key=key,requires_effect_enabling='true',uniqueness='wh_main_anc_group_unique')
    tables['unit_abilities'].append(a)
    s = one('unit_special_abilities','key',donor)
    s.update(key=key,unique_id=str(uid),active_time=f'{seconds:.4f}',recharge_time=f'{cooldown:.4f}',num_uses='-1',mana_cost='0.0000')
    if key == PREY: s.update(target_intercept_range='100.0000')
    tables['unit_special_abilities'].append(s)
    j = [dict(r) for r in native('special_ability_to_special_ability_phase_junctions')[1] if r['special_ability']==donor]
    assert len(j)==1
    phase = one('special_ability_phases','id',j[0]['phase'])
    phase.update(id=key,duration=f'{seconds:.4f}')
    tables['special_ability_phases'].append(phase)
    j[0].update(special_ability=key,phase=key)
    tables['special_ability_to_special_ability_phase_junctions'].extend(j)
    tables['special_ability_phase_stat_effects'].extend(dict(phase=key,stat=stat,value=f'{value:.4f}',how=how) for stat,value,how in stats)
    # Keep native targeting/usage safety flags; no new cast stance or skeleton dependency.
    for t in ('special_ability_to_invalid_target_flags','special_ability_to_invalid_usage_flags',
              'special_ability_to_auto_deactivate_flags','special_ability_to_recharge_contexts'):
        rows = [dict(r,special_ability=key) for r in native(t)[1] if r['special_ability']==donor]
        if rows: tables.setdefault(t,[]).extend(rows)
    e = one('effects','effect','wh2_main_effect_ability_enable_skv_trophy_heads_assassin')
    e['effect'] = effect
    tables['effects'].append(e)
    tables['effect_bonus_value_unit_ability_junctions'].append(dict(effect=effect,bonus_value_id='enable',unit_ability=key))
    tables['land_units_to_unit_abilites_junctions'].append(dict(ability=key,land_unit='mc_da_anh_human',culture='*'))
    localize('unit_abilities_onscreen_name',key,name)
    localize('unit_abilities_tooltip_text',key,tooltip)
    localize('special_ability_phases_onscreen_name',key,name)
    localize('effects_description',effect,'Ability: '+name)
    return effect

prey_desc = 'Marks an enemy lord or hero within 100m for 20 seconds: -15 Melee Defence and -20% Speed. Cooldown: 90 seconds. No Winds of Magic cost.'
last_desc = 'For 10 seconds, Da Anh gains +50% base and armour-piercing melee damage, but loses 15 Melee Defence. Cooldown: 120 seconds. No Winds of Magic cost.'
prey_effect = ability(PREY,'Moonlit Prey',TROPHY,20,90,1800312901,
                      [('stat_melee_defence',-15,'add'),('scalar_speed',0.8,'mult')],prey_desc)
last_effect = ability(LAST,'The Last Shadow',ONSLAUGHT,10,120,1800312902,
                      [('stat_melee_damage_base',1.5,'mult'),('stat_melee_damage_ap',1.5,'mult'),('stat_melee_defence',-15,'add')],last_desc)
tables['land_units_to_unit_abilites_junctions'] = [r for r in tables['land_units_to_unit_abilites_junctions'] if not(r['land_unit']=='mc_da_anh_human' and r['ability']==TROPHY)]
execution = next(r for r in tables['character_skills'] if r['key']=='mc_da_anh_execution')
execution.update(localised_name='Moonlit Prey',localised_description=prey_desc)
for r in tables['character_skill_level_to_effects_junctions']:
    if r['character_skill_key']=='mc_da_anh_execution': r['effect_key']=prey_effect
last_skill = dict(execution,key='mc_da_anh_last_shadow',localised_name='The Last Shadow',localised_description=last_desc,
                  unlocked_at_rank='19',image_path=one('character_skills','key','wh_main_skill_all_all_self_deadly_onslaught')['image_path'])
tables['character_skills'].append(last_skill)
detail = next(r for r in tables['character_skill_level_details'] if r['skill_key']=='mc_da_anh_execution')
tables['character_skill_level_details'].append(dict(detail,skill_key=last_skill['key'],unlocked_at_rank='19',image_path=last_skill['image_path']))
tables['character_skill_level_to_effects_junctions'].append(dict(character_skill_key=last_skill['key'],effect_key=last_effect,level='1',effect_scope='character_to_character_own',value='1.0000'))
for skill in (execution,last_skill):
    localize('character_skills_localised_name',skill['key'],skill['localised_name'])
    localize('character_skills_localised_description',skill['key'],skill['localised_description'])
nodes = tables['character_skill_nodes']
next(r for r in nodes if r['key']=='mc_da_anh_supply_node')['tier']='1'
prey_node = next(r for r in nodes if r['key']=='mc_da_anh_node_15')
prey_node['tier']='2'
last_node = dict(prey_node,key='mc_da_anh_last_shadow_node',character_skill_key=last_skill['key'],tier='3',required_num_parents='1')
nodes.append(last_node)
tables['character_skill_node_set_items'].append(dict(set='mc_da_anh_skills',item=last_node['key'],mod_disabled='false'))
link = dict(tables['character_skill_node_links'][0])
link.update(child_key=last_node['key'],parent_key=prey_node['key'],link_type='REQUIRED')
tables['character_skill_node_links'].append(link)

# Invariants: renamed skills have exactly the native effects/ranks and original node IDs.
for old,_,_ in renames:
    key = mapping[old]
    for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key')]:
        assert [dict(r,**{field:old}) for r in tables[t] if r[field]==key] == [r for r in native(t)[1] if r[field]==old]
assert len({r['key'] for r in nodes})==len(nodes)==len(original['character_skill_nodes'])+1
assert {r['key'] for r in original['character_skill_nodes']} < {r['key'] for r in nodes}
nodekeys={r['key'] for r in nodes}
assert all(r['parent_key'] in nodekeys and r['child_key'] in nodekeys for r in tables['character_skill_node_links'])
assert all(r['character_skill_node'] in nodekeys and r['character_skill'] in mapping.values() for r in tables['character_skill_nodes_skill_locks'])
assert len(tables['character_skill_nodes_skill_locks'])==len(original['character_skill_nodes_skill_locks'])==12
assert all(r['points_on_creation']=='0' for r in nodes if r['visible_in_ui']=='true')
assert [r for r in tables['land_units_to_unit_abilites_junctions'] if r['land_unit']!='mc_da_anh_human']==[r for r in original['land_units_to_unit_abilites_junctions'] if r['land_unit']!='mc_da_anh_human']
for a in (PREY,LAST):
    assert one('unit_abilities','key',TROPHY)['requires_effect_enabling']=='true'
    assert [r['land_unit'] for r in tables['land_units_to_unit_abilites_junctions'] if r['ability']==a]==['mc_da_anh_human']

files = []
for t, rows in tables.items():
    h,m = copy.deepcopy(headers.get(t) or native(t)[0])
    internal='db/'+t+'_tables/'+('mc_moonshadow' if t in headers else 'mc_moon_skills')
    m[0]=';'.join(m[0].split(';')[:2]+[internal])
    p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rows),t
    with p.open('w',encoding='utf8',newline='') as f:
        csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
    files.append(internal)
# Update existing private localization in place to avoid competing duplicate loc keys.
locpaths = list((B/'text/db').glob('*.loc.tsv'))
assert locpaths
left = dict(loc)
for source in locpaths:
    h,rows = read(source)
    for r in rows:
        if r['key'] in left: r['text']=left.pop(r['key'])
    internal=source.relative_to(B).as_posix()[:-4]
    p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:
        csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows(h+[[r[k] for k in h[0]] for r in rows])
    files.append(internal)
internal='text/db/mc_moon_skills.loc';p=O/(internal+'.tsv')
with p.open('w',encoding='utf8',newline='') as f:
    csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+[[k,v,'true'] for k,v in left.items()])
files.append(internal)
icons = []
icon_reference=R/'reference/local/moonshadow-v12-icons'
for key,donor in ((PREY,TROPHY),(LAST,ONSLAUGHT)):
    source='ui/battle ui/ability_icons/'+donor+'.png'
    cli('pack','extract','-p',Path(C['game'])/'data/ui.pack','-f',source+';'+str(icon_reference))
    internal='ui/battle ui/ability_icons/'+key+'.png'
    p=O/internal;p.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(icon_reference/source,p)
    icons.append(internal)
shutil.copy2(BASE,PACK)
cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files])
cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in icons])
before=unpack(BASE);after=unpack(PACK)
assert set(after)==set(before)|set(files)|set(icons)
assert all(after[p]==data for p,data in before.items() if p not in files)
assert before['script/campaign/mod/mc_moonshadow_start.lua']==after['script/campaign/mod/mc_moonshadow_start.lua']
roundtrip=R/'reference/local/moonshadow-v12-roundtrip';roundtrip.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(roundtrip),'text;'+str(roundtrip))
for p in files: assert read(O/(p+'.tsv'))[1]==read(roundtrip/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diagnostics=json.loads(text[text.index('{'):]);blocking=[]
for group in diagnostics['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}): blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,
            renamed_skills=[dict(original=old,key=mapping[old],name=name) for old,name,_ in renames],
            new_abilities=[PREY,LAST],personal_skills=['Moonshadow Veil','Sever the Supply Lines','Moonlit Prey','The Last Shadow'],personal_skill_display_ranks=[6,8,12,20],
            existing_node_ids_preserved=True,renamed_native_effects_and_ranks_preserved=True,poison_locks_preserved=True,starting_movement_fix_unchanged=True,
            appearance_stats_recruitment_unchanged=True,roundtrip_passed=True,english_ascii_localization=True,old_save_skill_migration_verified=False,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2));assert not blocking
