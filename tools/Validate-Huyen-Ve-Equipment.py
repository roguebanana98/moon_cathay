"""Validate actual item wiring, gated battle abilities and unchanged v12 payloads."""
import ast
import csv
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root/'build/huyen-ve-equipment'
report = json.loads((out/'equipment-report.json').read_text(encoding='utf-8'))
spec = report['spec']
manifest_path = out/'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
verification = Path(manifest['verification_directory'])
tree = ast.parse((root/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'unpack')
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<pack reader>', 'exec'))
before = unpack(root/'build/huyen-ve-name/mc_huyen_ve_v12_name.pack')
after = unpack(manifest['pack'])
assert set(after) == set(before) | set(report['files'])
assert not set(before) & set(report['files']), 'Equipment must be additive, not replace a previous payload'
assert all(after[k] == before[k] for k in before), 'A v12 payload changed'
assert not any('ownership_content_pack_junctions_tables/' in k for k in after)

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))

def rows(table):
    data = read(out/('db/'+table+'_tables/mc_huyen_ve_equipment.tsv'))
    return [dict(zip(data[0], r)) for r in data[2:]]

for internal in report['files']:
    if internal.startswith('db/') or internal.endswith('.loc'):
        source = read(out/(internal+'.tsv'))
        actual = read(verification/(internal+'.tsv'))
        assert source[0] == actual[0] and sorted(source[2:]) == sorted(actual[2:]), internal
        assert len(actual[2:]) == len(set(map(tuple, actual[2:]))), internal
    else:
        assert after[internal] == (out/internal).read_bytes() == (verification/internal).read_bytes()

items = {r['key']: r for r in rows('ancillaries')}
assert set(items) == {r['key'] for r in spec['items']}
assert {r['category'] for r in items.values()} == {'weapon', 'armour', 'enchanted_item', 'arcane_item', 'talisman'}
assert all(r[k] == 'false' for r in items.values()
           for k in ('randomly_dropped', 'can_be_stolen', 'can_be_destroyed', 'transferrable'))
assert {(r['agent_subtype'], r['ancillary']) for r in rows('ancillaries_included_agent_subtypes')} == {
    (spec['subtype'], key) for key in items}
assert {(r['character_name'], r['character_item']) for r in rows('battle_set_piece_armies_characters_items')} == {
    (spec['unit'], key) for key in items}
expected_effects = {(item['key'], effect, scope, float(value))
                   for item in spec['items'] for effect, scope, value in item['effects']}
assert {(r['ancillary'], r['effect'], r['effect_scope'], float(r['value']))
        for r in rows('ancillary_to_effects')} == expected_effects
assert {r['ancillary_key'] for r in rows('ancillary_set_ancillary_junctions')} == set(items)
assert rows('ancillary_set_effect_junctions') == [{'effect_key': 'wh_main_effect_character_stat_ward_save',
    'set_key': spec['set_key'], 'effect_scope': 'character_to_character_own', 'value': '5.0000'}]

abilities = {r['key']: r for r in rows('unit_special_abilities')}
phases = {r['id']: r for r in rows('special_ability_phases')}
ability_keys = {r['key'] for r in spec['abilities'].values()}
assert set(abilities) == set(phases) == ability_keys
assert all(r['requires_effect_enabling'] == 'true' for r in rows('unit_abilities'))
assert {(r['land_unit'], r['ability']) for r in rows('land_units_to_unit_abilites_junctions')} == {
    (spec['unit'], key) for key in ability_keys}
grants = rows('effect_bonus_value_unit_ability_junctions')
assert {(r['effect'], r['unit_ability'], r['bonus_value_id']) for r in grants} == {
    ('mc_huyen_ve_enable_'+suffix, config['key'], 'enable') for suffix, config in spec['abilities'].items()}
assert {r['effect'] for r in grants} <= {r[0] for item in spec['items'] for r in item['effects']}
assert not any(k.startswith('script/') for k in report['files']), 'No campaign free-grant script is allowed'

aura = spec['abilities']['warden_aura']['key']
lantern = spec['abilities']['moon_lantern']['key']
silence = spec['abilities']['pha_ta']['key']
assert float(abilities[aura]['effect_range']) == 35 and abilities[aura]['passive'] == 'true'
assert abilities[aura]['only_affect_owned_units'] == 'true'
assert rows('special_ability_phase_stat_effects') == [{'phase': aura, 'stat': 'stat_morale', 'value': '6.0000', 'how': 'add'}]
assert float(phases[lantern]['mana_regen_mod']) == 0.15 and abilities[lantern]['passive'] == 'true'
assert abilities[silence]['num_uses'] == '2'
assert float(abilities[silence]['recharge_time']) == 120 and float(abilities[silence]['target_intercept_range']) == 60
assert float(abilities[silence]['active_time']) == float(phases[silence]['duration']) == 15
assert abilities[silence]['target_enemies'] == 'true' and abilities[silence]['num_effected_enemy_units'] == '1'
assert rows('special_ability_phase_attribute_effects') == [{'attribute': 'silenced', 'phase': silence, 'attribute_type': 'positive'}]
assert not any(r['phase'] == silence for r in rows('special_ability_phase_stat_effects')), 'Donor debuffs leaked'
assert float(phases[silence]['damage_amount']) == float(phases[silence]['heal_amount']) == 0
assert all(float(r['mana_cost']) == 0 for r in abilities.values())
assert len({r['unique_id'] for r in abilities.values()}) == 3
native = read(root/'reference/local/lord-vanilla/db/unit_special_abilities_tables/data__.tsv')
native_ids = {r[native[0].index('unique_id')] for r in native[2:]}
assert not native_ids & {r['unique_id'] for r in abilities.values()}

