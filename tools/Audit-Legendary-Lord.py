"""Read-only dependency inventory for the existing Agents of the Moon lord."""
import csv
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
reference=root/'reference/local/lord-vanilla/db'
subtype='wh3_main_cth_dragon_blooded_shugengan_yin'

def read(table):
    with (reference/table/'data__.tsv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(rows[0],r)) for r in rows[2:]]

agent=next(r for r in read('agent_subtypes_tables') if r['key']==subtype)
sets=[r for r in read('character_skill_node_sets_tables') if r['agent_subtype_key']==subtype]
keys={subtype,agent['associated_unit_override'],*(r['key'] for r in sets)}
matches={}
for path in sorted(reference.glob('*/data__.tsv')):
    with path.open(encoding='utf-8-sig',newline='') as f:
        data=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    hits=[r for r in data[2:] if keys.intersection(r)]
    if hits:
        matches[path.parent.name]={'rows':len(hits),'columns':sorted({data[0][i] for r in hits for i,v in enumerate(r) if v in keys})}
report={
    'status':'baseline_audit_complete_prototype_in_progress',
    'faction':'cr_cth_agents_of_the_moon','baseline_subtype':subtype,
    'baseline_associated_unit':agent['associated_unit_override'],
    'baseline_skill_sets':[r['key'] for r in sets],
    'direct_dependency_tables':matches,
    'scope':'New Legendary Lord; reuse existing model; preserve v3 province and Long Vi changes',
    'accepted_design':'Male human swordsman replacing Ju Di; temporary name; healing, AOE and Yang Dragon Breath; no transformation or Blood-line',
    'prototype_report':'build/moon-lord/lord-report.json',
    'pending':['Runtime testing','Final name, balance and skill progression','Frontend portrait and description'],
}
out=root/'reports/legendary-lord-baseline.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
