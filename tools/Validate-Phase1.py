"""Validate actual Phase 1 artifacts, not gameplay compatibility."""
import csv
import json
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]
packs=list((root/'build').glob('*.pack'))
assert packs, 'No skeleton build'
for p in packs:
    b=p.read_bytes()
    assert b[:4]==b'PFH5'
    flags,dc,ds,fc,fs,_=struct.unpack('<6I',b[4:28])
    assert flags==3, 'Expected uncompressed mod pack'
    deps=b[28:28+ds].rstrip(b'\0').decode().split('\0')
    assert dc==2 and deps==['!b_mixer.pack','!cr_immortal_empires_expanded.pack']
    pos=28+ds; end=pos+fs; names=[]; total=0
    for _ in range(fc):
        size,compressed=struct.unpack('<IB',b[pos:pos+5]);pos+=5
        stop=b.index(0,pos);name=b[pos:stop].decode();pos=stop+1
        assert not compressed
        names.append(name);total+=size
    assert pos==end and end+total==len(b)
    assert set(names)=={'dependencies_manager_v2.rpfm_reserved','notes.rpfm_reserved','settings.rpfm_reserved'}
    print('PASS mod pack: exact dependency names, RPFM metadata only, no gameplay payload:',p.name)
r=json.loads((root/'reports/agents-of-the-moon.json').read_text(encoding='utf-8'))
expected={'cr_combi_region_'+x for x in ['dai_loa','leilou','long_vi','preenn']}
for label in ('startpos','existing_save'):
    s=r[label]
    assert {x['region'] for x in s['regions']}==expected
    assert s['leader']['character_id']==329 and s['leader']['details_id']==339
    assert s['leader']['subtype']=='wh3_main_cth_dragon_blooded_shugengan_yin'
    assert s['leader']['names']['forename']['text']=='Ju'
    assert s['leader']['names']['family_name']['text']=='Di'
    print('PASS snapshot identity/settlements/leader:',label)
with (root/'reports/khuresh-startpos.tsv').open(encoding='utf-8') as f:
    rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==42 and len({r['region'] for r in rows})==42
assert len({r['province'] for r in rows})==17 and len({r['owner'] for r in rows})==14
print('PASS Khuresh: 42 regions, 17 provinces, 14 owners')
print('These checks do not validate game runtime or future gameplay builds.')
