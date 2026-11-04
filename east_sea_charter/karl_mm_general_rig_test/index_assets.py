from pathlib import Path
import subprocess,concurrent.futures
R=Path(__file__).resolve().parent
GAME=Path(r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data')
CLI=r'D:\Mod TW3k\rpfm-v4.5.4-x86_64-pc-windows-msvc\rpfm_cli.exe'
def index(p):
    target=R/'indices'/(p.stem+'.txt')
    if not target.exists():
        s=subprocess.check_output([CLI,'-g','warhammer_3','pack','list','-p',str(p)],text=True,stderr=subprocess.DEVNULL)
        target.write_text(s,encoding='utf8')
    lines=target.read_text(encoding='utf8').splitlines()
    hits=[x for x in lines if ('emp' in x.lower() and any(k in x.lower() for k in ['general','emp_lord','emp_ch_lord','karl'])) or 'humanoid01.anim' in x.lower()]
    print(p.name, '\n'+'\n'.join(hits[:55]),flush=True)
packs=[GAME/n for n in ['variants.pack','variants2.pack','variants3.pack','variants4.pack','variants5.pack','anim.pack','anim2.pack','anim_3.pack','models.pack','models2.pack','models3.pack']]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(index,packs))
