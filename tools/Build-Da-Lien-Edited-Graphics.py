"""Build v22 graphics, retaining native raw vertex channels for all surviving original geometry."""
import json,hashlib,copy,subprocess,importlib.util,sys,shutil
import xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-v22-da-lien-appearance';B=R/'build/huyen-ve-v20-da-lien-visual-test'
T='variantmeshes/wh_variantmodels/mc_da_lien';BODY=T+'/vmp_neferata/vmp_neferata_01';STAFF=T+'/vmp_props/vmp_neferata_staff_01'
H=T+'/moon_staff';files=[];proof=[]
s=importlib.util.spec_from_file_location('rf',R.parent/'tooling/model-workbench/addon-source/rmv2_format.py');rf=importlib.util.module_from_spec(s);sys.modules['rf']=rf;s.loader.exec_module(rf)
head=json.loads((O/'moon-head-geometry.json').read_text());assert hashlib.sha256(Path(head['approved_scene']).read_bytes()).hexdigest()==head['approved_sha256']
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
def xml(tree,internal):
    p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);tree.write(p,encoding='utf-8');files.append(internal)
def srgb_to_linear(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def linear_to_srgb(x):return np.where(x<=.0031308,x*12.92,1.055*np.maximum(x,0)**(1/2.4)-.055)
tmp=O/'texture-input';tmp.mkdir(exist_ok=True)
# Convert the exact approved linear-light material tint into the native diffuse map.
source=R/'build/da-lien-model-review/preview-textures/variantmeshes/wh_variantmodels/hu1ba/vmp/vmp_neferata/tex/neferata_body.png'
im=np.array(Image.open(source).convert('RGBA'));original_alpha=im[:,:,3].copy()
im[:,:,:3]=np.round(np.clip(linear_to_srgb(srgb_to_linear(im[:,:,:3].astype(np.float32)/255)*np.array(head['body_tint'])),0,1)*255).astype(np.uint8)
assert np.array_equal(im[:,:,3],original_alpha)
Image.fromarray(im).save(tmp/'da_lien_skin_warm.png')
def dds(input_name,relative,fmt,srgb=False):
    p=O/relative;p.parent.mkdir(parents=True,exist_ok=True)
    run([C['texconv'],'-nologo','-y']+(['-srgb'] if srgb else [])+['-m','0','-f',fmt,'-o',p.parent,tmp/input_name])
    produced=p.parent/(Path(input_name).stem+'.dds')
    if produced!=p:shutil.move(produced,p)
    assert p.is_file();files.append(relative)
skin=T+'/vmp_neferata/tex/da_lien_skin_warm.dds'
dds('da_lien_skin_warm.png',skin,'BC7_UNORM_SRGB',True)
skinmat=T+'/vmp_neferata/materials/da_lien_skin_warm.xml.material'
tree=E.parse(B/(T+'/vmp_neferata/materials/neferata_body_weighted4_alpha_off.xml.material'))
for tx in tree.findall('.//texture'):
    if tx.findtext('slot')=='t_xml_base_colour':tx.find('source').text=skin
xml(tree,skinmat)
# Flat PBR material patches for silver, gold and wine enamel. UVs sample patch centres.
materials={p['material']:(p['linear_color'],p['metallic'],p['roughness']) for p in head['parts']}
assert len(materials)==3
base=np.zeros((128,128,4),dtype=np.uint8);base[:,:,3]=255
mm=np.zeros_like(base);mm[:,:,2:]=255
patches={};rects=[(0,0,64,64),(64,0,128,64),(0,64,64,128)]
for (name,(color,metal,rough)),(x0,y0,x1,y1) in zip(materials.items(),rects):
    base[y0:y1,x0:x1,:3]=np.round(np.clip(linear_to_srgb(np.array(color)),0,1)*255).astype(np.uint8)
    mm[y0:y1,x0:x1,0]=round(metal*255);mm[y0:y1,x0:x1,1]=round(rough*255)
    # Game UV convention: top-left image patch is v=0.25.
    patches[name]=[(x0+x1)/256,(y0+y1)/256]
base[64:,64:,:3]=base[:64,:64,:3];mm[64:,64:]=mm[:64,:64]
Image.fromarray(base).save(tmp/'moon_base.png');Image.fromarray(mm).save(tmp/'moon_material.png')
Image.new('RGBA',(128,128),(255,128,0,128)).save(tmp/'moon_normal.png')
Image.new('RGBA',(128,128),(0,0,0,0)).save(tmp/'moon_mask.png')
tex={}
for name,fmt,srgb in [('base','BC7_UNORM_SRGB',True),('material','BC7_UNORM',False),('normal','BC3_UNORM',False),('mask','BC3_UNORM',False)]:
    tex[name]=H+'/tex/moon_'+name+'.dds';dds('moon_'+name+'.png',tex[name],fmt,srgb)
headmat=H+'/materials/moon_head.xml.material'
tree=E.parse(B/(T+'/vmp_props/materials/neferata_staff_rigid_alpha_off.xml.material'))
slots={'t_xml_base_colour':tex['base'],'t_xml_material_map':tex['material'],'t_xml_normal':tex['normal'],'t_xml_mask':tex['mask']}
for tx in tree.findall('.//texture'):
    if tx.findtext('slot') in slots:tx.find('source').text=slots[tx.findtext('slot')]
xml(tree,headmat)
def trim_model(model,remove,label):
    mesh=model.mesh;old=copy.deepcopy(mesh);tri=mesh.indices.reshape(-1,3)
    mask=np.ones(mesh.vertex_count,dtype=bool);mask[list(remove)]=False
    assert np.all(np.all(mask[tri],axis=1)|np.all(~mask[tri],axis=1)),label
    tri=tri[np.all(mask[tri],axis=1)]
    # Keep every retained vertex, including native unreferenced seam entries.
    ids=np.flatnonzero(mask);remap=np.full(mesh.vertex_count,-1,dtype=np.int32);remap[ids]=np.arange(len(ids))
    raw=np.frombuffer(mesh.raw_block,dtype=np.uint8).reshape(mesh.vertex_count,-1)[ids].copy().tobytes()
    oldn=mesh.vertex_count
    for key,value in vars(mesh).copy().items():
        if isinstance(value,np.ndarray) and key!='indices' and len(value)==oldn:setattr(mesh,key,value[ids].copy())
    mesh.raw_block=raw;mesh.indices=remap[tri].astype(np.uint16).ravel();model.bbox_min=model.bbox_max=None
    return old,ids
def material_refs(model,ref):
    root=E.parse((O/ref) if (O/ref).exists() else (B/ref))
    slots={t.findtext('slot'):t.findtext('source') for t in root.findall('.//texture')}
    model.material.textures=[(typ,slots[name]) for typ,name in [(27,'t_xml_base_colour'),(1,'t_xml_normal'),(3,'t_xml_mask'),(29,'t_xml_material_map')] if name in slots]
def save_model(f,internal,original,selection):
    p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(rf.save(f));files.append(internal);check=rf.load(p.read_bytes())
    for i,old in enumerate(original.lods[0].models):
        now=check.lods[0].models[i];ids=selection.get(i,np.arange(old.mesh.vertex_count))
        for channel in ('positions','normals','tangents','binormals','uv0','bone_indices','bone_weights'):
            assert np.array_equal(getattr(now.mesh,channel),getattr(old.mesh,channel)[ids]),(internal,i,channel)
        proof.append({'file':internal,'part':i,'retained_vertices':len(ids),'channels_exact':True})
    return check
body=rf.load((B/(BODY+'.rigid_model_v2')).read_bytes());original_body=copy.deepcopy(body)
remove=set()
islands=json.loads((R/'build/da-lien-collar-edit/collar-islands.json').read_text())['groups']
approved=set(json.loads((R/'build/da-lien-collar-edit/collar-removal-report.json').read_text())['removed_islands'])
for g in islands:
    if g['id'] in approved:remove.update(g['vertex_ids'])
assert body.lods[0].models[0].mesh.vertex_count==42547
_,body_ids=trim_model(body.lods[0].models[0],remove,'collar')
collar_removed_vertices=len(remove)
ws=E.parse(B/(BODY+'.wsmodel'))
for ref in ws.findall('.//material'):
    i=int(ref.get('part_index'))
    if i==3:ref.text=skinmat
    material_refs(body.lods[0].models[i],ref.text)
save_model(body,BODY+'.rigid_model_v2',original_body,{0:body_ids});xml(ws,BODY+'.wsmodel')
staff=rf.load((B/(STAFF+'.rigid_model_v2')).read_bytes());original_staff=copy.deepcopy(staff)
remove=set()
groups=json.loads((R/'build/da-lien-moon-staff/staff-islands.json').read_text())['groups']
for g in groups:
    if g['min'][0]<-1.20:remove.update(g['vertex_ids'])
_,staff_ids=trim_model(staff.lods[0].models[0],remove,'goblet')
staffws=E.parse(B/(STAFF+'.wsmodel'));oldref=staffws.find('.//material').text
material_refs(staff.lods[0].models[0],oldref)
template=copy.deepcopy(original_staff.lods[0].models[0])
def game(array):
    a=np.asarray(array,dtype=np.float32);return np.stack([-a[:,0],a[:,2],-a[:,1]],axis=1)
for part in head['parts']:
    model=copy.deepcopy(template);n=len(part['positions']);assert n%3==0 and n<65536
    mesh=rf.RmvMeshData.empty(n,0);mesh.positions=game(part['positions']);mesh.normals=game(part['normals'])
    mesh.tangents=game(part['tangents']);mesh.binormals=game(part['binormals'])
    mesh.uv0[:]=patches[part['material']];mesh.colours[:]=1
    mesh.indices=np.arange(n,dtype=np.uint16).reshape(-1,3)[:,[0,2,1]].ravel()
    mesh.raw_format=rf.VF_STATIC;mesh.raw_version=staff.version
    model.mesh=mesh;model.material.model_name=part['name'][:31];model.material.matrix_index=-1;model.material.parent_matrix_index=-1
    model.material.pivot=(0,0,0);model.bbox_min=model.bbox_max=None;material_refs(model,headmat)
    idx=len(staff.lods[0].models);staff.lods[0].models.append(model)
    E.SubElement(staffws.find('materials'),'material',part_index=str(idx),lod_index='0').text=headmat
check=save_model(staff,STAFF+'.rigid_model_v2',original_staff,{0:staff_ids});xml(staffws,STAFF+'.wsmodel')
errors=[]
for expected,actual in zip(staff.lods[0].models[1:],check.lods[0].models[1:]):
    err=float(np.max(np.abs(expected.mesh.positions-actual.mesh.positions)));assert err<.001;errors.append(err)
    assert actual.material.matrix_index==-1 and actual.material.parent_matrix_index==-1
    assert np.isfinite(actual.mesh.positions).all()
# Stage a complete model graph for exported-asset animation verification; only files list enters pack.
stage=R/'reference/local/da-lien-v22-graphics';shutil.copytree(B/'variantmeshes',stage/'variantmeshes',dirs_exist_ok=True)
for internal in files:
    p=stage/internal;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/internal,p)
for internal in files:
    if internal.endswith(('.wsmodel','.material')):
        for node in E.parse(O/internal).iter():
            if node.tag in ('source','geometry','material') and node.text:
                path=node.text.strip().replace('\\','/').lower()
                if path:assert path.startswith('commontextures/') or (stage/path).is_file(),(internal,path)
report={'status':'graphics_checks_passed','approved_scene':head['approved_scene'],'approved_sha256':head['approved_sha256'],
 'files':files,'retained_native_channels':proof,'head_roundtrip_max_position_error':max(errors),
 'new_head_parts':len(head['parts']),'staff_static_no_secondary_bone_attachment':True,
 'skin_tint_baked_to_diffuse':head['body_tint'],'skin_source_size':[int(im.shape[1]),int(im.shape[0])],
 'collar_removed_vertices':collar_removed_vertices,'source_model_lod_count_preserved':len(body.lods),
 'deployed':False,'runtime_verified':False}
(O/'graphics-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('files','retained_native_channels')},indent=2))
