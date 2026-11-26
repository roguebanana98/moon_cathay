"""V15: native spell mechanics with private English display names, no artwork/VFX edits."""
import ast,copy,csv,hashlib,json,re,shutil,struct,subprocess,sys,unicodedata
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-casters-v15-spells';O.mkdir(parents=True,exist_ok=True)
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moon-casters-v15-base'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v14_custom_battle.pack';PACK=O/'mc_moonshadow_heroes_v15_caster_spells.pack'
if PACK.exists():
    assert '--rebuild' in sys.argv and not (O/'deployment.json').exists() and not (Path(C['game'])/'data'/PACK.name).exists()
    PACK.unlink()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='4eead338f8daab6f76f5dab468b71d17a03f7806267ab59f05fe94d1d40a5ce6'
spec=json.loads((R/'src/campaign/moon-caster-spells.json').read_text(encoding='utf8'))
T=defaultdict(list);headers={};internals={};cache={};loc={};files=[];audits=[]
def native(t):
    if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def rows(t):return native(t)[1]
def one(t,f,v):
    found=[r for r in rows(t) if r[f]==v];assert len(found)==1,(t,f,v);return dict(found[0])
def load(t,name):
    headers[t],T[t]=read(B/('db/'+t+'_tables/'+name+'.tsv'));internals[t]='db/'+t+'_tables/'+name
for t in ('character_skill_nodes','character_skill_node_set_items','character_skill_node_links'):
    load(t,'mc_moon_casters')
load('battle_set_piece_armies_characters','mc_moon_heroes_custom_battle')
load('battle_set_piece_armies_characters_skillsets','mc_moon_heroes_custom_battle')
load('battle_set_piece_armies_characters_skillsets_skills','mc_moon_heroes_custom_battle')
load('land_units_to_unit_abilites_junctions','mc_moon_casters')
old_tables=copy.deepcopy(T)
english={}
for p in (R/'reference/local/moon-casters-native-loc').rglob('*.loc.tsv'):
    for r in read(p)[1]:english[r['key']]=r['text']
def resolve(k,depth=0):
    assert depth<16,k
    return re.sub(r'\{\{tr:([^}]+)\}\}',lambda m:resolve(m[1],depth+1),english.get(k,''))
def ascii_text(s):return unicodedata.normalize('NFKD',s.replace('\u2019',"'").replace('\u2018',"'").replace('\u2013','-').replace('\u2014','-')).encode('ascii','ignore').decode()
def localized(kind,new,old,fallback=''):
    text=resolve(kind+'_'+old) or fallback
    for before,after in sorted(replacements.items(),key=lambda pair:len(pair[0]),reverse=True):
        if before:text=text.replace(before,after)
    loc[kind+'_'+new]=ascii_text(text)
