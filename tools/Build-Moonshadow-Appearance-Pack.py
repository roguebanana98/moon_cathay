"""Replace only Moonshadow Assassin graphics over the installed v6 roster."""
import csv,json,hashlib,subprocess,shutil,struct,copy,sys
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moonshadow-v7-appearance';BASE=Path(C['game'])/'data/mc_moonshadow_heroes_v6_celestial_tower.pack'
PACK=O/'mc_moonshadow_heroes_v7_appearance.pack'
if PACK.exists():
    assert '--rebuild' in sys.argv and not json.loads((O/'pack-validation.json').read_text())['deployed'],'Preserve deployed builds'
E=json.loads((O/'export-report.json').read_text());faces=[8,11,3,12];G='variantmeshes/wh_variantmodels/mc_moonshadow_assassin'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE)=='584b353b46bda2f284687e77fe0fba26119ebe843b9f69760d1edd1e919e7333'
def unpack(path):
    raw=Path(path).read_bytes();assert raw[:4]==b'PFH5';_,dc,ds,fc,fs,_=struct.unpack_from('<6I',raw,4);pos=28+ds;end=pos+fs;entries=[]
    for _ in range(fc):
        size,compression=struct.unpack_from('<IB',raw,pos);pos+=5;assert compression==0
        stop=raw.index(0,pos);name=raw[pos:stop].decode().replace('\\','/');pos=stop+1;entries.append((name,size))
    assert pos==end;result={}
    for name,size in entries:result[name]=raw[pos:pos+size];pos+=size
    assert pos==len(raw);return {k:v for k,v in result.items() if not k.endswith('.rpfm_reserved')}
def cli(*args):
    p=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
    with (O/'pack-build.log').open('a',encoding='utf8') as f:f.write(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
files=[];dbfiles=[]
def table(name,rows,header=None):
    if header is None:header=read(R/('reference/local/lord-vanilla/db/'+name+'_tables/data__.tsv'))[0]
    h,m=copy.deepcopy(header);internal='db/'+name+'_tables/mc_moonshadow' if name in ('unit_variants','campaign_character_arts') else 'db/'+name+'_tables/mc_moonshadow_appearance'
    m[0]=';'.join(m[0].split(';')[:2]+[internal]);p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows([h,m]+[[r.get(k,'') for k in h] for r in rows])
    dbfiles.append(internal)
    return internal
Q=R/'build/moonshadow-celestial-tower'
h,rows=read(Q/'db/unit_variants_tables/mc_moonshadow.tsv');old=copy.deepcopy(rows)
next(r for r in rows if r['unit']=='mc_moonshadow_assassin_human')['variant']='mc_moonshadow_assassin'
table('unit_variants',rows,h)
h,arts=read(Q/'db/campaign_character_arts_tables/mc_moonshadow.tsv');generic=next(r for r in arts if r['art_set_id']=='mc_moonshadow_assassin_art');legendary=next(r for r in arts if r['art_set_id']=='mc_da_anh_art').copy()
artrows=[legendary];uniforms=[];variants=[]
def native_row(t,k,value):return next(r for r in read(R/('reference/local/lord-vanilla/db/'+t+'_tables/data__.tsv'))[1] if r[k]==value).copy()
for i,n in enumerate(faces):
    key='mc_moonshadow_assassin_face%02d'%n;uniform='mc_moonshadow_uniform_face%02d'%n
    row=generic.copy();row['id']=str(1986112100 if i==0 else 1986112110+i);row['uniform']=uniform;artrows.append(row)
    row=native_row('agent_uniforms','uniform_name','wh2_main_uniform_def_khainite_assassin_01');row.update(uniform_name=uniform,filename=key,battle_filename=key,campaign_porthole_filename=key);uniforms.append(row)
    row=native_row('variants','variant_name','wh2_main_def_assassin');row.update(variant_name=key,variant_filename=key,low_poly_filename='',super_low_poly_filename='',scale_variation='0.0000');variants.append(row)
row=variants[0].copy();row.update(variant_name='mc_moonshadow_assassin',variant_filename='mc_moonshadow_assassin');variants.append(row)
table('campaign_character_arts',artrows,h);table('agent_uniforms',uniforms);table('variants',variants)
def vmd(key,choices):
    root=ET.Element('VARIANT_MESH');slot=ET.SubElement(root,'SLOT',name='body')
    for n in choices:
        node=ET.SubElement(slot,'VARIANT_MESH',model=G+'/moonshadow_face_%02d.rigid_model_v2'%n);ET.SubElement(node,'META_DATA').text='audio_armour_type:leather'
    for name,bone,model in [('weapon_1','be_prop_0',None),('weapon_2','be_prop_1','knife'),('shield','be_prop_2',None),('weapon_3','be_prop_3',None),('weapon_4','be_prop_4',None),('weapon_5','be_prop_5','handbow')]:
        slot=ET.SubElement(root,'SLOT',name=name,attach_point=bone)
        if model:
            node=ET.SubElement(slot,'VARIANT_MESH',model=G+'/'+model+'.rigid_model_v2');ET.SubElement(node,'META_DATA').text='equipment'
    path='variantmeshes/variantmeshdefinitions/'+key+'.variantmeshdefinition';p=O/path;p.parent.mkdir(parents=True,exist_ok=True);ET.indent(root);p.write_bytes(ET.tostring(root,encoding='utf-8'));files.append(path)
vmd('mc_moonshadow_assassin',faces)
for n in faces:vmd('mc_moonshadow_assassin_face%02d'%n,[n])
for n in faces:
    for folder in ('units','portholes'):
        src=O/'renders'/('face_%02d_%s.png'%(n,'body' if folder=='units' else 'head'))
        path='ui/portraits/'+folder+'/no_culture/mc_moonshadow_assassin_face%02d_0.png'%n;p=O/path;p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,p);files.append(path)
