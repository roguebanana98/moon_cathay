"""Inverse-skin approved Da Anh to real native01d; export corrected prop frames."""
import bpy,addon_utils,sys,json,ast,hashlib,subprocess,bmesh,re
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/da-anh-v11-dagger-handbow';BASE='variantmeshes/wh_variantmodels/mc_da_anh';G=O/BASE;T=G/'tex';P=O/'png';T.mkdir(parents=True,exist_ok=True);P.mkdir(exist_ok=True);maps={}
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim,rmv2_format as rf
# Reuse tested native conversion and texture-export helpers without executing builds.
s=ast.parse((R/'tools/Export-Da-Anh-Appearance.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name in ['select','subset','dds','flat']],type_ignores=[]),'<texture helpers>','exec'))
original_dds=dds
def dds(im,kind):
 if im.packed_file and bytes(im.packed_file.data)[:4]==b'DDS ':
  raw=bytes(im.packed_file.data);key=hashlib.sha256(raw).hexdigest()[:16]+'_'+str(kind);target=T/('map_'+key+'.dds');target.write_bytes(raw);maps[key]=BASE+'/tex/'+target.name;return maps[key]
 return original_dds(im,kind)
s=ast.parse((R/'tools/Export-Moonshadow-Appearances.py').read_text(encoding='utf-8-sig'));wanted=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name=='convert']
aliases={'head_0':'head','neck_1':'neck_0','eyebrows_0':'eyebrow_0','eyelid_left_0':'eyelid_upper_left_0','eyelid_right_0':'eyelid_upper_right_0','shoulderpad_left_0':'shoulder_pad_left','shoulderpad_right_0':'shoulder_pad_right','armour_side_left_0':'root','armour_side_right_0':'root','skirt_front_center_0':'cingulum_front_0','skirt_front_center_1':'cingulum_front_1','skirt_back_left_0':'skirt_back_0','skirt_back_left_1':'skirt_back_1','skirt_back_right_0':'skirt_back_0','skirt_back_right_1':'skirt_back_1'}
exec(compile(ast.Module(body=wanted,type_ignores=[]),'<inverse native skin>','exec'))
SOURCE=R/'assets/working/da-anh/da-anh-dagger-handbow-approved.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE));source=bpy.data.objects['Da Anh | Native humanoid01e'];native=bpy.data.objects['REFERENCE Moonshadow Assassin native humanoid01d'];scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get()];bodies=[o for o in visible if any(m.type=='ARMATURE' and m.object==source for m in o.modifiers)];prop_sources=[o for o in visible if o not in bodies];assert len(prop_sources)==2
body=[];props=[];desired_points={};desired_normals={};dg=bpy.context.evaluated_depsgraph_get()
for src in bodies:
 for i in sorted({p.material_index for p in src.data.polygons}):
  ob=src.copy();ob.data=src.data.copy();scene.collection.objects.link(ob);subset(ob.data,i);mat=src.data.materials[i];ob.data.materials.clear();ob.data.materials.append(mat)
  for p in ob.data.polygons:p.material_index=0
  ob.name='DA11 | '+src.name+' '+str(i);body.append(ob)
for src in prop_sources:
 ob=src.copy();ob.data=src.data.copy();scene.collection.objects.link(ob);props.append(ob)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for ob in body:
 ev=ob.evaluated_get(dg);me=ev.to_mesh();desired_points[ob.name]=[ev.matrix_world@v.co for v in me.vertices];normal_matrix=ev.matrix_world.to_3x3().inverted().transposed();desired_normals[ob.name]=[(normal_matrix@n.vector).normalized() for n in me.corner_normals];ev.to_mesh_clear()
approved_props={ob.name:ob.evaluated_get(dg).matrix_world.copy() for ob in props}
def textures(ob):
 images={};mat=ob.data.materials[0]
 for n in mat.node_tree.nodes:
  if n.type!='TEX_IMAGE' or not n.image:continue
  name=n.image.name.lower();suffix=re.search(r'_(27|29|1)\.(dds|png)(?:\.\d+)?$',name)
  kind=int(suffix.group(1)) if suffix else 27 if any(s in name for s in ['base_colour','base_color','basecolor','diffuse']) else 29 if any(s in name for s in ['materialmap','material_map','material.dds']) else 1 if 'normal' in name else None
  if kind:images[kind]=n.image
 if not images:images={27:flat('Da Anh black fabric base',(.07,.075,.09,1)),29:flat('Da Anh black fabric material',(0,.88,1,1)),1:flat('Da Anh flat normal',(.5,.5,1,1))}
 if 'Outer shirt' in ob.name:images[29]=flat('Da Anh outer cloth material',(0,.85,1,1));images[1]=flat('Da Anh flat normal',(.5,.5,1,1))
 assert 27 in images,(ob.name,[n.image.name for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image])
 images.setdefault(29,flat('Da Anh default material',(0,.85,1,1)));images.setdefault(1,flat('Da Anh flat normal',(.5,.5,1,1)))
 ob.rmv2.textures.clear()
 for kind,im in images.items():slot=ob.rmv2.textures.add();slot.set_type_from_int(kind);slot.path=dds(im,kind)
for ob in body+props:textures(ob)
D=R/'reference/local/khainite-weapons';clips=json.loads((R/'build/moonshadow-animation-preview/clips.json').read_text());source.animation_data_clear();source.data.pose_position='REST';native.animation_data_clear();native.parent=None;native.matrix_world=Matrix.Identity(4);native.data.pose_position='POSE'
select([native]);import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01d/hands/hu1d_hand_pose_grip.anim'),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});scene.frame_set(0);bpy.context.view_layer.update()
grip_basis={b.name:b.matrix_basis.copy() for b in native.pose.bones if b.name.startswith(('finger_','thumb_'))}
def apply_grip():
 for name,matrix in grip_basis.items():native.pose.bones[name].matrix_basis=matrix
 bpy.context.view_layer.update()
select([native]);import_anim.import_file(bpy.context,str(D/clips[0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});scene.frame_set(0);apply_grip();native_skin={b.name:native.pose.bones[b.name].matrix@b.matrix_local.inverted() for b in native.data.bones}
for ob in body:convert(ob,source,native)
for ob in props:
 kind='handbow' if 'handbow' in ob.name.lower() else 'knife';bone='be_prop_5' if kind=='handbow' else 'be_prop_1'
 offset=native.pose.bones[bone].matrix.inverted()@approved_props[ob.name];ob.constraints.clear();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.data.transform(offset);ob.rmv2.vertex_format='STATIC';con=ob.constraints.new('COPY_TRANSFORMS');con.target=native;con.subtarget=bone;ob['export_kind']=kind
native.animation_data_clear();native.data.pose_position='REST';select(body);path=G/'da_anh.rigid_model_v2';assert bpy.ops.export_scene.rmv2(filepath=str(path),source='SELECTED',skeleton_name='humanoid01d',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
for ob in props:
 con=ob.constraints[0];con.mute=True;select([ob]);assert bpy.ops.export_scene.rmv2(filepath=str(G/(ob['export_kind']+'.rigid_model_v2')),source='SELECTED',skeleton_name='',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'};con.mute=False
models=[]
for p in G.glob('*.rigid_model_v2'):
 f=rf.load(p.read_bytes());assert len(f.lods)==4;assert f.skeleton_name==('humanoid01d' if p.stem=='da_anh' else '')
 for lod in f.lods:
  for m in lod.models:
   if p.stem=='da_anh':assert m.mesh.bone_indices.max()<83 and abs(m.mesh.bone_weights.sum(axis=1)-1).max()<.02
   for typ,tx in m.material.textures:assert (O/tx).exists(),tx
 models.append(dict(file=p.relative_to(O).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),lod_triangles=[sum(len(m.mesh.indices)//3 for m in l.models) for l in f.lods]))
# Reimport all actual engine exports, with actual native prop constraints.
for ob in visible+body+props:ob.hide_set(True);ob.hide_render=True
native.data.pose_position='POSE';select([native]);before=set(bpy.data.objects);bpy.ops.import_scene.rmv2(filepath=str(path),build_materials=True,texture_root=str(O),import_all_lods=False,attach_armature=True);imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];imported_props=[]
for kind,bone in [('knife','be_prop_1'),('handbow','be_prop_5')]:
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None;before=set(bpy.data.objects);bpy.ops.import_scene.rmv2(filepath=str(G/(kind+'.rigid_model_v2')),build_materials=True,texture_root=str(O),import_all_lods=False)
 for ob in [o for o in bpy.data.objects if o not in before and o.type=='MESH']:
  c=ob.constraints.new('COPY_TRANSFORMS');c.target=native;c.subtarget=bone;imported_props.append(ob)
all_clips=clips+[dict(label='Campaign '+str(i),path=p) for i,p in enumerate(json.loads((O/'campaign-clips.json').read_text()))];checks=[]
for clip in all_clips:
 select([native]);import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});action=native.animation_data.action;action.use_fake_user=True;a,b=map(int,action.frame_range);poses=[]
 for frame in sorted({a,(a+b)//2,b}):
  scene.frame_set(frame);apply_grip();dg=bpy.context.evaluated_depsgraph_get();pts=[]
  for ob in imported+imported_props:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices]);assert np.isfinite(p).all();pts.append(p);ev.to_mesh_clear()
  poses.append(np.concatenate(pts))
 delta=max(float(np.linalg.norm(p-poses[0],axis=1).max()) for p in poses[1:]);assert delta>1e-5
 checks.append(dict(clip=clip['path'],motion=delta))
select([native]);import_anim.import_file(bpy.context,str(D/clips[0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});scene.frame_set(0);apply_grip()
for ob in bpy.data.objects:
 if ob not in imported+imported_props:ob.hide_set(True);ob.hide_render=True
for ob in imported+imported_props:ob.hide_set(False);ob.hide_render=False
native.hide_render=False;native.hide_set(True);scene.frame_start=0;scene.frame_end=int(native.animation_data.action.frame_range[1])
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'engine-da-anh.blend'),compress=True)
(O/'export-report.json').write_text(json.dumps(dict(skeleton='humanoid01d',bones=83,models=models,roundtrip_clips=checks,sampled_poses=len(checks)*3,native_animation_set='hu1d_elf_sword_and_handbow',campaign_animation='cam_hero_hu1d_elf_sword_and_handbow',source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),runtime_verified=False),indent=2),encoding='utf8');print('DA_ANH_DAGGER_HANDBOW_EXPORTED',flush=True)
