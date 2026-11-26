"""Private standalone integration of the requested Workshop engineer into current roster.

No original/submod pack is required at runtime. Workshop inputs stay read-only.
"""
import ast,copy,csv,hashlib,json,re,shutil,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-heroes-v17-engineer';O.mkdir(parents=True,exist_ok=True)
D=R/'reference/local/luke-engineer';N=R/'reference/local/lord-vanilla/db'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v16_tidecaller_healing.pack'
SOURCE=Path(C['workshop'])/'2815205063/Luke_cth_master_engineer.pack'
PACK=O/'mc_moonshadow_heroes_v17_master_engineer.pack'
if PACK.exists():
    assert '--rebuild' in sys.argv and not (O/'deployment.json').exists() and not (Path(C['game'])/'data'/PACK.name).exists()
    PACK.unlink()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='594a980327a20e439692106d71116b8f8313f8bcd5744aa30e046df881eba6ce'
source_sha=sha(SOURCE);before=unpack(BASE);donor=unpack(SOURCE)
F='cr_cth_agents_of_the_moon';S='Luke_cth_master_engineer';T={};H={};dbfiles=[];assets=[];removed_native_art=0
for directory in sorted((D/'db').iterdir()):
    t=directory.name.removesuffix('_tables');parts=list(directory.glob('*.tsv'))
    assert len(parts)==1
    H[t],T[t]=read(parts[0])
    if t in ('agent_culture_details','technology_effects_junction'):T[t]=[]
    if t=='campaign_character_art_sets':
        removed_native_art=sum(r['agent_subtype']!=S for r in T[t])
        T[t]=[dict(r,faction=F) for r in T[t] if r['agent_subtype']==S]
    if t=='faction_agent_permitted_subtypes':T[t]=[dict(agent='wizard',faction=F,subtype=S,mod_disabled='false')]
    if t=='character_skill_node_sets':T[t]=[dict(r,faction_key=F) for r in T[t]]
    if t=='building_effects_junction':T[t]=[dict(r,context_requirement='mc_engineer_owner') for r in T[t]]
# Scope the existing Forge enable/cap additions to the requested faction.
H['building_effect_context_expressions'],native_context=read(N/'building_effect_context_expressions_tables/data__.tsv')
context=next(r for r in native_context if r['key']=='AislinnBuiltInColony')
T['building_effect_context_expressions']=[dict(context,key='mc_engineer_owner',expression='Region.Owner.RecordKey == "'+F+'"',display_only_active_effects='true')]
description='Master artisans of the Cathayan forges maintain the army\'s firearms and artillery, bringing engineering expertise and experimental weapons to the battlefield.'
names={'engineer_mount_sky_lantern':'Sky Lantern','engineer_mount_sky_junk':'Sky Junk','engineer_warhorse':'Warhorse','engineer_gyrobomber':'Gyrobomber','engineer_rocket':'Portable Fire Rain Rocket','engineer_rocket_02':'Skywrath Rocket','cth_engineer_kongbai':'Spare Skill Points'}
descs={'engineer_mount_sky_lantern':'An aerial observation platform used by the armies of Cathay.','engineer_mount_sky_junk':'A flying fortress that rains rockets upon the enemy.','engineer_warhorse':'A dependable warhorse trained for the noise and danger of battle.','engineer_gyrobomber':'A heavily armed flying machine combining Cathayan and Dwarfen engineering.','engineer_rocket':'A portable Fire Rain rocket launcher. Available on foot, on a Warhorse, or aboard a Sky Lantern.','engineer_rocket_02':'An aerial rocket launcher that rains explosive projectiles down upon the enemy.','cth_engineer_kongbai':'Spends surplus skill points without granting an effect. Up to 99 ranks.'}
loc={}
for i in ('','_02','_03','_04','_05'):loc['land_units_onscreen_name_'+S+i]='Master Engineer'
for k in ('unit_description_short_texts_text_','unit_description_historical_texts_text_'):loc[k+S]=description
for k in ('agent_subtypes_onscreen_name_override_','agent_culture_details_onscreen_name_'):loc[k+(S if 'subtypes' in k else '9880156')]='Master Engineer'
for k in ('agent_subtypes_description_text_override_','agent_culture_details_description_text_'):loc[k+(S if 'subtypes' in k else '9880156')]=description
for key,name in names.items():
    loc['character_skills_localised_name_'+key]=name;loc['character_skills_localised_description_'+key]=descs[key]
for key in ('engineer_rocket','engineer_rocket_02'):
    loc['unit_abilities_onscreen_name_'+key]=names[key];loc['unit_abilities_tooltip_text_'+key]=descs[key]
mounts=[('engineer_sky_lantern','engineer_mount_sky_lantern','_02'),('engineer_sky_junk','engineer_mount_sky_junk','_03'),('engineer_warhorse','engineer_warhorse','_04'),('engineer_gyrobomber','engineer_gyrobomber','_05')]
for ancillary,skill,suffix in mounts:
    loc['ancillaries_onscreen_name_'+ancillary]=names[skill];loc['ancillaries_colour_text_'+ancillary]=descs[skill]
    loc['units_custom_battle_mounts_mount_name_'+S+S+suffix]=names[skill]
    loc['units_custom_battle_mounts_localised_description_'+S+S+suffix]=descs[skill]
