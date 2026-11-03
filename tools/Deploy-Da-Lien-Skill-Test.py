"""Deploy user-authorized private v23 skill test, replacing active v22 only."""
import copy,hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v23-da-lien-skills'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
V=O/'pack-validation.json';v=json.loads(V.read_text())
assert v['status']=='static_checks_passed' and v['new_blocking_diagnostics']==0
assert json.loads((O/'skill-regression.json').read_text())['status']=='passed'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert source.parent==O.resolve() and target.parent==data and sha(source)==v['sha256']
oldname=Path(v['base']).name;assert sha(data/oldname)==v['base_sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
matches=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname]
assert len(matches)==1 and matches[0]['active'] and matches[0]['owned'],'Expected active v22; inspect launcher state'
assert not target.exists() and not any(m.get('uuid')==source.name for m in mods)
# A live process keeps the previous pack in memory; do not change deployment then.
q=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
assert q.stdout.strip()=='0','Game is running; deployment deferred until it closes'
stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
backup=R/'build/huyen-ve-deployment'/('v23-'+stamp);backup.mkdir(parents=True)
(backup/'20190104-moddata.dat').write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
old=matches[0];new=copy.deepcopy(old);new.update(uuid=source.name,name=source.name,packfile=target.as_posix(),active=True)
mods.insert(mods.index(old)+1,new);old['active']=False
others=lambda a:[m for m in a if not(m.get('game')=='warhammer3' and m.get('uuid') in (oldname,source.name))]
assert others(before)==others(mods)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; copied pack but did not update launcher'
tmp=launcher.with_name(launcher.name+'.dl23.tmp')
tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(tmp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report=dict(status='deployed_for_skill_test',time_utc=datetime.now(timezone.utc).isoformat(),source=str(source),target=str(target),sha256=sha(target),enabled=source.name,disabled=oldname,launcher_backup=str(backup/'20190104-moddata.dat'),other_launcher_entries_unchanged=True,old_pack_file_preserved=True,saves_modified=False,workshop_files_modified=False,runtime_verified=False)
(backup/'deployment-report.json').write_text(json.dumps(report,indent=2))
(O/'deployment-report.json').write_text(json.dumps(report,indent=2))
v.update(deployed=True,deployment_target=str(target));V.write_text(json.dumps(v,indent=2))
print(json.dumps(report,indent=2))
