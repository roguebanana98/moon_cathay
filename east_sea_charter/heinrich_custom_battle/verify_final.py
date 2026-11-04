import json,csv,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;v=json.loads((R/'pack_validation.json').read_text());O=R/'payload';C=R/'roundtrip_final'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path in v['payloads']:
    if path.startswith(('db/','text/')):
        def rows(p):
            with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))[2:]
        assert rows(O/(path+'.tsv'))==rows(C/(path+'.tsv')),path
    else:assert sha(O/path)==sha(C/path),path
assert sha(Path(v['deployment_target']))==sha(Path(v['pack']))==v['sha256']
v['final_payload_roundtrip_verified']=len(v['payloads']);(R/'pack_validation.json').write_text(json.dumps(v,indent=2))
print('VERIFIED',len(v['payloads']),'payloads; deployed pack SHA256 matches')
