"""Extend approved fitted black fabric to exposed torso and arms."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';SOURCE=O/'celestial-concubine-01-black-leggings.blend';OUT=O/'celestial-concubine-01-black-bodysuit.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));body=bpy.data.objects['Iron_Body'];body.data=body.data.copy()
mat=bpy.data.materials['Black fitted leg fabric'];idx=next(i for i,m in enumerate(body.data.materials) if m==mat)
changed=sum(p.material_index!=idx for p in body.data.polygons)
for p in body.data.polygons:p.material_index=idx
body['fabric_cover']='Opaque fitted black fabric over torso, arms, hips and thighs; face, hair, armour, weapons, original shape and weights retained.'
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'black-bodysuit.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),newly_covered_faces=changed,all_body_faces=len(body.data.polygons),geometry_unchanged=True,weights_unchanged=True,game_modified=False),indent=2))
print('BLACK_BODYSUIT_READY',flush=True)
