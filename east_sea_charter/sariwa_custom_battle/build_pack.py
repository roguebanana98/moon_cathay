import csv,json,subprocess,hashlib,shutil,copy,sys,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'payload';O.mkdir(exist_ok=True)
REF=R/'reference/db';SKREF=R.parent/'skill_tree_design/vanilla_reference/db'
MODELREF=R.parent/'endo_damsel_preview/reference'
PREV=R.parent/'heinrich_skill_tree/edh_heinrich_v3_skill_tree.pack'
PACK=R/'edh_heinrich_sariwa_v4.pack'
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
SCHEMA=r'D:\Warhammer3_Modding\tooling\rpfm-schema-wh3\schema_wh3.ron'
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III')
KEY='edh_sariwa';DONOR='wh_main_brt_cha_damsel_0';OLDSET='wh_main_skill_node_set_brt_damsel';SET=KEY+'_skill_node_set'
NEW='variantmeshes/wh_variantmodels/edh/sariwa/'
files=[];tables={};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,**kw):return subprocess.run([str(a) for a in [CLI,'-g','warhammer_3']+args],check=True,**kw)
def read(t):
    p=REF/(t+'_tables/data__.tsv')
    if not p.exists():p=SKREF/(t+'_tables/data__.tsv')
    with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return rows[:2],[dict(zip(rows[0],r)) for r in rows[2:]]
def one(t,k,v):
    rs=[r for r in read(t)[1] if r[k]==v];assert len(rs)==1,(t,k,v,len(rs));return rs[0]
def write(t,rs):
    if not rs:return
    (header,meta),_=read(t);path='db/'+t+'_tables/'+KEY
    assert all(set(r)==set(header) for r in rs),t
    meta[0]=';'.join(meta[0].split(';')[:2]+[path]);p=O/(path+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([header,meta]+[[r[k] for k in header] for r in rs])
    files.append(path);tables[t]=rs
def clone(t,k,v,**changes):r=dict(one(t,k,v),**changes);write(t,[r]);return r
def save(tree,path):
    p=O/path;p.parent.mkdir(parents=True,exist_ok=True);tree.write(p,encoding='utf8',xml_declaration=False);files.append(path)
def asset(src,dest):
    target=O/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target);files.append(dest);return dest

if PACK.exists():
    prior=json.loads((R/'pack_validation.json').read_text(encoding='utf8'))
    assert '--rebuild-candidate' in sys.argv and not prior.get('deployed') and sha(PACK)==prior['sha256'],'Version released packs instead of replacing them'
rig_report=json.loads((R/'rig_export_report.json').read_text());assert rig_report['status']=='rig_animation_and_prop_exports_passed'
assert len(rig_report['native_clips_tested'])==11
materials={};textures={};models={}
for f in (R/'export/tex').glob('*.dds'):asset(f,NEW+'tex/'+f.name)
asset(R.parent/'sariwa_damsel02/textures/edh_sariwa_body_base_colour_v1.dds',NEW+'tex/edh_sariwa_body_base_colour_v1.dds')
def material(path,role):
    path=path.strip().replace('\\','/').lower();cache=(path,role)
    if cache in materials:return materials[cache]
    dest=NEW+'materials/'+role+'_'+Path(path).name;materials[cache]=dest;tree=ET.parse(MODELREF/path)
    for tex in tree.findall('.//texture'):
        slot=tex.findtext('slot');source=tex.find('source')
        if source is None:continue
        old=source.text.strip().replace('\\','/').lower()
        if slot=='t_xml_mask':source.text=NEW+'tex/edh_sariwa_'+('jade_mask' if role=='naga_jade' else 'body_mask')+'.dds'
        elif role in ('naga','naga_jade') and slot in ('t_xml_base_colour','t_xml_normal','t_xml_material_map'):
            name={'t_xml_base_colour':'edh_sariwa_naga_base_colour.dds','t_xml_normal':'edh_sariwa_normal.dds','t_xml_material_map':'edh_sariwa_naga_material_map.dds'}[slot];source.text=NEW+'tex/'+name
        elif role=='body' and slot=='t_xml_base_colour':source.text=NEW+'tex/edh_sariwa_body_base_colour_v1.dds'
        elif role=='staff' and slot=='t_xml_base_colour':source.text=NEW+'tex/edh_sariwa_staff_base_colour.dds'
        elif (MODELREF/old).exists():
            if old not in textures:textures[old]=asset(MODELREF/old,NEW+'tex/'+hashlib.sha256(old.encode()).hexdigest()[:8]+'_'+Path(old).name)
            source.text=textures[old]
    save(tree,dest);return dest
