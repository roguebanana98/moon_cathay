"""V25: gender-compatible campaign art plus existing-save model rebinding."""
import ast,copy,csv,ctypes,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/assault-v25-campaign-appearance';O.mkdir(exist_ok=True)
N=R/'reference/local/lord-vanilla/db';B=R/'reference/local/moonveil-v24-roundtrip';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v24_moonveil_adept.pack';PACK=O/'mc_moonshadow_heroes_v25_assault_campaign.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='fbc216739933f919c87326ed548e772f4148e6e13e432a7e6aa5d727e50af60f'
# Run boundary/old-save tests using the already-installed standalone Lua DLL.
dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll');dll.luaL_newstate.restype=ctypes.c_void_p;dll.luaL_openlibs.argtypes=[ctypes.c_void_p];dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int;dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int;dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p;dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
 dll.luaL_openlibs(state);code=(R/'tools/tests/assault-campaign-appearance.lua').read_bytes();result=dll.luaL_loadbufferx(state,code,len(code),b'assault-appearance-tests',b't')
 if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
 if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)
T={};H={};P={};files=[];dbfiles=[]
def base(t):return read(B/('db/'+t+'_tables/zzzz_mc_moon_generals.tsv'))
def native(t):return read(N/(t+'_tables/data__.tsv'))
art=next(r for r in base('campaign_character_art_sets')[1] if r['art_set_id']=='mc_assault_general_art');male=dict(art,art_set_id='mc_assault_general_art_male',is_male='true',culture='wh3_main_cth_cathay');T['campaign_character_art_sets']=[male]
arts=[r for p in (B/'db/campaign_character_arts_tables').glob('*.tsv') for r in read(p)[1]];assert not any(r['id']=='1986113100' for r in arts+native('campaign_character_arts')[1]);a=next(r for r in arts if r['art_set_id']=='mc_assault_general_art');T['campaign_character_arts']=[dict(a,id='1986113100',art_set_id=male['art_set_id'])]
t='agent_uniforms';H[t],T[t]=base(t);original=copy.deepcopy(T[t]);u=next(r for r in T[t] if r['uniform_name']=='mc_assault_general_uniform');u['campaign_politician_filename']='mc_assault_general';P[t]='db/'+t+'_tables/zzzz_mc_moon_generals'
assert [r for r in original if r['uniform_name']!='mc_assault_general_uniform']==[r for r in T[t] if r['uniform_name']!='mc_assault_general_uniform']
assert all(u[field]=='mc_assault_general' for field in ['filename','battle_filename','campaign_porthole_filename','campaign_politician_filename'])
for t,rs in T.items():
 h,meta=copy.deepcopy(H.get(t) or native(t)[0]);p=P.get(t,'db/'+t+'_tables/mc_assault_campaign_appearance');meta[0]=';'.join(meta[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
 dbfiles.append(p)
for folder in ['units','portholes']:
 settings=json.loads((R/('build/moon-generals-v20/portrait-mc_assault_general-'+folder+'.json')).read_text());settings['entries'][0]['id']=male['art_set_id'];jp=O/('portrait-assault-male-'+folder+'.json');jp.write_text(json.dumps(settings,indent=2));p='ui/portraits/'+folder+'/portrait_settings__mc_assault_campaign_male.bin';(O/p).parent.mkdir(parents=True,exist_ok=True);cli('portrait-settings','from-json','-j',jp,'-b',O/p);files.append(p)
p='script/campaign/mod/mc_assault_campaign_appearance.lua';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/p,O/p);files.append(p)
before=unpack(BASE);assert all(p not in before for p in files);shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles]);cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files]);after=unpack(PACK)
assert set(after)==set(before)|set(files+dbfiles);changed=[p for p in before if after[p]!=before[p]];assert changed==['db/agent_uniforms_tables/zzzz_mc_moon_generals'];assert all(after[p]==b for p,b in before.items() if p not in changed)
# The actual approved 01b mesh/VMD/weapon bytes survive unchanged.
assets=['variantmeshes/variantmeshdefinitions/mc_assault_general.variantmeshdefinition','variantmeshes/variantmeshdefinitions/mc_assault_general_mounted.variantmeshdefinition','variantmeshes/wh_variantmodels/mc_assault_general/body.rigid_model_v2','variantmeshes/wh_variantmodels/mc_assault_general/weapon.rigid_model_v2']
assert all(before[p]==after[p] for p in assets);assert b'humanoid01b\0' in after[assets[2]][:140]
check=R/'reference/local/assault-v25-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check),'script;'+str(check))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1],p
assert (check/files[-1]).read_bytes()==(R/'src'/files[-1]).read_bytes()
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diag=json.loads(text[text.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,lua_boundary_tests_passed=True,existing_save_rebinding=True,male_and_female_art_sets_verified=True,approved_model_and_weapon_unchanged=True,skills_stats_mounts_other_characters_unchanged=True,only_existing_table_changed=changed,script_sha256=sha(R/'src'/files[-1]),runtime_verified=False,deployed=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2));assert not blocking
