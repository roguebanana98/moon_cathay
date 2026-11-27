"""Small Moon-only recruitment/CB visibility patch; does not alter v37 assets."""
import csv, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-hide-onyx-crowmen-v1'
O.mkdir(parents=True, exist_ok=True)
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
N = R / 'reference/local/zhao-shugengan-comparison-20261126/native/db'
PACK = O / 'mc_moon_hide_onyx_crowmen_v1.pack'
F = 'cr_cth_agents_of_the_moon'
UNITS = ['wh3_dlc24_cth_inf_onyx_crowmen', 'wh3_dlc24_cth_inf_onyx_crowmen_ror']
assert not PACK.exists(), 'Preserve completed candidate'

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return rows[:2], [dict(zip(rows[0], row)) for row in rows[2:]]

def cli(*args):
    p = subprocess.run([C['rpfm'], '-g', 'warhammer_3', *map(str, args)], capture_output=True, text=True, encoding='utf-8')
    with (O / 'build.log').open('a', encoding='utf-8') as f:
        f.write(p.stdout + p.stderr)
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout

paths = []
for table in ['units_to_exclusive_faction_permissions', 'units_custom_battle_permissions']:
    headers, native = read(N / (table + '_tables/data__.tsv'))
    path = 'db/' + table + '_tables/zzzzzz_mc_moon_hide_onyx_crowmen'
    headers[1][0] = ';'.join(headers[1][0].split(';')[:2] + [path])
    if table == 'units_to_exclusive_faction_permissions':
        rows = [dict(key=u, faction=F, allowed='false') for u in UNITS]
    else:
        rows = []
        for u in UNITS:
            donor = next(r for r in native if r['unit'] == u and r['faction'] == 'wh3_main_cth_cathay_mp')
            rows.append(dict(donor, faction=F, campaign_exclusive='true', siege_unit_attacker='false', siege_unit_defender='false'))
    assert all(r['faction'] == F for r in rows)
    dest = O / (path + '.tsv')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None, lineterminator='\n').writerows(headers + [[r[k] for k in headers[0]] for r in rows])
    paths.append(path)
cli('pack', 'create', '-p', PACK)
cli('pack', 'add', '-p', PACK, '-t', C['schema'], '-f', *[str(O / (p + '.tsv')) + ';' + p for p in paths])
cli('pack', 'add-dependency-pack', '-p', PACK, '-d', '!cr_immortal_empires_expanded.pack')
roundtrip = O / 'roundtrip'
cli('pack', 'extract', '-p', PACK, '-t', C['schema'], '-F', 'db;' + str(roundtrip))
for p in paths:
    assert read(O / (p + '.tsv')) == read(roundtrip / (p + '.tsv'))
diagnostics = cli('pack', 'diagnose', '--game-path', 'H:/SteamLibrary/steamapps/common/Total War WARHAMMER III', '--pak-path', R / 'reference/local/moon-jade-game.pak2', '--schema-path', C['schema'], '--pack-path', PACK, R / 'build/moon-v37-zhao-cb-fix/mc_moonshadow_heroes_v37_zhao_cb_fix.pack')
(O / 'diagnostics.txt').write_text(diagnostics)
data = json.loads(diagnostics[diagnostics.index('{'):])
own_results = [v for result in data['results'] for v in result.values() if v.get('pack') == PACK.name]
assert not own_results, own_results
assert all('NoReferenceTableNorColumnFoundNoPak' in r['report_type'] for result in data['results'] for v in result.values() for r in v.get('results', []))
with PACK.open('rb') as f:
    digest = hashlib.file_digest(f, 'sha256').hexdigest()
report = dict(pack=PACK.name, sha256=digest, bytes=PACK.stat().st_size, faction=F, units=UNITS, roundtrip_equal=True, diagnostics=0, runtime_verified=False, removes_existing_units=False, changes_garrisons=False, changes_other_factions=False)
(O / 'validation.json').write_text(json.dumps(report, indent=2))
assert subprocess.run(['powershell', '-NoProfile', '-Command', '@(Get-Process -Name Warhammer3,launcher -ErrorAction SilentlyContinue).Count'], capture_output=True, text=True, check=True).stdout.strip() == '0', 'Close game and launcher before installation'
dist = R / 'dist/moon-hide-onyx-crowmen-v1'
dist.mkdir(parents=True, exist_ok=True)
game = Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data')
assert game.is_dir()
for target in [dist / PACK.name, game / PACK.name]:
    assert not target.exists()
    shutil.copy2(PACK, target)
settings = Path.home() / 'AppData/Roaming/The Creative Assembly/Launcher/20190104-moddata.dat'
original = settings.read_bytes()
mods = json.loads(original.decode('utf-8-sig'))
assert not any(m['uuid'] == PACK.name for m in mods)
backup = O / ('launcher-before-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
backup.write_bytes(original)
mods.append(dict(uuid=PACK.name, order=max(m['order'] for m in mods)+1, active=True, game='warhammer3', packfile=(game / PACK.name).as_posix(), name=PACK.name, short='', category='', owned=True))
assert mods[:-1] == json.loads(original.decode('utf-8-sig'))
settings.write_text(json.dumps(mods, ensure_ascii=False), encoding='utf-8')
report.update(installed=str(game / PACK.name), enabled=True, launcher_backup=str(backup), unrelated_launcher_entries_unchanged=True)
(O / 'installation.json').write_text(json.dumps(report, indent=2))
for name in ['validation.json', 'installation.json']:
    shutil.copy2(O / name, dist / name)
(dist / 'SHA256.txt').write_text(digest + '  ' + PACK.name + '\n')
(dist / 'README.txt').write_text('Enable alongside v37 and IEE. Moon-only Onyx Crowmen visibility patch, including the RoR.\nDisables faction recruitment permission and hides Moon-specific Custom Battle permissions.\nNative Cathay Custom Battle roster, other factions, existing armies and garrisons unchanged.\nNo scripts or model changes. Runtime not verified.\n')
print(json.dumps(report, indent=2))
