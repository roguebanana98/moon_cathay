import ctypes,hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);O=R/'build/sariwa-campaign-appearance';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text())
dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll');dll.luaL_newstate.restype=ctypes.c_void_p;dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int
dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p;dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
 dll.luaL_openlibs(state);code=(R/'tools/tests/sariwa-campaign-appearance.lua').read_bytes();result=dll.luaL_loadbufferx(state,code,len(code),b'sariwa-appearance-tests',b't')
 if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
 if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)
script=R/'src/script/campaign/mod/edh_sariwa_campaign_appearance.lua';assert hashlib.sha256(script.read_bytes()).hexdigest()==v['script_sha256']
p=subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',v['pack']],capture_output=True,text=True);(O/'diagnostics.txt').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0
d=json.loads(p.stdout[p.stdout.index('{'):]);counts={}
for group in d['results']:
 for issue in next(iter(group.values())).get('results',[]):
  typ=issue['report_type'];assert isinstance(typ,dict) and set(typ) in [{'NoReferenceTableNorColumnFoundNoPak'},{'FileOverwrite'}],issue
  key=next(iter(typ));counts[key]=counts.get(key,0)+1
v.update(static_validation='passed',lua_boundary_tests='passed',diagnostic_counts=counts,unexpected_diagnostics=0,runtime_verified=False)
(O/'build-report.json').write_text(json.dumps(v,indent=2));print('PASS: script and pack checks; no unexpected diagnostics',counts)
