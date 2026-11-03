import pathlib,json,subprocess,xml.etree.ElementTree as E
R=pathlib.Path('D:/Warhammer3_Modding/moon_cathay');C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));D=R/'reference/local/pandalorian-yuan-bo';game=pathlib.Path(C['game'])/'data'
ws=D/'variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.wsmodel'
paths={x.text.replace('\\','/').lower() for x in E.parse(ws).findall('.//material')}
for phase in range(2):
 missing={p for p in paths if not (D/p).exists()};print('MISSING',len(missing),flush=True)
 for pack in game.glob('variants*.pack'):
  if not missing:break
  lines=subprocess.check_output([C['rpfm'],'-g','warhammer_3','pack','list','-p',str(pack)],stderr=subprocess.DEVNULL,text=True).splitlines();hits=[p for p in lines if p.lower() in missing]
  if hits:
   subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f']+[p+';'+str(D) for p in hits],check=True);missing-={p.lower() for p in hits}
 if phase==0:
  paths={x.text.replace('\\','/').lower() for p in paths if (D/p).exists() for x in E.parse(D/p).findall('.//texture/source') if x.text and 'commontextures' not in x.text.lower()}
print('UNRESOLVED',missing)

