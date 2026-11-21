"""Private additive hero roster: native temporary appearance, no base overrides."""
import ast, csv, hashlib, json, os, struct, subprocess, copy, shutil
from PIL import Image
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
N = R/'reference/local/lord-vanilla/db'
O = R/'build/moonshadow-celestial-tower'; O.mkdir(parents=True, exist_ok=True)
PACK = O/'mc_moonshadow_heroes_v6_celestial_tower.pack'
assert not PACK.exists(), 'Preserve previous builds'
F = 'cr_cth_agents_of_the_moon'
G = 'mc_moonshadow_assassin'; L = 'mc_da_anh'
D = 'wh2_main_def_khainite_assassin'; DU = 'wh2_main_def_cha_khainite_assassin_0'
BUILDINGS = ['wh3_main_cth_magic_tower_'+str(i) for i in range(1,4)]
CONTEXT = 'mc_moonshadow_owner'
tables = defaultdict(list); files = []; loc = {}

def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        a = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return a[:2], [dict(zip(a[0], v)) for v in a[2:]]

cache = {}
def rows(t):
    if t not in cache: cache[t] = read(N/(t+'_tables/data__.tsv'))
    return cache[t][1]

def one(t, key, value):
    found = [r for r in rows(t) if r[key] == value]
    assert len(found) == 1, (t, key, value, len(found))
    return found[0]

def clone(t, field, value, **changes):
    row = dict(one(t, field, value), **changes); tables[t].append(row); return row

def cli(*args):
    result = subprocess.run([C['rpfm'], '-g', 'warhammer_3', *map(str,args)], capture_output=True,text=True)
    with (O/'build.log').open('a',encoding='utf-8') as f: f.write(result.stdout+result.stderr)
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

# Separate keys are kept for all future appearance swaps. No custom animation key.
for i, (s, name) in enumerate([(G,'Moonshadow Assassin'), (L,'Da Anh')]):
    legendary = s == L; u = s+'_human'; art = s+'_art'
    clone('agent_subtypes','key',D,key=s,associated_unit_override=u,
          auto_generate=str(not legendary).lower(), recruitable=str(not legendary).lower(),
          cap='1' if legendary else '0', loyalty_is_applicable='false',
          contributes_to_agent_cap=str(not legendary).lower(), can_be_loaned='false',
          saving_settings='cannot_be_loaded_in_campaign' if legendary else 'can_be_saved_loaded',
          small_icon='ui/campaign ui/agents/wh2_main_def_spy.png')
    clone('main_units','unit',DU,unit=u,land_unit=u,campaign_cap='1' if legendary else '-1',
          multiplayer_cap='1' if legendary else '0', recruitment_cost='1400' if legendary else '1000',
          upkeep_cost='300' if legendary else '250',
          audio_voiceover_culture='wh3_main_vo_culture_Cathay',can_be_bribed='false' if legendary else 'true')
    land = clone('land_units','key',DU,key=u,historical_description_text=u,short_description_text=u,
                 is_male='true', melee_attack='78' if legendary else '70',
                 melee_defence='48' if legendary else '42', bonus_hit_points='4080' if legendary else '3680')
    tables['unit_description_historical_texts'].append({'key':u})
    tables['unit_description_short_texts'].append({'key':u})
    uv = next(r for r in rows('unit_variants') if r['unit']==DU)
    tables['unit_variants'].append(dict(uv,unit=u,name=u,unit_card=s))
    clone('campaign_character_art_sets','art_set_id','wh2_main_art_set_def_khainite_assassin_01',
          art_set_id=art,agent_subtype=s,faction=F)
    clone('campaign_character_arts','id','5677',id=str(1986112100+i),art_set_id=art)
    tables['faction_agent_permitted_subtypes'].append(dict(agent='spy',faction=F,subtype=s,mod_disabled='false'))
    for t, field in [('special_ability_groups_to_units_junctions','unit'),('land_units_to_unit_abilites_junctions','land_unit')]:
        tables[t].extend(dict(r,**{field:u}) for r in rows(t) if r[field]==DU and
                        not any('murderous' in v for v in r.values()))
    if legendary:
        tables['land_units_to_unit_abilites_junctions'].append(dict(ability='wh2_main_unit_abilities_concealment_bombs',land_unit=u,culture='*'))
    clone('character_skill_node_sets','key','wh2_main_skill_node_set_def_khainite_assassin',
          key=s+'_skills',agent_subtype_key=s,faction_key=F)
    loc['agent_subtypes_onscreen_name_override_'+s] = 'Legendary Hero' if legendary else name
    loc['land_units_onscreen_name_'+u] = name
    loc['unit_description_short_texts_text_'+u] = 'Assassin - Character hunter'
    loc['unit_description_historical_texts_text_'+u] = (
        "The Moon's Hidden Blade, master of the covert agents of Long Vi." if legendary else
        'A covert agent of Long Vi, trained to eliminate enemy agents, sabotage settlements and strike at exposed commanders.')

