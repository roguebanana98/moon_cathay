"""Back up and restore only a disposable local campaign QA session."""
import hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-characters';p=O/'qa-session.json'
assert sys.argv[1] in ['prepare','restore']
running=subprocess.run(['tasklist','/FI','IMAGENAME eq Warhammer3.exe','/FO','CSV'],capture_output=True,text=True)
assert '"Warhammer3.exe"' not in running.stdout,'Exit the game before changing QA state'
pref=Path(os.environ['APPDATA'])/'The Creative Assembly/Warhammer3/scripts/preferences.script.txt'
if sys.argv[1]=='prepare':
 assert not p.exists() or json.loads(p.read_text())['status']=='restored','QA already active'
 root=(Path(os.environ['APPDATA'])/'The Creative Assembly/Warhammer3/save_games').resolve()
 backup=O/('qa-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir();records=[]
 for f in root.iterdir():
  if f.is_file():
   shutil.copy2(f,backup/f.name);digest=hashlib.sha256(f.read_bytes()).hexdigest();assert hashlib.sha256((backup/f.name).read_bytes()).hexdigest()==digest;records.append(dict(name=f.name,sha256=digest))
 raw=pref.read_bytes();(backup/'preferences-original.txt').write_bytes(raw);text=raw.decode('utf-8-sig');before='fe_game_intro_video_enabled true;' in text
 assert text.count('fe_game_intro_video_enabled true;')+text.count('fe_game_intro_video_enabled false;')==1
 if before:pref.write_text(text.replace('fe_game_intro_video_enabled true;','fe_game_intro_video_enabled false;',1),encoding='utf-8')
 p.write_text(json.dumps(dict(status='prepared',save_root=str(root),backup=str(backup),saves=records,intro_before=before),indent=2));print('Backed up and hashed',len(records),'original saves')
else:
 s=json.loads(p.read_text());assert s['status']=='prepared';root=Path(s['save_root']).resolve();backup=Path(s['backup']);original={r['name']:r['sha256'] for r in s['saves']};retained=O/'qa-created-saves';retained.mkdir(exist_ok=True)
 for f in root.iterdir():
  if not f.is_file():continue
  assert f.resolve().parent==root
  digest=hashlib.sha256(f.read_bytes()).hexdigest()
  if f.name not in original:
   dest=retained/f.name;assert not dest.exists();shutil.move(str(f),str(dest))
  elif digest!=original[f.name]:
   shutil.copy2(f,retained/(f.name+'.qa-version'));shutil.copy2(backup/f.name,f)
 for name,digest in original.items():
  f=root/name;assert f.resolve().parent==root
  if not f.exists():shutil.copy2(backup/name,f)
  assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
 text=pref.read_text(encoding='utf-8-sig');was='true' if s['intro_before'] else 'false';other='false' if s['intro_before'] else 'true';text=text.replace('fe_game_intro_video_enabled '+other+';','fe_game_intro_video_enabled '+was+';',1);pref.write_text(text,encoding='utf-8')
 s.update(status='restored',original_save_hashes_verified=len(original),intro_restored=True);p.write_text(json.dumps(s,indent=2));print('Restored/verified',len(original),'original saves and intro preference')
