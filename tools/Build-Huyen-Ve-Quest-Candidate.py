"""Build a non-deployed v25 chapter-1 integration candidate over v24."""
import ast,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
N=R/'reference/local/lord-vanilla/db';O=R/'build/huyen-ve-v25-quest-candidate';O.mkdir(exist_ok=True)
BASE=R/'build/huyen-ve-v24-da-lien-moonstone/mc_huyen_ve_v24_da_lien_moonstone.pack'
PACK=O/'mc_huyen_ve_v25_quest_chapter1_candidate.pack';files=[]
S=json.loads((R/'src/campaign/huyen-ve-quests.json').read_text())
assert S['enabled_chapters']==[1]
def read_path(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],x)) for x in a[2:]]
def native(t):return read_path(N/(t+'_tables/data__.tsv'))
def write(t,rs):
    (h,m),_=native(t);m=m.copy();p='db/'+t+'_tables/mc_huyen_ve_quests';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs)
    with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
mission='mc_huyen_ve_quest_01'
title='A Seal in the Moonlight'
description='Hold Long Vi and win two ordinary campaign battles with Huyen Ve commanding a participating army. Only battles fought after this mission is issued count. Quest battles do not count. Reports from the recovered road will reveal Da Lien\'s distress signal.'
m=dict(next(x for x in native('missions')[1] if x['key']=='wh2_dlc09_books_of_nagash'))
m.update(key=mission,localised_title=title,localised_description=description,ui_image='cth/messenger',ui_icon='event_mission_neutral.png',quest_character='',event_category='Quest',set_piece_battle='',quest_mission='false',quest_mission_final='false',generate='false',can_be_manually_cancelled='false')
write('missions',[m])
icon='ui/battle ui/ability_icons/wh3_main_lore_passive_power_of_yin.png'
write('mission_issuers',[dict(issuer_key='mc_huyen_ve_moon_court',default_rounds_between='0',icon_path=icon)])
write('campaign_payload_ui_details',[dict(component='mc_huyen_ve_quest_reward_pendant',icon='ui/battle ui/ability_icons/wh_magic_item_passive_talisman.png',state='positive',sort_order='0')])
loc=[
 ['missions_localised_title_'+mission,title,'true'],
 ['missions_localised_description_'+mission,description,'true'],
 ['missions_localised_mission_completed_text_'+mission,'The pendant is recovered. The road patrols have found Da Lien\'s distress signal.','true'],
 ['mission_text_text_mc_huyen_ve_quest_01_owned','Hold Long Vi (owned). Win campaign battles with Huyen Ve: %n / 2.','true'],
 ['mission_text_text_mc_huyen_ve_quest_01_unowned','Recover and hold Long Vi. Win campaign battles with Huyen Ve: %n / 2.','true'],
 ['campaign_payload_ui_details_description_mc_huyen_ve_quest_reward_pendant','Moonshadow Jade Pendant. An existing copy is retained instead of granting a duplicate.','true'],
 ['mission_issuers_on_screen_name_mc_huyen_ve_moon_court','Agents of the Moon','true']]
p='text/db/mc_huyen_ve_quests.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)
scripts=['mc_huyen_ve_quest_state.lua','mc_huyen_ve_quest_campaign.lua','mc_huyen_ve_campaign_test_items.lua','mc_da_lien_visual_test.lua','mc_da_lien_crimson_moonstone.lua']
for name in scripts:
    p='script/campaign/mod/'+name;dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,dest);files.append(p)
assert not PACK.exists(),'Protect existing candidate'
shutil.copy2(BASE,PACK)
for p in files:
    tab=p.startswith('db/') or p.endswith('.loc');args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK)]
    if tab:args+=['-t',C['schema']]
    subprocess.run(args+['-f',str(O/(p+('.tsv' if tab else '')))+';'+p],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(BASE);after=unpack(PACK);changed=sorted(p for p in before if before[p]!=after.get(p))
assert set(changed)=={'script/campaign/mod/'+name for name in scripts[2:]}
assert set(after)==set(before)|set(files) and all(after[p]==b for p,b in before.items() if p not in changed)
check=R/'reference/local/huyen-ve-v25-check';check.mkdir(exist_ok=True)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(PACK),'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)],check=True,stdout=subprocess.DEVNULL)
for p in files:
    if p.startswith('db/') or p.endswith('.loc'):assert read_path(O/(p+'.tsv'))[1]==read_path(check/(p+'.tsv'))[1],p
    else:assert after[p]==(O/p).read_bytes()
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(BASE.parent/'diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');diff={p:rs for p,rs in new.items() if rs and old.get(p)!=rs}
metadata=[];blocking=[]
for p,rs in diff.items():
    for row in rs:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in row['cells_affected']):metadata.append(dict(path=p,report=row))
        else:blocking.append(dict(path=p,report=row))
(O/'diagnostics-review.json').write_text(json.dumps(dict(metadata=metadata,blocking=blocking),indent=2))
assert not blocking,blocking
v=dict(status='chapter1_candidate_static_checks_passed',pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),files=files,changed_payloads=changed,enabled_chapters=[1],new_blocking_diagnostics=0,new_schema_metadata_warnings=len(metadata),deployed=False,runtime_verified=False,release_blockers=['chapter 2 rescue battle not implemented or map-validated','chapters 3-6 not implemented','campaign state and reward runtime verification'])
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
