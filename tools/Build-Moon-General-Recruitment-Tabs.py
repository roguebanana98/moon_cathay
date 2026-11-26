"""V29: use the native CG category for Bastion and a separate Assault category."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v29-general-tabs';O.mkdir(exist_ok=True);B=R/'reference/local/moon-v26-roundtrip'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v26_recruitment_names.pack';PACK=O/'mc_moonshadow_heroes_v29_general_tabs.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='c3b6a083c76d0f1360a4c6a3afef736921c115858fd54a56824c58d6c20d0e79'
paths=[]
for t in ['agent_subtypes','agent_recruitment_categories']:
 p='db/'+t+'_tables/zzzz_mc_moon_generals';(h,meta),rs=read(B/(p+'.tsv'));old=copy.deepcopy(rs)
 if t=='agent_subtypes':
  bastion=next(r for r in rs if r['key']=='mc_bastion_general');bastion['recruitment_category']='wh3_dlc24_cth_celestial_general'
  assert next(r['recruitment_category'] for r in rs if r['key']=='mc_assault_general')=='mc_assault_general'
  for a,b in zip(old,rs):assert {k:v for k,v in a.items() if k!='recruitment_category'}=={k:v for k,v in b.items() if k!='recruitment_category'}
 else:
  rs=[r for r in rs if r['key']!='mc_bastion_general'];assert len(rs)==1 and rs[0]['key']=='mc_assault_general';rs[0]['order']='4'
 dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 paths.append(p)
permissions=read(B/'db/faction_agent_permitted_subtypes_tables/zzzz_mc_moon_generals.tsv')[1]
assert all(next(r['mod_disabled'] for r in permissions if r['subtype']=='wh3_dlc24_cth_celestial_general_'+k)=='true' for k in ['yin','yang'])
assert all(next(r['mod_disabled'] for r in permissions if r['subtype']=='mc_'+k+'_general')=='false' for k in ['assault','bastion'])
before=unpack(BASE);assert 'script/campaign/mod/mc_moon_hide_celestial_general_tab.lua' not in before
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in paths]);after=unpack(PACK)
assert set(after)==set(before);assert {k for k,b in before.items() if after[k]!=b}==set(paths);assert all(after[k]==b for k,b in before.items() if k not in paths)
check=R/'reference/local/moon-v29-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check))
for p in paths:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,bastion_category='wh3_dlc24_cth_celestial_general',native_category_label_unchanged=True,assault_category='mc_assault_general',private_bastion_category_removed=True,native_cg_subtypes_still_disabled=True,no_ui_hiding_script=True,all_other_payloads_unchanged=True,changed_payloads=paths,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2));assert not blocking
