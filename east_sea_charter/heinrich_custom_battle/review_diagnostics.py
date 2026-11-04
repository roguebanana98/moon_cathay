import json
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'diagnostics.txt').read_text(encoding='utf-8-sig');d=json.loads(s[s.index('{'):])
blocking=[];metadata=[]
for g in d['results']:
    e=next(iter(g.values()))
    for r in e.get('results',[]):
        item={'path':e.get('path'),'report':r}
        if isinstance(r['report_type'],dict) and set(r['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(c[0]==-1 for c in r['cells_affected']):metadata.append(item)
        else:blocking.append(item)
review={'blocking':blocking,'schema_metadata_only':metadata}
(R/'diagnostics_review.json').write_text(json.dumps(review,indent=2))
for item in blocking:print('BLOCKING',json.dumps(item))
print('DIAGNOSTICS',len(blocking),'blocking',len(metadata),'schema metadata')
if not blocking:
    p=R/'pack_validation.json';v=json.loads(p.read_text());v.update(status='static_checks_passed',blocking_diagnostics=0,schema_metadata_warning_count=len(metadata));p.write_text(json.dumps(v,indent=2))
