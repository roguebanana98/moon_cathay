import csv,hashlib,importlib.util,json,lzma,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
O=R/'build/east-sea-faction';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text());pack=Path(v['pack'])
Q=R/'reference/local/edh-faction-roundtrip'
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-t',C['schema'],'-F','/;'+str(Q)],check=True,capture_output=True)
def table(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
for p in v['files']:
 if p.startswith(('db/','text/')):
  a=table(O/(p+'.tsv'));z=table(Q/(p+'.tsv'))
  assert a[0]==z[0] and a[2:]==z[2:],p
script='script/campaign/mod/edh_east_sea_charter_start.lua'
assert (Q/script).read_bytes()==(R/'src'/script).read_bytes()
outer=b.Document((Q/'campaigns/cr_combi_expanded/startpos.esf').read_bytes());top,_=outer.decode(16)
n=next(n for n in b.walk(top) if n['name']=='COMPRESSED_DATA');payload,info=n['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE)
old=(O/'base.raw.esf').read_bytes();d=b.Document(raw);baseline=b.Document(old);patches={}
for pos in [27576787,27578529]:
 name=baseline.header(pos)[4];hits=[]
 for near in range(pos-200,pos+200):
  try:
   if d.header(near)[4]==name:hits.append(near)
  except (AssertionError,IndexError,ValueError,struct.error,KeyError):pass
 assert len(hits)==1,(name,hits)
 patches[hits[0]]=old[pos:baseline.header(pos)[3]]
assert d.rewrite(patches)==old,'Changes outside the two selected cached faction records'
# Independently confirm the registered landless slot uses the native lord.
detail=None
for pos in range(67213897-512,67213897+512):
 try:
  if baseline.header(pos)[4]=='CHARACTER_DETAILS':
   n,_=baseline.decode(pos)
   if n['groups'][0][4]==515:detail=n;break
 except (AssertionError,IndexError,ValueError,struct.error,KeyError):pass
assert detail and detail['groups'][0][13]=='wh_main_emp_lord'
native=R/'reference/local/lord-vanilla/db/main_units_tables/data__.tsv'
units={r[0] for r in table(native)[2:]}
spec=json.loads((R/'src/campaign/east-sea-charter.json').read_text())
assert all(k in units for k in spec['army'])
assert json.loads((O/'lua-validation.json').read_text())['status']=='passed'
v.update(sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),db_loc_lossless_roundtrip=True,only_two_cached_startpos_records_changed=True,placeholder_general_verified=True,source_sha256=hashlib.sha256((R/'src'/script).read_bytes()).hexdigest(),static_validation='passed')
(O/'build-report.json').write_text(json.dumps(v,indent=2))
print('PASS: DB/loc roundtrip, exact startpos reversal, native General and unit keys, Lua boundaries;',v['sha256'])
