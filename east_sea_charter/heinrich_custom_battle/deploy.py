import json,hashlib,shutil,os,copy
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;v=json.loads((R/'pack_validation.json').read_text())
assert v['status']=='static_checks_passed' and v['blocking_diagnostics']==0
source=Path(v['pack']);data=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data').resolve();target=(data/source.name).resolve()
assert target.parent==data
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==v['sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
assert not target.exists() and not any(m.get('game')=='warhammer3' and m.get('uuid')==source.name for m in mods)
backup=R/'deployment_backup'/datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True)
(backup/launcher.name).write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
order=max(m.get('order',0) for m in mods if m.get('game')=='warhammer3')+1
entry={'uuid':source.name,'order':order,'active':True,'game':'warhammer3','packfile':target.as_posix(),'name':'Heinrich von Adlerhorst - Custom Battle Test','short':'','category':'','owned':True}
oldname=Path(v['previous_pack']).name if 'previous_pack' in v else None
if oldname:
    old=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname];assert len(old)==1
    old[0]['active']=False
mods.append(entry)
others=lambda seq:[m for m in seq if not(m.get('game')=='warhammer3' and m.get('uuid') in [source.name,oldname])]
assert others(before)==others(mods)
assert launcher.read_bytes()==raw,'Concurrent launcher change; pack copied, launcher not changed'
tmp=launcher.with_name(launcher.name+'.edh.tmp');tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf8');os.replace(tmp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report={'status':'deployed_and_enabled','target':str(target),'sha256':sha(target),'launcher_backup':str(backup/launcher.name),'disabled_previous_test_pack':oldname,'other_mod_entries_unchanged':True,'source_workshop_mod_unchanged':True,'saves_modified':False,'unit':v['unit'],'custom_battle_faction':'Empire','runtime_verified':False}
(R/'deployment_report.json').write_text(json.dumps(report,indent=2));v.update(deployed=True,deployment_target=str(target));(R/'pack_validation.json').write_text(json.dumps(v,indent=2))
print(json.dumps(report,indent=2))
