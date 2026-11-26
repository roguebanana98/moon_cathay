"""V35: native Moon/water/fire hybrid kit and native Shugengan support/mounts."""
import ast,copy,csv,hashlib,json,re,shutil,struct,subprocess,unicodedata
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-v35-moon-arts';O.mkdir(exist_ok=True);N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moon-v34-roundtrip'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v34_yuan_bo_lord.pack';PACK=O/'mc_moonshadow_heroes_v35_moon_arts.pack'
if PACK.exists():
    v=json.loads((O/'pack-validation.json').read_text());assert v['status']=='diagnostics_need_review' and not v['deployed'] and not (Path(C['game'])/'data'/PACK.name).exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','unpack','cli','read']],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='1c46a88ecfbcf54f7eb3481677775ebf9704d4bd90f3a4c2ca9aceb87e569b01'
S='mc_mooncourt_lord';U=S+'_human';GROUP=S+'_moon_arts';CAM='cam_lord_hu1e_dlc24_yuan_bo_dragon_jade'
T=defaultdict(list);paths={};cache={};loc={};files=[];unit_profiles=[]
def native(t):
    if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def rows(t):return native(t)[1]
def one(t,k,v):
    a=[r for r in rows(t) if r[k]==v];assert len(a)==1,(t,k,v,len(a));return dict(a[0])
def base(t):return read(B/('db/'+t+'_tables/zzzz_mc_mooncourt_lord.tsv'))[1]
def load(t):
    p=B/('db/'+t+'_tables/zzzz_mc_mooncourt_lord.tsv')
    T[t]=copy.deepcopy(read(p)[1]) if p.exists() else []
    paths[t]='db/'+t+'_tables/zzzz_mc_mooncourt_lord'
def add(t,r):T[t].append(r);return r
english={}
for p in (R/'reference/local/moon-v33-native-loc').rglob('*.tsv'):
    for r in read(p)[1]:english[r['key']]=r['text']
def textkey(k,depth=0):
    assert depth<16
    return re.sub(r'\{\{tr:([^}]+)\}\}',lambda m:textkey(m[1],depth+1),english.get(k,''))
def ascii_text(s):return unicodedata.normalize('NFKD',s.replace('\u2019',"'").replace('\u2018',"'").replace('\u2013','-').replace('\u2014','-')).encode('ascii','ignore').decode()
def label(kind,new,old,fallback=''):
    value=textkey(kind+'_'+old) or fallback
    for a,b in sorted(replacements.items(),key=lambda x:-len(x[0])):
        if a:value=value.replace(a,b)
    loc[kind+'_'+new]=ascii_text(value)

# Native Yin command/campaign/Harmony/support framework, no WWD growth or extra bound lores.
template='wh3_main_skill_node_set_cth_dragon_blooded_shugengan_yin'
nodeby={r['key']:r for r in rows('character_skill_nodes')}
items=[r for r in rows('character_skill_node_set_items') if r['set']==template and r['mod_disabled']=='false']
selected=[nodeby[r['item']] for r in items if nodeby[r['item']]['indent']!='3']
assert len(selected)==len(items)-4==64
magic={0:('wh3_main_skill_cth_magic_yang_01_dragons_breath_lord','Lunar Flame'),
       1:('wh3_main_skill_cth_magic_yin_05_power_of_yin','Lunar Resonance'),
       2:('wh2_main_skill_magic_life_wizard_earth_blood_lord','Restoring Tide'),
       3:('wh3_main_skill_cth_magic_yang_02_jade_shield_lord','Moonlit Ward'),
       4:('wh3_main_skill_cth_magic_yin_02_storm_of_shadows_lord','Undertow'),
       6:('wh3_main_skill_cth_magic_yang_07_might_of_heaven_and_earth_lord','Lunar Ascendance'),
       7:('wh2_main_skill_all_magic_fire_10_flame_storm_lord','Moonfire Tempest'),
       10:('wh_main_skill_all_magic_all_11_arcane_conduit','Astral Conduit'),
       11:('wh3_main_skill_cth_magic_yang_dummy_dragons_breath_jade_shield','Starting Moon Arts [HIDDEN]')}
