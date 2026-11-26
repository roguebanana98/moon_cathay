"""Export the approved Moon Jade appearance without modifying its Blender source."""
import bpy,bmesh,sys,json,math,hashlib,importlib.util,subprocess
import numpy as np
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-jade-reskin-v1';O.mkdir(parents=True,exist_ok=True)
SOURCE=R/'build/moon-jade-approved-variants/moon-jade-warriors-approved-seven-variants-v2.blend'
if not SOURCE.exists():SOURCE=R/'assets/working/moon-jade-warriors/moon-jade-warriors-working.blend'
BASE='variantmeshes/wh_variantmodels/mc_moon_jade_reskin';G=O/BASE;T=G/'tex';TMP=O/'bake';T.mkdir(parents=True,exist_ok=True);TMP.mkdir(exist_ok=True)
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import rmv2_format as rf,export_rmv2
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1;scene.render.bake.margin=8
scene.render.threads_mode='FIXED';scene.render.threads=8
report=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),models=[],textures={},warnings=[])
cols=[bpy.data.collections['VARIANT %02d | approved body05 + DEER head%02d'%(i,i)] for i in range(1,8)]
rig=next(o for o in cols[0].objects if o.type=='ARMATURE');rig.animation_data_clear();rig.location=(0,0,0);rig.data.pose_position='REST'
for pb in rig.pose.bones:pb.matrix_basis.identity()
base=[o for o in cols[0].objects if o.type=='MESH'];groups=[]
body=[o for o in base if any(m.type=='ARMATURE' for m in o.modifiers) and 'beitingsheshouh1.rigid_model_v2' not in o.get('source_geometry','')]
groups.append(('body',body,True))
for i,col in enumerate(cols,1):groups.append(('head_%02d'%i,[o for o in col.objects if o.type=='MESH' and 'beitingsheshouh%d.rigid_model_v2'%i in o.get('source_geometry','')],True))
groups.extend([('dao',[next(o for o in base if 'reference ring-pommel dao' in o.name)],False),('shield',[next(o for o in base if 'shield' in o.get('source_geometry',''))],False)])
assert len(body)==7,(len(body),[o.name for o in body])
for ob in scene.objects:
 if ob.type=='MESH':ob.hide_render=True
def select(obs):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.hide_set(False);ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
def dds(image,kind,stem):
 path=T/(stem+'.dds')
 if not path.exists():
  image.filepath_raw=str(TMP/(stem+'.png'));image.file_format='PNG';image.save()
  subprocess.run([C['texconv'],'-nologo','-y','-m','0',*(['-srgbi'] if kind==27 else []),'-f','BC7_UNORM_SRGB' if kind==27 else 'BC3_UNORM' if kind==1 else 'BC7_UNORM','-o',str(T),image.filepath_raw],check=True,stdout=subprocess.DEVNULL)
 key=BASE+'/tex/'+path.name;report['textures'][key]=hashlib.sha256(path.read_bytes()).hexdigest();return key
def constant(name,color):
 image=bpy.data.images.new(name,width=4,height=4,alpha=True);image.colorspace_settings.name='Non-Color';image.generated_color=color;image.pixels.foreach_set(np.array(list(color)*16,dtype=np.float32));image.update();image.pack()
 return image
def bake(ob,stem,kind):
 targetpath=T/(stem+'.dds')
 if targetpath.exists():report['textures'][BASE+'/tex/'+targetpath.name]=hashlib.sha256(targetpath.read_bytes()).hexdigest();return BASE+'/tex/'+targetpath.name
 nt=ob.data.materials[0].node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
 previous=out.inputs['Surface'].links[0].from_socket;emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(emit.outputs[0],out.inputs['Surface'])
 size=1024 if kind==27 else 512
 im=bpy.data.images.new(stem,width=size,height=size,alpha=True);im.colorspace_settings.name='sRGB' if kind==27 else 'Non-Color'
 target=nt.nodes.new('ShaderNodeTexImage');target.image=im
 for n in nt.nodes:n.select=False
 target.select=True;nt.nodes.active=target;select([ob])
 comb=None
 if kind==27:
  socket=bs.inputs['Base Color']
  if socket.is_linked:nt.links.new(socket.links[0].from_socket,emit.inputs['Color'])
  else:emit.inputs['Color'].default_value=socket.default_value
 else:
  comb=nt.nodes.new('ShaderNodeCombineXYZ')
  for i,key in enumerate(['Metallic','Roughness']):
   socket=bs.inputs[key]
   if socket.is_linked:nt.links.new(socket.links[0].from_socket,comb.inputs[i])
   else:comb.inputs[i].default_value=socket.default_value
  nt.links.new(comb.outputs[0],emit.inputs['Color'])
 bpy.ops.object.bake(type='EMIT',use_clear=True)
 if kind==27 and bs.inputs['Alpha'].is_linked:
  pixels=np.empty(size*size*4,dtype=np.float32);im.pixels.foreach_get(pixels)
  alpha=bpy.data.images.new(stem+'_alpha',width=size,height=size,alpha=True);alpha.colorspace_settings.name='Non-Color';target.image=alpha
  nt.links.new(bs.inputs['Alpha'].links[0].from_socket,emit.inputs['Color']);bpy.ops.object.bake(type='EMIT',use_clear=True)
  ap=np.empty_like(pixels);alpha.pixels.foreach_get(ap);pixels[3::4]=ap[0::4];im.pixels.foreach_set(pixels);im.update();bpy.data.images.remove(alpha)
 result=dds(im,kind,stem);nt.links.new(previous,out.inputs['Surface']);nt.nodes.remove(emit);nt.nodes.remove(target)
 if comb:nt.nodes.remove(comb)
 return result
