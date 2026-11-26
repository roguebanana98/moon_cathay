"""One-payload native art-set binding hotfix over the deployed playable v5."""
import ast,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/sariwa-campaign-appearance';O.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));old=json.loads((R/'build/east-sea-playable/deployment.json').read_text());base=Path(old['deployed_path']);assert hashlib.sha256(base.read_bytes()).hexdigest()==old['sha256']
pack=O/'edh_east_sea_charter_sariwa_model_v6.pack';assert not pack.exists(),'Keep existing artifacts; use a new revision'
script='script/campaign/mod/edh_sariwa_campaign_appearance.lua'
shutil.copy2(base,pack)
def cli(*args):
 p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
 with (O/'build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
cli('pack','add','-p',pack,'-f',str(R/'src'/script)+';'+script)
t=ast.parse((R/'tools/Build-East-Sea-Playable.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='payloads');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<payload-reader>','exec'))
before=payloads(base);after=payloads(pack);assert set(after)-set(before)=={script};assert all(after[k]==v for k,v in before.items());assert after[script]==(R/'src'/script).read_bytes()
# Verify the actual installed asset pack, not only previously extracted sources.
asset=Path(C['game'])/'data/edh_heinrich_sariwa_v4.pack';assets=payloads(asset)
assert hashlib.sha256(asset.read_bytes()).hexdigest()=='0ef0b3d05dc9599013c31a5014a1e5bd3d24d5e4cc75a34cde53a5c418957239'
assert b'humanoid01b\0' in assets['variantmeshes/wh_variantmodels/edh/sariwa/edh_sariwa_body.rigid_model_v2'][:140]
assert b'edh_sariwa_naga.wsmodel' in assets['variantmeshes/variantmeshdefinitions/edh_sariwa.variantmeshdefinition']
q=R/'reference/local/sariwa-appearance-roundtrip';cli('pack','extract','-p',pack,'-f',script+';'+str(q));assert (q/script).read_bytes()==after[script]
report=dict(pack=str(pack),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),base_pack=str(base),base_sha256=old['sha256'],added_payloads=[script],all_v5_payloads_byte_identical=True,script_sha256=hashlib.sha256(after[script]).hexdigest(),existing_save_support=True,native_api='add_character_model_override(character, edh_sariwa_art)',asset_pack_verified=True,asset_pack=str(asset),battle_assets_and_skills_unchanged=True,runtime_verified=False,static_validation='payload_validation_passed')
(O/'build-report.json').write_text(json.dumps(report,indent=2));print('PASS: one Lua addition; all v5 payloads identical; installed Damsel/Naga assets verified')
