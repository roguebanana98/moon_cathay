"""Blender-only Jade Warrior + white angel-wing appearance preview.

Run in a fresh background Blender process. No existing user scene is opened or
overwritten. The body and wings keep their respective native rigs; this is an
appearance assembly, not a completed single-skeleton game export.
"""
import bpy
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from mathutils import Matrix, Vector

R = Path(__file__).resolve().parents[1]
C = json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O = R/'build/divine-wing-guard-preview'
D = R/'reference/local/divine-wing-guard'
M = json.loads((O/'asset-manifest.json').read_text())
OUT = O/'divine-wing-guard-preview.blend'
if OUT.exists():
    assert '--rebuild-preview' in sys.argv, 'Preserve previous preview by default'

# Load the prepared local add-on in this process without installing/updating it.
addon_dir = Path(C['rpfm']).parent.parent/'rmv2-addon'
spec = importlib.util.spec_from_file_location('io_scene_rmv2', addon_dir/'__init__.py',
                                             submodule_search_locations=[str(addon_dir)])
addon = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = addon
spec.loader.exec_module(addon)
addon.register()
from io_scene_rmv2 import import_anim, import_rmv2, materials

scene = bpy.context.scene
assert not bpy.data.filepath, 'Use a fresh --factory-startup process, never an existing user file'
for ob in list(scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

converted = {}
warnings = []
sources = {}

def png(path):
    if path in converted:
        return converted[path]
    source = D/path
    assert source.is_file(),path
    destination = O/'textures'/Path(path).parent
    destination.mkdir(parents=True,exist_ok=True)
    output = destination/(source.stem+'.png')
    if not output.exists():
        subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(destination),str(source)],
                       check=True,stdout=subprocess.DEVNULL)
    converted[path] = output.relative_to(O).as_posix()
    return converted[path]

def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result

def move(ob,col):
    for parent in list(ob.users_collection):
        parent.objects.unlink(ob)
    col.objects.link(ob)

def select_only(ob=None):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=ob
    if ob: ob.select_set(True)

def rig(skeleton,name):
    select_only()
    arm,stats,issues = import_anim.import_file(bpy.context,str(D/('animations/skeletons/'+skeleton+'.anim')),
                                               dict(mode='SKELETON',attach_meshes=False,global_scale=1.0))
    warnings.extend(issues)
    arm.name=name
    arm.animation_data_clear()
    for bone in arm.pose.bones:
        bone.matrix_basis.identity()
    return arm

def model(entry,arm=None):
    select_only(arm)
    root,stats=import_rmv2.import_file(bpy.context,str(D/entry['geometry']),
                                     dict(build_materials=False,import_lods='FIRST',attach_armature=bool(arm)))
    lod=next(c for c in root.children if 'lod0' in c.name.lower())
    meshes=[o for o in lod.objects if o.type=='MESH']
    assert len(meshes)==len(entry['parts']),(entry['role'],len(meshes))
    for ob,part in zip(meshes,entry['parts']):
        pairs=[(t,png(p)) for t,p in part['textures']]
        mat=materials.build_material(part['name'],pairs,
                                      'TRANSPARENT' if entry['role']=='wing_source' else 'OPAQUE',str(O))
        ob.data.materials.clear();ob.data.materials.append(mat)
        ob['source_geometry']=entry['geometry'];ob['source_part_index']=part['index']
        ob['source_part_name']=part['name']
        sources[ob.name]=dict(source=entry['geometry'],part=part['index'],vertices=len(ob.data.vertices))
    return meshes

body_col=collection('01 | Jade Warriors - original armour')
wing_col=collection('02 | White angel wings - preview assembly')
hidden_col=collection('90 | Original angel donor - preserved hidden')
rig_col=collection('03 | Native rigs - preview only')
studio_col=collection('04 | Review studio')

body_rig=rig('humanoid01e','Divine Wing Guard | Jade Warrior native rig')
move(body_rig,rig_col)
body=[];props=[]
for role in ['body','head','sword','shield']:
    entry=next(m for m in M['models'] if m['role']==role)
    meshes=model(entry,body_rig if role in ['body','head'] else None)
    for ob in meshes:
        ob.name='Jade Warrior | '+role+' | '+ob['source_part_name']
        move(ob,body_col)
        if role in ['sword','shield']:
            con=ob.constraints.new('CHILD_OF');con.name='Native prop bone and original RMV2 pivot'
            con.target=body_rig;con.subtarget=entry['attach'];con.inverse_matrix=Matrix.Identity(4)
            props.append(ob)
        else: body.append(ob)

select_only(body_rig)
_,stats,issues=import_anim.import_file(bpy.context,str(D/M['idle']),
                                     dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0))
warnings.extend(issues)
body_rig.animation_data.action.name='JADE WARRIOR | native sword and shield stand'
body_rig.animation_data.action.use_fake_user=True
scene.frame_set(1);bpy.context.view_layer.update()

wing_rig=rig('humanoid16c','Divine Wing Guard | original angel wing rig')
move(wing_rig,rig_col)
entry=next(m for m in M['models'] if m['path'].endswith('terickz_angel_body_first_02.rigid_model_v2'))
donor=model(entry,wing_rig)
wings=[]
for ob in donor:
    move(ob,hidden_col);ob.hide_render=True;ob.hide_set(True)
    if ob['source_part_index']<2:
        continue
    copy=ob.copy();copy.data=ob.data.copy();copy.name='White Wing | '+ob['source_part_name']
    wing_col.objects.link(copy);copy.hide_render=False;copy.hide_set(False)
    copy.data.materials.clear()
    mat=ob.data.materials[0].copy();mat.name='Ivory White | '+ob['source_part_name']
    copy.data.materials.append(mat)
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    links=mat.node_tree.links
    base=shader.inputs['Base Color']
    if base.is_linked:
        source=base.links[0].from_socket
        gray=mat.node_tree.nodes.new('ShaderNodeRGBToBW')
        scale=mat.node_tree.nodes.new('ShaderNodeMath');scale.operation='MULTIPLY_ADD'
        scale.inputs[1].default_value=.3;scale.inputs[2].default_value=.65
        links.new(source,gray.inputs[0]);links.new(gray.outputs[0],scale.inputs[0]);links.new(scale.outputs[0],base)
    shader.inputs['Metallic'].default_value=0
    shader.inputs['Roughness'].default_value=.66
    copy['preview_only_white_shader']=True
    wings.append(copy)
