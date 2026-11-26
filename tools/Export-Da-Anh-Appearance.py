"""Export approved Da Anh on genuine native 96-bone humanoid01e."""
import bpy,addon_utils,sys,json,hashlib,subprocess,bmesh
from pathlib import Path
from mathutils import Matrix
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/da-anh-v8-appearance';BASE='variantmeshes/wh_variantmodels/mc_da_anh';G=O/BASE;T=G/'tex';P=O/'png';T.mkdir(parents=True,exist_ok=True);P.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim,rmv2_format as rf
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/working/da-anh/da-anh-legendary-hero.blend'));rig=bpy.data.objects['Da Anh | Native humanoid01e'];rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update()
visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get()];parts=[];maps={}
def select(obs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
def subset(mesh,material):
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=material],context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(mesh);bm.free();mesh.update()
def dds(im,kind):
 key=hashlib.sha256(bytes(im.packed_file.data) if im.packed_file else (im.name+str(tuple(im.pixels[:4]))).encode()).hexdigest()[:16]+'_'+str(kind)
 if key in maps:return maps[key]
 stem='map_'+key;png=P/(stem+'.png');old=im.filepath_raw;im.filepath_raw=str(png);im.file_format='PNG';im.save();im.filepath_raw=old
 fmt='BC7_UNORM_SRGB' if kind==27 else 'BC3_UNORM' if kind==1 else 'BC7_UNORM'
 subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f',fmt,'-o',str(T),str(png)],check=True,stdout=subprocess.DEVNULL)
 maps[key]=BASE+'/tex/'+stem+'.dds';return maps[key]
def flat(name,rgba):
 im=bpy.data.images.get(name)
 if not im:
  im=bpy.data.images.new(name,width=4,height=4,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels[:]=list(rgba)*16
 return im
for src in visible:
 if src.name.startswith('Death Squad knife'):
  ob=src.copy();ob.data=src.data.copy();bpy.context.scene.collection.objects.link(ob)
  hand='hand_right' if 'hand_right' in src.name else 'hand_left';transform=rig.data.bones[hand].matrix_local@src.matrix_basis
  ob.constraints.clear();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.data.transform(transform);ob.vertex_groups.clear();ob.vertex_groups.new(name=hand).add(list(range(len(ob.data.vertices))),1,'REPLACE')
  for m in list(ob.modifiers):ob.modifiers.remove(m)
  mod=ob.modifiers.new('Native 01e skin','ARMATURE');mod.object=rig;split=[ob]
 else:
  split=[]
  for i in sorted({f.material_index for f in src.data.polygons}):
   ob=src.copy();ob.data=src.data.copy();bpy.context.scene.collection.objects.link(ob);subset(ob.data,i)
   mat=src.data.materials[i];ob.data.materials.clear();ob.data.materials.append(mat)
   for f in ob.data.polygons:f.material_index=0
   ob.name='DA ENGINE | '+src.name+' '+str(i);split.append(ob)
 for ob in split:
  mat=ob.data.materials[0];nodes=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image];images={}
  for n in nodes:
   name=n.image.name.lower();kind=27 if any(s in name for s in ['base_colour','base_color','basecolor','diffuse']) else 29 if any(s in name for s in ['materialmap','material_map','material.dds']) else 1 if 'normal' in name else None
   if kind:images[kind]=n.image
  # Procedural black cloth is emitted as self-contained constant PBR maps.
  if not images:
   images={27:flat('Da Anh black fabric base',(.07,.075,.09,1)),29:flat('Da Anh black fabric material',(0,.88,1,1)),1:flat('Da Anh flat normal',(.5,.5,1,1))}
  if 'Outer shirt' in ob.name:
   images[29]=flat('Da Anh outer cloth material',(0,.85,1,1));images[1]=flat('Da Anh flat normal',(.5,.5,1,1))
  assert 27 in images,(ob.name,[n.image.name for n in nodes])
  images.setdefault(29,flat('Da Anh default material',(0,.85,1,1)));images.setdefault(1,flat('Da Anh flat normal',(.5,.5,1,1)))
  ob.rmv2.textures.clear()
  for kind,im in sorted(images.items()):
   slot=ob.rmv2.textures.add();slot.set_type_from_int(kind);slot.path=dds(im,kind)
  ob.rmv2.vertex_format='CINEMATIC';ob.hide_set(False);ob.hide_render=False;parts.append(ob)
 for ob in [src]:ob.hide_set(True);ob.hide_render=True
select(parts);path=G/'da_anh.rigid_model_v2'
assert bpy.ops.export_scene.rmv2(filepath=str(path),source='SELECTED',skeleton_name='humanoid01e',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
f=rf.load(path.read_bytes());assert f.skeleton_name=='humanoid01e' and len(f.lods)==4
counts=[]
for lod in f.lods:
 for m in lod.models:
  assert m.mesh.bone_indices.max()<96 and abs(m.mesh.bone_weights.sum(axis=1)-1).max()<.02
  for typ,tx in m.material.textures:assert (O/tx).exists(),tx
 counts.append(sum(len(m.mesh.indices)//3 for m in lod.models))
# Reimport actual exported geometry and exercise the unchanged native runtime rig.
select([rig]);before=set(bpy.data.objects);bpy.ops.import_scene.rmv2(filepath=str(path),build_materials=True,texture_root=str(O),import_all_lods=False,attach_armature=True)
imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
for ob in parts:ob.hide_set(True);ob.hide_render=True
for ob in imported:ob.hide_set(False);ob.hide_render=False
clips=json.loads((R/'build/celestial-concubines-animation/clips.json').read_text());D=R/'reference/local/celestial-concubines';checks=[]
rig.data.pose_position='POSE'
for clip in clips:
 select([rig]);import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});action=rig.animation_data.action;action.use_fake_user=True
 a,b=map(int,action.frame_range);poses=[]
 for frame in sorted({a,(a+b)//2,b}):
  bpy.context.scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();pts=[]
  for ob in imported:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.asarray([tuple(v.co) for v in me.vertices]);assert np.isfinite(p).all();pts.append(p);ev.to_mesh_clear()
  poses.append(np.concatenate(pts))
 delta=max(float(np.linalg.norm(p-poses[0],axis=1).max()) for p in poses[1:]);assert delta>1e-5
 checks.append(dict(clip=clip['path'],motion=delta))
select([rig]);import_anim.import_file(bpy.context,str(D/clips[0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});bpy.context.scene.frame_set(0);rig.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'engine-da-anh.blend'),compress=True)
report=dict(model=BASE+'/da_anh.rigid_model_v2',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),skeleton='humanoid01e',bones=96,lod_triangles=counts,parts=len(f.lods[0].models),roundtrip_clips=checks,sampled_poses=len(checks)*3,textures=list(maps.values()),native_bind_preserved=True,runtime_verified=False)
(O/'export-report.json').write_text(json.dumps(report,indent=2));print('DA_ANH_EXPORT_READY',counts,flush=True)


