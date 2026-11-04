import bpy,addon_utils,json,sys,math,hashlib,struct,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
import numpy as np
R=Path(__file__).resolve().parent;D=R/'reference';BASE='variantmeshes/wh_variantmodels/hu1/emp/'
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,import_rmv2,materials,skeleton
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1500;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Neutral studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.22,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
rig,_,warnings=import_anim.import_file(bpy.context,str(D/'animations/skeletons/humanoid01.anim'),{'mode':'SKELETON'})
rig.name='GENERAL_humanoid01__Karl_MM_TEST';rig.show_in_front=True
native_bones=skeleton.bone_name_by_index(rig)
rig['source']='General of the Empire on foot: hu1_empire_sword_and_shield / humanoid01'

def select(o):
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
def load_model(stem,prefix,target=None):
    ws=D/(BASE+stem+'.wsmodel');mapping={int(e.attrib['part_index']):e.text.strip().replace('\\','/').lower() for e in ET.parse(ws).findall('.//material') if e.attrib.get('lod_index')=='0'}
    select(target) if target else bpy.ops.object.select_all(action='DESELECT')
    if not target:bpy.context.view_layer.objects.active=None
    original=import_rmv2._build_mesh_object;counter=[0];created=[]
    def build(model,version,name,scale,bone_names,options):
        i=counter[0];counter[0]+=1
        o=original(model,version,name,scale,bone_names,{**options,'build_materials':False})
        o.name=f'{prefix}_{i:02d}';o['native_part']=i;o['source_wsmodel']=str(ws)
        xmlpath=D/mapping[i];xml=ET.parse(xmlpath)
        types={'t_xml_base_colour':27,'t_xml_normal':1,'t_xml_material_map':29,'t_xml_mask':3}
        tx=[]
        for t in xml.findall('.//texture'):
            slot=t.findtext('slot');p=t.findtext('source','').strip().replace('\\','/').lower()
            if slot in types and (D/p).is_file():tx.append((types[slot],p))
        alpha='TRANSPARENT' if 'alpha_on' in str(xmlpath).lower() else 'OPAQUE'
        mat=materials.build_material(prefix+' | '+xmlpath.stem,tx,alpha,str(D));o.data.materials.append(mat)
        o['source_material']=mapping[i];o.rmv2.alpha_mode=alpha
        created.append(o);return o
    import_rmv2._build_mesh_object=build
    try:root,stats=import_rmv2.import_file(bpy.context,str(D/(BASE+stem+'.rigid_model_v2')),{'import_lods':'FIRST','attach_armature':target is not None,'texture_root':str(D),'build_materials':False})
    finally:import_rmv2._build_mesh_object=original
    root.name=prefix+' | LOD0';return root,created

body_col,body=load_model('emp_karl_franz/emp_karl_franz','MM_KARL',rig)
assert all(all(g.name in rig.data.bones for g in o.vertex_groups) for o in body),'Unmapped vertex groups'
unweighted={o.name:sum(not any(g.weight>0 for g in v.groups) for v in o.data.vertices) for o in body}
assert not any(unweighted.values()),unweighted
def meshhash(o):return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest()
before={o.name:meshhash(o) for o in body}
def add_prop(stem,name,bone):
    col,objs=load_model('emp_props/'+stem,name)
    for o in objs:
        assert not any(m.type=='ARMATURE' for m in o.modifiers)
        con=o.constraints.new('CHILD_OF');con.name='Native VMD attachment | '+bone;con.target=rig;con.subtarget=bone
        # Importer cosmetically reorients Blender bones; remove that only for rigid props.
        con.inverse_matrix=skeleton.bone_fix_quaternion(rig.data.bones[bone]).to_matrix().to_4x4().inverted()
        o['native_attachment']=bone
    return objs
sword=add_prop('emp_general_sword_1h_01','GENERAL_SWORD','be_prop_1')
shield=add_prop('emp_general_shield_01','GENERAL_SHIELD','be_prop_2')

def complete_channels(action):
    slot=action.slots[0];bag=action.layers[0].strips[0].channelbag(slot,ensure=True);curves=bag.fcurves
    existing={(f.data_path,f.array_index) for f in curves}
    for b in rig.pose.bones:
        for prop,values in [('location',(0,0,0)),('rotation_quaternion',(1,0,0,0))]:
            path=f'pose.bones["{b.name}"].{prop}'
            for i,value in enumerate(values):
                if (path,i) not in existing:
                    fc=curves.new(path,index=i);fc.keyframe_points.insert(0,value,options={'FAST'})

manifest=json.loads((R/'reference_manifest.json').read_text())
wanted=['STAND','STAND_NO_WEAPON_IDLE_1','WALK_1','RUN_2','ATTACK_1','ATTACK_2','ATTACK_3','COMBAT_IDLE_1']
clips=[];paths=set()
for slot in wanted:
    found=next((c for c in manifest['clips'] if c['slot']==slot),None)
    if found and found['path'] not in paths:clips.append(found);paths.add(found['path'])
