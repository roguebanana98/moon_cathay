"""V13 model/recruitment preview. Spell design intentionally deferred by user."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess,sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-casters-v13';N=R/'reference/local/lord-vanilla/db';F='cr_cth_agents_of_the_moon'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v12_moon_skills.pack';PACK=O/'mc_moonshadow_heroes_v13_three_casters.pack'
if PACK.exists():
    assert '--rebuild' in sys.argv and not (O/'deployment.json').exists() and not (Path(C['game'])/'data'/PACK.name).exists()
    PACK.unlink()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='ec666bfa8561a7b8e3b7ead6159e1d68fe8004c6923c2f8dea865a87ada9d24f'
M=json.loads((O/'models.json').read_text(encoding='utf8'));review=json.loads((O/'model-review.json').read_text(encoding='utf8'))
assert review['samples']==63 and not review['missing_textures']
assert b'hu1e_mage_storm_dragon' in (R/'reference/local/moon-casters-animation/hu1e_mage_storm_dragon.bin').read_bytes()
for model in M['models']:
    ws=ET.parse(O/model['wsmodel'])
    assert (O/ws.findtext('geometry')).is_file()
    for material in ws.findall('.//material'):
        assert (O/material.text).is_file()
        for source in ET.parse(O/material.text).findall('.//source'):
            if source.text.startswith('variantmeshes/wh_variantmodels/mc_moon_casters/'):
                assert (O/source.text).is_file()
T=defaultdict(list);cache={};loc={};files=list(M['files']);dbfiles=[]
def native(t):
    if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def rows(t):return native(t)[1]
def one(t,field,value):
    found=[r for r in rows(t) if r[field]==value];assert len(found)==1,(t,field,value,len(found));return dict(found[0])
def clone(t,field,value,**changes):
    r=dict(one(t,field,value),**changes);T[t].append(r);return r
donor='wh3_main_cth_astromancer';unit='wh3_main_cth_cha_astromancer_0'
assert any(r['land_animation']=='cam_hu1e_mage_storm_dragon' for r in rows('campaign_character_arts'))
buildings=['wh3_main_cth_magic_tower_'+str(i) for i in (1,2,3)]
context='mc_moon_casters_owner'
clone('building_effect_context_expressions','key','AislinnBuiltInColony',key=context,expression='Region.Owner.RecordKey == "'+F+'"',display_only_active_effects='true')
# Shared native wizard capacity: add subtype availability only, never +1 cap per lore.
assert any(r['effect']=='wh3_main_effect_agent_cap_increase_cth_astromancer' and r['agent']=='wizard' and r['bonus_value_id']=='cap' for r in rows('effect_bonus_value_agent_junction'))
baseitems=[r for r in rows('character_skill_node_set_items') if r['set']=='wh3_main_skill_node_set_cth_astromancer']
nodeby={r['key']:r for r in rows('character_skill_nodes')}
# Only general resistance/support/actions/innate traits until spell trees are approved.
selected=[nodeby[x['item']] for x in baseitems if (nodeby[x['item']]['indent'] in ('0','5','6','8','99') and 'mount_' not in nodeby[x['item']]['character_skill_key'])]
for i,m in enumerate(M['models']):
    s=m['key'];u=s+'_human';art=s+'_art';name=m['name'];effect=s+'_recruitment'
    assert not any(r['key']==s for r in rows('agent_subtypes'))
    clone('agent_subtypes','key',donor,key=s,associated_unit_override=u,has_female_name='true',can_be_loaned='false',
          audio_voiceover_actor_group='wh3_main_vo_actor_Cathay_Miao_Ying',small_icon='ui/campaign ui/agents/wh_main_lore_heavens.png')
    clone('main_units','unit',unit,unit=u,land_unit=u,audio_voiceover_actor_group='wh3_main_vo_actor_Cathay_Miao_Ying')
    clone('land_units','key',unit,key=u,man_animation='hu1e_mage_storm_dragon',is_male='false',historical_description_text=u,short_description_text=u)
    for t in ('unit_description_historical_texts','unit_description_short_texts'):T[t].append(dict(key=u))
    uv=next(r for r in rows('unit_variants') if r['unit']==unit)
    T['unit_variants'].append(dict(uv,unit=u,name=u,variant=s,unit_card=s))
    clone('variants','variant_name','wh3_main_cth_cha_astromancer_campaign_01',variant_name=s,variant_filename=s,scale='0.9500',scale_variation='0.0000')
    clone('agent_uniforms','uniform_name','wh3_main_uniform_cth_astromancer_01',uniform_name=s+'_uniform',filename=s,battle_filename=s,campaign_porthole_filename=s)
    clone('campaign_character_art_sets','art_set_id','wh3_main_art_set_cth_astromancer_01',art_set_id=art,agent_subtype=s,faction=F,is_male='false')
    clone('campaign_character_arts','id','2076027974',id=str(1986112300+i),art_set_id=art,uniform=s+'_uniform',land_animation='cam_hu1e_mage_storm_dragon')
    T['faction_agent_permitted_subtypes'].append(dict(agent='wizard',faction=F,subtype=s,mod_disabled='false'))
    T['land_units_to_unit_abilites_junctions'].extend(dict(r,land_unit=u) for r in rows('land_units_to_unit_abilites_junctions') if r['land_unit']==unit)
    clone('effects','effect','wh3_main_effect_agent_enable_recruitment_cth_astromancer',effect=effect)
    T['effect_bonus_value_agent_subtype_junctions'].append(dict(bonus_value_id='availability',effect=effect,subtype=s))
    for building in buildings:
        native_enable=next(r for r in rows('building_effects_junction') if r['building']==building and r['effect']=='wh3_main_effect_agent_enable_recruitment_cth_astromancer')
        T['building_effects_junction'].append(dict(native_enable,effect=effect,context_requirement=context))
    clone('character_skill_node_sets','key','wh3_main_skill_node_set_cth_astromancer',key=s+'_skills',agent_subtype_key=s,faction_key=F)
    mapping={n['key']:s+'_node_'+str(j) for j,n in enumerate(selected)}
    for n in selected:
        new=dict(n,key=mapping[n['key']]);T['character_skill_nodes'].append(new)
        T['character_skill_node_set_items'].append(dict(set=s+'_skills',item=new['key'],mod_disabled='false'))
    for link in rows('character_skill_node_links'):
        if link['parent_key'] in mapping and link['child_key'] in mapping:T['character_skill_node_links'].append(dict(link,parent_key=mapping[link['parent_key']],child_key=mapping[link['child_key']]))
    loc.update({'agent_subtypes_onscreen_name_override_'+s:name,'land_units_onscreen_name_'+u:name,
                'unit_description_short_texts_text_'+u:'Wizard',
                'unit_description_historical_texts_text_'+u:{'mc_pyromancer':'A keeper of the sacred flame, sworn to defend the hidden court of the moon.','mc_astral_weaver':'A patient observer of the heavens, weaving the secrets of moonlight into the designs of the hidden court.','mc_tidecaller':'A guardian of the rivers and coastal waters, serving the hidden court with the patience of the rising tide.'}[s],
                'effects_description_'+effect:'Enables recruitment of '+name+' (shares Astromancer capacity)'})
    for folder,kind,size in [('units','body',None),('portholes','head',None)]:
        p='ui/portraits/'+folder+'/no_culture/'+s+'_0.png';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'renders'/(s+'_'+kind+'.png'),dest);files.append(p)
        settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text(encoding='utf8'))
        entry=settings['entries'][0];entry['id']=art;variant=entry['variants'][0];variant.update(filename=s,file_diffuse=p,faction_leader=False)
        jp=O/('portrait-'+s+'-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2),encoding='utf8')
        p='ui/portraits/'+folder+'/portrait_settings__'+s+'.bin';cli('portrait-settings','from-json','-j',jp,'-b',O/p);files.append(p)
    for p,kind,size in [('ui/units/icons/'+s+'.png','body',(104,208)),('ui/units/minspec_portholes/'+u+'.png','head',(256,256))]:
        (O/p).parent.mkdir(parents=True,exist_ok=True)
        with Image.open(O/'renders'/(s+'_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(O/p)
        files.append(p)
# Validate each new tree is self-contained and no hidden starting spell was inherited.
keys={r['key'] for r in T['character_skill_nodes']}
assert all(l['parent_key'] in keys and l['child_key'] in keys for l in T['character_skill_node_links'])
assert not any('heavens' in r['character_skill_key'] or 'mount_' in r['character_skill_key'] for r in T['character_skill_nodes'])
assert not any('cap' in r['bonus_value_id'] for r in T['effect_bonus_value_agent_subtype_junctions'])
assert len(T['building_effects_junction'])==9 and all(r['context_requirement']==context for r in T['building_effects_junction'])
for t,rs in T.items():
    h,m=copy.deepcopy(native(t)[0]);p='db/'+t+'_tables/mc_moon_casters';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    dbfiles.append(p)
assert all(v.isascii() for v in loc.values())
p='text/db/mc_moon_casters.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
dbfiles.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
for start in range(0,len(files),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files[start:start+20]])
before=unpack(BASE);after=unpack(PACK)
assert not set(before)&set(files+dbfiles),'Only additive hero records and namespaced graphics'
assert set(after)==set(before)|set(files)|set(dbfiles) and all(after[p]==data for p,data in before.items())
check=R/'reference/local/moon-casters-v13-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,existing_payloads_unchanged=True,starting_movement_fix_unchanged=True,shared_wizard_capacity=True,additional_capacity=0,buildings=buildings,faction=F,models=M['models'],sampled_poses=review['samples'],spells_pending=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2));assert not blocking
