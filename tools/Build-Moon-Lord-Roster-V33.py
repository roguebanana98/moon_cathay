"""Moon-only native recruitment groups; standalone WWD gallery20 skills/model."""
import ast, copy, csv, hashlib, json, shutil, struct, subprocess, unicodedata
from pathlib import Path
from collections import defaultdict
from PIL import Image

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-v33-lord-roster'; N=R/'reference/local/lord-vanilla/db'
B=R/'reference/local/moon-v32-roundtrip'; D=R/'reference/local/deer-wwd/base/db'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v32_moonveil_approved.pack'
PACK=O/'mc_moonshadow_heroes_v33_lord_roster.pack'
if PACK.exists():
    failed=json.loads((O/'pack-validation.json').read_text())
    assert failed['status']=='diagnostics_need_review' and not failed['deployed']
    assert not (Path(C['game'])/'data'/PACK.name).exists()
F='cr_cth_agents_of_the_moon'; S='mc_mooncourt_lord'; U=S+'_human'; ART=S+'_art'
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='137dba76c2a95c065a935434fbf2ecd0ef67e6b4f1de050da1bca9c1715f702a'
M=json.loads((O/'models.json').read_text()); review=json.loads((O/'model-review.json').read_text())
assert review['status']=='passed' and review['models']==1 and not review['missing_textures']
assert sha(M['source'])==M['source_sha256']
T=defaultdict(list); loc={}; files=list(M['files']); changed=[]; cache={}
def native(t):
    if t not in cache: cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def src(t): return [r for p in sorted((D/(t+'_tables')).glob('*.tsv')) for r in read(p)[1]]
def allbase(t): return [r for p in (B/('db/'+t+'_tables')).glob('*.tsv') for r in read(p)[1]]
def combined(t): return native(t)[1]+src(t)
def one(t,k,v,source=False):
    rs=[r for r in (src(t) if source else native(t)[1]) if r[k]==v]
    assert rs,(t,k,v); return dict(rs[-1])
def clone(t,k,v,source=False,**kw):
    r=dict(one(t,k,v,source),**kw);T[t].append(r);return r
def table(t,rs,p=None):
    h,meta=copy.deepcopy(native(t)[0]);p=p or 'db/'+t+'_tables/zzzz_mc_mooncourt_lord'
    meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:
        csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
    changed.append(p)

# Both Shugengan lores actually share this category. No shared label/UI edits.
p='db/agent_subtypes_tables/zzzz_mc_moon_generals';rs=read(B/(p+'.tsv'))[1]
for r in rs:r['recruitment_category']='wh3_main_cth_dragon_blooded_shugengan'
table('agent_subtypes',rs,p)
table('agent_recruitment_categories',[],'db/agent_recruitment_categories_tables/zzzz_mc_moon_generals')
for lore in ['yin','yang']:
    T['faction_agent_permitted_subtypes'].append(dict(agent='general',faction=F,subtype='wh3_main_cth_dragon_blooded_shugengan_'+lore,mod_disabled='true'))
T['faction_agent_permitted_subtypes'].append(dict(agent='general',faction=F,subtype=S,mod_disabled='false'))

clone('agent_subtypes','key','zhaoyixuan',True,key=S,auto_generate='true',
      associated_unit_override=U,recruitment_category='wh3_dlc24_cth_celestial_general',
      names_group='names_mc_agents_of_the_moon_vietnamese',saving_settings='can_be_saved_loaded')
clone('main_units','unit','deer_cth_zhaoyixuan',True,unit=U,land_unit=U)
clone('land_units','key','deer_cth_zhaoyixuan',True,key=U,historical_description_text=U,short_description_text=U)
clone('variants','variant_name','deer_cth_zhaoyixuan',True,variant_name=S,variant_filename=S)
uv=one('unit_variants','unit','deer_cth_zhaoyixuan',True)
T['unit_variants'].append(dict(uv,unit=U,name=U,variant=S,unit_card=S))
clone('agent_uniforms','uniform_name','deer_cth_zhaoyixuan',True,uniform_name=S+'_uniform',filename=S,battle_filename=S,campaign_porthole_filename=S,campaign_politician_filename='variantmeshes/variantmeshdefinitions/'+S+'.variantmeshdefinition')
# Match the original female model/name pool consistently in battle and campaign.
clone('campaign_character_art_sets','art_set_id','deer_cth_zhaoyixuan',True,art_set_id=ART,agent_subtype=S,faction=F,is_male='false')
assert not any(r['id']=='1986113200' for r in native('campaign_character_arts')[1]+allbase('campaign_character_arts'))
clone('campaign_character_arts','id','2018227202',True,id='1986113200',art_set_id=ART,uniform=S+'_uniform')
T['units_to_groupings_military_permissions'].append(dict(unit=U,military_group='wh3_main_cth'))
for t in ['unit_description_historical_texts','unit_description_short_texts']:T[t].append(dict(key=U))

