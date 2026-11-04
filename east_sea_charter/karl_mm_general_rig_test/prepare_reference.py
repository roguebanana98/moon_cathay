from pathlib import Path
import subprocess,concurrent.futures,json,xml.etree.ElementTree as ET,hashlib,re
R=Path(__file__).resolve().parent;D=R/'reference'
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data')
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
def listing(p):
    f=R/'indices'/(p.stem+'.txt')
    if not f.exists():f.write_text(subprocess.check_output([CLI,'-g','warhammer_3','pack','list','-p',str(p)],text=True,stderr=subprocess.DEVNULL),encoding='utf8')
    return [s.strip() for s in f.read_text(encoding='utf8').splitlines() if '/' in s and not s.startswith('0')]
def extract(pack,paths):
    paths=list(dict.fromkeys(paths))
    for i in range(0,len(paths),40):
        args=[CLI,'-g','warhammer_3','pack','extract','-p',str(pack),'-f']+[p+';'+str(D) for p in paths[i:i+40]]
        subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def getfile(p):
    path=D/p
    if path.exists():return
    for pack,paths in indexes.items():
        if p.lower() in paths:
            extract(pack,[paths[p.lower()]]);return
    raise FileNotFoundError(p)
packs=[GAME/n for n in ['variants.pack','variants2.pack','variants3.pack','variants4.pack','variants5.pack','anim.pack','anim2.pack','anim_3.pack','data.pack']]
indexes={p:{s.lower():s for s in listing(p)} for p in packs}
vmds=['emp_general_base','emp_generals','emp_general_swords_1h_set1','emp_general_shield_1h_set1']
for n in vmds:getfile('variantmeshes/variantmeshdefinitions/'+n+'.variantmeshdefinition')
base='variantmeshes/wh_variantmodels/hu1/emp/'
for p in ['emp_generals/emp_generals_body_01','emp_generals/emp_generals_cape_01','emp_generals/emp_generals_head_01','emp_generals/emp_generals_legs_01','emp_props/emp_general_sword_1h_01','emp_props/emp_general_shield_01']:
    for ext in ['.wsmodel','.rigid_model_v2']:getfile(base+p+ext)
for n in ['animations/skeletons/humanoid01.anim','animations/skeletons/reference_poses/humanoid01.anim','animations/database/battle/tables/hu1_empire_sword_and_shield.txt']:
    getfile(n)
table=json.loads((D/'animations/database/battle/tables/hu1_empire_sword_and_shield.txt').read_text())
slots={};fragments=[]
for e in table['Entries']:
    if e['Type']!='Fragment':continue
    p='animations/database/battle/fragments/'+e['Value']+'.txt';getfile(p)
    fr=json.loads((D/p).read_text());fragments.append(p)
    for slot,v in fr['SlotData'].items():
        if not v['Config'].get('Ignore'):slots[slot]=v
clips=[]
for slot,v in slots.items():
    if any(k in slot.lower() for k in ['stand','walk','run','attack','combat_idle','block']):
        choices=list(v['Entries'].values())
        if choices:
            p=choices[0]['animation']
            if p.endswith('.anim'):
                getfile(p);clips.append({'slot':slot,'path':p})
print('CLIPS',json.dumps(clips[:25]),flush=True)
# Obtain native DB row to document the donor's actual animation mapping.
for p in indexes[GAME/'data.pack'].values():
    if p.startswith('db/land_units_tables/'):
        subprocess.run([CLI,'-g','warhammer_3','pack','extract','-p',str(GAME/'data.pack'),'-t',r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron','-f',p+';'+str(D)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# Fill XML materials referenced by all wsmodels, preserving mod files first.
for ws in list(D.rglob('*.wsmodel')):
    tree=ET.parse(ws)
    for el in tree.findall('.//material'):
        if el.text:getfile(el.text.strip().replace('\\','/').lower())
tex=set()
for xml in D.rglob('*.xml.material'):
    for el in ET.parse(xml).findall('.//texture/source'):
        p=(el.text or '').strip().replace('\\','/').lower()
        if p and any(p.endswith(s) for s in ['_base_colour.dds','_material_map.dds','_normal.dds','_mask.dds']):tex.add(p)
ddspacks=sorted(GAME.glob('variants*dds*.pack'))+sorted(GAME.glob('models*dds*.pack'))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for p,lines in zip(ddspacks,ex.map(listing,ddspacks)):
        indexes[p]={s.lower():s for s in lines}
missing=[];texprovenance={}
for p in sorted(tex):
    try:
        getfile(p)
        texprovenance[p]=[k.name for k,v in indexes.items() if p in v]
    except FileNotFoundError:missing.append(p)
mod=Path(r'F:\SteamLibrary\steamapps\workshop\content\1142710\3728324408\Karl Franz Reskin - MM.pack')
manifest={'mod':str(mod),'mod_sha256':hashlib.sha256(mod.read_bytes()).hexdigest(),'skeleton':'humanoid01','table':table,'fragments':fragments,'clips':clips,'textures':texprovenance,'missing_textures':missing}
(R/'reference_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('REFERENCE_READY',len(clips),'clips',len(tex)-len(missing),'textures',missing,flush=True)
