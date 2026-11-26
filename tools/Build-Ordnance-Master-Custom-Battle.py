"""V18: rename the existing engineer and give it an explicit Custom Battle character."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-heroes-v18-ordnance-master';O.mkdir(parents=True,exist_ok=True)
B=R/'reference/local/ordnance-master-v18-base';B.mkdir(exist_ok=True)
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v17_master_engineer.pack';PACK=O/'mc_moonshadow_heroes_v18_ordnance_master.pack'
assert not PACK.exists(),'Preserve completed candidate'
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='199413834a0e024b7bcf580dc3ca565689e1d38ab6a823a8ba438972fd599c00'
cli('pack','extract','-p',BASE,'-t',C['schema'],'-F','db;'+str(B),'text;'+str(B))
N=R/'reference/local/lord-vanilla/db';S='Luke_cth_master_engineer';CHAR='mc_ordnance_master_cb_character';T={};H={};P={};files=[]
def native(t):return read(N/(t+'_tables/data__.tsv'))
def one(t,k,v):
    a=[r for r in native(t)[1] if r[k]==v];assert len(a)==1;return dict(a[0])
def load(t):
    p='db/'+t+'_tables/mc_engineer_integrated';H[t],T[t]=read(B/(p+'.tsv'));P[t]=p
load('units_custom_battle_permissions');old_permissions=copy.deepcopy(T['units_custom_battle_permissions'])
uniforms={S:'Luke_cth_master_engineer_emp',S+'_02':'Luke_cth_master_engineer_emp',S+'_03':'Luke_cth_master_engineer_emp',S+'_04':'Luke_cth_master_engineer_emp_02',S+'_05':'Luke_cth_master_engineer_dwf'}
for r in T['units_custom_battle_permissions']:
    assert r['unit'] in uniforms and r['faction']=='wh3_main_cth_cathay_mp'
    r.update(general_unit='false',campaign_exclusive='false',general_uniform=uniforms[r['unit']],set_piece_character=CHAR)
T['battle_set_piece_armies_characters']=[dict(one('battle_set_piece_armies_characters','character_name','wh3_main_cth_cha_astromancer_0'),
    character_name=CHAR,unit_type=S,agent_subtype=S,agent_type='wizard',character_model='354212573',
    portrait='ui/portraits/portholes/wh3_main_cth_cathay/'+S+'.png',forename='1986112700',surname='1986112701',male='true',magic_lore='',character_level='40',skillset='mc_ordnance_master_cb_skills')]
T['battle_set_piece_armies_characters_skillsets']=[dict(key='mc_ordnance_master_cb_skills')]
skills=['engineer_rocket','wh_main_skill_dwf_engineer_self_ballistics_calibration','wh_pro01_skill_grombrindal_flash_bang','wh2_dlc11_skill_cst_gunnery_wight_support_2']
original_node_skills={r['character_skill_key'] for r in read(B/'db/character_skill_nodes_tables/mc_engineer_integrated.tsv')[1]}
assert set(skills)<=original_node_skills
T['battle_set_piece_armies_characters_skillsets_skills']=[dict(skill=s,skillset_key='mc_ordnance_master_cb_skills',sort_order=str(i)) for i,s in enumerate(skills)]
T['names']=[]
for number,donor in [('1986112700','1087565330'),('1986112701','1015096215')]:
    assert not any(r['id']==number for r in native('names')[1]);T['names'].append(dict(one('names','id',donor),id=number,frequency='0',gender='m'))
for t,rs in T.items():
    h,m=copy.deepcopy(H.get(t) or native(t)[0]);p=P.get(t,'db/'+t+'_tables/mc_ordnance_master_cb');m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    assert all(set(r)==set(h) for r in rs),t
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rs])
    files.append(p)
# Update existing localization in place; stable subtype/unit/save keys are retained.
p='text/db/mc_master_engineer.loc';(h,m),loc=read(B/(p+'.tsv'))
changed=[]
for r in loc:
    text=r['text'].replace('Master Engineers','Ordnance Masters').replace('Master Engineer','Ordnance Master')
    if text!=r['text']:changed.append(r['key']);r['text']=text
loc.extend([dict(key='names_name_1986112700',text='Ordnance Master',tooltip='true'),dict(key='names_name_1986112701',text='',tooltip='true')])
assert all(r['text'].isascii() for r in loc)
for suffix in ('','_02','_03','_04','_05'):
    assert next(r['text'] for r in loc if r['key']=='land_units_onscreen_name_'+S+suffix)=='Ordnance Master'
dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in loc])
files.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in files])
before=unpack(BASE);after=unpack(PACK);assert set(after)==set(before)|set(files)
assert all(after[p]==b for p,b in before.items() if p not in files)
check=R/'reference/local/ordnance-master-v18-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'text;'+str(check))
for p in files:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
assert len(T['units_custom_battle_permissions'])==5
assert all(r['set_piece_character']==CHAR and r['general_unit']=='false' and r['general_uniform'] for r in T['units_custom_battle_permissions'])
assert read(B/'db/units_custom_battle_mounts_tables/mc_engineer_integrated.tsv')[1]==read(check/'db/units_custom_battle_mounts_tables/mc_engineer_integrated.tsv')[1]
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,
    display_name='Ordnance Master',stable_subtype=S,cb_faction='wh3_main_cth_cathay_mp',cb_hero_variants=5,cb_mounts=4,cb_skills=skills,cb_character=CHAR,roundtrip_passed=True,
    campaign_stats_skills_recruitment_models_unchanged=True,other_heroes_unchanged=True,standalone_original_mod_not_required=True,changed_localization_keys=changed,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert not blocking
