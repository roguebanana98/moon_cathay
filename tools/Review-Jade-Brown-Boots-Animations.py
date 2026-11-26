"""Brown shoe caps and native sword/shield animation montage for user review."""
import bpy,json,math,sys,importlib.util,subprocess
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-animation-review';O.mkdir(parents=True,exist_ok=True)
D=R/'reference/local/divine-wing-guard';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
OUT=O/'jade-warrior-brown-boots-animation-review.blend';assert not OUT.exists()
base='animations/battle/humanoid01e/sword_shield/'
clips=[('01 IDLE','stand/hu1e_sword_and_shield_stand_01.anim',120),('02 WALK','locomotion/hu1e_sword_shield_walk_01.anim',120),('03 RUN','locomotion/hu1e_sword_shield_run_01.anim',120),('04 CHARGE','locomotion/hu1e_sword_shield_charge_01.anim',90),('05 ATTACK A','attack/hu1e_sword_shield_attack_01.anim',0),('06 ATTACK B','attack/hu1e_sword_shield_attack_02.anim',0),('07 JUMP ATTACK','attack/hu1e_sword_shield_jump_attack_01.anim',0),('08 DEFEND','defend/hu1e_sword_shield_defend_front_01.anim',0)]
ix=json.loads((D/'indexes/anim2.json').read_text())['paths'];game=Path(json.loads((R/'build/divine-wing-guard-preview/asset-manifest.json').read_text())['game'])
paths=[base+p for _,p,_ in clips];assert all(p in ix for p in paths)
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(game/'data/anim2.pack'),'-f',*[ix[p]+';'+str(D) for p in paths]],check=True,stdout=subprocess.DEVNULL)
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_anim
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-normal-boots/jade-model05-normal-boot-toes.blend'))
scene=bpy.context.scene
for col in bpy.data.collections:
 if col.name.startswith('COMPARE |'):col.hide_render=True;col.hide_viewport=True
body=next(o for o in scene.objects if o.type=='MESH' and o.get('source_geometry','').endswith('beitingsheshou5.rigid_model_v2') and o.get('source_part_index')==0)
arm=next(o for o in scene.objects if o.type=='ARMATURE')
# Vertex attribute is attached to the edited shoe geometry and follows animation.
attr=body.data.attributes.new('BrownBootToe','FLOAT','POINT')
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
painted=0
for v in body.data.vertices:
 x,y,z=v.co;forward=(abs(x)-.1)*.28-(y-.04)*.96
 value=smooth((forward-.015)/.04)*(1-smooth((z-.105)/.055)) if z<.16 else 0
 attr.data[v.index].value=value
 if value>.5:painted+=1
for i,mat in enumerate(body.data.materials):
 if mat is None:continue
 mat=mat.copy();body.data.materials[i]=mat;tree=mat.node_tree;s=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED');old=s.inputs['Base Color'].links[0].from_socket
 mask=tree.nodes.new('ShaderNodeAttribute');mask.attribute_name='BrownBootToe'
 tex=tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=90;tex.inputs['Detail'].default_value=2
 ramp=tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.040,.025,.018,1);ramp.color_ramp.elements[1].color=(.095,.066,.049,1);tree.links.new(tex.outputs['Fac'],ramp.inputs[0])
 mix=tree.nodes.new('ShaderNodeMixRGB');tree.links.new(mask.outputs['Fac'],mix.inputs[0]);tree.links.new(old,mix.inputs[1]);tree.links.new(ramp.outputs[0],mix.inputs[2]);tree.links.new(mix.outputs[0],s.inputs['Base Color'])
 # Shoe paint becomes brown leather rather than reflective white trim.
 for name,value in [('Metallic',0),('Roughness',.65)]:
  socket=s.inputs[name]
  if socket.is_linked:
   prior=socket.links[0].from_socket;blend=tree.nodes.new('ShaderNodeMixRGB');tree.links.new(mask.outputs['Fac'],blend.inputs[0]);tree.links.new(prior,blend.inputs[1]);blend.inputs[2].default_value=(value,value,value,1);tree.links.new(blend.outputs[0],socket)
