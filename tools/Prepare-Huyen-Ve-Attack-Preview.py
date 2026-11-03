"""Save the corrected packed scene with the attack clip ready to play."""
import bpy,shutil,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
path=O/'huyen-ve-rigged-prototype.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene;rig=bpy.data.objects['humanoid01e_HuyenVe'];rig.animation_data.action=bpy.data.actions['QA_attack']
scene.frame_start=0;scene.frame_end=62;scene.render.fps=30;scene.frame_set(20);bpy.context.view_layer.update()
body=bpy.data.objects['mc_huyen_ve_body_lod0'];de=body.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[de.matrix_world@Vector(p) for p in de.bound_box]
center=Vector([sum(p[i] for p in pts)/len(pts) for i in range(3)])
orientation=(Vector((0,0,0))-Vector((2,-5,1.8))).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False
   space.lock_object=rig;space.lock_bone='root'
   space.region_3d.view_location=(0,0,0);space.region_3d.view_rotation=orientation;space.region_3d.view_distance=3.6
bpy.ops.wm.save_as_mainfile(filepath=str(path))
shutil.copy2(path,O/'huyen-ve-sword-grip-fixed.blend')
print('Attack preview saved; clip QA_attack, frames 0-62, initial pose 20')
