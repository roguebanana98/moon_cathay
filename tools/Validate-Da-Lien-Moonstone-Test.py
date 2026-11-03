"""Check final exported item effects, equipment gate and bounded native heal."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v24-da-lien-moonstone'
E=R/'reference/local/da-lien-v24-check';N=R/'reference/local/lord-vanilla/db'
S=json.loads((R/'src/campaign/da-lien-equipment.json').read_text())
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0],x)) for x in a[2:]]
def table(t):return read(E/('db/'+t+'_tables/mc_da_lien_moonstone.tsv'))
def native(t):return read(N/(t+'_tables/data__.tsv'))
key=S['item']['key'];ability=S['ability']['key'];grant='mc_da_lien_enable_moonlit_renewal'
item=table('ancillaries')[0]
assert item['key']==key and item['category']=='arcane_item'
assert all(item[k]=='false' for k in ['unique_to_world','unique_to_faction','transferrable','randomly_dropped','can_be_stolen','can_be_destroyed'])
assert item['turns_before_swap_allowed']=='0'
assert table('ancillaries_included_agent_subtypes')==[dict(agent_subtype='mc_da_lien',ancillary=key)]
assert table('battle_set_piece_armies_characters_items')==[dict(character_item=key,character_name='mc_da_lien_human')]
assert table('ancillary_types')[0]['ui_icon']==S['item']['icon']
actual={(x['effect'],x['effect_scope'],float(x['value'])) for x in table('ancillary_to_effects')}
assert actual=={(e,scope,float(v)) for e,scope,v in S['item']['effects']}
ua=table('unit_abilities')[0];special=table('unit_special_abilities')[0]
assert ua['key']==special['key']==ability and ua['requires_effect_enabling']=='true'
assert ua['source_type']=='bound' and not ua['overpower_option'] and not ua['superseded_abilities_set']
assert special['num_uses']=='1' and float(special['mana_cost'])==0 and float(special['miscast_chance'])==0
assert special['target_friends']=='true' and special['target_enemies']=='false' and special['num_effected_friendly_units']=='4'
assert float(special['effect_range'])==35 and float(special['active_time'])==7 and float(special['target_intercept_range'])==200
original=next(x for x in native('unit_special_abilities') if x['key']==S['ability']['native_donor'])
assert {k for k in original if original[k]!=special[k]}=={'key','unique_id','num_uses'}
phase=next(x for x in native('special_ability_phases') if x['id']==S['ability']['native_heal_phase'])
assert phase['resurrect']=='false' and float(phase['heal_amount'])==0.008 and float(phase['duration'])==7
assert table('special_ability_to_special_ability_phase_junctions')==[dict(order='1',special_ability=ability,target_self='true',target_friends='true',target_enemies='false',phase=phase['id'])]
assert table('land_units_to_unit_abilites_junctions')==[dict(ability=ability,land_unit='mc_da_lien_human',culture='*')]
assert table('effect_bonus_value_unit_ability_junctions')==[dict(effect=grant,bonus_value_id='enable',unit_ability=ability)]
# A learned skill must never enable the item ability. Equipping contributes the
# grant, unequipping removes it; the ordinary Earth Blood remains a separate key.
for p in (E/'db/character_skill_level_to_effects_junctions_tables').glob('*.tsv'):
    assert not any(x['effect_key']==grant for x in read(p))
assert S['ability']['native_donor']!='wh_dlc05_spell_life_earth_blood' and ability not in json.loads((R/'build/huyen-ve-v23-da-lien-skills/skill-manifest.json').read_text())['spells']
v=json.loads((O/'pack-validation.json').read_text());assert v['existing_payloads_unchanged'] and v['new_blocking_diagnostics']==0
report=dict(status='passed',checks=['arcane slot and Da Lien-only whitelist','native reequip-safe flags and zero swap delay','exact +5 reserve, +5 ward and equipment-only ability gate','one-use zero-cost bound heal, no overcast or miscast','native heal phase, no resurrection or healing-cap change','Custom Battle item link','all v23 skills, model, portraits and prior payloads unchanged'],campaign_grant_runtime_verified=False,runtime_verified=False)
(O/'item-regression.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
