"""Temporarily stage the undeployed prototype for frontend QA; preserve v24."""
import copy,hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-rescue-prototype'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
v=json.loads((O/'pack-validation.json').read_text());assert v['status']=='rescue_frontend_prototype_static_checks_passed' and v['new_blocking_diagnostics']==0
assert json.loads((R/'build/huyen-ve-v25-quest-candidate/lua-regression.json').read_text())['status']=='passed'
map_index=json.loads((R/'reference/local/huyen-ve-rescue-map-index-v2.json').read_text())
assert map_index['assets'] and map_index['battlefield']==json.loads((R/'src/campaign/huyen-ve-rescue-battle.json').read_text())['battlefield']
q=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True);assert q.stdout.strip()=='0'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve();assert source.parent==O.resolve() and target.parent==data
assert sha(source)==v['sha256']
oldname='mc_huyen_ve_v24_da_lien_moonstone.pack'
oldv=json.loads((R/'build/huyen-ve-v24-da-lien-moonstone/pack-validation.json').read_text());assert sha(data/oldname)==oldv['sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
old=next(m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname);assert old['active']
assert not target.exists() and not any(m.get('uuid')==source.name for m in mods)
backup=R/'build/huyen-ve-deployment'/('v25-qa-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
(backup/'20190104-moddata.dat').write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old);new.update(uuid=source.name,name=source.name,packfile=target.as_posix(),active=True)
mods.insert(mods.index(old)+1,new);old['active']=False
others=lambda a:[m for m in a if not (m.get('game')=='warhammer3' and m.get('uuid') in (oldname,source.name))]
assert others(before)==others(mods) and launcher.read_bytes()==raw
tmp=launcher.with_name(launcher.name+'.quest-qa.tmp');tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(tmp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report=dict(status='temporarily_staged_for_frontend_qa',source=str(source),target=str(target),sha256=sha(target),enabled=source.name,restore_active=oldname,launcher_backup=str(backup/'20190104-moddata.dat'),permanent_release=False,campaign_entry_enabled=False,runtime_verified=False)
report_path=O/'qa-staging.json'
if report_path.exists():shutil.copy2(report_path,backup/'previous-qa-staging.json')
report_path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
