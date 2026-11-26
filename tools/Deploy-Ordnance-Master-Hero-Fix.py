"""Install Ordnance Master hero UI category correction, with donor mods disabled."""
import copy, hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/ordnance-master-v19-hero-category'
v=json.loads((O/'pack-validation.json').read_text(encoding='utf8'))
assert v['status']=='static_checks_passed' and not v['blocking_diagnostics']
assert v['standalone_original_mod_not_required'] and v['variants']==5 and v['hero_flags_and_permissions_verified'] and v['parent_group']=='heroes_agents' and v['roundtrip_passed']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert source.parent==O.resolve() and target.parent==data and sha(source)==v['sha256']
assert not target.exists() and not (O/'deployment.json').exists()
assert sha(v['base'])==v['base_sha256']
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
assert running.stdout.strip()=='0','Close the game before deployment'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname='mc_moonshadow_heroes_v18_ordnance_master.pack'
old=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==oldname and m.get('active')]
assert len(old)==1 and not any(m.get('uuid')==source.name for m in mods)
baseline={m['packfile']:sha(m['packfile']) for m in mods if m.get('game')=='warhammer3' and m.get('active') and m.get('owned')}
backup=O/('deployment-backup-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/launcher.name).write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old[0]);new.update(uuid=source.name,packfile=target.as_posix(),name='Agents of the Moon - Ordnance Master Hero category',active=True,order=max(m.get('order',0) for m in mods if m.get('game')=='warhammer3')+1)
mods.insert(mods.index(old[0])+1,new);old[0]['active']=False
workshop_names={'luke_cth_master_engineer.pack','!luke_cth_master_engineer.pack'}
for m in mods:
 if m.get('game')=='warhammer3' and m.get('uuid','').lower() in workshop_names:m['active']=False
other=lambda rows:[m for m in rows if not(m.get('game')=='warhammer3' and (m.get('uuid') in (oldname,source.name) or m.get('uuid','').lower() in workshop_names))]
assert other(mods)==other(before)
assert launcher.read_bytes()==raw,'Launcher changed concurrently; copied pack left disabled'
temp=launcher.with_name(launcher.name+'.ordnance-hero-category.tmp')
temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf8');os.replace(temp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
assert all(sha(p)==h for p,h in baseline.items())
donor_report=json.loads((R/'build/moon-heroes-v17-engineer/pack-validation.json').read_text(encoding='utf8'))
assert sha(donor_report['source'])==donor_report['source_sha256']
assert not any(m.get('active') for m in mods if m.get('game')=='warhammer3' and m.get('uuid','').lower() in workshop_names)
report=dict(standalone_original_mod_not_required=True,original_and_portrait_mods_disabled=True,source_workshop_hash_unchanged=True,status='deployed_enabled',target=str(target),sha256=sha(target),enabled=source.name,disabled=oldname,previous_pack_retained=True,launcher_backup=str(backup/launcher.name),unrelated_launcher_entries_unchanged=True,previous_active_pack_hashes_unchanged=True,saves_modified=False,native_or_workshop_modified=False,game_launched=False,runtime_verified=False)
(O/'deployment.json').write_text(json.dumps(report,indent=2),encoding='utf8')
v['deployed']=True;(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
