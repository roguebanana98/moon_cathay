"""Validate actual packed rows and prove gameplay payloads unchanged from v14."""
import ast,csv,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-animation-integration'
manifest=json.loads((O/'pack-manifest.json').read_text(encoding='utf-8-sig'));links=json.loads((O/'integration-links.json').read_text());graph=json.loads((O/'animation-set-manifest.json').read_text());verification=Path(manifest['verification_directory'])
tree=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'))
before=unpack(manifest['base_pack']);after=unpack(manifest['pack']);changed=[p for p in before if before[p]!=after.get(p)]
expected={'db/land_units_tables/mc_moon_warden','db/unit_variants_tables/mc_moon_warden','db/campaign_character_arts_tables/mc_moon_warden'}
assert set(changed)==expected,changed
assert set(after)==set(before)|set(links['files'])
assert not any(p.endswith('.anim') or p.endswith('.bin') or '/fragments/' in p for p in set(after)-set(before))
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:data=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return [dict(zip(data[0],row)) for row in data[2:]]
def table(name,filename='mc_huyen_ve_model'):return read(verification/('db/'+name+'_tables/'+filename+'.tsv'))
unit=table('land_units','mc_moon_warden');uv=table('unit_variants','mc_moon_warden');art=table('campaign_character_arts','mc_moon_warden')
assert len(unit)==len(uv)==len(art)==1
assert unit[0]['key']==uv[0]['unit']==links['unit']
assert unit[0]['man_animation']==links['animation_table']
assert uv[0]['variant']==links['variant']
assert art[0]['uniform']==links['uniform'] and art[0]['land_animation']==links['campaign_animation_preserved']
variant=table('variants')[0];uniform=table('agent_uniforms')[0];anim=table('battle_animations_table')[0]
assert variant['variant_name']==variant['variant_filename']==links['variant']
assert all(uniform[k]==links['variant'] for k in ['filename','battle_filename','campaign_porthole_filename'])
assert uniform['uniform_name']==links['uniform']
assert anim=={'key':links['animation_table'],'skeleton':'humanoid01e'}
for name,details in links['changes_to_existing_v14'].items():
 old=read(R/('reference/local/huyen-ve-animation-integration/v14/db/'+name+'_tables/mc_moon_warden.tsv'))[0]
 new=table(name,'mc_moon_warden')[0]
 assert {key for key in old if old[key]!=new[key]}==set(details['fields']),(name,old,new)
native=graph['table'];custom=json.loads(after['animations/database/battle/tables/'+links['animation_table']+'.txt'])
assert custom['Entries']==native['Entries']
assert custom['Properties']==dict(native['Properties'],TableName=links['animation_table'])
for path in links['files']:
 if path.startswith('db/'):assert table(path.split('/')[1].removesuffix('_tables'),path.split('/')[-1])==read(O/(path+'.tsv'))
 else:assert after[path]==(O/path).read_bytes(),path
assert before['campaigns/cr_combi_expanded/startpos.esf']==after['campaigns/cr_combi_expanded/startpos.esf']
def diagnostic_rows(path):
 text=path.read_text(encoding='utf-8-sig');data=json.loads(text[text.index('{'):]);rows={}
 for group in data['results']:
  entry=next(iter(group.values()))
  if 'path' in entry:rows[entry['path']]=entry['results']
 return rows
old_diagnostics=diagnostic_rows(R/'build/huyen-ve-equipment/diagnostics.txt');new_diagnostics=diagnostic_rows(O/'diagnostics.txt')
added_diagnostics={p:v for p,v in new_diagnostics.items() if old_diagnostics.get(p)!=v}
assert not added_diagnostics,added_diagnostics
result={'status':'passed','base_payload_count':len(before),'integrated_payload_count':len(after),'changed_existing_payloads':changed,
 'new_payload_count':len(set(after)-set(before)),'battle_slots':graph['effective_slot_count'],'clip_count':graph['clip_count'],
 'gameplay_and_startpos_unchanged':True,'native_clips_referenced_not_bundled':True,'new_or_changed_diagnostics':0,'runtime_verified':False,'pack_sha256':hashlib.sha256(Path(manifest['pack']).read_bytes()).hexdigest()}
(O/'pack-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
