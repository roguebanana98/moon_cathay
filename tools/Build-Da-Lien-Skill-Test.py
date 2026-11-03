"""Build private v23: scoped Yin/celestial Da Lien skill tree over approved v22."""
import ast, csv, hashlib, json, shutil, struct, subprocess
from collections import defaultdict
from pathlib import Path

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
N=R/'reference/local/lord-vanilla/db'
B=R/'reference/local/da-lien-v23-base'
O=R/'build/huyen-ve-v23-da-lien-skills';O.mkdir(parents=True,exist_ok=True)
BASE=R/'build/huyen-ve-v22-da-lien-appearance/mc_huyen_ve_v22_da_lien_appearance.pack'
PACK=O/'mc_huyen_ve_v23_da_lien_skills.pack'
U='mc_da_lien_human';SET='mc_da_lien_skills';GROUP='mc_da_lien_moon_arts'
tables=defaultdict(list);files=[];loc=[];manifest=[]

def read_path(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],r)) for r in a[2:]]

cache={}
def native(t):
    if t not in cache:cache[t]=read_path(N/(t+'_tables/data__.tsv'))
    return cache[t]

def one(t,k,v):
    a=[r for r in native(t)[1] if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])

def output(t,rows,filename='mc_da_lien_skills'):
    (h,m),_=native(t);m=m.copy();p='db/'+t+'_tables/'+filename
    m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)<=set(h) for r in rows),t
    with dest.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r.get(k,'') for k in h] for r in rows])
    files.append(p)

def skill(slug,donor,name,row,col,rank=1,custom=None,shift=False,visible=True,free=0):
    key='mc_da_lien_skill_'+slug;node='mc_da_lien_node_'+slug
    s=one('character_skills','key',donor);s.update(key=key,localised_name=name,unlocked_at_rank=str(rank-1),is_background_skill='false',is_female_only_background_skill='false',is_male_only_background_skill='false',background_weighting='0.0000')
    tables['character_skills'].append(s)
    grants=[dict(e,character_skill_key=key) for e in native('character_skill_level_to_effects_junctions')[1] if e['character_skill_key']==donor]
    if custom is not None:
        grants=[dict(character_skill_key=key,effect_key=e,effect_scope=scope,value=f'{v:.4f}',level='1') for e,scope,v in custom]
    if shift:
        grants=[dict(e,level=str(int(e['level'])-1)) for e in grants if int(e['level'])>1]
    assert grants,slug
    maxlevel=max(int(e['level']) for e in grants)
    assert {int(e['level']) for e in grants}==set(range(1,maxlevel+1))
    tables['character_skill_level_to_effects_junctions'].extend(grants)
    old_details={int(d['level']):d for d in native('character_skill_level_details')[1] if d['skill_key']==donor and not d['campaign_key'] and not d['faction_key']}
    for level in range(1,maxlevel+1):
        d=dict(campaign_key='',faction_key='',level=str(level),skill_key=key,subculture_key='',image_path='x',unlocked_at_rank=str(rank-1))
        if custom is None and not shift and level in old_details:
            d['unlocked_at_rank']=str(max(rank-1,int(old_details[level]['unlocked_at_rank'])))
        tables['character_skill_level_details'].append(d)
    n=one('character_skill_nodes','key','wh3_main_skill_node_cth_alchemist_magic_0')
    n.update(key=node,character_skill_key=key,indent=str(row),tier=str(col),points_on_creation=str(free),required_num_parents='0',visible_in_ui=str(visible).lower())
    tables['character_skill_nodes'].append(n)
    tables['character_skill_node_set_items'].append(dict(set=SET,item=node,mod_disabled='false'))
    if visible:
        manifest.append(dict(slug=slug,skill=key,node=node,name=name,levels=maxlevel,row=row,column=col,rank=rank,donor=donor,custom=custom is not None))
    # Native descriptions still explain spells/passives; authored extras below replace custom descriptions.
    description=s['localised_description']
    if not description:description='Learn or improve '+name+'.'
    loc.extend([['character_skills_localised_name_'+key,name,'true'],['character_skills_localised_description_'+key,description,'true']])
    return key,node

