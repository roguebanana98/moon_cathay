import json,copy,shutil,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'payload';KEY='edh_heinrich_cb';ART=KEY+'_art'
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe';SCHEMA=r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron'
v=json.loads((R/'pack_validation.json').read_text());previous=Path(v['pack']);P=R/'edh_heinrich_custom_battle_v2.pack'
assert not P.exists();shutil.copy2(previous,P)
added=[]
for folder in ['units','portholes']:
    source=json.loads((R/('reference/'+folder+'_portraits.json')).read_text())
    donor=next(e for e in source['entries'] if e['id']=='wh_main_art_set_emp_general_01')
    entry=copy.deepcopy(donor);entry['id']=ART
    texture='ui/portraits/'+folder+'/no_culture/'+KEY+'_0.png';p=O/texture;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'heinrich_portrait.png',p)
    variant=entry['variants'][0];variant.update(filename=KEY,file_diffuse=texture,file_mask_1='',file_mask_2='',file_mask_3='',faction_leader=False)
    entry['variants']=[variant];source['entries']=[entry]
    jp=R/('portrait_'+folder+'_private.json');jp.write_text(json.dumps(source,indent=2))
    binary='ui/portraits/'+folder+'/portrait_settings__'+KEY+'.bin';bp=O/binary
    subprocess.run([CLI,'-g','warhammer_3','portrait-settings','from-json','-j',str(jp),'-b',str(bp)],check=True,stdout=subprocess.DEVNULL)
    for path in [texture,binary]:
        subprocess.run([CLI,'-g','warhammer_3','pack','add','-p',str(P),'-f',str(O/path)+';'+path],check=True,stdout=subprocess.DEVNULL)
        if path not in v['payloads']:v['payloads'].append(path);added.append(path)
v.update(pack=str(P),sha256=hashlib.sha256(P.read_bytes()).hexdigest(),graphics_count=v['graphics_count']+len(added),status='portrait_settings_patched_pending_diagnostics',deployed=False,previous_pack=str(previous),runtime_verified=False)
v['runtime_v1']={'custom_battle_listing':True,'selected_and_recruited':True,'battle_loaded':True,'model_and_textures_visible':True,'native_sword_shield_visible':True,'movement_command_completed':True,'portrait_card_fallback_observed':True}
(R/'pack_validation.json').write_text(json.dumps(v,indent=2))
with (R/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([CLI,'-g','warhammer_3','pack','diagnose','-g',r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III','-P',str(R/'wh3-current.pak2'),'-s',SCHEMA,'-p',str(P)],check=True,stdout=f,stderr=subprocess.STDOUT)
subprocess.run([CLI,'-g','warhammer_3','pack','extract','-p',str(P),'-t',SCHEMA,'-F','/;'+str(R/'roundtrip_final')],check=True,stdout=subprocess.DEVNULL)
print('PORTRAIT_SETTINGS_PATCHED',len(added),'payloads')
