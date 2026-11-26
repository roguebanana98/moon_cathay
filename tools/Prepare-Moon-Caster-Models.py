"""Namespace three read-only Hakutaku appearances; preserve original four LODs."""
import ast, hashlib, json, re, shutil, struct, subprocess, sys
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]; C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/sarvente-hakutaku';O=R/'build/moon-casters-v13';O.mkdir(parents=True,exist_ok=True)
G='variantmeshes/wh_variantmodels/mc_moon_casters';P='variantmeshes/wh_variantmodels/hu1e/cth/cth_hakutaku_diviner/'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
files=set();mapped={};bakes=[];audit=[]
def norm(p):return p.replace('\\','/').lower()
def put(p,b):
    target=O/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);files.add(p)
def dependency(p):
    p=norm(p)
    if p in mapped:return mapped[p]
    assert (D/p).is_file(),p
    dest=G+'/textures/'+hashlib.sha256(p.encode()).hexdigest()[:12]+'_'+Path(p).name
    mapped[p]=dest;put(dest,(D/p).read_bytes());return dest
def material(p,moon=False,tide=False):
    p=norm(p);name=Path(p).name
    # Identical garment UVs: take the original charcoal/red cloth for the moon model,
    # then bake its base colour to neutral silver with a Blender material shader.
    if moon:
        p=p.replace('shirt_white_','shirt_').replace('skirt_white_','skirt_').replace('head_acc_white_','head_acc_')
    dest=G+'/materials/'+('moon_' if moon else 'tide_' if tide else '')+hashlib.sha256(p.encode()).hexdigest()[:10]+'_'+Path(p).name
    if dest in files:return dest
    text=(D/p).read_text(encoding='utf8')
    def replace(m):
        source=norm(m.group(1))
        if not (D/source).is_file():return m.group(0) # Native shared texture or shader placeholder.
        target=dependency(source)
        if moon and any(x in name for x in ('shirt_white','skirt_white','head_acc_white')) and 'diffuse' in source:
            target=G+'/textures/moon_'+Path(source).name
            if not any(b['target']==target for b in bakes):bakes.append(dict(source=str(D/source),target=target))
        if tide and any(x in name for x in ('shirt_3','skirt_3')) and 'diffuse' in source:
            target=G+'/textures/tide_'+Path(source).name
            if not any(b['target']==target for b in bakes):bakes.append(dict(source=str(D/source),target=target,value=0.25,saturation=0.85))
        return '<source>'+target+'</source>'
    text=re.sub(r'<source>(.*?)</source>',replace,text)
    put(dest,text.encode('utf8'));return dest
models=[]
for i,key,name in [(1,'mc_pyromancer','Pyromancer'),(2,'mc_astral_weaver','Astral Weaver'),(3,'mc_tidecaller','Tidecaller')]:
    tree=ET.parse(D/(P+'cth_hakutaku_diviner_%02d.wsmodel'%i));geometry=norm(tree.findtext('geometry'))
    model=rf.load((D/geometry).read_bytes())
    assert model.skeleton_name=='humanoid01e' and len(model.lods)==4
    geo=G+'/'+key+'.rigid_model_v2';put(geo,(D/geometry).read_bytes());tree.find('geometry').text=geo
    for ref in tree.findall('.//material'):ref.text=material(ref.text,i==2,i==3)
    ws=G+'/'+key+'.wsmodel';put(ws,ET.tostring(tree.getroot(),encoding='utf8'))
    vmd='variantmeshes/variantmeshdefinitions/'+key+'.variantmeshdefinition'
    root=ET.Element('VARIANT_MESH');slot=ET.SubElement(root,'SLOT',name='body');node=ET.SubElement(slot,'VARIANT_MESH',model=ws)
    ET.SubElement(node,'META_DATA').text='audio_armour_type:leather'
    put(vmd,ET.tostring(root,encoding='utf8'))
    models.append(dict(key=key,name=name,source_model=i,wsmodel=ws,vmd=vmd,palette=['black / dark red','black / silver','navy / silver'][i-1]))
    audit.append(dict(key=key,skeleton=model.skeleton_name,lod_parts=[len(l.models) for l in model.lods],geometry_byte_identical=True))
report=dict(models=models,files=sorted(files),shader_bakes=bakes,audit=audit,spells_pending=True,source_pack='F:/SteamLibrary/steamapps/workshop/content/1142710/3270368516/@mustdy_sarv_hakutaku_diviner.pack')
(O/'models.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(models=models,files=len(files),bakes=bakes,audit=audit),indent=2))
