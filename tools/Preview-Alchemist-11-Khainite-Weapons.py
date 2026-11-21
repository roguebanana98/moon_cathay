"""Attach native Khainite dagger/handbow to a copy of current Alchemist 11."""
import bpy,addon_utils,sys,json,subprocess,ast,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/alchemist-11-khainite-weapons';D=R/'reference/local/khainite-weapons'
OUT=O/'alchemist-11-khainite-dagger-and-handbow-v3.blend';assert not OUT.exists()
# Opening the whole snapshot is essential: append() drops per-view-layer hide
# flags, including the user's hidden head parts and other comparison variants.
bpy.ops.wm.open_mainfile(filepath=str(O/'before-weapons-live.blend'))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='CONSOLE':area.type='VIEW_3D'
layout=O/'snapshot-3d-layout.blend';assert not layout.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(layout),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(layout))
root=bpy.data.objects['VARIANT 11'];original=set(root.children_recursive)|{root}
rig=next(o for o in original if o.type=='ARMATURE')
def fingerprint(ob):
    return hashlib.sha256(b''.join(__import__('struct').pack('<3f',*v.co) for v in ob.data.vertices)).hexdigest()
before={o.name:fingerprint(o) for o in original if o.type=='MESH'}
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import materials
converted={};missing=[];audit=[]
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'<prop importer>','exec'))
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/humanoid01d.anim'))
donor=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');donor.name='REFERENCE Khainite prop attachment frames'
donor.animation_data_clear()
for bone in donor.pose.bones:bone.matrix_basis.identity()
# Prop bones have placeholder origins in the skeleton-only bind. Resolve their
# real grip transforms from a native standing clip, without posing the target.
bpy.context.view_layer.objects.active=donor;donor.select_set(True)
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/battle/humanoid01d/sword_and_handbow/stand/hu1d_def_swha_stand_01.anim'))
bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
props=[];attachments=[]
base='variantmeshes/wh_variantmodels/hu1d/def/def_props/'
for label,ws,prop in [('Khainite dagger 01',base+'def_khanite_assassin_dagger_01.wsmodel','be_prop_1'),
                      ('Khainite handbow',base+'def_assassin_bow_1h_01_rigid.wsmodel','be_prop_5')]:
    source_bone=donor.pose.bones[prop]
    # Compare the actual hand frames, rather than assuming that differently named
    # Elf and Cathay weapon bones share the same bind transform.
    ancestor=min((donor.pose.bones[n] for n in ['hand_left','hand_right']),
        key=lambda b:(b.matrix.translation-source_bone.matrix.translation).length)
    hand=ancestor.name;assert hand in rig.pose.bones
    relative=ancestor.matrix.inverted()@source_bone.matrix
    assert relative.translation.length<.3,(label,hand,list(relative.translation))
    anchor=bpy.data.objects.new(label+' | '+hand,None);bpy.context.scene.collection.objects.link(anchor)
    con=anchor.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=hand
    meshes=import_ws(ws)
    for ob in meshes:
        local=ob.matrix_world.copy();ob.parent=anchor;ob.matrix_local=relative@local
        ob.name=label;ob['attachment_source_bone']=prop;ob['attachment_target_hand']=hand
        ob.hide_set(False);ob.hide_render=False
    props.extend(meshes)
    attachments.append(dict(weapon=label,source_prop=prop,target_hand=hand,relative_matrix=[list(r) for r in relative]))
donor.hide_set(True);donor.hide_render=True
assert not missing,missing
assert before=={o.name:fingerprint(o) for o in original if o.type=='MESH'}
scene=bpy.context.scene;target=Vector((0,0,1.1))
camdata=bpy.data.cameras.new('Weapon fitting camera');cam=bpy.data.objects.new('Weapon fitting camera',camdata);scene.collection.objects.link(cam)
cam.location=(.5,-5,1.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=3;scene.camera=cam;cam.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=3.7
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
for im in bpy.data.images:
    if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.update()
notes=bpy.data.texts.new('KHAINITE WEAPON PREVIEW');notes.write('Current live model-11 snapshot preserved. Native Khainite dagger variant 01 and native handbow attached using donor prop-to-hand bind offsets and target humanoid01e hand constraints. Static fitting only; no animation retarget or game export. No body geometry, materials or pose changes.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
(O/'weapon-fit.json').write_text(json.dumps(dict(scene=str(OUT),source_snapshot=str(O/'before-weapons-live.blend'),attachments=attachments,body_geometry_sha256=before,body_geometry_unchanged=True,body_materials_unchanged=True,body_pose_unchanged=True,animation_retargeted=False,game_modified=False),indent=2))
print('WEAPON_PREVIEW_READY',str(OUT),flush=True)
