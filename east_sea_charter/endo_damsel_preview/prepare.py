from pathlib import Path
import subprocess,xml.etree.ElementTree as ET,json
R=Path(__file__).resolve().parent;D=R/'reference'
INDEX=R.parent/'karl_mm_general_rig_test/indices'
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data')
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
lookup={}
for f in INDEX.glob('*.txt'):
    pack=GAME/(f.stem+'.pack')
    if not pack.exists():continue
    for line in f.read_text(encoding='utf8').splitlines():
        if '/' in line and not line.startswith('0'):lookup.setdefault(line.lower(),(pack,line))
def get(path):
    path=path.strip().replace('\\','/').lower()
    if not (D/path).exists():
        pack,original=lookup[path]
        subprocess.run([CLI,'-g','warhammer_3','pack','extract','-p',str(pack),'-f',original+';'+str(D)],check=True,stdout=subprocess.DEVNULL)
    return D/path
variants=[]
weaponset='variantmeshes/variantmeshdefinitions/brt_lords_sword_1h_set1.variantmeshdefinition'
weaponxml=ET.parse(get(weaponset));sword=next(e.attrib['model'] for e in weaponxml.iter('VARIANT_MESH') if 'model' in e.attrib)
for i in range(1,5):
    vmd=D/f'variantmeshes/variantmeshdefinitions/endo_damsel_campaign_{i:02d}.variantmeshdefinition'
    xml=ET.parse(vmd);v={'name':f'Damsel {i:02d}','slots':[]}
    for slot in xml.findall('.//SLOT'):
        if slot.attrib['name'] not in ('head','body','weapon_2','weapon_5'):continue
        model=next((e.attrib['model'] for e in slot.iter('VARIANT_MESH') if 'model' in e.attrib),sword if slot.attrib['name']=='weapon_2' else None)
        if model:v['slots'].append({'slot':slot.attrib['name'],'bone':slot.attrib.get('attach_point'),'model':model.replace('\\','/').lower()})
    variants.append(v)
models={s['model'] for v in variants for s in v['slots']}
materials=set();textures=set()
for model in models:
    xml=ET.parse(get(model));get(xml.findtext('geometry'))
    for e in xml.findall('.//material'):
        if e.attrib.get('lod_index')=='0':materials.add(e.text.strip().replace('\\','/').lower())
for material in materials:
    xml=ET.parse(get(material))
    for tex in xml.findall('.//texture'):
        if tex.findtext('slot') in ('t_xml_base_colour','t_xml_normal','t_xml_material_map','t_xml_mask'):
            textures.add(tex.findtext('source').strip().replace('\\','/').lower())
missing=[]
for texture in textures:
    if texture=='commontextures/default_black.dds' and texture not in lookup:
        missing.append(texture);continue
    get(texture)
skel='animations/skeletons/humanoid01b.anim';pose='animations/battle/humanoid01b/staff_and_sword/stand/hu1b_sfsw_stand_pose_01.anim'
get(skel);get(pose)
manifest={'variants':variants,'skeleton':skel,'pose':pose,'materials':len(materials),'textures':len(textures),'missing_neutral_masks':missing}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
