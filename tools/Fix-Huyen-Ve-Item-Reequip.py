"""Match native unique-item equip flags without widening subtype access."""
import csv,json,shutil,subprocess,hashlib,ast,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v18-item-reequip';O.mkdir(exist_ok=True);C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));base=R/'build/huyen-ve-v17-campaign/mc_huyen_ve_v17_campaign_test.pack';dest=O/'mc_huyen_ve_v18_item_reequip.pack';assert not dest.exists()
internal='db/ancillaries_tables/mc_huyen_ve_equipment';source=R/'reference/local/huyen-ve-v17-check'/(internal+'.tsv')
with source.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,delimiter='\t'))
original=[r.copy() for r in rows];head=rows[0]
for r in rows[2:]:
 for field in ['unique_to_world','unique_to_faction']:assert r[head.index(field)]=='true';r[head.index(field)]='false'
 assert r[head.index('transferrable')]=='false'
p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',quoting=csv.QUOTE_NONE,lineterminator='\n').writerows(rows)
shutil.copy2(base,dest)
def run(args):subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
run([C['rpfm'],'-g','warhammer_3','pack','add','-p',dest,'-t',C['schema'],'-f',str(p)+';'+internal])
t=ast.parse((R/'tools/Validate-Repaired-Province-Packs.py').read_text());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='unpack');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pack>','exec'));before=unpack(base);after=unpack(dest);assert before.keys()==after.keys();assert [p for p in before if before[p]!=after[p]]==[internal]
verify=R/'reference/local/huyen-ve-v18-check';verify.mkdir(exist_ok=True);run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',dest,'-t',C['schema'],'-f',internal+';'+str(verify)])
with (verify/(internal+'.tsv')).open(encoding='utf-8-sig',newline='') as f:actual=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
assert actual[0]==head and actual[2:]==rows[2:]
for old,new in zip(original[2:],actual[2:]):assert {k for k,a,b in zip(head,old,new) if a!=b}=={'unique_to_world','unique_to_faction'}
report={'status':'static_checks_passed','pack':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'base':str(base),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changed_payloads':[internal],'changed_fields':['unique_to_world','unique_to_faction'],'new_values':'false, matching vanilla Yuan Bo quest item donor','items':len(rows)-2,'transferrable_unchanged':False,'subtype_whitelist_unchanged':True,'grant_script_and_saved_duplicate_guards_unchanged':True,'runtime_reequip_confirmed':False,'deployed':False};(O/'pack-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