unique_names=['Moonfire Wrath','Lunar Attunement','Moonlit Aegis','Moonlit Muster','Celestial Accord','Lunar Wellspring']
chosen={};node_skills={};skillmap={};skill_names={};replacements={};mount_skill_sources={}
for n in selected:
    old=n['character_skill_key'];donor=old;name=textkey('character_skills_localised_name_'+old) or one('character_skills','key',old)['localised_name']
    private=False
    if n['indent']=='2':
        tier=int(n['tier']);donor,name=magic.get(tier,(old,name));private=True
    elif 'shugengan_yin_unique_' in old:
        i=int(old.rsplit('_',1)[-1]);name=unique_names[i];donor='wh_main_skill_all_all_self_deadly_onslaught' if i==0 else old;private=True
    elif old=='wh3_main_skill_cth_all_self_will_of_the_dragons':name='Blessing of the Moon';private=True
    elif '_mount_' in old:
        suffix='warhorse' if 'warhorse' in old else 'jade_longma';name='Warhorse' if suffix=='warhorse' else 'Jade Longma';private=True;mount_skill_sources[suffix]=old
    if private:
        new=S+'_moon_skill_'+str(len(chosen));chosen[new]=donor;skillmap[old]=new;skill_names[new]=name
        native_name=textkey('character_skills_localised_name_'+donor)
        if native_name and int(n['tier'])!=11:replacements[native_name]=name
    else:new=old
    node_skills[n['key']]=new