# Cathay already has a spy-category culture entry. Reuse its category rather than
# overriding another Cathay Hero's culture record. Subtype art supplies appearance.
assert any(r['agent']=='spy' and r['culture']=='wh3_main_cth_cathay' and r['recruitable_in_ui']=='true'
           for r in rows('agent_culture_details'))

# Add only recruitment effects to the native Celestial Tower chain. Native
# construction costs, names, slots and Astromancer effects remain untouched.
# Context also prevents the spy-category capacity bonus reaching other factions.
clone('building_effect_context_expressions','key','AislinnBuiltInColony',key=CONTEXT,
      expression='Region.Owner.RecordKey == "'+F+'"',display_only_active_effects='true')
enable = 'mc_moonshadow_recruitment'; cap = 'mc_moonshadow_capacity'
for effect, donor, text in [(enable,'wh2_main_effect_agent_enable_recruitment_spy_def','Enables recruitment of Moonshadow Assassins'),
                            (cap,'wh2_main_effect_agent_cap_increase_def_khainite_assassin','Moonshadow Assassin capacity: %+n')]:
    clone('effects','effect',donor,effect=effect)
    loc['effects_description_'+effect] = text
    tables['effect_bonus_value_agent_subtype_junctions'].append(dict(bonus_value_id='availability' if effect==enable else 'cap',effect=effect,subtype=G))
    # Native recruitment checks both the spy category and subtype permissions.
    tables['effect_bonus_value_agent_junction'].append(dict(bonus_value_id='availability' if effect==enable else 'cap',effect=effect,agent='spy'))
    for building in BUILDINGS:
        tables['building_effects_junction'].append(dict(building=building,effect=effect,context_requirement=CONTEXT,
            effect_scope='province_to_province_own_unseen' if effect==enable else 'faction_to_faction_own_unseen',
            value='1.0000',value_damaged='0.0000',value_ruined='0.0000'))

# Curated native assassin tree. Clone nodes so all edits stay local. Remove slave
# economy, Dark Elf loyalty and random Dark Elf background skill generation.
items = [r for r in rows('character_skill_node_set_items') if r['set']=='wh2_main_skill_node_set_def_khainite_assassin']
nodeby = {r['key']:r for r in rows('character_skill_nodes')}
nodes = [nodeby[r['item']] for r in items]
def keep(n,legendary):
    s = n['character_skill_key']
    return not ('innate_' in s or 'slave' in s or 'loyalty' in s or
                (legendary and 'immortality' in s))

# The action-enabling background skill excludes all Dark Elf slave effects.
dummy = 'mc_moonshadow_actions'
clone('character_skills','key','wh2_main_skill_all_dummy_agent_actions_def_khainite_assassin',key=dummy)
base_effects = [r for r in rows('character_skill_level_to_effects_junctions')
                if r['character_skill_key']=='wh2_main_skill_all_dummy_agent_actions_def_khainite_assassin' and
                not any(v in r['effect_key'] for v in ['slave','scavenge'])]
base_effects.extend(dict(character_skill_key=dummy,effect_key=e,level='1',effect_scope='character_to_character_own',value='1.0000')
    for e in ['wh3_dlc23_effect_agent_action_enable_spy_hinder_settlement_damage_building',
              'wh2_main_effect_agent_action_enable_spy_assist_army_enhance_mobility'])
for row in base_effects: tables['character_skill_level_to_effects_junctions'].append(dict(row,character_skill_key=dummy))

