"""Check tier progression, vanilla-derived definitions and unchanged campaign bytes."""
import ast
import csv
import hashlib
import json
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]
# Reuse the pack parser without executing the historical validator's main code.
tree=ast.parse((root/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack parser>','exec'))
out=root/'build/longvi-tiered'
manifest_path=out/'pack-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
old=unpack(root/'build/province-array-fix/mc_longvi8_v2_uint32_fix.pack')
new=unpack(manifest['pack'])
report=json.loads((out/'long-vi-buildings-report.json').read_text())
assert old.keys()==new.keys()
changed=[k for k in old if old[k]!=new[k]]
assert set(changed)<=set(report['files'])
assert new['campaigns/cr_combi_expanded/startpos.esf']==old['campaigns/cr_combi_expanded/startpos.esf']
assert hashlib.sha256(Path(manifest['pack']).read_bytes()).hexdigest()==manifest['sha256']
verify=Path(manifest['verification_directory'])

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        data=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return data[0],data[2:]

def table(name):
    return rows(verify/('db/'+name+'_tables/mc_long_vi_eight_slots.tsv'))

for internal in report['files']:
    h,a=rows(out/(internal+'.tsv'));j,b=rows(verify/(internal+'.tsv'))
    assert h==j and sorted(a)==sorted(b),internal
chain='mc_long_vi_cth_settlement'
_,unlocks=table('campaign_building_chain_slot_unlocks')
assert unlocks==[[chain,str(t),str(c)] for t,c in [(1,1),(2,2),(3,3),(4,5),(5,7)]]
_,upgrades=table('building_upgrades_junction')
assert all([chain+'_'+str(t),chain+'_'+str(t+1)] in upgrades for t in range(1,5))
h,levels=table('building_levels')
assert {r[h.index('level_name')] for r in levels}=={chain+'_'+x for x in ['1','2','3','4','5','ruin']}
# Major-city effects, garrison, costs, art and recruitment must match vanilla,
# with only the scoped keys and necessary numeric row IDs changed.
for name,cols in {
    'building_levels':['level_name','chain'],
    'building_effects_junction':['building'],
    'building_culture_variants':['building'],
    'building_units_allowed':['building'],
    'building_level_armed_citizenry_junctions':['building_level'],
}.items():
    h,a=table(name)
    vh,vanilla=rows(root/('reference/local/vanilla/db/'+name+'_tables/data__.tsv'))
    assert h==vh
    for row in a:
        original=row.copy()
        for c in cols:
            i=h.index(c);original[i]=original[i].replace(chain,'wh3_main_cth_settlement_major')
        if name in ('building_units_allowed','building_level_armed_citizenry_junctions'):
            assert any(original[1:]==v[1:] for v in vanilla)
        else:
            assert original in vanilla
_,permissions=table('slot_template_permitted_building_chains')
assert permissions==[['wh3_main_cth_settlement_minor','','cr_minor_primary_long_vi','','true'],[chain,'','cr_minor_primary_long_vi','','false']]
manifest['static_validation']='passed'
manifest['checks']=['Original v2 startpos and province tables byte-identical','All 12 DB/loc payloads roundtrip unchanged','Five-tier upgrades and 1/2/3/5/7 unlock progression','Vanilla Cathay major-city definitions preserved under Long Vi-only keys']
manifest['changed_payloads']=changed
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
