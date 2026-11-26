"""Extract selected native sword/handbow clips for a private Blender test."""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/khainite-weapons';O=R/'build/moonshadow-animation-preview';O.mkdir(parents=True,exist_ok=True)
B='animations/battle/humanoid01d/sword_and_handbow/'
clips=[('01 Stand','stand/hu1d_def_swha_stand_01.anim'),
       ('02 Walk','locomotion/hu1d_swha_walk_01.anim'),
       ('03 Run','locomotion/hu1d_swha_run_01.anim'),
       ('04 Dagger attack 1','attacks/hu1d_swha_attack_01.anim'),
       ('05 Dagger attack 3','attacks/hu1d_swha_attack_03.anim'),
       ('06 Jump attack','attacks/hu1d_swha_jumping_attack_01.anim'),
       ('07 Aim handbow','missile_actions/hu1d_def_swha_aim_level_03.anim'),
       ('08 Fire handbow','missile_actions/hu1d_def_swha_shoot_level_03.anim')]
paths=[B+p for label,p in clips]
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f']+[p+';'+str(D) for p in paths],check=True)
(O/'clips.json').write_text(json.dumps([dict(label=label,path=B+p) for label,p in clips],indent=2))
print('Ready: eight native clips')
