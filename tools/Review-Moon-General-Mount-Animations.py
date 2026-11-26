"""Exercise shipped rider geometry against compiled native mounted profiles."""
import bpy,addon_utils,json,sys,subprocess
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v21-mounts';D=R/'reference/local/moon-general-mounts'
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
spec=json.loads((O/'mount-models.json').read_text());grips=json.loads((R/'build/moon-generals-preview/animation-review-clips.json').read_text())['grips'];clipset=sorted(set(p for m in spec['models'] for p in m['clips']))
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f',*[p+';'+str(D) for p in clipset]],check=True,stdout=subprocess.DEVNULL)
checks=[];(O/'renders').mkdir(exist_ok=True)
for m in spec['models']:
 s=m['subtype'];label='Assault' if 'assault' in s else 'Bastion';bpy.ops.wm.open_mainfile(filepath=str(R/'build/moon-generals-v20'/(s+'-roundtrip.blend')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.hide_set(False);meshes=[o for o in bpy.data.objects if o.type=='MESH'];props=[o for o in meshes if any(c.type=='COPY_TRANSFORMS' and c.target==rig for c in o.constraints)]
 assert props
 for ob in props:
  for con in ob.constraints:
   if con.type=='COPY_TRANSFORMS' and con.target==rig:con.subtarget=m['attachment']
 for clip in m['clips']:
  rig.animation_data_clear()
  for b in rig.pose.bones:b.matrix_basis.identity()
  bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
  import_anim.import_file(bpy.context,str(R/'reference/local/wwd-all-lords'/grips[label]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
  _,_,warnings=import_anim.import_file(bpy.context,str(D/clip),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert not warnings,warnings
  first,last=map(int,rig.animation_data.action.frame_range);positions=[];distances=[]
  for frame in sorted({first,(first+last)//2,last}):
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
   for ob in meshes:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.array([tuple(ev.matrix_world@v.co) for v in me.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all() and abs(p).max()<40;points.append(p)
   positions.append(np.concatenate(points))
   # Shaft runs along prop-local X. This detects large attachment errors.
   axis=(rig.matrix_world@rig.pose.bones[m['attachment']].matrix).inverted();hands=[axis@(rig.matrix_world@b.matrix.translation) for b in rig.pose.bones if b.name.lower() in ['bn_l_hand','bn_r_hand','hand_l','hand_r']]
   if hands:distances.append(min(float((p.y*p.y+p.z*p.z)**.5) for p in hands))
  delta=max(float(np.max(abs(p-positions[0]))) for p in positions[1:]);assert delta>1e-6,(m['unit'],clip)
  checks.append(dict(unit=m['unit'],clip=clip,samples=len(positions),motion=delta,minimum_hand_axis_distances=distances))
 # Restore true idle and render rider/weapon for visual attachment inspection.
 rig.animation_data_clear()
 for b in rig.pose.bones:b.matrix_basis.identity()
 import_anim.import_file(bpy.context,str(R/'reference/local/wwd-all-lords'/grips[label]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
 import_anim.import_file(bpy.context,str(D/m['clips'][0]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
 scene=bpy.context.scene;scene.frame_set(1);scene.render.resolution_x=640;scene.render.resolution_y=640;cam=scene.camera;cam.data.ortho_scale=4.0;cam.location=(3,-6,3.3);cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/'renders'/(m['unit']+'.png'));bpy.ops.render.render(write_still=True)
report=dict(status='passed',models=len(spec['models']),samples=sum(c['samples'] for c in checks),checks=checks,game_runtime_verified=False,mount_body_fit_runtime_verified=False)
(O/'animation-review.json').write_text(json.dumps(report,indent=2));print('MOUNT_ANIMATION_CHECK_PASSED',report['samples'],flush=True)