def link(child,parents,kind='REQUIRED',threshold=1):
    n=next(n for n in tables['character_skill_nodes'] if n['key']==child);n['required_num_parents']=str(threshold)
    for parent in parents:
        tables['character_skill_node_links'].append(dict(child_key=child,parent_key=parent,initial_descent_tiers='0',parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',child_link_position_offset='0.0000',link_type=kind))

SPELLS=[
 ('blossom','wh3_main_skill_cth_magic_yin_03_blossom_wind','Blossom Wind','wh3_main_spell_yin_blossom_wind',0,1,True),
 ('earth','wh_dlc05_skill_magic_life_wizard_earth_blood','Earth Blood','wh_dlc05_spell_life_earth_blood',2,1,False),
 ('stone','wh_dlc05_skill_magic_life_wizard_flesh_to_stone','Flesh to Stone','wh_dlc05_spell_life_flesh_to_stone',3,1,False),
 ('shadows','wh3_main_skill_cth_magic_yin_02_storm_of_shadows','Storm of Shadows','wh3_main_spell_yin_storm_of_shadows',4,1,False),
 ('talons','wh3_main_skill_cth_magic_yin_07_talons_of_night','Talons of Night','wh3_main_spell_yin_talons_of_night',6,8,False),
 ('comet','wh_main_skill_all_magic_heavens_09_comet_of_casandora','Comet of Casandora','wh_main_spell_heavens_comet_of_casandora',7,8,False)]
active={}
for slug,donor,name,ability,col,rank,shift in SPELLS:
    active[slug]=skill(slug,donor,name,2,col,rank,shift=shift)
power=skill('power_of_yin','wh3_main_skill_cth_magic_yin_05_power_of_yin','Power of Yin',2,1)
evasion=skill('evasion','wh_main_skill_all_magic_all_06_evasion','Evasion',2,5,7)
earthing=skill('earthing','wh_main_skill_all_magic_all_07_earthing','Earthing',2,8,8)
reserves=skill('reserves','wh_main_skill_all_magic_all_08_power_drain','Magical Reserves',2,9,8)
conduit=skill('conduit','wh_main_skill_all_magic_all_11_arcane_conduit','Arcane Conduit',2,10,12)
link(evasion[1],[active[x][1] for x in ['blossom','earth','stone','shadows']]+[power[1]],'SUBSET_REQUIRED',4)
for pair in [active['talons'],active['comet'],earthing,reserves]:link(pair[1],[evasion[1]])
link(conduit[1],[active['talons'][1],active['comet'][1],earthing[1],reserves[1]],'SUBSET_REQUIRED',4)

# Native action framework and backgrounds, not Alchemist magic/self/uniques.
nd={n['key']:n for n in native('character_skill_nodes')[1]}
olditems=read_path(B/'db/character_skill_node_set_items_tables/mc_da_lien.tsv')[1]
background_items=[dict(i) for i in olditems if i['item']=='wh3_main_agent_action_scaling' or '_alchemist_innate_' in i['item']]
tables['character_skill_node_set_items'].extend(background_items)
actions=skill('foundation_actions','wh3_main_skill_all_dummy_agent_actions_cth_alchemist','',8,0,visible=False,free=1)
foundation=skill('foundation_blossom','wh_main_skill_all_magic_metal_dummy_searing_doom','',8,1,visible=False,free=1,
                 custom=[('wh3_main_effect_ability_enable_blossom_wind','character_to_character_own',1)])
for i,(slug,donor,name) in enumerate([
 ('mobility','wh2_main_skill_all_hero_assist_army_increase_mobility','Increase Mobility'),
 ('income','wh2_main_skill_all_hero_passive_boost_income','Boost Income'),
 ('damage_building','wh2_main_skill_all_hero_hinder_settlement_damage_building','Damage Building'),
 ('assassinate','wh2_main_skill_all_hero_hinder_agent_assassinate','Assassinate'),
 ('hinder_replenishment','wh2_main_skill_all_hero_hinder_army_hinder_replenishment','Hinder Replenishment'),
 ('specialist','wh2_main_skill_all_hero_reduce_action_cost','Specialist')]):skill(slug,donor,name,4,i)
skill('wind_harmony','wh3_main_skill_cth_all_unique_magic_resist','Wind Harmony',0,0,7)
skill('ranged_discipline','wh3_main_skill_cth_all_unique_missile_resist','Ranged Discipline',0,1,7)
skill('mentor','wh3_main_skill_all_mentor_hero','Mentor',0,10)

own='character_to_character_own';force='character_to_force_own_unseen'
uniques=[
 ('moon_scholar','Moon Scholar','wh3_cp1_skill_cth_alchemist_unique_student_of_the_house_of_secrets',8,
  [('wh3_main_effect_ability_cooldown_spells_yin',own,-10),('wh3_main_effect_ability_cooldown_lore_of_heavens',own,-10)],'Cooldown: -10% for Lore of Yin and Lore of Heavens spells.'),
 ('silver_ward','Silver Ward','wh3_cp1_skill_cth_alchemist_unique_steel_sheathing',12,
  [('wh_main_effect_character_stat_armour',own,20)],'Armour: +20 (self).'),
 ('deep_wells','Deep Wells','wh_main_skill_all_magic_all_08_power_drain',16,
  [('wh3_main_effect_winds_of_magic_pool_cap',force,5)],'Winds of Magic reserve capacity: +5 (own army).'),
 ('moonlit_grace','Moonlit Grace','wh3_cp1_skill_cth_alchemist_unique_alchemical_wrath',20,
  [('wh_main_effect_character_stat_speed',own,10),('wh_main_effect_character_stat_melee_defence',own,8)],'Speed: +10%; melee defence: +8 (self).'),
 ('veil','Veil of the Moon','wh2_main_skill_all_immortality_hero',24,
  [('wh_main_effect_character_wound_recovery_time_mod',own,-2)],'Wound recovery time: -2 turns. Immortality is already granted for free.'),
 ('lunar_mastery','Lunar Mastery','wh3_cp1_skill_cth_alchemist_unique_living_forge',28,
  [('wh3_main_effect_spell_mastery',own,10)],'Spell mastery: +10% (self).')]
for i,(slug,name,donor,rank,grants,desc) in enumerate(uniques):
    k,_=skill(slug,donor,name,1,i,rank,custom=grants)
    next(x for x in loc if x[0]=='character_skills_localised_description_'+k)[1]=desc
    next(x for x in tables['character_skills'] if x['key']==k)['localised_description']=desc
# Make the signature spell's free base/paid upgrades unambiguous.
next(x for x in loc if x[0]=='character_skills_localised_description_'+active['blossom'][0])[1]='Blossom Wind is available from the start. Spend two skill points to unlock overcasting and improve cooldown, cost and miscast chance.'
assert len(manifest)==26 and sum(x['levels'] for x in manifest)==51

# Six base spells plus the one selected lore passive, using native overcast links.
g=one('special_ability_groups','ability_group','wh3_main_lore_of_yin')
assert not any(r['unique_id']=='1800312700' for r in native('special_ability_groups')[1])
g.update(ability_group=GROUP,button_name=GROUP,is_composite_group='true',unique_id='1800312700')
tables['special_ability_groups']=[g]
tables['special_ability_groups_to_unit_abilities_junctions']=[dict(special_ability_groups=GROUP,unit_special_abilities=x[3]) for x in SPELLS]+[dict(special_ability_groups=GROUP,unit_special_abilities='wh3_main_lore_passive_power_of_yin')]
# Exact replacements remove the old Metal group and inherent Enchanted Metallurgy.
output('special_ability_groups_to_units_junctions',[dict(ability_group=GROUP,unit=U,group_page_order='0')],'mc_da_lien')
output('land_units_to_unit_abilites_junctions',[
    dict(ability=a,land_unit=U,culture='*') for a in ['wh3_main_unit_passive_single_entity','wh_main_character_passive_evasion','wh_main_character_abilities_arcane_conduit']],'mc_da_lien')
output('character_skill_node_set_items',tables.pop('character_skill_node_set_items'),'mc_da_lien')
for t,rs in tables.items():output(t,rs)

# Custom Battle uses this tree's battle skills; campaign-only skills are excluded.
cb=[x['skill'] for x in manifest if x['row'] in (0,1,2) and x['slug']!='mentor']+[foundation[0]]
output('battle_set_piece_armies_characters_skillsets_skills',[
 dict(skill=k,skillset_key='mc_da_lien_cb_skills',sort_order=str(i)) for i,k in enumerate(cb)],'mc_da_lien_custom_battle')
loc.extend([
 ['special_ability_groups_localised_name_'+GROUP,'Moon Arts','true']])
# Update existing description keys in their original payload; avoid duplicate loc keys.
oldloc=read_path(B/'text/db/mc_da_lien.loc.tsv')[1]
updates={'unit_description_short_texts_text_'+U:'Human Wizard - Moon Arts',
         'unit_description_historical_texts_text_'+U:'Da Lien serves the Agents of the Moon, wielding Yin and celestial magic to break enemy formations and protect her allies.'}
for r in oldloc:
    if r['key'] in updates:r['text']=updates[r['key']]
oldinternal='text/db/mc_da_lien.loc';oldout=O/(oldinternal+'.tsv');oldout.parent.mkdir(parents=True,exist_ok=True)
with oldout.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+oldinternal,'','']]+[[r[k] for k in ['key','text','tooltip']] for r in oldloc])
files.append(oldinternal)
p='text/db/mc_da_lien_skills.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)

