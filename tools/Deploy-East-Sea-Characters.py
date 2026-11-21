import copy,hashlib,json,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-characters';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());source=Path(v['pack'])
assert v['static_validation']=='passed' and hashlib.sha256(source.read_bytes()).hexdigest()==v['sha256']
expected=json.loads((R/'build/east-sea-faction/build-report.json').read_text())['dependency_sha256']
for k,digest in expected.items():assert hashlib.sha256(Path(C[k]).read_bytes()).hexdigest()==digest, 'Dependency changed; inspect '+k
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();before=json.loads(raw.decode('utf-8-sig'));mods=copy.deepcopy(before)
entry=next(m for m in mods if m.get('uuid')=='edh_east_sea_charter_faction_v2.pack');assert entry['active']
assert next(m for m in mods if m.get('uuid')=='edh_heinrich_sariwa_v4.pack')['active']
assert not any(m.get('uuid')==source.name for m in mods)
(O/'launcher-before-v3.dat').write_bytes(raw);dest=Path(C['game'])/'data'/source.name;assert not dest.exists();shutil.copy2(source,dest)
entry['active']=False;new=dict(entry);new.update(uuid=source.name,packfile=dest.as_posix(),name='East Sea Charter - Heinrich and Sariwa',active=True);mods.insert(0,new)
assert [(m.get('uuid'),m.get('active')) for m in mods[1:] if m.get('uuid')!=entry['uuid']]==[(m.get('uuid'),m.get('active')) for m in before if m.get('uuid')!=entry['uuid']]
tmp=launcher.with_name(launcher.name+'.edh-characters.tmp');tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');assert launcher.read_bytes()==raw;os.replace(tmp,launcher)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==v['sha256']
test=Path(C['game'])/'edh_characters_test_mods.txt';lines=['add_working_directory "'+str(Path(C['iee']).parent).replace('\\','/')+'";','add_working_directory "'+str(Path(C['mixer']).parent).replace('\\','/')+'";']+['mod "'+name+'";' for name in [source.name,'mc_huyen_ve_v25_r8_longvi_city.pack','!cr_immortal_empires_expanded.pack','!b_mixer.pack','edh_heinrich_sariwa_v4.pack']];test.write_text('\n'.join(lines)+'\n',encoding='ascii')
v.update(deployed=True,deployed_path=str(dest),launcher_backup=str(O/'launcher-before-v3.dat'),dependency_sha256=expected,other_mod_activation_unchanged=True)
(O/'deployment.json').write_text(json.dumps(v,indent=2));print('Enabled',source.name,'; faction v2 disabled, character graphics v4 retained')
