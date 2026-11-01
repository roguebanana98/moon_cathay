"""Read-only checks against extracted primary game data; no runtime validation."""
import csv
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = root/'reference/local/lord-vanilla/db'
sources = {}

def read(relative):
    path = root/relative
    raw = path.read_bytes()
    sources[relative] = hashlib.sha256(raw).hexdigest()
    return raw.decode('utf-8-sig')

def rows(table):
    relative = f'reference/local/lord-vanilla/db/{table}_tables/data__.tsv'
    data = list(csv.reader(read(relative).splitlines(), delimiter='\t'))
    return [dict(zip(data[0], row)) for row in data[2:]]

checks = []
def check(name, condition, evidence):
    assert condition, name
    checks.append({'check': name, 'static_evidence': evidence})

manager = read('reference/local/lord-scripts/script/_lib/lib_campaign_manager.lua')
for function in ('create_force', 'create_force_with_general', 'get_saved_value', 'set_saved_value'):
    check(function, f'function campaign_manager:{function}(' in manager, 'campaign manager implementation')
missions = read('reference/local/lord-scripts/script/_lib/lib_campaign_mission_manager.lua')
check('scripted mission objective', 'function mission_manager:add_new_scripted_objective(' in missions,
      'mission manager implementation')
marker = read('reference/local/lord-scripts/script/campaign/wh2_campaign_interactive_marker_manager.lua')
check('campaign investigation marker', '"AreaEntered"' in marker and 'context:family_member():character()' in marker,
      'marker manager exposes entering character; Hero filter still needs authoring')

spell_keys = {'wh3_main_spell_yang_dragons_breath', 'wh_dlc05_spell_life_earth_blood',
              'wh_main_spell_fire_flame_storm', 'wh_dlc05_spell_shadow_the_enfeebling_foe',
              'wh_main_spell_death_spirit_leech'}
cooldown = rows('effect_bonus_value_unit_ability_junctions')
members = {r['unit_ability'] for r in cooldown if r['effect'] == 'wh2_main_effect_ability_cooldown_spells'}
check('all five current spells support generic cooldown effect', spell_keys <= members,
      sorted(spell_keys))
silence = rows('special_ability_phase_attribute_effects')
check('actual silenced attribute donor', any(r['phase'] == 'wh3_dlc27_character_abilities_the_black_tongue'
      and r['attribute'] == 'silenced' for r in silence), 'Black Tongue phase -> silenced')
abilities = rows('unit_special_abilities')
donor = next(r for r in abilities if r['key'] == 'wh3_dlc27_character_abilities_the_black_tongue')
check('targeted active donor', donor['target_enemies'] == 'true' and donor['num_effected_enemy_units'] == '1',
      {k: donor[k] for k in ('key', 'num_uses', 'active_time', 'target_enemies', 'num_effected_enemy_units')})
phases = rows('special_ability_phases')
conduit = next(r for r in phases if r['id'] == 'wh_main_character_abilities_arcane_conduit')
check('battle power recharge phase exists', float(conduit['mana_regen_mod']) != 0,
      {'phase': conduit['id'], 'mana_regen_mod': conduit['mana_regen_mod']})
sets = rows('ancillary_set_effect_junctions')
check('native equipment set effects', len(sets) > 0, 'set key links to scoped effects')
anc = rows('ancillaries')
weapon = next(r for r in anc if r['key'] == 'wh3_dlc24_anc_weapon_the_dragons_fang')
check('quest item donor prevents random drop/theft/destruction',
      all(weapon[k] == 'false' for k in ('randomly_dropped', 'can_be_stolen', 'can_be_destroyed')),
      {k: weapon[k] for k in ('key', 'randomly_dropped', 'can_be_stolen', 'can_be_destroyed')})
quest_ui = rows('character_ancillary_quest_ui_details')
check('quest UI links item/subtype/rank', any(r['agent_subtype'] == 'wh3_dlc24_cth_yuan_bo' for r in quest_ui),
      'character_ancillary_quest_ui_details records')
battles = rows('battle_set_pieces')
battle = next(r for r in battles if r['battle_name'] == 'wh3_dlc24_cth_yuan_bo_dragons_fang')
check('native quest battle map/script configuration', bool(battle['battlefield_folder']) and bool(battle['battle_script']),
      {k: battle[k] for k in ('battle_name', 'battlefield_folder', 'battle_script', 'teleport_cost', 'can_autoresolve_in_campaign')})
army_junctions = rows('battle_set_piece_armies_junctions')
check('quest battle army configuration', any(r['battle_name'] == battle['battle_name'] for r in army_junctions),
      'army/battle junction records')
snapshot = json.loads(read('reference/local/startpos-compact.json'))
quest_factions = [n for n in snapshot['selected'] if n.get('name') == 'FACTION'
                  and 'wh3_main_cth_cathay_qb1' in n['groups'][0]]
check('candidate Cathay quest faction exists in IEE startpos', bool(quest_factions),
      'wh3_main_cth_cathay_qb1; shared faction, not reserved exclusively for this mod')
result = {'date': '2026-11-02', 'status': 'static_feasibility_confirmed_runtime_unverified',
          'checks': checks, 'source_sha256': sources,
          'not_done': ['No mission/item DB authored', 'No new pack built', 'No gameplay launched',
                       'No battle map suitability/teleport/retry runtime verification']}
(root/'reports/equipment-quest-feasibility.json').write_text(
    json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'{len(checks)} static evidence checks passed; runtime remains unverified.')
