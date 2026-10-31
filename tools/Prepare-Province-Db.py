"""Prepare local full-file overrides so the old composite-key rows are removed.

These derived dependency tables stay in ignored build/, never authored src/.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = json.loads((ROOT/'src/campaign/province-layout.json').read_text())
target = {r:(p['key'],r==p['capital']) for p in spec['provinces'] for r in p['regions']}
reference = ROOT/'reference/local/iee/db'
output = ROOT/'build/province-edit/db'
changes = []
for table,filename in (
    ('region_to_province_junctions_tables','!cr_map_expansion.tsv'),
    ('regions_to_region_groups_junctions_tables','!cr_map_expansion_province.tsv'),
):
    source = reference/table/filename
    with source.open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    header = rows[0]
    assert rows[1][0].startswith('#'+table+';')
    seen = set()
    for row in rows[2:]:
        region = row[header.index('region')]
        if region not in target:
            continue
        province,capital = target[region]
        before = row.copy()
        if table == 'region_to_province_junctions_tables':
            row[header.index('province')] = province
            row[header.index('is_capital')] = str(capital).lower()
        else:
            old = row[header.index('region_group')]
            assert old in {p['key'] for p in spec['provinces']}
            row[header.index('region_group')] = province
        seen.add(region)
        if row != before:
            changes.append({'table':table,'before':before,'after':row})
    assert seen == set(target)
    destination = output/table/filename
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('w',encoding='utf-8',newline='') as f:
        csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE).writerows(rows)
assert len(changes)==4
(output.parent/'db-changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(json.dumps(changes,indent=2))
