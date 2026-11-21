import copy,hashlib,json,os,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-refuge';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());source=Path(v['pack'])
assert v['static_validation']=='passed' and hashlib.sha256(source.read_bytes()).hexdigest()==v['sha256']
old=json.loads((R/'build/east-sea-characters/deployment.json').read_text())
assert hashlib.sha256(Path(old['deployed_path']).read_bytes()).hexdigest()==v['base_sha256']
actual={k:hashlib.sha256(Path(C[k]).read_bytes()).hexdigest() for k in ['mixer','iee','schema']}
(O/'dependency-fingerprints.json').write_text(json.dumps(actual,indent=2))
if actual!=old['dependency_sha256']:
 review=json.loads((O/'dependency-review.json').read_text())
 assert review['status']=='reviewed_for_additive_refuge_deployment' and review['dependency_sha256']==actual,'Dependencies changed after the compatibility review'
 assert review['relevant_faction_definitions_unchanged'] and review['existing_region_definitions_unchanged']
 assert set(review['current_iee_faction_ids'])=={'mixer_emp_vaults_gigasdongo','cr_cth_agents_of_the_moon'}
 assert review['startpos_policy']=='Preserve existing user mod v3 startpos; no rebase in additive refuge feature'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
entry=next(m for m in mods if m.get('uuid')=='edh_east_sea_charter_characters_v3.pack')
assert not any(m.get('uuid')==source.name for m in mods)
backup=O/('launcher-before-refuge-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.dat');backup.write_bytes(raw)
dest=Path(C['game'])/'data'/source.name;assert not dest.exists();shutil.copy2(source,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==v['sha256']
entry['active']=False;new=dict(entry);new.update(uuid=source.name,packfile=dest.as_posix(),name='East Sea Charter - Refuge and Homecoming',active=True);mods.insert(0,new)
assert [(m.get('uuid'),m.get('active')) for m in mods[1:] if m.get('uuid')!=entry['uuid']]==[(m.get('uuid'),m.get('active')) for m in before if m.get('uuid')!=entry['uuid']]
temp=launcher.with_name(launcher.name+'.edh-refuge.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');assert launcher.read_bytes()==raw;os.replace(temp,launcher)
v.update(deployed=True,deployed_path=str(dest),launcher_backup=str(backup),dependency_sha256=actual,other_mod_activation_unchanged=True,game_not_launched=True,saves_not_edited=True)
(O/'deployment.json').write_text(json.dumps(v,indent=2));print('Enabled',source.name,'; v3 retained and disabled; no game launch/save changes')
