import hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-faction'
session=O/'qa-session.json'
assert not session.exists() or json.loads(session.read_text())['status']=='restored','QA already active'
save=Path(os.environ['APPDATA'])/'The Creative Assembly/Warhammer3/save_games'
backup=O/('qa-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir()
records=[]
for p in save.iterdir():
 if p.is_file():
  q=backup/p.name;shutil.copy2(p,q)
  digest=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(q.read_bytes()).hexdigest()==digest
  records.append(dict(name=p.name,sha256=digest))
session.write_text(json.dumps(dict(status='prepared',save_root=str(save),backup=str(backup),saves=records),indent=2))
print('Backed up and verified',len(records),'save files')
