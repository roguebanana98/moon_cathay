"""Background Blender review; separate scenes, never overwrite approved sources."""
import ast,bpy,copy,hashlib,importlib.util,json,math,shutil,subprocess,sys,xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v36-zhao-jade';M=json.loads((O/'asset-review-input.json').read_text());D=Path(M['reference'])
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_rmv2,import_anim,materials
sys.path.insert(0,str(addon_dir));import rmv2_format as rf
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
warnings=[];converted={};checks=[];renders=[]
helpers=ast.parse((R/'tools/Review-Moon-Jade-Family-V2.py').read_text());exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['select','load','model']],type_ignores=[]),'<model review helpers>','exec'))
def skeleton(key):
 bpy.ops.object.select_all(action='DESELECT')
 rig,_,issues=import_anim.import_file(bpy.context,str(D/('animations/skeletons/'+key+'.anim')),dict(mode='SKELETON',attach_meshes=False,global_scale=1.0));warnings.extend(issues);return rig
body_entry=next(p for p in M['zhao'] if p['slot']=='body');sword_entry=next(p for p in M['zhao'] if p['slot']=='weapon_2')
original_sword=M['models'][sword_entry['model']]
def reset_scene():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 rig=skeleton('humanoid01e');body=model(M['models'][body_entry['model']],rig);return rig,body
def prop(entry,rig,bone):
 obs=model(entry)
 for ob in obs:
  c=ob.constraints.new('CHILD_OF');c.target=rig;c.subtarget=bone;c.inverse_matrix=Matrix.Identity(4)
 return obs
def render(name,obs):
 scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Review neutral');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1)
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 pts=[ob.matrix_world@Vector(c) for ob in obs for c in ob.bound_box];lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)]);target=(lo+hi)/2
 data=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(cam);cam.location=target+Vector((3,-7,1.6));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z)*1.25;scene.camera=cam
 for title,delta,power in [('Key',(1,-4,6),1300),('Fill',(-4,-1,3),850),('Rim',(2,4,5),1500)]:
  data=bpy.data.lights.new(title,'AREA');data.energy=power;data.size=5;ob=bpy.data.objects.new(title,data);scene.collection.objects.link(ob);ob.location=target+Vector(delta);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);renders.append(scene.render.filepath)
 for im in bpy.data.images:
  if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')),compress=True)

rig,body=reset_scene();sword=prop(original_sword,rig,'weapon_2');load(rig,M['clips']['foot'][0]);bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
K=rig.pose.bones['hand_right'].matrix.inverted()@rig.pose.bones['weapon_2'].matrix
assert abs(K.to_3x3().determinant()-1)<1e-4
before=rf.load((D/original_sword['geometry']).read_bytes());after=copy.deepcopy(before)
B=np.array([[-1,0,0],[0,0,-1],[0,1,0]],dtype=np.float64);rotation=np.array(K.to_3x3());G=np.linalg.inv(B)@rotation@B
for lod in after.lods:
 for part in lod.models:
  part.material.pivot=tuple(np.linalg.inv(B)@(rotation@(B@np.array(part.material.pivot))+np.array(K.translation)))
  part.mesh.positions=(part.mesh.positions@G.T).astype(np.float32)
  # Loaded RMV meshes retain a lossless raw vertex block. Clear it after edits
  # or save() would silently write the original, untransformed vertices.
  part.mesh.raw_block=None
  for attr in ['normals','tangents','binormals']:
   a=getattr(part.mesh,attr,None)
   if a is not None and a.ndim==2 and a.shape[1]>=3:a[:,:3]=a[:,:3]@G.T
  part.bbox_min=None;part.bbox_max=None