# Generate an authored, bounded migration for existing test saves. Old shared skill
# definitions are untouched. Background traits, XP, items and the Hero are preserved.
obsolete=sorted({nd[i['item']]['character_skill_key'] for i in olditems if '_alchemist_innate_' not in i['item'] and i['item']!='wh3_main_agent_action_scaling'})
template=(R/'src/script/campaign/mod/mc_da_lien_skill_migration.lua').read_text()
old_start=template.index('-- BEGIN GENERATED LEGACY SKILLS')
old_end=template.index('-- END GENERATED LEGACY SKILLS')+len('-- END GENERATED LEGACY SKILLS')
replacement='-- BEGIN GENERATED LEGACY SKILLS\nlocal legacy_skills = {\n'+''.join('    "'+k+'",\n' for k in obsolete)+'}\n-- END GENERATED LEGACY SKILLS'
template=template[:old_start]+replacement+template[old_end:]
(R/'src/script/campaign/mod/mc_da_lien_skill_migration.lua').write_text(template,encoding='utf-8')
internal='script/campaign/mod/mc_da_lien_skill_migration.lua';(O/internal).parent.mkdir(parents=True,exist_ok=True)
(O/internal).write_text(template,encoding='utf-8');files.append(internal)

# Referential and spell graph checks before constructing the pack.
efkeys={e['effect'] for e in native('effects')[1]}
assert all(e['effect_key'] in efkeys for e in tables['character_skill_level_to_effects_junctions'])
ua={x['key']:x for x in native('unit_abilities')[1]};special={x['key'] for x in native('unit_special_abilities')[1]}
for _,_,_,ability,_,_,_ in SPELLS:
    assert ability in special and ua[ability]['requires_effect_enabling']=='true'
    overcast=ua[ability]['overpower_option'];assert overcast and overcast in ua and overcast in special
