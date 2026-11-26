"""Update only Da Anh over the installed Moonshadow v7 roster."""
import csv,json,hashlib,subprocess,shutil,struct,copy,sys,ast
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/da-anh-v11-dagger-handbow';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v10_starting_movement.pack';PACK=O/'mc_moonshadow_heroes_v11_da_anh_handbow.pack';G='variantmeshes/wh_variantmodels/mc_da_anh'
assert not PACK.exists(),'Keep completed builds'
# Reuse verified binary pack reader, CLI and TSV reader without running old build.
s=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','unpack','cli','read']],type_ignores=[]),'<pack helpers>','exec'))
assert sha(BASE)=='b8a6ee8424e56f407b1ae20e17965cc5bd9a55123ffde92247708485cddbadb4'
E=json.loads((O/'export-report.json').read_text());assert E['skeleton']=='humanoid01d' and len(E['roundtrip_clips'])==10
files=[];dbfiles=[]
def save_table(name,rows,header,internal=None):
 internal=internal or 'db/'+name+'_tables/mc_moonshadow';h,m=copy.deepcopy(header);m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,m]+[[r.get(k,'') for k in h] for r in rows])
 dbfiles.append(internal)
def base_table(name):return read(O/('base-db/db/'+name+'_tables/mc_moonshadow.tsv'))
def native(name):return read(R/('reference/local/lord-vanilla/db/'+name+'_tables/data__.tsv'))
h,rows=base_table('campaign_character_arts');row=next(r for r in rows if r['art_set_id']=='mc_da_anh_art');row['land_animation']='cam_hero_hu1d_elf_sword_and_handbow';save_table('campaign_character_arts',rows,h)
h,rows=base_table('land_units');row=next(r for r in rows if r['key']=='mc_da_anh_human');row.update(man_animation='hu1d_elf_sword_and_handbow',category='inf_ranged',primary_missile_weapon='wh2_main_def_handbow_bolt_khainite_assassin',primary_ammo='50',secondary_ammo='0',can_skirmish='true',ar_unit_category='archer');save_table('land_units',rows,h)
h,rows=base_table('main_units');row=next(r for r in rows if r['unit']=='mc_da_anh_human');row['missile_cp']='250.0000';save_table('main_units',rows,h)
root=ET.Element('VARIANT_MESH');slot=ET.SubElement(root,'SLOT',name='body');node=ET.SubElement(slot,'VARIANT_MESH',model=G+'/da_anh.rigid_model_v2');ET.SubElement(node,'META_DATA').text='audio_armour_type:leather'
for slot_name,bone,model in [('weapon_1','be_prop_0',None),('weapon_2','be_prop_1','knife'),('shield','be_prop_2',None),('weapon_3','be_prop_3',None),('weapon_4','be_prop_4',None),('weapon_5','be_prop_5','handbow')]:
 slot=ET.SubElement(root,'SLOT',name=slot_name,attach_point=bone)
 if model:
  node=ET.SubElement(slot,'VARIANT_MESH',model=G+'/'+model+'.rigid_model_v2');ET.SubElement(node,'META_DATA').text='equipment'
p='variantmeshes/variantmeshdefinitions/mc_da_anh.variantmeshdefinition';path=O/p;path.parent.mkdir(parents=True,exist_ok=True);ET.indent(root);path.write_bytes(ET.tostring(root,encoding='utf-8'));files.append(p)
for folder,kind in [('units','body'),('portholes','head')]:
 p='ui/portraits/'+folder+'/no_culture/mc_da_anh_0.png';(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/('renders/face_01_'+kind+'.png'),O/p);files.append(p)
for p,kind,size in [('ui/units/icons/mc_da_anh.png','body',(104,208)),('ui/units/minspec_portholes/mc_da_anh_human.png','head',(256,256))]:
 (O/p).parent.mkdir(parents=True,exist_ok=True)
 with Image.open(O/('renders/face_01_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(O/p)
 files.append(p)
files.extend(p.relative_to(O).as_posix() for p in (O/G).rglob('*') if p.is_file())
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles]);cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files])
before=unpack(BASE);after=unpack(PACK);changed=[p for p in before if before[p]!=after[p]]
allowed={'db/unit_variants_tables/mc_moonshadow','db/campaign_character_arts_tables/mc_moonshadow','db/land_units_tables/mc_moonshadow','db/main_units_tables/mc_moonshadow','ui/portraits/units/no_culture/mc_da_anh_0.png','ui/portraits/portholes/no_culture/mc_da_anh_0.png','ui/portraits/units/portrait_settings__mc_da_anh.bin','ui/portraits/portholes/portrait_settings__mc_da_anh.bin','ui/units/icons/mc_da_anh.png','ui/units/minspec_portholes/mc_da_anh_human.png'}
assert all(p in allowed or p.startswith(G+'/') or p=='variantmeshes/variantmeshdefinitions/mc_da_anh.variantmeshdefinition' for p in changed),changed
assert before['script/campaign/mod/mc_moonshadow_start.lua']==after['script/campaign/mod/mc_moonshadow_start.lua']
assert all(before[p]==after[p] for p in before if p.startswith(('db/character_skill','text/')))
assert set(after)==set(before)|set(files)|set(dbfiles)
roundtrip=O/'roundtrip';roundtrip.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(roundtrip))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(roundtrip/(p+'.tsv'))[1]
# Generic assassin and every unrelated row/payload remain unchanged.
for name,key in [('unit_variants','unit'),('land_units','key'),('main_units','unit')]:
 old=base_table(name)[1];new=read(roundtrip/('db/'+name+'_tables/mc_moonshadow.tsv'))[1]
 assert [r for r in old if r[key]!='mc_da_anh_human']==[r for r in new if r[key]!='mc_da_anh_human']
assert [r for r in base_table('campaign_character_arts')[1] if r['art_set_id']!='mc_da_anh_art']==[r for r in read(roundtrip/'db/campaign_character_arts_tables/mc_moonshadow.tsv')[1] if r['art_set_id']!='mc_da_anh_art']
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diagnostics=json.loads(text[text.index('{'):]);blocking=[]
for group in diagnostics['results']:
 for kind,g in group.items():
  for issue in g.get('results',[]):
   typ=issue['report_type']
   if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),changed_entries=changed,new_entries=sorted(set(after)-set(before)),blocking_diagnostics=blocking,moonshadow_assassin_unchanged=True,skills_stats_recruitment_spawn_unchanged=True,da_anh_dagger_handbow_configuration=True,starting_movement_fix_unchanged=True,battle_animation='hu1d_elf_sword_and_handbow',campaign_animation='cam_hero_hu1d_elf_sword_and_handbow',deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not blocking
