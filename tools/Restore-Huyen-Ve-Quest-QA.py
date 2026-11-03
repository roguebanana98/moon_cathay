"""End temporary quest QA, restoring only the two relevant launcher flags."""
import copy, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'build/huyen-ve-v25-rescue-prototype'
stage = json.loads((O / 'qa-staging.json').read_text())
check = subprocess.run(['powershell', '-NoProfile', '-Command',
    '@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],
    capture_output=True, text=True, check=True)
assert check.stdout.strip() == '0', 'Exit the test game before restoring launcher state'
config = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
stable = json.loads((R / 'build/huyen-ve-v24-da-lien-moonstone/pack-validation.json').read_text())
stable_path = Path(config['game']) / 'data' / stage['restore_active']
assert hashlib.sha256(stable_path.read_bytes()).hexdigest() == stable['sha256']
launcher = Path(os.environ['APPDATA']) / 'The Creative Assembly/Launcher/20190104-moddata.dat'
raw = launcher.read_bytes()
mods = json.loads(raw.decode('utf-8-sig'))
before = copy.deepcopy(mods)
names = (stage['enabled'], stage['restore_active'])
for name in names:
    matches = [m for m in mods if m.get('game') == 'warhammer3' and m.get('uuid') == name]
    assert len(matches) == 1, name
    matches[0]['active'] = name == stage['restore_active']
others = lambda rows: [m for m in rows if not
    (m.get('game') == 'warhammer3' and m.get('uuid') in names)]
assert others(before) == others(mods)
backup = Path(stage['launcher_backup']).parent / ('before-restore-' + datetime.now(timezone.utc).strftime('%H%M%S') + '.dat')
backup.write_bytes(raw)
assert launcher.read_bytes() == raw
tmp = launcher.with_name(launcher.name + '.quest-restore.tmp')
tmp.write_text(json.dumps(mods, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
os.replace(tmp, launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig')) == mods
result = dict(status='stable_v24_restored', active=stage['restore_active'],
    inactive=stage['enabled'], other_entries_unchanged=True,
    stable_sha256=stable['sha256'], backup=str(backup))
prefs_report = O / 'qa-preferences.json'
if prefs_report.exists():
    prefs = json.loads(prefs_report.read_text())
    if prefs.get('restore_required'):
        path = Path(prefs['path'])
        current = path.read_bytes()
        decoded = current.decode('utf-8-sig')
        old = 'fe_game_intro_video_enabled false;'
        new = 'fe_game_intro_video_enabled true;'
        assert prefs['before'] is True
        assert decoded.count(old) + decoded.count(new) == 1
        # Restore only the setting we changed; retain preferences saved by game.
        if old in decoded:
            (O / 'preferences-before-restoration.txt').write_bytes(current)
            path.write_bytes(decoded.replace(old, new, 1).encode('utf-8'))
        assert new in path.read_text(encoding='utf-8-sig')
        prefs.update(restore_required=False, restored=True)
        prefs_report.write_text(json.dumps(prefs, indent=2))
        result['intro_preference_restored'] = True
(O / 'qa-restoration.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
