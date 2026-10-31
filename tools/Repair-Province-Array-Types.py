"""Repair only two wrong primitive array tags in each previously tested startpos.

UINT16_ARRAY (0x47) was incorrectly used for optimized UINT32_ARRAY (0x57).
Element payloads and all record lengths remain exactly unchanged.
"""
import hashlib
import importlib.util
import json
import lzma
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'tools/Build-Province-Candidate.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
Document=builder.Document
OUT=ROOT/'build/province-array-fix'
OUT.mkdir(exist_ok=True)

def fix(label,source):
    outer=Document(source.read_bytes())
    root,_=outer.decode(16)
    c=next(n for n in builder.walk(root) if n['name']=='COMPRESSED_DATA')
    payload,info=c['groups'][0][:2]
    length,props=info['groups'][0][:2]
    raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE)
    assert len(raw)==length
    doc=Document(raw)
    hits={}
    for manager,values in [(193,[251,254]),(304,[153,404])]:
        pattern=b'\x47\x04'+struct.pack('<HH',*values)
        start=raw.find(pattern)
        assert start>=0 and raw.find(pattern,start+1)<0, 'Non-unique patch candidate'
        hits[start]=(manager,values)
    verified=set()
    def scan(start,manager_offset=None):
        if raw[start]&128:
            _,count,pos,end,name,version=doc.header(start)
            if not any(start<=h<end for h in hits):return end
            if name=='FACTION_PROVINCE_MANAGER':
                assert version==1
                manager_offset=start
            if count is None:
                while pos<end:pos=scan(pos,manager_offset)
            else:
                for _ in range(count):
                    doc.r.p=pos;size=doc.r.var();pos=doc.r.p;stop=pos+size
                    while pos<stop:pos=scan(pos,manager_offset)
                    assert pos==stop
            assert pos==end
            return end
        value,end=doc.decode(start)
        if start in hits:
            assert manager_offset is not None
            node,_=doc.decode(manager_offset)
            manager,values=hits[start]
            assert node['groups'][0][:3]==[manager,205,values]
            assert value==values
            verified.add(start)
        return end
    scan(16)
    assert verified==set(hits)
    modified=bytearray(raw)
    for offset in hits:modified[offset]=0x57
    modified=bytes(modified)
    assert [i for i,(a,b) in enumerate(zip(raw,modified)) if a!=b]==sorted(hits)
    fixed=Document(modified)
    for offset,(_,values) in hits.items():
        assert fixed.data[offset]==0x57
        assert fixed.decode(offset)[0]==values
    prop=props[0];lc=prop%9;lp=(prop//9)%5;pb=(prop//9)//5
    filters=[{'id':lzma.FILTER_LZMA1,'dict_size':int.from_bytes(props[1:5],'little'),'lc':lc,'lp':lp,'pb':pb}]
    packed=lzma.compress(modified,format=lzma.FORMAT_RAW,filters=filters)
    payload_start=outer.children(c['offset'])[0][0]
    output=outer.rewrite({payload_start:b'\x46'+builder.var(len(packed))+packed})
    check=Document(output);check_root,_=check.decode(16)
    check_c=next(n for n in builder.walk(check_root) if n['name']=='COMPRESSED_DATA')
    check_payload,check_info=check_c['groups'][0][:2]
    check_length,check_props=check_info['groups'][0][:2]
    assert lzma.decompress(check_props+struct.pack('<Q',check_length)+check_payload,format=lzma.FORMAT_ALONE)==modified
    destination=OUT/(label+'.esf');destination.write_bytes(output)
    return {'label':label,'source':str(source),'output':str(destination),'changed_payload_bytes':sorted(hits),
            'old_tag':'0x47 UINT16_ARRAY','new_tag':'0x57 optimized UINT32_ARRAY',
            'all_other_payload_bytes_identical':True,'sha256':hashlib.sha256(output).hexdigest(),
            'runtime_status':'not_game_tested'}

reports=[]
for label,build_id in [('province_v2','fee299cf08e14425b7402cbcb32261c0'),('longvi8_v2','b2cbe56e484b44719ecd658a6ca36cc4')]:
    source=ROOT/'reference/local/province-pack-check'/build_id/'campaigns/cr_combi_expanded/startpos.esf'
    reports.append(fix(label,source))
(OUT/'repair-report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
