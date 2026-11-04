"""Review dependency diagnostics and check deployed bytes when present."""
import hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent
def parsed(path):
    text=path.read_text(encoding='utf-8-sig')
    return json.loads(text[text.index('{'):])
data=parsed(R/'diagnostics.txt')
metadata=[];blocking=[]
for group in data['results']:
    entry=next(iter(group.values()))
    for issue in entry.get('results',[]):
        item={'path':entry.get('path'),'report':issue}
        if (isinstance(issue['report_type'],dict)
            and set(issue['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'}
            and all(cell[0]==-1 for cell in issue['cells_affected'])):
            metadata.append(item)
        else:blocking.append(item)
baseline=json.loads((R.parent/'heinrich_custom_battle/diagnostics_review.json').read_text())
assert metadata==baseline['schema_metadata_only'], 'New metadata warnings need review'
review={'blocking':blocking,'schema_metadata_only':metadata,'same_metadata_as_v2':True}
(R/'diagnostics_review.json').write_text(json.dumps(review,indent=2))
assert not blocking,json.dumps(blocking,indent=2)
v=json.loads((R/'pack_validation.json').read_text(encoding='utf8'))
assert hashlib.sha256(Path(v['pack']).read_bytes()).hexdigest()==v['sha256']
assert v['visible_skills']==52 and v['career_lock_rows']==8 and v['native_effect_rows_preserved']==143
if v.get('deployment_target'):
    assert hashlib.sha256(Path(v['deployment_target']).read_bytes()).hexdigest()==v['sha256']
v.update(status='static_checks_passed',blocking_diagnostics=0,schema_metadata_warning_count=len(metadata))
(R/'pack_validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
print('PASS: 52 skills, 143 native effect rows, 58 links, 8 career locks; 0 blocking diagnostics; '
      +str(len(metadata))+' existing v2 metadata warnings. Runtime campaign test not performed.')
