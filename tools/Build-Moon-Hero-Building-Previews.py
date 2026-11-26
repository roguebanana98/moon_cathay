"""V30: campaign-only hero preview permissions for the Moon building browser."""
import ast, copy, csv, hashlib, json, shutil, struct, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
O = R / 'build/moon-v30-building-previews'
O.mkdir(exist_ok=True)
B = R / 'reference/local/moon-v29-roundtrip'
N = R / 'reference/local/lord-vanilla/db'
F = 'cr_cth_agents_of_the_moon'
BASE = Path(C['game']) / 'data/mc_moonshadow_heroes_v29_general_tabs.pack'
PACK = O / 'mc_moonshadow_heroes_v30_building_previews.pack'
assert not PACK.exists()
helpers = ast.parse((R / 'tools/Build-Moonshadow-Appearance-Pack.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in ('sha', 'unpack', 'cli', 'read')], type_ignores=[]), '<helpers>', 'exec'))
assert sha(BASE) == 'b2f13fdc6022b2459b15097be9a28298684f09bc7557ba03cc5a05d24c9dbf67'
before = unpack(BASE)

def all_rows(table):
    return [r for p in (B / ('db/' + table + '_tables')).glob('*.tsv') for r in read(p)[1]]

units = ['mc_moonshadow_assassin_human', 'mc_pyromancer_human',
         'mc_astral_weaver_human', 'mc_tidecaller_human',
         'Luke_cth_master_engineer', 'mc_moonveil_adept_human']
permissions = all_rows('units_custom_battle_permissions')
assert not any(r['faction'] == F and r['unit'] in units for r in permissions)
preview = []
for unit in units:
    if unit == 'mc_moonshadow_assassin_human':
        row = dict(next(r for r in permissions if r['unit'] == 'mc_da_anh_human'),
                   unit=unit,
                   general_portrait='ui/portraits/portholes/no_culture/mc_moonshadow_assassin_face08_0.png',
                   general_uniform='mc_moonshadow_uniform_face08', set_piece_character='')
    else:
        row = dict(next(r for r in permissions if r['unit'] == unit))
    row.update(faction=F, campaign_exclusive='true')
    assert row['general_unit'] == 'false'
    assert row['general_portrait'] in before, row['general_portrait']
    assert any(r['uniform_name'] == row['general_uniform'] for r in all_rows('agent_uniforms'))
    preview.append(row)

paths = []
def write_table(table, rows):
    h, meta = copy.deepcopy(read(N / (table + '_tables/data__.tsv'))[0])
    internal = 'db/' + table + '_tables/zzzz_mc_moon_building_previews'
    meta[0] = ';'.join(meta[0].split(';')[:2] + [internal])
    dest = O / (internal + '.tsv')
    dest.parent.mkdir(parents=True, exist_ok=True)
    assert all(set(r) == set(h) for r in rows)
    with dest.open('w', encoding='utf8', newline='') as f:
        csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None, lineterminator='\n').writerows([h, meta] + [[r[k] for k in h] for r in rows])
    paths.append(internal)

write_table('units_custom_battle_permissions', preview)
# Moonshadow predates the custom-battle integration used by the later heroes.
# Supply the same native military grouping as those heroes for UI visibility.
assert not any(r['unit'] == units[0] for r in all_rows('units_to_groupings_military_permissions'))
write_table('units_to_groupings_military_permissions', [dict(unit=units[0], military_group='wh3_main_cth')])

# Every card is already packaged: no generated art or gameplay recruitment rows.
variants = all_rows('unit_variants')
for unit in units:
    card = next(r['unit_card'] for r in variants if r['unit'] == unit)
    assert ('ui/units/icons/' + card + '.png').lower() in {p.lower() for p in before}
assert not set(paths) & set(before)
assert 'script/campaign/mod/mc_moon_hide_celestial_general_tab.lua' not in before
shutil.copy2(BASE, PACK)
cli('pack', 'add', '-p', PACK, '-t', C['schema'], '-f', *[str(O / (p + '.tsv')) + ';' + p for p in paths])
after = unpack(PACK)
assert set(after) == set(before) | set(paths)
assert all(after[p] == data for p, data in before.items())
check = R / 'reference/local/moon-v30-roundtrip'
check.mkdir(exist_ok=True)
cli('pack', 'extract', '-p', PACK, '-t', C['schema'], '-F', 'db;' + str(check))
for p in paths:
    assert read(O / (p + '.tsv'))[1] == read(check / (p + '.tsv'))[1]
with (O / 'diagnostics.txt').open('w', encoding='utf8') as f:
    subprocess.run([C['rpfm'], '-g', 'warhammer_3', 'pack', 'diagnose', '-g', C['game'], '-P', 'D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2', '-s', C['schema'], '-p', str(PACK)], check=True, stdout=f, stderr=subprocess.STDOUT)
txt = (O / 'diagnostics.txt').read_text()
diag = json.loads(txt[txt.index('{'):])
blocking = []
for group in diag['results']:
    for kind, g in group.items():
        for issue in g.get('results', []):
            typ = issue['report_type']
            if not (isinstance(typ, dict) and set(typ) == {'NoReferenceTableNorColumnFoundNoPak'}):
                blocking.append(dict(kind=kind, path=g.get('path'), issue=issue))
report = dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review', pack=str(PACK), sha256=sha(PACK), base=str(BASE), base_sha256=sha(BASE), blocking_diagnostics=blocking, roundtrip_passed=True, existing_payloads_unchanged=True, campaign_preview_units=units, campaign_exclusive=True, all_portrait_and_card_files_present=True, recruitment_buildings_caps_and_skills_unchanged=True, no_ui_hiding_script=True, new_payloads=paths, deployed=False, runtime_verified=False)
(O / 'pack-validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
assert not blocking
