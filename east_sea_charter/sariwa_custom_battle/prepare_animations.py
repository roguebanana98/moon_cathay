from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parent;D=R/'reference'
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data')
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
lookup={}
for f in (R.parent/'karl_mm_general_rig_test/indices').glob('anim*.txt'):
    for line in f.read_text(encoding='utf8').splitlines():
        if '/' in line and not line.startswith('0'):lookup.setdefault(line.lower(),(GAME/(f.stem+'.pack'),line))
def get(path):
    path=path.replace('\\','/').lower();p=D/path
    if not p.exists():
        pack,source=lookup[path]
        subprocess.run([CLI,'-g','warhammer_3','pack','extract','-p',str(pack),'-f',source+';'+str(D)],check=True,stdout=subprocess.DEVNULL)
    return p
slots={};visited=set();fragment_paths=[]
def table(name):
    if name in visited:return
    visited.add(name)
    obj=json.loads(get('animations/database/battle/tables/'+name+'.txt').read_text())
    for e in obj['Entries']:
        if e['Type']=='Fragment':
            path='animations/database/battle/fragments/'+e['Value']+'.txt'
            f=json.loads(get(path).read_text());fragment_paths.append(path)
            for key,value in f['SlotData'].items():
                if not value['Config'].get('Ignore'):slots[key]=value
        elif e['Type'] in ('Table','AnimationTable'):table(e['Value'])
table('hu1b_bretonnian_staff_and_sword')
print('SLOTS',list(slots))
clips=[]
for slot,v in slots.items():
    if any(x in slot.lower() for x in ['stand','walk','run','attack','combat_idle','cast']):
        entries=list(v['Entries'].values())
        if entries:
            path=entries[0]['animation']
            if path.endswith('.anim'):
                get(path);clips.append({'slot':slot,'path':path})
manifest={'table':'hu1b_bretonnian_staff_and_sword','tables':list(visited),'fragments':fragment_paths,'clips':clips}
(R/'animation_manifest.json').write_text(json.dumps(manifest,indent=2))
print('CLIPS',len(clips),*clips,sep='\n')
