"""Validate private pack serialization and requested DB invariants, not gameplay."""
import csv
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
build = root/'build/province-edit'
manifest_path = build/'pack-manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
pack = Path(manifest['pack'])
b = pack.read_bytes()
assert hashlib.sha256(b).hexdigest() == manifest['sha256']
assert b[:4] == b'PFH5'
flags,dc,ds,fc,fs,_ = struct.unpack('<6I',b[4:28])
assert flags == 3
deps = b[28:28+ds].rstrip(b'\0').decode().split('\0')
assert dc == 2 and deps == ['!b_mixer.pack','!cr_immortal_empires_expanded.pack']
pos = 28+ds
end = pos+fs
names = []
total = 0
for _ in range(fc):
    size,compressed = struct.unpack('<IB',b[pos:pos+5])
    pos += 5
    stop = b.index(0,pos)
    names.append(b[pos:stop].decode().replace('\\','/'))
    pos = stop+1
    total += size
    assert not compressed
assert pos == end and end+total == len(b)
expected = {'campaigns/cr_combi_expanded/startpos.esf',
            'db/region_to_province_junctions_tables/!cr_map_expansion',
            'db/regions_to_region_groups_junctions_tables/!cr_map_expansion_province'}
assert {n for n in names if not n.endswith('.rpfm_reserved')} == expected
verify = Path(manifest['verification_directory'])
assert (verify/'campaigns/cr_combi_expanded/startpos.esf').read_bytes() == (build/'province-candidate.esf').read_bytes()

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        data = list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    assert data[1][0].startswith('#')
    return data[0],data[2:]

for internal in sorted(expected - {'campaigns/cr_combi_expanded/startpos.esf'}):
    prepared = build/(internal+'.tsv')
    extracted = verify/(internal+'.tsv')
    assert extracted.is_file(), 'Schema decoding failed: '+str(extracted)
    ah,ar = rows(prepared)
    bh,br = rows(extracted)
    assert ah == bh and sorted(ar) == sorted(br), internal
header,data = rows(verify/'db/region_to_province_junctions_tables/!cr_map_expansion.tsv')
records = [dict(zip(header,row)) for row in data]
spec = json.loads((root/'src/campaign/province-layout.json').read_text())
for province in spec['provinces']:
    actual = [r for r in records if r['province']==province['key']]
    assert len(actual)==len(province['regions'])
    assert {r['region'] for r in actual}==set(province['regions'])
    assert [r['region'] for r in actual if r['is_capital']=='true']==[province['capital']]
    for region in province['regions']:
        assert sum(r['region']==region for r in records)==1
manifest['status'] = 'static_pack_verification_passed_not_game_tested'
manifest['checks'] = ['PFH5 mod type','exact IEE/MIXER dependencies','exact three gameplay payloads',
                      'pack startpos byte-identical to audited candidate','both DB tables imported and exported losslessly',
                      'five unique regions; exactly one capital per target province']
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
