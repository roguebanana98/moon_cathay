"""Add only the new-campaign placement script over the current r6 pack."""
import ast,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
v=json.loads((O/'pack-validation.json').read_text());base=O/'mc_huyen_ve_v25_quest_chain_test_r6.pack';pack=O/'mc_huyen_ve_v25_quest_chain_test_r7.pack'
assert v['pack']==str(base) and hashlib.sha256(base.read_bytes()).hexdigest()==v['sha256']
q=json.loads((O/'lua-regression.json').read_text());assert q['status']=='passed'
p='script/campaign/mod/mc_huyen_ve_start_at_long_vi.lua'
assert hashlib.sha256((R/'src'/p).read_bytes()).hexdigest()==q['source_sha256'][str(Path('src')/p)]
assert not pack.exists();shutil.copy2(base,pack)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','add','-p',str(pack),'-f',str(R/'src'/p)+';'+p],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'reader','exec'))
before=unpack(base);after=unpack(pack)
assert p not in before and set(after)==set(before)|{p}
assert all(after[key]==b for key,b in before.items()) and after[p]==(R/'src'/p).read_bytes()
v.update(pack=str(pack),base=str(base),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),files=[p],deployed=False,runtime_verified=False,sword_graphics_only=False,new_campaign_start_only=True)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2))
report=dict(status='passed',pack=str(pack),sha256=v['sha256'],added_script=p,all_existing_payloads_byte_identical=True,startpos_esf_unchanged=True,native_api='pre_first_tick + new_game guard + valid land + teleport_to existing commander',existing_saves_unchanged=True,game_runtime_verified=False)
(O/'long-vi-start-validation-r7.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
