"""Validate prototype pack and byte-preserving ESF edits, without gameplay claims."""
import ast
import csv
import hashlib
import importlib.util
import json
import lzma
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1];out=root/'build/moon-lord'
s=importlib.util.spec_from_file_location('builder',root/'tools/Build-Province-Candidate.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def document(path):
    d=b.Document(path.read_bytes());n,_=d.decode(16)
    c=next(x for x in b.walk(n) if x['name']=='COMPRESSED_DATA')
    payload,info=c['groups'][0][:2];length,props=info['groups'][0][:2]
    return b.Document(lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE))

before=document(root/'reference/local/longvi-tiered-check/campaigns/cr_combi_expanded/startpos.esf')
after=document(out/'startpos.esf')
report=json.loads((out/'startpos-report.json').read_text())
expected={x['offset']:x for x in report['changes']};seen=set()
def compare(pa,pb):
    ta,tb=before.data[pa],after.data[pb]
    if ta&128:
        ha,hb=before.header(pa),after.header(pb)
        _,ca,a,ea,na,va=ha;_,cb,z,eb,nb,vb=hb
        assert (na,va)==(nb,vb)
        if pa==67126403:
            n,_=after.decode(pb)
            assert n['groups']==[[k,1] for k in report['skill_block']]
            seen.add(pa);return ea,eb
        assert ca==cb,(na,ca,cb)
        if before.data[pa:ea]==after.data[pb:eb]:return ea,eb
        if ca is None:
            while a<ea:a,z=compare(a,z)
        else:
            for _ in range(ca):
                before.r.p=a;la=before.r.var();a=before.r.p;stopa=a+la
                after.r.p=z;lb=after.r.var();z=after.r.p;stopb=z+lb
                while a<stopa:a,z=compare(a,z)
                assert a==stopa and z==stopb
        assert a==ea and z==eb,(na,a,ea,z,eb)
        return ea,eb
    av,ea=before.decode(pa);bv,eb=after.decode(pb)
    if pa in expected:
        x=expected[pa];assert (av,bv)==(x['old'],x['new'])
        assert ta==tb,'Primitive type must be preserved'
        seen.add(pa)
    else:assert before.data[pa:ea]==after.data[pb:eb],(pa,pb,av,bv)
    return ea,eb
compare(16,16)
assert seen==set(report['patch_offsets'])

tree=ast.parse((root/'tools/Validate-Repaired-Province-Packs.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack parser>','exec'))
manifest_path=out/'pack-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
old=unpack(root/'build/longvi-tiered/mc_longvi_v3_tiered_capital.pack');new=unpack(manifest['pack'])
spec=json.loads((out/'lord-report.json').read_text());target='campaigns/cr_combi_expanded/startpos.esf'
assert set(new)==set(old)|set(spec['files'])
assert not any('ownership_content_pack_junctions_tables/' in k for k in new), 'Banned ownership table in mod pack'
if 'original_pack' in manifest:
    original=unpack(manifest['original_pack'])
    removed={'db/agent_subtype_ownership_content_pack_junctions_tables/mc_moon_warden',
             'db/main_unit_ownership_content_pack_junctions_tables/mc_moon_warden'}
    assert set(original)-set(new)==removed and not set(new)-set(original)
    assert all(new[k]==original[k] for k in new),'Repair changed another payload'
assert all(old[k]==new[k] for k in old if k!=target)
assert new[target]==(out/'startpos.esf').read_bytes()
assert hashlib.sha256(Path(manifest['pack']).read_bytes()).hexdigest()==manifest['sha256']
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return d[0],d[2:]
for internal in spec['files']:
    h,a=rows(out/(internal+'.tsv'));j,z=rows(Path(manifest['verification_directory'])/(internal+'.tsv'))
    assert h==j and sorted(a)==sorted(z),internal
    assert len(a)==len(set(map(tuple,a))),internal+' duplicate rows'
def db(table):
    h,a=rows(out/('db/'+table+'_tables/mc_moon_warden.tsv'))
    return [dict(zip(h,r)) for r in a]
agent=db('agent_subtypes')[0]
assert agent['auto_generate']=='false' and agent['cap']=='1' and agent['recruitable']=='true'
assert agent['has_female_name']=='false' and agent['associated_unit_override']==spec['unit']
assert len(db('faction_agent_permitted_subtypes'))==1
assert all('dragon_form' not in r['ability'] for r in db('land_units_to_unit_abilites_junctions'))
nodes=db('character_skill_nodes')
assert {n['character_skill_key'] for n in nodes}==set(spec['starting_skills'])
assert all(n['points_on_creation']=='1' for n in nodes)
manifest['static_validation']='passed'
manifest['checks']=['All ESF changes restricted to 15 audited fields/skill block; primitive types preserved',
 'All other campaign records, IDs, army, regions and province arrays preserved',
 'All v3 DB/loc payloads byte-identical', '15 new DB/loc payloads roundtrip through RPFM; no banned ownership tables',
 'Male scoped subtype, unique cap, no random recruitment or transformation grant',
 'Three spell skills plus hidden Dragon Breath enable skill']
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