for s in [G,L]:
    selected = [n for n in nodes if keep(n,s==L)]
    mapping = {n['key']:s+'_node_'+str(i) for i,n in enumerate(selected)}
    for n in selected:
        sk = n['character_skill_key']
        if sk=='wh2_main_skill_all_dummy_agent_actions_def_khainite_assassin': sk=dummy
        if sk=='wh2_main_skill_all_hero_assist_army_scavenge':sk='wh2_main_skill_all_hero_assist_army_increase_mobility'
        if s==L and sk=='wh2_main_skill_skv_trophy_heads_assassin':sk=L+'_execution'
        row=dict(n,key=mapping[n['key']],character_skill_key=sk)
        if n['indent']=='5': row['tier']=str(int(n['tier'])-(1 if int(n['tier'])>1 else 0))
        tables['character_skill_nodes'].append(row)
        olditem=next(r for r in items if r['item']==n['key'])
        tables['character_skill_node_set_items'].append(dict(olditem,set=s+'_skills',item=row['key']))
    for r in rows('character_skill_node_links'):
        if r['parent_key'] in mapping and r['child_key'] in mapping:
            tables['character_skill_node_links'].append(dict(r,parent_key=mapping[r['parent_key']],child_key=mapping[r['child_key']]))
    for r in rows('character_skill_nodes_skill_locks'):
        if r['character_skill_node'] in mapping:
            tables['character_skill_nodes_skill_locks'].append(dict(r,character_skill_node=mapping[r['character_skill_node']]))
    # Extra sabotage improvement is available to both hero subtypes.
    node = s+'_sabotage'
    tables['character_skill_nodes'].append(dict(key=node,campaign_key='',character_skill_key='wh2_main_skill_all_hero_hinder_settlement_damage_building',faction_key='',indent='5',tier='5',subculture='',points_on_creation='0',required_num_parents='0',visible_in_ui='true'))
    tables['character_skill_node_set_items'].append(dict(set=s+'_skills',item=node,mod_disabled='false'))

# Da Anh's personal branch uses native, rig-independent abilities; custom skill
# labels do not replace the native ability definitions or affect other characters.
unique = [
 ('veil','Moonshadow Veil','wh2_main_skill_skv_assassin_smoke_bomb',5,'Unlocks Concealment Bombs, allowing Da Anh to vanish and reposition.'),
 ('execution','Silent Execution','wh2_main_skill_skv_trophy_heads_assassin',11,"Unlocks Assassin's Trophy, weakening a chosen enemy before the killing blow."),
 ('supply','Sever the Supply Lines','wh2_main_skill_all_hero_reduce_action_cost',7,'Hero action cost: -15%. Hero action success chance: +10%.')]
for idx,(key,name,donor,rank,desc) in enumerate(unique):
    sk = L+'_'+key; node=sk+'_node'
    clone('character_skills','key',donor,key=sk,localised_name=name,localised_description=desc,unlocked_at_rank=str(rank))
    tables['character_skill_level_details'].append(dict(campaign_key='',faction_key='',level='1',
        skill_key=sk,subculture_key='',image_path='',unlocked_at_rank=str(rank)))
    if key=='supply':
        for effect,value in [('wh_main_effect_agent_action_cost_mod','-15.0000'),('wh_main_effect_agent_action_success_chance','10.0000')]:
            assert any(r['effect']==effect for r in rows('effects')), effect
            tables['character_skill_level_to_effects_junctions'].append(dict(character_skill_key=sk,effect_key=effect,level='1',effect_scope='character_to_character_own',value=value))
    else:
        tables['character_skill_level_to_effects_junctions'].extend(dict(r,character_skill_key=sk) for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==donor and r['level']=='1')
    if key=='execution':
        # Move the existing final trophy node to the personal row, retaining links.
        found=next(n for n in tables['character_skill_nodes'] if n['key'].startswith(L+'_node_') and n['character_skill_key']==sk)
        found.update(indent='4',tier=str(idx),required_num_parents='0')
        tables['character_skill_node_links'][:]=[r for r in tables['character_skill_node_links'] if r['child_key']!=found['key']]
    else:
        tables['character_skill_nodes'].append(dict(key=node,campaign_key='',character_skill_key=sk,faction_key='',indent='4',tier=str(idx),subculture='',points_on_creation='0',required_num_parents='0',visible_in_ui='true'))
        tables['character_skill_node_set_items'].append(dict(set=L+'_skills',item=node,mod_disabled='false'))
    loc['character_skills_localised_name_'+sk]=name;loc['character_skills_localised_description_'+sk]=desc

