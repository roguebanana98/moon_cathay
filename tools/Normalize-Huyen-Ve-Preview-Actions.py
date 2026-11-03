import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-animation-integration';sys.path.insert(0,str(R/'tools'))
from HuyenVeAnimationPreview import complete_preview_channels
path=O/'huyen-ve-all-animations.blend';bpy.ops.wm.open_mainfile(filepath=str(path));rig=bpy.data.objects['humanoid01e_HuyenVe'];counts={}
for action in bpy.data.actions:
 if action.name.startswith('HV_'):counts[action.name]=complete_preview_channels(action,rig)
rig.animation_data.action=bpy.data.actions['HV_026_ATTACK_1'];rig.animation_data.action_slot=rig.animation_data.action.slots[0];bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(path))
report=json.loads((O/'scene-integration-report.json').read_text());report['standalone_preview_identity_channels_added']=counts
(O/'scene-integration-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PREVIEW_CHANNELS',sum(counts.values()))