def short(s):return hashlib.sha256(s.encode()).hexdigest()[:12]
native_nodes={r['key']:r for r in rows('character_skill_nodes')}
bonus=rows('effect_bonus_value_unit_ability_junctions')
uid_used={r['unique_id'] for r in rows('unit_special_abilities')}
group_uid_used={r['unique_id'] for r in rows('special_ability_groups')}
core_tiers=[0,1,2,3,4,6,7]
for idx,(s,cfg) in enumerate(spec.items()):
    # Template provides the existing two spell blocks, prerequisites and support nodes.
    items=[r for r in rows('character_skill_node_set_items') if r['set']==cfg['template']]
    template=[native_nodes[r['item']] for r in items if native_nodes[r['item']]['indent'] in ('2','3') and 'magic' in native_nodes[r['item']]['character_skill_key']]
    template=[r for r in template if r['tier'] in [str(i) for i in range(12)]]
    assert len(template)==12 and len({r['tier'] for r in template})==12,(s,len(template))
    chosen={tier:(old,name) for tier,(old,name) in zip(core_tiers,cfg['skills'])}
    chosen[11]=(cfg['starter'],'Starting Spell [HIDDEN]')
    skillmap={};source_by_tier={};ability_names={};replacements={}
    for n in template:
        tier=int(n['tier']);old,name=chosen.get(tier,(n['character_skill_key'],one('character_skills','key',n['character_skill_key'])['localised_name']))
        source_by_tier[tier]=old;skillmap[old]=s+'_magic_'+str(tier)
        native_name=resolve('character_skills_localised_name_'+old) or one('character_skills','key',old)['localised_name']
        if tier in core_tiers:replacements[native_name]=name
        for effect in [r['effect_key'] for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==old]:
            for b in bonus:
                if b['effect']==effect and b['bonus_value_id']=='enable':
                    if tier in core_tiers:ability_names[b['unit_ability']]=name
                    else:ability_names.setdefault(b['unit_ability'],resolve('unit_abilities_onscreen_name_'+b['unit_ability']))
    # All native cost/cooldown/overcast effect targets are carried through together.
    effects={r['effect_key'] for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key'] in skillmap}
    abilities={r['unit_ability'] for r in bonus if r['effect'] in effects}
    pending=list(abilities)
    while pending:
        a=one('unit_abilities','key',pending.pop())
        for key in (a['overpower_option'],one('unit_special_abilities','key',a['key'])['parent_ability']):
            if key and key not in abilities:abilities.add(key);pending.append(key)
    amap={a:s+'_ability_'+short(a) for a in sorted(abilities)}
    for a in abilities:
        parent=next((p for p in abilities if one('unit_abilities','key',p)['overpower_option']==a),None)
        if parent and parent in ability_names:ability_names[a]=ability_names[parent]+' (Upgraded)'
    emap={e:s+'_effect_'+short(e) for e in effects if any(r['effect']==e for r in bonus)}
    # Native equipment and other native effects can still affect these copies.
    # Original casters do not possess the private abilities, so their kit is unchanged.
    T['effect_bonus_value_unit_ability_junctions'].extend(dict(r,unit_ability=amap[r['unit_ability']]) for r in bonus if r['unit_ability'] in amap)
    for old,new in emap.items():
        row=one('effects','effect',old);row['effect']=new;T['effects'].append(row)
        T['effect_bonus_value_unit_ability_junctions'].extend(dict(r,effect=new,unit_ability=amap[r['unit_ability']]) for r in bonus if r['effect']==old)
        localized('effects_description',new,old)
    for tier,old in source_by_tier.items():
        new=skillmap[old];source=one('character_skills','key',old);name=chosen.get(tier,(old,resolve('character_skills_localised_name_'+old) or source['localised_name']))[1]
        source.update(key=new,localised_name=name);T['character_skills'].append(source)
        loc['character_skills_localised_name_'+new]=ascii_text(name)
        localized('character_skills_localised_description',new,old,source['localised_description'])
        T['character_skill_level_details'].extend(dict(r,skill_key=new) for r in rows('character_skill_level_details') if r['skill_key']==old)
        T['character_skill_level_to_effects_junctions'].extend(dict(r,character_skill_key=new,effect_key=emap.get(r['effect_key'],r['effect_key'])) for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==old)
    for j,(old,new) in enumerate(sorted(amap.items())):
        a=one('unit_abilities','key',old);expected=dict(a,key=new,overpower_option=amap.get(a['overpower_option'],a['overpower_option']))
        assert not a['superseded_abilities_set'],(s,old,'Check native supersession before copying')
        T['unit_abilities'].append(expected)
        special=one('unit_special_abilities','key',old);uid=str(1800316000+idx*100+j);assert uid not in uid_used;uid_used.add(uid)
        T['unit_special_abilities'].append(dict(special,key=new,unique_id=uid,parent_ability=amap.get(special['parent_ability'],special['parent_ability'])))
        for t,field in [('special_ability_to_special_ability_phase_junctions','special_ability'),('special_ability_to_auto_deactivate_flags','special_ability'),
                        ('special_ability_to_invalid_target_flags','special_ability'),('special_ability_to_invalid_usage_flags','special_ability'),
                        ('special_ability_to_recharge_contexts','special_ability'),('unit_abilities_to_additional_ui_effects_juncs','ability'),
                        ('special_ability_intensity_settings','ability'),('special_ability_behaviour_to_ability_junctions','ability'),
                        ('ability_to_ui_collection_junctions','ability'),('unit_special_ability_to_special_ability_toggle_groups_junctions','unit_special_ability')]:
            T[t].extend(dict(r,**{field:new}) for r in rows(t) if r[field]==old)
        name=ability_names.get(old) or resolve('unit_abilities_onscreen_name_'+old)
        assert name,(s,old,'missing native name')
        loc['unit_abilities_onscreen_name_'+new]=ascii_text(name)
        localized('unit_abilities_tooltip_text',new,old)
    group=s+'_lore'
    # Native lore membership includes base spells and the native lore passive; upgraded
    # variants are reached through the identical overpower_option relationship.
    lore_abilities=set()
    for tier in core_tiers:
        old=source_by_tier[tier]
        eff={r['effect_key'] for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==old}
        lore_abilities.update(r['unit_ability'] for r in bonus if r['effect'] in eff and r['bonus_value_id']=='enable')
    # No upgraded spell is a separate base slot.
    overcasts={one('unit_abilities','key',a)['overpower_option'] for a in abilities}
    lore_abilities-=overcasts
    assert len(lore_abilities)==7,(s,lore_abilities)
    group_specs=[(cfg['native_group'],group,cfg['group_name'])]
    if s=='mc_tidecaller':group_specs.append(('wh_dlc05_lore_life',group+'_life','Restorative Waters'))
    grouped=set()
    for page,(native_group,private_group,title) in enumerate(group_specs):
        for upgraded in (False,True):
            ng=native_group+('_upgraded' if upgraded else '');pg=private_group+('_upgraded' if upgraded else '')
            members={r['unit_special_abilities'] for r in rows('special_ability_groups_to_unit_abilities_junctions') if r['special_ability_groups']==ng}&abilities
            assert members,(s,ng)
            g=one('special_ability_groups','ability_group',ng);g_uid=str(1800316500+idx*10+page*2+int(upgraded));assert g_uid not in group_uid_used
            group_uid_used.add(g_uid);g.update(ability_group=pg,unique_id=g_uid);T['special_ability_groups'].append(g)
            loc['special_ability_groups_name_'+pg]=title
            T['special_ability_groups_to_unit_abilities_junctions'].extend(dict(special_ability_groups=pg,unit_special_abilities=amap[a]) for a in sorted(members))
            T['effect_bonus_value_special_ability_group_junctions'].extend(dict(r,special_ability_group=pg) for r in rows('effect_bonus_value_special_ability_group_junctions') if r['special_ability_group']==ng)
            grouped.update(members)
            if not upgraded:T['special_ability_groups_to_units_junctions'].append(dict(ability_group=pg,unit=s+'_human',group_page_order=str(page)))
    assert lore_abilities<=grouped
    # Common spellcaster abilities such as Arcane Conduit retain their native activation.
    T['land_units_to_unit_abilites_junctions'].extend(dict(ability=amap[a],land_unit=s+'_human',culture='*') for a in sorted(abilities-lore_abilities-overcasts))
    mapping={n['key']:s+'_magic_node_'+n['tier'] for n in template}
    for n in template:
        new=dict(n,key=mapping[n['key']],character_skill_key=skillmap[source_by_tier[int(n['tier'])]],indent='2')
        T['character_skill_nodes'].append(new);T['character_skill_node_set_items'].append(dict(set=s+'_skills',item=new['key'],mod_disabled='false'))
    for link in rows('character_skill_node_links'):
        if link['parent_key'] in mapping and link['child_key'] in mapping:T['character_skill_node_links'].append(dict(link,parent_key=mapping[link['parent_key']],child_key=mapping[link['child_key']]))
    cb=s+'_cb_spells';T['battle_set_piece_armies_characters_skillsets'].append(dict(key=cb))
    T['battle_set_piece_armies_characters_skillsets_skills'].extend(dict(skill=skillmap[source_by_tier[t]],skillset_key=cb,sort_order=str(i)) for i,t in enumerate([11]+core_tiers))
    char=next(r for r in T['battle_set_piece_armies_characters'] if r['character_name']==s+'_human');char.update(skillset=cb,character_level='40',magic_lore=group)
    # Explicit mechanical equivalence: only identifiers/labels differ from native.
    for old,new in amap.items():
        a=next(r for r in T['unit_abilities'] if r['key']==new);base=one('unit_abilities','key',old)
        assert dict(a,key=old,overpower_option=base['overpower_option'])==base
        a=next(r for r in T['unit_special_abilities'] if r['key']==new);base=one('unit_special_abilities','key',old)
        assert dict(a,key=old,unique_id=base['unique_id'],parent_ability=base['parent_ability'])==base
    for old,new in skillmap.items():
        actual=[dict(r,character_skill_key=old,effect_key=next((k for k,v in emap.items() if v==r['effect_key']),r['effect_key'])) for r in T['character_skill_level_to_effects_junctions'] if r['character_skill_key']==new]
        assert actual==[r for r in rows('character_skill_level_to_effects_junctions') if r['character_skill_key']==old]
        assert [dict(r,skill_key=old) for r in T['character_skill_level_details'] if r['skill_key']==new]==[r for r in rows('character_skill_level_details') if r['skill_key']==old]
    audits.append(dict(subtype=s,skills=cfg['skills'],starter=cfg['starter'],template=cfg['template'],ability_mapping=amap,effect_mapping=emap,skill_mapping=skillmap,native_mechanics_icons_vfx_unchanged=True))
    print('PREPARED',s,len(amap),'native abilities',flush=True)
# Original general nodes/actions and Da Anh's CB preset are retained exactly.
assert all(r in T['character_skill_nodes'] for r in old_tables['character_skill_nodes'])
assert next(r for r in T['battle_set_piece_armies_characters'] if r['agent_subtype']=='mc_da_anh')==next(r for r in old_tables['battle_set_piece_armies_characters'] if r['agent_subtype']=='mc_da_anh')
keys={r['key'] for r in T['character_skill_nodes']};assert len(keys)==len(T['character_skill_nodes'])
assert all(r['parent_key'] in keys and r['child_key'] in keys for r in T['character_skill_node_links'])
assert all(v.isascii() for v in loc.values())
for t,rs in T.items():
    if not rs:continue
    h,m=copy.deepcopy(headers.get(t) or native(t)[0]);p=internals.get(t,'db/'+t+'_tables/mc_caster_spells');m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
p='text/db/mc_caster_spells.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in sorted(loc.items())])
files.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files])
before=unpack(BASE);after=unpack(PACK);assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items() if p not in files)
assert all(p.startswith(('db/','text/')) for p in files),'No new icon, VFX, animation or model assets'
check=R/'reference/local/moon-casters-v15-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,heroes=audits,roundtrip_passed=True,native_mechanics_icons_vfx_unchanged=True,models_recruitment_stats_da_anh_unchanged=True,each_tree_visible_magic_skills=11,starter_points_per_new_hero=1,custom_battle_spells_enabled=True,deployed=False,runtime_verified=False,existing_save_free_starter_migration_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in v.items() if k!='heroes'},indent=2));assert not blocking
