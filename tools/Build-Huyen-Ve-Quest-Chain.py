"""Build all six chapters over the tested rescue graph, without touching saves."""
import ast,csv,hashlib,json,re,shutil,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
S=json.loads((R/'src/campaign/huyen-ve-quests.json').read_text())
O=R/'build/huyen-ve-v25-quest-chain';O.mkdir(exist_ok=True)
rev=sys.argv[1] if len(sys.argv)>1 else 'r1'
assert re.fullmatch(r'r\d+',rev)
PACK=O/('mc_huyen_ve_v25_quest_chain_test_'+rev+'.pack')
BASE=R/'build/huyen-ve-v25-rescue-prototype/mc_huyen_ve_v25_rescue_prototype_v4.pack'
N=R/'reference/local/lord-vanilla/db';files=[];cache={};loc=[]
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
def native(t):
    if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def one(t,col,key):
    rs=[r for r in native(t)[1] if r[col]==key];assert len(rs)==1,(t,key);return dict(rs[0])
def write(t,rows,basename='mc_huyen_ve_quests'):
    (h,m),_=native(t);m=m.copy();p='db/'+t+'_tables/'+basename
    m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(row)==set(h) for row in rows),t
    with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rows])
    files.append(p)
def text(key,value):loc.append([key,value,'true'])
descriptions=[
 'Hold Long Vi and win two ordinary campaign battles with Huyen Ve commanding a participating army. Battles before this mission and quest battles do not count.',
 'Rescue Da Lien from the Chaos warband and keep her alive. Huyen Ve must command the rescue army. Victory grants Da Lien at rank 5 and her Crimson Moonstone; an existing Hero and item are retained.',
 'Occupy Avauka. If a faction at peace with you owns it, you may instead pay 2,000 gold to open the road and ransom the armour. Already owning Avauka satisfies the objective.',
 'Send an independent Hero to the marked archive near Leilou. Afterwards, move an independent Hero into owned Long Vi to deliver the evidence. Lords and embedded Heroes cannot investigate or deliver.',
 'Huyen Ve\'s own army must kill enemy entities in ordinary campaign battles after this chapter begins. Embedded Heroes and all army unit classes count. Allied armies and quest battles do not count. The target scales with unit size: 2,000 at Ultra.',
 'Bring Huyen Ve to owned Long Vi and pay 3,000 gold once. Keep Long Vi for two subsequent faction turns while the blade is restored. Losing it pauses work; recovery resumes without another payment.'
]
active=[None,
 'Rescue Da Lien with Huyen Ve and keep her alive.',
 'Occupy Avauka, or negotiate passage for 2,000 gold if its owner is at peace with you.',
 'Send an independent Hero to the archive marker near Leilou.',
 'Enemy entities killed by Huyen Ve\'s army: %n / %n.',
 'Bring Huyen Ve to owned Long Vi and commission restoration for 3,000 gold.'
]
rewards=['Moonshadow Jade Pendant','Da Lien (rank 5) and Crimson Moonstone',
 'Long Vi Mountain-Pattern Armour','Warden\'s Seal','Moon Lantern','Nightwarden\'s Blade']
missions=[];payloads=[]
for i,stage in enumerate(S['stages'],1):
    assert stage['chapter']==i
    key=stage['mission'];m=one('missions','key','wh2_dlc09_books_of_nagash')
    m.update(key=key,mission_type='FIGHT_SET_PIECE_BATTLE' if i==2 else 'SCRIPTED',
      localised_title=stage['title'],localised_description=descriptions[i-1],
      localised_mission_completed_text='Reward confirmed: '+rewards[i-1]+'.',
      ui_image='cth/messenger',ui_icon='event_mission_neutral.png',event_category='Quest',
      set_piece_battle='mc_huyen_ve_rescue_da_lien' if i==2 else '',
      location_x='0',location_y='0',trigger_radius='5.0000' if i==2 else '0.0000',
      quest_character='mc_moon_warden' if i==2 else '',quest_mission='true' if i==2 else 'false',
      quest_mission_final='false',generate='false',can_be_manually_cancelled='false')
    missions.append(m)
    for field in ['localised_title','localised_description','localised_mission_completed_text']:text('missions_'+field+'_'+key,m[field])
    if active[i-1]:text('mission_text_text_'+key+'_active',active[i-1])
    p='mc_huyen_ve_quest_reward_'+str(i)
    payloads.append(dict(component=p,icon='ui/battle ui/ability_icons/wh3_main_lore_passive_power_of_yin.png',state='positive',sort_order=str(i)))
    text('campaign_payload_ui_details_description_'+p,rewards[i-1]+'. Existing copies are retained; no duplicate reward is created.')
