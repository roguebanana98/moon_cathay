"""Back up native saves before creating a disposable campaign for smoke QA."""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
q=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True);assert q.stdout.strip()=='0'
game_user=Path(os.environ['APPDATA'])/'The Creative Assembly/Warhammer3'
saves=(game_user/'save_games').resolve()
backup=O/('campaign-smoke-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir()
rows=[]
for p in saves.iterdir():
    if not p.is_file():continue
    assert p.resolve().parent==saves
    target=backup/'original-saves'/p.name;target.parent.mkdir(exist_ok=True)
    shutil.copy2(p,target)
    sha=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
    rows.append(dict(name=p.name,sha256=sha))
pref=game_user/'scripts/preferences.script.txt';raw=pref.read_bytes();text=raw.decode('utf-8-sig')
key='fe_game_intro_video_enabled '
assert text.count(key+'true;')+text.count(key+'false;')==1
before=key+'true;' in text
(backup/'preferences-original.txt').write_bytes(raw)
if before:pref.write_bytes(text.replace(key+'true;',key+'false;',1).encode('utf-8'))
report=dict(status='prepared',save_root=str(saves),backup=str(backup),saves=rows,preferences=str(pref),intro_before=before,restoration_required=True)
(O/'campaign-smoke-session.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(status='prepared',save_count=len(rows),backup=str(backup))))