def model(path,role,exported=None):
    path=path.strip().replace('\\','/').lower();tree=ET.parse(MODELREF/path)
    geometry=tree.find('geometry');native=geometry.text.strip().replace('\\','/').lower();dest=NEW+KEY+'_'+role+'.rigid_model_v2'
    asset(exported or MODELREF/native,dest);geometry.text=dest
    for e in tree.findall('.//material'):e.text=material(e.text,role)
    ws=NEW+KEY+'_'+role+'.wsmodel';save(tree,ws);models[role]=ws;return ws
base='variantmeshes/wh_variantmodels/'
head=model(base+'hu1b/brt/endo_damsel/endo_damsel_head_04.wsmodel','head')
body=model(base+'hu1b/brt/endo_damsel/endo_damsel_body_02.wsmodel','body')
sword=model(base+'hu1/brt/brt_props/brt_lords_sword_1h_01.wsmodel','sword')
staff_source=base+'hu1/brt/brt_props/brt_damsel_staff_1h_02.wsmodel'
staff=model(staff_source,'staff',R/'export/edh_sariwa_staff.rigid_model_v2')
naga=model(staff_source,'naga',R/'export/edh_sariwa_naga.rigid_model_v2')
jade=model(staff_source,'naga_jade',R/'export/edh_sariwa_naga_jade.rigid_model_v2')
vmd=ET.Element('VARIANT_MESH')
for name,attach,paths in [('head',None,[head]),('body',None,[body]),('weapon_1','be_prop_0',[]),('weapon_2','be_prop_1',[sword]),('shield','be_prop_2',[]),('weapon_3','be_prop_3',[]),('weapon_4','be_prop_4',[]),('weapon_5','be_prop_5',[staff,naga,jade])]:
    slot=ET.SubElement(vmd,'SLOT',{'name':name,**({'attach_point':attach} if attach else {})})
    # Sibling VARIANT_MESH entries are random alternatives. Nest compulsory
    # crown slots inside the shaft model to inherit prop docking/visibility.
    parent_model=None
    for i,path in enumerate(paths):
        parent=slot if i==0 else ET.SubElement(parent_model,'SLOT',{'name':name+'_component_'+str(i)})
        part=ET.SubElement(parent,'VARIANT_MESH',{'model':path})
        if i==0:parent_model=part
        if name=='body':ET.SubElement(part,'META_DATA').text='audio_armour_type:body'
        if name=='weapon_2':ET.SubElement(part,'META_DATA').text='audio_melee_weapon_type:sword'
        if name=='weapon_5' and i==0:ET.SubElement(part,'META_DATA').text='audio_melee_weapon_type:staff'
save(ET.ElementTree(vmd),'variantmeshes/variantmeshdefinitions/'+KEY+'.variantmeshdefinition')

