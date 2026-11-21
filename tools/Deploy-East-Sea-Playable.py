import copy,hashlib,json,os,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-playable';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());source=Path(v['pack'])
assert v['mixer_native_library_contract']=='passed' and v['unexpected_diagnostics']==0 and v['dependency_fingerprints_verified']
assert hashlib.sha256(source.read_bytes()).hexdigest()==v['sha256']
assert hashlib.sha256(Path(v['base_pack']).read_bytes()).hexdigest()==v['base_sha256']
actual={k:hashlib.sha256(Path(C[k]).read_bytes()).hexdigest() for k in ['mixer','iee','schema']};assert actual==v['dependency_sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname=Path(v['base_pack']).name;entry=next(m for m in mods if m.get('uuid')==oldname);assert entry['active']
assert not any(m.get('uuid')==source.name for m in mods)
dest=Path(C['game'])/'data'/source.name;assert not dest.exists()
backup=O/('launcher-before-playable-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.dat');backup.write_bytes(raw)
shutil.copy2(source,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==v['sha256']
entry['active']=False;new=dict(entry);new.update(uuid=source.name,packfile=dest.as_posix(),name='East Sea Charter - Playable Campaign',active=True);mods.insert(0,new)
assert [m for m in mods if m.get('uuid') not in [oldname,source.name]]==[m for m in before if m.get('uuid')!=oldname]
temp=launcher.with_name(launcher.name+'.edh-playable.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');assert launcher.read_bytes()==raw;os.replace(temp,launcher)
loaded=json.loads(launcher.read_text(encoding='utf-8-sig'));assert loaded==mods
v.update(deployed=True,deployed_path=str(dest),launcher_backup=str(backup),previous_pack_retained_disabled=oldname,other_mods_unchanged=True,game_not_launched=True,saves_not_modified=True)
(O/'deployment.json').write_text(json.dumps(v,indent=2));print('Enabled',source.name,'; v4 retained and disabled; all other mods unchanged; game not launched')
