"""Build private v20 Hero appearance test over v19, without changing prior payloads."""
import ast, csv, json, hashlib, shutil, subprocess, struct
import xml.etree.ElementTree as E
from pathlib import Path

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
REF=R/'reference/local/lord-vanilla/db'
D=R/'reference/local/beautiful-neferata'
O=R/'build/huyen-ve-v20-da-lien-visual-test';O.mkdir(parents=True,exist_ok=True)
BASE=R/'build/huyen-ve-v19-moonlit-command/mc_huyen_ve_v19_moonlit_command.pack'
PACK=O/'mc_huyen_ve_v20_da_lien_visual_test.pack'
NEW='mc_da_lien';UNIT=NEW+'_human';ART=NEW+'_art';FACTION='cr_cth_agents_of_the_moon'
DONOR='wh3_main_cth_alchemist';DU='wh3_main_cth_cha_alchemist_0'
files=[]
def run(args):
    return subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
def read(table):
    with (REF/(table+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return rows[:2],[dict(zip(rows[0],r)) for r in rows[2:]]
def write(table, rows):
    (header,meta),_=read(table);internal='db/'+table+'_tables/'+NEW
    assert all(set(row)<=set(header) for row in rows),table
    meta[0]=';'.join(meta[0].split(';')[:2]+[internal])
    p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows([header,meta]+[[r.get(k,'') for k in header] for r in rows])
    files.append(internal)
def one(table, field, value):
    matches=[r for r in read(table)[1] if r[field]==value]
    assert len(matches)==1,(table,value,len(matches))
    return matches[0]
def clone(table,field,value,**changes):
    row=dict(one(table,field,value),**changes);write(table,[row]);return row

# Human caster Hero framework; no Vampire/Lord traits or skills are imported.
clone('agent_subtypes','key',DONOR,key=NEW,auto_generate='false',cap='1',
      associated_unit_override=UNIT,has_female_name='true',contributes_to_agent_cap='false',
      can_be_loaned='false',recruitable='false',saving_settings='cannot_be_loaded_in_campaign')
clone('main_units','unit',DU,unit=UNIT,land_unit=UNIT,campaign_cap='1',
      porthole_camera='wh3_dlc29_vmp_neferata')
neferata=one('land_units','key','wh3_dlc29_vmp_cha_neferata')
land=clone('land_units','key',DU,key=UNIT,man_animation=neferata['man_animation'],
           man_entity=neferata['man_entity'],primary_melee_weapon=neferata['primary_melee_weapon'],
           historical_description_text=UNIT,short_description_text=UNIT,is_male='false')
assert land['attribute_group']==DU
write('unit_description_historical_texts',[{'key':UNIT}])
write('unit_description_short_texts',[{'key':UNIT}])
unit_variant=next(r for r in read('unit_variants')[1] if r['unit']==DU)
write('unit_variants',[dict(unit_variant,faction='',unit=UNIT,name=UNIT,variant=NEW,unit_card=NEW)])
clone('variants','variant_name','wh3_dlc29_vmp_neferata',variant_name=NEW,variant_filename=NEW)
clone('agent_uniforms','uniform_name','wh3_dlc29_uniform_vmp_neferata',
      uniform_name=NEW+'_uniform',filename=NEW,battle_filename=NEW,campaign_porthole_filename=NEW)
clone('campaign_character_art_sets','art_set_id','wh3_main_art_set_cth_alchemist_01',
      art_set_id=ART,agent_subtype=NEW,faction=FACTION,is_male='false')
art=dict(one('campaign_character_arts','art_set_id','wh3_main_art_set_cth_alchemist_01'),
         id='1800312600',art_set_id=ART,uniform=NEW+'_uniform',
         land_animation='cam_hu1ba_dlc29_vmp_neferata_staff_and_sword')
write('campaign_character_arts',[art])
write('faction_agent_permitted_subtypes',[{'agent':'engineer','faction':FACTION,'subtype':NEW,'mod_disabled':'false'}])
skillset=clone('character_skill_node_sets','key','wh3_main_skill_node_set_cth_alchemist',
               key=NEW+'_skills',agent_subtype_key=NEW,faction_key=FACTION)
nodes={r['key']:r for r in read('character_skill_nodes')[1]}
skills={r['key']:r for r in read('character_skills')[1]}
items=[]
for row in read('character_skill_node_set_items')[1]:
    if row['set']!='wh3_main_skill_node_set_cth_alchemist':continue
    node=nodes[row['item']];skill=node['character_skill_key']
    if any(x in skill.lower() for x in ('mount','horse','immortality')):continue
    items.append(dict(row,set=NEW+'_skills'))
write('character_skill_node_set_items',items)
write('special_ability_groups_to_units_junctions',[dict(r,unit=UNIT) for r in read('special_ability_groups_to_units_junctions')[1] if r['unit']==DU])
write('land_units_to_unit_abilites_junctions',[dict(r,land_unit=UNIT) for r in read('land_units_to_unit_abilites_junctions')[1] if r['land_unit']==DU])
assert skillset['agent_key']=='engineer'

# Re-key private appearance resources so neither native Neferata nor her reskin is overridden.
prefix='variantmeshes/wh_variantmodels/hu1ba/vmp/'
target='variantmeshes/wh_variantmodels/mc_da_lien/'
source_files={p.relative_to(D).as_posix().lower():p for p in (D/'variantmeshes/wh_variantmodels/hu1ba/vmp').rglob('*') if p.is_file()}
for path,src in source_files.items():
    internal=target+path.removeprefix(prefix)
    dest=O/internal;dest.parent.mkdir(parents=True,exist_ok=True)
    if path.endswith(('.wsmodel','.material')):
        tree=E.parse(src)
        for node in tree.iter():
            if node.text and node.text.strip().lower().replace('\\','/').startswith(prefix):
                node.text=target+node.text.strip().lower().replace('\\','/').removeprefix(prefix)
        tree.write(dest,encoding='utf-8')
    else: shutil.copy2(src,dest)
    files.append(internal)
vmd=E.parse(D/'variantmeshes/variantmeshdefinitions/vmp_neferata.variantmeshdefinition')
for node in vmd.findall('.//VARIANT_MESH'):
    if node.get('model'):
        node.set('model',target+node.get('model').lower().replace('\\','/').removeprefix(prefix))
for node in vmd.findall('.//META_DATA'):
    if node.text and node.text.startswith('audio_entity_type:'):node.text='audio_entity_type:'+DU
internal='variantmeshes/variantmeshdefinitions/'+NEW+'.variantmeshdefinition'
p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);vmd.write(p,encoding='utf-8');files.append(internal)

# Native donor portraits from the selected mod, scoped to the new character only.
mod=Path(C['workshop'])/'3809988722/Beautiful Neferata.pack'
portrait_paths=['ui/portraits/faction_leaders/vmp_neferata_0.png',
                'ui/portraits/portholes/no_culture/vmp_neferata_0.png',
                'ui/portraits/units/no_culture/vmp_neferata_0.png']
run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',mod,'-f']+[p+';'+str(D) for p in portrait_paths])
for folder in ('units','portholes','faction_leaders'):
    sub='/no_culture' if folder!='faction_leaders' else ''
    internal='ui/portraits/'+folder+sub+'/'+NEW+'_0.png'
    p=O/internal;p.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(D/('ui/portraits/'+folder+sub+'/vmp_neferata_0.png'),p);files.append(internal)
    donor='portholes' if folder=='faction_leaders' else folder
    settings=json.loads((R/'build/huyen-ve-v17-campaign'/('portrait-donor-'+donor+'.json')).read_text())
    entry=settings['entries'][0];entry['id']=ART;variant=entry['variants'][0]
    variant.update(filename=NEW,file_diffuse=internal,faction_leader=folder=='faction_leaders')
    jp=O/('portrait-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2))
    binpath='ui/portraits/'+folder+'/portrait_settings__'+NEW+'.bin';bp=O/binpath
    run([C['rpfm'],'-g','warhammer_3','portrait-settings','from-json','-j',jp,'-b',bp]);files.append(binpath)
internal='ui/units/icons/'+NEW+'.png';p=O/internal;p.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(D/'ui/portraits/units/no_culture/vmp_neferata_0.png',p);files.append(internal)
internal='ui/units/minspec_portholes/'+UNIT+'.png';p=O/internal;p.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(D/'ui/portraits/portholes/no_culture/vmp_neferata_0.png',p);files.append(internal)
internal='text/db/'+NEW+'.loc';p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
loc=[['agent_subtypes_onscreen_name_override_'+NEW,'Legendary Hero','true'],
     ['land_units_onscreen_name_'+UNIT,'Da Lien','true'],
     ['unit_description_short_texts_text_'+UNIT,'Human Wizard - visual test','true'],
     ['unit_description_historical_texts_text_'+UNIT,'A human wizard serving the Agents of the Moon. Appearance test; final spell tree pending.','true']]
with p.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'','']]+loc)
files.append(internal)
internal='script/campaign/mod/mc_da_lien_visual_test.lua';p=O/internal;p.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(R/'src'/internal,p);files.append(internal)

