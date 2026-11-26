"""Read-only extraction of native animations actually assigned to both generals."""
from pathlib import Path
ns={'__file__':str(Path(__file__).with_name('Prepare-WWD-All-Lords.py'))}
exec(Path(ns['__file__']).read_text(encoding='utf8').split('def read(t):')[0],ns)
globals().update(ns)
O=R/'build/moon-generals-preview'
allclips=json.loads((O/'all-native-clips.json').read_text(encoding='utf8'))
names={
 'Assault': ['hu1b_elf_sp_wd_stand_01','hu1b_elf_sp_wd_walk_01','hu1b_elf_sp_wd_run_01','hu1b_elf_sp_wd_charge_01','hu1b_elf_sp_attack_07','hu1b_elf_sp_attack_08','hu1b_elf_sp_jumping_attack_03','hu1b_sp_wd_defend_front_01'],
 'Bastion': ['hu1e_celestial_general_stand_01','hu1e_celestial_general_walk_01','hu1e_celestial_general_combat_run_01','hu1e_celestial_general_charge_01','hu1e_celestial_general_attack_01','hu1e_celestial_general_attack_02','hu1e_celestial_general_jump_attack_01','hu1e_celestial_general_defend_front_01']}
labels=['Idle','Walk','Run','Charge','Attack A','Attack B','Jump attack','Defend']
out={}
for model,stems in names.items():
    out[model]=[]
    for label,stem in zip(labels,stems):
        hits=[p for p in allclips[model] if Path(p).stem==stem]
        assert len(hits)==1,(model,stem,hits)
        out[model].append(dict(label=label,path=hits[0]))
grips={'Assault':'animations/battle/humanoid01b/hands/hu1b_hand_pose_grip.anim',
       'Bastion':'animations/battle/humanoid01e/sword_and_bow/hands/hu1e_hand_pose_grip.anim'}
resolve([x['path'] for clips in out.values() for x in clips]+list(grips.values()),'animation')
assert not missing,missing
(O/'animation-review-clips.json').write_text(json.dumps(dict(clips=out,grips=grips),indent=2),encoding='utf8')
print('NATIVE_REVIEW_CLIPS_READY',sum(map(len,out.values())),flush=True)
