"""Add three casters and Da Anh to Cathay Custom Battle; campaign stays identical."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-heroes-v14-custom-battle';O.mkdir(parents=True,exist_ok=True)
N=R/'reference/local/lord-vanilla/db';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v13_three_casters.pack'
PACK=O/'mc_moonshadow_heroes_v14_custom_battle.pack';assert not PACK.exists(),'Preserve completed candidate'
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='841d7c91ccab5c97442d9538189e8f4db6a6ec4449c9f8debaf35cd3c31842ea'
cache={};T=defaultdict(list);loc={};files=[]
def native(t):
    if t not in cache:cache[t]=read(N/(t+'_tables/data__.tsv'))
    return cache[t]
def one(t,f,v):
    a=[r for r in native(t)[1] if r[f]==v];assert len(a)==1,(t,f,v);return dict(a[0])
entries=[('mc_pyromancer','Pyromancer',1986112300),('mc_astral_weaver','Astral Weaver',1986112301),('mc_tidecaller','Tidecaller',1986112302),('mc_da_anh','Da Anh',1986112101)]
before=unpack(BASE)
for i,(s,name,art) in enumerate(entries):
    u=s+'_human';wizard=s!='mc_da_anh';donor='wh3_main_cth_cha_astromancer_0' if wizard else 'wh2_main_def_cha_khainite_assassin_0'
    portrait='ui/portraits/portholes/no_culture/'+s+'_0.png';assert portrait in before
    candidates=[r for r in native('units_custom_battle_permissions')[1] if r['unit']==donor and r['general_unit']=='false']
    assert len(candidates)==1
    T['units_custom_battle_permissions'].append(dict(candidates[0],faction='wh3_main_cth_cathay_mp',unit=u,set_piece_character=u,general_portrait=portrait,general_uniform=s+'_uniform',campaign_exclusive='false'))
    char=one('battle_set_piece_armies_characters','character_name',donor)
    first=str(1986112400+2*i);last=str(1986112401+2*i)
    for number,kind,donor_name,text in [(first,'forename',char['forename'],name),(last,'family_name',char['surname'],'')]:
        assert not any(r['id']==number for r in native('names')[1])
        assert not any(number.encode() in b for p,b in before.items() if p.startswith(('db/names_tables/','text/')))
        n=one('names','id',donor_name);n.update(id=number,gender='f',frequency='0');assert n['type']==kind
        T['names'].append(n);loc['names_name_'+number]=text
    char.update(character_name=u,unit_type=u,agent_subtype=s,agent_type='wizard' if wizard else 'spy',portrait=portrait,character_model=str(art),forename=first,surname=last,male='false',magic_lore='',skillset='' if wizard else 'mc_da_anh_cb_skills',character_level='1' if wizard else '40')
    T['battle_set_piece_armies_characters'].append(char)
    T['units_to_groupings_military_permissions'].append(dict(unit=u,military_group='wh3_main_cth'))
T['battle_set_piece_armies_characters_skillsets']=[dict(key='mc_da_anh_cb_skills')]
skills=['mc_da_anh_veil','mc_da_anh_execution','mc_da_anh_last_shadow']
T['battle_set_piece_armies_characters_skillsets_skills']=[dict(skill=s,skillset_key='mc_da_anh_cb_skills',sort_order=str(i)) for i,s in enumerate(skills)]
# Explicitly no caster lore, army skill, campaign point or capacity mutation.
assert len(T['units_custom_battle_permissions'])==4 and all(r['general_unit']=='false' for r in T['units_custom_battle_permissions'])
assert all(r['magic_lore']=='' for r in T['battle_set_piece_armies_characters'])
assert all(not r['skillset'] for r in T['battle_set_piece_armies_characters'] if r['agent_type']=='wizard')
for t,rs in T.items():
    h,m=copy.deepcopy(native(t)[0]);p='db/'+t+'_tables/mc_moon_heroes_custom_battle';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
p='text/db/mc_moon_heroes_custom_battle.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
assert all(v.isascii() for v in loc.values())
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+[[k,v,'true'] for k,v in loc.items()])
files.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files])
after=unpack(PACK);assert not set(files)&set(before)
assert set(after)==set(before)|set(files) and all(after[p]==data for p,data in before.items())
check=R/'reference/local/moon-heroes-v14-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,existing_payloads_unchanged=True,campaign_unchanged=True,roundtrip_passed=True,custom_battle_units=[s+'_human' for s,_,_ in entries],custom_battle_faction='wh3_main_cth_cathay_mp',hero_entries=True,da_anh_custom_skills=skills,caster_spells_pending=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert not blocking
