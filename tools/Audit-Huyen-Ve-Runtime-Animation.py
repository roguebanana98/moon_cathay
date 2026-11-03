import struct,json
from pathlib import Path
R=Path('D:/Warhammer3_Modding/moon_cathay');rows=[]
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
 b=p.read_bytes();count=struct.unpack_from('<I',b)[0];pos=4;hits=[]
 for i in range(count):
  n=struct.unpack_from('<H',b,pos)[0];pos+=2;name=b[pos:pos+n].decode();pos+=n;size=struct.unpack_from('<I',b,pos)[0];pos+=4
  if 'yuan_bo' in name or 'mc_huyen_ve' in name:hits.append({'name':name,'bytes':size})
  pos+=size
 assert pos==len(b),(p,pos,len(b));rows.append({'animpack':str(p),'entries':count,'matches':hits})
print(json.dumps(rows,indent=2));(R/'build/huyen-ve-v16-approved/native-animation-runtime-audit.json').write_text(json.dumps(rows,indent=2))
