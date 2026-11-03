"""Create the private VMD/WSMODEL/material graph for the authored model."""
from pathlib import Path
import json,sys
import xml.etree.ElementTree as ET

R=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1]) if len(sys.argv)>1 else R/'build/huyen-ve-model-v1'
REF=R/'reference/local/yuan-bo-model/variantmeshes/wh_variantmodels/hu1e/cth'
BASE='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve'
DEST=OUT/BASE;(DEST/'materials').mkdir(parents=True,exist_ok=True)

def save(root,path):
    ET.indent(root,space='  ');path.parent.mkdir(parents=True,exist_ok=True);ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=False)

for asset in ['body','sword']:
    formats=['weighted4','weighted2'] if asset=='body' else ['rigid']
    for fmt in formats:
        filename='mc_huyen_ve_'+asset+'_'+fmt+'.xml.material'
        template=(REF/'cth_dragon_jade_human/materials'/('cth_dragon_jade_human_01_'+fmt+'_alpha_off.xml.material')) if asset=='body' else REF/'cth_props/materials/cth_dragon_jade_human_sword_2h_01_alpha_off.xml.material'
        root=ET.parse(template).getroot();root.find('name').text=filename.removesuffix('.material')
        for source in root.findall('./textures/texture/source'):
            old=source.text.lower()
            if '/tex/cth_dragon_jade_human_' in old:
                suffix=next(x for x in ['base_colour','material_map','normal','mask'] if old.endswith('_'+x+'.dds'))
                source.text=BASE+'/tex/mc_huyen_ve_'+asset+'_'+suffix+'.dds'
        for param in root.findall('./params/param'):
            if param.findtext('name')=='emissive_strength':param.find('value').text='0'
        save(root,DEST/'materials'/filename)
    root=ET.Element('model',version='1');ET.SubElement(root,'geometry').text=BASE+'/mc_huyen_ve_'+asset+'.rigid_model_v2';mats=ET.SubElement(root,'materials')
    for level in range(4):
        fmt=('weighted4' if level<2 else 'weighted2') if asset=='body' else 'rigid'
        ET.SubElement(mats,'material',part_index='0',lod_index=str(level)).text=BASE+'/materials/mc_huyen_ve_'+asset+'_'+fmt+'.xml.material'
    save(root,DEST/('mc_huyen_ve_'+asset+'.wsmodel'))

root=ET.Element('VARIANT_MESH')
slot=ET.SubElement(root,'SLOT',name='body');model=ET.SubElement(slot,'VARIANT_MESH',model=BASE+'/mc_huyen_ve_body.wsmodel')
ET.SubElement(model,'META_DATA').text='audio_entity_type:wh3_dlc24_cth_yuan_bo_LORD';ET.SubElement(model,'META_DATA').text='audio_armour_type:plate'
slot=ET.SubElement(root,'SLOT',name='weapon_2',attach_point='weapon_2');model=ET.SubElement(slot,'VARIANT_MESH',model=BASE+'/mc_huyen_ve_sword.wsmodel')
ET.SubElement(model,'META_DATA').text='audio_melee_weapon_type:sword_medium'
for name in ['weapon_1','weapon_3','weapon_4','weapon_5','weapon_6']:ET.SubElement(root,'SLOT',name=name,attach_point=name)
ET.SubElement(root,'SLOT',name='head')
vmd=OUT/'variantmeshes/variantmeshdefinitions/mc_huyen_ve_human.variantmeshdefinition';save(root,vmd)
paths=sorted(p.relative_to(OUT).as_posix() for p in (OUT/'variantmeshes').rglob('*') if p.is_file())
assert len(paths)==16,len(paths)
(OUT/'graphics-manifest.json').write_text(json.dumps(dict(vmd=vmd.relative_to(OUT).as_posix(),files=paths,scope='Graphics-only asset pack for Asset Editor; no DB override, gameplay or deployment'),indent=2))
print(json.dumps(paths,indent=2))
