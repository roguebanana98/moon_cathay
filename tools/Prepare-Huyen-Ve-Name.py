"""Prepare only identity localization and a scoped save-name repair for v11."""
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
identity = json.loads((root/'src/campaign/moon-warden.json').read_text(encoding='utf-8'))
out = root/'build/huyen-ve-name'
source = root/'src'
files = []
for internal in ('text/db/mc_moon_warden.loc', 'text/db/mc_moon_warden_custom_battle.loc'):
    with (source/(internal+'.tsv')).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    for row in rows[2:]:
        if row[0] in ('land_units_onscreen_name_mc_moon_warden_human',
                      'names_name_mc_moon_warden', 'names_name_1800312100'):
            row[1] = identity['display_name']
        elif row[0] == 'agent_subtypes_onscreen_name_override_mc_moon_warden':
            row[1] = identity['lord_type']
        elif row[0].startswith('frontend_faction_leaders_'):
            row[1] = identity['display_name'] + ' — ' + identity['lord_type'] + '.'
    destination = out/(internal+'.tsv')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)
    files.append(internal)
internal = 'script/campaign/mod/mc_huyen_ve_name.lua'
destination = out/internal
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_bytes((root/'src'/internal).read_bytes())
files.append(internal)
(out/'name-report.json').write_text(json.dumps({'identity': identity,
    'files': files, 'runtime_verified': False}, indent=2), encoding='utf-8')
print(identity['display_name'])
