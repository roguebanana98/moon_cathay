import csv,json,subprocess,hashlib,shutil,xml.etree.ElementTree as ET,collections
from pathlib import Path
R=Path(__file__).resolve().parent;REF=R/'reference';SRC=R.parent/'karl_mm_general_rig_test/reference'
O=R/'payload';O.mkdir(exist_ok=True)
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
SCHEMA=r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron'
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III')
PACK=R/'edh_heinrich_custom_battle_v1.pack'
KEY='edh_heinrich_cb';DONOR='wh_main_emp_cha_general_0';NEWPATH='variantmeshes/wh_variantmodels/edh/heinrich_cb/'
files=[];table_rows={}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,stdout=subprocess.DEVNULL,**kw)
def read(table):
    with (REF/('db/'+table+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def one(table,k,v):
    rows=[r for r in read(table)[1] if r[k]==v];assert len(rows)==1,(table,k,v,len(rows));return rows[0]
def write(table,rows):
    (header,meta),_=read(table);path='db/'+table+'_tables/'+KEY
    assert all(set(r)<=set(header) for r in rows),table
    meta[0]=';'.join(meta[0].split(';')[:2]+[path]);p=O/(path+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows([header,meta]+[[r.get(k,'') for k in header] for r in rows])
    files.append(path);table_rows[table]=rows
def clone(table,k,v,**changes):
    row=dict(one(table,k,v),**changes);write(table,[row]);return row
def save_xml(tree,path):
    p=O/path;p.parent.mkdir(parents=True,exist_ok=True);tree.write(p,encoding='utf8',xml_declaration=False);files.append(path)
material_map={};texture_map={};geometry_sources={}
def private_material(path):
    path=path.replace('\\','/').lower()
    if path in material_map:return material_map[path]
    private=NEWPATH+'materials/'+f'm{len(material_map):02d}_'+Path(path).name
    material_map[path]=private
    tree=ET.parse(SRC/path)
    for e in tree.findall('.//texture/source'):
        source=(e.text or '').strip().replace('\\','/').lower()
        if source and (SRC/source).is_file():
            if source not in texture_map:
                dest=NEWPATH+'tex/'+hashlib.sha256(source.encode()).hexdigest()[:8]+'_'+Path(source).name
                texture_map[source]=dest;target=O/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SRC/source,target);files.append(dest)
            e.text=texture_map[source]
    save_xml(tree,private);return private
def private_model(stem,name):
    ws=SRC/('variantmeshes/wh_variantmodels/hu1/emp/'+stem+'.wsmodel');tree=ET.parse(ws)
    geometry=tree.find('geometry');source=geometry.text.strip().replace('\\','/').lower();dest=NEWPATH+name+'.rigid_model_v2'
    target=O/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SRC/source,target);files.append(dest);geometry.text=dest
    geometry_sources[dest]={'source':str(SRC/source),'sha256':sha(target)}
    for e in tree.findall('.//material'):e.text=private_material(e.text.strip())
    result=NEWPATH+name+'.wsmodel';save_xml(tree,result);return result
body=private_model('emp_karl_franz/emp_karl_franz',KEY+'_body')
sword=private_model('emp_props/emp_general_sword_1h_01',KEY+'_sword')
shield=private_model('emp_props/emp_general_shield_01',KEY+'_shield')
vmd=ET.Element('VARIANT_MESH')
for name,attach,model in [('body',None,body),('weapon_1','be_prop_0',None),('weapon_2','be_prop_1',sword),('shield','be_prop_2',shield),('weapon_3','be_prop_3',None),('weapon_4','be_prop_4',None),('weapon_5','be_prop_5',None)]:
    slot=ET.SubElement(vmd,'SLOT',{'name':name,**({'attach_point':attach} if attach else {})})
    if model:
        vm=ET.SubElement(slot,'VARIANT_MESH',{'model':model})
        meta=ET.SubElement(vm,'META_DATA');meta.text='audio_armour_type:heavy_plate' if name=='body' else 'audio_melee_weapon_type:sword' if name=='weapon_2' else 'audio_shield_type:metal'
save_xml(ET.ElementTree(vmd),'variantmeshes/variantmeshdefinitions/'+KEY+'.variantmeshdefinition')
main=clone('main_units','unit',DONOR,unit=KEY,land_unit=KEY,in_encyclopedia='false',campaign_cap='0',multiplayer_cap='1',multiplayer_qb_cap='1')
land=clone('land_units','key',DONOR,key=KEY,historical_description_text=KEY,short_description_text=KEY)
assert land['man_animation']=='hu1_empire_sword_and_shield'
variant=one('unit_variants','unit',DONOR)
write('unit_variants',[dict(variant,unit=KEY,name=KEY,variant=KEY)])
clone('variants','variant_name',variant['variant'],variant_name=KEY,variant_filename=KEY)
permission=one('units_custom_battle_permissions','unit',DONOR)
uniform=KEY+'_uniform';portrait=permission['general_portrait']
clone('agent_uniforms','uniform_name',permission['general_uniform'],uniform_name=uniform,filename=KEY,battle_filename=KEY,campaign_porthole_filename=KEY)
write('units_custom_battle_permissions',[dict(permission,unit=KEY,general_uniform=uniform,set_piece_character=KEY,campaign_exclusive='false')])
character=one('battle_set_piece_armies_characters','character_name',DONOR)
art=one('campaign_character_arts','id',character['character_model']);artset=KEY+'_art';artid='1800412600'
assert not any(r['id']==artid for r in read('campaign_character_arts')[1])
clone('campaign_character_art_sets','art_set_id',art['art_set_id'],art_set_id=artset,agent_subtype=KEY)
clone('campaign_character_arts','id',character['character_model'],id=artid,art_set_id=artset,uniform=uniform)
clone('agent_subtypes','key',character['agent_subtype'],key=KEY,auto_generate='false',associated_unit_override=KEY,cap='1',contributes_to_agent_cap='false',can_be_loaned='false',recruitable='false',saving_settings='cannot_be_loaded_in_campaign')
firstid='1800412610';lastid='1800412611'
assert not any(r['id'] in [firstid,lastid] for r in read('names')[1])
first=one('names','id',character['forename']);last=one('names','id',character['surname'])
write('names',[dict(first,id=firstid,frequency='0'),dict(last,id=lastid,frequency='0')])
write('battle_set_piece_armies_characters',[dict(character,character_name=KEY,unit_type=KEY,agent_subtype=KEY,character_model=artid,forename=firstid,surname=lastid,character_level='1')])
write('units_to_groupings_military_permissions',[dict(r,unit=KEY) for r in read('units_to_groupings_military_permissions')[1] if r['unit']==DONOR and r['military_group']=='wh_main_group_empire'])
write('unit_description_historical_texts',[{'key':KEY}]);write('unit_description_short_texts',[{'key':KEY}])
loc='text/db/'+KEY+'.loc';p=O/(loc+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
texts={f'units_land_units_onscreen_name_{KEY}':'Heinrich von Adlerhorst (Test)',f'land_units_onscreen_name_{KEY}':'Heinrich von Adlerhorst (Test)',f'unit_description_short_texts_text_{KEY}':'Armoured Sword and Shield Lord',f'unit_description_historical_texts_text_{KEY}':'Local custom battle test: Karl Franz Reskin - MM body, Empire General skeleton, sword and shield. Temporary General statistics.',f'agent_subtypes_onscreen_name_{KEY}':'Heinrich von Adlerhorst',f'names_name_{firstid}':'Heinrich',f'names_name_{lastid}':'von Adlerhorst',f'unit_variants_name_{KEY}':'Heinrich von Adlerhorst (Test)'}
with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+loc,'','']]+[[k,v,'true'] for k,v in texts.items()])
files.append(loc)
assert permission['faction']=='wh_main_emp_empire' and permission['general_unit']=='true'
assert len(table_rows['units_to_groupings_military_permissions'])==1
assert not PACK.exists(),'Version the candidate instead of replacing it'
run([CLI,'-g','warhammer_3','pack','create','-p',PACK])
# Add all DB/loc rows with schema conversion, then all graphics byte-for-byte.
for path in [f for f in files if f.startswith(('db/','text/'))]:
    run([CLI,'-g','warhammer_3','pack','add','-p',PACK,'-t',SCHEMA,'-f',str(O/(path+'.tsv'))+';'+path])
