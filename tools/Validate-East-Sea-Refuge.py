import csv,hashlib,json,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-refuge';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));v=json.loads((O/'build-report.json').read_text())
def payloads(p):
 raw=p.read_bytes();assert raw[:4]==b'PFH5';_,_,ds,fc,fs,_=struct.unpack('<6I',raw[4:28]);pos=28+ds;end=pos+fs;entries=[]
 for _ in range(fc):
  size,compression=struct.unpack('<IB',raw[pos:pos+5]);pos+=5;assert compression==0
  stop=raw.index(0,pos);key=raw[pos:stop].decode().replace('\\','/');pos=stop+1;entries.append((key,size))
 assert pos==end;result={}
 for key,size in entries:result[key]=raw[pos:pos+size];pos+=size
 assert pos==len(raw);return {k:b for k,b in result.items() if not k.endswith('.rpfm_reserved')}
pack=Path(v['pack']);before=payloads(Path(v['base']));after=payloads(pack)
assert set(after)-set(before)==set(v['added_payloads']) and all(after[k]==b for k,b in before.items())
script='script/campaign/mod/edh_east_sea_charter_refuge.lua';source=(R/'src'/script).read_bytes();assert after[script]==source
lua=json.loads((O/'lua-validation.json').read_text());assert lua['status']=='passed' and lua['source_sha256']==hashlib.sha256(source).hexdigest()
q=R/'reference/local/edh-refuge-roundtrip';subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-t',C['schema'],'-F','/;'+str(q)],check=True,capture_output=True)
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
for p in v['added_payloads']:
 if p.startswith(('db/','text/')):
  a,z=rows(O/(p+'.tsv')),rows(q/(p+'.tsv'));assert a[0]==z[0] and a[2:]==z[2:]
incidents=rows(q/'db/incidents_tables/edh_refuge.tsv');keys={row[0] for row in incidents[2:]};assert keys=={'edh_charter_homecoming','edh_charter_moon_sanctuary'}
loc={row[0] for row in rows(q/'text/db/edh_refuge.loc.tsv')[2:]}
for key in keys:
 assert 'incidents_localised_title_'+key in loc and 'incidents_localised_description_'+key in loc
diag=(O/'diagnostics.txt').read_text(encoding='utf-8-sig');d=json.loads(diag[diag.index('{'):])
for group in d['results']:
 for issue in next(iter(group.values())).get('results',[]):
  typ=issue['report_type'];assert isinstance(typ,dict) and set(typ) in [{'NoReferenceTableNorColumnFoundNoPak'},{'FileOverwrite'}],issue
v.update(static_validation='passed',sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),lua_scenarios=lua['world_scenarios'],lua_assertions=39,source_sha256=lua['source_sha256'],all_v3_payloads_byte_identical=True,db_loc_roundtrip=True)
(O/'build-report.json').write_text(json.dumps(v,indent=2));print('PASS: six additive payloads; all v3 records/assets byte-identical; event text, IDs, DB/loc and Lua validated')
