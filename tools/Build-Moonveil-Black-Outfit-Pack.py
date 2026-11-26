"""V31: exact black Moonveil body slot with all four original head families."""
import ast, csv, hashlib, json, shutil, struct, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
O = R / 'build/moonveil-v31-black-outfits'
OLD = R / 'build/moonveil-v24'
BASE = Path(C['game']) / 'data/mc_moonshadow_heroes_v30_building_previews.pack'
PACK = O / 'mc_moonshadow_heroes_v31_moonveil_black.pack'
assert not PACK.exists()
helpers = ast.parse((R / 'tools/Build-Moonshadow-Appearance-Pack.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in ('sha', 'unpack', 'cli', 'read')], type_ignores=[]), '<helpers>', 'exec'))
assert sha(BASE) == '06a2ac285b6ae858907061ad3f621daab95ffa2b771acaaa5c264ee229f80ff6'
M = json.loads((O / 'models.json').read_text())
review = json.loads((O / 'model-review.json').read_text())
assert review['status'] == 'passed' and review['models'] == 4 and not review['missing_textures']
assert sha(M['source']) == M['source_sha256']
before = unpack(BASE)
black_path = next(m['vmd'] for m in M['models'] if m['palette'] == 'black')
black_body = ET.fromstring(before[black_path]).find("SLOT[@name='body']")
files = []
for model in M['models']:
    path = model['vmd']
    original = ET.fromstring(before[path])
    new = ET.parse(O / path).getroot()
    # Compare full nested body choice trees and preserve every head choice.
    assert ET.tostring(new.find("SLOT[@name='body']")) == ET.tostring(black_body)
    assert ET.tostring(new.find("SLOT[@name='head']")) == ET.tostring(original.find("SLOT[@name='head']"))
    files.append(path)
    for folder, kind in [('units', 'body'), ('portholes', 'head')]:
        path = 'ui/portraits/' + folder + '/no_culture/' + model['key'] + '_0.png'
        dest = O / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(O / 'renders' / (model['key'] + '_' + kind + '.png'), dest)
        files.append(path)

for path, kind, size in [
    ('ui/units/icons/mc_moonveil_adept.png', 'body', (104, 208)),
    *[('ui/units/minspec_portholes/mc_moonveil_adept_' + suffix + '.png', 'head', (256, 256)) for suffix in ['human', 'warhorse', 'sky_lantern']],
]:
    dest = O / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(O / 'renders' / ('mc_moonveil_adept_white_' + kind + '.png')) as im:
        im.resize(size, Image.Resampling.LANCZOS).save(dest)
    files.append(path)

assert set(files) <= set(before)
shutil.copy2(BASE, PACK)
for i in range(0, len(files), 16):
    cli('pack', 'add', '-p', PACK, '-f', *[str(O / p) + ';' + p for p in files[i:i + 16]])
after = unpack(PACK)
assert set(after) == set(before)
changed = sorted(p for p in before if after[p] != before[p])
assert set(changed) <= set(files)
assert all(after[p] == data for p, data in before.items() if p not in files)
assert not any(p.startswith(('db/', 'script/', 'text/')) for p in changed)
assert not any(p.endswith(('.rigid_model_v2', '.dds', '.wsmodel', '.xml.material')) for p in changed)
check = R / 'reference/local/moon-v31-roundtrip'
check.mkdir(exist_ok=True)
cli('pack', 'extract', '-p', PACK, '-t', C['schema'], '-F', 'db;' + str(check))
with (O / 'diagnostics.txt').open('w', encoding='utf8') as f:
    subprocess.run([C['rpfm'], '-g', 'warhammer_3', 'pack', 'diagnose', '-g', C['game'], '-P', 'D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2', '-s', C['schema'], '-p', str(PACK)], check=True, stdout=f, stderr=subprocess.STDOUT)
txt = (O / 'diagnostics.txt').read_text()
diag = json.loads(txt[txt.index('{'):])
blocking = []
for group in diag['results']:
    for kind, group_data in group.items():
        for issue in group_data.get('results', []):
            typ = issue['report_type']
            if not (isinstance(typ, dict) and set(typ) == {'NoReferenceTableNorColumnFoundNoPak'}):
                blocking.append(dict(kind=kind, path=group_data.get('path'), issue=issue))
report = dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review', pack=str(PACK), sha256=sha(PACK), base=str(BASE), base_sha256=sha(BASE), blocking_diagnostics=blocking, roundtrip_passed=True, body_slot_exactly_black=True, original_heads_preserved=True, head_families=4, original_head_choices=8, geometry_skeleton_weights_lods_textures_unchanged=True, db_scripts_skills_building_previews_unchanged=True, portraits_rerendered=True, blender_animation_samples=review['samples'], changed_payloads=changed, deployed=False, runtime_verified=False)
(O / 'pack-validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
assert not blocking
