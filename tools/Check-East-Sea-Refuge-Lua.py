import ctypes,hashlib,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);O=R/'build/east-sea-refuge';O.mkdir(exist_ok=True)
dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll');dll.luaL_newstate.restype=ctypes.c_void_p;dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int
dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p;dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
 dll.luaL_openlibs(state);code=(R/'tools/tests/east-sea-refuge.lua').read_bytes();result=dll.luaL_loadbufferx(state,code,len(code),b'edh-refuge-tests',b't')
 if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
 if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)
(O/'lua-validation.json').write_text(json.dumps(dict(status='passed',world_scenarios=15,source_sha256=hashlib.sha256((R/'src/script/campaign/mod/edh_east_sea_charter_refuge.lua').read_bytes()).hexdigest(),game_runtime_verified=False,mock_boundary_only=True),indent=2))
