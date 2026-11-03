import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-rigged-prototype.blend'));rig=bpy.data.objects['humanoid01e_HuyenVe'];rig.animation_data.action=bpy.data.actions['QA_attack'];bpy.context.scene.frame_set(20);bpy.context.view_layer.update();inv=rig.pose.bones['weapon_2'].matrix.inverted()
r={p.name:{'head':list(inv@p.head),'tail':list(inv@p.tail)} for p in rig.pose.bones if p.name.startswith(('hand','thumb','finger'))}
(O/'finger-points.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
