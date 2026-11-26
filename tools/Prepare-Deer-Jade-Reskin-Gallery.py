"""Private source-model gallery dependencies; source packs remain read-only."""
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import re

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
SOURCE=Path(r'H:\SteamLibrary\steamapps\workshop\content\1142710\2965749119\@DEER24JadeWarriorRESKIN2.pack')
base=json.loads((R/'build/divine-wing-guard-preview/asset-manifest.json').read_text())
A=SimpleNamespace(angels=SOURCE,game=Path(base['game']))
GAME=A.game/'data';D=R/'reference/local/deer-jade-reskin';O=R/'build/deer-jade-reskin-gallery'
D.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
assert SOURCE.is_file() and GAME.is_dir()
indexes={};provenance={};aliases={}
helpers=ast.parse((R/'tools/Prepare-Divine-Wing-Guard-Preview.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['norm','index','resolve','xml']],type_ignores=[]),'<read-only asset helpers>','exec'))
sys.path.insert(0,str(Path(C['rpfm']).parent.parent/'rmv2-addon'))
import rmv2_format as rf

ix=index(SOURCE)
paths=sorted(p for p in ix if p.endswith('.wsmodel') and p.startswith('1/beitingsheshou/'))
assert len(paths)==13,paths
models=[];textures=set();material_fallbacks=[]
for path in paths:
    resolve([path]);tree=xml(path);geo=norm(tree.findtext('geometry'));resolve([geo])
    m=rf.load((D/geo).read_bytes())
    mats={int(x.get('part_index')):norm(x.text) for x in tree.findall('.//material') if x.get('lod_index')=='0'}
    for material in set(mats.values()):
        try:resolve([material])
        except RuntimeError:
            # A source WSModel can retain a stale material override path.
            # The RMV2's own embedded material remains a usable preview source.
            material_fallbacks.append(dict(model=path,missing_override=material,uses='embedded RMV2 material'))
    parts=[]
    for i,part in enumerate(m.lods[0].models):
        pairs=[(int(t),norm(p)) for t,p in part.material.textures if int(t) in (0,1,3,27,29) and p.lower().endswith('.dds')]
        if i in mats and (D/mats[i]).exists():
            pairs=[]
            for tx in xml(mats[i]).findall('.//texture'):
                typ={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29,'t_xml_mask':3}.get(tx.findtext('slot'))
                source=tx.findtext('source')
                if typ is not None and source and source.lower().endswith('.dds'):pairs.append((typ,norm(source)))
        textures.update(p for _,p in pairs)
        parts.append(dict(index=i,name=part.material.model_name,vertices=len(part.mesh.positions),textures=pairs,material=mats.get(i)))
    role='head' if re.search(r'h\d+\.wsmodel$',path) else 'rider_body' if '_lancer' in path else 'body'
    models.append(dict(role=role,path=path,geometry=geo,skeleton=m.skeleton_name,lods=len(m.lods),parts=parts))
    print(role,Path(path).name,m.skeleton_name,len(parts),flush=True)
resolve(textures,'texture')
# Reuse the already extracted native reference paths for the common sword/shield.
props=[]
for model in base['models']:
    if model['role'] not in ['sword','shield']:continue
    for p in [model['path'],model['geometry']]+[t for part in model['parts'] for _,t in part['textures']]:
        target=D/p
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'reference/local/divine-wing-guard'/p,target)
    props.append(model)
resolve(['animations/skeletons/humanoid01e.anim'],'animation')
idle=base['idle'];resolve([idle],'animation')
report=dict(source=str(SOURCE),source_bytes=SOURCE.stat().st_size,source_mtime_ns=SOURCE.stat().st_mtime_ns,
            models=models,props=props,idle=idle,aliases=aliases,provenance=provenance,
            body_count=5,rider_body_count=1,head_count=7,material_fallbacks=material_fallbacks,preview_only=True,game_modified=False)
(O/'manifest.json').write_text(json.dumps(report,indent=2))
print('DEER_JADE_ASSETS_READY',len(models),len(textures),flush=True)