assert any(x['attribute']=='spell_mastery' and x['attribute_group']=='wh3_main_cth_cha_alchemist_0' for x in native('unit_attributes_to_groups_junctions')[1])
assert all(n['key'] not in nd for n in tables['character_skill_nodes'])
assert all(s['key'] not in {x['key'] for x in native('character_skills')[1]} for s in tables['character_skills'])
for e in tables['character_skill_level_to_effects_junctions']:
    assert not any(bad in e['effect_key'] for bad in ['searing_doom','metalshifting','enchanted_metallurgy','glittering_robe','golden_hounds','transmutation'])

assert not PACK.exists(),'Protect previously built candidate'
shutil.copy2(BASE,PACK)
for internal in files:
    tab=internal.startswith('db/') or internal.endswith('.loc')
    args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK)]
    if tab:args+=['-t',C['schema']]
    subprocess.run(args+['-f',str(O/(internal+('.tsv' if tab else '')))+';'+internal],check=True,stdout=subprocess.DEVNULL)

t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(BASE);after=unpack(PACK)
changed=sorted(p for p in before if before[p]!=after.get(p))
added=sorted(set(after)-set(before))
assert set(after)==set(before)|set(files)
assert set(changed)==set(files)&set(before)
assert all(after[p]==v for p,v in before.items() if p not in files)
assert not any(p.startswith('variantmeshes/') for p in changed+added)
check=R/'reference/local/da-lien-v23-check';check.mkdir(exist_ok=True)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(PACK),'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)],check=True,stdout=subprocess.DEVNULL)
for internal in files:
    if internal.startswith('db/') or internal.endswith('.loc'):
        assert read_path(O/(internal+'.tsv'))[1]==read_path(check/(internal+'.tsv'))[1],internal
    else:assert after[internal]==(O/internal).read_bytes()
(O/'skill-manifest.json').write_text(json.dumps(dict(visible=manifest,max_points=51,spells=[x[3] for x in SPELLS],cb_skills=cb,legacy_skills=obsolete,files=files,base=str(BASE)),indent=2))
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text())
fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(BASE.parent/'diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt')
blocking=[];metadata=[]
for path,reports in new.items():
    if old.get(path)==reports:continue
    for r in reports:
        if set(r['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in r['cells_affected']):metadata.append(dict(path=path,report=r))
        else:blocking.append(dict(path=path,report=r))
(O/'diagnostics-review.json').write_text(json.dumps(dict(metadata=metadata,blocking=blocking),indent=2))
assert not blocking,blocking
v=dict(status='static_checks_passed',pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_entries=changed,new_entries=added,visible_nodes=26,max_skill_points=51,spells=[x[2] for x in SPELLS],new_blocking_diagnostics=0,new_schema_metadata_warnings=len(metadata),appearance_and_prior_non_da_lien_payloads_unchanged=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
