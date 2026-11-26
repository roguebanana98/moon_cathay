"""Roundtrip exact shipped geometry/textures; exercise native battle/campaign clips."""
import bpy,addon_utils,sys,json,subprocess
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-generals-v20'
M=json.loads((O/'export-report.json').read_text());S=json.loads((R/'build/moon-generals-preview/animation-review-clips.json').read_text());D=R/'reference/local/wwd-all-lords';A=R/'reference/local/moon-general-runtime'
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,materials
campaign={'Assault':['animations/battle/humanoid01b/staff_and_sword/campaign/cam_hu1b_sws_stand_01.anim','animations/battle/humanoid01b/staff_and_sword/campaign/cam_hu1b_sws_run_03.anim'],'Bastion':['animations/battle/humanoid01e/celestial_general/campaign/cam_hu1e_celestial_general_stand_01.anim','animations/battle/humanoid01e/celestial_general/campaign/cam_hu1e_celestial_general_combat_run_01.anim']}
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f',*[p+';'+str(A) for group in campaign.values() for p in group]],check=True,stdout=subprocess.DEVNULL)
checks=[];renders=O/'renders';renders.mkdir(exist_ok=True)
for label,m in zip(['Assault','Bastion'],M['models']):
 bpy.ops.wm.open_mainfile(filepath=str(O/(m['key']+'-export.blend')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith(label))
 for ob in list(bpy.data.objects):
  if ob!=rig:bpy.data.objects.remove(ob,do_unlink=True)
 rig.hide_set(False);rig.data.pose_position='POSE';rig.matrix_world=Matrix.Identity(4);rig.animation_data_clear()
 meshes=[];props=[]
 for kind in ['body','weapon']:
  bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
  before=set(bpy.data.objects);bpy.ops.import_scene.rmv2(filepath=str(O/m[kind]),build_materials=False,import_all_lods=False,attach_armature=kind=='body')
  group=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert group
  for ob in group:
   ob.hide_render=False;ob.hide_set(False);pairs=[]
   for tx in ob.rmv2.textures:
    src=O/tx.path;assert src.is_file(),tx.path
    dest=O/'review-textures'/Path(tx.path).parent;dest.mkdir(parents=True,exist_ok=True)
    png=dest/(src.stem+'.png')
    if not png.exists():subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(src)],check=True,stdout=subprocess.DEVNULL)
    pairs.append((tx.type_as_int(),png.relative_to(O).as_posix()))
   mat=materials.build_material(ob.name,pairs,ob.rmv2.alpha_mode,str(O));ob.data.materials.clear();ob.data.materials.append(mat)
   if kind=='weapon':
    con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=m['attachment'];props.append(ob)
   else:assert any(mod.type=='ARMATURE' and mod.object==rig for mod in ob.modifiers)
  meshes.extend(group)
 for clip,base in [(x['path'],D) for x in S['clips'][label]]+[(x,A) for x in campaign[label]]:
  rig.animation_data_clear()
  for b in rig.pose.bones:b.matrix_basis.identity()
  bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
  import_anim.import_file(bpy.context,str(D/S['grips'][label]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
  _,_,warnings=import_anim.import_file(bpy.context,str(base/clip),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert not warnings,warnings
  first,last=map(int,rig.animation_data.action.frame_range);snapshots=[]
  for frame in sorted({first,(first+last)//2,last}):
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
   for ob in meshes:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.array([tuple(ev.matrix_world@v.co) for v in me.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all() and abs(p).max()<40;points.append(p)
   snapshots.append(np.concatenate(points))
  delta=max(float(np.max(abs(p-snapshots[0]))) for p in snapshots[1:]);assert delta>1e-6,(label,clip)
  checks.append(dict(model=m['key'],clip=clip,samples=len(snapshots),motion=delta))
 # Reset every channel before restoring the tested battle idle.
 rig.animation_data_clear()
 for b in rig.pose.bones:b.matrix_basis.identity()
 import_anim.import_file(bpy.context,str(D/S['grips'][label]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
 import_anim.import_file(bpy.context,str(D/S['clips'][label][0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
 scene=bpy.context.scene;scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.threads_mode='FIXED';scene.render.threads=12
 scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('General studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
 for pos,power in [((3,-4,5),650),((-3,-2,3),420),((0,3,4),600)]:
  data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.size=4;ob=bpy.data.objects.new('Studio',data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('Portrait');cam=bpy.data.objects.new('Portrait',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
 for kind,z,scale,size in [('body',1.05,2.8,(512,768)),('head',1.7,.85,(512,512))]:
  cam.location=(.35,-6,z+.2);cam.rotation_euler=(Vector((0,0,z))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(renders/(m['key']+'_'+kind+'.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/(m['key']+'-roundtrip.blend')),compress=True)
(O/'model-review.json').write_text(json.dumps(dict(status='passed',checks=checks,samples=sum(x['samples'] for x in checks),runtime_verified=False),indent=2));print('GENERAL_ROUNDTRIP_PASSED',flush=True)

