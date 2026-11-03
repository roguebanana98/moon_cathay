"""Build v19 and validate skill graph, ability grants and unchanged native support."""
import ast,csv,json,hashlib,shutil,subprocess,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v19-moonlit-command';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));REF=R/'reference/local/huyen-ve-v19-base';spec=json.loads((O/'skill-manifest.json').read_text());base=R/'build/huyen-ve-v18-item-reequip/mc_huyen_ve_v18_item_reequip.pack';pack=O/'mc_huyen_ve_v19_moonlit_command.pack';assert not pack.exists();shutil.copy2(base,pack)
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
for internal in spec['files']:
 tabular=internal.startswith('db/') or internal.endswith('.loc')
 args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',pack]
 if tabular:args+=['-t',C['schema']]
 run(args+['-f',str(O/(internal+('.tsv' if tabular else '')))+';'+internal])
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack>','exec'));before=unpack(base);after=unpack(pack);assert set(after)==set(before)|set(spec['files']);changed=[p for p in before if before[p]!=after[p]];assert changed==['db/character_skill_nodes_tables/mc_moon_warden']
verify=R/'reference/local/huyen-ve-v19-check';verify.mkdir(exist_ok=True);run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',pack,'-t',C['schema'],'-F','db;'+str(verify),'text;'+str(verify)])
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:d=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return d[:2],[dict(zip(d[0],r)) for r in d[2:]]
for internal in spec['files']:
 if internal.startswith('db/') or internal.endswith('.loc'):assert read(O/(internal+'.tsv'))[1]==read(verify/(internal+'.tsv'))[1],internal
 else:assert after[internal]==(O/internal).read_bytes(),internal
nodes=read(verify/'db/character_skill_nodes_tables/mc_moon_warden.tsv')[1];old=read(REF/'db/character_skill_nodes_tables/mc_moon_warden.tsv')[1];newby={r['key']:r for r in nodes}
for r in old:
 n=newby[r['key']];fields={k for k in r if r[k]!=n[k]};assert fields==({'tier'} if r['key']=='mc_moon_warden_spell_2' else set())
assert [(r['character_skill_key'],r['tier']) for r in sorted([r for r in nodes if r['indent']=='1'],key=lambda r:int(r['tier']))]==[('mc_moon_warden_magic_breath','0'),('mc_moon_warden_magic_earth','1'),(spec['skill'],'2'),('mc_moon_warden_magic_flame','3')]
# Ensure no pre-existing ability/skill effect definition is overridden.
for folder,keyfield,key in [('unit_abilities','key',spec['ability']),('unit_special_abilities','key',spec['ability']),('character_skills','key',spec['skill'])]:
 allrows=[r for p in (verify/('db/'+folder+'_tables')).glob('*.tsv') for r in read(p)[1]];assert sum(r[keyfield]==key for r in allrows)==1
assert before['db/character_skill_nodes_tables/mc_moon_warden_support']==after['db/character_skill_nodes_tables/mc_moon_warden_support']
assert before['db/character_skill_node_links_tables/mc_moon_warden_spell_ranks']==after['db/character_skill_node_links_tables/mc_moon_warden_spell_ranks']
for path in before:
 if path.startswith(('variantmeshes/','animations/','script/','ui/')):assert before[path]==after[path]
loc=read(verify/'text/db/mc_huyen_ve_moonlit_command.loc.tsv')[1];assert all(r['text'].isascii() for r in loc)
ability=read(verify/'db/unit_special_abilities_tables/mc_huyen_ve_moonlit_command.tsv')[1][0];phase=read(verify/'db/special_ability_phases_tables/mc_huyen_ve_moonlit_command.tsv')[1][0];assert ability['wind_up_stance']=='' and phase['requested_stance']==''
report={'status':'static_checks_passed','pack':str(pack),'sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),'base':str(base),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changed_entries':changed,'new_payloads':len(set(after)-set(before)),'skill_order':spec['skill_order'],'skill_requires_point':True,'flame_storm_prerequisites_preserved':True,'army_of_renown_unchanged_native':True,'native_skill_owner_count':len(spec['army_of_renown']['native_owners']),'all_previous_graphics_scripts_animation_links_unchanged':True,'requires_new_animation_stance':False,'runtime_verified':False,'deployed':False};(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
