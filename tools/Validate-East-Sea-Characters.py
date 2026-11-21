import csv,hashlib,importlib.util,json,lzma,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/east-sea-characters';v=json.loads((O/'build-report.json').read_text());Q=R/'reference/local/edh-characters-roundtrip'
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',v['pack'],'-t',C['schema'],'-F','/;'+str(Q)],capture_output=True,check=True)
def table(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
for p in v['files']:
 if p.startswith(('db/','text/')):
  a=table(O/(p+'.tsv'));z=table(Q/(p+'.tsv'));assert a[0]==z[0] and a[2:]==z[2:],p
script='script/campaign/mod/edh_east_sea_charter_start.lua';assert (Q/script).read_bytes()==(R/'src'/script).read_bytes()
outer=b.Document((Q/'campaigns/cr_combi_expanded/startpos.esf').read_bytes());top,_=outer.decode(16);compressed=next(n for n in b.walk(top) if n['name']=='COMPRESSED_DATA');payload,info=compressed['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE);d=b.Document(raw);old=(O/'base.raw.esf').read_bytes();baseline=b.Document(old);change=json.loads((O/'startpos-changes.json').read_text());patches={}
nodes={}
for name,near,index,value in [('CHARACTER_DETAILS',change['details_offset'],4,515),('UNIT',change['unit_offset'],0,2454)]:
 hits=[]
 for pos in range(near-1024,near+1024):
  try:
   if d.header(pos)[4]==name:
    n,_=d.decode(pos)
    if n['groups'][0][index]==value:hits.append(n)
  except (AssertionError,IndexError,KeyError,ValueError,struct.error):pass
 assert len(hits)==1;node=hits[0];patches[node['offset']]=old[near:baseline.header(near)[3]];nodes[name]=node
reversed_doc=b.Document(d.rewrite(patches))
assert reversed_doc.table==baseline.table and reversed_doc.data[:reversed_doc.table]==old[:baseline.table], 'Unrelated campaign record changed'
assert all(reversed_doc.r.strings[15][k]==value for k,value in baseline.r.strings[15].items())
details=nodes['CHARACTER_DETAILS'];assert details['groups'][0][13]=='edh_heinrich_cb' and details['groups'][0][28]=='edh_heinrich_cb_art'
assert 'is_named_character' in details['groups'][0][8] and 'is_immortal' in details['groups'][0][8]
assert next(n for n in b.walk(details) if n['name']=='CAMPAIGN_SKILLS')['groups'][0][1]=='edh_heinrich_skill_node_set'
assert next(n for n in b.walk(nodes['UNIT']) if n['name']=='UNIT_RECORD_KEY')['groups']==[['edh_heinrich_cb']]
base=R/'reference/local/edh-campaign-base'
changed={p.relative_to(Q).as_posix().removesuffix('.tsv') for p in Q.rglob('*') if p.is_file() and (base/p.relative_to(Q)).is_file() and p.read_bytes()!=(base/p.relative_to(Q)).read_bytes()}
assert changed=={script,'campaigns/cr_combi_expanded/startpos.esf'},changed
assert json.loads((O/'lua-validation.json').read_text())['status']=='passed'
v.update(static_validation='passed',db_loc_roundtrip=True,unchanged_faction_payloads=True,only_starting_leader_and_unit_changed_in_startpos=True,leader_cqi=515,sha256=hashlib.sha256(Path(v['pack']).read_bytes()).hexdigest())
(O/'build-report.json').write_text(json.dumps(v,indent=2));print('PASS: exact leader/unit-only startpos edits; all other faction payloads identical; DB/loc, tree, flags and Lua verified')
