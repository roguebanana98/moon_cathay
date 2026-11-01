"""Read cached ESF snapshots and verify provenance against the unchanged saved game."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
key = 'cr_cth_agents_of_the_moon'
inputs = json.loads((root/'reports/analysis-inputs.json').read_text(encoding='utf-8-sig'))
save = next(x for x in inputs if x['path'].endswith('.save'))
actual_hash = hashlib.sha256(Path(save['path']).read_bytes()).hexdigest()
assert actual_hash == save['sha256'].lower(), 'Save changed: regenerate cached inspection before relying on it'

def walk(node):
    if isinstance(node, dict) and 'groups' in node:
        yield node
        for group in node['groups']:
            for child in group:
                yield from walk(child)

def summary(node):
    return {'type': node['name'], 'values': [
        [value for value in group if not isinstance(value, dict)]
        for group in node['groups']]}

snapshots = {}
for filename in ('save-compact.json', 'startpos-compact.json'):
    path = root/'reference/local'/filename
    data = json.loads(path.read_text(encoding='utf-8'))
    faction = next(n for n in data['selected']
                   if n.get('name') == 'FACTION' and key in n['groups'][0])
    missions = []
    for mission in walk(faction):
        if mission['name'] != 'CAMPAIGN_MISSION':
            continue
        definition = next(n for n in walk(mission) if n['name'] == 'CAMPAIGN_MISSION_DEFINITION')
        detail = {'key': definition['groups'][0][0],
                  'states': [v for g in mission['groups'] for v in g if isinstance(v, str)],
                  'objectives': [], 'payloads': [], 'effect_bundles': []}
        for node in walk(definition):
            if node['name'].startswith('CAMPAIGN_MISSION_OBJECTIVE_IMPL_'):
                detail['objectives'].append(summary(node))
            elif node['name'].startswith('CAMPAIGN_PAYLOAD::COMPONENT::'):
                detail['payloads'].append(summary(node))
            elif node['name'] == 'CAMPAIGN_EFFECT_BUNDLE':
                detail['effect_bundles'].append(summary(node))
        missions.append(detail)
    snapshots[filename] = {'cache_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'mission_count': len(missions), 'missions': missions}
result = {'audit_date': '2026-11-02', 'faction': key,
          'save_source': save['path'], 'save_sha256_verified': actual_hash,
          'save_snapshot_date': '2026-10-30',
          'scope': 'Read-only cached snapshot audit; not live campaign UI or v12 runtime verification',
          'snapshots': snapshots}
(root/'reports/faction-missions-audit.json').write_text(
    json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
for filename, snapshot in snapshots.items():
    print(filename, snapshot['mission_count'], 'missions')
    for mission in snapshot['missions']:
        print(' ', mission['key'], mission['states'])
