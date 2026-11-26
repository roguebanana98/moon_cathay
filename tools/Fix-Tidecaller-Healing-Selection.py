"""V16: expose Tidecaller's six spells in one native-style composite UI group."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/tidecaller-v16-healing-selection';O.mkdir(parents=True,exist_ok=True)
B=R/'reference/local/tidecaller-v16-base';B.mkdir(exist_ok=True)
N=R/'reference/local/lord-vanilla/db'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v15_caster_spells.pack'
PACK=O/'mc_moonshadow_heroes_v16_tidecaller_healing.pack';assert not PACK.exists(),'Preserve existing build'
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='f760fa5fc705efaa12c945805a4076e5e8f2bb5cd4d4ee717ba2c79d44868648'
cli('pack','extract','-p',BASE,'-t',C['schema'],'-F','db;'+str(B),'text;'+str(B))
T={};H={};P={};files=[]
def load(t,name):
    p='db/'+t+'_tables/'+name;H[t],T[t]=read(B/(p+'.tsv'));P[t]=p
for t in ('special_ability_groups','special_ability_groups_to_unit_abilities_junctions','special_ability_groups_to_units_junctions'):
    load(t,'mc_caster_spells')
load('battle_set_piece_armies_characters','mc_moon_heroes_custom_battle')
old=copy.deepcopy(T)
combined='mc_tidecaller_lore_combined';unit='mc_tidecaller_human';sources=['mc_tidecaller_lore','mc_tidecaller_lore_life']
native=read(N/'special_ability_groups_tables/data__.tsv')[1]
assert next(r for r in native if r['ability_group']=='wh2_main_lore_teclis')['is_composite_group']=='true'
uids={r['unique_id'] for r in native+T['special_ability_groups']}
for upgraded in (False,True):
    suffix='_upgraded' if upgraded else '';group=combined+suffix
    donor=next(r for r in T['special_ability_groups'] if r['ability_group']==sources[0]+suffix)
    uid=str(1800316600+int(upgraded));assert uid not in uids
    T['special_ability_groups'].append(dict(donor,ability_group=group,is_composite_group='true',sort_order='0',unique_id=uid))
    members={r['unit_special_abilities'] for r in old['special_ability_groups_to_unit_abilities_junctions'] if r['special_ability_groups'] in [s+suffix for s in sources]}
    assert len(members)==(6 if upgraded else 7),(upgraded,members)
    T['special_ability_groups_to_unit_abilities_junctions'].extend(dict(special_ability_groups=group,unit_special_abilities=a) for a in sorted(members))
T['special_ability_groups_to_units_junctions']=[r for r in T['special_ability_groups_to_units_junctions'] if r['unit']!=unit]
T['special_ability_groups_to_units_junctions'].append(dict(ability_group=combined,unit=unit,group_page_order='0'))
next(r for r in T['battle_set_piece_armies_characters'] if r['character_name']==unit)['magic_lore']=combined
# Regression: validate the actual CB-selected group, not the union of all unit groups.
v15=json.loads((R/'build/moon-casters-v15-spells/pack-validation.json').read_text(encoding='utf8'))
hero=next(h for h in v15['heroes'] if h['subtype']=='mc_tidecaller')
char=next(r for r in T['battle_set_piece_armies_characters'] if r['character_name']==unit)
visible={r['unit_special_abilities'] for r in T['special_ability_groups_to_unit_abilities_junctions'] if r['special_ability_groups']==char['magic_lore']}
heals={name:hero['ability_mapping'][key] for name,key in [('Restorative Waters','wh_dlc05_spell_life_earth_blood'),('Renewing Tide','wh_dlc05_spell_life_regrowth')]}
assert set(heals.values())<=visible
assert [r for r in T['special_ability_groups_to_units_junctions'] if r['unit']==unit]==[dict(ability_group=combined,unit=unit,group_page_order='0')]
assert [r for r in T['battle_set_piece_armies_characters'] if r['character_name']!=unit]==[r for r in old['battle_set_piece_armies_characters'] if r['character_name']!=unit]
assert dict(char,magic_lore='mc_tidecaller_lore')==next(r for r in old['battle_set_piece_armies_characters'] if r['character_name']==unit)
for t,rs in T.items():
    h,m=copy.deepcopy(H[t]);p=P[t];dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
p='text/db/mc_tidecaller_combined.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[['special_ability_groups_name_'+combined+s,'Lore of the Tides','true'] for s in ('','_upgraded')])
files.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files])
before=unpack(BASE);after=unpack(PACK)
assert set(after)==set(before)|set(files) and all(after[p]==b for p,b in before.items() if p not in files)
assert all(not p.startswith(('variantmeshes/','ui/','animations/')) for p in files)
check=R/'reference/local/tidecaller-v16-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
# Verify both healing unlock skills are present in the actual character's CB preset.
def table(t,name='mc_caster_spells'):return read(check/('db/'+t+'_tables/'+name+'.tsv'))[1]
preset={r['skill'] for r in table('battle_set_piece_armies_characters_skillsets_skills','mc_moon_heroes_custom_battle') if r['skillset_key']==char['skillset']}
effects=table('character_skill_level_to_effects_junctions');bonus=table('effect_bonus_value_unit_ability_junctions')
for name,native_skill in [('Restorative Waters','wh_dlc05_skill_magic_life_wizard_earth_blood'),('Renewing Tide','wh_dlc05_skill_magic_life_wizard_regrowth')]:
    skill=hero['skill_mapping'][native_skill];assert skill in preset
    enabled={r['effect_key'] for r in effects if r['character_skill_key']==skill and r['level']=='1' and float(r['value'])>0}
    assert any(r['effect'] in enabled and r['unit_ability']==heals[name] and r['bonus_value_id']=='enable' for r in bonus)
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,cb_selected_group=combined,healing_abilities_in_selected_group=heals,base_group_members=len(visible),single_visible_spell_group=True,native_source_groups_preserved_for_modifiers=True,spell_mechanics_icons_vfx_skills_models_unchanged=True,other_heroes_unchanged=True,cb_healing_unlocks_verified=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert not blocking