bonus=rows('effect_bonus_value_unit_ability_junctions')
skill_effect_rows=[r for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key'] in set(chosen.values())]
effects={r['effect_key'] for r in skill_effect_rows};abilities={r['unit_ability'] for r in bonus if r['effect'] in effects}
ability_names={}
for sk,donor in chosen.items():
    name=skill_names[sk]
    if name in ['Starting Moon Arts [HIDDEN]','Evasion','Earthing','Power Drain']:continue
    es={r['effect_key'] for r in skill_effect_rows if r['character_skill_key']==donor}
    for b in bonus:
        if b['effect'] in es and b['bonus_value_id']=='enable':ability_names[b['unit_ability']]=name
pending=list(abilities)
while pending:
    a=one('unit_abilities','key',pending.pop());special=one('unit_special_abilities','key',a['key'])
    for key in [a['overpower_option'],special['parent_ability']]:
        if key and key not in abilities:abilities.add(key);pending.append(key)
amap={a:S+'_moon_ability_'+str(i) for i,a in enumerate(sorted(abilities))}
for a in abilities:
    parent=next((p for p in abilities if one('unit_abilities','key',p)['overpower_option']==a),None)
    if parent and parent in ability_names:ability_names[a]=ability_names[parent]+' (Upgraded)'
# Private ability-linked effects preserve exact spell level cost/cooldown changes.
# Personal Yin cooldown becomes a private all-Moon-Arts cooldown; external native
# lore modifiers remain limited to source-school subset groups below.
group_bonus=rows('effect_bonus_value_special_ability_group_junctions')
group_effects={r['effect'] for r in group_bonus if r['effect'] in effects}
emap={e:S+'_moon_effect_'+str(i) for i,e in enumerate(sorted(effects)) if any(r['effect']==e for r in bonus) or e in group_effects}
for old,new in emap.items():
    add('effects',dict(one('effects','effect',old),effect=new));label('effects_description',new,old)
    T['effect_bonus_value_unit_ability_junctions'].extend(dict(r,effect=new,unit_ability=amap[r['unit_ability']]) for r in bonus if r['effect']==old)
T['effect_bonus_value_unit_ability_junctions'].extend(dict(r,unit_ability=amap[r['unit_ability']]) for r in bonus if r['unit_ability'] in amap)
for new,donor in chosen.items():
    add('character_skills',dict(one('character_skills','key',donor),key=new,localised_name=skill_names[new]))
    loc['character_skills_localised_name_'+new]=skill_names[new];label('character_skills_localised_description',new,donor)
    for t,field in [('character_skill_level_details','skill_key'),('character_skills_to_level_reached_criterias','character_skill')]:T[t].extend(dict(r,**{field:new}) for r in rows(t) if r[field]==donor)
    T['character_skill_level_to_effects_junctions'].extend(dict(r,character_skill_key=new,effect_key=emap.get(r['effect_key'],r['effect_key'])) for r in skill_effect_rows if r['character_skill_key']==donor)
uids={r['unique_id'] for r in rows('unit_special_abilities')}
for p in (B/'db/unit_special_abilities_tables').glob('*.tsv'):uids.update(r['unique_id'] for r in read(p)[1])
aux=[('special_ability_to_special_ability_phase_junctions','special_ability'),('special_ability_to_auto_deactivate_flags','special_ability'),('special_ability_to_invalid_target_flags','special_ability'),('special_ability_to_invalid_usage_flags','special_ability'),('special_ability_to_recharge_contexts','special_ability'),('unit_abilities_to_additional_ui_effects_juncs','ability'),('special_ability_intensity_settings','ability'),('special_ability_behaviour_to_ability_junctions','ability'),('ability_to_ui_collection_junctions','ability'),('unit_special_ability_to_special_ability_toggle_groups_junctions','unit_special_ability')]
for i,(old,new) in enumerate(amap.items()):
    a=one('unit_abilities','key',old);add('unit_abilities',dict(a,key=new,overpower_option=amap.get(a['overpower_option'],a['overpower_option'])))
    a=one('unit_special_abilities','key',old);uid=str(1986115100+i);assert uid not in uids
    add('unit_special_abilities',dict(a,key=new,unique_id=uid,parent_ability=amap.get(a['parent_ability'],a['parent_ability'])))
    for t,field in aux:T[t].extend(dict(r,**{field:new}) for r in rows(t) if r[field]==old)
    name=ability_names.get(old) or textkey('unit_abilities_onscreen_name_'+old);assert name,old
    loc['unit_abilities_onscreen_name_'+new]=ascii_text(name);label('unit_abilities_tooltip_text',new,old)

# Visible mixed lore: all six spells, passive and native overcast variants.
spell_donors={magic[t][0] for t in [0,1,2,3,4,6,7]}
spell_effects={r['effect_key'] for r in skill_effect_rows if r['character_skill_key'] in spell_donors}
spell_abilities={r['unit_ability'] for r in bonus if r['effect'] in spell_effects and r['bonus_value_id']=='enable'}
overcasts={one('unit_abilities','key',a)['overpower_option'] for a in spell_abilities};overcasts.discard('')
assert len(spell_abilities-overcasts)==7
gid_used={r['unique_id'] for r in rows('special_ability_groups')}
for p in (B/'db/special_ability_groups_tables').glob('*.tsv'):gid_used.update(r['unique_id'] for r in read(p)[1])
gid=1986115000
def group(old,new,members,title):
    global gid
    g=one('special_ability_groups','ability_group',old);assert str(gid) not in gid_used;g.update(ability_group=new,unique_id=str(gid));gid+=1;add('special_ability_groups',g)
    loc['special_ability_groups_name_'+new]=title
    T['special_ability_groups_to_unit_abilities_junctions'].extend(dict(special_ability_groups=new,unit_special_abilities=amap[a]) for a in sorted(members))
for upgraded,members in [(False,spell_abilities-overcasts),(True,overcasts)]:group('wh3_main_lore_of_yin'+('_upgraded' if upgraded else ''),GROUP+('_upgraded' if upgraded else ''),members,'Moon Arts')
for r in group_bonus:
    if r['effect'] in group_effects:
        add('effect_bonus_value_special_ability_group_junctions',dict(r,effect=emap[r['effect']],special_ability_group=GROUP+('_upgraded' if r['special_ability_group'].endswith('_upgraded') else '')))
for idx,school in enumerate(['wh3_main_lore_of_yin','wh3_main_lore_of_yang','wh_dlc05_lore_life','wh_main_lore_fire']):
    for upgraded in [False,True]:
        old=school+('_upgraded' if upgraded else '');members={r['unit_special_abilities'] for r in rows('special_ability_groups_to_unit_abilities_junctions') if r['special_ability_groups']==old}&abilities
        if not members:continue
        new=GROUP+'_source_'+str(idx)+('_upgraded' if upgraded else '');group(old,new,members,'Moon Arts')
        T['effect_bonus_value_special_ability_group_junctions'].extend(dict(r,special_ability_group=new) for r in group_bonus if r['special_ability_group']==old)

# Replace the source tree binding, retaining unrelated legacy records for save IDs.
load('character_skill_node_set_items');T['character_skill_node_set_items']=[]
node_map={n['key']:S+'_moon_node_'+str(i) for i,n in enumerate(selected)}
for n in selected:
    add('character_skill_nodes',dict(n,key=node_map[n['key']],character_skill_key=node_skills[n['key']]))
    T['character_skill_node_set_items'].append(dict(set=S+'_skills',item=node_map[n['key']],mod_disabled='false'))
for r in rows('character_skill_node_links'):
    if r['parent_key'] in node_map and r['child_key'] in node_map:add('character_skill_node_links',dict(r,parent_key=node_map[r['parent_key']],child_key=node_map[r['child_key']]))
for r in rows('character_skill_nodes_skill_locks'):
    if r['character_skill_node'] in node_map:add('character_skill_nodes_skill_locks',dict(r,character_skill_node=node_map[r['character_skill_node']],character_skill=skillmap.get(r['character_skill'],r['character_skill'])))
for n in T['character_skill_nodes']:assert sum(r['child_key']==n['key'] and r['link_type'] in ['SUBSET_REQUIRED','REQUIRED'] for r in T['character_skill_node_links'])>=int(n['required_num_parents']),n['key']
# Retire WWD-only skill/innate/item effects, including pre-existing purchased ranks.
retired={}
for t in ['character_skill_level_to_effects_junctions','character_skill_level_to_ancillaries_junctions','ancillary_to_effects','ancillaries_required_skills','character_skills_to_level_reached_criterias']:
    p='db/'+t+'_tables/zzzz_mc_mooncourt_lord';retired[p]=[]

# Source foot graphics/animation remain exactly v34; normalize Harmony to native Shugengan.
load('agent_subtypes');T['agent_subtypes'][0]['magic_lore']=GROUP
load('land_units');foot=copy.deepcopy(T['land_units'][0]);foot['harmony_amplification_type']=one('land_units','key','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0')['harmony_amplification_type'];T['land_units'][0]=foot
load('main_units');main=copy.deepcopy(T['main_units'][0]);load('unit_variants');uv=copy.deepcopy(T['unit_variants'][0]);load('units_to_groupings_military_permissions')
load('units_custom_battle_permissions');permission=next(r for r in T['units_custom_battle_permissions'] if r['faction']=='wh3_main_cth_cathay_mp')
load('land_units_to_unit_abilites_junctions');T['land_units_to_unit_abilites_junctions']=[]
load('special_ability_groups_to_units_junctions');T['special_ability_groups_to_units_junctions']=[]
load('battle_set_piece_armies_characters');T['battle_set_piece_armies_characters'][0].update(skillset=S+'_moon_cb_skills',magic_lore=GROUP)
mounted_sword=json.loads((O/'mounted-sword.json').read_text());files.extend(mounted_sword['files'])
mounted_variant=mounted_sword['variant'];mounted_uniform=S+'_mounted_uniform'
add('variants',dict(base('variants')[0],variant_name=mounted_variant,variant_filename=mounted_variant))
add('agent_uniforms',dict(base('agent_uniforms')[0],uniform_name=mounted_uniform,filename=mounted_variant,battle_filename=mounted_variant,campaign_porthole_filename=mounted_variant,campaign_politician_filename=mounted_sword['vmd']))
add('battle_set_piece_armies_characters_skillsets',dict(key=S+'_moon_cb_skills'))
cbskills=[node_skills[n['key']] for n in selected if n['indent'] in ['1','2'] or n['character_skill_key']=='wh3_main_skill_cth_all_self_will_of_the_dragons']
T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(skill=k,skillset_key=S+'_moon_cb_skills',sort_order=str(i)) for i,k in enumerate(dict.fromkeys(cbskills)))

