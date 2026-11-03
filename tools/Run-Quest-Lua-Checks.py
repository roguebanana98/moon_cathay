"""Run authored Lua tests using an existing standalone Lua DLL; no game attach."""
import ctypes,hashlib,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=Path('C:/Program Files/Cheat Engine 7.5/lua53-64.dll')
assert P.is_file()
# Only load the standard Lua library, never the host app or luaclient libraries.
dll=ctypes.CDLL(str(P))
dll.luaL_newstate.argtypes=[];dll.luaL_newstate.restype=ctypes.c_void_p
dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int
dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)];dll.lua_tolstring.restype=ctypes.c_char_p
dll.lua_close.argtypes=[ctypes.c_void_p]
tests=[R/'tools/tests/huyen-ve-quest-chapter1.lua',R/'tools/tests/huyen-ve-quest-chain.lua',R/'tools/tests/huyen-ve-rescue-battle.lua',R/'tools/tests/huyen-ve-quest-rewards.lua',R/'tools/tests/huyen-ve-rescue-native-library.lua',R/'tools/tests/huyen-ve-long-vi-start.lua']
os.chdir(R)
report_paths=[R/'build/huyen-ve-v25-quest-candidate/lua-regression.json',R/'build/huyen-ve-v25-quest-chain/lua-regression.json']
for p in report_paths:
    p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(dict(status='running',native_game_runtime_verified=False)))
for test in tests:
    state=dll.luaL_newstate();assert state
    try:
        dll.luaL_openlibs(state)
        code=test.read_bytes()
        result=dll.luaL_loadbufferx(state,code,len(code),str(test).encode(),'t'.encode())
        if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
        if result:
            error=dll.lua_tolstring(state,-1,None).decode('utf-8','replace')
            for p in report_paths:p.write_text(json.dumps(dict(status='failed',test=str(test),error=error)))
            raise RuntimeError(error)
    finally:dll.lua_close(state)
o=R/'build/huyen-ve-v25-quest-candidate';o.mkdir(exist_ok=True)
report=dict(status='passed',lua_runtime=str(P),lua_runtime_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),tests=[str(t) for t in tests],native_game_runtime_verified=False,notes='Real authored Lua state, campaign adapter and battle script exercised with mocked CA interfaces; standard Lua 5.3 runtime, scripts use 5.1-compatible syntax; does not validate the game engine or battle map.')
report['source_sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((R/'src/script/campaign/mod').glob('mc_huyen_ve_quest_*.lua'))+[R/'src/script/campaign/mod/mc_huyen_ve_start_at_long_vi.lua']}
for p in report_paths:p.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