# Unit and custom battle identity: an on-foot hero for Empire, separate from Heinrich.
main=clone('main_units','unit',DONOR,unit=KEY,land_unit=KEY,campaign_cap='0',multiplayer_cap='1',multiplayer_qb_cap='1',in_encyclopedia='false')
land=clone('land_units','key',DONOR,key=KEY,historical_description_text=KEY,short_description_text=KEY)
assert land['man_animation']=='hu1b_bretonnian_staff_and_sword' and land['is_male']=='false'
variant=one('unit_variants','unit',DONOR);write('unit_variants',[dict(variant,unit=KEY,name=KEY,variant=KEY,unit_card=KEY)])
clone('variants','variant_name',variant['variant'],variant_name=KEY,variant_filename=KEY)
permission=one('units_custom_battle_permissions','unit',DONOR)
uniform=KEY+'_uniform';portrait='ui/portraits/portholes/no_culture/'+KEY+'_0.png'
clone('agent_uniforms','uniform_name',permission['general_uniform'],uniform_name=uniform,filename=KEY,battle_filename=KEY,campaign_porthole_filename=KEY)
write('units_custom_battle_permissions',[dict(permission,unit=KEY,faction='wh_main_emp_empire',general_uniform=uniform,general_portrait=portrait,set_piece_character=KEY,campaign_exclusive='false')])
character=one('battle_set_piece_armies_characters','character_name',DONOR);art=one('campaign_character_arts','id',character['character_model'])
artset=KEY+'_art';artid='1800412700'
assert not any(r['id']==artid for r in read('campaign_character_arts')[1])
clone('campaign_character_art_sets','art_set_id',art['art_set_id'],art_set_id=artset,agent_subtype=KEY)
clone('campaign_character_arts','id',art['id'],id=artid,art_set_id=artset,uniform=uniform)
clone('agent_subtypes','key',character['agent_subtype'],key=KEY,auto_generate='false',associated_unit_override=KEY,cap='1',contributes_to_agent_cap='false',can_be_loaned='false',recruitable='false',saving_settings='cannot_be_loaded_in_campaign')
firstid='1800412710';lastid='1800412711';assert not any(r['id'] in (firstid,lastid) for r in read('names')[1])
write('names',[dict(one('names','id',character['forename']),id=firstid,frequency='0'),dict(one('names','id',character['surname']),id=lastid,frequency='0')])
write('battle_set_piece_armies_characters',[dict(character,character_name=KEY,unit_type=KEY,agent_subtype=KEY,character_model=artid,forename=firstid,surname=lastid,portrait=portrait,skillset=SET,magic_lore='wh_main_lore_heavens',character_level='1')])
group=next(r for r in read('units_to_groupings_military_permissions')[1] if r['unit']==DONOR)
write('units_to_groupings_military_permissions',[dict(group,unit=KEY,military_group='wh_main_group_empire')])
write('unit_description_historical_texts',[{'key':KEY}]);write('unit_description_short_texts',[{'key':KEY}])
native_abilities=[dict(r,land_unit=KEY) for r in read('land_units_to_unit_abilites_junctions')[1] if r['land_unit']==DONOR]
native_abilities=[r for r in native_abilities if r['ability']!='wh_main_character_abilities_arcane_conduit']
native_abilities.append({'ability':'wh2_main_character_passive_grand_arcane_conduit','land_unit':KEY,'culture':'*'})
write('land_units_to_unit_abilites_junctions',native_abilities)
write('special_ability_groups_to_units_junctions',[dict(r,unit=KEY) for r in read('special_ability_groups_to_units_junctions')[1] if r['unit']==DONOR])
_,setrows=read('unit_set_to_unit_junctions')
write('unit_set_to_unit_junctions',[dict(r,unit=KEY) for r in setrows if r.get('unit')==DONOR])

