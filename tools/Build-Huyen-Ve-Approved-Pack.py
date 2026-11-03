"""Build private v16 over v15; prove only graphics entries change."""
import ast,json,hashlib,subprocess,shutil,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v16-approved';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));base=R/'build/huyen-ve-animation-integration/mc_huyen_ve_v15_model_animations.pack';pack=O/'mc_huyen_ve_v16_approved_model.pack'
assert json.loads((O/'animation-validation.json').read_text())['status']=='passed'
graphics=json.loads((O/'graphics-validation.json').read_text());body=O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve_v2/mc_huyen_ve_body.rigid_model_v2';assert hashlib.sha256(body.read_bytes()).hexdigest()==graphics['body_sha256']
assert not pack.exists(),'Refusing overwrite existing private pack'
shutil.copy2(base,pack)
files=sorted(p.relative_to(O).as_posix() for p in (O/'variantmeshes').rglob('*') if p.is_file())
for path in files:
 subprocess.run([C['rpfm'],'-g','warhammer_3','pack','add','-p',str(pack),'-f',str(O/path)+';'+path],check=True,stdout=subprocess.DEVNULL)
tree=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(base);after=unpack(pack);changed=[p for p in before if before[p]!=after.get(p)];added=sorted(set(after)-set(before))
assert set(after)==set(before)|set(files)
assert all(p.startswith('variantmeshes/') for p in changed+added)
assert all(after[p]==(O/p).read_bytes() for p in files)
assert before['campaigns/cr_combi_expanded/startpos.esf']==after['campaigns/cr_combi_expanded/startpos.esf']
for p in before:
 if not p.startswith('variantmeshes/'):assert before[p]==after[p],p
report={'status':'passed','pack':str(pack),'sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),'base_pack':str(base),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changed_existing_entries':changed,'new_entries':added,'payload_hash_checks':len(files),'all_non_graphics_payloads_unchanged':True,'source_mod_buffs_flags_or_DB_imported':False,'native_clips_referenced_not_bundled':True,'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='new_entries'},indent=2))

# A text animation table is not a runtime database. Always finish with the
# native animation lookup repair; the intermediate pack is not a test candidate.
subprocess.run([C['python'],str(R/'tools/Fix-Huyen-Ve-Runtime-Animation-Link.py')],check=True)
