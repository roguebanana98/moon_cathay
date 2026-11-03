"""User-authorized v20 private deployment, preserving v19, other mods and saves."""
import json,hashlib,shutil,copy,os
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v20-da-lien-visual-test'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
vp=O/'pack-validation.json';v=json.loads(vp.read_text())
assert v['status']=='static_checks_passed' and v['new_blocking_diagnostics']==0
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert target.parent==data and sha(source)==v['sha256']
oldname='mc_huyen_ve_v19_moonlit_command.pack';assert sha(data/oldname)==v['base_sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
matches=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname]
assert len(matches)==1 and matches[0]['active'] and matches[0]['owned'],'Expected active v19; inspect launcher before modifying'
old=matches[0]
assert not any(m.get('game')=='warhammer3' and m.get('active') and m.get('owned') and m.get('uuid')!=oldname for m in mods)
assert not target.exists() and not any(m.get('game')=='warhammer3' and m.get('uuid')==source.name for m in mods)
stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
backup=R/'build/huyen-ve-deployment'/('v20-'+stamp);backup.mkdir(parents=True)
(backup/'20190104-moddata.dat').write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old);new.update(uuid=source.name,name=source.name,packfile=target.as_posix(),active=True)
mods.insert(mods.index(old)+1,new);old['active']=False
others=lambda entries:[m for m in entries if not (m.get('game')=='warhammer3' and m.get('uuid') in (oldname,source.name))]
assert others(before)==others(mods)
assert launcher.read_bytes()==raw,'Launcher changed concurrently: copied pack but did not update launcher'
tmp=launcher.with_name(launcher.name+'.dl20.tmp')
tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(tmp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report={'status':'deployed_for_campaign_visual_test','time_utc':datetime.now(timezone.utc).isoformat(),
 'source':str(source),'target':str(target),'sha256':sha(target),'enabled':source.name,'disabled':oldname,
 'launcher_backup':str(backup/'20190104-moddata.dat'),'other_launcher_entries_unchanged':True,
 'old_pack_file_preserved':True,'saves_modified':False,'workshop_files_modified':False,
 'spawn_executed_by_assistant':False,'runtime_verified':False}
(backup/'deployment-report.json').write_text(json.dumps(report,indent=2))
(O/'deployment-report.json').write_text(json.dumps(report,indent=2))
v.update(deployed=True,deployment_target=str(target));vp.write_text(json.dumps(v,indent=2))
print(json.dumps(report,indent=2))
