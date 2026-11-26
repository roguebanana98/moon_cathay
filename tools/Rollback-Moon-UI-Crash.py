"""Remove the unverified tab-hiding change by re-enabling the verified v26 pack."""
import ast,copy,hashlib,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-ui-crash-rollback';O.mkdir(exist_ok=True)
old='mc_moonshadow_heroes_v28_hide_celestial_tab.pack';new='mc_moonshadow_heroes_v26_recruitment_names.pack';data=Path(C['game'])/'data';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(data/old)=='10d30f33fb9b86cddf2d1e1127cb56f45afa157cfe1683ffa3abb48973ea5007'
assert sha(data/new)=='c3b6a083c76d0f1360a4c6a3afef736921c115858fd54a56824c58d6c20d0e79'
s=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name=='unpack'],type_ignores=[]),'<pack reader>','exec'))
before=unpack(data/old);after=unpack(data/new);bad='script/campaign/mod/mc_moon_hide_celestial_general_tab.lua'
assert set(before)-set(after)=={bad} and set(after)<=set(before);assert all(before[k]==v for k,v in after.items())
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True);assert running.stdout.strip()=='0'
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat';raw=launcher.read_bytes();mods=json.loads(raw.decode('utf-8-sig'));original=copy.deepcopy(mods)
active=[m for m in mods if m.get('game')=='warhammer3' and m.get('active') and m.get('uuid','').startswith('mc_moonshadow_heroes_')];assert len(active)==1 and active[0]['uuid']==old
target=[m for m in mods if m.get('game')=='warhammer3' and m.get('uuid')==new];assert len(target)==1 and not target[0]['active']
backup=O/('launcher-backup-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.dat');backup.write_bytes(raw)
active[0]['active']=False;target[0]['active']=True;target[0]['order']=active[0]['order']
other=lambda rs:[r for r in rs if not(r.get('game')=='warhammer3' and r.get('uuid') in [old,new])];assert other(mods)==other(original)
assert launcher.read_bytes()==raw;temp=launcher.with_name(launcher.name+'.moon-ui-crash-rollback.tmp');temp.write_text(json.dumps(mods,ensure_ascii=False,separators=(',',':')),encoding='utf8');os.replace(temp,launcher);assert json.loads(launcher.read_text(encoding='utf-8-sig'))==mods
report=dict(status='rolled_back_enabled',enabled=new,disabled=old,enabled_sha256=sha(data/new),removed_payload=bad,all_other_payloads_byte_identical=True,unrelated_launcher_entries_unchanged=True,backup=str(backup),saves_modified=False,pack_files_modified=False,game_launched=False,runtime_verified=False)
(O/'rollback.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
