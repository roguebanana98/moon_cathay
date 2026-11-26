import json,subprocess,re,xml.etree.ElementTree as E
from pathlib import Path
R=Path.cwd();C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));D=R/'reference/local/xiao-original'
p=Path(C['workshop'])/"3270368516/@mustdy_sarv_hakutaku_diviner.pack"
ws=list(D.rglob('*.wsmodel'))
want={x.text.replace('\\','/').lower() for p in ws for x in E.parse(p).findall('.//material') if x.get('lod_index')=='0'}
def resolve(want,pattern):
 want={p for p in want if not (D/p).exists()}
 for pack in (Path(C['game'])/'data').glob(pattern):
  if not want:break
  names=set(subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(pack)],text=True,stderr=subprocess.DEVNULL).splitlines());hits=want&names
  if hits:
   subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f']+[p+';'+str(D) for p in sorted(hits)],check=True,stdout=subprocess.DEVNULL);want-=hits
 return want
missing=resolve(want,'variants*.pack');missing=resolve(missing,'*.pack') if missing else set()
assert not missing,missing
tex={path.replace('\\','/').lower() for p in want for slot,path in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',(D/p).read_text()) if slot in ['t_xml_base_colour','t_xml_diffuse','t_xml_normal','t_xml_material_map']}

missing=resolve(tex,'variants_dds*.pack');missing=resolve(missing,'*.pack') if missing else set()
print('MISSING',sorted(missing),'MATERIALS',len(want),'TEXTURES',len(tex))