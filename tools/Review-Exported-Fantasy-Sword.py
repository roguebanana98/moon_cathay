"""Reimport the actual RMV2/DDS and verify attachment through native animations."""
import bpy,addon_utils,sys,json
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-fantasy-longsword'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-fantasy-sword-preview.blend'));addon_utils.enable('io_scene_rmv2')
rig=bpy.data.objects['humanoid01e_NATIVE_BIND'];bpy.data.objects['HuyenVe_Fantasy_Longsword_PREVIEW'].hide_render=True;bpy.data.objects['HuyenVe_Fantasy_Longsword_PREVIEW'].hide_set(True)
before=set(bpy.data.objects);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.rmv2(filepath=str(O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_sword.rigid_model_v2'),import_all_lods=True,attach_armature=False,texture_root=str(O))
swords=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(swords)==4
for o in swords:
 assert len(o.vertex_groups)==0 and not o.constraints and not o.parent
 c=o.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget='weapon_2'
 level=o.users_collection[0].rmv2.lod_level
 o['preview_lod']=level;o.hide_set(level!=0);o.hide_render=level!=0
rows=[];rig.animation_data_create()
for tag,token in [('stand','/stand/hu1e_dlc24_yuan_bo_sword_stand_01.anim'),('run','sword_run'),('attack','sword_attack_01.anim'),('cast','cast')]:
 choices=[a for a in bpy.data.actions if token in str(a.get('native_path',''))];assert choices,tag
 action=choices[0];rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
 lo,hi=map(int,action.frame_range)
 for frame in sorted({lo,(lo+hi)//2,hi}):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix
  for obj in swords:
   ev=obj.evaluated_get(dg);actual=ev.matrix_world
   err=max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4));assert err<1e-5
   points=np.array([tuple(actual@v.co) for v in obj.data.vertices]);assert np.isfinite(points).all()
  rows.append(dict(clip=tag,frame=frame,all_four_lods_follow_weapon_2=True))
stand=next(a for a in bpy.data.actions if '/stand/hu1e_dlc24_yuan_bo_sword_stand_01.anim' in str(a.get('native_path','')))
rig.animation_data.action=stand;rig.animation_data.action_slot=stand.slots[0];scene=bpy.context.scene;scene.frame_set(0)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.filepath=str(O/'exported-sword-review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'huyen-ve-fantasy-sword-exported-review.blend'))
(O/'exported-animation-validation.json').write_text(json.dumps(dict(status='passed',sampled_poses=len(rows),exported_lods=4,checks=rows,no_double_attachment=True,game_runtime_verified=False),indent=2))
bpy.ops.render.render(write_still=True)
