import bpy,addon_utils,json,struct,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;SRC=R.parent/'sariwa_damsel02';D=R/'reference'
OUT=R/'export';OUT.mkdir(exist_ok=True)
TEX=OUT/'tex';TEX.mkdir(exist_ok=True)
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,export_rmv2,rmv2_format as rf
bpy.ops.wm.open_mainfile(filepath=str(SRC/'Sariwa_Damsel02_Naga3_v2.blend'))
scene=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith('Sariwa'))
body=[o for o in bpy.data.objects if o.type=='MESH' and any('Sariwa | '+s in o.name for s in ['head','body'])]
staff=next(o for o in bpy.data.objects if o.type=='MESH' and 'Sariwa | weapon_5' in o.name)
crown=bpy.data.objects['Sariwa | Naga three-head crown']
assert len(rig.data.bones)==89 and len(body)==3
assert all(all(g.name in rig.data.bones for g in o.vertex_groups) for o in body)
assert all(all(any(g.weight>0 for g in v.groups) for v in o.data.vertices) for o in body)
def meshhash(o):return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest()
before={o.name:meshhash(o) for o in body}
manifest=json.loads((R/'animation_manifest.json').read_text())
want=['STAND','WALK_1','RUN_1','ATTACK_1','ATTACK_2','COMBAT_IDLE_1','CAST_SPELL_FORWARD_SHORT','CAST_SPELL_FORWARD_MEDIUM','CAST_SPELL_FORWARD_LONG','CAST_SPELL_UP_SHORT','CAST_SPELL_UP_LONG']
def select(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def complete(action):
    bag=action.layers[0].strips[0].channelbag(action.slots[0],ensure=True);curves=bag.fcurves;existing={(f.data_path,f.array_index) for f in curves}
    for b in rig.pose.bones:
        for prop,vals in [('location',(0,0,0)),('rotation_quaternion',(1,0,0,0))]:
            path=f'pose.bones["{b.name}"].{prop}'
            for i,val in enumerate(vals):
                if (path,i) not in existing:curves.new(path,index=i).keyframe_points.insert(0,val,options={'FAST'})
actions=[];checks=[]
for slot in want:
    clip=next(c for c in manifest['clips'] if c['slot']==slot);select(rig)
    _,stats,warns=import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':True})
    action=rig.animation_data.action;action.name='SARIWA | '+slot;action.use_fake_user=True;complete(action)
    lo,hi=map(int,action.frame_range);bounds=[];errors=[]
    for frame in sorted(set(int(x) for x in np.linspace(lo,hi,7))):
        scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();coords=[]
        for o in body:
            ev=o.evaluated_get(dg);me=ev.to_mesh();coords.extend(tuple(ev.matrix_world@v.co) for v in me.vertices);ev.to_mesh_clear()
        xyz=np.array(coords);dims=xyz.max(0)-xyz.min(0);assert np.isfinite(xyz).all() and max(dims)<5,(slot,frame,dims)
        bounds.append({'frame':frame,'dimensions':dims.tolist()})
        a=crown.evaluated_get(dg).matrix_world;b=staff.evaluated_get(dg).matrix_world
        errors.append(max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)))
    assert max(errors)<1e-4
    checks.append({'slot':slot,'path':clip['path'],'frames':[lo,hi],'samples':bounds,'attachment_error':max(errors),'warnings':warns})
    actions.append(action);print('CLIP_OK',slot,lo,hi,flush=True)
assert before=={o.name:meshhash(o) for o in body}
rig.animation_data.action=None
for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
track=rig.animation_data.nla_tracks.new();track.name='Sariwa | native Damsel motion tests';cursor=1
for action in actions:
    start,end=action.frame_range;strip=track.strips.new(action.name,cursor,action);strip.action_frame_start=start;strip.action_frame_end=max(end,start+1)
    strip.blend_type='REPLACE';strip.extrapolation='NOTHING';scene.timeline_markers.new(action.name,frame=cursor);cursor=int(strip.frame_end)+1
scene.frame_start=1;scene.frame_end=cursor-1;scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Sariwa_Damsel_Rig_Anim_TEST.blend'))

# Bake the sculpted prop materials to native-compatible albedo / material-map atlases.
select(crown);crown.data=crown.data.copy()
albedo=bpy.data.images.new('Naga game albedo',width=1024,height=1024,alpha=False);albedo.colorspace_settings.name='sRGB'
pbr=bpy.data.images.new('Naga game material map',width=1024,height=1024,alpha=False);pbr.colorspace_settings.name='Non-Color'
saved=[]
for mat in crown.data.materials:
    mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    emit=nodes.new('ShaderNodeEmission');target=nodes.new('ShaderNodeTexImage')
    saved.append((mat,bs,output,emit,target));mat.node_tree.links.new(emit.outputs[0],output.inputs['Surface'])
scene.render.engine='CYCLES';scene.cycles.samples=1
for name,image in [('base_colour',albedo),('material_map',pbr)]:
    for mat,bs,out,emit,target in saved:
        color=bs.inputs['Base Color'].default_value if name=='base_colour' else (bs.inputs['Metallic'].default_value,bs.inputs['Roughness'].default_value,0,1)
        emit.inputs['Color'].default_value=color;emit.inputs['Strength'].default_value=1;target.image=image;mat.node_tree.nodes.active=target
    bpy.ops.object.bake(type='EMIT',margin=3,use_clear=True)
    image.filepath_raw=str(TEX/('edh_sariwa_naga_'+name+'.png'));image.file_format='PNG';image.save()