write('missions',missions)
text('mission_text_text_mc_huyen_ve_quest_01_owned','Hold Long Vi (owned). Campaign victories commanded by Huyen Ve: %n / 2.')
text('mission_text_text_mc_huyen_ve_quest_01_unowned','Recover and hold Long Vi. Campaign victories commanded by Huyen Ve: %n / 2.')
text('mission_text_text_mc_huyen_ve_quest_04_deliver','Evidence recovered. Move an independent Hero into owned Long Vi to deliver it.')
text('mission_text_text_mc_huyen_ve_quest_06_processing','Restoration paid. Owned Long Vi processing turns: %n / 2. Work pauses if Long Vi is lost.')
for cost in [2000,3000]:
    p='mc_huyen_ve_quest_pay_'+str(cost)
    payloads.append(dict(component=p,icon='ui/battle ui/ability_icons/wh3_main_lore_passive_power_of_yin.png',state='negative',sort_order='0'))
    text('campaign_payload_ui_details_description_'+p,'Pay '+format(cost,',')+' gold once if funds and conditions are still valid when this option is chosen.')
write('campaign_payload_ui_details',payloads)
write('mission_issuers',[dict(issuer_key='mc_huyen_ve_moon_court',default_rounds_between='0',icon_path='ui/battle ui/ability_icons/wh3_main_lore_passive_power_of_yin.png')])
text('mission_issuers_on_screen_name_mc_huyen_ve_moon_court','Agents of the Moon')
dilemmas=[];choices=[];options=[]
for i,(key,title,desc,label) in enumerate([
 ('mc_huyen_ve_negotiate','Reopen the Southern Road','The keepers of Avauka offer safe passage and the return of the armour for 2,000 gold. The payment is made only if peace and sufficient funds still hold.','Pay 2,000 gold'),
 ('mc_huyen_ve_restore','Restore the Nightwarden','The smiths of Long Vi can restore the blade for 3,000 gold. Work needs two subsequent faction turns while you hold Long Vi. Huyen Ve may leave after commissioning it.','Pay 3,000 gold')]):
    d=one('dilemmas','key','wh3_main_minor_cult_loan');d.update(key=key,localised_title=title,localised_description=desc,ui_image='cth/messenger',generate='false');dilemmas.append(d)
    text('dilemmas_localised_title_'+key,title);text('dilemmas_localised_description_'+key,desc)
    for choice,caption in [('FIRST',label),('SECOND','Not yet')]:
        choices.append(dict(choice_key=choice,dilemma_key=key,audio_event_hover='',audio_choice_vo=''))
        text('cdir_events_dilemma_choice_details_localised_choice_label_'+key+choice,caption)
    for j,(option,value) in enumerate([('VAR_CHANCE','100'),('GEN_TARGET_NONE','')]):
        options.append(dict(id=str(1800312950+i*2+j),dilemma_key=key,option_key=option,value=value,target='default'))
write('dilemmas',dilemmas);write('cdir_events_dilemma_choice_details',choices);write('cdir_events_dilemma_option_junctions',options)
marker=one('campaign_interactable_marker_infos','key','wh3_dlc27_monster_arcanum');marker['key']='mc_huyen_ve_archive_info'
write('campaign_interactable_marker_infos',[marker])
p='text/db/mc_huyen_ve_quests.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)
scripts=['mc_huyen_ve_quest_state.lua','mc_huyen_ve_quest_campaign.lua','mc_huyen_ve_quest_chain.lua','mc_huyen_ve_quest_rewards.lua','mc_huyen_ve_start_at_long_vi.lua']
for name in scripts:
    p='script/campaign/mod/'+name;dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,dest);files.append(p)
