import json,subprocess,ast,xml.etree.ElementTree as E,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));D=R/'reference/local/night-assassin'
s=ast.parse((R/'tools/Prepare-Xiao-Preview.py').read_text());exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name=='resolve'],type_ignores=[]),'<native resolver>','exec'))
B='variantmeshes/wh_variantmodels/hu1d/def/def_khanite_assassin/'
ws=[B+'def_khanite_assassin_'+kind+'_%02d.wsmodel'%i for kind,count in [('head',4),('torso',4),('legs',2)] for i in range(1,count+1)]
ws+=['variantmeshes/wh_variantmodels/hu1d/def/def_props/def_khanite_assassin_dagger_01.wsmodel','variantmeshes/wh_variantmodels/hu1d/def/def_props/def_assassin_bow_1h_01_rigid.wsmodel']
assert not resolve(set(ws),'variants*.pack')
want=set()
for p in ws:
 t=E.parse(D/p);want.add(t.findtext('geometry').replace('\\','/').lower());want.update(x.text.replace('\\','/').lower() for x in t.findall('.//material'))
assert not resolve(want,'variants*.pack')
tex={path.replace('\\','/').lower() for p in want if p.endswith('.material') for slot,path in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',(D/p).read_text()) if slot in ['t_xml_base_colour','t_xml_diffuse','t_xml_normal','t_xml_material_map']}
assert not resolve(tex,'variants_dds*.pack')
print('READY',len(ws),'wsmodels',len(tex),'textures')
