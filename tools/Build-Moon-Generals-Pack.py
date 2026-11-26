"""Private v20: approved two ordinary foot lords; preserve all v19 payloads."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v20';N=R/'reference/local/lord-vanilla/db'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v19_hero_category.pack';PACK=O/'mc_moonshadow_heroes_v20_two_generals.pack';F='cr_cth_agents_of_the_moon'
assert not PACK.exists(),'Preserve completed candidate'
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='2ee1d5ce81a64ab5979ab0b4d3201492e346d3f3d034d99a0a945401076bed33'
M=json.loads((O/'export-report.json').read_text());review=json.loads((O/'model-review.json').read_text());assert review['status']=='passed' and review['samples']==60
assert sha(Path(M['source']))==M['source_sha256']
T=defaultdict(list);cache={};loc={};files=[];dbfiles=[];unit='wh3_dlc24_cth_cha_celestial_general_yang';native_sub='wh3_dlc24_cth_celestial_general_'
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t]
def rows(t):return native(t)[1]
def one(t,k,v):
 a=[r for r in rows(t) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def clone(t,k,v,**changes):
 r=dict(one(t,k,v),**changes);T[t].append(r);return r
def extend_matching(t,field,old,new):T[t].extend(dict(r,**{field:new}) for r in rows(t) if r[field]==old)
# Verify real compiled native lookups include every previewed battle clip.
spec=json.loads((R/'build/moon-generals-preview/animation-review-clips.json').read_text());compiled={}
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
 b=p.read_bytes();pos=4
 for _ in range(struct.unpack_from('<I',b)[0]):
  length=struct.unpack_from('<H',b,pos)[0];pos+=2;name=b[pos:pos+length].decode();pos+=length;size=struct.unpack_from('<I',b,pos)[0];pos+=4;compiled[name]=b[pos:pos+size];pos+=size
profiles=[('Assault','yang','hu1b_elf_2handed_spear','cam_hu1b_bretonnian_staff_and_sword'),('Bastion','yin','hu1e_dlc24_celestial_general','cam_lord_hu1e_dlc24_celestial_general')]
for i,(m,(label,harmony,battle,campaign)) in enumerate(zip(M['models'],profiles)):
 s=m['key'];u=s+'_human';name=label+' General';donor=native_sub+harmony;art=s+'_art';art_id=str(1986112800+i);male='false' if i==0 else 'true'
 data=compiled['animations/database/battle/bin/'+battle+'.bin'];assert all(x['path'].encode() in data for x in spec['clips'][label])
 assert one('battle_animations_table','key',battle)['skeleton']==m['skeleton']
 assert any(r['land_animation']==campaign for r in rows('campaign_character_arts'))
 assert not any(r['key']==s for r in rows('agent_subtypes')) and not any(r['id']==art_id for r in rows('campaign_character_arts'))
 voice='wh3_main_vo_actor_Cathay_Alchemist' if i==0 else 'wh3_dlc24_vo_actor_Cathay_Celestial_General'
 clone('agent_subtypes','key',donor,key=s,associated_unit_override=u,recruitment_category=s,has_female_name='true' if i==0 else 'false',audio_voiceover_actor_group=voice)
 clone('agent_recruitment_categories','key','wh3_dlc24_cth_celestial_general',key=s,order=str(3+i))
 clone('main_units','unit',unit,unit=u,land_unit=u,audio_voiceover_actor_group=voice)
 stats=dict(armour='wh2_main_heavy_metal_90',melee_attack='65',melee_defence='35',charge_bonus='45') if i==0 else dict(armour='wh2_main_heavy_metal_110',melee_attack='55',melee_defence='50',charge_bonus='20')
 weapon=s+'_weapon'
 clone('melee_weapons','key','wh3_dlc24_cth_celestial_general_hammer',key=weapon,melee_weapon_type='spear',audio_type='spear')
 clone('land_units','key',unit,key=u,man_animation=battle,is_male=male,historical_description_text=u,short_description_text=u,primary_melee_weapon=weapon,**stats)
 for t in ['unit_description_historical_texts','unit_description_short_texts']:T[t].append(dict(key=u))
 uv=next(r for r in rows('unit_variants') if r['unit']==unit);T['unit_variants'].append(dict(uv,unit=u,name=u,variant=s,unit_card=s))
 clone('variants','variant_name','wh3_dlc24_cth_cha_celestial_general',variant_name=s,variant_filename=s,scale='1.1500',scale_variation='0.0000')
 clone('agent_uniforms','uniform_name','wh3_dlc24_uniform_cth_celestial_general_01',uniform_name=s+'_uniform',filename=s,battle_filename=s,campaign_porthole_filename=s)
 clone('campaign_character_art_sets','art_set_id','wh3_dlc24_cth_celestial_general_yang_01',art_set_id=art,agent_subtype=s,faction=F,is_male=male)
 clone('campaign_character_arts','id','1588752094',id=art_id,art_set_id=art,uniform=s+'_uniform',land_animation=campaign)
 T['faction_agent_permitted_subtypes'].append(dict(agent='general',faction=F,subtype=s,mod_disabled='false'))
 for t,field,old,new in [('land_units_to_unit_abilites_junctions','land_unit',unit,u),('unit_set_to_unit_junctions','unit_record',unit,u),('campaign_group_member_criteria_agent_subtypes','agent_subtype',donor,s),('effect_bonus_value_agent_subtype_junctions','subtype',donor,s)]:
  # Schema field names are taken from native TSV, including ownership junctions.
  if field not in native(t)[0][0]:
   field=next(k for k in native(t)[0][0] if any(r[k]==old for r in rows(t)))
  extend_matching(t,field,old,new)
 T['units_to_groupings_military_permissions'].append(dict(unit=u,military_group='wh3_main_cth'))
 # Ensure native 01b clips are available in Cathay's culture pack.
 if not any(r['battle_animations_table']==battle and r['culture_pack']=='wh3_main_cth_cathay' for r in rows('culture_to_battle_animation_tables')):
  T['culture_to_battle_animation_tables'].append(dict(battle_animations_table=battle,culture_pack='wh3_main_cth_cathay'))
 skillset='wh3_dlc24_skill_node_set_cth_celestial_general_'+harmony
 clone('character_skill_node_sets','key',skillset,key=s+'_skills',agent_subtype_key=s,faction_key=F)
 items=[r for r in rows('character_skill_node_set_items') if r['set']==skillset and r['mod_disabled']=='false'];nodes={r['key']:r for r in rows('character_skill_nodes')}
 selected=[nodes[r['item']] for r in items if '_mount_' not in nodes[r['item']]['character_skill_key']];mapping={r['key']:s+'_node_'+str(j) for j,r in enumerate(selected)}
 assert len(items)-len(selected)==3
 for node in selected:
  T['character_skill_nodes'].append(dict(node,key=mapping[node['key']]));T['character_skill_node_set_items'].append(dict(set=s+'_skills',item=mapping[node['key']],mod_disabled='false'))
 for link in rows('character_skill_node_links'):
  if link['parent_key'] in mapping and link['child_key'] in mapping:T['character_skill_node_links'].append(dict(link,parent_key=mapping[link['parent_key']],child_key=mapping[link['child_key']]))
 for lock in rows('character_skill_nodes_skill_locks'):
  if lock['character_skill_node'] in mapping:T['character_skill_nodes_skill_locks'].append(dict(lock,character_skill_node=mapping[lock['character_skill_node']]))
 portrait='ui/portraits/portholes/no_culture/'+s+'_0.png';char=s+'_cb';first=str(1986112810+2*i);last=str(1986112811+2*i)
 for number,source,text in [(first,'1087565330',name),(last,'1015096215','')]:
  assert not any(r['id']==number for r in rows('names'));clone('names','id',source,id=number,frequency='0',gender='f' if i==0 else 'm');loc['names_name_'+number]=text
 clone('battle_set_piece_armies_characters','character_name',unit,character_name=char,unit_type=u,agent_subtype=s,character_model=art_id,portrait=portrait,forename=first,surname=last,male=male,character_level='40',skillset=s+'_cb_skills')
 donor_permission=next(r for r in rows('units_custom_battle_permissions') if r['unit']==unit and r['faction']=='wh3_main_cth_cathay_mp')
 T['units_custom_battle_permissions'].append(dict(donor_permission,unit=u,set_piece_character=char,general_portrait=portrait,general_uniform=s+'_uniform'))
 T['battle_set_piece_armies_characters_skillsets'].append(dict(key=s+'_cb_skills'))
 # Explicit CB active abilities, sourced from the actual native personal tree.
 skills=[r['character_skill_key'] for r in selected if r['indent'] in ('1','2')]
 T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(skill=k,skillset_key=s+'_cb_skills',sort_order=str(j)) for j,k in enumerate(dict.fromkeys(skills)))
 role='A polearm commander who breaks enemy formations and leads the assault.' if i==0 else 'An armoured commander who anchors the line and holds the army together.'
 loc.update({'agent_subtypes_onscreen_name_override_'+s:name,'land_units_onscreen_name_'+u:name,'agent_recruitment_categories_onscreen_name_'+s:name,'agent_recruitment_categories_onscreen_description_'+s:role,'unit_description_short_texts_text_'+u:'Melee Lord','unit_description_historical_texts_text_'+u:role+' A general of the hidden court of the moon.'})
 root=ET.Element('VARIANT_MESH');slot=ET.SubElement(root,'SLOT',name='body');node=ET.SubElement(slot,'VARIANT_MESH',model=m['body']);ET.SubElement(node,'META_DATA').text='audio_armour_type:heavy_metal'
 slot=ET.SubElement(root,'SLOT',name='weapon_1',attach_point=m['attachment']);node=ET.SubElement(slot,'VARIANT_MESH',model=m['weapon']);ET.SubElement(node,'META_DATA').text='equipment'
 p='variantmeshes/variantmeshdefinitions/'+s+'.variantmeshdefinition';(O/p).parent.mkdir(parents=True,exist_ok=True);ET.indent(root);(O/p).write_bytes(ET.tostring(root,encoding='utf8'));files.append(p)
 for folder,kind in [('units','body'),('portholes','head')]:
  p='ui/portraits/'+folder+'/no_culture/'+s+'_0.png';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'renders'/(s+'_'+kind+'.png'),O/p);files.append(p)
  settings=json.loads((R/('build/huyen-ve-v17-campaign/portrait-donor-'+folder+'.json')).read_text());entry=settings['entries'][0];entry['id']=art;entry['variants'][0].update(filename=s,file_diffuse=p,faction_leader=False)
  jp=O/('portrait-'+s+'-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2));p='ui/portraits/'+folder+'/portrait_settings__'+s+'.bin';cli('portrait-settings','from-json','-j',jp,'-b',O/p);files.append(p)
 for p,kind,size in [('ui/units/icons/'+s+'.png','body',(104,208)),('ui/units/minspec_portholes/'+u+'.png','head',(256,256))]:
  (O/p).parent.mkdir(parents=True,exist_ok=True)
  with Image.open(O/'renders'/(s+'_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(O/p)
  files.append(p)
 files.extend(p.relative_to(O).as_posix() for p in (O/Path(m['body']).parent).rglob('*') if p.suffix in ('.dds','.rigid_model_v2'))
# Replace only Agents of the Moon's native CG recruitment permission.
for suffix in ('yang','yin'):T['faction_agent_permitted_subtypes'].append(dict(agent='general',faction=F,subtype=native_sub+suffix,mod_disabled='true'))
for t,rs in T.items():
 if not rs:continue
 h,metadata=copy.deepcopy(native(t)[0]);p='db/'+t+'_tables/zzzz_mc_moon_generals';metadata[0]=';'.join(metadata[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 assert all(set(r)==set(h) for r in rs),(t,set(rs[0])-set(h))
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,metadata]+[[r[k] for k in h] for r in rs])
 dbfiles.append(p)
assert all(v.isascii() for v in loc.values())
p='text/db/mc_moon_generals.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
dbfiles.append(p);files=sorted(set(files));before=unpack(BASE);assert not set(files+dbfiles)&set(before)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
for start in range(0,len(files),20):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files[start:start+20]])
after=unpack(PACK);assert set(after)==set(before)|set(files+dbfiles);assert all(after[p]==b for p,b in before.items())
check=R/'reference/local/moon-generals-v20-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,existing_payloads_unchanged=True,roundtrip_passed=True,animation_samples=review['samples'],native_compiled_lookups_verified=True,models=[m['key'] for m in M['models']],faction=F,regular_lords=True,foot_only=True,custom_battle_faction='wh3_main_cth_cathay_mp',native_cg_recruitment_replaced_only_for_moon=True,new_files=files+dbfiles,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in v if k!='new_files'},indent=2));assert not blocking
