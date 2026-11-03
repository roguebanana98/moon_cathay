"""Integrate the complete native clip set on the approved, manually aligned mesh.

Never rebuild hands or source geometry. Only bake the approved sword placement
for a static prop export and carry it consistently to the three lower LODs.
"""
import bpy,addon_utils,sys,json,hashlib,struct,subprocess,re
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-animation-integration';REF=R/'reference/local/yuan-bo-model'
manifest=json.loads((O/'animation-set-manifest.json').read_text(encoding='utf-8'))
record=json.loads(Path((R/'build/huyen-ve-model-v1/sword-manual-adjustment-latest.txt').read_text().strip()).read_text())
source=Path(record['saved_copy']);assert Path(record['source_live_file']).name=='huyen-ve-before-hand-fix.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==record['saved_copy_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim
sys.path.insert(0,str(R/'tools'))
from HuyenVeAnimationPreview import complete_preview_channels
rig=bpy.data.objects['humanoid01e_HuyenVe'];body=bpy.data.objects['mc_huyen_ve_body_lod0'];sword=bpy.data.objects['mc_huyen_ve_sword_lod0'];scene=bpy.context.scene
body_lods=[bpy.data.objects['mc_huyen_ve_body_lod'+str(i)] for i in range(4)]
swords=[bpy.data.objects['mc_huyen_ve_sword_lod'+str(i)] for i in range(4)]
def mesh_hash(o):
    return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest()
