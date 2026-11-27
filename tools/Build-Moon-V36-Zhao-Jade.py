"""Build a new candidate from immutable recovered v35 + approved Jade v2.

Default prepares DB/loc/manifest only. --build requires completed asset review.
"""
import argparse,collections,copy,csv,hashlib,json,re,shutil,struct,subprocess,unicodedata
from pathlib import Path

R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-v36-zhao-jade';O.mkdir(parents=True,exist_ok=True)
B=R/'reference/local/recovered-v35-audit';N=R/'reference/local/zhao-shugengan-comparison-20261126/native/db'
BASE=R/'mc_moonshadow_heroes_v35_moon_arts.pack';JADE=R/'build/moon-jade-reskin-v2/mc_moon_jade_warriors_reskin_v2_family.pack'
PACK=O/'mc_moonshadow_heroes_v36_zhao_jade.pack';P='mc_zhao_v36';S='mc_mooncourt_lord';F='cr_cth_agents_of_the_moon'
EXPECTED='109bb96662d68e2c0054b3fb17d5d6959fe227b620db872d9f2dce0bb9c4b37e'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(BASE)==EXPECTED
assert sha(JADE)=='9d711a7f571501f3c67a80b4f6d68da1b453f2a20d29c7e8e8248ddb68ba3ee1'
def read(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
cache={}
def native(t):
 if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
 return cache[t][1]
def one(t,k,v):
 a=[r for r in native(t) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def base(t):return [r for f in (B/'db'/(t+'_tables')).glob('*.tsv') for r in read(f)[1]]
T=collections.defaultdict(list);loc={};donors={};skill_names={};files={};new_assets={}
english={r['key']:r['text'] for f in (R/'reference/local/recovered-v35-native/text').rglob('*.tsv') for r in read(f)[1]}
def text(k,depth=0):
 assert depth<12
 return re.sub(r'\{\{tr:([^}]+)\}\}',lambda m:text(m[1],depth+1),english.get(k,''))
def ascii(s):return unicodedata.normalize('NFKD',s.replace('\u2019',"'").replace('\u2013','-').replace('\u2014','-').replace('\r','').replace('\n','\\n').replace('\t',' ')).encode('ascii','ignore').decode()
def label(kind,key,source,fallback=''):loc[kind+'_'+key]=ascii(text(kind+'_'+source) or fallback)
def add(t,r):T[t].append(r);return r
def clone_skill(old,key,name,max_level=None,rank=None):
 s=one('character_skills','key',old);s.update(key=key,localised_name=name,is_background_skill='false',is_female_only_background_skill='false',is_male_only_background_skill='false',background_weighting='0.0000')
 if rank is not None:s['unlocked_at_rank']=str(rank)
 add('character_skills',s);donors[key]=old;skill_names[key]=name
 loc['character_skills_localised_name_'+key]=name;label('character_skills_localised_description',key,old,s['localised_description'])
 effects=[r for r in native('character_skill_level_to_effects_junctions') if r['character_skill_key']==old and (max_level is None or int(r['level'])<=max_level)]
 for r in effects:add('character_skill_level_to_effects_junctions',dict(r,character_skill_key=key))
 maximum=max_level or max([int(r['level']) for r in effects]+[1])
 h=one('character_skill_level_details','skill_key','wh2_main_skill_all_immortality_lord')
 native_details=[r for r in native('character_skill_level_details') if r['skill_key']==old]
 for level in range(1,maximum+1):
  detail=next((r for r in native_details if int(r['level'])==level),dict(h,unlocked_at_rank=s['unlocked_at_rank']))
  add('character_skill_level_details',dict(detail,skill_key=key,level=str(level),unlocked_at_rank=str(rank) if rank is not None else detail['unlocked_at_rank']))
 return key

spells=[('ember_bolt','Ember Bolt','wh_main_skill_all_magic_fire_01_fireball','wh_main_spell_fire_fireball'),
 ('lunar_snare','Lunar Snare','wh3_main_skill_cth_magic_yin_02_storm_of_shadows_lord','wh3_main_spell_yin_storm_of_shadows'),
 ('crashing_tide','Crashing Tide','wh2_dlc11_skill_all_magic_deep_02_tidecall_lord','wh2_dlc11_spell_deep_tidecall'),
 ('grasp_eclipse','Grasp of the Eclipse','wh3_main_skill_cth_magic_yin_07_talons_of_night_lord','wh3_main_spell_yin_talons_of_night'),
 ('sea_mist','Sea Mist','wh2_dlc11_skill_all_magic_deep_05_fog_of_the_damned_lord','wh2_dlc11_spell_deep_fog_of_the_damned'),
 ('flameforged_blade','Flameforged Blade','wh2_main_skill_all_magic_fire_03_flaming_sword_of_rhuin_lord','wh_main_spell_fire_flaming_sword_of_rhuin')]
for slug,name,sk,ab in spells:clone_skill(sk,P+'_skill_'+slug,name,2,0)
passive=clone_skill('wh3_main_skill_cth_magic_yin_05_power_of_yin',P+'_skill_passive','Lunar Ascendancy',1,0)
unique_names=['Mooncourt Defence','Threefold Attunement','Protection of the Mooncourt','Master of the Mooncourt','Resonant Presence','Empowered Mooncaster']
for i,name in enumerate(unique_names):clone_skill('wh3_main_skill_cth_dragon_blooded_shugengan_yin_unique_'+str(i),P+'_unique_'+str(i),name,1,12 if i==0 else 0)
clone_skill('wh3_main_skill_cth_all_unique_magic_resist',P+'_wind_harmony','Wind Harmony',1,6)
clone_skill('wh3_main_skill_cth_all_unique_missile_resist',P+'_ranged_discipline','Ranged Discipline',1,6)
for suffix in ['warhorse','jade_longma']:
 clone_skill('wh3_main_skill_cth_dragon_blooded_shugengan_lord_yin_mount_'+suffix,P+'_mount_'+suffix,'Warhorse' if suffix=='warhorse' else 'Jade Longma',1,0)
 add('character_skills_to_level_reached_criterias',dict(character_skill=P+'_mount_'+suffix,character_level='4' if suffix=='warhorse' else '14',upgrade_to_skill_level='1'))
bound=[]
for suffix,name,ab in [('metal','Metal Affinity','wh3_main_spell_bound_plague_of_rust'),('death','Death Affinity','wh3_main_spell_bound_spirit_leech'),('beasts','Beast Affinity','wh3_main_spell_bound_flock_of_doom'),('shadow','Shadow Affinity','wh3_main_spell_bound_enfeebling_foe')]:
 key=clone_skill('wh3_main_skill_cth_dragon_blooded_shugengan_self_'+suffix,P+'_bound_'+suffix,name,1,9);bound.append((key,ab))

# Private copies of precisely six spells, their overcasts and one lore passive.
ability_titles={ab:name for _,name,_,ab in spells};ability_titles['wh3_main_lore_passive_power_of_yin']='Lunar Ascendancy'
abilities=set(ability_titles)
for ab in list(abilities):
 parent=one('unit_abilities','key',ab)['overpower_option']
 if parent:abilities.add(parent);ability_titles[parent]=ability_titles[ab]+' (Upgraded)'
amap={ab:P+'_ability_'+str(i) for i,ab in enumerate(sorted(abilities))}
used={r['unique_id'] for r in native('unit_special_abilities')}|{r['unique_id'] for r in base('unit_special_abilities')}
aux=[('special_ability_to_special_ability_phase_junctions','special_ability'),('special_ability_to_auto_deactivate_flags','special_ability'),('special_ability_to_invalid_target_flags','special_ability'),('special_ability_to_invalid_usage_flags','special_ability'),('special_ability_to_recharge_contexts','special_ability'),('unit_abilities_to_additional_ui_effects_juncs','ability'),('special_ability_intensity_settings','ability'),('special_ability_behaviour_to_ability_junctions','ability'),('ability_to_ui_collection_junctions','ability'),('unit_special_ability_to_special_ability_toggle_groups_junctions','unit_special_ability')]
for i,(old,new) in enumerate(amap.items()):
 a=one('unit_abilities','key',old);add('unit_abilities',dict(a,key=new,overpower_option=amap.get(a['overpower_option'],a['overpower_option'])))
 a=one('unit_special_abilities','key',old);uid=str(1986130100+i);assert uid not in used
 add('unit_special_abilities',dict(a,key=new,unique_id=uid,parent_ability=amap.get(a['parent_ability'],a['parent_ability'])))
 for t,f in aux:
  for r in native(t):
   if r[f]==old:add(t,dict(r,**{f:new}))
 loc['unit_abilities_onscreen_name_'+new]=ability_titles[old];label('unit_abilities_tooltip_text',new,old)

bonus=native('effect_bonus_value_unit_ability_junctions');emap={}
for r in T['character_skill_level_to_effects_junctions']:
 old=r['effect_key'];matching=[b for b in bonus if b['effect']==old and b['unit_ability'] in amap]
 if matching:
  if old not in emap:
   new=P+'_effect_'+str(len(emap));emap[old]=new;add('effects',dict(one('effects','effect',old),effect=new));label('effects_description',new,old)
   # The unique Yin cooldown affects only the two Moon spells, never bound/Fire/Deep.
   if old=='wh3_main_effect_ability_cooldown_spells_yin':matching=[b for b in matching if any(w in b['unit_ability'] for w in ['storm_of_shadows','talons_of_night'])]
   assert matching,old
   for b in matching:add('effect_bonus_value_unit_ability_junctions',dict(b,effect=new,unit_ability=amap[b['unit_ability']]))
  r['effect_key']=emap[old]
# Native school modifiers continue to affect their own school subset only.
for b in bonus:
 if b['unit_ability'] in amap:add('effect_bonus_value_unit_ability_junctions',dict(b,unit_ability=amap[b['unit_ability']]))

foundation=P+'_foundation'
clone_skill('wh3_main_skill_cth_magic_yin_dummy_cloak_of_jet_storm_of_shadows',foundation,'Starting Moon Arts [HIDDEN]',1,0)
T['character_skill_level_to_effects_junctions']=[r for r in T['character_skill_level_to_effects_junctions'] if r['character_skill_key']!=foundation]
for slug in ['ember_bolt','lunar_snare']:
 ab=next(a for s,_,_,a in spells if s==slug);en=next(b for b in bonus if b['unit_ability']==ab and b['bonus_value_id']=='enable')
 new=P+'_foundation_enable_'+slug;add('effects',dict(one('effects','effect',en['effect']),effect=new));label('effects_description',new,en['effect'])
 add('effect_bonus_value_unit_ability_junctions',dict(en,effect=new,unit_ability=amap[ab]))
 add('character_skill_level_to_effects_junctions',dict(character_skill_key=foundation,effect_key=new,level='1',effect_scope='character_to_character_own',value='1.0000'))

# Fresh tree; all old tree memberships are replaced, not appended.
template='wh3_main_skill_node_set_cth_dragon_blooded_shugengan_yin'
nn={r['key']:r for r in native('character_skill_nodes')};source_nodes=[nn[r['item']] for r in native('character_skill_node_set_items') if r['set']==template and r['mod_disabled']=='false']
mapping={};nodes={};magic_nodes={}
def node(key,skill,indent,tier,required=0,visible=True,points=0):
 r=dict(source_nodes[0],key=key,character_skill_key=skill,indent=str(indent),tier=str(tier),required_num_parents=str(required),visible_in_ui=str(visible).lower(),points_on_creation=str(points))
 add('character_skill_nodes',r);add('character_skill_node_set_items',dict(set=S+'_skills',item=key,mod_disabled='false'));nodes[key]=r;return key
for n in source_nodes:
 if n['indent']=='2':continue
 sk=n['character_skill_key'];newskill=sk
 if 'shugengan_yin_unique_' in sk:newskill=P+'_unique_'+sk.rsplit('_',1)[1]
 elif sk=='wh3_main_skill_cth_all_unique_magic_resist':newskill=P+'_wind_harmony'
 elif sk=='wh3_main_skill_cth_all_unique_missile_resist':newskill=P+'_ranged_discipline'
 elif '_mount_' in sk:newskill=P+'_mount_'+('warhorse' if 'warhorse' in sk else 'jade_longma')
 elif 'shugengan_self_' in sk:newskill=P+'_bound_'+sk.rsplit('_',1)[1]
 key=P+'_node_'+n['key'].split('shugengan_yin_',1)[-1];mapping[n['key']]=key
 new=dict(n,key=key,character_skill_key=newskill);add('character_skill_nodes',new);nodes[key]=new
 add('character_skill_node_set_items',dict(set=S+'_skills',item=key,mod_disabled='false'))
layout=[('ember_bolt',0,0),('passive',1,0),('lunar_snare',2,0),('crashing_tide',3,0),('evasion',5,4),('grasp_eclipse',6,0),('sea_mist',7,0),('flameforged_blade',8,0),('earthing',9,0),('reserves',10,0),('conduit',11,4)]
generic={'evasion':'wh_main_skill_all_magic_all_06_evasion','earthing':'wh_main_skill_all_magic_all_07_earthing','reserves':'wh_main_skill_all_magic_all_08_power_drain','conduit':'wh_main_skill_all_magic_all_11_arcane_conduit'}
for slug,tier,req in layout:magic_nodes[slug]=node(P+'_node_magic_'+slug,generic.get(slug,P+'_skill_'+slug),2,tier,req)
node(P+'_node_foundation',foundation,2,12,visible=False,points=1)
link_template=native('character_skill_node_links')[0]
def link(parent,child,kind='REQUIRED'):
 add('character_skill_node_links',dict(link_template,parent_key=parent,child_key=child,link_type=kind,initial_descent_tiers='0',parent_link_position='1',child_link_position='1',parent_link_position_offset='0.0000',child_link_position_offset='0.0000'))
for r in native('character_skill_node_links'):
 if r['parent_key'] in mapping and r['child_key'] in mapping:add('character_skill_node_links',dict(r,parent_key=mapping[r['parent_key']],child_key=mapping[r['child_key']]))
for slug in ['passive','lunar_snare','crashing_tide']:
 link(magic_nodes['ember_bolt'],magic_nodes[slug]);link(magic_nodes[slug],magic_nodes['evasion'],'SUBSET_REQUIRED')
for slug in ['grasp_eclipse','sea_mist','flameforged_blade','earthing','reserves']:
 link(magic_nodes['evasion'],magic_nodes[slug]);link(magic_nodes[slug],magic_nodes['conduit'],'SUBSET_REQUIRED')
# Exactly one bound affinity; native old locks are deliberately not copied.
bound_nodes=[r for r in nodes.values() if r['character_skill_key'].startswith(P+'_bound_')]
for n in bound_nodes:
 for m in bound_nodes:
  if n!=m:add('character_skill_nodes_skill_locks',dict(character_skill_node=n['key'],character_skill=m['character_skill_key'],level='1'))
assert len(bound_nodes)==4 and len(T['character_skill_nodes_skill_locks'])==12
assert sum(n['visible_in_ui']=='true' for n in nodes.values())==54

# One main page and its overcast page. No inherited six-spell Yin/WWD page.
for i,upgrade in enumerate([False,True]):
 g=one('special_ability_groups','ability_group','wh3_main_lore_of_yin'+('_upgraded' if upgrade else ''));g.update(ability_group=P+'_arts'+('_upgraded' if upgrade else ''),unique_id=str(1986130000+i));add('special_ability_groups',g)
 loc['special_ability_groups_name_'+g['ability_group']]='Moon Arts'
 for old,new in amap.items():
  isup=old in {one('unit_abilities','key',ab)['overpower_option'] for _,_,_,ab in spells}
  if isup==upgrade:add('special_ability_groups_to_unit_abilities_junctions',dict(special_ability_groups=g['ability_group'],unit_special_abilities=new))

# Private stat records; shared Shugengan/native records are never overwritten.
footdonor=one('land_units','key','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0');oldfoot=next(r for r in base('land_units') if r['key']==S+'_human')
entity=one('battle_entities','key',footdonor['man_entity']);entity.update(key=P+'_foot_entity',run_speed='4.2000');add('battle_entities',entity)
weapon=one('melee_weapons','key',footdonor['primary_melee_weapon']);weapon.update(key=P+'_weapon',damage='210',ap_damage='90');add('melee_weapons',weapon)
for suffix,idx in [('human',0),('warhorse',1),('jade_longma',2)]:
 u=S+'_'+suffix;dl=one('land_units','key','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_'+str(idx));l=next(r for r in base('land_units') if r['key']==u).copy()
 weaponkey=P+'_weapon'
 if dl['primary_melee_weapon']!=footdonor['primary_melee_weapon']:
  mw=one('melee_weapons','key',dl['primary_melee_weapon']);weaponkey=P+'_weapon_'+suffix;mw.update(key=weaponkey,damage=str(int(mw['damage'])-70),ap_damage=str(int(mw['ap_damage'])-30));add('melee_weapons',mw)
 l.update(armour='wh2_main_leather_20' if idx==0 else 'wh2_main_chainmail_60',bonus_hit_points=str(int(dl['bonus_hit_points'])-200),melee_attack='45',melee_defence='35',morale='70',charge_bonus=str(int(dl['charge_bonus'])-10),primary_melee_weapon=weaponkey,man_entity=entity['key'] if idx==0 else dl['man_entity'],damage_mod_missile='15',damage_mod_physical='0',damage_mod_all='0',harmony_amplification_type=footdonor['harmony_amplification_type'],spell_mastery='1.0000')
 add('land_units',l)
 dm=one('main_units','unit',dl['key']);m=next(r for r in base('main_units') if r['unit']==u).copy()
 for field in ['recruitment_cost','upkeep_cost','multiplayer_cost']:m[field]=dm[field]
 add('main_units',m)
 # Every ability remains gated by its own skill; no starting lore passive.
 active_skill_donors={donors.get(n['character_skill_key'],n['character_skill_key']) for n in nodes.values()}
 effects={r['effect_key'] for r in native('character_skill_level_to_effects_junctions') if r['character_skill_key'] in active_skill_donors}
 support={b['unit_ability'] for b in bonus if b['effect'] in effects and b['unit_ability'] not in abilities and not any(x in b['unit_ability'] for x in ['spell_yin_','spell_bound_','spell_fire_','spell_deep_'])}
 for ability in sorted(set(amap.values())|{ab for _,ab in bound}|support|{'wh3_main_unit_passive_single_entity'}):add('land_units_to_unit_abilites_junctions',dict(land_unit=u,ability=ability,culture='*'))
 add('special_ability_groups_to_units_junctions',dict(ability_group=P+'_arts',unit=u,group_page_order='0'))

sub=next(r for r in base('agent_subtypes') if r['key']==S).copy();sub.update(magic_lore=P+'_arts',cost='1000');add('agent_subtypes',sub)
# Mounted-only appearance preserves the approved foot model/prop pivot exactly.
mounted=P+'_mounted'
v=next(r for r in base('variants') if r['variant_name']==S).copy();v.update(variant_name=mounted,variant_filename=mounted);add('variants',v)
uniform=next(r for r in base('agent_uniforms') if r['uniform_name']==S+'_uniform').copy();uniform.update(uniform_name=mounted+'_uniform',filename=mounted,battle_filename=mounted,campaign_porthole_filename=mounted,campaign_politician_filename='variantmeshes/variantmeshdefinitions/'+mounted+'.variantmeshdefinition');add('agent_uniforms',uniform)
for r in base('unit_variants'):
 if r['unit'] in [S+'_human',S+'_warhorse',S+'_jade_longma']:
  add('unit_variants',dict(r,variant=r['variant'] if r['unit']==S+'_human' else mounted))
for r in base('units_custom_battle_permissions'):
 if r['unit'] in [S+'_human',S+'_warhorse',S+'_jade_longma']:
  add('units_custom_battle_permissions',dict(r,general_uniform=r['general_uniform'] if r['unit']==S+'_human' else mounted+'_uniform'))
# Preserve existing mount ancillary identities; grant them through new skills.
for suffix in ['warhorse','jade_longma']:
 add('character_skill_level_to_ancillaries_junctions',dict(skill=P+'_mount_'+suffix,level='1',granted_ancillary=S+'_moon_mount_'+suffix))
 add('campaign_character_uniform_ancillary_junctions',dict(ancillary=S+'_moon_mount_'+suffix,art_set=S+'_art',uniform=mounted+'_uniform'))
for r in read(B/'db/ancillaries_tables/zzzz_mc_mooncourt_lord.tsv')[1]:
 seal=r.copy()
 if seal['key']==S+'_command_seal':seal['immortal']='false'
 add('ancillaries',seal)

# CB starts at native caster level, with selectable spells but no unique-line buffs.
cb=next(r for r in base('battle_set_piece_armies_characters') if r['character_name']==S+'_cb').copy()
cb.update(skillset=P+'_cb_skills',magic_lore=P+'_arts',character_level='1');add('battle_set_piece_armies_characters',cb)
add('battle_set_piece_armies_characters_skillsets',dict(key=P+'_cb_skills'))
for i,key in enumerate([foundation]+[P+'_skill_'+s for s,_,_,_ in spells]+[passive]):add('battle_set_piece_armies_characters_skillsets_skills',dict(skill=key,skillset_key=P+'_cb_skills',sort_order=str(i)))

# Empty only obsolete Zhao payloads whose effects/grants could survive in old saves.
retire_tables=['character_skill_level_to_effects_junctions','character_skill_level_to_ancillaries_junctions','character_skills_to_level_reached_criterias','ancillary_to_effects','ancillaries_required_skills']
for t in retire_tables:
 for f in (B/'db'/(t+'_tables')).glob('*.tsv'):
  if f.stem in ['zzzz_mc_mooncourt_lord','zzzz_mc_mooncourt_moon_arts']:
   internal=f.relative_to(B).as_posix()[:-4];files[internal]=([],read(f)[0])
replace={'character_skill_node_set_items','land_units','main_units','agent_subtypes','land_units_to_unit_abilites_junctions','special_ability_groups_to_units_junctions','battle_set_piece_armies_characters','unit_variants','units_custom_battle_permissions','ancillaries'}
for t,rs in T.items():
 internal='db/'+t+'_tables/'+('zzzz_mc_mooncourt_lord' if t in replace else 'zzzzz_mc_zhao_agile')
 files[internal]=(rs,read(N/(t+'_tables/data__.tsv'))[0])
for p,(rs,headers) in files.items():
 h,meta=copy.deepcopy(headers);meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 assert all(set(r)==set(h) for r in rs),p
 with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
lp='text/db/zzzzz_mc_zhao_v36.loc';dest=O/(lp+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
# Keep native numbers/tooltips, but replace the six native spell labels in private text.
replacements={text('unit_abilities_onscreen_name_'+ab):name for _,name,_,ab in spells}
replacements[text('unit_abilities_onscreen_name_wh3_main_lore_passive_power_of_yin')]='Lunar Ascendancy'
for key,val in list(loc.items()):
 for old,new in sorted(replacements.items(),key=lambda x:-len(x[0])):
  if old:val=val.replace(ascii(old),new)
 loc[key]=val
loc['character_skills_localised_description_'+P+'_unique_1']='Spell mastery: +10%. Cooldown: -20% for Lunar Snare and Grasp of the Eclipse only.'
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+lp,'','']]+[[k,v,'true'] for k,v in loc.items()])
manifest=dict(base=str(BASE),base_sha256=EXPECTED,jade=str(JADE),jade_sha256=sha(JADE),pack=str(PACK),db_paths=list(files),loc_path=lp,spells=[dict(slug=s,name=name,donor_skill=sk,donor_ability=ab,ability=amap[ab]) for s,name,sk,ab in spells],ability_map=amap,effect_map=emap,skill_donors=donors,skill_names=skill_names,visible_nodes=54,total_nodes=len(nodes),nodes=list(nodes.values()),bound=[dict(skill=s,ability=a) for s,a in bound],land_units=T['land_units'],main_units=T['main_units'],foundation=foundation,unique_names=unique_names,original_foot_model_animation_unchanged=True,runtime_verified=False)
legacy=sorted({r['key'] for r in base('character_skills') if r['key'].startswith(S+'_')}|{r['character_skill_key'] for r in base('character_skill_nodes') if r['key'].startswith(S+'_') and r['points_on_creation']!='0'})
script='script/campaign/mod/mc_zhao_v36_migration.lua';dest=O/script;dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text((R/'tools/templates/zhao-v36-migration.lua').read_text(encoding='utf-8').replace('__LEGACY_SKILLS__',',\n'.join('    '+json.dumps(s) for s in legacy)),encoding='utf-8')
manifest.update(migration_script=script,legacy_skills=legacy,mounted_variant=mounted)
(O/'design-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(files),'DB payloads;',len(amap),'private spell/passive abilities;54 visible nodes',flush=True)

if '--build' not in __import__('sys').argv:raise SystemExit(0)
review=json.loads((O/'asset-review.json').read_text());assert review['status']=='passed'
assert not PACK.exists(),'Preserve any completed candidate; use a new version for further edits.'
def cli(*args):
 p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True,encoding='utf-8')
 with (O/'pack-build.log').open('a',encoding='utf-8') as f:f.write(p.stdout+p.stderr)
 assert p.returncode==0,p.stdout+p.stderr
 return p.stdout
shutil.copy2(BASE,PACK)
# Stream Jade payloads into a private staging tree; preserve every approved byte.
cli('pack','extract','-p',JADE,'-F','/;'+str(O/'jade'))
jade_paths=[p for p in (O/'jade').rglob('*') if p.is_file() and not p.name.endswith('.rpfm_reserved')]
for start in range(0,len(jade_paths),25):cli('pack','add','-p',PACK,'-f',*[str(p)+';'+p.relative_to(O/'jade').as_posix() for p in jade_paths[start:start+25]])
cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in list(files)+[lp]])
for start in range(0,len(review['additional_files']),25):cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in review['additional_files'][start:start+25]])
print('BUILT',str(PACK),sha(PACK),flush=True)
