"""Author item definitions; private DB derivatives stay in build, never src."""
import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ref = root/'reference/local/lord-vanilla/db'
out = root/'build/huyen-ve-equipment'
spec = json.loads((root/'src/campaign/huyen-ve-equipment.json').read_text(encoding='utf-8'))
tables = defaultdict(list)
cache = {}
loc = []

def read(table):
    if table not in cache:
        with (ref/(table+'_tables/data__.tsv')).open(encoding='utf-8-sig', newline='') as f:
            data = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
        cache[table] = (data[:2], [dict(zip(data[0], r)) for r in data[2:]])
    return cache[table]

def donor(table, column, key):
    return dict(next(r for r in read(table)[1] if r[column] == key))

def text(key, value):
    loc.append([key, value, 'true'])

# All items are scoped to the existing custom subtype. No vanilla record override.
base = donor('ancillaries', 'key', 'wh3_dlc24_anc_weapon_the_dragons_fang')
effect_keys = {r['effect'] for r in read('effects')[1]}
custom_effect_keys = {'mc_huyen_ve_enable_'+k for k in spec['abilities']}
for item in spec['items']:
    key = item['key']
    item_type = key+'_type'
    category = item['category']
    tables['ancillaries'].append(dict(base, key=key, type=item_type,
        category=category, unique_to_world='true', unique_to_faction='true',
        randomly_dropped='false', can_be_stolen='false', can_be_destroyed='false',
        transferrable='false', uniqueness_score='200'))
    native_type = donor('ancillary_types', 'type', 'wh_main_anc_'+category)
    tables['ancillary_types'].append(dict(native_type, type=item_type))
    tables['ancillary_info'].append({'ancillary': key})
    tables['ancillaries_included_agent_subtypes'].append({'agent_subtype': spec['subtype'], 'ancillary': key})
    tables['battle_set_piece_armies_characters_items'].append({'character_item': key, 'character_name': spec['unit']})
    tables['ancillary_set_ancillary_junctions'].append({'ancillary_key': key, 'set_key': spec['set_key']})
    for effect, scope, value in item['effects']:
        assert effect in effect_keys | custom_effect_keys, effect
        tables['ancillary_to_effects'].append({'ancillary': key, 'effect': effect,
                                             'effect_scope': scope, 'value': f'{value:.4f}'})
    text('ancillaries_onscreen_name_'+key, item['name'])
    text('ancillaries_colour_text_'+key, item['description'])

tables['ancillary_sets'].append({'key': spec['set_key'], 'icon': 'ui/skins/default/icon_item_set.png'})
tables['ancillary_set_effect_junctions'].append({'effect_key': 'wh_main_effect_character_stat_ward_save',
    'set_key': spec['set_key'], 'effect_scope': 'character_to_character_own', 'value': f"{spec['set_ward_save']:.4f}"})
text('ancillary_sets_name_'+spec['set_key'], spec['set_name'])
text('ancillary_sets_description_'+spec['set_key'], 'The five relics of the Warden of Long Vi. Equip the complete set for +5% ward save.')

