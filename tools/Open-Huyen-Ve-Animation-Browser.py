"""Live Blender UI setup: native Action Editor plus automatic preview range."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-animation-integration'
rig=bpy.data.objects.get('humanoid01e_HuyenVe');assert rig is not None
actions=[a for a in bpy.data.actions if a.name.startswith('HV_')];assert len(actions)==89
if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_cancel(restore_frame=False)
bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
for area in bpy.context.screen.areas:
    if area.type=='CONSOLE':area.type='VIEW_3D'
    if area.type=='DOPESHEET_EDITOR':
        area.ui_type='DOPESHEET';space=area.spaces.active;space.mode='ACTION';space.show_region_ui=False
        space.dopesheet.show_only_selected=False
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.shading.type='MATERIAL';space.show_region_ui=False;space.overlay.show_overlays=False;space.show_gizmo=False
        space.lock_object=rig;space.lock_bone='root';space.region_3d.view_location=(0,0,0);space.region_3d.view_distance=3.6
for handler in list(bpy.app.handlers.depsgraph_update_post):
    if getattr(handler,'_huyen_ve_action_browser',False):bpy.app.handlers.depsgraph_update_post.remove(handler)
state={'action':None}
def update_preview_range(scene,depsgraph=None):
    action=rig.animation_data.action
    if not action or not action.name.startswith('HV_'):return
    if state['action']==action.as_pointer():return
    state['action']=action.as_pointer()
    if len(action.slots):rig.animation_data.action_slot=action.slots[0]
    start,end=map(int,action.frame_range);scene.frame_start=start;scene.frame_end=max(start+1,end)
    fps=float(action.get('native_fps',30));scene.render.fps=max(1,round(fps));scene.render.fps_base=scene.render.fps/fps
    scene.frame_set(start)
    for area in bpy.context.screen.areas:
        if area.type=='DOPESHEET_EDITOR':
            region=next((r for r in area.regions if r.type=='WINDOW'),None)
            if region:
                with bpy.context.temp_override(area=area,region=region):bpy.ops.action.view_all()
update_preview_range._huyen_ve_action_browser=True
bpy.app.handlers.depsgraph_update_post.append(update_preview_range)
bpy.app.driver_namespace['huyen_ve_action_browser_range_handler']=update_preview_range
update_preview_range(bpy.context.scene)
name='HUYEN VE - OPEN ANIMATION BROWSER'
text=bpy.data.texts.get(name) or bpy.data.texts.new(name);text.clear();text.write(Path(__file__).read_text(encoding='utf-8'))
# Save UI as a separate viewer file; model source and game pack are untouched.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'huyen-ve-animation-browser.blend'))
print('Animation browser ready: 89 HV_* actions; Space plays/stops; frame range follows selection during this session')
