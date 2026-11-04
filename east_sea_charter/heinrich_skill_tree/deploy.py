"""Install verified v3; atomically replace only the previous Heinrich launcher entry."""
import copy,hashlib,json,os,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parent
v=json.loads((R/'pack_validation.json').read_text(encoding='utf8'))
assert v['status']=='static_checks_passed' and v['blocking_diagnostics']==0
source=Path(v['pack']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==v['sha256']
game_data=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data').resolve()
target=(game_data/source.name).resolve();assert target.parent==game_data and not target.exists()
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname=Path(v['previous_pack']).name
previous=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname]
assert len(previous)==1 and previous[0]['active'] is True
assert not any(m.get('game')=='warhammer3' and m.get('uuid')==source.name for m in mods)
backup=R/'deployment_backup'/datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True);(backup/launcher.name).write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
entry=copy.deepcopy(previous[0]);entry.update(uuid=source.name,packfile=target.as_posix(),
    name='Heinrich von Adlerhorst - Skill Tree v3',active=True)
previous[0]['active']=False
entry['order']=max(m.get('order',0) for m in mods if m.get('game')=='warhammer3')+1
mods.append(entry)
others=lambda seq:[m for m in seq if not(m.get('game')=='warhammer3' and m.get('uuid') in (source.name,oldname))]
assert others(before)==others(mods)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; copied pack not enabled'
temp=launcher.with_name(launcher.name+'.edh.tmp')
temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf8')
os.replace(temp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report={'status':'deployed_and_enabled','target':str(target),'sha256':sha(target),
    'disabled_previous_pack':oldname,'launcher_backup':str(backup/launcher.name),
    'other_mod_entries_unchanged':True,'campaign_saves_modified':False,
    'runtime_campaign_tree_verified':False}
(R/'deployment_report.json').write_text(json.dumps(report,indent=2))
v.update(deployed=True,deployment_target=str(target))
(R/'pack_validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