for suffix,donor in [('warhorse','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_1'),('jade_longma','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_2')]:
    u=S+'_'+suffix;dl=one('land_units','key',donor);dm=one('main_units','unit',donor);nf=one('land_units','key','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0');nm=one('main_units','unit','wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0')
    m=dict(main,unit=u,land_unit=u,mount=dm['mount'],weight=dm['weight'])
    for field in ['recruitment_cost','upkeep_cost','multiplayer_cost']:m[field]=str(int(main[field])+int(dm[field])-int(nm[field]))
    T['main_units'].append(m);land=dict(foot,key=u,man_animation=dl['man_animation'],mount=dl['mount'],num_mounts='1')
    for field in ['bonus_hit_points','charge_bonus','melee_attack','melee_defence']:land[field]=str(int(foot[field])+int(dl[field])-int(nf[field]))
    for field in ['category','attribute_group','spacing','ground_stat_effect_group','ai_usage_group','capture_tier','key_building_capture_tier','score_capture_tier','can_brace']:land[field]=dl[field]
    T['land_units'].append(land);T['unit_variants'].append(dict(uv,unit=u,name=u,variant=mounted_variant));T['units_to_groupings_military_permissions'].append(dict(unit=u,military_group='wh3_main_cth'))
    T['units_custom_battle_permissions'].extend(dict(permission,unit=u,general_uniform=mounted_uniform,faction=f,campaign_exclusive='true' if f!='wh3_main_cth_cathay_mp' else 'false') for f in ['wh3_main_cth_cathay_mp','cr_cth_agents_of_the_moon'])
    override=next(r for r in rows('campaign_mount_animation_set_overrides') if r['mount_unit']==donor)
    add('campaign_mount_animation_set_overrides',dict(override,mount_unit=u,character_animation_set=CAM))
    mountskill=skillmap[mount_skill_sources[suffix]];ancsrc=next(r for r in rows('ancillaries') if r['provided_bodyguard_unit']==donor);anc=S+'_moon_mount_'+suffix
    add('ancillaries',dict(ancsrc,key=anc,provided_bodyguard_unit=u));add('ancillary_info',dict(one('ancillary_info','ancillary',ancsrc['key']),ancillary=anc));add('ancillaries_included_agent_subtypes',dict(agent_subtype=S,ancillary=anc));add('character_skill_level_to_ancillaries_junctions',dict(skill=mountskill,level='1',granted_ancillary=anc))
    add('campaign_character_uniform_ancillary_junctions',dict(ancillary=anc,art_set=S+'_art',uniform=mounted_uniform))
    add('units_custom_battle_mounts',dict(next(r for r in rows('units_custom_battle_mounts') if r['base_unit']=='wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0' and r['mounted_unit']==donor),base_unit=U,mounted_unit=u))
    title='Warhorse' if suffix=='warhorse' else 'Jade Longma';loc['ancillaries_onscreen_name_'+anc]=title;loc['ancillaries_colour_text_'+anc]='A mount trained to carry a guardian of the moon.';loc['land_units_onscreen_name_'+u]='Zhao Yixuan';loc['units_custom_battle_mounts_mount_name_'+U+u]=title;loc['units_custom_battle_mounts_localised_description_'+U+u]='Mount: '+title+'.'
    p='ui/units/minspec_portholes/'+u+'.png';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'build/moon-v34-yuan-bo-lord/ui/units/minspec_portholes'/ (U+'.png'),O/p);files.append(p)
    unit_profiles.append(dict(unit=u,battle=dl['man_animation'],campaign=override['rider_animation_set'],source=donor))
