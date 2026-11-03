"""Repair runtime animation lookup, keeping the approved graphics unchanged."""
import ast,csv,json,hashlib,subprocess,shutil,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v16-approved';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));source=O/'mc_huyen_ve_v16_approved_model.pack';dest=O/'mc_huyen_ve_v16_native_anim_fix.pack';assert not dest.exists()
base=R/'build/huyen-ve-animation-integration';p=O/'runtime-fix/db/land_units_tables/mc_moon_warden.tsv';p.parent.mkdir(parents=True,exist_ok=True)
with (base/'db/land_units_tables/mc_moon_warden.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
ix=rows[0].index('man_animation');assert rows[2][ix]=='mc_huyen_ve_human';rows[2][ix]='hu1e_dlc24_yuan_bo_dragon_jade'
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows(rows)
shutil.copy2(source,dest)
def run(args):subprocess.run([str(x) for x in args],check=True,stdout=subprocess.DEVNULL)
run([C['rpfm'],'-g','warhammer_3','pack','add','-p',dest,'-t',C['schema'],'-f',str(p)+';db/land_units_tables/mc_moon_warden'])
removed=['db/battle_animations_table_tables/mc_huyen_ve_model','animations/database/battle/tables/mc_huyen_ve_human.txt']
run([C['rpfm'],'-g','warhammer_3','pack','delete','-p',dest,'-f',*removed])
tree=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'));before=unpack(source);after=unpack(dest)
assert set(before)-set(after)==set(removed);assert not set(after)-set(before)
changed=[x for x in after if after[x]!=before[x]];assert changed==['db/land_units_tables/mc_moon_warden']
assert b'hu1e_dlc24_yuan_bo_dragon_jade' in after[changed[0]] and b'mc_huyen_ve_human' not in after[changed[0]]
for path in after:
 if path.startswith('variantmeshes/'):assert after[path]==before[path],path
verify=R/'reference/local/huyen-ve-v16-runtime-fix-check';verify.mkdir(parents=True,exist_ok=True)
run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',dest,'-t',C['schema'],'-f','db/land_units_tables/mc_moon_warden;'+str(verify)])
with (verify/'db/land_units_tables/mc_moon_warden.tsv').open(encoding='utf-8-sig',newline='') as f:actual=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
assert actual[0]==rows[0] and actual[2:]==rows[2:]
audit=json.loads((O/'native-animation-runtime-audit.json').read_text());assert any(m['name'].endswith('/hu1e_dlc24_yuan_bo_dragon_jade.bin') for a in audit for m in a['matches'])
report={'status':'static_runtime_lookup_fixed','pack':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'replaces_untested_v16':str(source),'previous_lookup':'mc_huyen_ve_human','fixed_lookup':'hu1e_dlc24_yuan_bo_dragon_jade','missing_custom_runtime_bin':True,'native_runtime_bin_verified':True,'removed_unused_custom_entries':removed,'changed_payloads':changed,'all_graphics_byte_identical':True,'only_land_units_field_changed':'man_animation','deployed':False,'runtime_verified':False}
(O/'runtime-animation-fix.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