# Approved 21-skill tree, private names/IDs, native effects and prerequisite graph.
approved=json.loads((R.parent/'skill_tree_design/skills-vanilla-v2.json').read_text(encoding='utf8'))['s'];assert len(approved)==21
skillmap={s['key']:KEY+'_skill_s'+str(i).zfill(2) for i,s in enumerate(approved,1)}
arcane='wh_main_skill_all_magic_all_11_arcane_conduit';greater='wh2_dlc14_skilll_all_magic_all_greater_arcane_conduit'
source_skills={r['key']:r for r in read('character_skills')[1]};source_nodes={r['key']:r for r in read('character_skill_nodes')[1]}
nodemap={s['node']['key']:KEY+'_node_s'+str(i).zfill(2) for i,s in enumerate(approved,1)}
newskills=[dict(source_skills[s['key']],key=skillmap[s['key']],localised_name=s['name']) for s in approved]
newnodes=[dict(source_nodes[s['node']['key']],key=nodemap[s['node']['key']],character_skill_key=skillmap[s['key']]) for s in approved]
write('character_skills',newskills);write('character_skill_nodes',newnodes)
clone('character_skill_node_sets','key',OLDSET,key=SET,agent_subtype_key=KEY)
excluded={'wh_main_skill_brt_wizard_unique_damsel_warhorse','wh_dlc07_skill_brt_damsel_heavens_unique_unicorn'}
setitems=[dict(r,set=SET,item=nodemap.get(r['item'],r['item'])) for r in read('character_skill_node_set_items')[1] if r['set']==OLDSET and source_nodes[r['item']]['character_skill_key'] not in excluded]
write('character_skill_node_set_items',setitems)
links=[dict(r,child_key=nodemap[r['child_key']],parent_key=nodemap.get(r['parent_key'],r['parent_key'])) for r in read('character_skill_node_links')[1] if r['child_key'] in nodemap]
write('character_skill_node_links',links)
blockmap=dict(skillmap);blockmap[arcane]=skillmap[greater]
write('character_skill_nodes_skill_locks',[dict(r,character_skill_node=nodemap[r['character_skill_node']],character_skill=blockmap.get(r['character_skill'],r['character_skill'])) for r in read('character_skill_nodes_skill_locks')[1] if r['character_skill_node'] in nodemap])
for t,col in [('character_skill_level_to_effects_junctions','character_skill_key'),('character_skill_utilization_hints_junctions','key'),('character_skill_to_unit_list_display_junctions','character_skill')]:
    write(t,[dict(r,**{col:skillmap[r[col]]}) for r in read(t)[1] if r[col] in skillmap])
details=[]
for s in approved:
    old=arcane if s['key']==greater else s['key']
    details.extend(dict(r,skill_key=skillmap[s['key']]) for r in read('character_skill_level_details')[1] if r['skill_key']==old)
write('character_skill_level_details',details)
clone('battle_set_piece_armies_characters_skillsets','key',OLDSET,key=SET)
write('battle_set_piece_armies_characters_skillsets_skills',[dict(r,skillset_key=SET,skill=blockmap.get(r['skill'],r['skill'])) for r in read('battle_set_piece_armies_characters_skillsets_skills')[1] if r['skillset_key']==OLDSET])

texts={f'units_land_units_onscreen_name_{KEY}':'Sariwa',f'land_units_onscreen_name_{KEY}':'Sariwa',f'agent_subtypes_onscreen_name_{KEY}':'Sariwa',f'unit_variants_name_{KEY}':'Sariwa',f'names_name_{firstid}':'Sariwa',f'names_name_{lastid}':'',f'unit_description_short_texts_text_{KEY}':'Human Khuresh Scholar-Priestess (Heavens)',f'unit_description_historical_texts_text_{KEY}':'Sariwa, keeper of the Naga oath. Endo Damsel 02 with ivory and jade ceremonial textiles, a three-headed bronze Naga staff, native Damsel sword-and-staff animations, the Lore of Heavens and Greater Arcane Conduit.'}
for s in approved:
    private=skillmap[s['key']];texts['character_skills_localised_name_'+private]=s['name'];texts['character_skills_localised_description_'+private]='{{tr:character_skills_localised_description_'+s['key']+'}}'
