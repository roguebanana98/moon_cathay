"""Compare v20 diagnostics with v19 and verify appearance-test invariants."""
import ast,json,csv
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v20-da-lien-visual-test'
t=ast.parse((R/'tools/Validate-Huyen-Ve-Animation-Pack.py').read_text())
fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='diagnostic_rows')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<diagnostics>','exec'))
old=diagnostic_rows(R/'build/huyen-ve-v19-moonlit-command/diagnostics.txt')
new=diagnostic_rows(O/'diagnostics.txt');metadata=[];blocking=[]
for path,items in new.items():
    if old.get(path)==items:continue
    for row in items:
        if set(row['report_type'])=={'NoReferenceTableNorColumnFoundNoPak'} and all(cell[0]==-1 for cell in row['cells_affected']):
            metadata.append({'path':path,'field':row['report_type']['NoReferenceTableNorColumnFoundNoPak']})
        else:blocking.append({'path':path,'report':row})
report=json.loads((O/'pack-validation.json').read_text())
report.update(new_blocking_diagnostics=len(blocking),new_schema_metadata_warnings=metadata)
(O/'diagnostics-review.json').write_text(json.dumps({'metadata':metadata,'blocking':blocking},indent=2))
print(json.dumps({'metadata':metadata,'blocking':blocking},indent=2))
assert not blocking,'Resolve diagnostics before deployment'
assert report['existing_payloads_unchanged'] and report['caste']=='hero'
assert report['attribute_group']=='wh3_main_cth_cha_alchemist_0'
for path in report['files']:
    assert 'ownership_content_pack_junctions' not in path
def rows(table):
    p=R/'reference/local/da-lien-v20-check/db'/(table+'_tables/mc_da_lien.tsv')
    with p.open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t'))
    return [dict(zip(d[0],r)) for r in d[2:]]
assert rows('main_units')[0]['caste']=='hero'
assert rows('campaign_character_art_sets')[0]['agent_type']=='engineer'
assert rows('agent_subtypes')[0]['auto_generate']=='false'
assert rows('agent_subtypes')[0]['has_female_name']=='true'
assert all('neferata' not in r['item'] for r in rows('character_skill_node_set_items'))
assert not any('mount' in r['item'].lower() for r in rows('character_skill_node_set_items'))
(O/'pack-validation.json').write_text(json.dumps(report,indent=2))
print('DA_LIEN_STATIC_AND_DIAGNOSTICS_PASSED')