warnings=[];segments=[];samples=[];cursor=1
data={p.name:{'location':[],'rotation_quaternion':[],'scale':[]} for p in arm.pose.bones}
for label,path,duration in clips:
 arm.hide_set(False);bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm;arm.animation_data_clear()
 for pb in arm.pose.bones:pb.rotation_mode='QUATERNION';pb.matrix_basis.identity()
 _,stats,issues=import_anim.import_file(bpy.context,str(D/(base+path)),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));warnings.extend(issues)
 action=arm.animation_data.action;complete_preview_channels(action,arm);action.name='NATIVE JADE | '+label;action.use_fake_user=True
 first,last=map(int,action.frame_range);first=max(1,first);frames=[]
 for f in range(first,last+1):
  scene.frame_set(f);bpy.context.view_layer.update()
  # Remove translation across the stage in armature space, retain vertical motion.
  for pb in arm.pose.bones:
   if pb.parent is None:
    pose=pb.matrix.copy();pose.translation.x=0;pose.translation.y=0;pb.matrix_basis=pb.bone.matrix_local.inverted()@pose
  frames.append({p.name:{prop:tuple(getattr(p,prop)) for prop in ['location','rotation_quaternion','scale']} for p in arm.pose.bones})
 arm.animation_data_clear();n=duration or len(frames)
 segments.append(dict(label=label,start=cursor,end=cursor+n-1,native_frames=len(frames),source=base+path))
 for i in range(n):
  pose=frames[i%len(frames)]
  for name,channels in data.items():
   for prop in channels:channels[prop].append(pose[name][prop])
 cursor+=n;print('JADE_CLIP_SAMPLED',label,len(frames),flush=True)
arm.animation_data_clear();action,curves=import_anim._new_action_fcurves(arm,'JADE WARRIOR | eight native animation stages');action.use_fake_user=True
frame_numbers=list(range(1,cursor))
for name,channels in data.items():
 previous=None
 for i,raw in enumerate(channels['rotation_quaternion']):
  q=Quaternion(raw)
  if previous is not None and q.dot(previous)<0:q.negate()
  channels['rotation_quaternion'][i]=tuple(q);previous=q
 for prop,values in channels.items():import_anim._fill_fcurves(curves,arm.pose.bones[name].path_from_id(prop),4 if prop=='rotation_quaternion' else 3,values,frame_numbers,name)
for fc in curves:
 for point in fc.keyframe_points:point.interpolation='LINEAR'
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for seg in segments:scene.timeline_markers.new(seg['label'],frame=seg['start'])
scene.frame_start=1;scene.frame_end=cursor-1;scene.render.fps=30
if 'FRAME_DROP' in {i.identifier for i in scene.bl_rna.properties['sync_mode'].enum_items}:scene.sync_mode='FRAME_DROP'
# Verify mesh evaluation and native prop transforms at representative frames.
visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
for seg in segments:
 for f in sorted({seg['start'],(seg['start']+seg['end'])//2,seg['end']}):
  scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for ob in visible:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();assert all(math.isfinite(c) for v in me.vertices for c in v.co),(ob.name,f);ev.to_mesh_clear()
  samples.append(f)
cam=scene.camera;target=Vector((0,0,1.05));cam.location=(2.6,-7,2.25);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.9
scene.render.resolution_x=1200;scene.render.resolution_y=1200
captionmat=bpy.data.materials.new('Animation captions');captionmat.use_nodes=True;s=next(n for n in captionmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in s.inputs:s.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in s.inputs:s.inputs['Emission Strength'].default_value=1
for seg in segments:
 cv=bpy.data.curves.new(seg['label'],'FONT');cv.body=seg['label'];cv.align_x='CENTER';cv.size=.09;cv.materials.append(captionmat);ob=bpy.data.objects.new(seg['label'],cv);scene.collection.objects.link(ob);ob.parent=cam;ob.location=(0,-1.25,-2)
 for f,scale in [(0,0),(seg['start'],1),(seg['end']+1,0)]:ob.scale=(scale,)*3;ob.keyframe_insert(data_path='scale',frame=f)
 for layer in ob.animation_data.action.layers:
  for strip in layer.strips:
   bag=strip.channelbag(ob.animation_data.action_slot)
   if bag:
    for fc in bag.fcurves:
     for pt in fc.keyframe_points:pt.interpolation='CONSTANT'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.region_3d.view_perspective='CAMERA'
arm.hide_set(True);scene.frame_set(1);bpy.context.view_layer.update()
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
note=bpy.data.texts.new('REVIEW | Jade Warrior animations');note.write('Space: pause/resume. Native humanoid01e sword/shield clips, stationary Blender montage, no game export. Inspect long handle, new blade, round shield, neckguard and flattened shoes for clipping. Numerical finite checks do not prove absence of visual clipping.\n'+json.dumps(segments,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
for label,f in [('idle',1),('walk',segments[1]['start']+15),('attack',segments[4]['start']+10)]:
 scene.frame_set(f);scene.render.filepath=str(O/('review-'+label+'.png'));bpy.ops.render.render(write_still=True)
scene.frame_set(1);target=Vector((0,0,.15));cam.location=(.75,-1.7,.43);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.65;scene.render.resolution_y=800;scene.render.filepath=str(O/'brown-boots-detail.png');bpy.ops.render.render(write_still=True)
(O/'review-report.json').write_text(json.dumps(dict(scene=str(OUT),segments=segments,painted_vertices=painted,sampled_frames=samples,warnings=warnings,game_integrated=False,runtime_verified=False),indent=2))
print('JADE_ANIMATION_REVIEW_READY',cursor-1,flush=True)
