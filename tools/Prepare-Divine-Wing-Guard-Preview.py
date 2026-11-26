"""Extract private preview dependencies only; never edit game/Workshop inputs."""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
P = argparse.ArgumentParser()
P.add_argument('--game', required=True, type=Path)
P.add_argument('--angels', required=True, type=Path)
A = P.parse_args()
D = R / 'reference/local/divine-wing-guard'
O = R / 'build/divine-wing-guard-preview'
D.mkdir(parents=True, exist_ok=True)
O.mkdir(parents=True, exist_ok=True)
GAME = A.game / 'data'
assert GAME.is_dir() and A.angels.is_file()
sys.path.insert(0, str(Path(C['rpfm']).parent.parent / 'rmv2-addon'))
import rmv2_format as rf

indexes = {}
provenance = {}
aliases = {}

def norm(path):
    return path.replace('\\', '/').strip().lower()

def index(pack):
    key = str(pack)
    if key not in indexes:
        cache = D / 'indexes' / (pack.stem + '.json')
        fingerprint = [pack.stat().st_size, pack.stat().st_mtime_ns]
        if cache.exists() and json.loads(cache.read_text())['fingerprint'] == fingerprint:
            indexes[key] = json.loads(cache.read_text())['paths']
        else:
            result = subprocess.run([C['rpfm'], '-g', 'warhammer_3', 'pack', 'list', '-p', key],
                                    check=True, capture_output=True, text=True, encoding='utf-8')
            paths = {norm(p): p.strip() for p in result.stdout.splitlines()
                     if p.strip() and '[INFO]' not in p and '[WARN]' not in p}
            indexes[key] = paths
            cache.parent.mkdir(exist_ok=True)
            cache.write_text(json.dumps(dict(fingerprint=fingerprint, paths=paths)))
    return indexes[key]

def resolve(paths, kind='model'):
    wanted = {norm(p) for p in paths if p}
    todo = {p for p in wanted if not (D / p).is_file()}
    packs = [A.angels]
    if kind == 'texture':
        packs += sorted(GAME.glob('variants_dds*.pack')) + [GAME / 'commontextures.pack']
    elif kind == 'animation':
        packs += [GAME / 'anim.pack', GAME / 'anim2.pack', GAME / 'anim_3.pack']
    else:
        packs += [p for p in sorted(GAME.glob('variants*.pack')) if '_dds' not in p.name]
    for pack in packs:
        if not todo:
            break
        ix = index(pack)
        hits = sorted(todo & ix.keys())
        for start in range(0, len(hits), 20):
            batch = hits[start:start+20]
            subprocess.run([C['rpfm'], '-g', 'warhammer_3', 'pack', 'extract', '-p', str(pack),
                            '-f', *[ix[p] + ';' + str(D) for p in batch]], check=True,
                           stdout=subprocess.DEVNULL)
            for p in batch:
                provenance[p] = str(pack)
        todo -= set(hits)
    # Only accept unambiguous known native basename aliases.
    for path in list(todo):
        if not path.endswith(('.dds', '.xml.material')):
            continue
        replacement = path.replace('_diffuse.dds', '_base_colour.dds')
        if path == 'commontextures/default_black.dds':
            replacement = 'commontextures/default_black_srgb.dds'
        for pack in packs:
            ix = index(pack)
            hits = [replacement] if replacement != path and replacement in ix else [
                p for p in ix if Path(p).name in {Path(path).name, Path(replacement).name}]
            if len(hits) == 1:
                actual = hits[0]
                subprocess.run([C['rpfm'], '-g', 'warhammer_3', 'pack', 'extract', '-p', str(pack),
                                '-f', ix[actual] + ';' + str(D)], check=True,
                               stdout=subprocess.DEVNULL)
                destination = D / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((D / actual).read_bytes())
                aliases[path] = actual
                provenance[path] = str(pack)
                todo.remove(path)
                break
    if todo:
        raise RuntimeError('Unresolved dependencies: ' + repr(sorted(todo)))

