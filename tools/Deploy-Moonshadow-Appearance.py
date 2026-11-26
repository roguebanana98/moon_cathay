"""Deploy the explicitly requested Moonshadow Assassin appearance update only."""
import json,hashlib,shutil,os,copy,subprocess
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moonshadow-v7-appearance'
v=json.loads((O/'pack-validation.json').read_text());q=json.loads((O/'roundtrip-animation-check.json').read_text())
assert v['status']=='static_checks_passed' and not v['blocking_diagnostics'] and q['status']=='passed' and q['sampled_poses']==96
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert source.parent==O.resolve() and target.parent==data and sha(source)==v['sha256']
assert not target.exists(),'Preserve installed packs'
assert sha(v['base'])==v['base_sha256']
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
assert running.stdout.strip()=='0','Close game before deployment'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname='mc_moonshadow_heroes_v6_celestial_tower.pack'
old=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname and m.get('active')]
assert len(old)==1 and not any(m.get('uuid')==source.name for m in mods)
baseline={m['packfile']:sha(m['packfile']) for m in mods if m.get('game')=='warhammer3' and m.get('active') and m.get('owned')}
backup=O/('deployment-backup-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/launcher.name).write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old[0]);new.update(uuid=source.name,packfile=target.as_posix(),name='Agents of the Moon - Moonshadow Assassin (4 appearances)',active=True,order=max(m.get('order',0) for m in mods if m.get('game')=='warhammer3')+1)
mods.insert(mods.index(old[0])+1,new);old[0]['active']=False
other=lambda rows:[m for m in rows if not(m.get('game')=='warhammer3' and m.get('uuid') in (oldname,source.name))]
assert other(mods)==other(before)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; leave copied pack disabled'
temp=launcher.with_name(launcher.name+'.moonshadow-appearance.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf8');os.replace(temp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
assert all(sha(p)==h for p,h in baseline.items())
report={'status':'deployed_enabled','target':str(target),'sha256':sha(target),'enabled':source.name,'disabled':oldname,'previous_pack_retained':True,'launcher_backup':str(backup/launcher.name),'unrelated_launcher_entries_unchanged':True,'previous_active_pack_hashes_unchanged':True,'saves_modified':False,'native_or_workshop_modified':False,'game_launched':False,'runtime_verified':False}
(O/'deployment.json').write_text(json.dumps(report,indent=2));v['deployed']=True;(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(report,indent=2))
