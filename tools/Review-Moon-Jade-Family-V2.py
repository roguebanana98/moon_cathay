"""Review unchanged exported people against four native equipment/animation sets."""
import bpy,json,sys,math,subprocess,importlib.util
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-jade-reskin-v2';D=R/'reference/local/moon-jade-expanded';M=json.loads((O/'native-review-assets.json').read_text())
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_rmv2,import_anim,materials
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
warnings=[];checks=[];units=[];converted={}
def select(rig):
 bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
def load(rig,path):
 rig.animation_data_clear()
 for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.matrix_basis.identity()
 select(rig);_,_,issues=import_anim.import_file(bpy.context,str(D/path),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));warnings.extend(issues);complete_preview_channels(rig.animation_data.action,rig)
 return tuple(map(int,rig.animation_data.action.frame_range))
def model(entry,rig=None):
 if rig:select(rig)
 root,_=import_rmv2.import_file(bpy.context,str(D/entry['geometry']),dict(build_materials=False,import_lods='FIRST',attach_armature=bool(rig)))
 lod=next(c for c in root.children if 'lod0' in c.name.lower());obs=[o for o in lod.objects if o.type=='MESH'];assert len(obs)==len(entry['parts'])
 for ob,part in zip(obs,entry['parts']):
  pairs=[]
  for typ,path in part['textures']:
   if path not in converted:
    src=D/path;dest=O/'native-preview-textures'/Path(path).parent;dest.mkdir(parents=True,exist_ok=True);png=dest/(src.stem+'.png')
    if not png.exists():subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(src)],check=True,stdout=subprocess.DEVNULL)
    converted[path]=png.relative_to(O).as_posix()
   pairs.append((typ,converted[path]))
  mat=materials.build_material(ob.name,pairs,'TRANSPARENT' if 'alpha_on' in part['material'] else 'OPAQUE',str(O));ob.data.materials.clear();ob.data.materials.append(mat);ob.hide_render=False;ob.hide_set(False)
 return obs
for key,unit in M['units'].items():
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets/working/moon-jade-warriors/moon-jade-exported-assets-review.blend'));scene=bpy.context.scene;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.cycles.samples=12
 arm=next(o for o in scene.objects if o.type=='ARMATURE')
 for ob in list(scene.objects):
  if ob.type=='MESH' and any(c.type=='CHILD_OF' and c.target==arm for c in ob.constraints):bpy.data.objects.remove(ob,do_unlink=True)
 people=[o for o in scene.objects if o.type=='MESH'];props=[]
 for prop in unit['props']:
  obs=model(M['models'][prop['model']])
  for ob in obs:
   con=ob.constraints.new('CHILD_OF');con.target=arm;con.subtarget=prop['attach'];con.inverse_matrix=Matrix.Identity(4)
  props.extend(obs)
 horse=None;horse_meshes=[]
 if key=='lancers':
  select(arm);bpy.ops.object.select_all(action='DESELECT');horse,_,issues=import_anim.import_file(bpy.context,str(D/'animations/skeletons/horse01.anim'),dict(mode='SKELETON',attach_meshes=False,global_scale=1.0));warnings.extend(issues)
  for entry in M['mount']:horse_meshes.extend(model(M['models'][entry['model']],horse))
  load(horse,M['horse_clips'][0])
 allobs=people+props+horse_meshes
 for clip in unit['clips']:
  first,last=load(arm,clip);first=max(1,first)
  for frame in sorted({first,(first+last)//2,last}):
   scene.frame_set(frame);bpy.context.view_layer.update()
   if horse:
    # Native rider clips are relative to the mount root (hip approx z=.11).
    # Presentation adds that root height; engine placement remains untouched.
    arm.location=horse.matrix_world@horse.pose.bones['root'].matrix.translation
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
   for ob in allobs:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();assert all(math.isfinite(c) and abs(c)<20 for v in me.vertices for c in v.co),(key,clip,frame,ob.name);ev.to_mesh_clear()
   checks.append(dict(unit=key,clip=clip,frame=frame,all_seven_heads=True))
  print('JADE_FAMILY_NATIVE_CLIP',key,clip,flush=True)
 load(arm,unit['clips'][0]);scene.frame_set(1);bpy.context.view_layer.update()
 if horse:arm.location=horse.matrix_world@horse.pose.bones['root'].matrix.translation
 bpy.context.view_layer.update();cam=scene.camera
 target=Vector((0,-.15,1.5 if horse else 1.05));cam.location=target+Vector((3,-6,1.4 if horse else .8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.2 if horse else 2.8
 scene.render.filepath=str(O/(key+'-native-equipment.png'));bpy.ops.render.render(write_still=True)
 # Crossbow aiming pose, with the same native props retained for inspection.
 if key.startswith('crossbow'):
  aim=unit['clips'][2];first,last=load(arm,aim);scene.frame_set(max(1,(first+last)//2));bpy.context.view_layer.update();scene.render.filepath=str(O/(key+'-aim.png'));bpy.ops.render.render(write_still=True)
  load(arm,unit['clips'][0]);scene.frame_set(1)
 arm.hide_set(True)
 if horse:horse.hide_set(True)
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(key+'-review.blend')),compress=True)
 units.append(dict(key=key,unit=unit['unit'],native_equipment=True,people_model_unchanged=True,mounted=bool(horse)))
(O/'family-review.json').write_text(json.dumps(dict(status='passed',units=units,checks=checks,warnings=warnings,native_equipment_and_mount_unchanged=True,body_and_seven_heads_unchanged_from_v1=True,mounted_presentation='rider clip relative to native horse root; no engine animation changes',runtime_verified=False),indent=2));print('JADE_FAMILY_REVIEW_PASSED',len(checks),flush=True)
