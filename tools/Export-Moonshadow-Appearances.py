"""Export approved appearances onto the native runtime 01d rig, with baked maps."""
import bpy,addon_utils,sys,json,math,hashlib,subprocess
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moonshadow-v7-appearance';BASE='variantmeshes/wh_variantmodels/mc_moonshadow_assassin'
G=O/BASE;T=G/'tex';TMP=O/'png';T.mkdir(parents=True,exist_ok=True);TMP.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,skeleton,rmv2_format as rf
clips=json.loads((R/'build/moonshadow-animation-preview/clips.json').read_text());D=R/'reference/local/khainite-weapons'
report={'variants':[],'textures':{},'skeleton':'humanoid01d','native_battle_lookup':'hu1d_elf_sword_and_handbow','native_campaign_lookup':'cam_hero_hu1d_elf_sword_and_handbow'}
def select(obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection
def save_image(im,stem,kind):
    path=TMP/(stem+'.png');old=im.filepath_raw;im.filepath_raw=str(path);im.file_format='PNG';im.save();im.filepath_raw=old
    fmt='BC7_UNORM_SRGB' if kind==27 else 'BC3_UNORM' if kind==1 else 'BC7_UNORM'
    target=T/(stem+'.dds')
    if not target.exists():subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f',fmt,'-o',str(T),str(path)],check=True,stdout=subprocess.DEVNULL)
    rel=BASE+'/tex/'+target.name;report['textures'][rel]=hashlib.sha256(target.read_bytes()).hexdigest();return rel
def bake(ob,stem,kind):
    # Only shader-derived colours/maps need baking. Normal maps remain native.
    target=T/(stem+'.dds')
    if target.exists():
        rel=BASE+'/tex/'+target.name;report['textures'][rel]=hashlib.sha256(target.read_bytes()).hexdigest();return rel
    mat=ob.data.materials[0];nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    original=output.inputs['Surface'].links[0].from_socket
    emission=nt.nodes.new('ShaderNodeEmission')
    if kind==27:
        socket=bsdf.inputs['Base Color'];nt.links.new(socket.links[0].from_socket,emission.inputs['Color'])
    else:
        combine=nt.nodes.new('ShaderNodeCombineColor');combine.mode='RGB'
        for channel,name in [('Red','Metallic'),('Green','Roughness')]:
            socket=bsdf.inputs[name]
            if socket.is_linked:nt.links.new(socket.links[0].from_socket,combine.inputs[channel])
            else:combine.inputs[channel].default_value=socket.default_value
        combine.inputs['Blue'].default_value=1;nt.links.new(combine.outputs[0],emission.inputs['Color'])
    nt.links.new(emission.outputs[0],output.inputs['Surface'])
    source=next(n.image for n in nt.nodes if n.type=='TEX_IMAGE' and n.image)
    im=bpy.data.images.new(stem,width=source.size[0],height=source.size[1],alpha=True)
    im.colorspace_settings.name='sRGB' if kind==27 else 'Non-Color'
    node=nt.nodes.new('ShaderNodeTexImage');node.image=im
    for n in nt.nodes:n.select=False
    node.select=True;nt.nodes.active=node
    select([ob]);bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.device='CPU';bpy.context.scene.cycles.samples=1
    bpy.context.scene.render.bake.margin=12
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    result=save_image(im,stem,kind);nt.links.new(original,output.inputs['Surface']);nt.nodes.remove(node);nt.nodes.remove(emission)
    print('BAKED',stem,flush=True);return result
def textures(ob):
    mat=ob.data.materials[0];nodes=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    by={}
    for n in nodes:
        name=n.image.name.lower()
        kind=27 if 'base_colour' in name or 'base_color' in name or 'diffuse' in name else 29 if 'material_map' in name else 1 if 'normal' in name else None
        if kind is not None:by[kind]=n.image
    assert set(by)>={27,29,1},(ob.name,[(n.name,n.image.name) for n in nodes])
    body='cth_alchemist_body_01_base_colour' in by[27].name
    hood='Black hood cloth' in mat.name
    if body:
        # Main body bake contains the weighted hand-preservation mask. Tiny
        # native ancillary cards share that atlas and must not overwrite it.
        bypaths={27:BASE+'/tex/charcoal_body_base.dds',29:BASE+'/tex/charcoal_body_material.dds'}
        if len(ob.data.polygons)>1000:
            bypaths={27:bake(ob,'charcoal_body_base',27),29:bake(ob,'charcoal_body_material',29)}
    elif hood:bypaths={27:bake(ob,'black_hood_base',27),29:bake(ob,'black_hood_material',29)}
    else:bypaths={}
    for kind,im in by.items():
        if kind not in bypaths:
            packed=bytes(im.packed_file.data) if im.packed_file else im.name.encode()
            stem='map_'+hashlib.sha256(packed).hexdigest()[:16]+'_'+str(kind)
            bypaths[kind]=save_image(im,stem,kind)
    ob.rmv2.textures.clear()
    for kind,path in sorted(bypaths.items()):
        slot=ob.rmv2.textures.add();slot.set_type_from_int(kind);slot.path=path
    return bypaths
aliases={'head_0':'head','neck_1':'neck_0','eyebrows_0':'eyebrow_0','eyelid_left_0':'eyelid_upper_left_0','eyelid_right_0':'eyelid_upper_right_0','shoulderpad_left_0':'shoulder_pad_left','shoulderpad_right_0':'shoulder_pad_right','armour_side_left_0':'root','armour_side_right_0':'root','skirt_front_center_0':'cingulum_front_0','skirt_front_center_1':'cingulum_front_1','skirt_back_left_0':'skirt_back_0','skirt_back_left_1':'skirt_back_1','skirt_back_right_0':'skirt_back_0','skirt_back_right_1':'skirt_back_1'}
def convert(ob,source,native):
    verts=[];normal_inverse=[];maxerror=0;cloth=set()
    if 'Original outfit without back cape' in ob.name:
        parent=list(range(len(ob.data.vertices)))
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        for e in ob.data.edges:
            a,b=map(find,e.vertices);parent[b]=a
        parts={}
        for v in ob.data.vertices:parts.setdefault(find(v.index),[]).append(v)
        for part in parts.values():
            lo=min(v.co.z for v in part);hi=max(v.co.z for v in part)
            if .4<lo<.65 and .9<hi<1.05:cloth.update(v.index for v in part)
    hood='def_Khanite_assassin_head_02_sub' in ob.name
    for v in ob.data.vertices:
        weights={}
        for g in v.groups:
            name=ob.vertex_groups[g.group].name
            if g.weight<1e-6:continue
            dest=name if name in native.data.bones else aliases.get(name)
            if dest is None:
                if any(s in name for s in ('beard','crest','ponytail','feather')):dest='head'
                elif name.startswith('cape_'):dest='spine_2'
                else:raise RuntimeError('Unmapped weighted bone '+name)
            weights[name]=(dest,g.weight)
        if hood:weights={'head_0':('head',1.0)}
        if v.index in cloth:weights={'root':('root',1.0)}
        assert weights,(ob.name,v.index)
        total=sum(w for _,w in weights.values())
        merged={}
        for dest,w in weights.values():merged[dest]=merged.get(dest,0)+w/total
        if v.index in cloth:
            # Preserve the continuous kilt at the waist. Native assassin cloak
            # bones have unrelated pivots; a small thigh blend at the hem lets
            # it follow locomotion without opening the upper robe.
            leg=max(0,min(.3,(.86-v.co.z)*1.0));left=max(0,min(1,.5+v.co.x*5))
            merged={'root':1-leg,'upperleg_left':leg*left,'upperleg_right':leg*(1-left)}
        merged=dict(sorted(((n,w) for n,w in merged.items() if w>1e-6),key=lambda a:-a[1])[:4])
        total=sum(merged.values());merged={n:w/total for n,w in merged.items()}
        # Fit to the approved posed surface, then invert the exact native skin
        # matrix. Bone cosmetic/rest axes differ across 01e/01d; directly rotating
        # mesh islands by those axes changes the hood and kilt silhouettes.
        blend=Matrix([[0.0]*4 for _ in range(4)])
        for name,w in merged.items():
            for i in range(4):
                for j in range(4):blend[i][j]+=native_skin[name][i][j]*w
        desired=desired_points[ob.name][v.index];p=blend.inverted()@desired
        normal_inverse.append(blend.to_3x3().inverted())
        maxerror=max(maxerror,(blend@p-desired).length)
        verts.append((p,merged))
    assert maxerror<1e-5,(ob.name,maxerror)
    ob.vertex_groups.clear()
    for _,weights in verts:
        for name in weights:
            if ob.vertex_groups.get(name) is None:ob.vertex_groups.new(name=name)
    for v,(p,weights) in zip(ob.data.vertices,verts):
        v.co=p
        for name,w in weights.items():ob.vertex_groups[name].add([v.index],w,'REPLACE')
    # Custom corner normals must be inverse-skinned too, not left in the
    # approved posed frame while vertex positions are moved into native bind.
    normals=[tuple((normal_inverse[loop.vertex_index]@desired_normals[ob.name][loop.index]).normalized()) for loop in ob.data.loops]
    ob.data.normals_split_custom_set(normals)
    ob.parent=None;ob.matrix_world=Matrix.Identity(4)
    for m in ob.modifiers:
        if m.type=='ARMATURE':m.object=native
    ob.rmv2.vertex_format='CINEMATIC';ob.data.update()
for number,index in ((8,1),(11,2),(3,3),(12,4)):
    bpy.ops.wm.open_mainfile(filepath=str(R/('build/moonshadow-assassin-final/moonshadow-assassin-face-%02d.blend'%number)))
    source=bpy.data.objects['MSA %02d | Alchemist_11_NATIVE_RIG'%index]
    native=bpy.data.objects['REFERENCE Khainite prop attachment frames'];native.animation_data_clear();native.hide_set(False)
    source.data.pose_position='POSE';bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get()]
    body=[o for o in visible if any(m.type=='ARMATURE' and m.object==source for m in o.modifiers)]
    props=[o for o in visible if o not in body];assert len(props)==2
    dg=bpy.context.evaluated_depsgraph_get();desired_points={};desired_normals={}
    for ob in body:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();desired_points[ob.name]=[v.co.copy() for v in me.vertices];desired_normals[ob.name]=[n.vector.copy() for n in me.corner_normals];ev.to_mesh_clear()
    approved_hands={name:source.pose.bones[name].matrix.copy() for name in ('hand_right','hand_left')}
    source.animation_data_clear();source.data.pose_position='REST';native.data.pose_position='REST';native.matrix_world=Matrix.Identity(4);native.parent=None
    # Bake the full body before any small cards using the shared atlas.
    body.sort(key=lambda o:-len(o.data.polygons))
    for ob in body+props:textures(ob)
    native.data.pose_position='POSE';select([native]);import_anim.import_file(bpy.context,str(D/clips[0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    native_skin={b.name:native.pose.bones[b.name].matrix@b.matrix_local.inverted() for b in native.data.bones}
    for ob in body:convert(ob,source,native)
    for ob in props:
        hand='hand_right' if 'Death Squad knife' in ob.name else 'hand_left';prop='be_prop_1' if hand=='hand_right' else 'be_prop_5'
        local=ob.matrix_basis.copy()
        offset=native.pose.bones[prop].matrix.inverted()@approved_hands[hand]@local
        ob.constraints.clear();ob.parent=None;ob.data.transform(offset);ob.matrix_world=Matrix.Identity(4);ob.rmv2.vertex_format='STATIC'
        # Runtime attachment follows the engine's prop bone, not a Blender-only anchor.
        c=ob.constraints.new('COPY_TRANSFORMS');c.target=native;c.subtarget=prop
    checks=[]
    for clip in clips:
        select([native]);import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
        action=native.animation_data.action;action.use_fake_user=True;action.name='ENGINE '+clip['label']
        start,end=map(int,action.frame_range);motion=[]
        for frame in sorted({start,(start+end)//2,end}):
            bpy.context.scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();sample=[]
            for ob in body:
                ev=ob.evaluated_get(dg);me=ev.to_mesh();points=np.array([tuple(v.co) for v in me.vertices]);assert np.isfinite(points).all();sample.extend(points[:4]);ev.to_mesh_clear()
            motion.append(np.array(sample))
        delta=max(float(np.linalg.norm(a-motion[0],axis=1).max()) for a in motion[1:]);assert delta>1e-5,clip
        checks.append({'clip':clip['path'],'max_sample_motion':delta})
    native.animation_data_clear();native.data.pose_position='REST'
    select(body)
    name='moonshadow_face_%02d'%number;path=G/(name+'.rigid_model_v2')
    assert bpy.ops.export_scene.rmv2(filepath=str(path),source='SELECTED',skeleton_name='humanoid01d',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
    for ob in props:
        kind='knife' if 'Death Squad knife' in ob.name else 'handbow'
        if number==8:
            con=ob.constraints[0];con.mute=True;select([ob])
            assert bpy.ops.export_scene.rmv2(filepath=str(G/(kind+'.rigid_model_v2')),source='SELECTED',skeleton_name='',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
            con.mute=False
    for ob in bpy.data.objects:
        if ob not in body+props+[native]:ob.hide_set(True);ob.hide_render=True
    for ob in body+props:ob.hide_set(False);ob.hide_render=False
    native.hide_set(True);native.data.pose_position='POSE';select([native]);import_anim.import_file(bpy.context,str(D/clips[0]['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});bpy.context.scene.frame_set(0)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('engine-face-%02d.blend'%number)),compress=True)
    exported=rf.load(path.read_bytes());assert exported.skeleton_name=='humanoid01d' and len(exported.lods)==4
    lods=[sum(len(m.mesh.indices)//3 for m in l.models) for l in exported.lods]
    report['variants'].append({'face':number,'file':BASE+'/'+path.name,'lod_triangles':lods,'clips_checked':checks})
    (O/'export-report.json').write_text(json.dumps(report,indent=2));print('EXPORTED_FACE',number,lods,flush=True)
print('MOONSHADOW_EXPORT_OK',flush=True)
