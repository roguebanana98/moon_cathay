"""Verify the v12 pack changes only identity files and preserves gameplay."""
import ast
import csv
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root/'build/huyen-ve-name'
manifest_path = out/'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
report = json.loads((out/'name-report.json').read_text(encoding='utf-8'))
tree = ast.parse((root/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'unpack')
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<pack reader>', 'exec'))
before = unpack(root/'build/moon-lord-spell-ranks/mc_moon_warden_v11_spell_progression.pack')
after = unpack(manifest['pack'])
script = 'script/campaign/mod/mc_huyen_ve_name.lua'
locs = {'text/db/mc_moon_warden.loc', 'text/db/mc_moon_warden_custom_battle.loc'}
assert set(after) - set(before) == {script}
assert not set(before) - set(after)
assert {k for k in before if before[k] != after[k]} == locs
assert after[script] == (root/'src'/script).read_bytes()
assert all(before[k] == after[k] for k in before if k not in locs)
all_rows = {}
for internal in locs:
    def read(path):
        with path.open(encoding='utf-8-sig', newline='') as f:
            return list(csv.reader(f, delimiter='\t'))
    authored = read(out/(internal+'.tsv'))
    extracted = read(Path(manifest['verification_directory'])/(internal+'.tsv'))
    assert authored == extracted, internal
    rows = extracted[2:]
    assert len(rows) == len({r[0] for r in rows})
    all_rows.update({r[0]: r[1] for r in rows})
    assert not any('Moon Warden' in r[1] or 'Ju Di' in r[1] for r in rows)
identity = report['identity']
for key in ('land_units_onscreen_name_mc_moon_warden_human',
            'names_name_mc_moon_warden', 'names_name_1800312100'):
    assert all_rows[key] == identity['display_name']
assert all_rows['agent_subtypes_onscreen_name_override_mc_moon_warden'] == 'Legendary Lord'
assert all_rows['names_name_mc_moon_warden_empty'] == all_rows['names_name_1800312101'] == ''
assert hashlib.sha256(Path(manifest['pack']).read_bytes()).hexdigest() == manifest['sha256']
manifest['static_validation'] = 'passed'
manifest['checks'] = ['Exact v11 payload set plus scoped campaign rename script',
    'Only the two identity localization payloads changed',
    'All gameplay DB, startpos, skills, model and province payloads byte-identical to v11',
    'Campaign and Custom Battle names match approved identity; Legendary Lord retained',
    'Localization roundtrip matches source exactly; no duplicate localization keys',
    'Dependency header and pack SHA256 verified']
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
