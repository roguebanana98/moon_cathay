"""Add scoped native Cathay major-city display mappings over the current r7 pack."""
import ast, csv, hashlib, json, shutil, struct, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O = R/'build/longvi-city-visual'
O.mkdir(parents=True, exist_ok=True)
base = R/'build/huyen-ve-v25-quest-chain/mc_huyen_ve_v25_quest_chain_test_r7.pack'
pack = O/'mc_huyen_ve_v25_r8_longvi_city.pack'
assert not pack.exists(), 'Output exists; preserve previous build'
table = 'campaign_settlement_display_building_ids_tables'
internal = 'db/'+table+'/mc_long_vi_city_visual'
source = R/'reference/local/lord-vanilla/db'/table/'data__.tsv'
with source.open(encoding='utf-8-sig', newline='') as f:
    data = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
rows = []
for tier in ('1','2','3','4','5','ruin'):
    donor = 'wh3_main_cth_settlement_major_'+tier
    found = [r for r in data[2:] if r[0] == donor]
    assert len(found) == 1
    custom = 'mc_long_vi_cth_settlement_'+tier
    rows.append([custom, custom, found[0][2]])
meta = data[1].copy()
meta[0] = ';'.join(meta[0].split(';')[:2]+[internal])
tsv = O/(internal+'.tsv')
tsv.parent.mkdir(parents=True, exist_ok=True)
with tsv.open('w', encoding='utf-8', newline='') as f:
    csv.writer(f, delimiter='\t', lineterminator='\n').writerows([data[0],meta]+rows)
shutil.copy2(base, pack)
def cli(*args):
    subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],check=True,capture_output=True)
cli('pack','add','-p',pack,'-t',C['schema'],'-f',str(tsv)+';'+internal)
verify = R/'reference/local/longvi-city-visual-check'
verify.mkdir(parents=True, exist_ok=True)
cli('pack','extract','-p',pack,'-t',C['schema'],'-f',internal+';'+str(verify))
extracted = list(verify.rglob('*.tsv'))
assert len(extracted) == 1, extracted
with extracted[0].open(encoding='utf-8-sig',newline='') as f:
    actual = list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
assert actual[0] == data[0] and sorted(actual[2:]) == sorted(rows)
tree = ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text())
scope = {'Path':Path,'struct':struct}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack'],type_ignores=[]),'<pack-reader>','exec'),scope)
old,new = scope['unpack'](base),scope['unpack'](pack)
assert internal not in old
assert set(new)-set(old) == {internal}
assert all(new[k] == v for k,v in old.items())
report = dict(pack=str(pack),base=str(base),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),added_payload=internal,rows=rows,all_existing_payloads_byte_identical=True,roundtrip=True,deployed=False,runtime_verified=False)
(O/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
