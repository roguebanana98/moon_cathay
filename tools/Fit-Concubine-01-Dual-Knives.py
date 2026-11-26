"""Body/head01 knife fitting; preserve the native sword-shield review action."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';O.mkdir(parents=True,exist_ok=True)
SOURCE=R/'build/celestial-concubines-animation/celestial-concubines-animation-review.blend'
DONOR=R/'build/deer-miao-witch-preview/deer-miao-witch-elves-dual-knives.blend'
OUT=O/'celestial-concubine-01-head-01-dual-knives.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
rig=bpy.data.objects['Body_01_native_humanoid01e'];root=rig.parent
for ob in bpy.data.objects:ob.hide_set(True);ob.hide_render=True
root.location=(0,0,0)
body=list(root.children_recursive)
for ob in [root]+body:ob.hide_set(False);ob.hide_render=False
rig.hide_set(True)
with bpy.data.libraries.load(str(DONOR),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n in ['Death Squad knife | hand_right','Death Squad knife | hand_left']]
weapons=[]
for ob in dst.objects:
 assert ob is not None
 local=ob.matrix_basis.copy();hand='hand_right' if 'hand_right' in ob.name else 'hand_left'
 anchor=bpy.data.objects.new('Death Squad grip | '+hand,None);scene.collection.objects.link(anchor)
 con=anchor.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=hand
 ob.parent=anchor;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local
 for con in list(ob.constraints):ob.constraints.remove(con)
 if not ob.users_collection:scene.collection.objects.link(ob)
 ob.hide_set(False);ob.hide_render=False;anchor.hide_render=True;weapons.append(ob)
assert len(weapons)==2
checks=[]
for frame in (1,50,100,160,220,280,336):
 scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for ob in weapons:
  hand='hand_right' if 'hand_right' in ob.name else 'hand_left'
  actual=ob.evaluated_get(dg).matrix_world@Vector(ob['handle_midpoint'])
  expected=rig.matrix_world@rig.pose.bones[hand].matrix@Vector(ob['palm_target'])
  err=(actual-expected).length;assert err<1e-4,err;checks.append(dict(frame=frame,hand=hand,handle_to_palm_error=err))
scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
   sp.region_3d.view_location=(0,0,1);sp.region_3d.view_distance=3.2;sp.region_3d.view_rotation=Vector((-.4,8,-.5)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'
notes=bpy.data.texts.new('DUAL KNIFE FITTING');notes.write('Body01 + head01 with two Dark Society Death Squad knives. Original sword and shield retained hidden. Existing native hu1e_sword_and_shield review animation retained for fitting; this is NOT a dual-knife combat animation conversion. Other variants retained hidden. No mod changes.')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'weapon-fit.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),body=1,head=1,weapon_models=['ninja_knife_1','ninja_knife_2'],animation_unchanged='hu1e_sword_and_shield',checks=checks,game_modified=False),indent=2))
print('DUAL_KNIFE_FIT_READY',flush=True)
