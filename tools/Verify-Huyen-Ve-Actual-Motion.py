"""Regression check: prove mesh motion across frames, not just finite positions."""
import bpy,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v16-approved';rows=[]
for tag,path,rig_name,body_name in [('v15',R/'build/huyen-ve-animation-integration/huyen-ve-all-animations.blend','humanoid01e_HuyenVe','mc_huyen_ve_body_lod0'),('v16',O/'huyen-ve-v16-animation-review.blend','humanoid01e_NATIVE_BIND','face_lod0')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));rig=bpy.data.objects[rig_name];body=bpy.data.objects[body_name];assert rig.data.pose_position=='POSE';rig.animation_data_create()
 for token in ['sword_run','sword_attack_01','sword_stand']:
  choices=[a for a in bpy.data.actions if token in str(a.get('native_path',''))];assert choices,(tag,token)
  action=choices[0];rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0];start,end=map(int,action.frame_range);frames=sorted({start,start+(end-start)//3,start+2*(end-start)//3,end});samples=[]
  for frame in frames:
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dg);mesh=ev.to_mesh();inv=(rig.matrix_world@rig.pose.bones['root'].matrix).inverted();points=np.array([tuple(inv@(body.matrix_world@v.co)) for v in mesh.vertices]);samples.append(points);ev.to_mesh_clear()
  maximum=max(float(np.linalg.norm(p-samples[0],axis=1).max()) for p in samples[1:]);assert maximum>.0005,(tag,token,maximum)
  rows.append({'version':tag,'native_clip':action.get('native_path'),'frames':frames,'root_relative_max_vertex_motion':maximum,'mesh':body.name})
(O/'actual-motion-regression.json').write_text(json.dumps({'status':'passed','checks':rows,'scope':'Actual evaluated mesh changes across frames in Blender; engine lookup tested separately, not an in-game run'},indent=2));print(json.dumps(rows,indent=2))