# Merge the exact source node set with its native nodes; scope every node privately.
items=[r for r in src('character_skill_node_set_items') if r['set']=='zhaoyixuan_skill_node_set' and r['item']]
nodeby={r['key']:r for r in combined('character_skill_nodes') if r['key']}
selected=[nodeby[r['item']] for r in items]
assert len(selected)==len({n['key'] for n in selected})
node_map={n['key']:S+'_node_'+str(i) for i,n in enumerate(selected)}
skill_keys={n['character_skill_key'] for n in selected}
custom_skills={r['key']:r for r in src('character_skills') if r['key'] in skill_keys}
skill_map={k:S+'_skill_'+str(i) for i,k in enumerate(sorted(custom_skills))}
custom_abilities=[r['key'] for r in src('unit_abilities') if 'zhaoyixuan' in r['key']]
ability_map={k:S+'_ability_'+str(i) for i,k in enumerate(sorted(custom_abilities))}
phases=[r for r in src('special_ability_to_special_ability_phase_junctions') if r['special_ability'] in ability_map]
phase_map={k:S+'_phase_'+str(i) for i,k in enumerate(sorted({r['phase'] for r in phases}))}
effect_map={k:S+'_effect_'+str(i) for i,k in enumerate(sorted(custom_abilities))}
anc_map={'deer_cth_zhaoyixuan_junfu':S+'_command_seal'}
mapping={**node_map,**skill_map,**phase_map,**anc_map}
# Ability and enabling effect have the same source keys; route by field/table below.
def remap(r,t):
    out=dict(r)
    for k,v in r.items():
        if (t=='character_skill_nodes' and k=='key') or k in ['parent_key','child_key','character_skill_node']:
            out[k]=node_map.get(v,v)
        elif (t=='character_skills' and k=='key') or k in ['character_skill_key','skill','skill_key','character_skill','required_skill']:
            out[k]=skill_map.get(v,v)
        elif (t=='ancillaries' and k=='key') or k in ['ancillary','granted_ancillary','required_ancillary']:
            out[k]=anc_map.get(v,v)
        elif k in ['effect','effect_key']:
            out[k]=effect_map.get(v,v)
        elif (t=='special_ability_phases' and k=='id') or k in ['phase','special_ability_phase']:
            out[k]=phase_map.get(v,v)
        elif (t in ['unit_abilities','unit_special_abilities'] and k=='key') or k in ['ability','unit_ability','special_ability','parent_ability']:
            out[k]=ability_map.get(v,v)
    return out
clone('character_skill_node_sets','key','zhaoyixuan_skill_node_set',True,key=S+'_skills',agent_subtype_key=S,faction_key=F)
for n,it in zip(selected,items):
    T['character_skill_nodes'].append(remap(n,'character_skill_nodes'))
    T['character_skill_node_set_items'].append(dict(it,set=S+'_skills',item=node_map[it['item']]))
for t,field in [('character_skill_node_links','parent_key'),('character_skill_nodes_skill_locks','character_skill_node')]:
    seen=set()
    for r in combined(t):
        if r[field] not in node_map:continue
        if t=='character_skill_node_links' and r['child_key'] not in node_map:continue
        row=remap(r,t);sig=tuple(row.items())
        if sig not in seen:T[t].append(row);seen.add(sig)
for r in custom_skills.values():T['character_skills'].append(remap(r,'character_skills'))
for n in T['character_skill_nodes']:
    assert sum(r['child_key']==n['key'] and r['link_type'] in ['SUBSET_REQUIRED','REQUIRED'] for r in T['character_skill_node_links'])>=int(n['required_num_parents']),n['key']
for t,field in [('character_skill_level_details','skill_key'),('character_skill_level_to_effects_junctions','character_skill_key'),('character_skills_to_level_reached_criterias','character_skill'),('character_skill_level_to_ancillaries_junctions','skill')]:
    T[t].extend(remap(r,t) for r in src(t) if r[field] in skill_map)
for t in ['unit_abilities','unit_special_abilities','special_ability_to_special_ability_phase_junctions','special_ability_to_auto_deactivate_flags','special_ability_intensity_settings','unit_abilities_to_additional_ui_effects_juncs']:
    for r in src(t):
        if any(v in ability_map for v in r.values()):
            row=remap(r,t)
            if t=='unit_special_abilities':row['unique_id']=str(1986113230+sorted(ability_map).index(r['key']))
            T[t].append(row)
