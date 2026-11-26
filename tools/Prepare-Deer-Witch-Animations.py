import csv,json,subprocess
from pathlib import Path
R=Path.cwd();C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/deer-miao-witch-preview';D=R/'reference/local/witch-elves'
with (O/'db/land_units_tables/data__.tsv').open(encoding='utf-8-sig') as f:
 rows=csv.DictReader((l for l in f if not l.startswith('#')),delimiter='\t')
 for row in rows:
  if 'witch_elve' in row.get('key',''): print({k:v for k,v in row.items() if k in ['key','man_animation','battle_entity']})
B='animations/battle/humanoid01b/subset/elves/dual_sword/'
clips=[('01 Stand','stand/hu1b_elf_ds_stand_01.anim'),('02 Walk','locomotion/hu1b_elf_ds_walk_01.anim'),('03 Run','locomotion/hu1b_elf_ds_run_01.anim'),('04 Attack 1','attacks/hu1b_elf_ds_attack_01.anim'),('05 Attack 3','attacks/hu1b_elf_ds_attack_03.anim'),('06 Jump attack','attacks/hu1b_elf_ds_jumping_attack_01.anim')]
paths=[B+p for l,p in clips]+['animations/skeletons/humanoid01b.anim','animations/battle/humanoid01b/hands/hu1b_hand_pose_grip.anim']
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f']+[p+';'+str(D) for p in paths],check=True,stdout=subprocess.DEVNULL)
(O/'clips.json').write_text(json.dumps([dict(label=l,path=B+p) for l,p in clips],indent=2))
