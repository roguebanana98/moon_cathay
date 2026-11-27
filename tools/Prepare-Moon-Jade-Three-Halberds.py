"""Extract only native reference assets needed for the three original halberds."""
import runpy,json,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ctx=runpy.run_path(str(R/'tools/Prepare-Moon-Jade-Family-V2.py'))
root=ET.parse(ctx['D']/'variantmeshes/variantmeshdefinitions/cth_jade_warrior_halberd.variantmeshdefinition').getroot()
slot=next(s for s in root.findall('SLOT') if s.get('name')=='weapon_1')
paths=[ctx['model'](n.get('model')) for n in slot.findall('VARIANT_MESH')];assert len(paths)==3
ctx['resolve'](ctx['textures'],'texture')
(ctx['O']/'three-halberds-assets.json').write_text(json.dumps(dict(models=[ctx['models'][p] for p in paths],native_only=True),indent=2))
print('THREE_NATIVE_HALBERDS_READY',flush=True)
