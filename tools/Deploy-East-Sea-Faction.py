import copy,hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-faction'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());source=Path(v['pack'])
assert v['static_validation']=='passed' and hashlib.sha256(source.read_bytes()).hexdigest()==v['sha256']
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
assert not any(m.get('uuid')==source.name for m in mods)
assert any(m.get('uuid')=='mc_huyen_ve_v25_r8_longvi_city.pack' and m.get('active') for m in mods)
backup=O/('deployment-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir();(backup/launcher.name).write_bytes(raw)
dest=Path(C['game'])/'data'/source.name;assert not dest.exists();shutil.copy2(source,dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==v['sha256']
template=copy.deepcopy(next(m for m in mods if m.get('uuid')=='edh_heinrich_sariwa_v4.pack'))
for m in mods:
 if m.get('game')=='warhammer3':m['order']=m.get('order',0)+1
template.update(uuid=source.name,order=0,active=True,packfile=dest.as_posix(),name='East Sea Charter - Dai Loa and Preenn')
mods.insert(0,template)
assert [(m['uuid'],m.get('active')) for m in mods[1:]]==[(m['uuid'],m.get('active')) for m in before]
assert launcher.read_bytes()==raw
temp=launcher.with_name(launcher.name+'.edh-faction.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(temp,launcher)
v.update(deployed=True,deployed_path=str(dest),launcher_backup=str(backup/launcher.name),other_mod_activation_unchanged=True,other_mod_relative_order_unchanged=True)
(O/'deployment.json').write_text(json.dumps(v,indent=2));print('Deployed',source.name,'and enabled before the campaign baseline')
