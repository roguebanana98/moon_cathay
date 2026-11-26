"""Separate Blender-only Zhao Yixuan/Yuan Bo sword and animation trial."""
import bpy, addon_utils, ast, json, sys, re, math, hashlib, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/zhao-yuan-bo-preview';O.mkdir(exist_ok=True)
OUT=O/'zhao-yuan-bo-sword-animation-trial.blend'
assert not OUT.exists(),'Preserve completed trial'
REF=R/'reference/local/yuan-bo-model'
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials,import_anim
sys.path.insert(0,str(R/'tools'))
from HuyenVeAnimationPreview import complete_preview_channels
converted={};missing=[];audit=[]
def material_tree(path):
    tree=ET.Element('material')
    for slot,source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',Path(path).read_text(encoding='utf8')):
        tx=ET.SubElement(tree,'texture');ET.SubElement(tx,'slot').text=slot;ET.SubElement(tx,'source').text=source
    return tree
helpers=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text().replace('ET.parse(D/matpath)','material_tree(D/matpath)'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws']],type_ignores=[]),'<preview helpers>','exec'))
bpy.ops.import_scene.tw_anim(filepath=str(REF/'animations/skeletons/humanoid01e.anim'))
rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Zhao Yixuan | Yuan Bo native humanoid01e'
rig.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis.identity();b.rotation_mode='QUATERNION'
D=R/'build/moon-v33-lord-roster'
model=json.loads((D/'models.json').read_text())['models'][0]
body=import_ws(model['representative'][0],rig)
def group(name,obs):
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
    for ob in obs:
        for old in list(ob.users_collection):old.objects.unlink(ob)
        col.objects.link(ob)
    return col
group('01 | Zhao Yixuan original body',body)
group('03 | Native humanoid01e rig',[rig])
def mesh_hash():
    return hashlib.sha256(json.dumps([(o.name,[(tuple(v.co),[(o.vertex_groups[g.group].name,g.weight) for g in v.groups]) for v in o.data.vertices]) for o in body]).encode()).hexdigest()
before=mesh_hash()
D=REF
weapon=import_ws('variantmeshes/wh_variantmodels/hu1e/cth/cth_props/cth_dragon_jade_human_sword_2h_01.wsmodel')
group('02 | Yuan Bo sword - weapon_2',weapon)
for ob in weapon:
    ob.name='Yuan Bo sword | native weapon_2'
    # RMV2 import stores the original material pivot in matrix_basis. Keep it:
    # COPY_TRANSFORMS would replace that pivot and put the blade in the palm.
    con=ob.constraints.new('CHILD_OF');con.name='Native VMD weapon_2 + original RMV2 pivot';con.target=rig;con.subtarget='weapon_2';con.inverse_matrix=Matrix.Identity(4)
assert not missing,missing
manifest=json.loads((R/'build/huyen-ve-animation-integration/animation-set-manifest.json').read_text())
paths=manifest['unique_clips']
def pick(folder,tail):
    hits=[p for p in paths if '/yuan_bo_human/'+folder+'/' in p and p.endswith(tail+'.anim')]
    assert hits,(folder,tail);return hits[0]
clips=[('01 IDLE',pick('stand','sword_stand_01')),
       ('02 WALK',pick('locomotion','sword_walk_02')),
       ('03 RUN',pick('locomotion','sword_run_02')),
       ('04 SWORD ATTACK 1',pick('attack','sword_attack_01')),
       ('05 SWORD ATTACK 2',pick('attack','sword_attack_02')),
       ('06 CAST SHORT',pick('spell_cast','sword_spell_cast_short_01')),
       ('07 CAST LONG',pick('spell_cast','sword_spell_cast_long_01'))]
scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
baked={b.name:{'location':[],'rotation_quaternion':[]} for b in rig.pose.bones}
frames=[];cursor=1;index=[];checks=[]
for label,path in clips:
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    imported,_,warnings=import_anim.import_file(bpy.context,str(REF/path),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
    assert imported==rig and not warnings,(path,warnings)
    action=rig.animation_data.action;action.name='YUAN BO | '+label;action.use_fake_user=True
    complete_preview_channels(action,rig)
    first,last=map(int,action.frame_range);start=cursor
    previous={};snaps=[]
    for frame in range(first,last+1):
        scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        for ob in weapon:
            expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix@ob.matrix_basis
            actual=ob.evaluated_get(dg).matrix_world
            assert max(abs(expected[a][b]-actual[a][b]) for a in range(4) for b in range(4))<1e-4
        if frame in {first,(first+last)//2,last}:
            vertices=[]
            for ob in body:
                ev=ob.evaluated_get(dg);me=ev.to_mesh();arr=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear()
                assert np.isfinite(arr).all() and abs(arr).max()<40;vertices.append(arr)
            snaps.append(np.concatenate(vertices))
        for bone in rig.pose.bones:
            loc,rot,scale=bone.matrix_basis.decompose();rot.normalize()
            if bone.parent is None:loc.x=0;loc.y=0 # treadmill only in the review montage
            if bone.name in previous and rot.dot(previous[bone.name])<0:rot.negate()
            previous[bone.name]=rot.copy()
            baked[bone.name]['location'].append(tuple(loc));baked[bone.name]['rotation_quaternion'].append(tuple(rot))
        frames.append(cursor);cursor+=1
    motion=max(float(np.max(abs(p-snaps[0]))) for p in snaps[1:]);assert motion>1e-6,(label,motion)
    index.append(dict(label=label,native_path=path,frames=[start,cursor-1],native_action=action.name))
    scene.timeline_markers.new(label,frame=start)
    checks.append(dict(clip=label,motion=motion,weapon_attachment_verified=True,samples=len(snaps)))
    print('YUAN_BO_CLIP_READY',label,start,cursor-1,flush=True)
rig.animation_data_clear()
montage=bpy.data.actions.new('PLAY ALL | Yuan Bo sword and casting');montage.use_fake_user=True
rig.animation_data_create();rig.animation_data.action=montage
slot=montage.slots.new(id_type='OBJECT',name=rig.name);rig.animation_data.action_slot=slot
strip=montage.layers.new('Native clips in sequence').strips.new(type='KEYFRAME');bag=strip.channelbag(slot,ensure=True)
for bone in rig.pose.bones:
    for prop,values in baked[bone.name].items():
        for axis in range(len(values[0])):
            curve=bag.fcurves.new('pose.bones["'+bone.name+'"].'+prop,index=axis)
            curve.keyframe_points.add(len(frames));coords=np.empty(len(frames)*2);coords[0::2]=frames;coords[1::2]=[v[axis] for v in values];curve.keyframe_points.foreach_set('co',coords)
            for k in curve.keyframe_points:k.interpolation='LINEAR'
            curve.update()
assert before==mesh_hash(),'Original body geometry/weights must remain unchanged'
scene.frame_start=1;scene.frame_end=cursor-1;scene.frame_set(1)
rig.hide_set(True)
scene.world=bpy.data.worlds.new('Neutral trial studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.clip_end=500
            sp.region_3d.view_location=Vector((0,0,1));sp.region_3d.view_distance=3.8
            sp.region_3d.view_rotation=Vector((-.25,8,-1.1)).to_track_quat('-Z','Y');sp.region_3d.view_perspective='ORTHO'
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.film_transparent=True
scene.render.resolution_x=700;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='Standard'
for pos,power in [((3,-4,5),650),((-3,-2,3),420),((0,3,4),600)]:
    data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.size=4;ob=bpy.data.objects.new('Studio',data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Preview camera');cam=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=3.3
cam.location=(3,-7,2.0);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(O/'zhao-yuan-bo-standing.png');bpy.ops.render.render(write_still=True)
bpy.data.texts.new('YUAN BO TRIAL - ANIMATION INDEX').write('Zhao Yixuan original body, native humanoid01e bind/weights unchanged. Original Yuan Bo sword attached at weapon_2 with zero manual offset. Press SPACE to play all seven clips; use Timeline markers for idle/walk/run/sword attacks/casting. Native actions also retained individually. Montage removes horizontal root translation for a stationary review only. Blender test only; active mod is unchanged.\n\n'+json.dumps(index,indent=2))
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),skeleton='humanoid01e',body_and_weights_unchanged=True,weapon='Native Yuan Bo sword',attachment='weapon_2',manual_weapon_offset=False,checks=checks,clips=index,frames=cursor-1,missing_textures=missing,game_modified=False,runtime_verified=False),indent=2))
print('ZHAO_YUAN_BO_PREVIEW_READY',OUT,flush=True)
