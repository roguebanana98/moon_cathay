import copy,hashlib,json,os,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/sariwa-campaign-appearance';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());source=Path(v['pack'])
assert v['static_validation']=='passed' and v['lua_boundary_tests']=='passed' and v['unexpected_diagnostics']==0
assert hashlib.sha256(source.read_bytes()).hexdigest()==v['sha256']
assert hashlib.sha256(Path(v['base_pack']).read_bytes()).hexdigest()==v['base_sha256']
assert hashlib.sha256(Path(v['asset_pack']).read_bytes()).hexdigest()=='0ef0b3d05dc9599013c31a5014a1e5bd3d24d5e4cc75a34cde53a5c418957239'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname=Path(v['base_pack']).name;entry=next(m for m in mods if m.get('uuid')==oldname);assert entry['active']
assert next(m for m in mods if m.get('uuid')==Path(v['asset_pack']).name)['active']
assert not any(m.get('uuid')==source.name for m in mods)
dest=Path(C['game'])/'data'/source.name;assert not dest.exists()
backup=O/('launcher-before-model-fix-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.dat');backup.write_bytes(raw)
shutil.copy2(source,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==v['sha256']
entry['active']=False;new=dict(entry);new.update(uuid=source.name,packfile=dest.as_posix(),name='East Sea Charter - Sariwa Campaign Model Fix',active=True);mods.insert(0,new)
assert [m for m in mods if m.get('uuid') not in [oldname,source.name]]==[m for m in before if m.get('uuid')!=oldname]
temp=launcher.with_name(launcher.name+'.edh-appearance.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');assert launcher.read_bytes()==raw;os.replace(temp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
v.update(deployed=True,deployed_path=str(dest),launcher_backup=str(backup),previous_pack_retained_disabled=oldname,other_mods_unchanged=True,game_not_launched=True,saves_not_edited=True)
(O/'deployment.json').write_text(json.dumps(v,indent=2));print('Enabled',source.name,'; v5 retained/disabled; asset pack active; all other mods unchanged')
