import bpy,addon_utils
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
addon_utils.enable('io_scene_rmv2')
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'karl_mm_general_rig_test/Karl_MM_on_Empire_General_TEST.blend'))
scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['GENERAL_humanoid01__Karl_MM_TEST'];target=rig.matrix_world@rig.pose.bones['head'].head+Vector((0,0,-.10))
cam=scene.camera;cam.location=target+Vector((.5,-4,.15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.85
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.file_format='PNG';scene.cycles.samples=32
scene.render.filepath=str(R/'heinrich_portrait.png');bpy.ops.render.render(write_still=True)
