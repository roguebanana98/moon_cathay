"""Private v24 signature item, additive over v23. No shared spell/phase edits."""
import ast,csv,hashlib,json,shutil,struct,subprocess
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
S=json.loads((R/'src/campaign/da-lien-equipment.json').read_text())
N=R/'reference/local/lord-vanilla/db'
O=R/'build/huyen-ve-v24-da-lien-moonstone';O.mkdir(parents=True,exist_ok=True)
BASE=R/'build/huyen-ve-v23-da-lien-skills/mc_huyen_ve_v23_da_lien_skills.pack'
PACK=O/'mc_huyen_ve_v24_da_lien_moonstone.pack'
T=defaultdict(list);cache={};files=[]
def read_path(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],x)) for x in a[2:]]
def native(t):
    if t not in cache:cache[t]=read_path(N/(t+'_tables/data__.tsv'))
    return cache[t]
def one(t,k,v):
    a=[r for r in native(t)[1] if r[k]==v];assert len(a)==1,(t,k,v);return dict(a[0])
def write(t,rs):
    (h,m),_=native(t);m=m.copy();p='db/'+t+'_tables/mc_da_lien_moonstone';m[0]=';'.join(m[0].split(';')[:2]+[p])
    assert all(set(r)==set(h) for r in rs),t
    dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)

item=S['item'];ability=S['ability'];key=item['key'];a=ability['key'];grant='mc_da_lien_enable_moonlit_renewal'
assert not any(r['key']==key for r in native('ancillaries')[1])
anc=one('ancillaries','key','wh3_dlc24_anc_weapon_the_dragons_fang')
anc.update(key=key,type=key+'_type',category=item['category'],unique_to_world='false',unique_to_faction='false',transferrable='false',randomly_dropped='false',can_be_stolen='false',can_be_destroyed='false',uniqueness_score='200')
T['ancillaries']=[anc]
T['ancillary_types']=[dict(type=key+'_type',ui_icon=item['icon'])]
T['ancillary_info']=[dict(ancillary=key)]
T['ancillaries_included_agent_subtypes']=[dict(agent_subtype=S['subtype'],ancillary=key)]
T['battle_set_piece_armies_characters_items']=[dict(character_item=key,character_name=S['unit'])]
T['ancillary_to_effects']=[dict(ancillary=key,effect=e,effect_scope=scope,value=f'{v:.4f}') for e,scope,v in item['effects']]

u=one('unit_abilities','key',ability['native_donor'])
u.update(key=a,requires_effect_enabling='true',uniqueness='wh_main_anc_group_unique',overpower_option='',superseded_abilities_set='')
T['unit_abilities']=[u]
special=one('unit_special_abilities','key',ability['native_donor'])
uid='1800312800';assert not any(x['unique_id']==uid for x in native('unit_special_abilities')[1])
special.update(key=a,unique_id=uid,num_uses=str(ability['uses_per_battle']),mana_cost=f"{ability['winds_cost']:.4f}")
T['unit_special_abilities']=[special]
T['special_ability_to_special_ability_phase_junctions']=[dict(x,special_ability=a) for x in native('special_ability_to_special_ability_phase_junctions')[1] if x['special_ability']==ability['native_donor']]
assert len(T['special_ability_to_special_ability_phase_junctions'])==1
assert T['special_ability_to_special_ability_phase_junctions'][0]['phase']==ability['native_heal_phase']
assert one('special_ability_phases','id',ability['native_heal_phase'])['resurrect']=='false'
T['effects']=[dict(one('effects','effect','wh_dlc05_effect_ability_enable_earth_blood'),effect=grant)]
T['effect_bonus_value_unit_ability_junctions']=[dict(effect=grant,bonus_value_id='enable',unit_ability=a)]
T['land_units_to_unit_abilites_junctions']=[dict(ability=a,land_unit=S['unit'],culture='*')]
ef={x['effect'] for x in native('effects')[1]}|{grant}
assert all(x['effect'] in ef for x in T['ancillary_to_effects'])

# Reference the native ruby artwork directly; prove that exact path exists.
icons=subprocess.run([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(Path(C['game'])/'data/ui.pack')],capture_output=True,text=True,check=True).stdout.splitlines()
assert item['icon'] in icons
assert 'ui/battle ui/ability_icons/'+u['icon_name']+'.png' in icons
for t,rs in T.items():write(t,rs)
loc=[
 ['ancillaries_onscreen_name_'+key,item['name'],'true'],
 ['ancillaries_colour_text_'+key,item['description'],'true'],
 ['unit_abilities_onscreen_name_'+a,ability['name'],'true'],
 ['unit_abilities_tooltip_text_'+a,'Restores health to up to 4 friendly units within 35m for 7 seconds. Range: 200m. One use per battle; no Winds of Magic cost. Does not resurrect fallen models. Requires Crimson Moonstone.','true'],
 ['effects_description_'+grant,'Bound ability: Moonlit Renewal','true']]
assert all(x[1].isascii() for x in loc)
p='text/db/mc_da_lien_moonstone.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)
p='script/campaign/mod/mc_da_lien_crimson_moonstone.lua';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,dest);files.append(p)

assert not PACK.exists(),'Protect existing candidate'
shutil.copy2(BASE,PACK)
for p in files:
    tab=p.startswith('db/') or p.endswith('.loc');args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',str(PACK)]
    if tab:args+=['-t',C['schema']]
    subprocess.run(args+['-f',str(O/(p+('.tsv' if tab else '')))+';'+p],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(BASE);after=unpack(PACK)
assert not set(files)&set(before)
assert set(after)==set(before)|set(files) and all(after[p]==b for p,b in before.items())
assert not any('ownership_content_pack_junctions_tables/' in p for p in after)
check=R/'reference/local/da-lien-v24-check';check.mkdir(exist_ok=True)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(PACK),'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check)],check=True,stdout=subprocess.DEVNULL)
for p in files:
    if p.startswith('db/') or p.endswith('.loc'):assert read_path(O/(p+'.tsv'))[1]==read_path(check/(p+'.tsv'))[1],p
    else:assert after[p]==(O/p).read_bytes()
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(R/'reference/local/wh3-diagnostics.pak2'),'-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(BASE.parent/'diagnostics.txt');new=diagnostic_rows(O/'diagnostics.txt');blocking=[];metadata=[]
for path,reports in new.items():
    if old.get(path)==reports:continue
    for row in reports:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in row['cells_affected']):metadata.append(dict(path=path,report=row))
        else:blocking.append(dict(path=path,report=row))
(O/'diagnostics-review.json').write_text(json.dumps(dict(metadata=metadata,blocking=blocking),indent=2))
assert not blocking,blocking
v=dict(status='static_checks_passed',pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),files=files,new_payloads=len(files),existing_payloads_unchanged=True,new_blocking_diagnostics=0,new_schema_metadata_warnings=len(metadata),item=key,ability=a,uses_per_battle=1,winds_cost=0,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
