import sys,json,importlib.util
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');s=importlib.util.spec_from_file_location('rf',R.parent/'tooling/model-workbench/addon-source/rmv2_format.py');rf=importlib.util.module_from_spec(s);sys.modules['rf']=rf;s.loader.exec_module(rf)
p=R/'reference/local/pandalorian-yuan-bo/variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.rigid_model_v2';f=rf.load(p.read_bytes());rows=[]
for i,l in enumerate(f.lods):
 parts=[{'part':j,'name':m.material.model_name,'vertices':m.mesh.vertex_count,'triangles':len(m.mesh.indices)//3,'bounds_min':m.mesh.positions.min(axis=0).tolist(),'bounds_max':m.mesh.positions.max(axis=0).tolist()} for j,m in enumerate(l.models)]
 rows.append({'lod':i,'distance':l.camera_distance,'parts':parts,'triangles':sum(x['triangles'] for x in parts)})
print(json.dumps({'skeleton':f.skeleton_name,'lods':[{'lod':x['lod'],'distance':x['distance'],'triangles':x['triangles'],'parts':len(x['parts'])} for x in rows],'names':[[p['name'] for p in x['parts']] for x in rows]},indent=2))
(R/'build/huyen-ve-model-v2/source-lod-audit.json').write_text(json.dumps(rows,indent=2))
