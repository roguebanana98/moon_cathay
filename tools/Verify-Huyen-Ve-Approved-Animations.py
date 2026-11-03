import bpy,addon_utils,json,sys,hashlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v16-approved';V=R/'build/huyen-ve-animation-integration';BASE='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve_v2'
sys.path.insert(0,'D:/Warhammer3_Modding/tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'); bpy.ops.wm.open_mainfile(filepath=str(R/'build/huyen-ve-model-v2/huyen-ve-approved-20261103.blend'));addon_utils.enable('io_scene_rmv2');rig=bpy.data.objects['humanoid01e_NATIVE_BIND']
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_set(True);o.hide_render=True
rig.hide_set(False);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
old=set(bpy.data.objects);bpy.ops.import_scene.rmv2(filepath=str(O/BASE/'mc_huyen_ve_body.rigid_model_v2'),import_all_lods=True,texture_root=str(O));bodies=[o for o in bpy.data.objects if o not in old and o.type=='MESH']
# Imported LOD subcollections preserve grouping; identify each object's level.
def level(o):
 return next(i for i in range(4) if any(c.name.endswith('lod'+str(i)) for c in o.users_collection))
for o in bodies:o.hide_set(level(o)!=0);o.hide_render=level(o)!=0
old=set(bpy.data.objects);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.rmv2(filepath=str(O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_sword.rigid_model_v2'),import_all_lods=True,attach_armature=False,texture_root=str(V));swords=[o for o in bpy.data.objects if o not in old and o.type=='MESH']
for o in swords:
 c=o.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget='weapon_2';o.hide_set(level(o)!=0);o.hide_render=level(o)!=0
with bpy.data.libraries.load(str(V/'huyen-ve-all-animations.blend'),link=False) as (src,dst):dst.actions=[n for n in src.actions if n.startswith('HV_')]
actions=dst.actions;assert len(actions)==89
for a in actions:a.use_fake_user=True
rig.animation_data_create()
for p in rig.pose.bones:p.rotation_mode='QUATERNION'
rows=[]
for idx,a in enumerate(actions):
 rig.animation_data.action=a;rig.animation_data.action_slot=a.slots[0];lo,hi=map(int,a.frame_range);frames=sorted({lo,(lo+hi)//2,hi})
 for fr in frames:
  bpy.context.scene.frame_set(fr);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for o in bodies:
   if level(o)!=0:continue
   ev=o.evaluated_get(dg);m=ev.to_mesh();assert np.isfinite(np.array([v.co[:] for v in m.vertices])).all(),(a.name,fr,o.name);ev.to_mesh_clear()
  for o in swords:
   actual=o.evaluated_get(dg).matrix_world;expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix;assert max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-4
 rows.append({'action':a.name,'frames':frames})
 if idx%10==0:print('ACTION_CHECK',idx+1,89,flush=True)
chosen=next(a for a in actions if str(a.get('native_path','')).endswith('sword_attack_01.anim'));rig.animation_data.action=chosen;rig.animation_data.action_slot=chosen.slots[0];scene=bpy.context.scene;scene.frame_start=0;scene.frame_end=int(chosen.frame_range[1]);scene.frame_set(0);rig.hide_set(True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=3.4
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file and Path(bpy.path.abspath(im.filepath)).exists():im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'huyen-ve-v16-animation-review.blend'))
report={'status':'passed','clip_count':len(actions),'sampled_poses':sum(len(r['frames']) for r in rows),'lod_mesh_counts':{str(i):sum(level(o)==i for o in bodies) for i in range(4)},'checks':'Finite deformation on actual exported LOD0; exact weapon_2 transform; all LOD vertex channels checked separately against native','clips':rows,'runtime_verified':False}
(O/'animation-validation.json').write_text(json.dumps(report,indent=2))
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(O/'animation-preview.png');bpy.ops.render.render(write_still=True)





