"""Preserve pre-QA saves and archive only saves created by the smoke test."""
import hashlib,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
report_path=O/'campaign-smoke-session.json';s=json.loads(report_path.read_text());assert s['restoration_required']
q=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True);assert q.stdout.strip()=='0'
root=Path(s['save_root']).resolve();backup=Path(s['backup']).resolve();assert backup.is_relative_to(O.resolve())
original={r['name']:r['sha256'] for r in s['saves']};restored=[];archived=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in root.iterdir():
    if not p.is_file():continue
    assert p.resolve().parent==root
    if p.name not in original:
        target=backup/'qa-created-saves'/p.name;target.parent.mkdir(exist_ok=True)
        assert target.resolve().is_relative_to(backup) and not target.exists()
        shutil.move(str(p),str(target));archived.append(p.name)
for name,digest in original.items():
    p=root/name;source=backup/'original-saves'/name
    assert p.resolve().parent==root and source.resolve().is_relative_to(backup) and sha(source)==digest
    if not p.exists() or sha(p)!=digest:shutil.copy2(source,p);restored.append(name)
    assert sha(p)==digest
pref=Path(s['preferences']);raw=pref.read_bytes();text=raw.decode('utf-8-sig');key='fe_game_intro_video_enabled '
assert text.count(key+'true;')+text.count(key+'false;')==1
new=text.replace(key+('false;' if s['intro_before'] else 'true;'),key+('true;' if s['intro_before'] else 'false;'),1)
if new!=text:pref.write_bytes(new.encode('utf-8'))
s.update(status='restored',restoration_required=False,original_saves_verified=len(original),overwritten_saves_restored=restored,qa_saves_archived=archived,intro_restored=True)
report_path.write_text(json.dumps(s,indent=2));print(json.dumps(dict(status='restored',original_saves_verified=len(original),overwritten_count=len(restored),qa_save_count=len(archived),intro_restored=True)))
