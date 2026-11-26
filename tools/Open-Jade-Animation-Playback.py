"""Run only when launching the saved review interactively, never save over it."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-animation-review'
def start():
 window=bpy.context.window_manager.windows[0]
 area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
 for a in window.screen.areas:
  if a.type=='DOPESHEET_EDITOR':
   region=next((r for r in a.regions if r.type=='WINDOW'),None)
   if region:
    try:
     with bpy.context.temp_override(window=window,area=a,region=region):bpy.ops.action.view_all()
    except RuntimeError:pass
 with bpy.context.temp_override(window=window,area=area):
  if not window.screen.is_animation_playing:bpy.ops.screen.animation_play()
 bpy.app.timers.register(observe,first_interval=2)
 return None
observations=[]
def observe():
 observations.append(dict(frame=bpy.context.scene.frame_current,playing=any(w.screen.is_animation_playing for w in bpy.context.window_manager.windows)))
 (O/'live-playback-status.json').write_text(json.dumps(observations))
 return 2 if len(observations)<3 else None
bpy.app.timers.register(start,first_interval=4)
