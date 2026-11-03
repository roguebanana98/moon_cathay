"""Deterministic PBR channel conversion for a private WH3 model build."""
import json
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
OUT=R/'build/huyen-ve-model-v1'
INTERNAL='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve'
TEX=OUT/INTERNAL/'tex';TEX.mkdir(parents=True,exist_ok=True)
TMP=OUT/'texture-intermediate';TMP.mkdir(parents=True,exist_ok=True)
SRC=next((R/'assets/authored/ancient warrior armor 3d model').glob('*.fbm'))
SIZE=(2048,2048)

def read(suffix,mode='RGB'):
    path=next(p for p in SRC.iterdir() if p.stem.endswith('_'+suffix))
    return Image.open(path).convert(mode).resize(SIZE,Image.Resampling.LANCZOS)

def dds(name,im,fmt):
    png=TMP/(name+'.png');im.save(png)
    subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f',fmt,'-o',str(TEX),str(png)],check=True)

dds('mc_huyen_ve_body_base_colour',read('basecolor'),'BC7_UNORM_SRGB')
metal=np.asarray(read('metallic','L'));rough=np.asarray(read('roughness','L'))
mm=np.empty((*metal.shape,4),dtype=np.uint8)
mm[:,:,0]=metal;mm[:,:,1]=rough;mm[:,:,2]=255;mm[:,:,3]=255
dds('mc_huyen_ve_body_material_map',Image.fromarray(mm),'BC7_UNORM')
n=np.asarray(read('normal'));orange=np.empty((*n.shape[:2],4),dtype=np.uint8)
orange[:,:,0]=255;orange[:,:,1]=255-n[:,:,1];orange[:,:,2]=0;orange[:,:,3]=n[:,:,0]
dds('mc_huyen_ve_body_normal',Image.fromarray(orange),'BC3_UNORM')
dds('mc_huyen_ve_body_mask',Image.new('RGBA',SIZE,(0,0,0,0)),'BC3_UNORM')
(OUT/'texture-conversion.json').write_text(json.dumps(dict(body_size=SIZE,
    material_map='R=metallic, G=roughness, B=255, A=255',
    normal='orange packing: R=255, G=255-source_OpenGL_G, B=0, A=source_R; decoded preview uses original normal',
    mask='RGBA=0; no faction tint or emissive',source=str(SRC)),indent=2))
