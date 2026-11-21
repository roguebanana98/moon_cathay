"""Inspect the local campaign candidate without modifying its inputs."""
import importlib.util,json,lzma,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('b',R/'tools/Build-Province-Candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
P=R/'reference/local/edh-faction-base/campaigns/cr_combi_expanded/startpos.esf'
d=b.Document(P.read_bytes());root,_=d.decode(16)
c=next(n for n in b.walk(root) if n['name']=='COMPRESSED_DATA');payload,info=c['groups'][0][:2];length,props=info['groups'][0][:2]
raw=lzma.decompress(props+struct.pack('<Q',length)+payload,format=lzma.FORMAT_ALONE)
O=R/'build/east-sea-faction';O.mkdir(parents=True,exist_ok=True);(O/'base.raw.esf').write_bytes(raw)
d=b.Document(raw);root,_=d.decode(16)
def skim(n):
 return {'name':n['name'],'offset':n['offset'],'groups':[[({'name':v['name'],'offset':v['offset']} if isinstance(v,dict) and 'name' in v else v) for v in g] for g in n['groups']]}
selected=[]
for n in b.walk(root):
 g=n['groups'][0] if n['groups'] else []
 if n['name']=='FACTION' and any(k in g for k in ['mixer_emp_vaults_gigasdongo','cr_cth_agents_of_the_moon','cr_emp_guests_of_the_raja']):
  selected.append(skim(n))
  selected.extend(skim(v) for v in g if isinstance(v,dict) and 'groups' in v)
 elif n['name'] in ['REGION','CAMPAIGN_PLAYER_SETUP','CAMPAIGN_PLAYER_SETUP_INGAME_MODIFIABLES'] and any(k in g for k in ['mixer_emp_vaults_gigasdongo','cr_combi_region_dai_loa','cr_combi_region_preenn']):selected.append(skim(n))
(O/'inspection.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
print('Wrote inspection:',len(selected),'records',len(raw),'bytes')
