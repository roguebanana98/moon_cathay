"""V19: correct all five engineer UI groups from commander to heroes_agents."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/ordnance-master-v19-hero-category';O.mkdir(parents=True,exist_ok=True)
B=R/'reference/local/ordnance-master-v19-base';B.mkdir(exist_ok=True)
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v18_ordnance_master.pack';PACK=O/'mc_moonshadow_heroes_v19_hero_category.pack'
assert not PACK.exists(),'Preserve completed build'
tree=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='7efa84399e3014fefdd77769bac8ec979d8c37e00550b4ceea42fe778502af2a'
p='db/main_units_tables/mc_engineer_integrated'
cli('pack','extract','-p',BASE,'-t',C['schema'],'-f',p+';'+str(B))
(h,m),rows=read(B/(p+'.tsv'));old=copy.deepcopy(rows)
assert len(rows)==5
for r in rows:
    assert r['unit'].startswith('Luke_cth_master_engineer') and r['caste']=='hero'
    assert r['ui_unit_group_land']=='wh3_dlc24_cth_cha_celestial_general'
    r['ui_unit_group_land']='emp_engineer'
    assert dict(r,ui_unit_group_land='wh3_dlc24_cth_cha_celestial_general')==next(x for x in old if x['unit']==r['unit'])
native=read(R/'reference/local/lord-vanilla/db/ui_unit_groupings_tables/data__.tsv')[1]
group=next(r for r in native if r['key']=='emp_engineer');assert group['parent_group']=='heroes_agents'
dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,m]+[[r[k] for k in h] for r in rows])
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',str(dest)+';'+p)
before=unpack(BASE);after=unpack(PACK)
assert set(before)==set(after) and [x for x in before if before[x]!=after[x]]==[p]
check=R/'reference/local/ordnance-master-v19-roundtrip';check.mkdir(exist_ok=True)
cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check))
assert read(check/(p+'.tsv'))[1]==rows
perm=read(check/'db/units_custom_battle_permissions_tables/mc_engineer_integrated.tsv')[1]
assert len(perm)==5 and all(r['general_unit']=='false' and r['campaign_exclusive']=='false' for r in perm)
assert {r['unit'] for r in perm}=={r['unit'] for r in rows}
assert all(r['caste']=='hero' and next(g for g in native if g['key']==r['ui_unit_group_land'])['parent_group']=='heroes_agents' for r in rows)
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text(encoding='utf8');diag=json.loads(text[text.index('{'):]);blocking=[]
for item in diag['results']:
    for kind,g in item.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,
       changed_payload=p,only_changed_field='ui_unit_group_land',variants=5,category='emp_engineer',parent_group='heroes_agents',hero_flags_and_permissions_verified=True,
       stats_models_skills_recruitment_unchanged=True,roundtrip_passed=True,standalone_original_mod_not_required=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert not blocking
