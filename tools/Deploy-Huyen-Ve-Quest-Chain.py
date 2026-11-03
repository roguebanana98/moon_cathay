"""Deploy the verified complete private test pack; preserve v24 and launcher."""
import ast,copy,hashlib,json,os,shutil,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
v=json.loads((O/'pack-validation.json').read_text());q=json.loads((O/'lua-regression.json').read_text())
assert v['status']=='all_six_chapters_built_static_checks_passed' and v['enabled_chapters']==list(range(1,7)) and v['new_blocking_diagnostics']==0
assert q['status']=='passed'
for name,sha in q['source_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
check=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
assert check.stdout.strip()=='0','Close game before deployment'
source=Path(v['pack']).resolve();data=(Path(C['game'])/'data').resolve();target=(data/source.name).resolve()
assert source.parent==O.resolve() and target.parent==data
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==v['sha256']
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<reader>','exec'))
payload=unpack(source)
for p in v['files']:
    if p.endswith('.lua'):assert payload[p]==(R/'src'/p).read_bytes(),p
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));before=copy.deepcopy(mods)
oldname='mc_huyen_ve_v24_da_lien_moonstone.pack'
previous=[m for m in mods if m.get('game')=='warhammer3' and m.get('active') and
    (m.get('uuid')==oldname or m.get('uuid','').startswith('mc_huyen_ve_v25_quest_chain_test_'))]
assert len(previous)==1
old=previous[0];previous_name=old['uuid']
assert not target.exists() and not any(m.get('uuid')==source.name for m in mods)
stable=json.loads((R/'build/huyen-ve-v24-da-lien-moonstone/pack-validation.json').read_text())
# Older inactive packs may have been removed by the user. Preserve and verify
# the currently installed revision as rollback rather than restoring old packs.
previous_source=(R/'build/huyen-ve-v24-da-lien-moonstone'/previous_name if previous_name==oldname else O/previous_name)
assert previous_source.is_file() and sha(data/previous_name)==sha(previous_source)
fallback=previous_name
if (data/oldname).exists():
    assert sha(data/oldname)==stable['sha256'];fallback=oldname
backup=R/'build/huyen-ve-deployment'/('v25-chain-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
(backup/'20190104-moddata.dat').write_bytes(raw)
shutil.copy2(source,target);assert sha(target)==v['sha256']
new=copy.deepcopy(old);new.update(uuid=source.name,name=source.name,packfile=target.as_posix(),active=True)
mods.insert(mods.index(old)+1,new);old['active']=False
other=lambda rows:[m for m in rows if not(m.get('game')=='warhammer3' and m.get('uuid') in [previous_name,source.name])]
assert other(mods)==other(before) and launcher.read_bytes()==raw
tmp=launcher.with_name(launcher.name+'.quest-chain.tmp');tmp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(tmp,launcher)
assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report=dict(status='private_full_quest_chain_test_deployed',source=str(source),target=str(target),sha256=sha(target),active=source.name,inactive=previous_name,stable_fallback=fallback,enabled_chapters=list(range(1,7)),other_mods_unchanged=True,launcher_backup=str(backup/'20190104-moddata.dat'),runtime_verified=False)
(O/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