graphics=[f for f in files if not f.startswith(('db/','text/'))]
for i in range(0,len(graphics),35):
    run([CLI,'-g','warhammer_3','pack','add','-p',PACK,'-f']+[str(O/f)+';'+f for f in graphics[i:i+35]])
CHECK=R/'roundtrip';CHECK.mkdir(exist_ok=True)
run([CLI,'-g','warhammer_3','pack','extract','-p',PACK,'-t',SCHEMA,'-F','/;'+str(CHECK)])
for path in graphics:assert sha(O/path)==sha(CHECK/path),path
for path in [f for f in files if f.startswith(('db/','text/'))]:
    def rows(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))[2:]
    assert rows(O/(path+'.tsv'))==rows(CHECK/(path+'.tsv')),path
# Resolve every private graphics reference against the pack itself.
for path in graphics:
    if path.endswith(('.wsmodel','.material','.variantmeshdefinition')):
        for e in ET.parse(O/path).iter():
            refs=[e.text or '']+list(e.attrib.values())
            for ref in refs:
                s=ref.strip().replace('\\','/').lower()
                if s.startswith(NEWPATH) or s=='variantmeshes/variantmeshdefinitions/'+KEY+'.variantmeshdefinition':assert s in files,(path,s)
with (R/'diagnostics.txt').open('w',encoding='utf8') as out:
    subprocess.run([CLI,'-g','warhammer_3','pack','diagnose','-g',str(GAME),'-P',r'D:\Warhammer3_Modding\moon_cathay\reference\local\wh3-diagnostics.pak2','-s',SCHEMA,'-p',str(PACK)],check=True,stdout=out,stderr=subprocess.STDOUT)
report={'status':'roundtrip_and_asset_graph_passed','pack':str(PACK),'sha256':sha(PACK),'unit':KEY,'faction':permission['faction'],'name':texts[f'units_land_units_onscreen_name_{KEY}'],'donor':DONOR,'animation':land['man_animation'],'skeleton':'humanoid01','new_db_tables':len(table_rows),'payloads':files,'graphics_count':len(graphics),'texture_count':len(texture_map),'material_count':len(material_map),'source_geometry':geometry_sources,'rows':table_rows,'campaign_recruitment':False,'deployed':False,'runtime_verified':False}
(R/'pack_validation.json').write_text(json.dumps(report,indent=2))
print('PACK_BUILT',str(PACK),len(files),'payloads',flush=True)

