"""Preview native attack on the user's manually placed sword and original hands."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
record_path=Path((O/'sword-manual-adjustment-latest.txt').read_text(encoding='utf-8').strip())
record=json.loads(record_path.read_text(encoding='utf-8'))
assert Path(record['source_live_file']).name=='huyen-ve-before-hand-fix.blend'
source=Path(record['saved_copy']);assert hashlib.sha256(source.read_bytes()).hexdigest()==record['saved_copy_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
rig=bpy.data.objects['humanoid01e_HuyenVe'];body=bpy.data.objects['mc_huyen_ve_body_lod0'];sword=bpy.data.objects['mc_huyen_ve_sword_lod0']
def geometry_hash(obj):return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in obj.data.vertices)).hexdigest()
before={o.name:geometry_hash(o) for o in [body,sword]};basis=sword.matrix_basis.copy()
rig.animation_data.action=bpy.data.actions['QA_attack']
scene.frame_start=0;scene.frame_end=62;scene.render.fps=30;scene.frame_set(0);bpy.context.view_layer.update()
orientation=(-Vector((2,-5,1.8))).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='MATERIAL';space.shading.use_scene_lights=False;space.shading.use_scene_world=False;space.overlay.show_overlays=False
   space.lock_object=rig;space.lock_bone='root';space.region_3d.view_location=(0,0,0);space.region_3d.view_rotation=orientation;space.region_3d.view_distance=3.6
after={o.name:geometry_hash(o) for o in [body,sword]};assert before==after
assert max(abs(basis[i][j]-sword.matrix_basis[i][j]) for i in range(4) for j in range(4))<1e-8
destination=O/'huyen-ve-manual-sword-attack-preview.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
report=dict(source=str(source),output=str(destination),action='QA_attack',frame_start=0,frame_end=62,fps=30,
 geometry_unchanged=True,sword_placement_unchanged=True,geometry_hashes=after,sword_location=list(sword.location),
 scope='Only choose existing native animation and set viewport playback; no hand/body/bone/constraint/LOD/export edits')
(O/'manual-sword-attack-preview.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
