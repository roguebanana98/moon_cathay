"""Resolve native Khainite Assassin props and skeleton into ignored references."""
import json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/khainite-weapons';D.mkdir(parents=True,exist_ok=True)
base='variantmeshes/wh_variantmodels/hu1d/def/def_props/'
ws=[base+'def_khanite_assassin_dagger_%02d.wsmodel'%i for i in range(1,4)]+[base+'def_assassin_bow_1h_01_rigid.wsmodel']
game=Path(C['game'])/'data'
def listing(p):return set(subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(p)],text=True,stderr=subprocess.DEVNULL).splitlines())
def extract(pack,paths):
    if paths:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f']+[p+';'+str(D) for p in sorted(paths)],check=True,stdout=subprocess.DEVNULL)
remaining=set(ws)
for pack in [game/('variants'+suffix+'.pack') for suffix in ['', '2','3','4','5']]:
    hits=remaining&listing(pack);extract(pack,hits);remaining-=hits
    if not remaining:break
assert not remaining,remaining
want=set()
for path in ws:
    tree=E.parse(D/path);want.add(tree.findtext('geometry').replace('\\','/').lower())
    want.update(n.text.replace('\\','/').lower() for n in tree.findall('.//material'))
for pack in [game/('variants'+suffix+'.pack') for suffix in ['', '2','3','4','5']]:
    hits=want&listing(pack);extract(pack,hits);want-=hits
    if not want:break
assert not want,want
textures=set()
for p in D.rglob('*.material'):
    for tx in E.parse(p).findall('.//texture'):
        if tx.findtext('slot') in ['t_xml_base_colour','t_xml_diffuse','t_xml_normal','t_xml_material_map']:
            textures.add(tx.findtext('source').replace('\\','/').lower())
for pack in game.glob('variants_dds*.pack'):
    hits=textures&listing(pack);extract(pack,hits);textures-=hits
    if not textures:break
assert not textures,textures
sk='animations/skeletons/humanoid01d.anim'
for pack in [game/'anim.pack',game/'anim2.pack',game/'anim_3.pack']:
    if sk in listing(pack):extract(pack,[sk]);break
assert (D/sk).exists()
(D/'weapon-reference.json').write_text(json.dumps(dict(wsmodels=ws,source_dagger_bone='be_prop_1',source_crossbow_bone='be_prop_5',read_only_source=True),indent=2))
print('Native dagger variants, handbow, materials, textures and humanoid01d skeleton ready')
