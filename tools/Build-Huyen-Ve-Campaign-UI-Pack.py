"""Build and verify private v17 UI/campaign test changes over fixed v16."""
import ast,csv,json,hashlib,shutil,subprocess,struct
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v17-campaign';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));base=R/'build/huyen-ve-v16-approved/mc_huyen_ve_v16_native_anim_fix.pack';pack=O/'mc_huyen_ve_v17_campaign_test.pack';assert not pack.exists()
manifest=json.loads((O/'ui-campaign-manifest.json').read_text());shutil.copy2(base,pack)
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
for internal in manifest['files']:
 tabular=internal.startswith('db/') or internal.endswith('.loc');args=[C['rpfm'],'-g','warhammer_3','pack','add','-p',pack]
 if tabular:args+=['-t',C['schema']]
 args+=['-f',str(O/(internal+('.tsv' if tabular else '')))+';'+internal];run(args)
tree=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack-reader>','exec'));before=unpack(base);after=unpack(pack)
changed=[p for p in before if before[p]!=after.get(p)];added=sorted(set(after)-set(before));assert set(after)==set(before)|set(manifest['files']);assert set(changed)<=set(manifest['files'])
assert before['campaigns/cr_combi_expanded/startpos.esf']==after['campaigns/cr_combi_expanded/startpos.esf']
assert all(before[p]==after[p] for p in before if p.startswith(('animations/','variantmeshes/')))
assert b'hu1e_dlc24_yuan_bo_dragon_jade' in after['db/land_units_tables/mc_moon_warden']
verify=R/'reference/local/huyen-ve-v17-check';verify.mkdir(parents=True,exist_ok=True)
run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',pack,'-t',C['schema'],'-F','text;'+str(verify),'db;'+str(verify),'ui;'+str(verify),'script;'+str(verify)])
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t'))
loc={};portrait_checks=[]
for internal in manifest['files']:
 if internal.startswith('db/') or internal.endswith('.loc'):
  expected=read(O/(internal+'.tsv'));actual=read(verify/(internal+'.tsv'));assert actual[0]==expected[0] and actual[2:]==expected[2:],internal
  if internal.endswith('.loc'):
   for row in actual[2:]:assert row[1].isascii(),row;loc[row[0]]=row[1]
 else:assert after[internal]==(O/internal).read_bytes(),internal
 if internal.endswith('.bin'):
  output=O/('roundtrip-'+internal.split('/')[-2]+'.json');run([C['rpfm'],'-g','warhammer_3','portrait-settings','to-json','-b',verify/internal,'-j',output]);d=json.loads(output.read_text());assert len(d['entries'])==1;entry=d['entries'][0];assert entry['id']=='mc_moon_warden_art'
  for variant in entry['variants']:
   img=variant['file_diffuse'];assert img in after;assert img.startswith('ui/portraits/');portrait_checks.append({'settings':internal,'image':img})
for item,name in manifest['items'].items():assert loc['ancillaries_onscreen_name_'+item]==name
assert loc['names_name_1800312100']=='Huyen Ve, Warden of Long Vi'
for x in json.loads((O/'portrait-render-report.json').read_text())['images']:
 image=Image.open(verify/x['file']);assert list(image.size)==x['size'];assert image.mode=='RGBA';assert image.getextrema()[-1][0]==0 and image.getextrema()[-1][1]==255
# Only three display fields change in DB; item mechanics stay intact.
allowed={'unit_variants':{'unit_card'},'units_custom_battle_permissions':{'general_portrait'},'battle_set_piece_armies_characters':{'portrait'}}
for table,fields in allowed.items():
 name='mc_moon_warden' if table=='unit_variants' else 'mc_moon_warden_custom_battle';rel='db/'+table+'_tables/'+name+'.tsv';old=read(R/'reference/local/huyen-ve-v17-base'/rel);new=read(verify/rel)
 assert len(old)==len(new)==3;actual={k for k,a,b in zip(old[0],old[2],new[2]) if a!=b};assert actual==fields,(table,actual)
items=read(verify/'db/ancillaries_tables/mc_huyen_ve_equipment.tsv');keys={r[items[0].index('key')] for r in items[2:]};assert set(manifest['items'])<=keys
script=after['script/campaign/mod/mc_huyen_ve_campaign_test_items.lua'].decode();assert all(script.count('"'+key+'"')==1 for key in manifest['items']);assert 'cm:get_saved_value(marker)' in script and 'cm:set_saved_value(marker, true)' in script and 'cm:force_add_ancillary(character, item, true, true)' in script
name_script=after['script/campaign/mod/mc_huyen_ve_name.lua'].decode();assert 'cm:change_character_custom_name' in name_script and 'Huyen Ve, Warden of Long Vi' in name_script
report={'status':'static_checks_passed','pack':str(pack),'sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),'base':str(base),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changed_entries':changed,'new_entries':added,'ascii_loc_rows':len(loc),'portrait_settings':portrait_checks,'campaign_test_items':list(manifest['items']),'save_load_and_duplicate_guards_present':True,'animation_fix_and_3D_graphics_preserved':True,'startpos_unchanged':True,'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['changed_entries','new_entries','portrait_settings']},indent=2))
