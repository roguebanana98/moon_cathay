"""Read-only dependency extraction for all original unmounted WWD lord appearances."""
import csv,json,re,struct,subprocess,sys,shutil
from pathlib import Path
from lxml import etree as E
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/wwd-all-lords-preview';D=R/'reference/local/wwd-all-lords';D.mkdir(parents=True,exist_ok=True)
SOURCE=Path(C['workshop'])/'2789903784/DEER24Cathay.pack';GAME=Path(C['game'])/'data'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
indexes={};missing=set();aliases={}
def norm(s):return s.replace('\\','/').strip().lower()
def index(pack):
    key=str(pack)
    if key not in indexes:
        text=subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',key],encoding='utf8')
        indexes[key]={norm(p):p for p in text.splitlines() if p.strip() and '[INFO]' not in p and '[WARN]' not in p}
    return indexes[key]
def extract(pack,paths):
    for start in range(0,len(paths),20):
        subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f',*[p+';'+str(D) for p in paths[start:start+20]]],check=True,stdout=subprocess.DEVNULL)
def resolve(paths,kind='model'):
    todo={norm(p) for p in paths if p and not (D/norm(p)).exists()}
    packs=[SOURCE]
    if kind=='texture':packs+=list(GAME.glob('variants_dds*.pack'))+list(GAME.glob('warmachines_dds*.pack'))+[GAME/'commontextures.pack']+list(GAME.glob('models*dds.pack'))+list(GAME.glob('terrain_textures*.pack'))
    elif kind=='animation':packs += [GAME/'anim2.pack',GAME/'anim.pack',GAME/'anim_3.pack']+list(GAME.glob('anim[3-9]*.pack'))
    else:packs += [p for p in GAME.glob('variants*.pack') if '_dds' not in p.name]
    for pack in packs:
        if not todo:break
        ix=index(pack);hits=todo&ix.keys()
        if hits:extract(pack,[ix[p] for p in sorted(hits)]);todo-=hits
    # Some donor WSModels have stale parent folders for otherwise native materials.
    for path in list(todo):
        if not path.endswith(('.xml.material','.dds')):continue
        for pack in packs:
            ix=index(pack);replacement=path.replace('_diffuse.dds','_base_colour.dds')
            if path=='commontextures/default_black.dds':replacement='commontextures/default_black_srgb.dds'
            hits=[ix[replacement]] if replacement!=path and replacement in ix else [real for key,real in ix.items() if Path(key).name in {Path(path).name,Path(replacement).name}]
            if len(hits)==1:
                extract(pack,hits);actual=norm(hits[0]);dest=D/path;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(D/actual,dest);aliases[path]=actual;todo.remove(path);break
    if todo:missing.update(todo)
    return todo
def xml(path):return E.fromstring(Path(path).read_bytes(),parser=E.XMLParser(recover=True))
def read(t):
    out=[]
    for p in (R/'reference/local/deer-wwd/base/db'/(t+'_tables')).glob('*.tsv'):
        with p.open(encoding='utf-8-sig') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
        out.extend(dict(zip(a[0],r)) for r in a[2:])
    return out
variants={r['variant_name']:r for r in read('variants')}
selected=json.loads((O/'lords.json').read_text(encoding='utf8'))
def vmd_path(key):
    v=variants[key];return 'variantmeshes/variantmeshdefinitions/'+v['variant_filename']+'.variantmeshdefinition'
def components(path,attach='',visited=None):
    path=norm(path);visited=set() if visited is None else visited
    assert path not in visited,path
    visited=visited|{path};assert not resolve([path])
    result=[]
    def walk(node,bone):
        tag=str(node.tag).upper();bone=node.get('attach_point',bone)
        if tag=='VARIANT_MESH_REFERENCE':
            result.extend(components(node.get('definition'),bone,visited));return
        if tag=='VARIANT_MESH' and node.get('model'):
            model_path=norm(node.get('model'))
            if Path(model_path).name!='null.rigid_model_v2':result.append(dict(path=model_path,attach=bone))
        if tag=='SLOT':
            choices=[x for x in node if str(x.tag).upper() in ('VARIANT_MESH','VARIANT_MESH_REFERENCE')]
            if choices:walk(choices[0],bone)
            for x in node:
                if str(x.tag).upper()=='SLOT':walk(x,bone)
        else:
            for x in node:
                if str(x.tag).upper() not in ('META_DATA','COMMENT'):walk(x,bone)
    walk(xml(D/path),attach);return result
