"""Read the actual exported RMV2/DDS/XML payload, not just the Blender scene."""
from pathlib import Path
import importlib.util
import sys,json,struct,hashlib
import numpy as np
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1]) if len(sys.argv)>1 else R/'build/huyen-ve-model-v1'
path=R.parent/'tooling/model-workbench/addon-source/rmv2_format.py'
spec=importlib.util.spec_from_file_location('rmv2_check',path);rf=importlib.util.module_from_spec(spec);sys.modules[spec.name]=rf;spec.loader.exec_module(rf)
results=[]
for path in (OUT/'variantmeshes').rglob('*.rigid_model_v2'):
    model=rf.load(path.read_bytes());body='body' in path.name
    assert model.version==8 and len(model.lods)==4
    assert model.skeleton_name==('humanoid01e' if body else '')
    lods=[]
    for level,lod in enumerate(model.lods):
        assert len(lod.models)==1
        obj=lod.models[0];mesh=obj.mesh;mat=obj.material
        assert np.isfinite(mesh.positions).all()
        assert len(mesh.indices)%3==0 and max(mesh.indices)<mesh.vertex_count
        assert mat.vertex_format==((4 if level<2 else 3) if body else 0)
        assert mat.matrix_index==-1
        if body:
            assert mesh.bone_indices.max()<96
            assert np.max(np.abs(mesh.bone_weights.sum(axis=1)-1))<.005
            assert np.all(mesh.bone_weights.sum(axis=1)>0)
        else:assert mesh.bone_weights.shape[1]==0
        for typ,tex in mat.textures:assert (OUT/tex).is_file(),tex
        lods.append(dict(level=level,triangles=len(mesh.indices)//3,vertices=mesh.vertex_count,format=mat.vertex_format))
    results.append(dict(file=path.relative_to(OUT).as_posix(),skeleton=model.skeleton_name,lods=lods))

for path in (OUT/'variantmeshes').rglob('*'):
    if path.suffix not in ['.wsmodel','.material','.variantmeshdefinition']:continue
    tree=ET.parse(path);refs=[x.text for x in tree.iter() if x.tag in ['geometry','material','source'] and x.text and x.text.strip()]
    refs += [x.attrib['model'] for x in tree.iter('VARIANT_MESH') if 'model' in x.attrib]
    for ref in refs:assert ref.startswith('commontextures/') or (OUT/ref).is_file(),(path,ref)
vmd=ET.parse(OUT/'variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition')
weapon=vmd.find("./SLOT[@name='weapon_2']");assert weapon.get('attach_point')=='weapon_2' and weapon.find('VARIANT_MESH') is not None
textures=[]
for path in (OUT/'variantmeshes').rglob('*.dds'):
    b=path.read_bytes();assert b[:4]==b'DDS '
    h,w=struct.unpack_from('<II',b,12);mips=struct.unpack_from('<I',b,28)[0]
    assert w in [512,1024,2048] and w==h and mips>=10
    textures.append(dict(file=path.name,width=w,height=h,mipmaps=mips))
manifest=json.loads((OUT/'graphics-manifest.json').read_text());assert len(manifest['files'])==16
report=dict(status='exported_asset_checks_passed',models=results,textures=textures,vmd_weapon_2=True,
    hashes={p:hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in manifest['files']},
    scope='Static binary/path checks; not WH3 runtime verification')
(OUT/'export-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['models'],indent=2))