for mat,bs,out,emit,target in saved:mat.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
for name,color in [('normal',(1,.5,0,.5)),('mask',(0,0,0,0)),('jade_mask',(0,0,0,.45)),('body_mask',(0,0,0,0))]:
    im=bpy.data.images.new(name,width=4,height=4,alpha=True);im.generated_color=color;im.filepath_raw=str(TEX/('edh_sariwa_'+name+'.png'));im.file_format='PNG';im.save()

# Separate jade surfaces for their native emissive material; bake UVs stay unchanged.
select(crown);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bpy.ops.object.mode_set(mode='OBJECT')
jade_indices={i for i,m in enumerate(crown.data.materials) if 'luminous jade' in m.name}
for poly in crown.data.polygons:poly.select=poly.material_index in jade_indices
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
jade=next(o for o in bpy.context.selected_objects if o!=crown);jade.name='Sariwa | Naga jade'

export_records=[]
PREFIX='variantmeshes/wh_variantmodels/edh/sariwa/'
for obj,stem,jade_part in [(staff,'edh_sariwa_staff',False),(crown,'edh_sariwa_naga',False),(jade,'edh_sariwa_naga_jade',True)]:
    duplicate=obj.copy();duplicate.data=obj.data.copy();scene.collection.objects.link(duplicate);duplicate.parent=None
    duplicate.constraints.clear();duplicate.matrix_world=Matrix.Identity(4);duplicate.name=stem;duplicate.vertex_groups.clear()
    duplicate.rmv2.vertex_format='STATIC';duplicate.rmv2.material_id='AUTO';duplicate.rmv2.matrix_index=0;duplicate.rmv2.parent_matrix_index=0
    duplicate.rmv2.model_name=stem;duplicate.rmv2.alpha_mode='OPAQUE'
    if obj!=staff:
        duplicate.rmv2.textures.clear();duplicate.rmv2.textures_initialized=True
        for tt,path in [('BaseColour','tex/edh_sariwa_naga_base_colour.dds'),('Normal','tex/edh_sariwa_normal.dds'),('MaterialMap','tex/edh_sariwa_naga_material_map.dds'),('Mask','tex/edh_sariwa_'+('jade_mask' if jade_part else 'mask')+'.dds')]:
            t=duplicate.rmv2.textures.add();t.texture_type=tt;t.path=PREFIX+path
    select(duplicate)
    stats,warnings=export_rmv2.export_file(bpy.context,str(OUT/(stem+'.rigid_model_v2')),{'source':'SELECTED','version':'8','apply_modifiers':True,'write_attach_points':False,'auto_lods':True,'auto_lod_count':4})
    parsed=rf.load((OUT/(stem+'.rigid_model_v2')).read_bytes())
    assert len(parsed.lods)==4 and all(len(l.models)==1 for l in parsed.lods)
    assert all(l.models[0].material.vertex_format==rf.VF_STATIC for l in parsed.lods)
    # Export must preserve the model's local attachment-space coordinates.
    from io_scene_rmv2 import import_rmv2
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    root,round_stats=import_rmv2.import_file(bpy.context,str(OUT/(stem+'.rigid_model_v2')),{'import_lods':'FIRST','attach_armature':False,'build_materials':False})
    reloaded=[o for o in root.all_objects if o.type=='MESH']
    source_bounds=np.array([list(v.co) for v in duplicate.data.vertices]);round_bounds=np.array([list(v.co) for o in reloaded for v in o.data.vertices])
    err=float(max(abs(source_bounds.min(0)-round_bounds.min(0)).max(),abs(source_bounds.max(0)-round_bounds.max(0)).max()))
    assert err<.002,(stem,err)
    for o in list(root.all_objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(root)
    export_records.append({'model':stem,**stats,'warnings':warnings,'local_bounds_error':err,'lod_triangles':[len(l.models[0].mesh.indices)//3 for l in parsed.lods]})
    bpy.data.objects.remove(duplicate,do_unlink=True);print('EXPORT_OK',stem,stats,flush=True)
# Render a private portrait using the tested original native pose.
rig.animation_data.nla_tracks[0].mute=True;rig.animation_data.action=actions[0];scene.frame_set(1)
target=rig.matrix_world@rig.pose.bones['head'].head+Vector((0,0,-.06));cam=scene.camera
cam.location=target+Vector((.25,-4,.1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.72
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA';scene.cycles.samples=32
scene.render.filepath=str(R/'sariwa_portrait.png');bpy.ops.render.render(write_still=True)
report={'status':'rig_animation_and_prop_exports_passed','skeleton':'humanoid01b','bones':len(rig.data.bones),'body_mesh_parts':len(body),
    'native_table':manifest['table'],'native_clips_tested':checks,'body_mesh_bytes_unchanged':True,'exports':export_records,'animation_scene':str(R/'Sariwa_Damsel_Rig_Anim_TEST.blend')}
(R/'rig_export_report.json').write_text(json.dumps(report,indent=2));print('RIG_EXPORT_READY',flush=True)
