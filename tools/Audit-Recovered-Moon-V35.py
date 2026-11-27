"""Read-only inventory of the recovered v35; never rebuild or deploy it."""
import collections,csv,hashlib,json,re,struct,subprocess,xml.etree.ElementTree as ET
from pathlib import Path

R=Path(__file__).resolve().parents[1]
PACK=R/'mc_moonshadow_heroes_v35_moon_arts.pack'
OUT=R/'build/recovered-v35-audit'; OUT.mkdir(parents=True,exist_ok=True)
REF=R/'reference/local/recovered-v35-audit'

def index(path,hashes=False):
    with path.open('rb') as f:
        magic=f.read(4); assert magic==b'PFH5',(str(path),magic)
        flags,dc,ds,fc,fs,stamp=struct.unpack('<6I',f.read(24))
        deps=f.read(ds); raw=f.read(fs); pos=0; entries=[]
        for _ in range(fc):
            size,compressed=struct.unpack_from('<IB',raw,pos);pos+=5
            end=raw.index(0,pos);name=raw[pos:end].decode().replace('\\','/');pos=end+1
            assert not compressed, name
            entries.append(dict(path=name,size=size))
        assert pos==len(raw)
        offset=f.tell(); paths={}
        for item in entries:
            item['offset']=offset;offset+=item['size']
            assert item['path'].lower() not in paths,item['path']
            paths[item['path'].lower()]=item
            if hashes:
                f.seek(item['offset']);left=item['size'];digest=hashlib.sha256()
                while left:
                    chunk=f.read(min(left,8*1024*1024));assert chunk
                    digest.update(chunk);left-=len(chunk)
                item['sha256']=digest.hexdigest()
        assert offset==path.stat().st_size,(offset,path.stat().st_size)
        return dict(flags=flags,count=fc,dependencies=[x.decode() for x in deps.split(b'\0') if x],paths=paths)

ix=index(PACK,True)
def payload(name):
    e=ix['paths'][name.lower()]
    with PACK.open('rb') as f:f.seek(e['offset']);return f.read(e['size'])
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return [dict(zip(a[0],row)) for row in a[2:]]
def table(name,pattern='*.tsv'):
    return [r for p in (REF/'db'/(name+'_tables')).glob(pattern) for r in rows(p)]
loc={r['key']:r['text'] for p in (REF/'text').rglob('*.tsv') for r in rows(p)}
paths=ix['paths'];counts=collections.Counter(p.split('/')[0] for p in paths)
spells=[r for r in table('unit_abilities','*moon_arts*')]
allnodes={r['key']:r for r in table('character_skill_nodes')}
members=[r for r in table('character_skill_node_set_items') if r['set']=='mc_mooncourt_lord_skills' and r['mod_disabled']=='false']
nodes=[allnodes[r['item']] for r in members]
skills={r['key']:r for r in table('character_skills')}
zhao_nodes=[dict(node=r['key'],skill=r['character_skill_key'],name=loc.get('character_skills_localised_name_'+r['character_skill_key'],skills.get(r['character_skill_key'],{}).get('localised_name','native')),indent=r['indent'],tier=r['tier'],rank=skills.get(r['character_skill_key'],{}).get('unlocked_at_rank','native')) for r in nodes]
vmd={};references=[]
for p in paths:
    if p.endswith(('.variantmeshdefinition','.wsmodel','.xml.material')):
        data=payload(p)
        if p.endswith('.variantmeshdefinition'):
            root=ET.fromstring(data)
            vmd[p]=[n.get('model') for n in root.iter('VARIANT_MESH') if n.get('model')]
        text=data.decode('utf-8-sig',errors='replace')
        for ref in re.findall(r'(?:variantmeshes|commontextures|rigidmodels|variantmodels)/[^<>"\r\n]+?\.(?:wsmodel|rigid_model_v2|dds|xml\.material|variantmeshdefinition)',text,re.I):
            references.append((p,ref.strip().replace('\\','/').lower()))
external=sorted({ref for _,ref in references if ref not in paths})
private_missing=[(p,ref) for p,ref in references if ref not in paths and ('/mc_' in ref or '/mc_' in p and ref.startswith('variantmeshes/wh_variantmodels/mc_'))]
native_candidates=sorted((Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data')).glob('variants*.pack'))
native_candidates += [Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data/commontextures.pack')]
remaining=set(external);resolved={}
for pack in native_candidates:
    if not remaining:break
    if not pack.exists():continue
    # Native packs use additional header flags/compression; let RPFM parse them.
    listing=subprocess.run(['D:/Test/tooling/rpfm/rpfm_cli.exe','-g','warhammer_3','pack','list','-p',str(pack)],check=True,capture_output=True,text=True,encoding='utf-8')
    native={p.strip().replace('\\','/').lower() for p in listing.stdout.splitlines() if p.strip() and not re.search(r'\[(?:INFO|WARN|ERROR)\]',p)}
    for ref in remaining & native:resolved[ref]=pack.name
    remaining-=native

reference_comparisons={}
for rel in ['script/campaign/mod/mc_assault_campaign_appearance.lua','script/campaign/mod/mc_moonshadow_start.lua']:
    source=R/'src'/rel
    if source.exists() and rel in paths:reference_comparisons[rel]=dict(byte_identical=source.read_bytes()==payload(rel),text_identical_ignoring_line_endings=source.read_text(encoding='utf-8-sig')==payload(rel).decode('utf-8-sig').replace('\r\n','\n'))
subtypes=table('agent_subtypes')
report=dict(pack=str(PACK),bytes=PACK.stat().st_size,sha256=hashlib.file_digest(PACK.open('rb'),'sha256').hexdigest(),header='PFH5',structural_payload_bounds_valid=True,dependencies=ix['dependencies'],payload_count=ix['count'],top_level_counts=dict(counts),payloads=list(paths.values()),subtypes=subtypes,zhao_land=table('land_units','zzzz_mc_mooncourt_lord.tsv'),zhao_main=table('main_units','zzzz_mc_mooncourt_lord.tsv'),zhao_nodes=zhao_nodes,zhao_node_count=len(nodes),zhao_abilities=spells,variant_meshes=vmd,xml_asset_reference_count=len(references),external_xml_assets=external,native_resolved_external_xml_assets=resolved,unresolved_external_xml_assets=sorted(remaining),missing_private_xml_assets=private_missing,source_script_byte_comparisons=reference_comparisons,has_retired_tab_hiding_script=any('hide_celestial' in p for p in paths),has_jade_reskin=any('mc_moon_jade' in p for p in paths),has_skywing_assets=any('divine_wing' in p or 'skywing' in p for p in paths),runtime_verified=False,original_modified=False)
(OUT/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['payloads','subtypes','zhao_nodes','zhao_land','zhao_main','zhao_abilities','variant_meshes','external_xml_assets','native_resolved_external_xml_assets']},ensure_ascii=False,indent=2))
print('ZHAO SKILLS',json.dumps(zhao_nodes,ensure_ascii=False,indent=2))
