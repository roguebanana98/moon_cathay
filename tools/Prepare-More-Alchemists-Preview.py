"""Resolve only textures used by the private preview; all source packs read-only."""
import sys,json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/more-alchemists'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/addon-source'));import rmv2_format as rf
want=set();models=[]
for p in sorted(D.rglob('*.rigid_model_v2')):
    model=rf.load(p.read_bytes());models.append(dict(file=p.relative_to(D).as_posix(),skeleton=model.skeleton_name,parts=len(model.lods[0].models),lods=len(model.lods)))
    for mesh in model.lods[0].models:
        tex=mesh.material.textures;hasbase=any(t==27 for t,path in tex)
        for t,path in tex:
            if t not in ([27,1,29] if hasbase else [0,1,29]):continue
            path=path.replace('\\','/').lower()
            if not (D/path).is_file():want.add(path)
assert len(models)==10 and all(m['skeleton']=='humanoid01e' for m in models)
found=[]
for pack in (Path(C['game'])/'data').glob('variants_dds*.pack'):
    names=set(subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(pack)],text=True,stderr=subprocess.DEVNULL).splitlines())
    hits=want&names
    if hits:
        subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f']+[p+';'+str(D) for p in sorted(hits)],check=True,stdout=subprocess.DEVNULL)
        found.extend(dict(pack=str(pack),path=p) for p in hits);want-=hits
    if not want:break
assert not want,sorted(want)
(D/'preview-reference.json').write_text(json.dumps(dict(models=models,native_textures=found,source_pack_sha256=hashlib.sha256((Path(C['workshop'])/'2854480153/!solaire_more_alchemists.pack').read_bytes()).hexdigest()),indent=2))
print('Ready: 10 complete model variants and all required preview textures')
