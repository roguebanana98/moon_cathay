"""Combine saved v2 reviews: one visible character per unit, native horse intact."""
import bpy,math,json,sys,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-reskin-v2';OUT=O/'moon-jade-four-unit-gallery.blend'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon'
spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_anim
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
assert not OUT.exists() or '--refine-own-preview' in __import__('sys').argv,'Preserve gallery if edited'
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene
entries=[('halberd','01 | JADE WARRIORS - HALBERDS',-3.9),('crossbow','02 | JADE CROSSBOWMEN',-1.4),('crossbow_shield','03 | JADE CROSSBOWMEN - SHIELDS',1.1),('lancers','04 | JADE LANCERS',3.8)]
mat=bpy.data.materials.new('Gallery captions');mat.use_nodes=True;s=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in s.inputs:s.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in s.inputs:s.inputs['Emission Strength'].default_value=.8
report=[]
for key,label,x in entries:
 with bpy.data.libraries.load(str(O/(key+'-review.blend')),link=False) as (src,dst):dst.objects=list(src.objects)
 loaded=[o for o in dst.objects if o];allowed=[o for o in loaded if o.type=='ARMATURE' or (o.type=='MESH' and not o.hide_render)]
 col=bpy.data.collections.new(label);scene.collection.children.link(col)
 root=bpy.data.objects.new(label+' | placement',None);col.objects.link(root);root.location.x=x
 for ob in allowed:
  col.objects.link(ob)
  if ob.type=='ARMATURE':ob.hide_set(True)
  if ob.parent not in allowed and not any(c.type=='CHILD_OF' and c.target in allowed for c in ob.constraints):
   basis=ob.matrix_basis.copy();ob.parent=root;ob.matrix_parent_inverse.identity();ob.matrix_basis=basis
 human=next(o for o in allowed if o.type=='ARMATURE' and 'hand_right' in o.pose.bones)
 if key in ['crossbow','crossbow_shield']:
  human.hide_set(False);bpy.ops.object.select_all(action='DESELECT');human.select_set(True);bpy.context.view_layer.objects.active=human;human.animation_data_clear()
  for pb in human.pose.bones:pb.matrix_basis.identity()
  path='animations/battle/humanoid01e/'+('crossbow_and_sword/stand/hu1e_crossbow_and_sword_shoot_stand_01.anim' if key=='crossbow' else 'crossbow_sword_and_shield/transition/hu1e_crossbow_sword_and_shield_stand_to_shoot_stand_01.anim')
  import_anim.import_file(bpy.context,str(R/'reference/local/moon-jade-expanded'/path),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));complete_preview_channels(human.animation_data.action,human)
  first,last=map(int,human.animation_data.action.frame_range);scene.frame_set(max(1,first) if key=='crossbow' else (max(1,first)+last)//2)
 else:scene.frame_set(1)
 bpy.context.view_layer.update()
 # This file is a static appearance gallery. Freeze the selected native poses
 # so all four units remain comparable at the same global frame.
 for rig in [o for o in allowed if o.type=='ARMATURE']:
  pose={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones};rig.animation_data_clear()
  for pb in rig.pose.bones:pb.matrix_basis=pose[pb.name]
  rig.hide_set(True)
 # Only head01 is included; the six unused head choices are omitted entirely.
 for ob in allowed:
  if ob.type=='MESH':ob.hide_set(ob.hide_render)
 cv=bpy.data.curves.new(label,'FONT');cv.body=label;cv.align_x='CENTER';cv.size=.12;cv.materials.append(mat)
 ob=bpy.data.objects.new(label,cv);scene.collection.objects.link(ob);ob.location=(x,-.7,-.24);ob.rotation_euler=(math.pi/2,0,0)
 report.append(dict(unit=key,one_visible_character=True,visible_mesh_parts=sum(o.type=='MESH' and not o.hide_render for o in allowed)))
scene.frame_set(1);bpy.context.view_layer.update()
world=bpy.data.worlds.new('Four-unit studio');world.use_nodes=True;scene.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.07,.085,.11,1);bg.inputs[1].default_value=.4
target=Vector((0,0,1.65));cd=bpy.data.cameras.new('Four units');cam=bpy.data.objects.new('Four units',cd);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(.3,-20,4);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=11.4
for name,pos,power,size in [('Key',(-4,-5,7),3000,8),('Fill',(5,-4,5),2400,8),('Rim',(0,4,7),3200,8)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();ob.hide_set(True)
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=2200;scene.render.resolution_y=1100
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_location=target;sp.region_3d.view_distance=12
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'four-unit-gallery.png');bpy.ops.render.render(write_still=True)
(O/'four-unit-gallery.json').write_text(json.dumps(dict(scene=str(OUT),units=report,game_changed=False),indent=2));print('FOUR_UNIT_GALLERY_READY',OUT,flush=True)
