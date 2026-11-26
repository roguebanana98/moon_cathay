"""Read-only extraction of real native flight/landing/sword clips for review."""
import json
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/divine-wing-guard-animation';O.mkdir(parents=True,exist_ok=True)
D=R/'reference/local/divine-wing-guard'
M=json.loads((R/'build/divine-wing-guard-preview/asset-manifest.json').read_text())
game=Path(M['game'])/'data';pack=game/'anim2.pack'
ix=json.loads((D/'indexes/anim2.json').read_text())['paths']
base='animations/battle/humanoid16c/'
clips=[
 dict(label='01 TAKE OFF',path=base+'transitions/hu16c_sps_take_off_01.anim',rig='humanoid16c',mode='takeoff'),
 dict(label='02 FLIGHT',path=base+'locomotion/hu16c_sps_fly_01.anim',rig='humanoid16c',mode='loop',duration=120),
 dict(label='03 HOVER',path=base+'stand/hu16c_sps_fly_stand_01.anim',rig='humanoid16c',mode='loop',duration=90),
 dict(label='04 AIR ATTACK',path=base+'attacks/hu16c_sps_fly_attack_01.anim',rig='humanoid16c',mode='airattack'),
 dict(label='05 LANDING',path=base+'transitions/hu16c_sps_fly_charge_land_01.anim',rig='humanoid16c',mode='landing'),
 dict(label='06 GROUND STAND',path='animations/battle/humanoid01e/sword_shield/stand/hu1e_sword_and_shield_stand_01.anim',rig='humanoid01e',mode='loop',duration=60),
 dict(label='07 SWORD ATTACK A',path='animations/battle/humanoid01e/sword_shield/attack/hu1e_sword_shield_attack_01.anim',rig='humanoid01e',mode='groundattack'),
 dict(label='08 SWORD ATTACK B',path='animations/battle/humanoid01e/sword_shield/attack/hu1e_sword_shield_attack_02.anim',rig='humanoid01e',mode='groundattack'),
]
ground=base+'stand/hu16c_sps_stand_01.anim'
needed=sorted({c['path'] for c in clips}|{ground})
assert all(p in ix for p in needed)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(pack),'-f',
                *[ix[p]+';'+str(D) for p in needed]],check=True)
spec=dict(clips=clips,ground_wing_pose=ground,source_pack=str(pack),preview_only=True)
(O/'clips.json').write_text(json.dumps(spec,indent=2))
print('NATIVE_REVIEW_CLIPS_READY',len(clips),flush=True)