for u in [U]+[p['unit'] for p in unit_profiles]:
    T['land_units_to_unit_abilites_junctions'].extend(dict(ability=amap[a],land_unit=u,culture='*') for a in sorted(abilities))
    T['land_units_to_unit_abilites_junctions'].append(dict(ability='wh3_main_unit_passive_single_entity',land_unit=u,culture='*'))
    T['special_ability_groups_to_units_junctions'].append(dict(ability_group=GROUP,unit=u,group_page_order='0'))

# Native runtime profiles for both new mount units; no foot lookup changes.
bins={}
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
    raw=p.read_bytes();pos=4
    for _ in range(struct.unpack_from('<I',raw)[0]):
        z=struct.unpack_from('<H',raw,pos)[0];pos+=2;k=raw[pos:pos+z].decode();pos+=z;n=struct.unpack_from('<I',raw,pos)[0];pos+=4;bins[Path(k).stem]=raw[pos:pos+n];pos+=n
mount_clips={}
for profile in unit_profiles:
    assert profile['battle'] in bins
    assert one('battle_animations_table','key',profile['battle'])['skeleton']=='humanoid01e'
    paths0=sorted(set(x.decode() for x in re.findall(rb'animations/[a-zA-Z0-9_./ -]+?\.anim',bins[profile['battle']])))
    candidates=[p for p in paths0 if '/shugengan/' in p and '/rider/' in p]
    preferred=[p for p in candidates if ('/rider/warhorse/' if profile['unit'].endswith('warhorse') else '/rider/longma/') in p]
    clips=[]
    for tag in ['stand','walk','attack','cast']:
        options=[p for p in preferred if tag in Path(p).stem and not any(x in p for x in ['death','matched','idle','jump','transition'])]
        if not options:options=[p for p in candidates if tag in Path(p).stem and not any(x in p for x in ['death','matched','idle','jump','transition'])]
        assert options,(profile['battle'],tag);clips.append(options[0])
    mount_clips[profile['unit']]=clips
