"""V34: approved Yuan Bo sword, battle/campaign native profiles, unchanged skills."""
import ast,copy,csv,hashlib,json,shutil,struct,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-v34-yuan-bo-lord';O.mkdir(exist_ok=True);B=R/'reference/local/moon-v33-roundtrip';REF=R/'reference/local/yuan-bo-model'
BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v33_lord_roster.pack';PACK=O/'mc_moonshadow_heroes_v34_yuan_bo_lord.pack';assert not PACK.exists()
helpers=ast.parse((R/'tools/Build-Moonshadow-Appearance-Pack.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ('sha','unpack','cli','read')],type_ignores=[]),'<helpers>','exec'))
assert sha(BASE)=='909cab5c8a97ce6112b6bad90d8aa955ae0d336120a890a4b0690b13f936e16b'
fix=json.loads((R/'build/zhao-yuan-bo-preview/grip-fix-report.json').read_text());assert fix['all_341_frames_checked'] and fix['body_hands_weights_unchanged'] and fix['sword_vertices_unchanged']
portrait=json.loads((O/'portrait-review.json').read_text());assert portrait['source_unchanged'] and sha(portrait['source'])==portrait['source_sha256']
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
S='mc_mooncourt_lord';U=S+'_human';BATTLE='hu1e_dlc24_yuan_bo_dragon_jade';CAMPAIGN='cam_lord_hu1e_dlc24_yuan_bo_dragon_jade'
G='variantmeshes/wh_variantmodels/'+S+'/yuan_bo_sword';files=[];dbpaths=[];copied={};native_shared=set()
def copy_asset(path):
    path=path.replace('\\','/').strip().lower()
    if path.startswith('commontextures/'):
        native_shared.add(path);return path
    if path in copied:return copied[path]
    source=REF/path;assert source.exists(),path
    target=G+'/'+hashlib.sha256(path.encode()).hexdigest()[:10]+'_'+source.name;copied[path]=target;dest=O/target;dest.parent.mkdir(parents=True,exist_ok=True)
    if path.endswith(('.wsmodel','.xml.material')):
        root=ET.fromstring(source.read_bytes())
        for node in root.iter():
            if node.tag in ['geometry','material'] and node.text and node.text.strip():node.text=copy_asset(node.text)
            elif node.tag=='source' and node.text and node.text.lower().endswith('.dds'):node.text=copy_asset(node.text)
        dest.write_bytes(ET.tostring(root,encoding='utf8'))
    else:shutil.copy2(source,dest)
    files.append(target);return target
weapon=copy_asset('variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.wsmodel')
ws=ET.parse(O/weapon).getroot();geo=rf.load((O/ws.findtext('geometry')).read_bytes());assert len(geo.lods)==4
assert {(i,j) for i,lod in enumerate(geo.lods) for j,_ in enumerate(lod.models)}<={(int(n.get('lod_index')),int(n.get('part_index'))) for n in ws.findall('.//material')}
native_geo=REF/'variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.rigid_model_v2'
assert sha(O/ws.findtext('geometry'))==sha(native_geo)
assert abs(geo.lods[0].models[0].material.pivot[0]-.4833669066429138)<1e-6

# Verify real native runtime entries, rather than authoring a source-only lookup.
runtime_hits=[]
for p in (R/'reference/local/native-animation-runtime').rglob('*.animpack'):
    raw=p.read_bytes();count=struct.unpack_from('<I',raw)[0];pos=4
    for _ in range(count):
        n=struct.unpack_from('<H',raw,pos)[0];pos+=2;name=raw[pos:pos+n].decode();pos+=n;size=struct.unpack_from('<I',raw,pos)[0];pos+=4
        if name.endswith('/'+BATTLE+'.bin'):runtime_hits.append(dict(archive=str(p),entry=name,bytes=size,skeleton_present=b'humanoid01e' in raw[pos:pos+size]))
        pos+=size
    assert pos==len(raw)
assert runtime_hits
camp=R/'reference/local/huyen-ve-animation-integration/animations/campaign/database/bin'/ (CAMPAIGN+'.bin');assert camp.exists() and b'yuan_bo' in camp.read_bytes()
native_rows=read(R/'reference/local/lord-vanilla/db/battle_animations_table_tables/data__.tsv')[1];assert any(r['key']==BATTLE and r['skeleton']=='humanoid01e' for r in native_rows)

before=unpack(BASE)
p='variantmeshes/variantmeshdefinitions/'+S+'.variantmeshdefinition';root=ET.fromstring(before[p]);original_body=ET.tostring(root.find("SLOT[@name='body']"))
assert root.find("SLOT[@name='weapon_2']") is None
node=ET.SubElement(ET.SubElement(root,'SLOT',name='weapon_2',attach_point='weapon_2'),'VARIANT_MESH',model=weapon);ET.SubElement(node,'META_DATA').text='audio_melee_weapon_type:sword_medium'
assert ET.tostring(root.find("SLOT[@name='body']"))==original_body
dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(ET.tostring(root,encoding='utf8'));files.append(p)
for t,field,value in [('land_units','man_animation',BATTLE),('campaign_character_arts','land_animation',CAMPAIGN)]:
    p='db/'+t+'_tables/zzzz_mc_mooncourt_lord';(h,meta),rs=read(B/(p+'.tsv'));old=copy.deepcopy(rs);assert len(rs)==1
    rs[0][field]=value
    assert {k:v for k,v in old[0].items() if k!=field}=={k:v for k,v in rs[0].items() if k!=field}
    dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,quotechar=None,lineterminator='\n').writerows([h,meta]+[[r[k] for k in h] for r in rs])
    dbpaths.append(p)
for folder,kind in [('units','body'),('portholes','head')]:
    p='ui/portraits/'+folder+'/no_culture/'+S+'_0.png';dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'renders'/(S+'_'+kind+'.png'),dest);files.append(p)
