"""Scoped replacement of Ju Di on the runtime-tested v3 campaign baseline."""
import hashlib
import importlib.util
import json
import lzma
import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('builder',ROOT/'tools/Build-Province-Candidate.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build/moon-lord'
spec=json.loads((OUT/'lord-report.json').read_text())
source=ROOT/'reference/local/longvi-tiered-check/campaigns/cr_combi_expanded/startpos.esf'
outer=b.Document(source.read_bytes());root,_=outer.decode(16)
c=next(n for n in b.walk(root) if n['name']=='COMPRESSED_DATA')
payload,info=c['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE)
assert raw==(ROOT/'reference/local/lord-base.raw.esf').read_bytes()
d=b.Document(raw);patches={};audit=[]

def field(record,index,old,new):
    a,z,v=d.children(record)[index]
    assert v==old,(record,index,v)
    if isinstance(new,str):encoded=d.add_string(new)
    else:
        tag=raw[a];width={0x17:2,0x18:3,0x08:4}[tag]
        encoded=bytes([tag])+new.to_bytes(width,'little')
    patches[a]=encoded;audit.append({'offset':a,'old':old,'new':new})

details=67126132;unit=15709105
node,_=d.decode(details)
assert node['name']=='CHARACTER_DETAILS' and node['groups'][0][4]==329
assert 'male' in node['groups'][0][8] and 'is_immortal' in node['groups'][0][8]
field(details,13,'wh3_main_cth_dragon_blooded_shugengan_yin',spec['subtype'])
field(details,28,'wh3_main_art_set_cth_dragon_blooded_shugengan_yin_010',spec['art'])
field(details,33,4368,8416);field(details,34,4368,8416)
field(67126459,4,'wh3_main_cth_dragon_blooded_shugengan_yin',spec['subtype'])
field(67126459,5,'wh3_main_art_set_cth_dragon_blooded_shugengan_yin_01',spec['art'])
field(67126386,1,'wh3_main_skill_node_set_cth_dragon_blooded_shugengan_yin',spec['skill_set'])
block=67126403
entries=[d.add_string(skill)+b'\x15' for skill in spec['starting_skills']]
patches[block]=d.record(block,b''.join(b.var(len(e))+e for e in entries),len(entries))
for target in [details,unit]:
    subtree,_=d.decode(target)
    for n in b.walk(subtree):
        if n['name']=='CAMPAIGN_LOCALISATION' and n['groups'][0]:
            old=n['groups'][0][0]
            if old in ('names_name_1376971991','names_name_623106632'):
                field(n['offset'],0,old,'names_name_mc_moon_warden' if old.endswith('1376971991') else 'names_name_mc_moon_warden_empty')
field(15709112,0,'wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0',spec['unit'])
field(unit,4,4368,8416);field(unit,5,4368,8416)
edited=d.rewrite(patches)
# Verify changed subtrees semantically and confirm only intended scalars change.
check=b.Document(edited)
def locate(name,near,index,value):
    for pos in range(near-1024,near+1024):
        try:
            if check.header(pos)[4]==name:
                try: candidate,_=check.decode(pos)
                except Exception as error: raise RuntimeError((name,pos,str(error))) from error
                if candidate['groups'][0][index]==value:return candidate
        except (AssertionError,IndexError,KeyError,ValueError,struct.error):pass
    raise AssertionError('Missing '+name)
unit_new=locate('UNIT',unit,0,1575)
details_new=locate('CHARACTER_DETAILS',details,4,329)
assert details_new and details_new['groups'][0][13]==spec['subtype']
assert details_new['groups'][0][8]==node['groups'][0][8]
assert next(n for n in b.walk(unit_new) if n['name']=='UNIT_RECORD_KEY')['groups']==[[spec['unit']]]
skills=next(n for n in b.walk(details_new) if n['name']=='CAMPAIGN_SKILLS_BLOCK')
assert skills['groups']==[[k,1] for k in spec['starting_skills']]
prop=props[0];filters=[{'id':lzma.FILTER_LZMA1,'dict_size':int.from_bytes(props[1:5],'little'),
    'lc':prop%9,'lp':(prop//9)%5,'pb':prop//45}]
packed=lzma.compress(edited,format=lzma.FORMAT_RAW,filters=filters)
assert lzma.decompress(packed,format=lzma.FORMAT_RAW,filters=filters)==edited
encoded=outer.rewrite({outer.children(c['offset'])[0][0]:b'\x46'+b.var(len(packed))+packed,
    outer.children(info['offset'])[0][0]:b'\x08'+struct.pack('<I',len(edited))})
(OUT/'startpos.esf').write_bytes(encoded)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'output_sha256':hashlib.sha256(encoded).hexdigest(),'changes':audit,
    'skill_block':spec['starting_skills'],'male_and_immortal_flags_preserved':True,
    'character_id':329,'army_id':225,'general_unit_id':1575,
    'runtime_verified':False,'patch_offsets':sorted(patches)}
(OUT/'startpos-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