# Emit versioned native-schema tables. Header metadata is copied, not guessed.
for t,rs in tables.items():
    if not rs: continue
    (h,m),_=read(N/(t+'_tables/data__.tsv'));p='db/'+t+'_tables/mc_moonshadow'
    assert all(set(r)<=set(h) for r in rs),(t,set().union(*(set(r) for r in rs))-set(h))
    m=m.copy();m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r.get(k,'') for k in h] for r in rs])
    files.append(p)
p='text/db/mc_moonshadow.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
assert all(v.isascii() for v in loc.values())
with dest.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p)
script='script/campaign/mod/mc_moonshadow_start.lua';files.append(script)
# Reuse native art only in ignored private output, with separate portrait IDs.
ref=R/'reference/local/moonshadow-ui';ref.mkdir(parents=True,exist_ok=True)
sources=['ui/portraits/'+folder+'/no_culture/def_assassin_campaign_01_0.png' for folder in ['units','portholes']]
cli('pack','extract','-p',Path(C['game'])/'data/ui.pack','-f',*[p+';'+str(ref) for p in sources])
for s in [G,L]:
    for folder in ['units','portholes']:
        p='ui/portraits/'+folder+'/no_culture/'+s+'_0.png';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ref/('ui/portraits/'+folder+'/no_culture/def_assassin_campaign_01_0.png'),dest);files.append(p)
        settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text())
        entry=settings['entries'][0];entry['id']=s+'_art';variant=entry['variants'][0]
        variant.update(filename='def_assassin_campaign_01',file_diffuse=p,faction_leader=False)
        jp=O/('portrait-'+s+'-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2))
        p='ui/portraits/'+folder+'/portrait_settings__'+s+'.bin';dest=O/p
        cli('portrait-settings','from-json','-j',jp,'-b',dest);files.append(p)
    for p,folder,size in [('ui/units/icons/'+s+'.png','units',(104,208)),('ui/units/minspec_portholes/'+s+'_human.png','portholes',None)]:
        dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True)
        src=ref/('ui/portraits/'+folder+'/no_culture/def_assassin_campaign_01_0.png')
        if size:
            with Image.open(src) as im:im.resize(size,Image.Resampling.LANCZOS).save(dest)
        else:shutil.copy2(src,dest)
        files.append(p)
base=Path(C['game'])/'data/mc_moonshadow_heroes_v5.pack'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='b5a58e4fffb4d7c587d7ff3afad7a87e375643b280a8c6fdaee01e0cf62908cc'
# Preserve original packed table GUIDs and every unrelated payload byte-for-byte.
shutil.copy2(base,PACK)
removed=['db/'+t+'_tables/mc_moonshadow' for t in ['building_chains','building_levels','building_culture_variants',
    'building_chain_availability_set_ids','building_chain_availabilities','building_chain_availability_sets',
    'building_set_to_building_junctions']]
cli('pack','delete','-p',PACK,'-f',*removed)
for p in ['db/building_effect_context_expressions_tables/mc_moonshadow',
          'db/building_effects_junction_tables/mc_moonshadow','text/db/mc_moonshadow.loc']:
    if p.startswith(('db/','text/')):cli('pack','add','-p',PACK,'-t',C['schema'],'-f',str(O/(p+'.tsv'))+';'+p)
    else:cli('pack','add','-p',PACK,'-f',str((R/'src'/p) if p==script else (O/p))+';'+p)
Q=R/'reference/local/moonshadow-tower-roundtrip';cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','/;'+str(Q))
for p in files:
    if p.startswith(('db/','text/')):assert read(O/(p+'.tsv'))==read(Q/(p+'.tsv')),p
    else:assert (Q/p).read_bytes()==((R/'src'/p) if p==script else (O/p)).read_bytes(),p
report=dict(pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),files=files,
    faction=F,generic_subtype=G,legendary_subtype=L,buildings=BUILDINGS,db_loc_roundtrip=True,
    rows={t:len(rs) for t,rs in tables.items()},native_temporary_appearance='Khainite Assassin',
    battle_animation=land['man_animation'],campaign_animation='cam_hero_hu1d_elf_sword_and_handbow',
    new_campaign_required_for_da_anh=True,runtime_verified=False,deployed=False)
(O/'build-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
