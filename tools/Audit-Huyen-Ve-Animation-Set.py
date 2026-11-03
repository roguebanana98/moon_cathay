"""Resolve the native donor animation graph against the installed pack indexes."""
import json,re,subprocess,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
REF=R/'reference/local/yuan-bo-model';EXTRA=R/'reference/local/huyen-ve-animation-integration';OUT=R/'build/huyen-ve-animation-integration';OUT.mkdir(parents=True,exist_ok=True)
indexes={name:{line.strip().replace('\\','/') for line in (REF/filename).read_text(encoding='utf-8-sig').splitlines() if line.startswith(('animation/','animations/'))} for name,filename in [('anim.pack','anim-index.txt'),('anim2.pack','anim2-index.txt'),('anim_3.pack','anim_3-index.txt'),('data.pack','data-index.txt')]}
def locations(path):return [name for name,paths in indexes.items() if path in paths]
table=json.loads((REF/'animations/database/battle/tables/hu1e_dlc24_yuan_bo_dragon_jade.txt').read_text())
fragments={};slots={};references=set()
for entry in table['Entries']:
 assert entry['Type']=='Fragment',entry
 internal='animations/database/battle/fragments/'+entry['Value']+'.txt';references.add(internal)
 data=json.loads((REF/internal).read_text());assert data['Properties']['SkeletonName']=='humanoid01e'
 fragments[entry['Value']]={'slots':len(data['SlotData']),'path':internal}
 for slot,value in data['SlotData'].items():
  if value['Config'].get('Ignore'):continue
  slots[slot]={'fragment':entry['Value'],**value}
  for choice in value['Entries'].values():
   references.add(choice['animation']);references.update(p for p in choice.get('metadata',[]) if p)
campaign='animations/campaign/database/bin/cam_lord_hu1e_dlc24_yuan_bo_dragon_jade.bin'
blob=(EXTRA/campaign).read_bytes();campaign_refs=sorted(set(m.group().decode('ascii') for m in re.finditer(rb'animations/[A-Za-z0-9_./{}-]+?\.(?:anim|meta)(?![a-z])',blob)))
# Length-prefixed strings can be immediately followed by an ASCII byte. Match
# the format suffix itself, rather than relying on a NUL terminator.
campaign_refs=sorted(set(m.group().decode('ascii') for m in re.finditer(rb'animations/[A-Za-z0-9_./{}-]+?\.(?:anim|meta)',blob)))
references.update(campaign_refs);references.add(campaign)
clips=sorted(p for p in references if p.endswith('.anim'))
missing=[p for p in references if not locations(p)];assert not [p for p in missing if not p.endswith('.meta')],missing
manifest={'status':'native_core_dependencies_resolved','native_metadata_not_found_in_direct_pack_indexes':sorted(missing),'skeleton':'humanoid01e','native_battle_table':'hu1e_dlc24_yuan_bo_dragon_jade',
 'table':table,'fragments':fragments,'effective_slots':slots,'effective_slot_count':len(slots),'unique_clips':clips,'clip_count':len(clips),
 'campaign_table':campaign,'campaign_references':campaign_refs,'references':{p:locations(p) for p in sorted(references)},
 'scope':'References resolve in installed native packs; no gameplay runtime or visual-quality claim'}
(OUT/'animation-set-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for pack,paths in indexes.items():
 needed=[p for p in clips if pack==locations(p)[-1] and not (REF/p).is_file()]
 for start in range(0,len(needed),40):
  batch=needed[start:start+40];args=[C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data'/pack)]
  for p in batch:args += ['-f',p+';'+str(REF)]
  result=subprocess.run(args,capture_output=True,text=True)
  if result.returncode:raise RuntimeError(result.stdout+result.stderr)
for p in clips:assert (REF/p).is_file(),p
manifest['clip_hashes']={p:hashlib.sha256((REF/p).read_bytes()).hexdigest() for p in clips}
(OUT/'animation-set-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'slots':len(slots),'clips':len(clips),'fragments':fragments,'references':len(references),'campaign_refs':len(campaign_refs),'native_metadata_not_found_in_direct_pack_indexes':len(missing)},indent=2))