loc='text/db/'+KEY+'.loc';p=O/(loc+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([['key','text','tooltip'],['#Loc;1;'+loc,'','']]+[[k,v,'true'] for k,v in texts.items()])
files.append(loc)
# Private portrait settings prevent the fallback vanilla card.
for folder in ['units','portholes']:
    source=json.loads((R.parent/'heinrich_custom_battle/reference'/(folder+'_portraits.json')).read_text())
    donor=next(e for e in source['entries'] if e['id']==art['art_set_id']);entry=copy.deepcopy(donor);entry['id']=artset
    portraitpath='ui/portraits/'+folder+'/no_culture/'+KEY+'_0.png';asset(R/'sariwa_portrait.png',portraitpath)
    variant=entry['variants'][0];variant.update(filename=KEY,file_diffuse=portraitpath,file_mask_1='',file_mask_2='',file_mask_3='',faction_leader=False);entry['variants']=[variant];source['entries']=[entry]
    jp=R/('portrait_'+folder+'.json');jp.write_text(json.dumps(source,indent=2))
    binary='ui/portraits/'+folder+'/portrait_settings__'+KEY+'.bin';bp=O/binary;bp.parent.mkdir(parents=True,exist_ok=True)
    run(['portrait-settings','from-json','-j',jp,'-b',bp],stdout=subprocess.DEVNULL);files.append(binary)
for path in ['ui/units/icons/'+KEY+'.png','ui/units/minspec_portholes/'+KEY+'.png']:asset(R/'sariwa_portrait.png',path)

# Pre-build graph and mechanical fidelity checks.
active={r['item'] for r in setitems if r['mod_disabled']=='false'}
assert all(r['key'] in active for r in newnodes)
assert all(r['parent_key'] in active and r['child_key'] in active for r in links)
assert len({(r['indent'],r['tier']) for r in newnodes})==len(newnodes)
for s in approved:
    expected=[r for r in read('character_skill_level_to_effects_junctions')[1] if r['character_skill_key']==s['key']]
    actual=[dict(r,character_skill_key=s['key']) for r in tables['character_skill_level_to_effects_junctions'] if r['character_skill_key']==skillmap[s['key']]]
    assert actual==expected,s['key']
assert all(r['ability']!='wh_main_character_abilities_arcane_conduit' for r in native_abilities)
assert permission['general_unit']=='false' and main['caste']=='hero'
files=list(dict.fromkeys(files));graphics=[f for f in files if not f.startswith(('db/','text/'))]
for path in graphics:
    if path.endswith(('.wsmodel','.material','.variantmeshdefinition')):
        for e in ET.parse(O/path).iter():
            for value in [e.text or '']+list(e.attrib.values()):
                ref=value.strip().replace('\\','/').lower()
                if ref.startswith(NEW):assert ref in files,(path,ref)
shutil.copy2(PREV,PACK)
for path in [f for f in files if f.startswith(('db/','text/'))]:run(['pack','add','-p',PACK,'-t',SCHEMA,'-f',str(O/(path+'.tsv'))+';'+path],stdout=subprocess.DEVNULL)
for i in range(0,len(graphics),35):run(['pack','add','-p',PACK,'-f']+[str(O/p)+';'+p for p in graphics[i:i+35]],stdout=subprocess.DEVNULL)
C=R/'roundtrip';run(['pack','extract','-p',PACK,'-t',SCHEMA,'-F','/;'+str(C)],stdout=subprocess.DEVNULL)
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))[2:]
for path in files:
    if path.startswith(('db/','text/')):assert rows(O/(path+'.tsv'))==rows(C/(path+'.tsv')),path
    else:assert sha(O/path)==sha(C/path),path
for source in (R.parent/'heinrich_skill_tree/roundtrip').rglob('*'):
    if not source.is_file() or source.name.endswith(('rpfm_reserved.md','rpfm_reserved.json')):continue
    rel=source.relative_to(R.parent/'heinrich_skill_tree/roundtrip');target=C/rel
    if rel.as_posix().startswith(('db/','text/')):assert rows(source)==rows(target),str(rel)
    else:assert sha(source)==sha(target),str(rel)
report={'status':'roundtrip_passed_pending_diagnostics','pack':str(PACK),'sha256':sha(PACK),'previous_pack':str(PREV),'unit':KEY,'faction':'wh_main_emp_empire','subtype':KEY,'skill_set':SET,'skill_count':21,'donor':DONOR,'native_animation_table':land['man_animation'],'payloads':files,'rows':tables,'source_to_private_skill':skillmap,'model_assets':models,'skeleton':'humanoid01b','native_clips_tested':11,'base_heinrich_payloads_preserved':True,'deployed':False,'runtime_verified':False}
(R/'pack_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
with (R/'diagnostics.txt').open('w',encoding='utf8') as f:run(['pack','diagnose','-g',GAME,'-P',R.parent/'heinrich_custom_battle/wh3-current.pak2','-s',SCHEMA,'-p',PACK],stdout=f,stderr=subprocess.STDOUT)
print('SARIWA_PACK_READY',str(PACK),len(files),'new payloads',flush=True)