(O/'mount-review-clips.json').write_text(json.dumps(mount_clips,indent=2))

# Mechanical equivalence assertions for every renamed spell/ability/skill donor.
for old,new in amap.items():
    actual=next(r for r in T['unit_abilities'] if r['key']==new);donor=one('unit_abilities','key',old)
    assert dict(actual,key=old,overpower_option=donor['overpower_option'])==donor
    actual=next(r for r in T['unit_special_abilities'] if r['key']==new);donor=one('unit_special_abilities','key',old)
    assert dict(actual,key=old,unique_id=donor['unique_id'],parent_ability=donor['parent_ability'])==donor
for new,old in chosen.items():
    assert [dict(r,skill_key=old) for r in T['character_skill_level_details'] if r['skill_key']==new]==[r for r in rows('character_skill_level_details') if r['skill_key']==old]
for s in ['undeath','kongbai','zhaoyixuan']:
    assert not any(s in r['character_skill_key'] for r in T['character_skill_nodes'])
assert len(T['character_skill_node_set_items'])==64
assert T['land_units'][0]['man_animation']=='hu1e_dlc24_yuan_bo_dragon_jade'
assert all(v.isascii() for v in loc.values())
outpaths=[]
def write(t,rs,p):
    h,meta=copy.deepcopy(native(t)[0]);meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True);assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
    outpaths.append(p)
for t,rs in T.items():
    if rs or t in paths:write(t,rs,paths.get(t,'db/'+t+'_tables/zzzz_mc_mooncourt_moon_arts'))
for p,rs in retired.items():write(p.split('/')[1][:-7],rs,p)
p='text/db/zzzz_mc_mooncourt_moon_arts.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
outpaths.append(p)
before=unpack(BASE)
if not PACK.exists():shutil.copy2(BASE,PACK)
cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in outpaths]);cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files])
after=unpack(PACK);assert all(after[p]==data for p,data in before.items() if p not in outpaths)
assert all(after[p]==data for p,data in before.items() if p.startswith(('variantmeshes/','animations/','script/')))
check=R/'reference/local/moon-v35-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in outpaths:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group0 in diag['results']:
    for kind,g in group0.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,skill_nodes=64,spells=[magic[t][1] for t in [0,2,3,4,6,7]],native_mechanics_icons_vfx_preserved=True,wwd_skill_effects_retired=True,source_bound_lores_removed=True,shugengan_red_blue_harmony_preserved=True,native_mounts=unit_profiles,foot_yuan_bo_graphics_and_animations_unchanged=True,custom_battle_preset_updated=True,ability_map=amap,skill_donors=chosen,groups=GROUP,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['ability_map','skill_donors']},indent=2));assert not blocking