def skin_hash(o):
    return hashlib.sha256(json.dumps([[(o.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in o.data.vertices],separators=(',',':')).encode()).hexdigest()
def bind_hash():return hashlib.sha256(json.dumps([(b.name,b.parent.name if b.parent else None,[list(r) for r in b.matrix_local]) for b in rig.data.bones]).encode()).hexdigest()
before={o.name:{'mesh':mesh_hash(o),'skin':skin_hash(o)} for o in body_lods};bind_before=bind_hash()
assert len(rig.data.bones)==96
assert max(abs(sword.matrix_basis[i][j]-record['matrix_basis'][i][j]) for i in range(4) for j in range(4))<1e-7
approved=sword.matrix_basis.copy()
for o in swords:
    assert o.parent is None
    assert len(o.constraints)==1 and o.constraints[0].subtarget=='weapon_2'
    o.matrix_basis=approved.copy()
    o.data.transform(o.matrix_basis);o.matrix_basis=Matrix.Identity(4);o.data.update()
    o.constraints[0].mute=True
    o.constraints[0].target=None
# Use exactly the PNGs embedded in the approved scene, not intermediate maps
# subsequently overwritten by the rejected hand/handle reconstruction.
BASE='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve';G=O/BASE;T=G/'tex';T.mkdir(parents=True,exist_ok=True)
tmp=O/'texture-intermediate';tmp.mkdir(exist_ok=True)
for obj in [body,sword]:
    nodes=[n for n in obj.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    assert len(nodes)==4
    for node in nodes:
        stem=Path(node['rmv2_path']).stem;im=node.image
        assert im.packed_file,'Approved preview image must be embedded'
        path=tmp/(stem+'.png');old=im.filepath_raw;im.filepath_raw=str(path);im.file_format='PNG';im.save();im.filepath_raw=old
        fmt='BC7_UNORM_SRGB' if stem.endswith('_base_colour') else 'BC7_UNORM' if stem.endswith('_material_map') else 'BC3_UNORM'
        subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f',fmt,'-o',str(T),str(path)],check=True)
rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis.identity()
bpy.context.view_layer.update()
def select(o):
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
def activate(col):
    def find(layer):
        if layer.collection==col:return layer
        for child in layer.children:
            result=find(child)
            if result:return result
    bpy.context.view_layer.active_layer_collection=find(bpy.context.view_layer.layer_collection)
for collection,filename,obj,skel in [('mc_huyen_ve_body','mc_huyen_ve_body.rigid_model_v2',body,'humanoid01e'),('mc_huyen_ve_sword','mc_huyen_ve_sword.rigid_model_v2',sword,'')]:
    activate(bpy.data.collections[collection]);select(obj)
    assert bpy.ops.export_scene.rmv2(filepath=str(G/filename),source='COLLECTION',skeleton_name=skel,auto_lods=False,apply_modifiers=True)=={'FINISHED'}
for o in swords:o.constraints[0].target=rig;o.constraints[0].subtarget='weapon_2';o.constraints[0].mute=False
actions=[];checks=[];path_slots={}
for slot,value in manifest['effective_slots'].items():
    for choice in value['Entries'].values():path_slots.setdefault(choice['animation'],[]).append(slot)
for i,path in enumerate(manifest['unique_clips']):
    activate(bpy.data.collections['mc_huyen_ve_body']);select(rig)
    imported,stats,warnings=import_anim.import_file(bpy.context,str(REF/path),{'mode':'ANIMATION','attach_meshes':True,'global_scale':1.0})
    assert imported==rig,(path,warnings)
    action=rig.animation_data.action;slots=sorted(path_slots.get(path,[]))
    label=slots[0] if slots else 'CAM_'+Path(path).stem.replace('cam_hu1e_dlc24_yuan_bo_sword_','')
    action.name=f'HV_{i+1:03d}_{label}';action.use_fake_user=True
    action['native_path']=path;action['native_slots']=', '.join(slots);action['frame_end']=int(action.frame_range[1])
    action['native_fps']=scene.render.fps/scene.render.fps_base
    complete_preview_channels(action,rig)
    start,end=map(int,action.frame_range);sampled=sorted({start,(start+end)//2,end})
    for frame in sampled:
        scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();de=body.evaluated_get(dg);mesh=de.to_mesh()
        assert np.isfinite(np.array([list(v.co) for v in mesh.vertices])).all(),(path,frame)
        de.to_mesh_clear();expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix;actual=sword.evaluated_get(dg).matrix_world
        assert max(abs(expected[a][b]-actual[a][b]) for a in range(4) for b in range(4))<1e-4,(path,frame)
    entry={'action':action.name,'native_path':path,'slots':slots,'frames':[start,end],'fps':action['native_fps'],'sampled_frames':sampled}
    actions.append(entry);print('INTEGRATED',i+1,len(manifest['unique_clips']),action.name,flush=True)
assert before=={o.name:{'mesh':mesh_hash(o),'skin':skin_hash(o)} for o in body_lods}
assert bind_hash()==bind_before
chosen=next(a for a in actions if a['native_path'].endswith('hu1e_dlc24_yuan_bo_sword_attack_01.anim'))
rig.animation_data.action=bpy.data.actions[chosen['action']]
if hasattr(rig.animation_data.action,'slots'):rig.animation_data.action_slot=rig.animation_data.action.slots[0]
scene.frame_start=0;scene.frame_end=chosen['frames'][1];scene.frame_set(0)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False;space.lock_object=rig;space.lock_bone='root';space.region_3d.view_location=(0,0,0);space.region_3d.view_distance=3.8
select(rig)
readme=bpy.data.texts.new('HUYEN VE - ANIMATION INDEX');readme.write('Approved before-hand-fix body; manually aligned sword. No hand reconstruction.\nSelect humanoid01e_HuyenVe; open Dope Sheet > Action Editor and choose HV_* action.\nFrame range and source path are stored in each action custom properties.\n\n'+ '\n'.join(f"{a['action']}: frames {a['frames'][0]}-{a['frames'][1]}, slots {', '.join(a['slots']) or 'campaign'}" for a in actions))
output=O/'huyen-ve-all-animations.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output))
report={'status':'integrated_local_not_runtime_verified','source':str(source),'source_sha256':record['saved_copy_sha256'],'output':str(output),
 'body_mesh_and_weights_unchanged':True,'native_bind_unchanged':True,'body_hashes':before,'rig_bind_hash':bind_before,'sword_manual_offset_baked':record['delta_translation'],
 'actions':actions,'action_count':len(actions),'sampled_pose_count':sum(len(a['sampled_frames']) for a in actions),
 'runtime_verified':False,'scope':'Native action library and exported approved meshes; visual and game runtime review remain separate'}
(O/'scene-integration-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('SCENE_INTEGRATION_COMPLETE',len(actions),flush=True)
