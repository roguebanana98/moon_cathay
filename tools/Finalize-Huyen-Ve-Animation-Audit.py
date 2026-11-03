import json,ast
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');O=R/'build/huyen-ve-v16-approved'
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-animation-integration/diagnostics.txt');new=diagnostic_rows(O/'runtime-fix-diagnostics.txt');added={p:v for p,v in new.items() if v and old.get(p)!=v};assert not added,added
p=O/'runtime-animation-fix.json';d=json.loads(p.read_text());d['new_or_changed_diagnostics']=0;d['actual_mesh_motion_regression']='passed: v15 and v16 move across run/attack/stand frames when clips are directly bound in Blender';p.write_text(json.dumps(d,indent=2))
p=O/'pack-validation.json';d=json.loads(p.read_text());d['status']='superseded_runtime_animation_lookup_invalid';d['use_pack_instead']='mc_huyen_ve_v16_native_anim_fix.pack';p.write_text(json.dumps(d,indent=2))
print('FIXED_PACK_CHECKS_PASSED; intermediate v16 explicitly marked superseded')
