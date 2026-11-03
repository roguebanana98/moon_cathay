"""Integrate validated v22 graphics over v21, preserving every gameplay and script payload."""
import ast,json,hashlib,shutil,subprocess,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-v22-da-lien-appearance';BASE=R/'build/huyen-ve-v21-da-lien-custom-battle/mc_huyen_ve_v21_da_lien_custom_battle.pack'
PACK=O/'mc_huyen_ve_v22_da_lien_appearance.pack'
graphics=json.loads((O/'graphics-validation.json').read_text());animation=json.loads((O/'animation-validation.json').read_text())
assert graphics['status']=='graphics_checks_passed' and animation['status']=='passed'
assert not PACK.exists();shutil.copy2(BASE,PACK)
for internal in graphics['files']:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK),'-f',str(O/internal)+';'+internal],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack>','exec'));before=unpack(BASE);after=unpack(PACK)
assert set(after)==set(before)|set(graphics['files'])
changed=[p for p in before if before[p]!=after[p]];added=sorted(set(after)-set(before))
assert all(p.startswith('variantmeshes/wh_variantmodels/mc_da_lien/') for p in changed+added)
assert all(before[p]==after[p] for p in before if p not in graphics['files'])
assert all(after[p]==(O/p).read_bytes() for p in graphics['files'])
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-v21-da-lien-custom-battle/diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt')
diff={p:v for p,v in new.items() if v and old.get(p)!=v};assert not diff,diff
report={'status':'static_checks_passed','pack':str(PACK),'sha256':hashlib.sha256(PACK.read_bytes()).hexdigest(),
 'base':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'changed_entries':changed,'new_entries':added,
 'graphics_payload_hash_checks':len(graphics['files']),'all_gameplay_db_scripts_startpos_unchanged':True,
 'custom_battle_and_campaign_spawn_preserved':True,'new_blocking_diagnostics':0,'new_or_changed_diagnostics':0,
 'approved_model_edits':['removed raised rear collar','baked warm human skin','silver/gold crescent staff head'],
 'exported_animation_clips_tested':len(animation['clips']),'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
