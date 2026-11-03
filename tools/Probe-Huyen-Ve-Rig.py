import bpy, addon_utils, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
REF=R/'reference/local/yuan-bo-model'
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
bpy.ops.import_scene.tw_anim(filepath=str(REF/'animations/skeletons/humanoid01e.anim'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
bpy.ops.import_scene.rmv2(filepath=str(REF/'variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.rigid_model_v2'),build_materials=False)
data={'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in rig.data.bones], 'meshes':[{'name':o.name,'bounds':[[min((o.matrix_world@__import__('mathutils').Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((o.matrix_world@__import__('mathutils').Vector(v))[i] for v in o.bound_box) for i in range(3)]],'groups':[g.name for g in o.vertex_groups]} for o in bpy.data.objects if o.type=='MESH']}
(R/'reports/huyen-ve-rig-probe.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.import_scene.tw_anim(filepath=str(REF/'animations/battle/humanoid01e/yuan_bo_human/stand/hu1e_dlc24_yuan_bo_sword_stand_01.anim'))
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
for name in ['weapon_2','hand_left','hand_right','finger_index_left_0','finger_index_right_0','finger_ring_left_0','finger_ring_right_0']:
    pb=rig.pose.bones[name];local=rig.pose.bones['weapon_2'].matrix.inverted()@pb.head
    print('GRIP',name,list(pb.head),'in_weapon',list(local))
deform=rig.pose.bones['weapon_2'].matrix@rig.data.bones['weapon_2'].matrix_local.inverted()
for name in ['hand_right','finger_index_right_0','finger_ring_right_0','thumb_right_1']:
 print('PROP_SPACE',name,list(deform.inverted()@rig.pose.bones[name].head))
from io_scene_rmv2 import skeleton
bone=rig.data.bones['weapon_2'];fix=skeleton.bone_fix_quaternion(bone).to_matrix().to_4x4()
correct=rig.pose.bones['weapon_2'].matrix@fix.inverted()
print('WEAPON_BIND',list(bone.matrix_local@fix.inverted()))
for name in ['hand_right','finger_index_right_0','finger_ring_right_0','thumb_right_1']:
 print('ACTUAL_PROP_LOCAL',name,list(correct.inverted()@rig.pose.bones[name].head))
