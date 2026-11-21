"""Read-only audit of the game's own QA save; never encodes or edits a save."""
import collections,hashlib,importlib.util,json,lzma,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from inspect_esf import Reader,walk
O=R/'build/east-sea-faction';S=json.loads((R/'src/campaign/east-sea-charter.json').read_text())
saves=list((O/'qa-created-saves').glob('*.save'));assert len(saves)==1
p=saves[0];digest=hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
d=b.Document(p.read_bytes());top,_=d.decode(16)
print('Read native save container',flush=True)
compressed=next(n for n in walk(top) if n['name']=='COMPRESSED_DATA');payload,info=compressed['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE);d=b.Document(raw)
print('Decompressed native save:',len(raw),'bytes',flush=True)
def records(name):
 idx=d.r.names.index(name)
 tags=bytes(0x80 | (idx>>8) | (version<<1) for version in range(16))
 pattern=b'['+re.escape(tags)+b']'+re.escape(bytes([idx&255]))
 positions={m.start() for m in re.finditer(pattern,raw)}
 positions.update(m.start() for m in re.finditer(re.escape(b'\xa0'+struct.pack('<H',idx)),raw))
 found={}
 for pos in sorted(positions):
  try:
   _,count,a,end,n,_=d.header(pos)
   if n!=name or count is not None or end>len(raw):continue
   if raw[a] not in (8,0x14,0x15,0x16,0x17,0x18,0x19):continue
   ident,z=d.decode(a)
   if not isinstance(ident,int) or raw[z]!=15:continue
   key,_=d.decode(z)
   if not isinstance(key,str):continue
   if name=='FACTION' and key not in [S['faction_key'],S['previous_owner']]:continue
   if name=='REGION' and not key.startswith(('cr_combi_region_','wh3_main_combi_region_','wh3_dlc')):continue
   if name=='REGION':
    fields=[];cursor=a
    for i in range(9):
     if raw[cursor]&128:
      fields.append(None);cursor=d.header(cursor)[3]
     else:
      value,cursor=d.decode(cursor);fields.append(value)
    found[key]={'name':name,'groups':[fields]}
   else:
    node,_=d.decode(pos);found[key]=node
  except (AssertionError,ValueError,IndexError,KeyError,struct.error):continue
 return found
factions=records('FACTION');print('Located faction records',flush=True)
regions=records('REGION');print('Located region owner fields',len(regions),flush=True)
f=factions[S['faction_key']];moon=factions[S['previous_owner']]
owned=sorted(key for key,n in regions.items() if n['groups'][0][8]==f['groups'][0][0])
moon_owned=sorted(key for key,n in regions.items() if n['groups'][0][8]==moon['groups'][0][0])
assert owned==sorted(S['regions']),owned
assert moon_owned==sorted(['cr_combi_region_long_vi','cr_combi_region_leilou']),moon_owned
def capital_id(faction):
 g=faction['groups'][0]
 army_index=next(i for i,v in enumerate(g) if isinstance(v,dict) and v.get('name')=='ARMY_ARRAY')
 # Human saves insert mission/shroud nodes absent from AI/static records.
 return next(v for v in g[army_index+1:] if type(v) is int)
assert capital_id(f)==regions[S['capital']]['groups'][0][0]
inspection={key:[v if not isinstance(v,dict) else v.get('name') for v in n['groups'][0][:23]] for key,n in factions.items()}
(O/'save-capital-fields.json').write_text(json.dumps(dict(factions=inspection,region_ids={k:n['groups'][0][0] for k,n in regions.items() if k in S['regions']+[S['previous_owner_capital']]}),indent=2))
assert capital_id(moon)==regions[S['previous_owner_capital']]['groups'][0][0]
def child(n,key):return next(v for v in n['groups'][0] if isinstance(v,dict) and v.get('name')==key)
def force_units(force):return [k for n in walk(force) if n['name']=='UNIT_RECORD_KEY' for k in n['groups'][0]]
armies=child(f,'ARMY_ARRAY')
forces=[force_units(n) for n in walk(armies) if n['name']=='MILITARY_FORCE']
field_armies=[ks for ks in forces if 'wh_main_emp_cha_general_0' in ks]
assert len(field_armies)==1
unit_keys=field_armies[0]
base_doc=b.Document((O/'base.raw.esf').read_bytes());base_force,_=base_doc.decode(27576827)
assert base_force['name']=='MILITARY_FORCE'
assert collections.Counter(unit_keys)==collections.Counter(force_units(base_force))+collections.Counter(S['army']),unit_keys
assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
qa=json.loads((O/'qa-session.json').read_text());assert qa['status']=='restored'
report=dict(status='passed',source_save=str(p),sha256=digest,read_only=True,
 game_version='9.0.5 / 51143.4399233',faction=S['display_name'],technical_key=S['faction_key'],
 regions=owned,capital=S['capital'],moon_regions=moon_owned,moon_capital=S['previous_owner_capital'],
 army_units=unit_keys,garrison_force_count=len(forces)-1,original_save_files_preserved=qa['original_save_hashes_verified'],
 runtime_new_campaign_verified=True,native_save_persistence_verified=True,engine_reload_tested=False,end_turn_tested=False,
 ui_evidence=['East Sea Charter shown under The Empire with 2 settlements','Preenn tooltip names East Sea Charter / The Empire','Dai Loa and Preenn province slots show new Empire flag; Avauka retains Snakebiters flag','Huyen Ve shown beside Moon-owned Long Vi'],
 native_warnings='Existing minor-faction intro and narrative warnings observed; no East Sea Charter initialization exception. One transient foreign-trespasser event occurs while repositioning before transfer.')
(O/'runtime-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