# Prove the native animation lookup exists in compiled animation archives.
lookup_names={neferata['man_animation'],art['land_animation']};hits=[]
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
    b=p.read_bytes();count=struct.unpack_from('<I',b)[0];pos=4
    for _ in range(count):
        size=struct.unpack_from('<H',b,pos)[0];pos+=2;name=b[pos:pos+size].decode();pos+=size
        size=struct.unpack_from('<I',b,pos)[0];pos+=4
        if Path(name).stem in lookup_names:hits.append({'archive':str(p),'name':name,'bytes':size})
        pos+=size
    assert pos==len(b)
campaign_bin='animations/campaign/database/bin/'+art['land_animation']+'.bin'
for packname in ('anim.pack','anim2.pack','anim_3.pack'):
    archive=Path(C['game'])/'data'/packname
    names=subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(archive)],text=True,stderr=subprocess.DEVNULL).splitlines()
    if campaign_bin in names:
        hits.append({'archive':str(archive),'name':campaign_bin,'verified':'native loose campaign BIN'})
        break
assert {Path(h['name']).stem for h in hits}==lookup_names,('Missing native runtime lookup',hits)

# Validate XML graph is self-contained except existing native common textures/shaders.
for internal in files:
    if internal.endswith(('.wsmodel','.material','.variantmeshdefinition')):
        tree=E.parse(O/internal)
        refs=[x.text.strip().lower().replace('\\','/') for x in tree.iter() if x.text and x.text.strip().lower().replace('\\','/').startswith(target)]
        refs += [x.get('model').lower().replace('\\','/') for x in tree.iter() if x.get('model')]
        assert all((O/ref).is_file() for ref in refs),(internal,refs)
