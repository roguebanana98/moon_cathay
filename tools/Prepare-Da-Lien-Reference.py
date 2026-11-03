"""Read native/model references into ignored local folders for Blender inspection."""
import json, subprocess, hashlib
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D = R/'reference/local/beautiful-neferata'
O = R/'build/da-lien-model-review'
O.mkdir(parents=True, exist_ok=True)
game = Path(C['game'])/'data'
mod = Path(C['workshop'])/'3809988722/Beautiful Neferata.pack'
def listing(pack):
    return subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(pack)], text=True, stderr=subprocess.DEVNULL).splitlines()
def extract(pack, paths):
    if paths:
        subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f'] + [p+';'+str(D) for p in paths], check=True, stdout=subprocess.DEVNULL)
found=[]
for pack in [game/'anim.pack',game/'anim2.pack',game/'anim_3.pack']:
    paths=listing(pack)
    hits=[p for p in paths if p.lower()=='animations/skeletons/humanoid01ba.anim' or ('neferata' in p.lower() and p.lower().endswith('.anim'))]
    found += [{'pack':str(pack),'path':p} for p in hits]
    selected=[p for p in hits if p.lower()=='animations/skeletons/humanoid01ba.anim' or '/stand/' in p.lower() or '/cast' in p.lower()]
    extract(pack, selected)
    print(pack.name, len(hits), 'clips, extracted',len(selected),flush=True)
# Native variant definition is used only to resolve original prop attachment points.
for pack in [game/'variants5.pack',game/'variants4.pack',game/'variants3.pack',game/'variants2.pack',game/'variants.pack']:
    hits=[p for p in listing(pack) if 'neferata' in p.lower() and p.lower().endswith('.variantmeshdefinition')]
    if hits:
        extract(pack,hits)
        print('VMD',hits,flush=True)
        break
manifest={'source_mod':str(mod),'source_mod_sha256':hashlib.sha256(mod.read_bytes()).hexdigest(),'clips':found,'reference_root':str(D),'status':'reference_only_no_gameplay_changes'}
(O/'reference-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(found[:18],indent=2))
