"""Copy approved model, retaining all seven original DEER head options."""
import bpy,json,hashlib,math,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-approved-variants';O.mkdir(parents=True,exist_ok=True)
SOURCE=R/'build/deer-jade-animation-review/jade-warrior-brown-boots-animation-review-v2.blend'
OUT=O/'moon-jade-warriors-approved-seven-variants.blend';assert not OUT.exists()
shutil.copy2(SOURCE,O/'approved-single-model-animation-checkpoint.blend')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
arm=next(o for o in scene.objects if o.type=='ARMATURE')
def bound(ob):
 return ob.parent==arm or any(m.type=='ARMATURE' and m.object==arm for m in ob.modifiers) or any(c.type=='CHILD_OF' and c.target==arm for c in ob.constraints)
base=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and bound(o) and 'beitingsheshouh5.rigid_model_v2' not in o.get('source_geometry','')]
assert any('reference ring-pommel dao' in o.name for o in base)
assert any('rear neckguard' in o.name for o in base)
def geometry_hash(ob):return hashlib.sha256(json.dumps([list(v.co) for v in ob.data.vertices]).encode()).hexdigest()
base_hash={o.name:geometry_hash(o) for o in base}
gallery=R/'build/deer-jade-reskin-gallery/deer24-jade-warriors-reskin-gallery.blend'
with bpy.data.libraries.load(str(gallery),link=False) as (src,dst):
 dst.collections=[n for n in src.collections if n.startswith('HEAD ')]
heads=sorted(dst.collections,key=lambda c:c.name)
assert len(heads)==7
source_scene_objects=list(scene.objects);models=[];rigs=[];all_variant_meshes=[]
for i,headcol in enumerate(heads):
 x=(i-3)*1.45;col=bpy.data.collections.new('VARIANT %02d | approved body05 + DEER head%02d'%(i+1,i+1));scene.collection.children.link(col)
 rig=arm.copy();rig.data=arm.data.copy();rig.name='Moon Jade %02d | native humanoid01e'%(i+1);col.objects.link(rig);rig.location.x=x;rig.hide_set(True);rigs.append(rig)
 obs=[]
 for source in base+[o for o in headcol.objects if o.type=='MESH']:
  ob=source.copy();ob.data=source.data.copy();col.objects.link(ob);ob.name='Moon Jade %02d | %s'%(i+1,source.name);ob.hide_render=False;ob.hide_set(False)
  if source not in base:
   ob.parent=rig;ob.matrix_parent_inverse.identity();ob.matrix_basis.identity()
  elif ob.parent==arm:ob.parent=rig
  for mod in ob.modifiers:
   if mod.type=='ARMATURE':mod.object=rig
  for con in ob.constraints:
   if con.type=='CHILD_OF' and con.target==arm:con.target=rig
  obs.append(ob)
 for source,ob in zip(base,obs):assert geometry_hash(ob)==base_hash[source.name]
 models.append(dict(number=i+1,key='mc_moon_jade_warrior_appearance_%02d'%(i+1),source_head='1/beitingsheshou/beitingsheshouh%d.wsmodel'%(i+1),collection=col.name,mesh_count=len(obs),rig=rig.name))
 all_variant_meshes.extend(obs)
# Remove source objects from this new gallery, keeping their saved checkpoint intact.
for ob in source_scene_objects:
 if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.materials.new('Variant labels');mat.use_nodes=True;s=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in s.inputs:s.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in s.inputs:s.inputs['Emission Strength'].default_value=.7
for i in range(7):
 cv=bpy.data.curves.new('FACE %02d'%(i+1),'FONT');cv.body='FACE %02d'%(i+1);cv.align_x='CENTER';cv.size=.12;cv.materials.append(mat);ob=bpy.data.objects.new(cv.body,cv);scene.collection.objects.link(ob);ob.location=((i-3)*1.45,-.42,-.19);ob.rotation_euler=(math.pi/2,0,0)
scene.frame_set(1);bpy.context.view_layer.update()
cam=scene.camera;target=Vector((0,0,.97));cam.location=(0,-16,1.7);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=10.8
scene.render.resolution_x=2400;scene.render.resolution_y=850
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_perspective='CAMERA';sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
checks=[];plan=json.loads((R/'build/deer-jade-animation-review/review-report.json').read_text())
for seg in plan['segments']:
 for f in [seg['start'],(seg['start']+seg['end'])//2,seg['end']]:
  scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for ob in all_variant_meshes:
   ev=ob.evaluated_get(dg);mesh=ev.to_mesh();assert all(math.isfinite(c) for v in mesh.vertices for c in v.co);ev.to_mesh_clear()
  checks.append(f)
scene.frame_set(1);bpy.context.view_layer.update()
note=bpy.data.texts.new('APPROVED | Moon Jade Warrior appearance family');note.write('User approved 26 November 2026. Same edited body05, original DEER head options01-07 (face/hair/beard options, not a claim of seven different face geometries), rear neckguard from06, round Chen shield, reference dao with corrected sharp edge and flat native-thickness spine, flattened brown boot toes. Eight-stage Blender montage retained. Assets only; no RMV2/DDS bake/LODs/pack export or game integration yet. Moon-only intended scope; do not globally override native Jade Warriors.\n'+json.dumps(models,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'moon-jade-seven-variants.png');bpy.ops.render.render(write_still=True)
for i in range(7):
 target=Vector(((i-3)*1.45,0,1.61));cam.location=target+Vector((.19,-2,.08));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.57
 scene.render.resolution_x=600;scene.render.resolution_y=650;scene.render.filepath=str(O/('face-%02d.png'%(i+1)));bpy.ops.render.render(write_still=True)
report=dict(scene=str(OUT),approved_source=str(SOURCE),approved_source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),single_checkpoint=str(O/'approved-single-model-animation-checkpoint.blend'),models=models,sampled_frames=checks,source_appearance_geometry_unchanged=True,packed_images=sum(bool(im.packed_file) for im in bpy.data.images),linked_libraries=len(bpy.data.libraries),intended_faction='Agents of the Moon',current_equipment='Jade Warriors sword and shield',game_integrated=False,game_exported=False,heads_are_source_options_not_necessarily_distinct_faces=True)
(O/'approved-variants-report.json').write_text(json.dumps(report,indent=2))
print('MOON_JADE_VARIANTS_READY',len(models),flush=True)
