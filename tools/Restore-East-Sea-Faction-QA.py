"""After exiting the game, retain QA saves separately and restore original files."""
import hashlib,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-faction'
running=subprocess.run(['tasklist','/FI','IMAGENAME eq Warhammer3.exe','/FO','CSV'],capture_output=True,text=True)
assert '"Warhammer3.exe"' not in running.stdout,'Exit the game before restoring QA saves'
p=O/'qa-session.json';s=json.loads(p.read_text());assert s['status']=='prepared'
root=Path(s['save_root']).resolve();backup=Path(s['backup']);original={r['name']:r['sha256'] for r in s['saves']}
retained=O/'qa-created-saves';retained.mkdir(exist_ok=True)
changes=[]
for f in root.iterdir():
 if not f.is_file():continue
 assert f.resolve().parent==root
 digest=hashlib.sha256(f.read_bytes()).hexdigest()
 if f.name not in original:
  dest=retained/f.name;assert not dest.exists();shutil.move(str(f),str(dest));changes.append('retained new QA file: '+f.name)
 elif digest!=original[f.name]:
  dest=retained/(f.name+'.qa-version');assert not dest.exists();shutil.copy2(f,dest);shutil.copy2(backup/f.name,f);changes.append('restored original: '+f.name)
for name,digest in original.items():
 dest=root/name;assert dest.resolve().parent==root
 if not dest.exists():shutil.copy2(backup/name,dest)
 assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest,name
s.update(status='restored',original_save_hashes_verified=len(original),changes=changes);p.write_text(json.dumps(s,indent=2));print('Restored/verified',len(original),'original save files;',changes)
