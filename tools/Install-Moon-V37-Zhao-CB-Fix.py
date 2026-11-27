"""Install the scoped CB repair and replace only v36 in the current load order."""
import copy, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-v37-zhao-cb-fix'
V = json.loads((O / 'validation.json').read_text())
assert V['roundtrip_equal'] and V['all_other_payloads_byte_identical']
assert subprocess.run(['powershell', '-NoProfile', '-Command', '@(Get-Process -Name Warhammer3,launcher -ErrorAction SilentlyContinue).Count'], capture_output=True, text=True, check=True).stdout.strip() == '0', 'Close game/launcher first'
pack = Path(V['pack'])
def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
assert sha(pack) == V['sha256']
dist = R / 'dist/moon-v37-zhao-cb-fix'
dist.mkdir(parents=True, exist_ok=True)
game = Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data')
assert game.is_dir()
for target in [game / pack.name, dist / pack.name]:
    if target.exists():
        assert sha(target) == V['sha256'], 'Do not replace another candidate'
    else:
        shutil.copy2(pack, target)
    assert sha(target) == V['sha256']
settings = Path.home() / 'AppData/Roaming/The Creative Assembly/Launcher/20190104-moddata.dat'
original = settings.read_bytes()
mods = json.loads(original.decode('utf-8-sig'))
old = [m for m in mods if m['uuid'] == 'mc_moonshadow_heroes_v36_zhao_jade.pack']
assert len(old) == 1 and old[0]['active'], 'Audit changed launcher state first'
assert not any(m['uuid'] == pack.name for m in mods)
backup = O / ('launcher-before-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
backup.write_bytes(original)
new = copy.deepcopy(old[0])
new.update(uuid=pack.name, name=pack.name, packfile=(game / pack.name).as_posix(), active=True)
old[0]['active'] = False
mods.append(new)
before = json.loads(original.decode('utf-8-sig'))
assert [m for m in mods if m['uuid'] not in {pack.name, old[0]['uuid']}] == [m for m in before if m['uuid'] != old[0]['uuid']]
settings.write_text(json.dumps(mods, ensure_ascii=False), encoding='utf-8')
report = dict(pack=pack.name, sha256=V['sha256'], installed=str(game / pack.name), launcher_backup=str(backup), enabled=True, disabled=old[0]['uuid'], order=new['order'], unrelated_launcher_entries_unchanged=True, runtime_verified=False)
(O / 'installation.json').write_text(json.dumps(report, indent=2))
for filename in ['installation.json', 'validation.json']:
    shutil.copy2(O / filename, dist / filename)
(dist / 'SHA256.txt').write_text(V['sha256'] + '  ' + pack.name + '\n')
(dist / 'README.txt').write_text('V37: scoped Zhao Custom Battle duplicate repair over v36.\nEnable v37 only; disable v36 and standalone Jade v1/v2.\nTwo DB payloads changed: remove direct duplicate lore abilities; use unit variants for one foot/mount family.\nCampaign tree, stats, script, models, sword variants and all Jade payloads byte-identical to v36.\nRuntime review pending, including mounted appearance.\n')
print(json.dumps(report, indent=2))
