"""Convert supplied sword PBR maps to WH3 DDS; source textures remain intact."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-fantasy-longsword';I='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/fantasy_sword/tex';T=O/I;T.mkdir(parents=True,exist_ok=True)
tmp=O/'texture-input';tmp.mkdir(exist_ok=True);A=next((R/'assets/authored/fantasy longsword 3d model').glob('*.fbm'));files=[]
def read(name,mode):return Image.open(next(p for p in A.iterdir() if p.stem.endswith('_'+name))).convert(mode).resize((2048,2048),Image.Resampling.LANCZOS)
def save(name,im,fmt,srgb=False):
 p=tmp/(name+'.png');im.save(p)
 subprocess.run([C['texconv'],'-nologo','-y']+(['-srgb'] if srgb else [])+['-m','0','-f',fmt,'-o',str(T),str(p)],check=True,stdout=subprocess.DEVNULL)
 files.append(I+'/'+name+'.dds')
save('fantasy_sword_base_colour',read('basecolor','RGB'),'BC7_UNORM_SRGB',True)
metal=np.array(read('metallic','L'));rough=np.array(read('roughness','L'));mm=np.full((*metal.shape,4),255,np.uint8);mm[:,:,0]=metal;mm[:,:,1]=rough
save('fantasy_sword_material_map',Image.fromarray(mm),'BC7_UNORM')
n=np.array(read('normal','RGB'));orange=np.zeros((*n.shape[:2],4),np.uint8);orange[:,:,0]=255;orange[:,:,1]=255-n[:,:,1];orange[:,:,3]=n[:,:,0]
save('fantasy_sword_normal',Image.fromarray(orange),'BC3_UNORM')
save('fantasy_sword_mask',Image.new('RGBA',(128,128),(0,0,0,0)),'BC3_UNORM')
(O/'texture-conversion.json').write_text(json.dumps(dict(files=files,size=[2048,2048],mask_size=[128,128],normal='WH3 orange: R255 G(255-sourceG) B0 A(sourceR)',material='R metallic G roughness B255 A255',mipmaps=True),indent=2))
print('Sword DDS conversion complete')