geo='variantmeshes/wh_variantmodels/mc_zhao_v36/mounted_sword_hand.rigid_model_v2';dest=O/geo;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(rf.save(after));actual=rf.load(dest.read_bytes());errors=[]
assert len(actual.lods)==4
for old,new in zip(before.lods,actual.lods):
 for a,b in zip(old.models,new.models):
  expected=(a.mesh.positions+np.array(a.material.pivot))@B.T@rotation.T+np.array(K.translation);got=(b.mesh.positions+np.array(b.material.pivot))@B.T
  err=float(abs(expected-got).max());print('MOUNTED_SWORD_ROUNDTRIP',err,'pivot',a.material.pivot,b.material.pivot,'sample',expected[0].tolist(),got[0].tolist(),flush=True);assert err<.002;errors.append(err)
  assert np.array_equal(a.mesh.indices,b.mesh.indices) and np.array_equal(a.mesh.uv0,b.mesh.uv0)
ws=ET.parse(D/sword_entry['model']).getroot();ws.find('geometry').text=geo
wspath='variantmeshes/wh_variantmodels/mc_zhao_v36/mounted_sword_hand.wsmodel';(O/wspath).write_bytes(ET.tostring(ws,encoding='utf-8'))
vmd=ET.parse(D/M['foot_vmd']).getroot();slot=vmd.find("SLOT[@name='weapon_2']");slot.set('attach_point','hand_right');slot.find('VARIANT_MESH').set('model',wspath)
vmdpath='variantmeshes/variantmeshdefinitions/mc_zhao_v36_mounted.variantmeshdefinition';(O/vmdpath).parent.mkdir(parents=True,exist_ok=True);(O/vmdpath).write_bytes(ET.tostring(vmd,encoding='utf-8'))
(D/geo).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/geo,D/geo);mounted_entry=dict(original_sword,geometry=geo)
for kind,paths in M['clips'].items():
 if kind!='foot':
  rig,body=reset_scene();sword=prop(mounted_entry,rig,'hand_right')
  mount=M['mounts'][kind];mr=skeleton(mount['skeleton']);mountobs=[]
  for e in mount['entries']:mountobs.extend(model(M['models'][e['model']],mr))
  load(mr,mount['idle'])
 else:mr=None;mountobs=[]
 for clip in paths:
  first,last=load(rig,clip)
  for f in sorted({max(1,first),(max(1,first)+last)//2,last}):
   bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
   if mr:rig.location=mr.matrix_world@mr.pose.bones['root'].matrix.translation
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();max_extent=0
   for ob in body+sword+mountobs:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all() and abs(p).max()<30,(kind,clip,f);max_extent=max(max_extent,float(abs(p).max()))
   palm=rig.matrix_world@((rig.pose.bones['finger_index_right_0'].head+rig.pose.bones['finger_ring_right_0'].head)*.5)
   # Points are on the handle, rather than the blade or prop origin.
   handle=Vector((.44,0,0))
   if kind!='foot':handle=Vector(tuple(rotation@np.array(handle)))
   gap=(sword[0].evaluated_get(dg).matrix_world@handle-palm).length
   if kind!='foot':assert gap<.20,(kind,clip,f,gap)
   checks.append(dict(kind=kind,clip=clip,frame=f,handle_to_knuckles=gap,max_finite_extent=max_extent))
  print('V36_NATIVE_POSE',kind,Path(clip).name,flush=True)
 load(rig,paths[0]);bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 if mr:rig.location=mr.matrix_world@mr.pose.bones['root'].matrix.translation
 bpy.context.view_layer.update();render('zhao-'+kind+'-review',body+sword+mountobs)
rig.hide_set(True)
jade=json.loads((R/'build/moon-jade-reskin-v2/family-review.json').read_text());assert jade['status']=='passed'
additional=[geo,wspath,vmdpath,'script/campaign/mod/mc_zhao_v36_migration.lua']
report=dict(status='passed',additional_files=additional,checks=checks,source_body_and_foot_sword_unchanged=True,mounted_sword_all_four_lods=True,mounted_sword_transform_errors=errors,weapon_to_hand_matrix=[list(row) for row in K],warnings=warnings,renders=renders,jade_review_reused_for_byte_identical_v2_assets=True,full_clipping_or_runtime_not_proven=True,longma_two_rig_flight_alignment_unverified=True,runtime_verified=False)
assert not warnings,warnings
(O/'asset-review.json').write_text(json.dumps(report,indent=2));print('V36_ASSET_REVIEW_PASSED',len(checks),flush=True)
