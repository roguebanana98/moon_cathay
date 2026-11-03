"""User-authorized v15 test deployment; preserve v14, other mods and saves."""
import json,hashlib,shutil,os,copy
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-animation-integration';manifest_path=O/'pack-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
validation=json.loads((O/'pack-validation.json').read_text());assert validation['status']=='passed'
source=Path(manifest['pack']).resolve();assert source.parent==O.resolve() and source.name=='mc_huyen_ve_v15_model_animations.pack'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(source)==manifest['sha256']==validation['pack_sha256']
game=Path(C['game']).resolve();data=(game/'data').resolve();assert data.is_dir() and data.parent==game
target=(data/source.name).resolve();assert target.parent==data
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
old_name='mc_huyen_ve_v14_native_icons.pack';matches=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==old_name]
assert len(matches)==1,'Expected one existing v14 launcher entry'
old=matches[0];assert Path(old['packfile']).resolve()==(data/old_name).resolve()
assert sha(data/old_name)==manifest['base_sha256'],'Deployed v14 differs from validated base'
assert not [m for m in mods if m.get('game')=='warhammer3' and m.get('active') and m.get('owned') and m.get('uuid')!=old_name and m.get('uuid')!=source.name], 'Unexpected active local mod: inspect before replacing'
deps=['!b_mixer.pack','!cr_immortal_empires_expanded.pack']
for name in deps:
 entry=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==name]
 assert len(entry)==1 and entry[0]['active'] and Path(entry[0]['packfile']).is_file(),name
stamp=datetime.now().strftime('%Y%m%d-%H%M%S');backup=R/'build/huyen-ve-deployment'/stamp;backup.mkdir(parents=True)
(backup/'20190104-moddata.dat').write_bytes(raw)
if target.exists():shutil.copy2(target,backup/target.name)
shutil.copy2(source,target);assert sha(target)==manifest['sha256']
new=copy.deepcopy(old);new.update(uuid=source.name,packfile=target.as_posix(),name=source.name,active=True)
existing=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==source.name]
if existing:
 assert len(existing)==1;existing[0].update(new)
else:mods.insert(mods.index(old)+1,new)
old['active']=False
unchanged_before=[m for m in before if not (m.get('game')=='warhammer3' and m.get('uuid') in [old_name,source.name])]
unchanged_after=[m for m in mods if not (m.get('game')=='warhammer3' and m.get('uuid') in [old_name,source.name])]
assert unchanged_before==unchanged_after
assert launcher.read_bytes()==raw,'Launcher config changed during deployment; source pack copied but config not written'
temp=launcher.with_name(launcher.name+'.huyenve-'+stamp+'.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(temp,launcher)
reloaded=json.loads(launcher.read_text(encoding='utf-8-sig'));assert reloaded==mods
assert sha(data/old_name)==manifest['base_sha256']
result={'status':'deployed_for_user_test','time_utc':datetime.now(timezone.utc).isoformat(),'source':str(source),'target':str(target),'sha256':sha(target),
 'launcher_config':str(launcher),'launcher_backup':str(backup/'20190104-moddata.dat'),'launcher_before_sha256':hashlib.sha256(raw).hexdigest(),'launcher_after_sha256':sha(launcher),
 'enabled':source.name,'disabled':old_name,'order':new['order'],'v14_file_preserved':True,'other_launcher_entries_unchanged':True,
 'enabled_wh3_mods':[{'uuid':m['uuid'],'order':m['order']} for m in mods if m.get('game')=='warhammer3' and m.get('active')],
 'native_game_packs_modified':False,'workshop_files_modified':False,'saves_modified':False,'runtime_verified':False}
(backup/'deployment-report.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(R/'build/huyen-ve-deployment/latest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
manifest.update(deployed=True,deployment_target=str(target),deployment_report=str(backup/'deployment-report.json'))
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
