import bpy,addon_utils,sys,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-v8-appearance';D=R/'reference/local/celestial-concubines'
bpy.ops.wm.open_mainfile(filepath=str(O/'engine-da-anh.blend'));rig=bpy.data.objects['Da Anh | Native humanoid01e'];sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
body=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get()];assert len(body)==9
clips=['animations/battle/humanoid01e/gatemaster_sword_and_shield/campaign/cam_hu1e_gatemaster_stand_01.anim','animations/battle/humanoid01e/gatemaster_sword_and_shield/campaign/cam_hu1e_gatemaster_run_02.anim'];results=[]
for path in clips:
 bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 imported,stats,warnings=import_anim.import_file(bpy.context,str(D/path),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert imported==rig
 a,b=map(int,rig.animation_data.action.frame_range);pts=[]
 for f in sorted({a,(a+b)//2,b}):
  bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();row=[]
  for ob in body:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.asarray([tuple(v.co) for v in me.vertices]);assert np.isfinite(p).all();row.append(p);ev.to_mesh_clear()
  pts.append(np.concatenate(row))
 motion=max(float(np.linalg.norm(p-pts[0],axis=1).max()) for p in pts[1:]);assert motion>1e-5;results.append(dict(clip=path,motion=motion,warnings=warnings))
(O/'campaign-animation-check.json').write_text(json.dumps(dict(status='passed',sampled_poses=6,results=results,runtime_verified=False),indent=2));print('CAMPAIGN_POSES_PASSED')
