"""Blender gallery of every body/head option in the installed DEER Jade reskin."""
import ast
import bpy
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from mathutils import Matrix,Vector

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/deer-jade-reskin';O=R/'build/deer-jade-reskin-gallery'
M=json.loads((O/'manifest.json').read_text())
OUT=O/'deer24-jade-warriors-reskin-gallery.blend'
assert not OUT.exists(),'Preserve existing gallery'
assert not bpy.data.filepath,'Run in a fresh background process'
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon'
spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)])
addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_anim,import_rmv2,materials
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene;converted={};warnings=[];sources={}
helper_text=(R/'tools/Build-Divine-Wing-Guard-Preview.py').read_text()
helper_text=helper_text.replace("'TRANSPARENT' if entry['role']=='wing_source' else 'OPAQUE'","'TRANSPARENT' if 'alpha_on' in (part.get('material') or '') else 'OPAQUE'")
tree=ast.parse(helper_text)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','collection','move','select_only','rig','model']],type_ignores=[]),'<native preview import helpers>','exec'))

label_mat=bpy.data.materials.new('Gallery labels');label_mat.use_nodes=True
shader=next(n for n in label_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in shader.inputs:shader.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in shader.inputs:shader.inputs['Emission Strength'].default_value=.5
def label(text,x,z,size=.10):
    curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.align_x='CENTER';curve.size=size
    ob=bpy.data.objects.new(text,curve);scene.collection.objects.link(ob);ob.location=(x,-.55,z);ob.rotation_euler=(math.pi/2,0,0);curve.materials.append(label_mat)
    return ob

rigs=[];gallery=[]
body_models=[m for m in M['models'] if m['role'] in ['body','rider_body']]
head_models=[m for m in M['models'] if m['role']=='head']
assert len(body_models)==6 and len(head_models)==7
for i,entry in enumerate(body_models):
    x=(i-2.5)*1.75
    col=collection('%02d | %s'%(i+1,Path(entry['path']).stem))
    arm=rig('humanoid01e','DEER JADE %02d | native humanoid01e'%(i+1));move(arm,col)
    obs=model(entry,arm)
    head=None
    if entry['role']=='body':
        head=head_models[i%len(head_models)];obs+=model(head,arm)
    for prop in M['props']:
        meshes=model(prop)
        for ob in meshes:
            con=ob.constraints.new('CHILD_OF');con.target=arm;con.subtarget=prop['attach'];con.inverse_matrix=Matrix.Identity(4)
        obs+=meshes
    for ob in obs:move(ob,col)
    select_only(arm)
    _,stats,issues=import_anim.import_file(bpy.context,str(D/M['idle']),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));warnings.extend(issues)
    arm.animation_data.action.name='DEER JADE %02d | native standing preview'%(i+1);arm.animation_data.action.use_fake_user=True
    arm.location.x=x;arm.hide_set(True);rigs.append(arm)
    label('%02d | %s'%(i+1,'RIDER BODY' if entry['role']=='rider_body' else 'BODY '+str(i+1)),x,-.25,.12)
    if entry['role']=='rider_body':label('standing view; no mount',x,-.43,.075)
    gallery.append(dict(number=i+1,body=entry['path'],head=head['path'] if head else None,collection=col.name))
    print('GALLERY_BODY',i+1,len(obs),flush=True)

for i,entry in enumerate(head_models):
    x=(i-3)*1.4
    col=collection('HEAD %02d | %s'%(i+1,Path(entry['path']).stem))
    arm=rig('humanoid01e','DEER HEAD %02d | native bind'%(i+1));move(arm,col)
    for ob in model(entry,arm):move(ob,col)
    arm.location=(x,0,1.05);arm.hide_set(True);rigs.append(arm)
    label('HEAD %02d'%(i+1),x,2.37,.105)

label('DEER24 | JADE WARRIORS RESKIN',0,3.80,.19)
label('Original source options | 5 infantry bodies + 1 rider body | 7 head / helmet options',0,3.52,.105)
label('SWORD + SHIELD STANDING COMPARISON | NO MOON RESKIN OR GAME CHANGES',0,-.71,.10)
scene.frame_set(1);bpy.context.view_layer.update()
scene.frame_start=1;scene.frame_end=53
world=bpy.data.worlds.new('Neutral model gallery');world.use_nodes=True;scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.07,.085,.11,1);bg.inputs[1].default_value=.4
try:scene.render.engine='CYCLES'
except TypeError:pass
if scene.render.engine=='CYCLES':scene.cycles.samples=20
scene.render.resolution_x=2200;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
assert 'PNG' in {i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items}
scene.render.image_settings.file_format='PNG'
camera_data=bpy.data.cameras.new('Gallery overview');camera=bpy.data.objects.new('Gallery overview',camera_data);scene.collection.objects.link(camera)
center=Vector((0,0,1.5));camera.location=(.25,-16,2.35);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=12.3;scene.camera=camera
for name,pos,power,size in [('Key',(-4,-5,7),2600,8),('Fill',(5,-4,4),1700,7),('Rim',(0,4,7),3000,7)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler();ob.hide_set(True)
camera.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=center;sp.region_3d.view_distance=12;sp.region_3d.view_rotation=camera.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:im.pack()
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
select_only()
note=bpy.data.texts.new('READ ME | DEER24 Jade Warriors Reskin')
note.write('Read-only source appearance gallery. Five infantry body options and one rider body, shown standing with native sword/shield for comparison; not a mounted animation test. Seven independent head/helmet options above. Bodies 01-05 pair heads01-05; source permits other combinations. Numbered options do not imply distinct face geometries. Source mesh, weights, UV, textures unchanged. Original WS material override missing for one option: embedded RMV2 material used as recorded in manifest. No reskin or game integration.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'deer24-jade-reskin-gallery.png');bpy.ops.render.render(write_still=True)
report=dict(scene=str(OUT),source=M['source'],gallery=gallery,heads=[h['path'] for h in head_models],warnings=warnings,
            packed_images=sum(bool(im.packed_file) for im in bpy.data.images),material_fallbacks=M['material_fallbacks'],
            source_geometry_sha256={m['geometry']:hashlib.sha256((D/m['geometry']).read_bytes()).hexdigest() for m in M['models']},
            game_modified=False,reskin_applied=False,source_colours_preserved=True,preview_only=True)
(O/'preview-report.json').write_text(json.dumps(report,indent=2))
print('DEER_JADE_GALLERY_READY',OUT,flush=True)
