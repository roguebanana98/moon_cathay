"""V28: guard hero recruitment while hiding the empty native Celestial General category only for Moon campaign UI."""
raise RuntimeError("RETIRED after live UI crash: tab-hiding prototype must not be built or deployed")
import ast,csv,ctypes,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];os.chdir(R);C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v28-celestial-tab-guard';O.mkdir(exist_ok=True)
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v27_hide_celestial_tab.pack';PACK=O/'mc_moonshadow_heroes_v28_hide_celestial_tab.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='e5aeb9c85ba93aca81af278b36433d8664883f1902e952d579f75de2d0b7fe8a'
layout=ET.parse(R/'reference/local/moon-recruitment-ui/ui/campaign ui/character_panel.twui.xml');assert layout.find('./hierarchy/root/character_panel/character_panel_info_holder/lords_and_agents_holder/lord_parent/list_box') is not None
assert layout.find('./hierarchy/root/character_panel/character_panel_info_holder/lords_and_agents_holder/lord_parent/list_box/button_template_lord/label') is not None
permission=read(R/'reference/local/moon-v26-roundtrip/db/faction_agent_permitted_subtypes_tables/zzzz_mc_moon_generals.tsv')[1]
assert all(next(r['mod_disabled'] for r in permission if r['subtype']=='wh3_dlc24_cth_celestial_general_'+s)=='true' for s in ['yang','yin'])
assert all(next(r['mod_disabled'] for r in permission if r['subtype']=='mc_'+s+'_general')=='false' for s in ['assault','bastion'])
dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll');dll.luaL_newstate.restype=ctypes.c_void_p;dll.luaL_openlibs.argtypes=[ctypes.c_void_p];dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int;dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int;dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p;dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
 dll.luaL_openlibs(state);code=(R/'tools/tests/moon-hide-celestial-general-tab.lua').read_bytes();result=dll.luaL_loadbufferx(state,code,len(code),b'moon-recruitment-ui-tests',b't')
 if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
 if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)
p='script/campaign/mod/mc_moon_hide_celestial_general_tab.lua';shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-f',str(R/'src'/p)+';'+p);before=unpack(BASE);after=unpack(PACK)
assert set(after)==set(before) and [k for k,b in before.items() if after[k]!=b]==[p];assert after[p]==(R/'src'/p).read_bytes()
check=R/'reference/local/moon-v28-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-f',p+';'+str(check));assert (check/p).read_bytes()==after[p]
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group in diag['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
v=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,lua_ui_boundary_tests_passed=True,native_layout_path_verified=True,moon_faction_only=True,other_factions_categories_unchanged=True,assault_bastion_tabs_preserved=True,all_other_payloads_unchanged=True,changed_payload=p,hero_recruitment_guard_verified=True,no_global_ui_or_category_overrides=True,deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2));assert not blocking