for lord in selected:
    lord['vmd_path']=vmd_path(lord['variant']);lord['scale']=float(variants[lord['variant']]['scale'])
    lord['components']=components(lord['vmd_path'])
unresolved=resolve([c['path'] for l in selected for c in l['components']]);assert not unresolved,sorted(unresolved)
geometry=set();materials=set()
for lord in selected:
    for c in lord['components']:
        if c['path'].endswith('.wsmodel'):
            tree=xml(D/c['path']);c['geometry']=norm(tree.findtext('geometry'))
            c['materials']={int(x.get('part_index')):norm(x.text) for x in tree.findall('.//material') if x.get('lod_index')=='0'}
            materials.update(c['materials'].values())
        else:c['geometry']=c['path'];c['materials']={}
        geometry.add(c['geometry'])
unresolved=resolve(geometry);assert not unresolved,sorted(unresolved)
unresolved=resolve(materials)
for lord in selected:
    for component in lord['components']:
        for part,material in list(component['materials'].items()):
            if material in unresolved:
                component.setdefault('embedded_material_fallbacks',{})[part]=material
                del component['materials'][part]
missing-=unresolved
textures=set()
for lord in selected:
    for c in lord['components']:
        model=rf.load((D/c['geometry']).read_bytes());c['skeleton']=model.skeleton_name;c['parts']=[]
        for i,part in enumerate(model.lods[0].models):
            mat=c['materials'].get(i)
            if mat:
                tree=xml(D/mat);pairs=[]
                for tx in tree.findall('.//texture'):
                    typ={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29}.get(tx.findtext('slot'))
                    source=tx.findtext('source')
                    if typ is not None and source and source.lower().endswith('.dds'):pairs.append([typ,norm(source)])
                alpha='alpha_on' in mat.lower() or 'alpha' in (tree.findtext('shader') or '').lower()
            else:
                pairs=[[t,norm(p)] for t,p in part.material.textures if t in (0,1,27,29) and p.lower().endswith('.dds')]
                alpha='alpha' in str(part.material.material_id).lower()
            textures.update(p for _,p in pairs)
            c['parts'].append(dict(name=part.material.model_name,textures=pairs,alpha=alpha,vertices=part.mesh.vertex_count))
    lord['skeleton']=next(c['skeleton'] for c in lord['components'] if c['skeleton'])
    print('GEOMETRY',lord['unit'],lord['skeleton'],sum(p['vertices'] for c in lord['components'] for p in c['parts']),flush=True)
resolve(textures,'texture')
assert not missing,sorted(missing)
resolve(['animations/database/battle/bin/wwd_animation_tables.animpack','animations/database/battle/bin/wwd_guanyu.animpack'])
bins={}
for pack in list((R/'reference/local/native-animation-runtime').rglob('*.animpack'))+list(D.rglob('*.animpack')):
    b=pack.read_bytes();count=struct.unpack_from('<I',b)[0];pos=4
    for _ in range(count):
        size=struct.unpack_from('<H',b,pos)[0];pos+=2;name=b[pos:pos+size].decode();pos+=size;size=struct.unpack_from('<I',b,pos)[0];pos+=4
        bins[Path(name).stem]=b[pos:pos+size];pos+=size
animations=set()
for lord in selected:
    data=bins.get(lord['anim'],b'');paths=re.findall(rb'animations/[a-zA-Z0-9_./ -]+?\.anim',data)
    choices=[p.decode() for p in paths if '/stand/' in p.decode() and not any(x in p.decode() for x in ['to_stand','stand_to','idle'])]
    if not choices:choices=[p.decode() for p in paths if '/stand/' in p.decode()]
    lord['idle']=choices[0] if choices else None
    animations.add('animations/skeletons/'+lord['skeleton']+'.anim')
    if lord['idle']:animations.add(lord['idle'])
resolve(animations,'animation');assert not missing,sorted(missing)
(O/'manifest.json').write_text(json.dumps(dict(lords=selected,source=str(SOURCE),reference=str(D),textures=len(textures),preview_material_aliases=aliases,missing=sorted(missing)),indent=2),encoding='utf8')
print('ALL_LORD_ASSETS_READY',len(selected),'textures',len(textures),flush=True)