export_obs=[]
for group,sources,weighted in groups:
 assert sources,group
 obs=[];rows=[]
 for source in sources:
  for mi in sorted({p.material_index for p in source.data.polygons}):
   ob=source.copy();ob.data=source.data.copy();scene.collection.objects.link(ob);ob.hide_set(False);ob.hide_render=False
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=mi],context='FACES');loose=[v for v in bm.verts if not v.link_faces]
   if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
   bm.to_mesh(ob.data);bm.free();mat=source.data.materials[mi].copy();ob.data.materials.clear();ob.data.materials.append(mat)
   for p in ob.data.polygons:p.material_index=0
   ob.parent=None;ob.constraints.clear();ob.matrix_world=Matrix.Identity(4) if weighted else source.matrix_basis.copy()
   for mod in list(ob.modifiers):
    if mod.type=='ARMATURE':mod.object=rig
    elif not weighted:ob.modifiers.remove(mod)
   if not ob.data.uv_layers:
    select([ob]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
   # Existing tiled UVs are translated per polygon to the base tile.
   uv=ob.data.uv_layers.active
   for p in ob.data.polygons:
    uvs=[uv.data[i].uv for i in p.loop_indices];sx=math.floor(sum(v.x for v in uvs)/len(uvs));sy=math.floor(sum(v.y for v in uvs)/len(uvs))
    for v in uvs:v.x-=sx;v.y-=sy
   stem=group+'_p%02d'%len(rows);ob.name=stem
   bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');alpha=bs.inputs['Alpha'].is_linked
   paths={27:bake(ob,stem+'_base_colour',27),29:bake(ob,stem+'_material_map',29)}
   # Keep source packed orange normal maps where present. The shield face
   # suppressed its old emblem relief, so bake its evaluated normal separately.
   normal=next((n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and '_normal' in n.image.filepath.lower()),None)
   if group=='shield':
    nt=mat.node_tree;target=nt.nodes.new('ShaderNodeTexImage');im=bpy.data.images.new(stem+'_tangent_normal',width=1024,height=1024,alpha=True);im.colorspace_settings.name='Non-Color';target.image=im
    for n in nt.nodes:n.select=False
    target.select=True;nt.nodes.active=target;select([ob]);bpy.ops.object.bake(type='NORMAL',use_clear=True)
    pixels=np.empty(1024*1024*4,dtype=np.float32);im.pixels.foreach_get(pixels);x=2*pixels[0::4]-1;y=2*pixels[1::4]-1
    pixels[0::4]=1;pixels[1::4]=(1-y)/2;pixels[2::4]=0;pixels[3::4]=np.clip((x+1)/2,0,1);im.pixels.foreach_set(pixels);im.update();normal=im;nt.nodes.remove(target)
   paths[1]=dds(normal or constant('Flat orange normal',(1,.5,0,.5)),1,stem+'_normal')
   ob.rmv2.vertex_format='CINEMATIC' if weighted else 'STATIC';ob.rmv2.material_id='AUTO';ob.rmv2.alpha_mode='TRANSPARENT' if alpha else 'OPAQUE';ob.rmv2.textures.clear()
   for typ,path in sorted(paths.items()):tx=ob.rmv2.textures.add();tx.set_type_from_int(typ);tx.path=path
   ob.rmv2.textures_initialized=True;obs.append(ob);rows.append(dict(name=ob.name,source=source.name,textures=paths,alpha=alpha,pivot=list(ob.matrix_world.translation)))
 select(obs);path=G/(group+'.rigid_model_v2');stats,warnings=export_rmv2.export_file(bpy.context,str(path),dict(source='SELECTED',skeleton_name='humanoid01e' if weighted else '',auto_lods=True,auto_lod_count=4,apply_modifiers=True,version=8));report['warnings'].extend(warnings)
 model=rf.load(path.read_bytes());assert len(model.lods)==4
 counts=[]
 for lod in model.lods:
  counts.append(sum(len(p.mesh.indices)//3 for p in lod.models))
  for part in lod.models:
   assert np.isfinite(part.mesh.positions).all()
   if weighted:assert part.mesh.bone_indices.max()<len(rig.data.bones) and abs(part.mesh.bone_weights.sum(axis=1)-1).max()<.03
 report['models'].append(dict(key=group,path=BASE+'/'+path.name,weighted=weighted,skeleton=model.skeleton_name,lod_triangles=counts,parts=rows));export_obs.extend(obs)
 for ob in obs:ob.hide_render=True
 (O/'export-report.json').write_text(json.dumps(report,indent=2));print('EXPORTED_MOON_JADE',group,counts,flush=True)
for ob in scene.objects:
 if ob.type=='MESH' and ob not in export_obs:ob.hide_set(True);ob.hide_render=True
rig.hide_set(True);select(export_obs);bpy.ops.wm.save_as_mainfile(filepath=str(O/'moon-jade-export-checkpoint.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==report['source_sha256']
print('MOON_JADE_EXPORT_COMPLETE',flush=True)