def xml(path):
    # Some source materials have a malformed root, but well-formed texture pairs.
    data = (D / path).read_text(encoding='utf-8-sig')
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        root = ET.Element('material')
        for slot, source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>', data, re.S):
            tx = ET.SubElement(root, 'texture')
            ET.SubElement(tx, 'slot').text = slot
            ET.SubElement(tx, 'source').text = source
        assert list(root), path
        return root

prefix = 'variantmeshes/wh_variantmodels/hu1e/cth/'
models = [
    dict(role='body', path=prefix+'cth_jade_warrior/cth_jade_warrior_body_01.wsmodel'),
    dict(role='head', path=prefix+'cth_jade_warrior/cth_jade_warrior_head_01.wsmodel'),
    dict(role='sword', attach='weapon_2', path=prefix+'cth_props/cth_jade_warrior_sword_1h_01.wsmodel'),
    dict(role='shield', attach='weapon_3', path=prefix+'cth_props/cth_jade_warrior_shield_01.wsmodel'),
]
for name in ['terickz_angel_body_first_01', 'terickz_angel_body_first_02', 'terickz_angels_seraphim']:
    models.append(dict(role='wing_source', path='variantmeshes/wh_variantmodels/hu16c/dae/dae_valkia/body/'+name+'.rigid_model_v2'))
resolve([m['path'] for m in models])
textures = set()
for m in models:
    m['geometry'] = norm(xml(m['path']).findtext('geometry')) if m['path'].endswith('.wsmodel') else m['path']
    resolve([m['geometry']])
    data = rf.load((D/m['geometry']).read_bytes())
    material_paths = {}
    if m['path'].endswith('.wsmodel'):
        material_paths = {int(x.get('part_index')): norm(x.text)
                          for x in xml(m['path']).findall('.//material') if x.get('lod_index') == '0'}
        resolve(material_paths.values())
    m.update(skeleton=data.skeleton_name, lods=len(data.lods), parts=[])
    for i, part in enumerate(data.lods[0].models):
        # Preview uses modern colour/normal/material-map channels, not obsolete
        # specular/gloss references embedded in third-party source materials.
        pairs = [(int(t), norm(p)) for t, p in part.material.textures
                 if int(t) in (0, 1, 3, 27, 29) and p.lower().endswith('.dds')]
        if i in material_paths:
            pairs = []
            for tx in xml(material_paths[i]).findall('.//texture'):
                kind = {'t_xml_base_colour':27, 't_xml_diffuse':0, 't_xml_normal':1,
                        't_xml_material_map':29, 't_xml_mask':3}.get(tx.findtext('slot'))
                source = tx.findtext('source')
                if kind is not None and source and source.lower().endswith('.dds'):
                    pairs.append((kind, norm(source)))
        textures.update(p for _,p in pairs)
        m['parts'].append(dict(index=i, name=part.material.model_name, textures=pairs,
                               material=material_paths.get(i), vertices=len(part.mesh.positions),
                               bounds=[part.mesh.positions.min(axis=0).tolist(),part.mesh.positions.max(axis=0).tolist()]))
    print(m['role'],Path(m['path']).name,m['skeleton'],len(m['parts']),'parts',flush=True)
resolve(textures, 'texture')
skeletons = sorted({m['skeleton'] for m in models if m['skeleton']})
resolve(['animations/skeletons/'+s+'.anim' for s in skeletons], 'animation')
idle = 'animations/battle/humanoid01e/sword_shield/stand/hu1e_sword_and_shield_stand_01.anim'
resolve([idle], 'animation')
report = dict(name='Divine Wing Guard',game=str(A.game),angels=str(A.angels),models=models,
              texture_count=len(textures),skeletons=skeletons,reference=str(D),aliases=aliases,
              provenance=provenance,idle=idle,game_modified=False,preview_only=True)
(O/'asset-manifest.json').write_text(json.dumps(report,indent=2))
print('ASSETS_READY',len(models),len(textures),skeletons,flush=True)