p='script/battle/quest_battles/mc_huyen_ve/rescue/battle_script.lua';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,dest);files.append(p)
# Class-based set includes two classes omitted by native all_land_units.
rules=[r for r in native('unit_set_to_unit_junctions')[1] if r['unit_set']=='all_land_units' and r['exclude']=='false']
classes={r['unit_class'] for r in rules if r['unit_class']}
classes|={r['class'] for r in native('land_units')[1] if r['class']}
assert 'com' in classes and {'inf_mel','inf_mis','art_fld','art_fix','cav_mel','cav_mis'}<=classes
assert not {r['class'] for r in native('land_units')[1]}-classes
unit_set=one('unit_sets','key','all_land_units');unit_set['key']='mc_huyen_ve_all_army_units'
write('unit_sets',[unit_set])
write('unit_set_to_unit_junctions',[dict(unit_caste='',unit_category='',unit_class=k,unit_record='',unit_set=unit_set['key'],exclude='false') for k in sorted(classes)])
assert not PACK.exists(),PACK
# Use the native Gem of Blood item artwork for Da Lien's red gemstone.
equipment=json.loads((R/'src/campaign/da-lien-equipment.json').read_text())['item']
icons=subprocess.run([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(Path(C['game'])/'data/ui.pack')],capture_output=True,text=True,check=True).stdout.splitlines()
assert equipment['icon'] in icons
write('ancillary_types',[dict(type=equipment['key']+'_type',ui_icon=equipment['icon'])],'mc_da_lien_moonstone')
# Preserve the user-approved portrait in subsequent full quest builds.
portraits=R/'assets/authored/da-lien/portraits'
if (portraits/'manifest.json').exists():
    manifest=json.loads((portraits/'manifest.json').read_text())
    for p,info in manifest['outputs'].items():
        source=portraits/p;assert hashlib.sha256(source.read_bytes()).hexdigest()==info['sha256']
        dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);files.append(p)
# Retain the selected user sword when rebuilding the complete chain.
sword_spec=R/'src/campaign/huyen-ve-sword.json'
if sword_spec.exists():
    selected=json.loads(sword_spec.read_text());graphics=json.loads((R/selected['graphics_manifest']).read_text())
    assert graphics['status']=='exported_graphics_passed'
    for p in graphics['files']:
        source=R/selected['graphics_root']/p;assert hashlib.sha256(source.read_bytes()).hexdigest()==graphics['sha256'][p]
        dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);files.append(p)
shutil.copy2(BASE,PACK)
for p in files:
    tab=p.startswith('db/') or p.endswith('.loc');args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK)]
    if tab:args+=['-t',C['schema']]
    subprocess.run(args+['-f',str(O/(p+('.tsv' if tab else '')))+';'+p],check=True,stdout=subprocess.DEVNULL)
for source,fn_name in [('Validate-Repaired-Province-Packs.py','unpack'),('Validate-Huyen-Ve-Animation-Pack.py','diagnostic_rows')]:
    t=ast.parse((R/'tools'/source).read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==fn_name);exec(compile(ast.Module(body=[fn],type_ignores=[]),source,'exec'))
before=unpack(BASE);after=unpack(PACK)
assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items() if p not in files)
check=R/'reference/local/huyen-ve-chain-check';check.mkdir(exist_ok=True)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(PACK),'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)],check=True,stdout=subprocess.DEVNULL)
for p in files:
    if p.startswith('db/') or p.endswith('.loc'):assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
    else:assert after[p]==(O/p).read_bytes(),p
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
old=diagnostic_rows(BASE.parent/'diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');metadata=[];blocking=[]
for path,rs in new.items():
    if old.get(path)==rs:continue
    for row in rs:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in row['cells_affected']):metadata.append(dict(path=path,report=row))
        else:blocking.append(dict(path=path,report=row))
(O/'diagnostics-review.json').write_text(json.dumps(dict(metadata=metadata,blocking=blocking),indent=2));assert not blocking,blocking
v=dict(status='all_six_chapters_built_static_checks_passed',pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),files=files,enabled_chapters=list(range(1,7)),new_blocking_diagnostics=0,metadata_warnings=len(metadata),unrelated_payloads_unchanged=True,kill_unit_classes=sorted(classes),deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