for p,kind,size in [('ui/units/icons/'+S+'.png','body',(104,208)),('ui/units/minspec_portholes/'+U+'.png','head',(256,256))]:
    dest=O/p;dest.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(O/'renders'/(S+'_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(dest)
    files.append(p)
shutil.copy2(BASE,PACK);cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbpaths]);cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files])
after=unpack(PACK);allowed=set(files+dbpaths);assert all(after[p]==data for p,data in before.items() if p not in allowed)
assert {p for p in after if p.startswith('animations/')}=={p for p in before if p.startswith('animations/')}
check=R/'reference/local/moon-v34-roundtrip';check.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(check))
for p in dbpaths:assert read(O/(p+'.tsv'))[1]==read(check/(p+'.tsv'))[1]
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
txt=(O/'diagnostics.txt').read_text();diag=json.loads(txt[txt.index('{'):]);blocking=[]
for group in diag['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append(dict(kind=kind,path=g.get('path'),issue=issue))
report=dict(status='static_checks_passed' if not blocking else 'diagnostics_need_review',pack=str(PACK),sha256=sha(PACK),base=str(BASE),base_sha256=sha(BASE),blocking_diagnostics=blocking,roundtrip_passed=True,approved_scene=portrait['source'],approved_scene_sha256=portrait['source_sha256'],native_battle_lookup=BATTLE,native_campaign_lookup=CAMPAIGN,compiled_native_runtime_verified=True,runtime_hits=runtime_hits,native_sword_geometry_all_lods_and_pivots_unchanged=True,source_sword_sha256=sha(native_geo),sword_wsmodel=weapon,attachment='weapon_2',no_custom_animation_export=True,body_weights_skills_stats_and_recruitment_unchanged=True,portraits_updated=True,shared_native_textures=sorted(native_shared),changed_existing_payloads=sorted(p for p in before if after[p]!=before[p]),new_payloads=sorted(set(after)-set(before)),deployed=False,runtime_verified=False)
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not blocking
