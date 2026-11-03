"""Graphics-only revision over active r5, preserving every unrelated payload."""
import ast,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain';G=R/'build/huyen-ve-fantasy-longsword'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
graphics=json.loads((G/'graphics-validation.json').read_text());animation=json.loads((G/'exported-animation-validation.json').read_text())
assert graphics['status']=='exported_graphics_passed' and animation['status']=='passed'
v=json.loads((O/'pack-validation.json').read_text());base=O/'mc_huyen_ve_v25_quest_chain_test_r5.pack';pack=O/'mc_huyen_ve_v25_quest_chain_test_r6.pack'
assert v['pack']==str(base) and hashlib.sha256(base.read_bytes()).hexdigest()==v['sha256']
assert not pack.exists();shutil.copy2(base,pack)
files=graphics['files']
for p in files:
 assert hashlib.sha256((G/p).read_bytes()).hexdigest()==graphics['sha256'][p]
 subprocess.run([C['rpfm'],'-g','warhammer_3','pack','add','-p',str(pack),'-f',str(G/p)+';'+p],check=True,stdout=subprocess.DEVNULL)
for name,fnname in [('Validate-Repaired-Province-Packs.py','unpack'),('Validate-Huyen-Ve-Animation-Pack.py','diagnostic_rows')]:
 t=ast.parse((R/'tools'/name).read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==fnname);exec(compile(ast.Module(body=[fn],type_ignores=[]),name,'exec'))
before=unpack(base);after=unpack(pack)
assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items() if p not in files)
assert all(after[p]==(G/p).read_bytes() for p in files)
# Existing VMD, body and native runtime animation link remain byte-identical.
assert before['variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition']==after['variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition']
with (G/'pack-diagnostics.txt').open('w',encoding='utf-8') as f:
 subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(pack)],check=True,stdout=f,stderr=subprocess.STDOUT)
old=diagnostic_rows(O/'diagnostics.txt');new=diagnostic_rows(G/'pack-diagnostics.txt')
assert old==new,'Diagnostics changed; review before deployment'
v.update(pack=str(pack),base=str(base),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),files=files,deployed=False,runtime_verified=False,portrait_only=False,sword_graphics_only=True)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2))
report=dict(status='passed',pack=str(pack),sha256=v['sha256'],files=files,all_unrelated_payloads_byte_identical=True,diagnostics_unchanged=True,lods=graphics['lods'],animation_sampled_poses=animation['sampled_poses'],game_runtime_verified=False)
(G/'pack-validation.json').write_text(json.dumps(report,indent=2))
spec=dict(character='mc_moon_warden',selected_sword='user_fantasy_longsword',source_folder='assets/authored/fantasy longsword 3d model',approved_preview='build/huyen-ve-fantasy-longsword/huyen-ve-fantasy-sword-preview.blend',graphics_manifest='build/huyen-ve-fantasy-longsword/graphics-validation.json',graphics_root='build/huyen-ve-fantasy-longsword',attachment='weapon_2',status='private_candidate_r6',game_runtime_verified=False)
(R/'src/campaign/huyen-ve-sword.json').write_text(json.dumps(spec,indent=2))
print(json.dumps(report,indent=2))
