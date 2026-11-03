import json,ast
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');O=R/'build/huyen-ve-v16-approved'
tree=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-animation-integration/diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');changes={p:v for p,v in new.items() if old.get(p)!=v};print('DIAGNOSTIC_CHANGES',len(changes));print(json.dumps(changes)[:3000]);assert not changes
p=O/'pack-validation.json';report=json.loads(p.read_text());report['new_or_changed_diagnostics_vs_v15']=0;p.write_text(json.dumps(report,indent=2))
