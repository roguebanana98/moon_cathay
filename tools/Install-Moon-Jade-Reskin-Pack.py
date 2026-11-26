"""Copy the verified standalone mod to dist and game data; leave launcher alone."""
import json,hashlib,shutil,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-reskin-v1';P=O/'mc_moon_jade_warriors_reskin_v1.pack'
report=json.loads((O/'pack-report.json').read_text());text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);assert diag['results']==[]
assert hashlib.sha256(P.read_bytes()).hexdigest()==report['sha256']
assert struct.unpack_from('<I',P.read_bytes(),4)[0]&15==3,'Must be a launcher-controlled MOD pack'
game=Path(json.loads((R/'build/divine-wing-guard-preview/asset-manifest.json').read_text())['game']);assert (game/'data').is_dir()
dist=R/'dist/moon-jade-warriors-reskin-v1';dist.mkdir(parents=True,exist_ok=True)
targets=[dist/P.name,game/'data'/P.name]
for target in targets:
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256'],'Do not overwrite another candidate'
 else:shutil.copy2(P,target)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
readme='''MOON JADE WARRIORS RESKIN V1

Chi thay ngoai hinh Jade Warriors KIEM-KHIEN cua Agents of the Moon.
7 lua chon dau DEER24; body05/che gay06; khien tron chu 陳 do;
dao can nau/chuoi vong; song dao tu, canh sac da sua dung phia;
mui giay ha phang va to nau.

Pack: mc_moon_jade_warriors_reskin_v1.pack
Da chep vao thu muc data cua game. BAT pack trong Total War Launcher,
cung IEE (!cr_immortal_empires_expanded.pack) va cac phu thuoc IEE dang dung.
Dat sau cac mod reskin khac neu chung sua rieng Jade Warriors cua Moon.
KHONG can DEER24 Jade Warriors Reskin lam dependency.

Khong sua chi so, ky nang, tuyen quan, animation hoac unit khac.
Giao, no va ky binh chua duoc reskin trong ban nay.
Khong thay doi launcher/load order hien tai, khong mo game.
Da qua RPFM roundtrip, zero diagnostics, actual RMV2/DDS reimport va
8 native animation checks trong Blender. Hien thi trong game CHUA duoc test.
Canh dao/can dai/khien/che gay van can nguoi dung xem clipping khi test.

Day la addon rieng, chua gop vao combined mod v34 dang thieu pack nen.
Tat pack nay trong launcher de quay lai ngoai hinh truoc do.
'''
(dist/'README.txt').write_text(readme,encoding='utf-8')
report.update(deployed=True,deployed_to_data=True,installed_path=str(targets[1]),distribution_path=str(targets[0]),launcher_changed=False,enabled_in_launcher=False,blocking_diagnostics=0,diagnostic_results=0,game_launched=False)
(O/'pack-report.json').write_text(json.dumps(report,indent=2));(dist/'pack-report.json').write_text(json.dumps(report,indent=2));(dist/'SHA256.txt').write_text(report['sha256']+'  '+P.name+'\n')
print(json.dumps(report,indent=2))
