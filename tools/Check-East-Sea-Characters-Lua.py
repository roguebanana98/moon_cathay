import ctypes,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R)
dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll');dll.luaL_newstate.restype=ctypes.c_void_p
dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int
dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p;dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
 dll.luaL_openlibs(state);code=(R/'tools/tests/east-sea-characters-start.lua').read_bytes()
 result=dll.luaL_loadbufferx(state,code,len(code),b'edh-character-start-tests',b't')
 if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
 if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)
(R/'build/east-sea-characters/lua-validation.json').write_text(json.dumps(dict(status='passed',cases=22,game_runtime_verified=False),indent=2))