donors = {
    'warden_aura': ('wh2_dlc10_item_passive_ring_of_grimnir', 'wh2_dlc10_item_passive_ring_of_vengeance'),
    'moon_lantern': ('wh_main_character_abilities_arcane_conduit', 'wh_main_character_abilities_arcane_conduit'),
    'pha_ta': ('wh3_dlc27_character_abilities_the_black_tongue', 'wh3_dlc27_character_abilities_the_black_tongue')
}
existing_ids = {r['unique_id'] for r in read('unit_special_abilities')[1]}
ability_text = {
    'warden_aura': ('Uy Lệnh Trấn Thủ', 'Leadership +6 for friendly units within 35m. Only active while An Tran Thu is equipped.'),
    'moon_lantern': ('Ánh Nguyệt Đăng', 'Winds of Magic power recharge rate +15%. Only active while Nguyet Dang is equipped.'),
    'pha_ta': ('Phá Tà', 'Silences one enemy unit for 15 seconds, preventing spellcasting. 60m range; 2 uses; 120s cooldown. Requires Kiem Tran Da.')
}
grant_base = donor('effects', 'effect', 'wh_main_effect_ability_enable_arcane_conduit')
for index, (suffix, config) in enumerate(spec['abilities'].items()):
    key = config['key']
    ability_donor, phase_donor = donors[suffix]
    ua = donor('unit_abilities', 'key', ability_donor)
    tables['unit_abilities'].append(dict(ua, key=key, requires_effect_enabling='true',
        uniqueness='wh_main_anc_group_unique', superseded_abilities_set='', overpower_option=''))
    ability = donor('unit_special_abilities', 'key', ability_donor)
    unique_id = str(1800312300+index)
    assert unique_id not in existing_ids
    ability.update(key=key, unique_id=unique_id)
    phase = donor('special_ability_phases', 'id', phase_donor)
    phase.update(id=key, affects_enemies='false' if suffix != 'pha_ta' else 'true',
                 affects_allies='true' if suffix != 'pha_ta' else 'false')
    link = donor('special_ability_to_special_ability_phase_junctions', 'special_ability', ability_donor)
    link.update(special_ability=key, phase=key)
    if suffix == 'warden_aura':
        ability.update(effect_range=f"{config['radius']:.4f}", only_affect_owned_units='true')
        # Keep native aura targeting semantics; omit its morale-based auto-deactivation flag.
        tables['special_ability_phase_stat_effects'].append({'phase': key, 'stat': 'stat_morale',
            'value': f"{config['leadership']:.4f}", 'how': 'add'})
    elif suffix == 'moon_lantern':
        phase['mana_regen_mod'] = f"{config['mana_regen_mod']:.4f}"
    else:
        ability.update(active_time=f"{config['duration']:.4f}", num_uses=str(config['uses']),
            recharge_time=f"{config['cooldown']:.4f}", target_intercept_range=f"{config['range']:.4f}",
            wind_up_stance='', audio_switch_ui_override='', ai_usage='hex_spellcaster',
            additional_melee_cp='100.0000', additional_missile_cp='0.0000')
        phase['duration'] = f"{config['duration']:.4f}"
        # Deliberately author only Silence, not the donor's other phase stat modifiers.
        tables['special_ability_phase_attribute_effects'].append({'attribute': 'silenced',
            'phase': key, 'attribute_type': 'positive'})
    tables['unit_special_abilities'].append(ability)
    tables['special_ability_phases'].append(phase)
    tables['special_ability_to_special_ability_phase_junctions'].append(link)
    tables['land_units_to_unit_abilites_junctions'].append({'ability': key, 'land_unit': spec['unit'], 'culture': '*'})
    effect = 'mc_huyen_ve_enable_'+suffix
    tables['effects'].append(dict(grant_base, effect=effect, is_positive_value_good='true'))
    tables['effect_bonus_value_unit_ability_junctions'].append({'effect': effect, 'bonus_value_id': 'enable', 'unit_ability': key})
    name, description = ability_text[suffix]
    text('unit_abilities_onscreen_name_'+key, name)
    text('unit_abilities_tooltip_text_'+key, description)
    text('special_ability_phases_onscreen_name_'+key, name)
    text('effects_description_'+effect, 'Ability: "'+name+'"')

files = []
for table, rows in tables.items():
    (header, meta), _ = read(table)
    internal = 'db/'+table+'_tables/mc_huyen_ve_equipment'
    meta = list(meta)
    meta[0] = ';'.join(meta[0].split(';')[:2]+[internal])
    assert all(set(row) == set(header) for row in rows), table
    values = [[row[k] for k in header] for row in rows]
    assert len(values) == len(set(map(tuple, values))), table
    path = out/(internal+'.tsv')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE).writerows([header, meta]+values)
    files.append(internal)
internal = 'text/db/mc_huyen_ve_equipment.loc'
path = out/(internal+'.tsv')
path.parent.mkdir(parents=True, exist_ok=True)
with path.open('w', encoding='utf-8', newline='') as f:
    csv.writer(f, delimiter='\t', lineterminator='\n').writerows([
        ['key', 'text', 'tooltip'], ['#Loc;1;'+internal, '', '']]+loc)
files.append(internal)
# Phase status icons are looked up by phase ID. Alias native art byte-for-byte
# under our scoped phase names; item/ability icons reference native paths directly.
icons = {}
for suffix, config in spec['abilities'].items():
    ua = donor('unit_abilities', 'key', donors[suffix][0])
    icons[f'ui/battle ui/ability_icons/{config["key"]}.png'] = 'ui/battle ui/ability_icons/'+ua['icon_name']+'.png'
for internal, native_path in icons.items():
    destination = out/internal
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root/'reference/local/huyen-ve-native-icons'/native_path, destination)
    files.append(internal)
(out/'equipment-report.json').write_text(json.dumps({'files': files, 'spec': spec,
    'runtime_verified': False, 'campaign_auto_grant': False, 'native_icon_aliases': icons,
    'custom_battle_method': 'Native battle_set_piece_armies_characters_items links for the existing Huyen Ve character'},
    indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Prepared {len(spec["items"])} items, {len(spec["abilities"])} abilities, {len(files)} payloads.')