loc = read(out/'text/db/mc_huyen_ve_equipment.loc.tsv')
localized = {r[0]: r[1] for r in loc[2:]}
assert len(localized) == len(loc[2:])
for item in spec['items']:
    assert localized['ancillaries_onscreen_name_'+item['key']] == item['name']
assert localized['ancillary_sets_name_'+spec['set_key']] == spec['set_name']
native_types_data = read(root/'reference/local/lord-vanilla/db/ancillary_types_tables/data__.tsv')
native_types = {r[0]: r[1] for r in native_types_data[2:]}
for r in rows('ancillary_types'):
    category = items[r['type'].removesuffix('_type')]['category']
    assert r['ui_icon'] == native_types['wh_main_anc_'+category]
    assert r['ui_icon'] not in after, 'Native item icons should be referenced, not replaced'
native_ability_icons = {'wh_magic_item_passive_talisman', 'wh_main_character_abilities_arcane_conduit',
                        'wh3_dlc27_character_abilities_the_black_tongue'}
assert {r['icon_name'] for r in rows('unit_abilities')} == native_ability_icons
for key in ability_keys:
    assert 'ui/battle ui/ability_icons/'+key+'.png' in after
assert len(report['native_icon_aliases']) == 3
for internal, native_path in report['native_icon_aliases'].items():
    assert after[internal] == (root/'reference/local/huyen-ve-native-icons'/native_path).read_bytes()
assert not any(k.startswith('ui/campaign ui/ancillaries/') for k in report['files'])

# v14 is an artwork-only revision of the delivered v13 item implementation.
previous = unpack(out/'mc_huyen_ve_v13_equipment.pack')
icon_tables = {'db/ancillary_types_tables/mc_huyen_ve_equipment', 'db/unit_abilities_tables/mc_huyen_ve_equipment'}
new_db_paths = {k for k in report['files'] if k.startswith('db/')}
assert all(after[k] == previous[k] for k in after if not k.startswith('ui/') and k not in new_db_paths)
for internal in sorted(new_db_paths):
    table = internal.split('/')[1].removesuffix('_tables')
    column = {'ancillary_types': 'ui_icon', 'unit_abilities': 'icon_name'}.get(table)
    old_data = read(root/'reference/local/huyen-ve-v13-check'/(internal+'.tsv'))
    old_rows = [dict(zip(old_data[0], r)) for r in old_data[2:]]
    strip = lambda r: {k:v for k,v in r.items() if k != column}
    assert [strip(r) for r in rows(table)] == [strip(r) for r in old_rows], table

diagnostic_text = (out/'diagnostics.txt').read_text(encoding='utf-8-sig')
diagnostics = json.loads(diagnostic_text[diagnostic_text.index('{'):])
metadata = []
for entry in diagnostics['results']:
    for kind, value in entry.items():
        if isinstance(value, dict) and 'mc_huyen_ve_equipment' in value.get('path', ''):
            for issue in value.get('results', []):
                assert set(issue['report_type']) == {'NoReferenceTableNorColumnFoundNoPak'}, issue
                metadata.append({'path': value['path'], 'columns': issue['column_names']})
manifest.update(static_validation='passed', new_payloads=len(report['files']),
    metadata_warnings=metadata, campaign_auto_grant=False,
    checks=['Every v12 payload, including startpos, byte-identical',
            'Five unique-slot quest items restricted to Huyen Ve; five native Custom Battle links',
            'Only item effects enable the three new unit abilities; none enabled unconditionally',
            '35m/+6 morale aura, 0.15 mana recharge, 15s/2-use/60m Silence verified',
            'No borrowed phase damage/debuffs, ID collisions or banned ownership tables',
            'Five-item set membership and +5% personal ward-save bonus configured',
            'All new DB/loc tables roundtrip; item/ability art uses native game paths',
            'Three phase icon aliases match native PNGs byte-for-byte; no authored art in pack',
            'All non-icon values and payloads preserved from v13',
            'RPFM new payload diagnostics contain only missing enum-reference metadata warnings'])
assert hashlib.sha256(Path(manifest['pack']).read_bytes()).hexdigest() == manifest['sha256']
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'Equipment validation passed: {len(items)} items, {len(abilities)} abilities, {len(report["files"])} additive payloads.')