checks=[];actions=[]
for idx,clip in enumerate(clips):
    select(rig)
    _,stats,warns=import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':True})
    action=rig.animation_data.action;action.name=f'GENERAL_{idx+1:02d}_{clip["slot"]}';action.use_fake_user=True
    action['native_path']=clip['path'];action['slot']=clip['slot'];complete_channels(action)
    first,last=map(int,action.frame_range);sampled=sorted(set(int(t) for t in np.linspace(first,last,9)))
    bounds=[];pose_matrices=[];max_attachment_error=0
    for frame in sampled:
        scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        coords=[]
        for o in body:
            evaluated=o.evaluated_get(dg);me=evaluated.to_mesh()
            xyz=np.array([list(evaluated.matrix_world@v.co) for v in me.vertices]);assert np.isfinite(xyz).all()
            coords.append(xyz);evaluated.to_mesh_clear()
        xyz=np.concatenate(coords);dim=xyz.max(0)-xyz.min(0);assert max(dim)<6,(clip,frame,dim)
        bounds.append({'frame':frame,'min':xyz.min(0).tolist(),'max':xyz.max(0).tolist()})
        pose_matrices.append([list(rig.pose.bones['hand_right'].matrix.translation),list(rig.pose.bones['hand_left'].matrix.translation)])
        for prop in sword+shield:
            bone=prop['native_attachment'];fix=skeleton.bone_fix_quaternion(rig.data.bones[bone]).to_matrix().to_4x4()
            expected=rig.matrix_world@rig.pose.bones[bone].matrix@fix.inverted()@prop.matrix_basis
            actual=prop.evaluated_get(dg).matrix_world
            err=max(abs(expected[a][b]-actual[a][b]) for a in range(4) for b in range(4));max_attachment_error=max(err,max_attachment_error)
            assert err<1e-4,(prop.name,frame,err)
    checks.append({'action':action.name,**clip,'frames':[first,last],'samples':bounds,'max_prop_attachment_error':max_attachment_error,'moving_hands':pose_matrices[0]!=pose_matrices[len(pose_matrices)//2],'warnings':warns})
    actions.append(action);print('CLIP_TESTED',action.name,len(sampled),flush=True)
assert before=={o.name:meshhash(o) for o in body},'Unexpected source mesh edit'
# Continuous NLA playlist with labelled clips for the user's Spacebar playback.
rig.animation_data.action=None
track=rig.animation_data.nla_tracks.new();track.name='GENERAL | idle walk run attacks'
cursor=1
for action in actions:
    start,end=action.frame_range;strip=track.strips.new(action.name,cursor,action)
    strip.action_frame_start=start;strip.action_frame_end=end;strip.blend_type='REPLACE';strip.extrapolation='NOTHING'
    scene.timeline_markers.new(action.name,frame=cursor)
    cursor=int(strip.frame_end)+1
scene.frame_start=1;scene.frame_end=cursor-1;scene.frame_set(1)
rig['preview_usage']='Space: play sequence. Timeline markers label each General action. All parts retain mod weights.'

stage=bpy.data.collections.new('STUDIO | preview only');scene.collection.children.link(stage)
def move_stage(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    stage.objects.link(o)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((3,-4,5),700,4),((-3,-2,3),500,3),((0,3,4),900,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1));move_stage(o)
bpy.ops.object.camera_add(location=(3,-7,2.5));cam=bpy.context.object;cam.name='CAM | full character';cam.data.type='ORTHO';cam.data.ortho_scale=3.2;aim(cam,(0,0,1.15));move_stage(cam);scene.camera=cam
scene.view_settings.view_transform='AgX'
for im in bpy.data.images:
    if im.source=='FILE' and im.has_data:im.pack()
select(rig)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.shading.type='MATERIAL';s.overlay.show_extras=False;s.overlay.show_floor=False
            s.region_3d.view_location=(0,0,1.1);s.region_3d.view_distance=4.1
            s.region_3d.view_rotation=cam.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
            s.clip_end=200
        if area.type=='DOPESHEET_EDITOR':area.spaces.active.show_region_ui=False
readme=bpy.data.texts.new('READ ME | Karl MM + Empire General test')
readme.write('Source: installed Karl Franz Reskin - MM, workshop 3728324408.\nBody: original mod LOD0 parts and weights, unchanged.\nRig: vanilla humanoid01, used by General of the Empire on foot.\nWeapons: vanilla General sword 01 / shield 01; VMD be_prop_1 / be_prop_2.\nSpacebar plays native idle/walk/run/attack playlist. Timeline markers identify clips.\nThis is a Blender test, not a game runtime result.\n')
report={'status':'blender_pose_and_attachment_test_passed','mod':manifest['mod'],'mod_sha256':manifest['mod_sha256'],'skeleton':'humanoid01','bone_count':len(rig.data.bones),'native_donor_unit':'wh_main_emp_cha_general_0','native_table':'hu1_empire_sword_and_shield','body_parts':len(body),'body_triangles':sum(len(o.data.polygons) for o in body),'unweighted_vertices':unweighted,'source_geometry_preserved':True,'bone_groups_all_resolved':True,'clips':checks,'timeline':[1,scene.frame_end],'textures_packed':len([im for im in bpy.data.images if im.packed_file]),'game_runtime_tested':False}
(R/'test_report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Karl_MM_on_Empire_General_TEST.blend'))
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'preview_idle.png');bpy.ops.render.render(write_still=True)
attack_marker=next(m for m in scene.timeline_markers if m.name.endswith('ATTACK_1'))
scene.frame_set(attack_marker.frame+15);scene.render.filepath=str(R/'preview_attack.png');bpy.ops.render.render(write_still=True)
print('TEST_COMPLETE',len(checks),'clips',len(rig.data.bones),'bones',flush=True)