for t in ['special_ability_phases','special_ability_phase_stat_effects','special_ability_phase_attribute_effects']:
    T[t].extend(remap(r,t) for r in src(t) if any(v in phase_map for v in r.values()))
for t in ['effects','effect_bonus_value_unit_ability_junctions']:
    T[t].extend(remap(r,t) for r in src(t) if r['effect'] in effect_map)
for t in ['ancillaries','ancillary_info','ancillary_to_effects','ancillaries_required_skills']:
    T[t].extend(remap(r,t) for r in src(t) if any(v in anc_map for v in r.values()))
T['ancillaries_included_agent_subtypes'].append(dict(agent_subtype=S,ancillary=anc_map['deer_cth_zhaoyixuan_junfu']))

# Source unit abilities plus every native spell/passive reachable from its exact tree.
abilities={r['ability'] for r in src('land_units_to_unit_abilites_junctions') if r['land_unit']=='deer_cth_zhaoyixuan'}
effects={r['effect_key'] for r in combined('character_skill_level_to_effects_junctions') if r['character_skill_key'] in skill_keys}
abilities.update(r['unit_ability'] for r in combined('effect_bonus_value_unit_ability_junctions') if r['effect'] in effects and r['bonus_value_id']=='enable')
for a in sorted(abilities):T['land_units_to_unit_abilites_junctions'].append(dict(ability=ability_map.get(a,a),land_unit=U,culture='*'))
for t in ['special_ability_groups_to_units_junctions','unit_set_to_unit_junctions']:
    field='unit' if t.startswith('special_') else 'unit_record'
    T[t].extend(dict(r,**{field:U}) for r in src(t) if r[field]=='deer_cth_zhaoyixuan')

# All source-specific UI text is English ASCII; native skills retain native keys/text.
english={}
for root in [R/'reference/local/moon-v33-native-loc',R/'reference/local/deer-wwd/english']:
    for p in root.rglob('*.tsv'):
        try:rs=read(p)[1]
        except Exception:continue
        for r in rs:
            if 'text' in r and r['text'].isascii():english[r['key']]=r['text']
titles={'zhaoyixuan_skill_texing':'Commander of the Southern Army','cth_zhaoyixuan_skill_1_0':'Soul of the Dragonblood','cth_zhaoyixuan_skill_1_1':'Southern Army Reforms','cth_zhaoyixuan_skill_1_2':'Lineage of Severance','cth_zhaoyixuan_skill_1_3':'Lower City Patrols','cth_zhaoyixuan_skill_1_4':'Loyal Guardians','cth_zhaoyixuanARMY_self_0':'Enduring Scion','cth_zhaoyixuanARMY_self_1':'Southern Army Battle Formation','deer_cth_zhaoyixuan_junfu':'Southern Army Command Seal','wh3_main_skill_innate_lvqiling_innate_4':'Dragonblood Authority'}
for old,new in skill_map.items():
    loc['character_skills_localised_name_'+new]=titles.get(old,english.get('character_skills_localised_name_'+old,''))
    assert loc['character_skills_localised_name_'+new],old
    loc['character_skills_localised_description_'+new]=english.get('character_skills_localised_description_'+old,'The original Zhao Yixuan skill from Walk with the Dragon. Effects and rank requirements are preserved.')
ability_names=['Wrath of the Soul River','Daughter of a Lost Age','Between Two Worlds']
for old,title in zip(sorted(ability_map),ability_names):
    new=ability_map[old];loc['unit_abilities_onscreen_name_'+new]=title;loc['unit_abilities_tooltip_text_'+new]='Zhao Yixuan\'s original ability from Walk with the Dragon.';loc['effects_description_'+effect_map[old]]='Ability: '+title
anc=anc_map['deer_cth_zhaoyixuan_junfu'];loc['ancillaries_onscreen_name_'+anc]='Southern Army Command Seal';loc['ancillaries_colour_text_'+anc]='A badge of authority commanding the Jade Warriors and Dragon Guard.'
for r in T['unit_abilities']:
    if r['icon_name']=='wwd_summon_soul_dragon':
        path='ui/battle ui/ability_icons/'+r['icon_name']+'.png';dest=O/path;dest.parent.mkdir(parents=True,exist_ok=True)
        cli('pack','extract','-p',M['source'],'-f',path+';'+str(O));assert dest.exists();files.append(path)
# Keep WWD's own skill artwork and reuse its existing spirit icon for namespaced phases.
p='ui/campaign ui/skills/wwd_wwd.png';(O/p).parent.mkdir(parents=True,exist_ok=True)
cli('pack','extract','-p',M['source'],'-f',p+';'+str(O));assert (O/p).exists();files.append(p)
for phase in T['special_ability_phases']:
    p='ui/battle ui/ability_icons/'+phase['id']+'.png';(O/p).parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(O/'ui/battle ui/ability_icons/wwd_summon_soul_dragon.png',O/p);files.append(p)

