"""Resize the approved user portrait and build a graphics-only revision over r4."""
import ast,hashlib,io,json,shutil,struct,subprocess
from pathlib import Path
from PIL import Image,ImageOps
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v25-quest-chain'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
A=R/'assets/authored/da-lien/portraits';A.mkdir(parents=True,exist_ok=True)
source=Path('D:/Temp/Temp/codex-clipboard-0ed45689-6753-448e-8dfb-5885ad90cf00.png')
original=A/'Da_Lien_user_portrait.png'
if not original.exists():shutil.copy2(source,original)
assert original.read_bytes()==source.read_bytes()
im=Image.open(original).convert('RGBA');assert im.size==(593,1280)
outputs={}
def save(p,img):
 dest=A/p;dest.parent.mkdir(parents=True,exist_ok=True);img.save(dest)
 outputs[p]={'size':list(img.size),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
# Full-height unit card preserves the supplied composition without distortion.
card=ImageOps.fit(im,(60,130),method=Image.Resampling.LANCZOS)
save('ui/portraits/units/no_culture/mc_da_lien_0.png',card)
save('ui/units/icons/mc_da_lien.png',card)
# Leader slot is wider: crop to the head and upper neck, keeping the face intact.
leader=im.crop((0,15,593,817)).resize((85,115),Image.Resampling.LANCZOS)
save('ui/portraits/faction_leaders/mc_da_lien_0.png',leader)
# Native porthole is a wide 300x164 canvas, not a stretched vertical photograph.
# Centre the head in its circular UI viewport; side fill matches the source background.
port=Image.new('RGBA',(300,164),im.getpixel((0,0)))
head=im.crop((0,0,593,900)).resize((108,164),Image.Resampling.LANCZOS)
port.alpha_composite(head,(96,0))
save('ui/portraits/portholes/no_culture/mc_da_lien_0.png',port)
save('ui/units/minspec_portholes/mc_da_lien_human.png',port)
manifest={'source':str(original.relative_to(R)),'original_size':list(im.size),'outputs':outputs,'method':'Lanczos; full unit card, head/neck leader crop, centred head on native porthole canvas; no generated pixels or face retouch.'}
(A/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
preview=Image.new('RGB',(600,310),(30,25,28))
preview.paste(card.resize((120,260),Image.Resampling.NEAREST),(10,10))
preview.paste(leader.resize((170,230),Image.Resampling.NEAREST),(145,10))
preview.paste(port,(300,130))
preview.save(O/'da-lien-portrait-preview.png')
base=O/'mc_huyen_ve_v25_quest_chain_test_r4.pack';pack=O/'mc_huyen_ve_v25_quest_chain_test_r5.pack'
assert not pack.exists();shutil.copy2(base,pack)
for p in outputs:
 subprocess.run([C['rpfm'],'-g','warhammer_3','pack','add','-p',str(pack),'-f',str(A/p)+';'+p],check=True,stdout=subprocess.DEVNULL)
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'reader','exec'))
before=unpack(base);after=unpack(pack)
assert before.keys()==after.keys()
assert set(p for p in before if before[p]!=after[p])==set(outputs)
for p,info in outputs.items():
 assert after[p]==(A/p).read_bytes()
 decoded=Image.open(io.BytesIO(after[p]));assert decoded.mode=='RGBA' and list(decoded.size)==info['size'];decoded.verify()
validation=json.loads((O/'pack-validation.json').read_text());assert validation['pack']==str(base)
validation.update(pack=str(pack),base=str(base),sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),files=list(outputs),deployed=False,runtime_verified=False,portrait_only=True)
(O/'pack-validation.json').write_text(json.dumps(validation,indent=2))
report={'status':'passed','source_preserved':True,'pack':str(pack),'changed_payloads':list(outputs),'all_other_payloads_byte_identical':True,'outputs':outputs,'runtime_verified':False}
(O/'portrait-validation-r5.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
