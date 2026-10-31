"""Verify repaired packs differ only in the intended startpos entry."""
import hashlib
import json
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=root/'build/province-array-fix'
manifest_path=out/'pack-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
def unpack(path):
    raw=Path(path).read_bytes()
    assert raw[:4]==b'PFH5'
    flags,dc,ds,fc,fs,_=struct.unpack('<6I',raw[4:28])
    assert flags==3
    deps=raw[28:28+ds]
    assert dc==2
    assert deps.rstrip(b'\0').decode().split('\0')==['!b_mixer.pack','!cr_immortal_empires_expanded.pack']
    pos=28+ds;end=pos+fs;entries=[]
    for _ in range(fc):
        size,compression=struct.unpack('<IB',raw[pos:pos+5]);pos+=5
        assert compression==0
        stop=raw.index(0,pos);name=raw[pos:stop].decode().replace('\\','/');pos=stop+1
        entries.append((name,size))
    assert pos==end
    files={}
    for name,size in entries:
        assert name not in files
        files[name]=raw[pos:pos+size];pos+=size
    assert pos==len(raw)
    return {k:v for k,v in files.items() if not k.endswith('.rpfm_reserved')}
target='campaigns/cr_combi_expanded/startpos.esf'
for item in manifest:
    old=unpack(item['original_pack']);new=unpack(item['pack'])
    assert old.keys()==new.keys()
    assert [key for key in old if old[key]!=new[key]]==[target]
    assert new[target]==(out/(item['label']+'.esf')).read_bytes()
    assert hashlib.sha256(Path(item['pack']).read_bytes()).hexdigest()==item['sha256']
    item['static_validation']='passed: only startpos changed; all other gameplay/loc files byte-identical; exact dependency header'
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
