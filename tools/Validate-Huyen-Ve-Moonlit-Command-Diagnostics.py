import ast,json
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');O=R/'build/huyen-ve-v19-moonlit-command';t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diag>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-v18-item-reequip/diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');changes={p:v for p,v in new.items() if v and old.get(p)!=v};metadata=[];blocking=[]
for p,items in changes.items():
 for r in items:
  if set(r['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(cell[0]==-1 for cell in r['cells_affected']):metadata.append({'path':p,'field':r['report_type']['NoReferenceTableNorColumnFoundNoPak']})
  else:blocking.append({'path':p,'report':r})
print('METADATA_WARNINGS',len(metadata),'BLOCKING',json.dumps(blocking));assert not blocking,blocking
p=O/'pack-validation.json';v=json.loads(p.read_text());v['new_blocking_diagnostics']=0;v['new_schema_metadata_warnings']=metadata;p.write_text(json.dumps(v,indent=2))
p=R/'src/campaign/moon-warden.json';s=json.loads(p.read_text());s['status']='v19_moonlit_command_static_checked_runtime_pending';s['magic_skill_line']=["Dragon's Breath",'Earth Blood','Moonlit Command','Flame Storm'];s['moonlit_command']={'skill_key':'mc_moon_warden_magic_moonlit_command','ability_key':'mc_huyen_ve_moonlit_command','levels':1,'cost':'one skill point','prerequisite':'Earth Blood learned','weapon_damage_percent':25,'bonus_vs_large':16,'duration_seconds':20,'radius_m':35,'cooldown_seconds':90,'winds_cost':0,'native_donor':'wh_dlc06_lord_abilities_spite_of_da_bad_moon'};p.write_text(json.dumps(s,indent=2,ensure_ascii=True)+'\n')
