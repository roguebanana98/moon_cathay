"""Native Alchemist bind/animations on namespaced Element Bender geometry."""
import bpy,addon_utils,ast,json,subprocess,sys,re
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v33-lord-roster';D=O;P=O/'renders';P.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import materials,import_anim
import xml.etree.ElementTree as ET
converted={};missing=[];audit=[]
def material_tree(path):
 tree=ET.Element('material')
 for slot,source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',Path(path).read_text(encoding='utf8')):
  tx=ET.SubElement(tree,'texture');ET.SubElement(tx,'slot').text=slot;ET.SubElement(tx,'source').text=source
 return tree
helpers=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text().replace('ET.parse(D/matpath)','material_tree(D/matpath)'));exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws','root']],type_ignores=[]),'<preview helpers>','exec'))
paths=json.loads((O/'native-animation-paths.json').read_text());foot=[p for p in paths['hu1e_mage_female_hero'] if '/humanoid01e/shugengan/' in p];horse=[]
def choose(paths,contains):
 a=[p for p in paths if all(x in p for x in contains)];assert a,contains;return a[0]
clips=[choose(foot,['/shugengan/stand/','stand_01']),choose(foot,['/shugengan/locomotion/','walk_02']),choose(foot,['/shugengan/locomotion/','run_02']),choose(foot,['/shugengan/attacks/','attack_01'])]
casts=[p for p in foot if 'cast' in p and ('short' in p or 'long' in p)];assert casts;clips+=casts[:2]
clips=list(dict.fromkeys(clips))
ref=R/'reference/local/moonveil-animations';subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f',*[p+';'+str(ref) for p in clips]],check=True,stdout=subprocess.DEVNULL)
M=json.loads((O/'models.json').read_text());checks=[]
for m in M['models']:
 for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
 bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'));rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.animation_data_clear();meshes=[]
 for ws in m['representative']:meshes+=import_ws(ws,rig)
 for clip in clips:
  bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;rig.animation_data_clear()
  for bone in rig.pose.bones:bone.matrix_basis.identity()
  _,_,warnings=import_anim.import_file(bpy.context,str(ref/clip),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert not warnings,warnings
  first,last=map(int,rig.animation_data.action.frame_range);snap=[]
  for f in sorted({first,(first+last)//2,last}):
   bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();points=[]
   for ob in meshes:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all() and abs(p).max()<40;points.append(p)
   snap.append(np.concatenate(points))
  delta=max(float(np.max(abs(p-snap[0]))) for p in snap[1:]);assert delta>1e-6,(m['key'],clip);checks.append(dict(model=m['key'],clip=clip,samples=len(snap),motion=delta))
 rig.animation_data_clear()
 for bone in rig.pose.bones:bone.matrix_basis.identity()
 import_anim.import_file(bpy.context,str(ref/clips[0]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});rig.hide_set(True)
 scene=bpy.context.scene;scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.threads_mode='FIXED';scene.render.threads=12;scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('Moonveil studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
 for pos,power in [((3,-4,5),650),((-3,-2,3),420),((0,3,4),600)]:
  data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.size=4;ob=bpy.data.objects.new('Studio',data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('Portrait');cam=bpy.data.objects.new('Portrait',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
 for kind,z,scale,size in [('body',1.05,2.6,(512,768)),('head',1.66,.72,(512,512))]:
  cam.location=(.3,-6,z+.15);cam.rotation_euler=(Vector((0,0,z))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(P/(m['key']+'_'+kind+'.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/(m['key']+'-review.blend')),compress=True)
assert not missing,missing
(O/'model-review.json').write_text(json.dumps(dict(status='passed',models=1,samples=sum(x['samples'] for x in checks),checks=checks,missing_textures=missing,battle_animation='hu1e_mage_lord',mounted_animation=None,game_runtime_verified=False),indent=2));print('MOONVEIL_MODEL_REVIEW_PASSED',flush=True)
