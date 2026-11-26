"""Reimport actual RMV2/DDS output and review native animations, not source meshes."""
import bpy,json,sys,importlib.util,subprocess,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-jade-reskin-v1';D=R/'reference/local/divine-wing-guard'
E=json.loads((O/'export-report.json').read_text());assert len(E['models'])==10
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_rmv2,import_anim,materials,rmv2_format as rf
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene
arm,_,warnings=import_anim.import_file(bpy.context,str(D/'animations/skeletons/humanoid01e.anim'),dict(mode='SKELETON',attach_meshes=False,global_scale=1.0));arm.name='Moon Jade | actual exported asset review';warnings=list(warnings)
meshes={};pivots={};converted={}
for entry in E['models']:
 arm.hide_set(False);bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
 root,stats=import_rmv2.import_file(bpy.context,str(O/entry['path']),dict(build_materials=False,import_lods='FIRST',attach_armature=entry['weighted']))
 lod=next(c for c in root.children if 'lod0' in c.name.lower());obs=[o for o in lod.objects if o.type=='MESH'];assert len(obs)==len(entry['parts'])
 for ob,row in zip(obs,entry['parts']):
  pairs=[]
  for typ,path in row['textures'].items():
   if path not in converted:
    src=O/path;dest=O/'roundtrip-textures'/Path(path).parent;dest.mkdir(parents=True,exist_ok=True);png=dest/(src.stem+'.png')
    if not png.exists():subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(src)],check=True,stdout=subprocess.DEVNULL)
    converted[path]=png.relative_to(O).as_posix()
   pairs.append((int(typ),converted[path]))
  mat=materials.build_material(ob.name,pairs,'TRANSPARENT' if row['alpha'] else 'OPAQUE',str(O));ob.data.materials.clear();ob.data.materials.append(mat)
  if not entry['weighted']:
   assert max(abs(ob.matrix_basis.translation[i]-row['pivot'][i]) for i in range(3))<1e-5
   con=ob.constraints.new('CHILD_OF');con.target=arm;con.subtarget='weapon_2' if entry['key']=='dao' else 'weapon_3';con.inverse_matrix=Matrix.Identity(4);pivots[ob.name]=ob.matrix_basis.copy()
  if entry['key'].startswith('head_'):ob.hide_render=entry['key']!='head_01';ob.hide_set(entry['key']!='head_01')
 meshes[entry['key']]=obs
plan=json.loads((R/'build/deer-jade-animation-review/review-report.json').read_text())['segments'];checks=[]
for seg in plan:
 arm.animation_data_clear();arm.hide_set(False)
 for p in arm.pose.bones:p.rotation_mode='QUATERNION';p.matrix_basis.identity()
 bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
 _,_,issues=import_anim.import_file(bpy.context,str(D/seg['source']),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));warnings.extend(issues);complete_preview_channels(arm.animation_data.action,arm)
 first,last=map(int,arm.animation_data.action.frame_range);first=max(1,first)
 for frame in sorted({first,(first+last)//2,last}):
  scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for key,obs in meshes.items():
   for ob in obs:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();assert all(math.isfinite(c) and abs(c)<10 for v in me.vertices for c in v.co),(key,frame);ev.to_mesh_clear()
    if ob.name in pivots:
     con=ob.constraints[0];expected=arm.matrix_world@arm.pose.bones[con.subtarget].matrix@pivots[ob.name];actual=ev.matrix_world
     assert max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))<1e-4
  checks.append(dict(clip=seg['label'],frame=frame,all_seven_heads_and_props=True))
 print('EXPORTED_ASSET_ANIM_CHECK',seg['label'],flush=True)
# Restore native idle and render the actual packed-output appearance.
arm.animation_data_clear()
for pb in arm.pose.bones:pb.matrix_basis.identity()
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
import_anim.import_file(bpy.context,str(D/plan[0]['source']),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));scene.frame_set(1);bpy.context.view_layer.update()
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=1000;scene.render.resolution_y=1100
world=bpy.data.worlds.new('Export review studio');world.use_nodes=True;scene.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.07,.085,.11,1);bg.inputs[1].default_value=.4
target=Vector((0,0,1.05))
for name,position,power,size in [('Key',(-4,-5,7),1800,6),('Fill',(5,-4,4),1300,5),('Rim',(0,4,7),2000,5)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=position;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();ob.hide_set(True)
cd=bpy.data.cameras.new('Export review');cam=bpy.data.objects.new('Export review',cd);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(1.4,-3.8,1.8);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=2.35
scene.render.filepath=str(O/'actual-exported-model.png');bpy.ops.render.render(write_still=True)
for i in [1,7]:
 for key,obs in meshes.items():
  if key.startswith('head_'):
   for ob in obs:ob.hide_render=key!='head_%02d'%i;ob.hide_set(ob.hide_render)
 target=Vector((0,0,1.61));cam.location=target+Vector((.19,-2,.08));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=.57;scene.render.resolution_x=600;scene.render.resolution_y=650
 scene.render.filepath=str(O/('actual-exported-head-%02d.png'%i));bpy.ops.render.render(write_still=True)
for key,obs in meshes.items():
 if key.startswith('head_'):
  for ob in obs:ob.hide_render=key!='head_01';ob.hide_set(ob.hide_render)
target=Vector((0,0,1.05));cam.location=(1.4,-3.8,1.8);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=2.35
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
arm.hide_set(True)
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'actual-exported-model-review.blend'),compress=True)
(O/'roundtrip-review.json').write_text(json.dumps(dict(status='passed',checks=checks,head_options=7,model_files=10,source_sha256=E['source_sha256'],warnings=warnings,actual_RMV2_DDS_reimport=True,prop_pivots_verified=True,runtime_verified=False),indent=2));print('MOON_JADE_ROUNDTRIP_PASSED',flush=True)
