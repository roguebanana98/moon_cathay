import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-animation-integration'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-all-animations.blend'));rig=bpy.data.objects['humanoid01e_HuyenVe'];rows={}
for name in ['QA_attack','HV_026_ATTACK_1']:
 rig.animation_data.action=None
 for p in rig.pose.bones:p.matrix_basis.identity()
 a=bpy.data.actions[name];rig.animation_data.action=a;rig.animation_data.action_slot=a.slots[0]
 bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
 rows[name]={'bones':{p.name:[list(r) for r in p.matrix] for p in rig.pose.bones},'slots':[(s.identifier,s.target_id_type) for s in a.slots]}
diff={name:max(abs(rows['QA_attack']['bones'][name][i][j]-rows['HV_026_ATTACK_1']['bones'][name][i][j]) for i in range(4) for j in range(4)) for name in rows['QA_attack']['bones']}
print(json.dumps({'max_delta':max(diff.values()),'nonmatching_bones':{k:v for k,v in diff.items() if v>1e-5},'slots':{k:v['slots'] for k,v in rows.items()}},indent=2))
(O/'action-state-comparison.json').write_text(json.dumps({'max_delta':max(diff.values()),'bone_deltas':diff},indent=2))
