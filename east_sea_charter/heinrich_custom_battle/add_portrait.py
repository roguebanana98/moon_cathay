import csv,json,shutil,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'payload';P=R/'edh_heinrich_custom_battle_v1.pack';KEY='edh_heinrich_cb'
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe';SCHEMA=r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron'
v=json.loads((R/'pack_validation.json').read_text());portrait='ui/portraits/portholes/no_culture/'+KEY+'_0.png'
for path in [portrait,'ui/units/icons/'+KEY+'.png','ui/units/minspec_portholes/'+KEY+'.png']:
    target=O/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'heinrich_portrait.png',target)
    subprocess.run([CLI,'-g','warhammer_3','pack','add','-p',str(P),'-f',str(target)+';'+path],check=True,stdout=subprocess.DEVNULL)
    if path not in v['payloads']:v['payloads'].append(path)
for table,changes in [('unit_variants',{'unit_card':KEY}),('units_custom_battle_permissions',{'general_portrait':portrait}),('battle_set_piece_armies_characters',{'portrait':portrait})]:
    path='db/'+table+'_tables/'+KEY;src=O/(path+'.tsv')
    with src.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    for k,value in changes.items():rows[2][rows[0].index(k)]=value;v['rows'][table][0][k]=value
    with src.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows(rows)
    subprocess.run([CLI,'-g','warhammer_3','pack','add','-p',str(P),'-t',SCHEMA,'-f',str(src)+';'+path],check=True,stdout=subprocess.DEVNULL)
v['sha256']=hashlib.sha256(P.read_bytes()).hexdigest();v['portrait']='Blender render of tested Karl MM model';v['graphics_count']+=3
(R/'pack_validation.json').write_text(json.dumps(v,indent=2))
with (R/'diagnostics.txt').open('w',encoding='utf8') as f:
    subprocess.run([CLI,'-g','warhammer_3','pack','diagnose','-g',r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III','-P',str(R/'wh3-current.pak2'),'-s',SCHEMA,'-p',str(P)],check=True,stdout=f,stderr=subprocess.STDOUT)
