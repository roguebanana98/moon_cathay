"""Pin Moonveil gallery selections 02/06/10/14 without random body/head choices."""
import copy, json, os, shutil
import xml.etree.ElementTree as ET
from pathlib import Path

R = Path(__file__).resolve().parents[1]
OLD = R / 'build/moonveil-v24'
O = R / 'build/moonveil-v32-approved-variants'
O.mkdir(exist_ok=True)
M = json.loads((OLD / 'models.json').read_text())
gallery = json.loads((R / 'build/moonveil-black-original-gallery/gallery.json').read_text())
choices = [next(x for x in gallery['combinations'] if x['number'] == n) for n in [2, 6, 10, 14]]
assert not (O / 'deployment.json').exists()
for path in M['files']:
    dest = O / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OLD / path, dest)
for model, selected in zip(M['models'], choices):
    root = ET.Element('VARIANT_MESH')
    ET.SubElement(root, 'META_DATA').text = 'equipment'
    for slot, source, metadata in [('body', selected['body'], 'audio_armour_type:leather'),
                                   ('head', selected['head'], 'audio_entity_type:wh3_cth_human_female')]:
        node = ET.SubElement(ET.SubElement(root, 'SLOT', name=slot), 'VARIANT_MESH', model=source)
        ET.SubElement(node, 'META_DATA').text = metadata
    (O / model['vmd']).write_bytes(ET.tostring(root, encoding='utf8'))
    model.update(gallery_number=selected['number'], body_palette='black', head_number=2,
                 representative=[selected['body'], selected['head']], selection=selected['collection'])
M['approved_gallery_numbers'] = [2, 6, 10, 14]
M['change'] = 'Exactly four selected black body variants with the selected shared head2. Existing appearance IDs retained for saved characters and portraits.'
(O / 'models.json').write_text(json.dumps(M, indent=2), encoding='utf8')
shutil.copy2(OLD / 'native-animation-paths.json', O / 'native-animation-paths.json')
review = (R / 'tools/Review-Moonveil-Adept-Models.py').read_text()
review = review.replace("O=R/'build/moonveil-v24'", "O=R/'build/moonveil-v32-approved-variants'")
p = R / 'tools/Review-Moonveil-Approved-Variants.py'
tmp = p.with_suffix('.py.tmp')
tmp.write_text(review, encoding='utf8')
os.replace(tmp, p)
print('APPROVED_MOONVEIL_READY', [(m['gallery_number'], m['key']) for m in M['models']])
