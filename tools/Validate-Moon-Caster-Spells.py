"""Inspect decoded v15 data: starters, spell names, membership and CB presets."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-casters-v15-spells'
v=json.loads((O/'pack-validation.json').read_text(encoding='utf8'))
root=R/'reference/local/moon-casters-v15-roundtrip/db'
def read(p):
    with p.open(encoding='utf-8-sig') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0],x)) for x in a[2:]]
def rows(t):return [r for p in (root/(t+'_tables')).glob('*.tsv') for r in read(p)]
loc={x['key']:x['text'] for x in read(O/'text/db/mc_caster_spells.loc.tsv')}
grants=rows('effect_bonus_value_unit_ability_junctions');effects=rows('character_skill_level_to_effects_junctions')
groups=rows('special_ability_groups_to_units_junctions');members=rows('special_ability_groups_to_unit_abilities_junctions')
cb=rows('battle_set_piece_armies_characters');cbs=rows('battle_set_piece_armies_characters_skillsets_skills')
reports=[]
for hero in v['heroes']:
    s=hero['subtype'];starter=hero['skill_mapping'][hero['starter']]
    active={x['effect_key'] for x in effects if x['character_skill_key']==starter and x['level']=='1' and float(x['value'])>0}
    unlocked={x['unit_ability'] for x in grants if x['effect'] in active and x['bonus_value_id']=='enable'}
    assert len(unlocked)==1,(s,unlocked)
    owned_groups={x['ability_group'] for x in groups if x['unit']==s+'_human'}
    owned={x['unit_special_abilities'] for x in members if x['special_ability_groups'] in owned_groups}
    assert unlocked<=owned
    character=next(x for x in cb if x['character_name']==s+'_human')
    preset={x['skill'] for x in cbs if x['skillset_key']==character['skillset']}
    assert starter in preset
    for old,name in hero['skills']:
        skill=hero['skill_mapping'][old];assert loc['character_skills_localised_name_'+skill]==name and skill in preset
        eff={x['effect_key'] for x in effects if x['character_skill_key']==skill}
        targets={x['unit_ability'] for x in grants if x['effect'] in eff and x['bonus_value_id']=='enable'}
        assert targets and targets<=owned,(s,old,targets-owned)
        assert all(loc['unit_abilities_onscreen_name_'+a] in (name,name+' (Upgraded)') for a in targets),(s,name,targets)
    reports.append(dict(subtype=s,starting_spell=[loc['unit_abilities_onscreen_name_'+a] for a in unlocked],renamed_spells_and_passive=7,custom_battle_preset_verified=True,all_base_abilities_in_owned_groups=True))
report=dict(status='passed',heroes=reports,runtime_verified=False)
(O/'spell-unlock-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
