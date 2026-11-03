"""Add a Cathay Custom Battle Hero entry and spell preset for Da Lien animation tests."""
import ast,csv,json,shutil,hashlib,subprocess,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
REF=R/'reference/local/lord-vanilla/db';O=R/'build/huyen-ve-v21-da-lien-custom-battle';O.mkdir(parents=True,exist_ok=True)
BASE=R/'build/huyen-ve-v20-da-lien-visual-test/mc_huyen_ve_v20_da_lien_visual_test.pack'
PACK=O/'mc_huyen_ve_v21_da_lien_custom_battle.pack';UNIT='mc_da_lien_human';DONOR='wh3_main_cth_cha_alchemist_0';files=[]
def read(table):
    with (REF/(table+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t'))
    return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
def write(table,rows):
    (header,meta),_=read(table);internal='db/'+table+'_tables/mc_da_lien_custom_battle'
    assert all(set(r)<=set(header) for r in rows),table
    meta[0]=';'.join(meta[0].split(';')[:2]+[internal]);p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([header,meta]+[[r.get(k,'') for k in header] for r in rows])
    files.append(internal)
portrait='ui/portraits/portholes/no_culture/mc_da_lien_0.png'
permission=next(r for r in read('units_custom_battle_permissions')[1] if r['unit']==DONOR and r['faction']=='wh3_main_cth_cathay_mp')
write('units_custom_battle_permissions',[dict(permission,unit=UNIT,set_piece_character=UNIT,
    general_portrait=portrait,general_uniform='mc_da_lien_uniform')])
character=next(r for r in read('battle_set_piece_armies_characters')[1] if r['character_name']==DONOR)
write('battle_set_piece_armies_characters',[dict(character,character_name=UNIT,unit_type=UNIT,
    agent_subtype='mc_da_lien',character_model='1800312600',portrait=portrait,
    forename='1800312610',surname='1800312611',skillset='mc_da_lien_cb_skills',character_level='40')])
write('battle_set_piece_armies_characters_skillsets',[{'key':'mc_da_lien_cb_skills'}])
node_keys={r['item'] for r in read('character_skill_node_set_items')[1] if r['set']=='wh3_main_skill_node_set_cth_alchemist'}
skills=[r['character_skill_key'] for r in read('character_skill_nodes')[1] if r['key'] in node_keys and '_alchemist_magic_' in r['key']]
assert len(skills)==12,skills
assert any('dummy_searing_doom' in s for s in skills) and any('glittering_robe' in s for s in skills)
write('battle_set_piece_armies_characters_skillsets_skills',[
    {'skill':s,'skillset_key':'mc_da_lien_cb_skills','sort_order':str(i)} for i,s in enumerate(skills)])
names=read('names')[1];assert not any(r['id'] in ('1800312610','1800312611') for r in names)
first=next(r for r in names if r['id']==character['forename']);last=next(r for r in names if r['id']==character['surname'])
write('names',[dict(first,id='1800312610',gender='f',frequency='0'),dict(last,id='1800312611',frequency='0')])
groups=[dict(r,unit=UNIT) for r in read('units_to_groupings_military_permissions')[1] if r['unit']==DONOR and r['military_group']=='wh3_main_cth']
assert len(groups)==1;write('units_to_groupings_military_permissions',groups)
internal='text/db/mc_da_lien_custom_battle.loc';p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+internal,'',''],
        ['names_name_1800312610','Da Lien','true'],['names_name_1800312611','','true']])
files.append(internal)
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
assert not PACK.exists(),'Do not overwrite an existing candidate'
shutil.copy2(BASE,PACK)
for internal in files:run([C['rpfm'],'-g','warhammer_3','pack','add','-p',PACK,'-t',C['schema'],'-f',str(O/(internal+'.tsv'))+';'+internal])
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack>','exec'));before=unpack(BASE);after=unpack(PACK)
assert not(set(before)&set(files)) and set(after)==set(before)|set(files)
assert all(after[p]==v for p,v in before.items()),'Pre-existing campaign/model payload changed'
check=R/'reference/local/da-lien-v21-check';check.mkdir(exist_ok=True)
run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)])
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t'))[2:]
for internal in files:assert rows(O/(internal+'.tsv'))==rows(check/(internal+'.tsv')),internal
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-v20-da-lien-visual-test/diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');blocking=[];metadata=[]
for path,items in new.items():
    if old.get(path)==items:continue
    for row in items:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in row['cells_affected']):metadata.append({'path':path,'report':row})
        else:blocking.append({'path':path,'report':row})
(O/'diagnostics-review.json').write_text(json.dumps({'metadata':metadata,'blocking':blocking},indent=2))
assert not blocking,blocking
assert permission['general_unit']=='false' and character['agent_type']=='engineer'
v={'status':'static_checks_passed','pack':str(PACK),'sha256':hashlib.sha256(PACK.read_bytes()).hexdigest(),
 'base':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'new_payloads':len(files),'files':files,
 'existing_payloads_unchanged':True,'new_blocking_diagnostics':0,'new_schema_metadata_warnings':metadata,
 'faction':'wh3_main_cth_cathay_mp','unit':UNIT,'general_unit':False,'agent_type':'engineer',
 'custom_battle_skills':skills,'temporary_lore':'Metal; native Alchemist base spells for casting-animation tests',
 'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