assert len(wings)==8
hidden_col.hide_render=True;hidden_col.hide_viewport=True

# Align the donor upper-back frame to the warrior's upper back. Source weights
# and bone bindings remain on their own rig; no unsupported skeleton claim.
source_bone=wing_rig.data.bones.get('spine_2') or wing_rig.data.bones.get('spine_1')
target_bone=body_rig.pose.bones.get('spine_2') or body_rig.pose.bones.get('spine_1')
assert source_bone and target_bone
source_anchor=source_bone.head_local.copy()
target_anchor=body_rig.matrix_world@target_bone.head
wing_scale=.78
offset=Vector((0,.10,0))
wing_rig.matrix_world=Matrix.Translation(target_anchor+offset)@Matrix.Scale(wing_scale,4)@Matrix.Translation(-source_anchor)
con=wing_rig.constraints.new('CHILD_OF');con.name='Preview back attachment - separate source wing rig'
con.target=body_rig;con.subtarget=target_bone.name
con.inverse_matrix=(body_rig.matrix_world@target_bone.matrix).inverted()
scene.frame_set(1);bpy.context.view_layer.update()

def bounds(objects):
    dg=bpy.context.evaluated_depsgraph_get()
    points=[]
    for ob in objects:
        ev=ob.evaluated_get(dg);me=ev.to_mesh()
        points.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    return [min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]

bb=bounds(body+props+wings)
assert all(math.isfinite(v) for side in bb for v in side)
center=(Vector(bb[0])+Vector(bb[1]))/2
height=bb[1][2]-bb[0][2]
width=bb[1][0]-bb[0][0]

world=bpy.data.worlds.new('Neutral charcoal studio');world.use_nodes=True;scene.world=world
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs[0].default_value=(.055,.07,.09,1);background.inputs[1].default_value=.35
try:scene.render.engine='CYCLES'
except TypeError:pass
if scene.render.engine=='CYCLES':scene.cycles.samples=24
scene.render.resolution_x=1600;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
formats={i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items}
assert 'PNG' in formats
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False

camdata=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',camdata)
studio_col.objects.link(cam);camdata.type='ORTHO';scene.camera=cam
cam.location=center+Vector((3,-9,1.5));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.ortho_scale=max(height*1.35,width*1.30)
for name,relative,power,size in [('Key',(-3,-5,5),1000,4),('Fill',(4,-3,2),600,4),('Rim',(1,4,5),1400,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);studio_col.objects.link(ob);ob.location=center+Vector(relative)
    ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()

for ob in [body_rig,wing_rig]:ob.hide_set(True)
for ob in studio_col.objects:ob.hide_set(True)
select_only()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.type='MATERIAL';space.overlay.show_overlays=False
            space.region_3d.view_location=center;space.region_3d.view_distance=max(width,height)*1.5
            space.region_3d.view_rotation=cam.rotation_euler.to_quaternion();space.region_3d.view_perspective='ORTHO'
scene.frame_start=1;scene.frame_end=int(body_rig.animation_data.action.frame_range[1])
notes=bpy.data.texts.new('READ ME - Divine Wing Guard')
notes.write('Jade Warriors armour, sword and shield + white feathered wings extracted from Angels of Warhammer.\n'
            'Appearance preview ONLY. Separate native body and wing rigs; not a final retargeted game skeleton.\n'
            'Original donor retained hidden. White tint is reversible shader only. No game integration or pack export.\n')
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        assert Path(bpy.path.abspath(image.filepath)).is_file(),image.filepath
        image.pack()
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
scene['preview_only']=True;scene['game_integrated']=False
scene['unit_name']='Divine Wing Guard'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
scene.render.filepath=str(O/'divine-wing-guard-front.png')
bpy.ops.render.render(write_still=True)
cam.location=center+Vector((-3,9,1.4))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(O/'divine-wing-guard-back.png')
bpy.ops.render.render(write_still=True)
report=dict(scene=str(OUT),blender_version=bpy.app.version_string,name='Divine Wing Guard',
            body_source='Jade Warriors body/head/sword/shield 01',wing_source=entry['geometry'],
            wing_part_indices=[o['source_part_index'] for o in wings],wing_scale=wing_scale,
            white_shader_only=True,separate_native_rigs=True,game_ready_rig=False,
            source_bone=source_bone.name,target_bone=target_bone.name,bounds=bb,
            body_parts=len(body),prop_parts=len(props),wing_parts=len(wings),warnings=warnings,
            packed_images=sum(bool(im.packed_file) for im in bpy.data.images),
            missing_images=[im.name for im in bpy.data.images if im.source=='FILE'
                            and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file()],
            game_modified=False,pack_exported=False,sources=sources)
report['source_asset_sha256']={m['geometry']:hashlib.sha256((D/m['geometry']).read_bytes()).hexdigest()
                               for m in M['models']}
(O/'preview-report.json').write_text(json.dumps(report,indent=2))
print('DIVINE_WING_GUARD_PREVIEW_READY',str(OUT),flush=True)