for folder,kind in [('units','body'),('portholes','head')]:
    path='ui/portraits/'+folder+'/no_culture/'+S+'_0.png';dest=O/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'renders'/(S+'_'+kind+'.png'),dest);files.append(path)
    settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text());entry=settings['entries'][0];entry['id']=ART;entry['variants'][0].update(filename=S,file_diffuse=path,faction_leader=False)
    jp=O/('portrait-'+folder+'.json');jp.write_text(json.dumps(settings));p='ui/portraits/'+folder+'/portrait_settings__'+S+'.bin';cli('portrait-settings','from-json','-j',jp,'-b',O/p);files.append(p)
for p,kind,size in [('ui/units/icons/'+S+'.png','body',(104,208)),('ui/units/minspec_portholes/'+U+'.png','head',(256,256))]:
    (O/p).parent.mkdir(parents=True,exist_ok=True)
    with Image.open(O/'renders'/(S+'_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(O/p)
    files.append(p)
for num,donor,text in [('1986113210','1087565330','Zhao Yixuan'),('1986113211','1015096215','')]:
    assert not any(r['id']==num for r in native('names')[1]+allbase('names'))
    clone('names','id',donor,id=num,gender='f',frequency='0');loc['names_name_'+num]=text
char=clone('battle_set_piece_armies_characters','character_name','deer_cth_zhaoyixuan',True,character_name=S+'_cb',unit_type=U,agent_subtype=S,character_model='1986113200',portrait='ui/portraits/portholes/no_culture/'+S+'_0.png',forename='1986113210',surname='1986113211',skillset=S+'_cb_skills')
T['battle_set_piece_armies_characters_skillsets'].append(dict(key=S+'_cb_skills'))
source_cb=src('battle_set_piece_armies_characters_skillsets_skills')
source_cb=[r for r in source_cb if r['skillset_key']=='zhaoyixuan_skill_node_set']
if source_cb:T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(r,skill=skill_map.get(r['skill'],r['skill']),skillset_key=S+'_cb_skills') for r in source_cb)
else:T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(skill=skill_map.get(k,k),skillset_key=S+'_cb_skills',sort_order=str(i)) for i,k in enumerate(sorted(skill_keys)) if k)
permission=one('units_custom_battle_permissions','unit','deer_cth_zhaoyixuan',True)
permission.update(unit=U,general_uniform=S+'_uniform',general_portrait=char['portrait'],set_piece_character=char['character_name'])
T['units_custom_battle_permissions'].append(permission)
T['units_custom_battle_permissions'].append(dict(permission,faction=F,campaign_exclusive='true'))
loc.update({'agent_subtypes_onscreen_name_override_'+S:'Zhao Yixuan','agent_subtypes_description_text_override_'+S:'Commander of the Southern Army. A dragon-blooded lord wielding Yin and the powers of the spirit world.','land_units_onscreen_name_'+U:'Zhao Yixuan','unit_description_short_texts_text_'+U:'Wizard Lord','unit_description_historical_texts_text_'+U:'The Southern Army commander from Walk with the Dragon, serving the hidden court of the moon.'})
for t,rs in T.items():
    if rs:table(t,rs)
p='text/db/zzzz_mc_mooncourt_lord.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(s.isascii() for s in loc.values())
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
changed.append(p)
before=unpack(BASE);assert 'script/campaign/mod/mc_moon_hide_celestial_general_tab.lua' not in before
files=sorted(set(files))
if not PACK.exists():shutil.copy2(BASE,PACK)
current=unpack(PACK)
assets_to_add=[p for p in files if current.get(p)!=(O/p).read_bytes()]
cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in changed])
for i in range(0,len(assets_to_add),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in assets_to_add[i:i+20]])
after=unpack(PACK);assert all(after[p]==data for p,data in before.items() if p not in changed)
check=R/'reference/local/moon-v33-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in changed:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,gallery_model=20,source_skill_nodes=len(selected),source_custom_skills=len(skill_map),custom_abilities=len(ability_map),source_skill_mechanics_preserved=True,source_native_animation=True,shugengan_group='wh3_main_cth_dragon_blooded_shugengan',native_shugengan_disabled_moon_only=True,private_assault_category_removed=True,unrelated_payloads_unchanged=True,no_ui_script=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));(O/'dependency-maps.json').write_text(json.dumps(dict(nodes=node_map,skills=skill_map,abilities=ability_map,effects=effect_map,phases=phase_map,ancillaries=anc_map),indent=2));print(json.dumps(report,indent=2));assert not blocking