assert not PACK.exists(),'Protect existing test build'
shutil.copy2(BASE,PACK)
for internal in files:
    args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',PACK]
    table=internal.startswith('db/') or internal.endswith('.loc')
    if table:args+=['-t',C['schema']]
    run(args+['-f',str(O/(internal+('.tsv' if table else '')))+';'+internal])
tree=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(BASE);after=unpack(PACK)
assert not(set(before)&set(files)),'No existing entry may be replaced'
assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items()),'Existing Huyen Ve/province payload changed'
check=R/'reference/local/da-lien-v20-check';check.mkdir(exist_ok=True)
run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)])
for internal in files:
    if internal.startswith('db/') or internal.endswith('.loc'):
        def rows(p):
            with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t'))
        assert rows(O/(internal+'.tsv'))[2:]==rows(check/(internal+'.tsv'))[2:],internal
    else:assert after[internal]==(O/internal).read_bytes(),internal
report={'status':'static_checks_passed','pack':str(PACK),'sha256':hashlib.sha256(PACK.read_bytes()).hexdigest(),
 'base':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'new_payloads':len(files),'files':files,
 'existing_payloads_unchanged':True,'subtype':NEW,'agent_type':'engineer','caste':'hero','attribute_group':land['attribute_group'],
 'native_animation_lookup_verified':hits,'spell_tree':'temporary Cathay Alchemist, no mounts; final custom wizard tree pending',
 'spawn':'once near owned Long Vi on load/faction turn, no new campaign required','source_model_mod':str(mod),
 'private_reference_derived_assets':True,'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
