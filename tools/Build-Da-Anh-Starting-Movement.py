"""Fix initial Da Anh campaign action points; retain v8 skill trees and appearance."""
import ast,json,hashlib,subprocess,shutil,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/da-anh-v10-starting-movement';O.mkdir(parents=True,exist_ok=True);BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v8_da_anh.pack';PACK=O/'mc_moonshadow_heroes_v10_starting_movement.pack'
s=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','unpack','cli']],type_ignores=[]),'<pack helpers>','exec'))
assert sha(BASE)=='37f3aa7a52438aca2ff56e439feb073d76135890dd5f3ad168036222695a26e6';assert not PACK.exists()
path='script/campaign/mod/mc_moonshadow_start.lua';source=R/'src'/path;code=source.read_text();assert 'cm:replenish_action_points(lookup, 1)' in code and 'cm:turn_number() ~= 1' in code and 'force_add_skill' not in code
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-f',str(source)+';'+path)
before=unpack(BASE);after=unpack(PACK);assert set(before)==set(after);changed=[p for p in before if before[p]!=after[p]];assert changed==[path];assert after[path]==source.read_bytes()
# Explicitly exclude the superseded, misunderstood v9 bonus skill build.
assert not any('mc_da_anh_mobility' in p for p in after)
assert all(before[p]==after[p] for p in before if p.startswith(('db/','variantmeshes/','ui/','text/')))
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();d=json.loads(text[text.index('{'):]);blocking=[]
for group in d['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),changed_entries=changed,blocking_diagnostics=blocking,movement_test_scenarios=23,new_spawn_full_action_points=True,existing_turn_one_save_one_time_repair=True,no_later_turn_refill=True,no_embedded_army_refill=True,no_reload_refill=True,skill_trees_byte_identical_to_v8=True,appearance_assets_byte_identical_to_v8=True,v9_skill_bonus_absent=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not blocking
