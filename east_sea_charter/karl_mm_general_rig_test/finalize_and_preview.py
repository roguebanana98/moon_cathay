import bpy,json,addon_utils
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;addon_utils.enable('io_scene_rmv2')
bpy.ops.wm.open_mainfile(filepath=str(R/'Karl_MM_on_Empire_General_TEST.blend'))
scene=bpy.context.scene;scene.frame_set(1)
for im in bpy.data.images:
    if im.source=='FILE':im.pack()
cam=scene.camera;target=Vector((.10,.11,.87));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.55
rig=bpy.data.objects['GENERAL_humanoid01__Karl_MM_TEST'];rig.data.display_type='STICK'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.region_3d.view_location=target;s.region_3d.view_distance=3.1
            s.region_3d.view_rotation=cam.rotation_euler.to_quaternion();s.overlay.show_overlays=False
            s.shading.type='MATERIAL';s.shading.studiolight_rotate_z=.6
        elif area.type=='DOPESHEET_EDITOR' and area.ui_type=='TIMELINE' and screen==bpy.context.window.screen:
            # Fit the complete, labelled playlist in the saved timeline view.
            with bpy.context.temp_override(window=bpy.context.window,area=area,region=next(r for r in area.regions if r.type=='WINDOW')):
                try:bpy.ops.action.view_all()
                except RuntimeError:pass
report=json.loads((R/'test_report.json').read_text());report['textures_packed']=len([im for im in bpy.data.images if im.packed_file])
(R/'test_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Karl_MM_on_Empire_General_TEST.blend'))
for frame,name in [(1,'preview_idle.png'),(186,'preview_attack.png')]:
    scene.frame_set(frame);scene.render.filepath=str(R/name);bpy.ops.render.render(write_still=True)
print('FINALIZED',report['textures_packed'],'packed images')
