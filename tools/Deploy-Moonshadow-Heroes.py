"""Deploy the authorized additive roster without replacing any existing mod."""
import copy, hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moonshadow-celestial-tower'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
v=json.loads((O/'build-report.json').read_text());assert v['static_validation']=='passed' and v['blocking_diagnostics']==0
assert v['lua_scenarios']==17 and v['no_unrelated_mod_payload_overrides'] and v['unchanged_character_payloads']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(R/'src/script/campaign/mod/mc_moonshadow_start.lua')==v['lua_source_sha256']
for k,h in v['dependency_sha256'].items():assert sha(C[k])==h,k
for p,h in v['enabled_local_baseline_sha256'].items():assert sha(p)==h,p
check=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
assert check.stdout.strip()=='0','Close game before deploying'
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert source.parent==O.resolve() and target.parent==data and sha(source)==v['sha256']
assert not target.exists(),'Preserve installed pack'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname='mc_moonshadow_heroes_v5.pack'
base=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname and m.get('active')]
assert len(base)==1,'Expected previous Moonshadow addon active'
assert not any(m.get('uuid')==source.name for m in mods)
active={str(Path(m['packfile'])) for m in mods if m.get('game')=='warhammer3' and m.get('active') and m.get('owned')}
assert active==set(v['enabled_local_baseline_sha256']),'Active mod set changed since validation'
backup=R/'build/huyen-ve-deployment'/('moonshadow-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True);(backup/launcher.name).write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(base[0]);new.update(uuid=source.name,name='Agents of the Moon - Moonshadow Heroes',
    packfile=target.as_posix(),active=True,order=max(m.get('order',0) for m in mods if m.get('game')=='warhammer3')+1)
mods.insert(mods.index(base[0])+1,new);base[0]['active']=False
other=lambda ms:[m for m in ms if not(m.get('game')=='warhammer3' and m.get('uuid') in [oldname,source.name])]
assert other(mods)==other(before)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; copied pack but did not change launcher'
temp=launcher.with_name(launcher.name+'.moonshadow.tmp')
temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(temp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
for p,h in v['enabled_local_baseline_sha256'].items():assert sha(p)==h
report=dict(status='deployed_celestial_tower_revision',source=str(source),target=str(target),sha256=sha(target),
    enabled=source.name,disabled=oldname,launcher_backup=str(backup/launcher.name),unrelated_launcher_entries_unchanged=True,
    existing_pack_hashes_unchanged=True,saves_modified=False,native_or_workshop_modified=False,
    new_campaign_required_for_da_anh=True,game_launched=False,runtime_verified=False)
(O/'deployment.json').write_text(json.dumps(report,indent=2));v.update(deployed=True)
(O/'build-report.json').write_text(json.dumps(v,indent=2));print(json.dumps(report,indent=2))
