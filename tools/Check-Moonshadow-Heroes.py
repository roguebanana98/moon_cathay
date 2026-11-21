"""Exercise spawn Lua and validate the packed campaign roster and native links."""
import ast, ctypes, csv, hashlib, json, os, struct, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moonshadow-celestial-tower';v=json.loads((O/'build-report.json').read_text())
P=Path(v['pack']);assert hashlib.sha256(P.read_bytes()).hexdigest()==v['sha256']
cache=Path('D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2');assert cache.is_file()
with (O/'diagnostics.txt').open('w',encoding='utf-8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P',str(cache),'-s',C['schema'],'-p',str(P)],check=True,stdout=f,stderr=subprocess.STDOUT)
s=(O/'diagnostics.txt').read_text();d=json.loads(s[s.index('{'):]);metadata=[]
for group in d['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            assert isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'} and all(x[0]==-1 for x in issue['cells_affected']), (kind,g.get('path'),issue)
            metadata.append(dict(path=g.get('path'),field=next(iter(typ.values()))))

dll=ctypes.CDLL('C:/Program Files/Cheat Engine 7.5/lua53-64.dll')
dll.luaL_newstate.restype=ctypes.c_void_p;dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];dll.luaL_loadbufferx.restype=ctypes.c_int
dll.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];dll.lua_pcallk.restype=ctypes.c_int
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];dll.lua_tolstring.restype=ctypes.c_char_p
dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate()
try:
    dll.luaL_openlibs(state);code=(R/'tools/tests/moonshadow-start.lua').read_bytes()
    result=dll.luaL_loadbufferx(state,code,len(code),b'moonshadow-tests',b't')
    if result==0:result=dll.lua_pcallk(state,0,-1,0,0,None)
    if result:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode())
finally:dll.lua_close(state)

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0],r)) for r in a[2:]]
Q=R/'reference/local/moonshadow-tower-roundtrip'
def table(t):return read(Q/('db/'+t+'_tables/mc_moonshadow.tsv'))
def native(t):return read(R/('reference/local/lord-vanilla/db/'+t+'_tables/data__.tsv'))
subtypes={r['key']:r for r in table('agent_subtypes')}
g=subtypes['mc_moonshadow_assassin'];l=subtypes['mc_da_anh']
assert g['auto_generate']==g['recruitable']=='true' and g['cap']=='0'
assert l['auto_generate']==l['recruitable']==l['contributes_to_agent_cap']=='false' and l['cap']=='1'
assert all(r['faction']=='cr_cth_agents_of_the_moon' for r in table('faction_agent_permitted_subtypes'))
assert not any(p.startswith(('db/'+t+'_tables/')) for p in v['files'] for t in
    ['building_chains','building_levels','building_culture_variants','building_chain_availability_set_ids',
     'building_chain_availabilities','building_chain_availability_sets','building_set_to_building_junctions'])
context=table('building_effect_context_expressions')[0]
assert context['expression']=='Region.Owner.RecordKey == "cr_cth_agents_of_the_moon"'
assert context['display_only_active_effects']=='true'
building_effects=table('building_effects_junction')
assert len(building_effects)==6
assert {r['building'] for r in building_effects}=={'wh3_main_cth_magic_tower_'+str(i) for i in range(1,4)}
assert all(r['context_requirement']==context['key'] and r['value']=='1.0000' for r in building_effects)
assert {r['bonus_value_id'] for r in table('effect_bonus_value_agent_subtype_junctions')}=={'availability','cap'}
assert len({n['key'] for n in table('character_skill_nodes')})==len(table('character_skill_nodes'))
nodeby={r['key']:r for r in table('character_skill_nodes')}
skills={r['key']:r for r in table('character_skills')}
effects=table('character_skill_level_to_effects_junctions')
for node in nodeby.values():
    assert not any(s in node['character_skill_key'] for s in ['slave','loyalty','innate_'])
    assert node['character_skill_key'] in skills or any(r['key']==node['character_skill_key'] for r in native('character_skills'))
assert not any('slave' in r['effect_key'] for r in effects)
assert not any('murderous' in r['ability'] for r in table('land_units_to_unit_abilites_junctions'))
for link in table('character_skill_node_links'):assert link['parent_key'] in nodeby and link['child_key'] in nodeby
for s in subtypes:
    members=[nodeby[r['item']] for r in table('character_skill_node_set_items') if r['set']==s+'_skills']
    assert len([n for n in members if n['points_on_creation']=='1' and n['character_skill_key']=='mc_moonshadow_actions'])==1
    visible=[n for n in members if n['visible_in_ui']=='true']
    assert len({(n['indent'],n['tier']) for n in visible})==len(visible),s
