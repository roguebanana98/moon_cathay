"""Align the cutting profile with the vanilla hammer's local striking axis."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/moon-generals-preview'
SOURCE=O/'moon-generals-bastion-hammer-shaft-guandao.blend'
OUT=O/'moon-generals-bastion-guandao-aligned.blend'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
blade=bpy.data.objects['Bastion | Guandao blade on native hammer shaft']
shaft=bpy.data.objects['Bastion | Original hammer shaft']
before=[tuple(v.co) for v in shaft.data.vertices]
# Native hammer's opposed impact caps run along local +/-Y. The previous
# cosmetic X90 roll put the blade's wide profile along Z, presenting its flat
# side in that strike direction. Undo that roll around the unchanged shaft X.
blade.data.transform(Matrix.Rotation(-math.pi/2,4,'X'))
blade.data.update()
widths=[max(v.co[k] for v in blade.data.vertices)-min(v.co[k] for v in blade.data.vertices) for k in range(3)]
assert widths[1]>5*widths[2],widths
assert before==[tuple(v.co) for v in shaft.data.vertices]
assert blade.constraints[0].subtarget=='weapon_1'
blade['orientation']='Blade cutting profile local XY; width/edge follows native hammer impact axis +/-Y; normal +/-Z'
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'guandao-alignment.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),blade_roll_correction_degrees=-90,blade_local_extents=widths,hammer_strike_axis='Y',blade_normal_axis='Z',shaft_vertices_unchanged=True,attachment_unchanged=True,game_modified=False),indent=2),encoding='utf8')
print('GUANDAO_STRIKE_AXIS_ALIGNED',flush=True)
