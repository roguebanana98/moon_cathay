"""Install v2 beside retained v1; leave launcher selection to the user."""
import json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-reskin-v2';report=json.loads((O/'pack-report.json').read_text());pack=Path(report['pack'])
diag=(O/'diagnostics.txt').read_text();assert json.loads(diag[diag.index('{'):])['results']==[]
assert hashlib.sha256(pack.read_bytes()).hexdigest()==report['sha256'];assert pack.stat().st_size<100*1024*1024
game=Path(json.loads((O/'native-review-assets.json').read_text())['native_game']);dist=R/'dist/moon-jade-warriors-reskin-v2';dist.mkdir(parents=True,exist_ok=True)
for target in [dist/pack.name,game/'data'/pack.name]:
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
 else:shutil.copy2(pack,target)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
report.update(deployed_to_data=True,installed_path=str(game/'data'/pack.name),distribution_path=str(dist/pack.name),blocking_diagnostics=0,launcher_changed=False,enabled_in_launcher=False)
(O/'pack-report.json').write_text(json.dumps(report,indent=2));(dist/'pack-report.json').write_text(json.dumps(report,indent=2))
(dist/'README.txt').write_text('''MOON JADE WARRIORS RESKIN V2 — HUMAN MODEL FAMILY

Ap dung chung than nguoi/mu/giap/giay va7lua chon dau da duyet cho:
- Jade Warriors (kiem-khien): giu nguyen reskinv1, dao va khien tron chu 陳.
- Jade Warriors (Halberds)
- Jade Warrior Crossbowmen
- Jade Warrior Crossbowmen (Shields)
- Jade Lancers

Bon loai moi CHI thay phan nguoi va dau; giu nguyen kich/no/thuong/
kiem phu/khien/ngua goc, cach gan vu khi va animation tuong ung.
Chi faction Agents of the Moon. Khong sua stats/tuyen quan/ky nang.

BAT mc_moon_jade_warriors_reskin_v2_family.pack trong launcher,
TAT v1 neu dang bat; v2 da bao gom toan bo v1, khong can bat ca hai.
Can IEE va cac dependency IEE dang dung. Khong can DEER24 pack nguon.
Da copy vao data; launcher/load order chua thay doi, chua mo game.
Da kiem tra Blender18clip/54khungmau/all7heads va RPFM0diagnostics.
Chua kiem chung ingame, nhat la clipping giap khi cuoi/but no.
File duoi100MiB, khong them Git LFS.
''',encoding='utf-8')
(dist/'SHA256.txt').write_text(report['sha256']+'  '+pack.name+'\n');print(json.dumps(report,indent=2))