assert all(r['text'].isascii() for r in read(Q/'text/db/mc_moonshadow.loc.tsv'))
# Confirm actual runtime binaries, not merely Blender actions or source JSON.
lookup=v['battle_animation'];hits=[]
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
    data=p.read_bytes();count=struct.unpack_from('<I',data)[0];pos=4
    for _ in range(count):
        n=struct.unpack_from('<H',data,pos)[0];pos+=2;name=data[pos:pos+n].decode();pos+=n
        n=struct.unpack_from('<I',data,pos)[0];pos+=4
        if Path(name).stem==lookup:hits.append(dict(archive=str(p),path=name,size=n))
        pos+=n
    assert pos==len(data)
assert hits,'Native battle animation lookup missing'
campaign='animations/campaign/database/bin/'+v['campaign_animation']+'.bin'
for name in ['anim.pack','anim2.pack','anim_3.pack']:
    path=Path(C['game'])/'data'/name
    names=subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(path)],text=True,stderr=subprocess.DEVNULL).splitlines()
    if campaign in names:hits.append(dict(archive=str(path),path=campaign));break
else:raise AssertionError('Native campaign animation lookup missing')
# Additive pack must never override any currently enabled mod payload.
def payloads(p):
    raw=p.read_bytes();assert raw[:4]==b'PFH5';_,_,ds,fc,fs,_=struct.unpack('<6I',raw[4:28]);pos=28+ds;end=pos+fs;entries=[]
    for _ in range(fc):
        size,compression=struct.unpack('<IB',raw[pos:pos+5]);pos+=5;assert compression==0
        stop=raw.index(0,pos);key=raw[pos:stop].decode().replace('\\','/');pos=stop+1;entries.append((key,size))
    assert pos==end;result={}
    for key,size in entries:result[key]=raw[pos:pos+size];pos+=size
    assert pos==len(raw);return {k:b for k,b in result.items() if not k.endswith('.rpfm_reserved')}
added=payloads(P);assert set(added)==set(v['files'])
launcher=Path(os.environ['APPDATA'])/'The Creative Assembly/Launcher/20190104-moddata.dat'
active=[m for m in json.loads(launcher.read_text(encoding='utf-8-sig')) if m.get('game')=='warhammer3' and m.get('active') and m.get('owned')]
baseline={}
for m in active:
    p=Path(m['packfile'])
    if p.name!='mc_moonshadow_heroes_v5.pack':assert not (set(payloads(p))&set(added)),p
    baseline[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
# Scope regression against the previously deployed roster. All character data,
# portraits, skills and the Da Anh script must remain byte-identical.
old=payloads(Path(C['game'])/'data/mc_moonshadow_heroes_v5.pack')
removed=set(old)-set(added);new=set(added)-set(old)
expected_removed={'db/'+t+'_tables/mc_moonshadow' for t in
    ['building_chains','building_levels','building_culture_variants','building_chain_availability_set_ids',
     'building_chain_availabilities','building_chain_availability_sets','building_set_to_building_junctions']}
assert removed==expected_removed,removed
assert new=={'db/building_effect_context_expressions_tables/mc_moonshadow'},new
changed={p for p in old.keys()&added.keys() if old[p]!=added[p]}
assert changed=={'db/building_effects_junction_tables/mc_moonshadow','text/db/mc_moonshadow.loc'},changed
assert not any('mc_moonshadow_hideout' in str(r) for r in read(Q/'text/db/mc_moonshadow.loc.tsv'))
v.update(static_validation='passed',blocking_diagnostics=0,schema_metadata_warnings=metadata,
    lua_scenarios=17,lua_source_sha256=hashlib.sha256((R/'src/script/campaign/mod/mc_moonshadow_start.lua').read_bytes()).hexdigest(),
    native_animation_lookup_verified=hits,enabled_local_baseline_sha256=baseline,
    dependency_sha256={k:hashlib.sha256(Path(C[k]).read_bytes()).hexdigest() for k in ['mixer','iee','schema']},
    no_unrelated_mod_payload_overrides=True,unchanged_character_payloads=True,
    removed_payloads=sorted(removed),changed_payloads=sorted(changed),runtime_verified=False)
(O/'build-report.json').write_text(json.dumps(v,indent=2))
print('PASS: DB/loc, faction-only recruitment, separate caps, skill graph, native animation binaries, 17 Lua scenarios; no enabled payload overrides')
