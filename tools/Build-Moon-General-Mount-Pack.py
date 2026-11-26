"""V21 restores working mount branches without changing approved foot appearances."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess,sys,re
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v21-mounts';N=R/'reference/local/lord-vanilla/db';D=R/'reference/local/deer-wwd/base/db'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v20_two_generals.pack';PACK=O/'mc_moonshadow_heroes_v21_general_mounts.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='03a7f8819c51c1ff913b1b8e11b1f3359436bfe49fc7d262ba0fb8100fa9686f'
B=R/'reference/local/moon-generals-v20-roundtrip';T=defaultdict(list);cache={};files=[];dbfiles=[];loc={};specs=[]
def rows(t,source='native'):
 k=(t,source)
 if k not in cache:
  ps=[N/(t+'_tables/data__.tsv')] if source=='native' else list((D/(t+'_tables')).glob('*.tsv')) if source=='donor' else [B/('db/'+t+'_tables/zzzz_mc_moon_generals.tsv')]
  cache[k]=[r for p in ps for r in read(p)[1]]
 return cache[k]
def one(t,k,v,source='native'):
 a=[r for r in rows(t,source) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
assets=json.loads((O/'mount-assets.json').read_text());files+=assets['files'];assert sha(assets['source'])==assets['source_sha256']
for m in assets['models']:
 key=m['key'];old=m['donor'];T['variants'].append(dict(m['variant'],variant_name=key,variant_filename=key,tech_folder='',low_poly_filename='',super_low_poly_filename=''))
 T['mounts'].append(dict(one('mounts','key',old,'donor'),key=key,variant=key))
 T['campaign_mounts'].append(dict(one('campaign_mounts','model',old,'donor'),model=key,variant=key))
 animation=T['mounts'][-1]['animation'];one('battle_animations_table','key',animation)
 if not any(r['battle_animations_table']==animation and r['culture_pack']=='wh3_main_cth_cathay' for r in rows('culture_to_battle_animation_tables')):T['culture_to_battle_animation_tables'].append(dict(battle_animations_table=animation,culture_pack='wh3_main_cth_cathay'))
profiles=[
 ('mc_assault_general','warhorse','White Warhorse','wh3_deer24_guanshan_horse','wh3_dlc24_skill_cth_celestial_general_mount_warhorse',4,'mc_assault_warhorse'),
 ('mc_assault_general','great_stag','Great Stag','wh3_deer24_guanshan1','wh2_twa02_skill_wef_glade_captain_mount_great_stag',14,'mc_assault_great_stag'),
 ('mc_bastion_general','warhorse','Warhorse','wh3_dlc24_cth_cha_celestial_general_yang_cathayan_horse','wh3_dlc24_skill_cth_celestial_general_mount_warhorse',4,None),
 ('mc_bastion_general','longma','Jade Longma','wh3_dlc24_cth_cha_celestial_general_yang_longma','wh3_dlc24_skill_cth_celestial_general_mount_longma',9,None),
 ('mc_bastion_general','celestial_lion','Celestial Lion','wh3_dlc24_cth_cha_celestial_general_yang_celestial_lion','wh3_dlc24_skill_cth_celestial_general_mount_celestial_lion',15,None)]
bins={}
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
 b=p.read_bytes();pos=4
 for _ in range(struct.unpack_from('<I',b)[0]):
  n=struct.unpack_from('<H',b,pos)[0];pos+=2;name=b[pos:pos+n].decode();pos+=n;z=struct.unpack_from('<I',b,pos)[0];pos+=4;bins[Path(name).stem]=b[pos:pos+z];pos+=z
for s,suffix,name,donor,skill_donor,rank,mount_key in profiles:
 assault=s=='mc_assault_general';source='donor' if assault else 'native';u=s+'_'+suffix;foot=s+'_human';sk=s+'_mount_'+suffix;anc=sk+'_ancillary'
 dland=one('land_units','key',donor,source);dmain=one('main_units','unit',donor,source);base=one('land_units','key',foot,'base');main=one('main_units','unit',foot,'base')
 battle=dland['man_animation'];assert battle in bins;assert one('battle_animations_table','key',battle)['skeleton']==('humanoid01b' if assault else 'humanoid01e')
 comparison='wh2_twa02_wef_cha_glade_captain_3' if suffix=='great_stag' else 'wh3_dlc24_cth_cha_celestial_general_yang_cathayan_horse' if assault else donor
 compbase='wh2_twa02_wef_cha_glade_captain_0' if suffix=='great_stag' else 'wh3_dlc24_cth_cha_celestial_general_yang';cm=one('main_units','unit',comparison);cb=one('main_units','unit',compbase)
 for field in ['recruitment_cost','upkeep_cost','multiplayer_cost']:main[field]=str(int(main[field])+int(cm[field])-int(cb[field]))
 main.update(unit=u,land_unit=u,mount=mount_key or dmain['mount'],weight=cm['weight']);T['main_units'].append(main)
 dl=one('land_units','key',comparison);bl=one('land_units','key',compbase)
 for field in ['bonus_hit_points','charge_bonus','melee_attack','melee_defence']:base[field]=str(int(base[field])+int(dl[field])-int(bl[field]))
 for field in ['attribute_group','spacing','ground_stat_effect_group','ai_usage_group','capture_tier','key_building_capture_tier','score_capture_tier']:base[field]=dl[field]
 base['category']=dl['category']
 if assault and suffix=='great_stag':
  horse=one('land_units','key','wh3_dlc24_cth_cha_celestial_general_yang_cathayan_horse');group=u+'_attributes'
  T['unit_attributes_groups'].append(dict(one('unit_attributes_groups','group_name',horse['attribute_group']),group_name=group))
  T['unit_attributes_to_groups_junctions'].extend(dict(r,attribute_group=group) for r in rows('unit_attributes_to_groups_junctions') if r['attribute_group']==horse['attribute_group'])
  T['unit_attributes_to_groups_junctions'].append(dict(attribute='causes_fear',attribute_group=group))
  base.update(attribute_group=group,ai_usage_group=horse['ai_usage_group'],ground_stat_effect_group=horse['ground_stat_effect_group'])
 if not assault:base['primary_melee_weapon']=dl['primary_melee_weapon']
 base.update(key=u,mount=mount_key or dland['mount'],num_mounts='1',man_animation=battle,can_brace=dland['can_brace']);T['land_units'].append(base)
 variant=s+'_mounted' if assault else s
 T['unit_variants'].append(dict(one('unit_variants','unit',foot,'base'),unit=u,variant=variant))
 T['units_to_groupings_military_permissions'].append(dict(unit=u,military_group='wh3_main_cth'))
 for t,field in [('unit_set_to_unit_junctions','unit_record'),('land_units_to_unit_abilites_junctions','land_unit')]:T[t].extend(dict(r,**{field:u}) for r in rows(t,'base') if r[field]==foot)
 campaign=next(r for r in rows('campaign_character_arts','base') if r['art_set_id']==s+'_art')['land_animation']
 override=next(r for r in rows('campaign_mount_animation_set_overrides',source) if r['mount_unit']==donor and r['character_animation_set']==campaign)
 T['campaign_mount_animation_set_overrides'].append(dict(override,mount_unit=u))
 if not any(r['battle_animations_table']==battle and r['culture_pack']=='wh3_main_cth_cathay' for r in rows('culture_to_battle_animation_tables')):T['culture_to_battle_animation_tables'].append(dict(battle_animations_table=battle,culture_pack='wh3_main_cth_cathay'))
 # Private skills grant private mounts, never the vanilla CG bodyguard unit.
 T['character_skills'].append(dict(one('character_skills','key',skill_donor),key=sk,localised_name=name,localised_description='Allows this general to ride a '+name+'.'))
 detail=one('character_skill_level_details','skill_key',skill_donor);T['character_skill_level_details'].append(dict(detail,skill_key=sk,unlocked_at_rank=str(rank)))
 criteria=one('character_skills_to_level_reached_criterias','character_skill',skill_donor);T['character_skills_to_level_reached_criterias'].append(dict(criteria,character_skill=sk,character_level=str(rank)))
 T['character_skill_level_to_effects_junctions'].extend(dict(r,character_skill_key=sk) for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==skill_donor)
 grant=one('character_skill_level_to_ancillaries_junctions','skill',skill_donor);T['character_skill_level_to_ancillaries_junctions'].append(dict(grant,skill=sk,granted_ancillary=anc))
 T['ancillaries'].append(dict(one('ancillaries','key',grant['granted_ancillary']),key=anc,provided_bodyguard_unit=u,faction_set='all'))
 T['ancillary_info'].append(dict(one('ancillary_info','ancillary',grant['granted_ancillary']),ancillary=anc))
 T['ancillaries_included_agent_subtypes'].append(dict(agent_subtype=s,ancillary=anc))
 node=next(dict(r) for r in rows('character_skill_nodes') if r['character_skill_key']==skill_donor);node.update(key=sk+'_node',character_skill_key=sk,indent='0',tier=str(0 if suffix=='warhorse' else 1 if suffix in ['great_stag','longma'] else 2),required_num_parents='0');T['character_skill_nodes'].append(node);T['character_skill_node_set_items'].append(dict(set=s+'_skills',item=node['key'],mod_disabled='false'))
 perm=one('units_custom_battle_permissions','unit',foot,'base');T['units_custom_battle_permissions'].append(dict(perm,unit=u));icon=one('ancillary_types','type',T['ancillaries'][-1]['type'])['ui_icon'];T['units_custom_battle_mounts'].append(dict(base_unit=foot,mounted_unit=u,icon_name=icon))
 loc.update({'character_skills_localised_name_'+sk:name,'character_skills_localised_description_'+sk:'Mount: '+name+'.','ancillaries_onscreen_name_'+anc:name,'ancillaries_colour_text_'+anc:'A mount trained to carry a general of the hidden court.','units_custom_battle_mounts_mount_name_'+foot+u:name,'units_custom_battle_mounts_localised_description_'+foot+u:'Mount: '+name+'.'})
 p='ui/units/minspec_portholes/'+u+'.png';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'build/moon-generals-v20/ui/units/minspec_portholes'/(foot+'.png'),O/p);files.append(p)
 # Select actual mounted idle/run/attack clips from compiled native profiles.
 paths=sorted(set(x.decode() for x in re.findall(rb'animations/[a-zA-Z0-9_./ -]+?\.anim',bins[battle])))
 prefix='animations/battle/humanoid01b/rider/'+('great_stag01/spear_bow/' if suffix=='great_stag' else 'horse01/spear_and_shield/') if assault else 'animations/battle/humanoid01e/rider/'+('bigcat02/celestial_general/' if suffix=='celestial_lion' else 'warhorse/celestial_general/')
 candidates=[p for p in paths if p.startswith(prefix)]
 selected=[]
 for tag in ['stand','run','attack']:
  options=[p for p in candidates if tag in Path(p).stem and not any(x in p for x in ['death','shoot','idle','fly','jump','moving','to_stand'])]
  if not options and tag=='run':options=[p for p in candidates if '/locomotion/' in p and 'walk' in Path(p).stem and 'death' not in p]
  if not options and tag=='run':options=[p for p in paths if '/rider/' in p and '/locomotion/' in p and ('run' in Path(p).stem or 'walk' in Path(p).stem) and not any(x in p for x in ['death','fly','moving'])]
  assert options,(battle,tag);selected.append(options[0])
 specs.append(dict(subtype=s,unit=u,mount=suffix,name=name,rank=rank,battle=battle,campaign=override['rider_animation_set'],clips=selected,attachment='be_prop_1' if assault else 'weapon_1',variant=variant))
# One shared mounted Assault body/weapon variant, matching the source prop slot.
s='mc_assault_general';T['variants'].append(dict(one('variants','variant_name',s,'base'),variant_name=s+'_mounted',variant_filename=s+'_mounted',mount_scale='1.1500'))
body=R/'build/moon-generals-v20/variantmeshes/variantmeshdefinitions/mc_assault_general.variantmeshdefinition';tree=ET.parse(body);tree.find("./SLOT[@name='weapon_1']").set('attach_point','be_prop_1');p='variantmeshes/variantmeshdefinitions/'+s+'_mounted.variantmeshdefinition';(O/p).parent.mkdir(parents=True,exist_ok=True);tree.write(O/p,encoding='utf8');files.append(p)
for t,rs in T.items():
 h,meta=copy.deepcopy(read(N/(t+'_tables/data__.tsv'))[0]);p='db/'+t+'_tables/zzzz_mc_moon_general_mounts';meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(set(r)==set(h) for r in rs),(t,set(rs[0])-set(h))
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 dbfiles.append(p)
p='text/db/mc_moon_general_mounts.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(v.isascii() for v in loc.values())
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
dbfiles.append(p);(O/'mount-models.json').write_text(json.dumps(dict(models=specs,files=files),indent=2))
if '--prepare-only' in sys.argv:print('MOUNT_DB_PREPARED',len(specs));sys.exit(0)
review=json.loads((O/'animation-review.json').read_text());assert review['status']=='passed' and review['models']==5
before=unpack(BASE);assert not set(files+dbfiles)&set(before);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
for i in range(0,len(files),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files[i:i+20]])
after=unpack(PACK);assert set(after)==set(before)|set(files+dbfiles) and all(after[p]==b for p,b in before.items())
check=R/'reference/local/moon-generals-v21-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,existing_payloads_unchanged=True,roundtrip_passed=True,native_compiled_lookups_verified=True,mounts=5,mount_skills=5,mount_ancillaries=5,regular_lords=True,foot_only=False,deployed=False,runtime_verified=False,models=specs)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in v if k!='models'},indent=2));assert not blocking
