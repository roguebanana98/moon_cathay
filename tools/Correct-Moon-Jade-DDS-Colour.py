"""Preserve sRGB bake values across DDS encoding (avoid a second gamma curve)."""
import json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-reskin-v1';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));E=json.loads((O/'export-report.json').read_text())
count=0
for path in E['textures']:
 if not path.endswith('_base_colour.dds'):continue
 dds=O/path;png=O/'bake'/(dds.stem+'.png');assert png.is_file()
 subprocess.run([C['texconv'],'-nologo','-y','-m','0','-srgbi','-f','BC7_UNORM_SRGB','-o',str(dds.parent),str(png)],check=True,stdout=subprocess.DEVNULL)
 dest=O/'roundtrip-textures'/Path(path).parent;dest.mkdir(parents=True,exist_ok=True)
 subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(dds)],check=True,stdout=subprocess.DEVNULL)
 E['textures'][path]=hashlib.sha256(dds.read_bytes()).hexdigest();count+=1
E['base_colour_srgb_input_explicit']=True;(O/'export-report.json').write_text(json.dumps(E,indent=2));print('SRGB_COLOUR_PRESERVED',count,flush=True)
