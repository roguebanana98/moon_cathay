"""V24: ordinary Light support hero replacing Moon faction Alchemist recruitment."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moonveil-v24';N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moon-casters-v23-roundtrip';F='cr_cth_agents_of_the_moon'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v23_caster_support.pack';PACK=O/'mc_moonshadow_heroes_v24_moonveil_adept.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='9224432b00ed01da007512bf24f28ada3371b1cb5d4270787196ef2607727e4e'
M=json.loads((O/'models.json').read_text());review=json.loads((O/'model-review.json').read_text());assert review['status']=='passed' and review['models']==4 and not review['missing_textures'];assert sha(M['source'])==M['source_sha256']
S='mc_moonveil_adept';U=S+'_human';donor='wh3_main_cth_alchemist';du='wh3_main_cth_cha_alchemist_0';T=defaultdict(list);cache={};loc={};files=list(M['files']);dbfiles=[]
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t]
def rows(t):return native(t)[1]
def one(t,k,v):
 a=[r for r in rows(t) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def clone(t,k,v,**changes):
 r=dict(one(t,k,v),**changes);T[t].append(r);return r
clone('agent_subtypes','key',donor,key=S,associated_unit_override=U,has_female_name='true',recruitment_category=S,small_icon='ui/campaign ui/agents/wh_main_lore_light.png')
clone('agent_recruitment_categories','key','brt_prophetess',key=S,order='5')
T['faction_agent_permitted_subtypes']=[dict(agent='engineer',faction=F,subtype=S,mod_disabled='false'),dict(agent='engineer',faction=F,subtype=donor,mod_disabled='true')]
context=S+'_owner';clone('building_effect_context_expressions','key','AislinnBuiltInColony',key=context,expression='Region.Owner.RecordKey == "'+F+'"',display_only_active_effects='true')
effect=S+'_recruitment';clone('effects','effect','wh3_main_effect_agent_enable_recruitment_cth_alchemist',effect=effect);T['effect_bonus_value_agent_subtype_junctions'].append(dict(bonus_value_id='availability',effect=effect,subtype=S))
for r in rows('building_effects_junction'):
 if r['effect']=='wh3_main_effect_agent_enable_recruitment_cth_alchemist':T['building_effects_junction'].append(dict(r,effect=effect,context_requirement=context))
assert len(T['building_effects_junction'])==7
assert any(r['effect']=='wh3_main_effect_agent_cap_increase_cth_alchemist' and r['agent']=='engineer' and r['bonus_value_id']=='cap' for r in rows('effect_bonus_value_agent_junction'))
for t,field in [('campaign_group_member_criteria_agent_subtypes','agent_subtype'),('effect_bonus_value_agent_subtype_junctions','subtype')]:T[t].extend(dict(r,**{field:S}) for r in rows(t) if r[field]==donor)
# One unit variant record per unit; coherent random colour options are nested VMDs.
root=ET.Element('VARIANT_MESH');slot=ET.SubElement(root,'SLOT',name='appearance')
for m in M['models']:ET.SubElement(slot,'VARIANT_MESH_REFERENCE',definition=m['vmd'])
p='variantmeshes/variantmeshdefinitions/'+S+'.variantmeshdefinition';(O/p).write_bytes(ET.tostring(root,encoding='utf8'));files.append(p)
clone('variants','variant_name','wh3_main_cth_cha_alchemist_campaign_01',variant_name=S,variant_filename=S,scale='1.0000',scale_variation='0.0000',low_poly_filename='',super_low_poly_filename='')
units=[(U,du),(S+'_warhorse','wh3_main_cth_cha_alchemist_1'),(S+'_sky_lantern','wh3_main_cth_cha_alchemist_2')]
for u,d in units:
 clone('main_units','unit',d,unit=u,land_unit=u,ui_unit_group_land='wizard_light')
 clone('land_units','key',d,key=u,historical_description_text=U,short_description_text=U)
 uv=next(r for r in rows('unit_variants') if r['unit']==d);T['unit_variants'].append(dict(uv,unit=u,name=u,variant=S,unit_card=S))
 T['units_to_groupings_military_permissions'].append(dict(unit=u,military_group='wh3_main_cth'))
 T['unit_set_to_unit_junctions'].extend(dict(r,unit_record=u) for r in rows('unit_set_to_unit_junctions') if r['unit_record']==d)
 T['special_ability_groups_to_units_junctions'].append(dict(ability_group='wh_main_lore_light',unit=u,group_page_order='0'))
 # Native Light list includes the passive and all six spells; upgrades follow
 # their original overpower_option links. Common mage skills retain native effects.
 native_light={r['unit_special_abilities'] for r in rows('special_ability_groups_to_unit_abilities_junctions') if r['special_ability_groups']=='wh_main_lore_light'}
 for ability in sorted(native_light):T['land_units_to_unit_abilites_junctions'].append(dict(ability=ability,land_unit=u,culture='*'))
 loc['land_units_onscreen_name_'+u]='Moonveil Adept'
 for r in rows('campaign_mount_animation_set_overrides'):
  if r['mount_unit']==d:T['campaign_mount_animation_set_overrides'].append(dict(r,mount_unit=u))
 # Alchemist's Sky Lantern uses the generic sword-lord campaign rider profile.
 if u.endswith('_sky_lantern'):
  T['campaign_mount_animation_set_overrides'].append(dict(character_animation_set='cam_hu1e_hr1_mage_female_hero',mount_unit=u,rider_animation_set='cam_hu1e_sj1_skylantern_sword_lord',vfx_filter_override='0'))
 for r in rows('units_custom_battle_permissions'):
  if r['unit']==d and r['faction']=='wh3_main_cth_cathay_mp':T['units_custom_battle_permissions'].append(dict(r,unit=u,general_portrait='ui/portraits/portholes/no_culture/'+S+'_white_0.png',general_uniform=S+'_white_uniform',set_piece_character=S+'_cb'))
 p='ui/units/minspec_portholes/'+u+'.png';(O/p).parent.mkdir(parents=True,exist_ok=True)
 with Image.open(O/'renders'/(S+'_white_head.png')) as im:im.resize((256,256),Image.Resampling.LANCZOS).save(O/p)
 files.append(p)
for t in ['unit_description_historical_texts','unit_description_short_texts']:T[t].append(dict(key=U))
clone('character_skill_node_sets','key','wh3_main_skill_node_set_cth_alchemist',key=S+'_skills',agent_subtype_key=S,faction_key=F)
nodeby={r['key']:r for r in rows('character_skill_nodes')};alchemist_items=[r for r in rows('character_skill_node_set_items') if r['set']=='wh3_main_skill_node_set_cth_alchemist' and r['mod_disabled']=='false']
general=[nodeby[r['item']] for r in alchemist_items if nodeby[r['item']]['indent'] in ['0','5','6','8','99'] and '_mount_' not in nodeby[r['item']]['character_skill_key']]
light_items=[r for r in rows('character_skill_node_set_items') if r['set']=='wh_main_skill_node_set_emp_light_wizard' and r['mod_disabled']=='false'];magic=[nodeby[r['item']] for r in light_items if nodeby[r['item']]['indent'] in ['2','3'] and 'magic_' in nodeby[r['item']]['character_skill_key']];assert len(magic)==12
selected=general+magic;mapping={r['key']:S+'_node_'+str(i) for i,r in enumerate(selected)}
for n in selected:
 T['character_skill_nodes'].append(dict(n,key=mapping[n['key']],indent='2' if n in magic else n['indent']));T['character_skill_node_set_items'].append(dict(set=S+'_skills',item=mapping[n['key']],mod_disabled='false'))
for r in rows('character_skill_node_links'):
 if r['parent_key'] in mapping and r['child_key'] in mapping:T['character_skill_node_links'].append(dict(r,parent_key=mapping[r['parent_key']],child_key=mapping[r['child_key']]))
for r in rows('character_skill_nodes_skill_locks'):
 if r['character_skill_node'] in mapping:T['character_skill_nodes_skill_locks'].append(dict(r,character_skill_node=mapping[r['character_skill_node']]))
skills={r['character_skill_key'] for r in selected};assert not any('metal_' in k or 'metallurg' in k or 'alchemical' in k for k in skills)
support_abilities=set()
for r in rows('character_skill_level_to_effects_junctions'):
 if r['character_skill_key'] in skills:
  support_abilities.update(b['unit_ability'] for b in rows('effect_bonus_value_unit_ability_junctions') if b['effect']==r['effect_key'] and b['bonus_value_id']=='enable')
for u,_ in units:
 present={r['ability'] for r in T['land_units_to_unit_abilites_junctions'] if r['land_unit']==u}
 T['land_units_to_unit_abilites_junctions'].extend(dict(ability=a,land_unit=u,culture='*') for a in sorted(support_abilities-present))
# Private native mount grants retain Alchemist's original unlock levels/effects.
for suffix,dunit in [('warhorse','wh3_main_cth_cha_alchemist_1'),('sky_lantern','wh3_main_cth_cha_alchemist_2')]:
 anc_donor=next(r for r in rows('ancillaries') if r['provided_bodyguard_unit']==dunit);old=next(r['skill'] for r in rows('character_skill_level_to_ancillaries_junctions') if r['granted_ancillary']==anc_donor['key']);sk=S+'_mount_'+suffix;anc=sk+'_ancillary'
 clone('character_skills','key',old,key=sk)
 for t,field in [('character_skill_level_details','skill_key'),('character_skills_to_level_reached_criterias','character_skill'),('character_skill_level_to_effects_junctions','character_skill_key')]:T[t].extend(dict(r,**{field:sk}) for r in rows(t) if r[field]==old)
 T['ancillaries'].append(dict(anc_donor,key=anc,provided_bodyguard_unit=S+'_'+suffix));clone('ancillary_info','ancillary',anc_donor['key'],ancillary=anc);T['ancillaries_included_agent_subtypes'].append(dict(agent_subtype=S,ancillary=anc));T['character_skill_level_to_ancillaries_junctions'].append(dict(skill=sk,level='1',granted_ancillary=anc))
 n=next(dict(nodeby[r['item']]) for r in alchemist_items if nodeby[r['item']]['character_skill_key']==old);n.update(key=sk+'_node',character_skill_key=sk);T['character_skill_nodes'].append(n);T['character_skill_node_set_items'].append(dict(set=S+'_skills',item=n['key'],mod_disabled='false'))
 source_cb=next(r for r in rows('units_custom_battle_mounts') if r['base_unit']==du and r['mounted_unit']==dunit);T['units_custom_battle_mounts'].append(dict(source_cb,base_unit=U,mounted_unit=S+'_'+suffix))
 title='Warhorse' if suffix=='warhorse' else 'Sky Lantern';loc.update({'ancillaries_onscreen_name_'+anc:title,'ancillaries_colour_text_'+anc:'A mount trained for the hidden court.','units_custom_battle_mounts_mount_name_'+U+S+'_'+suffix:title,'units_custom_battle_mounts_localised_description_'+U+S+'_'+suffix:'Mount: '+title+'.'})
for i,m in enumerate(M['models']):
 key=m['key'];art=key+'_art';aid=str(1986113000+i)
 assert not any(r['id']==aid for r in rows('campaign_character_arts'));clone('variants','variant_name','wh3_main_cth_cha_alchemist_campaign_01',variant_name=key,variant_filename=key,scale='1.0000',scale_variation='0.0000',low_poly_filename='',super_low_poly_filename='')
 clone('agent_uniforms','uniform_name','wh3_main_uniform_cth_alchemist_01',uniform_name=key+'_uniform',filename=key,battle_filename=key,campaign_porthole_filename=key)
 clone('campaign_character_art_sets','art_set_id','wh3_main_art_set_cth_alchemist_01',art_set_id=art,agent_subtype=S,faction=F)
 clone('campaign_character_arts','id','902452890',id=aid,art_set_id=art,uniform=key+'_uniform')
 for folder,kind in [('units','body'),('portholes','head')]:
  p='ui/portraits/'+folder+'/no_culture/'+key+'_0.png';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'renders'/(key+'_'+kind+'.png'),O/p);files.append(p)
  settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text());entry=settings['entries'][0];entry['id']=art;entry['variants'][0].update(filename=key,file_diffuse=p,faction_leader=False);jp=O/('portrait-'+key+'-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2));p='ui/portraits/'+folder+'/portrait_settings__'+key+'.bin';cli('portrait-settings','from-json','-j',jp,'-b',O/p);files.append(p)
p='ui/units/icons/'+S+'.png';(O/p).parent.mkdir(parents=True,exist_ok=True)
with Image.open(O/'renders'/(S+'_white_body.png')) as im:im.resize((104,208),Image.Resampling.LANCZOS).save(O/p)
files.append(p)
for number,source,text in [('1986113010','1087565330','Moonveil Adept'),('1986113011','1015096215','')]:
 assert not any(r['id']==number for r in rows('names'));clone('names','id',source,id=number,gender='f',frequency='0');loc['names_name_'+number]=text
clone('battle_set_piece_armies_characters','character_name',du,character_name=S+'_cb',unit_type=U,agent_type='engineer',agent_subtype=S,portrait='ui/portraits/portholes/no_culture/'+S+'_white_0.png',character_model='1986113000',forename='1986113010',surname='1986113011',male='false',magic_lore='wh_main_lore_light',skillset=S+'_cb_spells',character_level='40')
T['battle_set_piece_armies_characters_skillsets'].append(dict(key=S+'_cb_spells'));spell_skills=[r['character_skill_key'] for r in magic if 'magic_light_' in r['character_skill_key']]
T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(skill=k,skillset_key=S+'_cb_spells',sort_order=str(i)) for i,k in enumerate(spell_skills))
loc.update({'agent_subtypes_onscreen_name_override_'+S:'Moonveil Adept','agent_recruitment_categories_onscreen_name_'+S:'Moonveil Adept','agent_recruitment_categories_onscreen_description_'+S:'A guardian of the hidden paths, wielding light to shield allies and bind enemies.','unit_description_short_texts_text_'+U:'Support Wizard','unit_description_historical_texts_text_'+U:'Trained in the hidden sanctuaries of the moon, these adepts shield their companions and confound enemies with veils of radiant light.','effects_description_'+effect:'Enables recruitment of Moonveil Adepts (shares Alchemist capacity)'})
assert one('ui_unit_groupings','key','wizard_light')['parent_group']=='heroes_agents';assert all(r['general_unit']=='false' for r in T['units_custom_battle_permissions']) and len(T['units_custom_battle_permissions'])==3
for u,d in units:
 for t,key,ignored in [('main_units','unit',{'unit','land_unit','ui_unit_group_land'}),('land_units','key',{'key','historical_description_text','short_description_text'})]:
  actual=next(r for r in T[t] if r[key]==u);source=one(t,key,d);assert {k:v for k,v in actual.items() if k not in ignored}=={k:v for k,v in source.items() if k not in ignored}
nodekeys={r['key'] for r in T['character_skill_nodes']};assert all(r['parent_key'] in nodekeys and r['child_key'] in nodekeys for r in T['character_skill_node_links'])
for n in T['character_skill_nodes']:assert sum(r['child_key']==n['key'] and r['link_type']=='SUBSET_REQUIRED' for r in T['character_skill_node_links'])>=int(n['required_num_parents'])
for t,rs in T.items():
 if not rs:continue
 h,meta=copy.deepcopy(native(t)[0]);p='db/'+t+'_tables/zzzz_mc_moonveil';meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(set(r)==set(h) for r in rs),(t,set(rs[0])-set(h))
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 dbfiles.append(p)
p='text/db/mc_moonveil.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(v.isascii() for v in loc.values())
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
dbfiles.append(p);files=sorted(set(files));before=unpack(BASE);assert not set(files+dbfiles)&set(before);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
for i in range(0,len(files),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files[i:i+20]])
after=unpack(PACK);assert set(after)==set(before)|set(files+dbfiles) and all(after[p]==b for p,b in before.items())
check=R/'reference/local/moonveil-v24-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,existing_payloads_unchanged=True,subtype=S,regular_hero=True,agent_type='engineer',shared_alchemist_capacity=True,additional_capacity=0,appearance_variants=4,mounts=2,hero_ui_category_verified=True,native_light_spells=True,alchemy_skills_omitted=True,native_alchemist_stats_costs_exact=True,skill_prerequisites_reachable=True,model_animation_samples=review['samples'],native_or_workshop_modified=False,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2));assert not blocking
