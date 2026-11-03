"""Deploy the user-requested v18 item re-equip fix with launcher backup."""
import json,hashlib,shutil,copy,os
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v18-item-reequip';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));vp=O/'pack-validation.json';v=json.loads(vp.read_text());assert v['status']=='static_checks_passed' and v['new_or_changed_diagnostics']==0
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve();assert target.parent==data
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(source)==v['sha256'];oldname='mc_huyen_ve_v17_campaign_test.pack';assert sha(data/oldname)==v['base_sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
old=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname];assert len(old)==1 and old[0]['active'] and old[0]['owned'];old=old[0]
assert not any(m.get('game')=='warhammer3' and m.get('active') and m.get('owned') and m.get('uuid')!=oldname for m in mods)
assert not target.exists(),'New deployment file already exists; inspect before overwrite'
assert not any(m.get('game')=='warhammer3' and m.get('uuid')==source.name for m in mods)
stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S');backup=R/'build/huyen-ve-deployment'/('v18-'+stamp);backup.mkdir(parents=True);(backup/'20190104-moddata.dat').write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old);new.update(uuid=source.name,name=source.name,packfile=target.as_posix(),active=True);mods.insert(mods.index(old)+1,new);old['active']=False
others=lambda seq:[m for m in seq if not (m.get('game')=='warhammer3' and m.get('uuid') in [oldname,source.name])];assert others(before)==others(mods)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; file copied but launcher not updated'
tmp=launcher.with_name(launcher.name+'.hv18.tmp');tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(tmp,launcher);assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report={'status':'deployed_for_campaign_test','time_utc':datetime.now(timezone.utc).isoformat(),'source':str(source),'target':str(target),'sha256':sha(target),'enabled':source.name,'disabled':oldname,'launcher_backup':str(backup/'20190104-moddata.dat'),'other_launcher_entries_unchanged':True,'old_pack_file_preserved':True,'saves_modified':False,'workshop_files_modified':False,'runtime_verified':False}
(backup/'deployment-report.json').write_text(json.dumps(report,indent=2));(O/'deployment-report.json').write_text(json.dumps(report,indent=2));v.update(deployed=True,deployment_target=str(target));vp.write_text(json.dumps(v,indent=2));print(json.dumps(report,indent=2))