for effect,text in {
 'wh3_main_effect_agent_action_cost_mod_cth_engineer':'Master Engineer hero action cost: %+n%',
 'wh3_main_effect_agent_action_success_chance_cth_engineer':'Master Engineer hero action success chance: %+n%',
 'wh3_main_effect_agent_cap_increase_cth_engineer':'Wizard capacity: %+n (Master Engineers share this pool)',
 'wh3_main_effect_agent_enable_recruitment_cth_engineer':'Enables recruitment of Master Engineers',
 'wh3_main_effect_agent_recruitment_xp_cth_engineer':'Master Engineer recruit rank: %+n',
 'engineer_mount_sky_junk':'Mount: Sky Junk','engineer_warhorse':'Mount: Warhorse',
 'engineer_gyrobomber':'Mount: Gyrobomber (not shown on the campaign map)',
 'engineer_rocket':'Ability: Portable Fire Rain Rocket','cth_engineer_kongbai':'No additional effects'}.items():loc['effects_description_'+effect]=text
for skill in T['character_skills']:
    skill['localised_name']=names[skill['key']];skill['localised_description']=descs[skill['key']]
# Preserve original custom text coverage, while replacing all of it with English ASCII.
original_loc={r['key'] for p in (D/'text').rglob('*.tsv') for r in read(p)[1]}
assert original_loc<=loc.keys(),original_loc-loc.keys()
assert all(v.isascii() for v in loc.values())
assert len(T['faction_agent_permitted_subtypes'])==1 and T['faction_agent_permitted_subtypes'][0]['faction']==F
assert len(T['building_effects_junction'])==6 and all(r['context_requirement']=='mc_engineer_owner' for r in T['building_effects_junction'])
assert next(r for r in T['agent_subtypes'] if r['key']==S)['cap']=='-1'
assert all(r['campaign_cap']=='-1' for r in T['main_units'])
assert len(T['main_units'])==5 and len(T['ancillaries'])==4
for t,rs in T.items():
    if not rs:continue
    h,m=copy.deepcopy(H[t]);p='db/'+t+'_tables/mc_engineer_integrated';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    dbfiles.append(p)
p='text/db/mc_master_engineer.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in sorted(loc.items())])
dbfiles.append(p)
material_map={p:'variantmeshes/wh_variantmodels/mc_master_engineer/materials/'+hashlib.sha256(p.encode()).hexdigest()[:12]+'.xml.material' for p in donor if p.endswith('.xml.material')}
def rewrite_material_refs(data):
    text=data.decode('utf8')
    for original,private in material_map.items():text=re.sub(re.escape(original).replace('/',r'[/\\]'),lambda _:private,text,flags=re.I)
    return text.encode('utf8')
for original,data in donor.items():
    p=original
    if p.startswith(('db/','text/')):continue
    if p.endswith('.bin') and p.startswith('ui/portraits/'):continue # Rebuild the donor's invalid mask setting below.
    assert p.startswith(('variantmeshes/','warmachines/','ui/')),p
    if p.endswith('.xml.material'):p=material_map[p]
    if original.endswith(('.wsmodel','.xml.material')):data=rewrite_material_refs(data)
    assert p not in before,'Do not replace existing model/UI payloads'
    dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);assets.append(p)
# Reuse the original PNG bytes at the missing card/minspec aliases. No new artwork.
for u in (S,S+'_02',S+'_03',S+'_04',S+'_05'):
    p='ui/units/minspec_portholes/'+u+'.png';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(donor['ui/portraits/portholes/wh3_main_cth_cathay/'+S+'.png']);assets.append(p)
p='ui/units/icons/'+S+'.png';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_bytes(donor['ui/portraits/units/wh3_main_cth_cathay/'+S+'.png']);assets.append(p)
for folder in ('units','portholes'):
    settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text(encoding='utf8'))
    entry=settings['entries'][0];entry['id']=S;variant=entry['variants'][0]
    variant.update(filename='Luke_cth_master_engineer_emp',file_diffuse='ui/portraits/'+folder+'/wh3_main_cth_cathay/'+S+'.png',file_mask_1='',file_mask_2='',file_mask_3='',faction_leader=False)
    j=O/('portrait-'+folder+'.json');j.write_text(json.dumps(settings,indent=2),encoding='utf8')
    p='ui/portraits/'+folder+'/portrait_settings__mc_master_engineer.bin';cli('portrait-settings','from-json','-j',j,'-b',O/p);assets.append(p)
assert not any(p.startswith('animations/') for p in assets)
shutil.copy2(BASE,PACK)
for start in range(0,len(dbfiles),20):cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles[start:start+20]])
for start in range(0,len(assets),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in assets[start:start+20]])
after=unpack(PACK);assert not set(before)&set(dbfiles+assets)
assert set(after)==set(before)|set(dbfiles)|set(assets) and all(after[p]==b for p,b in before.items())
assert sha(SOURCE)==source_sha
check=R/'reference/local/moon-engineer-v17-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),source=str(SOURCE),source_sha256=source_sha,blocking_diagnostics=blocking,existing_payloads_unchanged=True,standalone_original_mod_not_required=True,faction=F,subtype=S,regular_repeatable_hero=True,mounts=4,unit_variants=5,english_ascii_loc=True,roundtrip_passed=True,source_global_astromancer_art_overrides_omitted=removed_native_art,source_global_technology_effects_omitted=3,forge_effects_owner_scoped=True,assets=len(assets),deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2));assert not blocking