for folder in ('units','portholes'):
    data=json.loads((Q/('portrait-mc_moonshadow_assassin-'+folder+'.json')).read_text());entry=data['entries'][0];donor=entry['variants'][0];entry['variants']=[]
    for n in faces:
        variant=donor.copy();variant.update(filename='mc_moonshadow_assassin_face%02d'%n,file_diffuse='ui/portraits/'+folder+'/no_culture/mc_moonshadow_assassin_face%02d_0.png'%n);entry['variants'].append(variant)
    jp=O/('portrait-'+folder+'.json');jp.write_text(json.dumps(data,indent=2));path='ui/portraits/'+folder+'/portrait_settings__mc_moonshadow_assassin.bin'
    cli('portrait-settings','from-json','-j',jp,'-b',O/path);files.append(path)
for path,kind,size in [('ui/units/icons/mc_moonshadow_assassin.png','body',(104,208)),('ui/units/minspec_portholes/mc_moonshadow_assassin_human.png','head',(256,256))]:
    p=O/path;p.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(O/'renders'/('face_08_'+kind+'.png')) as im:im.resize(size,Image.Resampling.LANCZOS).save(p)
    files.append(path)
models=[]
for path in sorted((O/G).glob('*.rigid_model_v2')):
    model=rf.load(path.read_bytes());assert len(model.lods)==4
    weighted=path.stem.startswith('moonshadow_face_');assert model.skeleton_name==('humanoid01d' if weighted else '')
    counts=[]
    for lod in model.lods:
        count=0
        for part in lod.models:
            me=part.mesh;assert len(me.positions)>0 and len(me.indices)%3==0
            if weighted:
                assert me.bone_indices.max()<83;assert abs(me.bone_weights.sum(axis=1)-1).max()<.02
            for typ,tx in part.material.textures:
                assert (O/tx.replace('\\','/')).is_file(),tx
            count+=len(me.indices)//3
        counts.append(count)
    assert all(a>=b>0 for a,b in zip(counts,counts[1:]));models.append({'path':path.relative_to(O).as_posix(),'lod_triangles':counts});files.append(path.relative_to(O).as_posix())
assert len(models)==6
for path in sorted((O/G/'tex').glob('*.dds')):
    assert path.read_bytes()[:4]==b'DDS ';files.append(path.relative_to(O).as_posix())
shutil.copy2(BASE,PACK)
cli('pack','add','-p',PACK,'-t',C['schema'],'-f',*[str(O/(p+'.tsv'))+';'+p for p in dbfiles])
cli('pack','add','-p',PACK,'-f',*[str(O/p)+';'+p for p in files])
before=unpack(BASE);after=unpack(PACK);changed=[p for p in before if before[p]!=after[p]]
allowed={'db/unit_variants_tables/mc_moonshadow','db/campaign_character_arts_tables/mc_moonshadow','ui/portraits/units/portrait_settings__mc_moonshadow_assassin.bin','ui/portraits/portholes/portrait_settings__mc_moonshadow_assassin.bin','ui/units/icons/mc_moonshadow_assassin.png','ui/units/minspec_portholes/mc_moonshadow_assassin_human.png'}
assert set(changed)==allowed,changed
assert all(after[p]==before[p] for p in before if p not in allowed)
assert set(after)==set(before)|set(files)|set(dbfiles)
roundtrip=O/'roundtrip';roundtrip.mkdir(exist_ok=True);cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','db;'+str(roundtrip))
for p in dbfiles:assert read(O/(p+'.tsv'))[1]==read(roundtrip/(p+'.tsv'))[1]
assert next(r for r in read(roundtrip/'db/campaign_character_arts_tables/mc_moonshadow.tsv')[1] if r['art_set_id']=='mc_da_anh_art')==legendary
with (O/'diagnostics.txt').open('w',encoding='utf8') as f:
    subprocess.run([C['rpfm'],'-g','warhammer_3','pack','diagnose','-g',C['game'],'-P','D:/Warhammer3_Modding/east_sea_charter/sariwa_custom_battle/resume-game.pak2','-s',C['schema'],'-p',str(PACK)],check=True,stdout=f,stderr=subprocess.STDOUT)
text=(O/'diagnostics.txt').read_text();diagnostics=json.loads(text[text.index('{'):]);blocking=[]
for group in diagnostics['results']:
    for kind,g in group.items():
        for issue in g.get('results',[]):
            typ=issue['report_type']
            if not(isinstance(typ,dict) and set(typ)=={'NoReferenceTableNorColumnFoundNoPak'}):blocking.append({'kind':kind,'path':g.get('path'),'issue':issue})
report={'status':'static_checks_passed' if not blocking else 'diagnostics_need_review','pack':str(PACK),'sha256':sha(PACK),'base':str(BASE),'base_sha256':sha(BASE),'models':models,'changed_entries':changed,'new_entries':sorted(set(after)-set(before)),'gameplay_skills_recruitment_spawn_unchanged':True,'da_anh_unchanged':True,'native_animation_links_unchanged':True,'face_order':faces,'blocking_diagnostics':blocking,'deployed':False,'runtime_verified':False}
(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('new_entries','blocking_diagnostics')},indent=2))
assert not blocking,blocking
