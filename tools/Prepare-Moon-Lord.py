"""Build private local DB derivatives for the human-only Moon Warden prototype."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/local/lord-vanilla/db'
OUT=ROOT/'build/moon-lord'
NEW='mc_moon_warden'
UNIT=NEW+'_human'
DONOR='wh3_dlc24_cth_yuan_bo'
DU='wh3_dlc24_cth_cha_yuan_bo_human'
ART='mc_moon_warden_art'
SET='mc_moon_warden_skills'
FACTION='cr_cth_agents_of_the_moon'
files=[]

def read(table):
    with (REF/(table+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:
        data=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return data[:2],[dict(zip(data[0],r)) for r in data[2:]]

def write(table,rows):
    (header,meta),_=read(table)
    assert all(set(r)<=set(header) for r in rows),table
    rows=list({tuple(r.get(k,'') for k in header):r for r in rows}.values())
    internal='db/'+table+'_tables/mc_moon_warden'
    meta[0]=';'.join(meta[0].split(';')[:2]+[internal])
    path=OUT/(internal+'.tsv');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows([header,meta]+[[r.get(k,'') for k in header] for r in rows])
    files.append(internal)

def clone(table,column,value,changes):
    _,rows=read(table)
    result=[dict(r,**changes) for r in rows if r[column]==value]
    assert result,(table,column,value)
    write(table,result)
    return result

clone('agent_subtypes','key',DONOR,dict(key=NEW,associated_unit_override=UNIT,
      auto_generate='false',recruitable='true',cap='1',has_female_name='false',magic_lore='mc_moon_warden_lore'))
clone('main_units','unit',DU,dict(unit=UNIT,land_unit=UNIT,campaign_cap='1'))
clone('land_units','key',DU,dict(key=UNIT))
clone('unit_variants','unit',DU,dict(unit=UNIT,name=UNIT))
clone('campaign_character_art_sets','art_set_id','wh3_dlc24_art_set_cth_yuan_bo',
      dict(art_set_id=ART,agent_subtype=NEW,faction=FACTION))
clone('campaign_character_arts','art_set_id','wh3_dlc24_art_set_cth_yuan_bo',
      dict(id='1800312000',art_set_id=ART))
clone('faction_agent_permitted_subtypes','subtype',DONOR,dict(faction=FACTION,subtype=NEW))
# Engine-owned ownership tables are banned in mod packs. Existing game files
# remain untouched; reference the donor resources without copying these tables.
_,abilities=read('land_units_to_unit_abilites_junctions')
retained=[dict(r,land_unit=UNIT) for r in abilities if r['land_unit']==DU and r['ability'] in
          ('wh3_main_unit_passive_single_entity','wh_main_character_abilities_arcane_conduit')]
assert len(retained)==2
write('land_units_to_unit_abilites_junctions',retained)
clone('special_ability_groups','ability_group','wh3_main_lore_of_yang',
      dict(ability_group='mc_moon_warden_lore',unique_id='1800312001',button_name='mc_moon_warden_lore',is_composite_group='true'))
clone('special_ability_groups_to_units_junctions','unit',DU,dict(unit=UNIT,ability_group='mc_moon_warden_lore'))
spells=['wh3_main_spell_yang_dragons_breath','wh_dlc05_spell_life_earth_blood','wh_main_spell_fire_flame_storm']
(_, _),spell_rows=read('special_ability_groups_to_unit_abilities_junctions')
header=read('special_ability_groups_to_unit_abilities_junctions')[0][0]
assert len(header)==2
write('special_ability_groups_to_unit_abilities_junctions',[
    {header[0]:'mc_moon_warden_lore',header[1]:spell}
    for spell in spells])
# Cathay melee/army/campaign lines, excluding mounts, donor-specific uniques,
# generic immortality (already immortal) and random background traits.
clone('character_skill_node_sets','key','wh3_dlc24_skill_node_set_cth_celestial_general_yang',
      dict(key=SET,agent_subtype_key=NEW,faction_key=FACTION))
_,items=read('character_skill_node_set_items');_,nodes=read('character_skill_nodes')
node_by_key={r['key']:r for r in nodes}
keep=[]
for r in items:
    if r['set']!='wh3_dlc24_skill_node_set_cth_celestial_general_yang':continue
    n=node_by_key[r['item']]
    if n['indent'] in ('2','4','5') or r['item']=='wh3_main_agent_action_scaling':
        keep.append(dict(r,set=SET))
skills=['wh3_main_skill_cth_magic_yang_01_dragons_breath_lord',
        'wh2_main_skill_magic_life_wizard_earth_blood_lord',
        'wh2_main_skill_all_magic_fire_10_flame_storm_lord']
custom_nodes=[]
for i,skill in enumerate(skills):
    original=next(r for r in nodes if r['character_skill_key']==skill)
    key=NEW+'_spell_'+str(i)
    custom_nodes.append(dict(original,key=key,campaign_key='',faction_key=FACTION,
        indent='1',tier=str(i),points_on_creation='1',required_num_parents='0',visible_in_ui='true'))
    keep.append(dict(set=SET,item=key,mod_disabled='false'))
dummy='wh3_main_skill_cth_magic_yang_dummy_dragons_breath'
original=custom_nodes[0]
custom_nodes.append(dict(original,key=NEW+'_breath_base',character_skill_key=dummy,campaign_key='',faction_key=FACTION,
    indent='99',tier='1',points_on_creation='1',required_num_parents='0',visible_in_ui='false'))
keep.append(dict(set=SET,item=NEW+'_breath_base',mod_disabled='false'))
skills.append(dummy)
write('character_skill_nodes',custom_nodes)
write('character_skill_node_set_items',keep)
# No cloned transformation ability, alternate dragon unit, mount or donor quest skill.
loc=[['agent_subtypes_onscreen_name_override_'+NEW,'Legendary Lord','true'],
     ['land_units_onscreen_name_'+UNIT,'Moon Warden','true'],
     ['names_name_mc_moon_warden','Moon Warden','true'],
     ['names_name_mc_moon_warden_empty','','true'],
     ['special_ability_groups_localised_name_mc_moon_warden_lore','Moon Arts','true']]
internal='text/db/mc_moon_warden.loc'
p=OUT/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
report={'files':files,'subtype':NEW,'unit':UNIT,'art':ART,'skill_set':SET,
        'starting_skills':skills,'spells':spells,'name':'Moon Warden','gender':'male',
        'model_donor':DU,'transformation':False,'baseline':'v3 tiered Long Vi',
        'status':'prototype_prepared_not_runtime_tested','starting_spells':'All three at level 1 for prototype testing'}
(OUT/'lord-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
