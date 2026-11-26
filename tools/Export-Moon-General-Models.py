"""Export approved native-bound generals; bake shaders and preserve source files."""
import bpy,addon_utils,sys,json,hashlib,subprocess,math,bmesh
from pathlib import Path
from mathutils import Matrix
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-generals-v20';O.mkdir(exist_ok=True)
SOURCE=R/'build/moon-generals-preview/moon-generals-assault-polearm-connected.blend'
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import rmv2_format as rf
report=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),models=[],textures={})
cache={}

def select(obs):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection
    for ob in obs:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]

def flat(name,color):
    im=bpy.data.images.get(name)
    if not im:
        im=bpy.data.images.new(name,width=4,height=4,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels[:]=list(color)*16
    return im

def dds(im,kind,stem=None):
    key=hashlib.sha256(bytes(im.packed_file.data) if im.packed_file else (im.name+str(tuple(im.pixels[:8]))).encode()).hexdigest()[:16]
    stem=stem or ('map_'+key+'_'+str(kind));dest=T/(stem+'.dds')
    if not dest.exists():
        png=TMP/(stem+'.png');old=im.filepath_raw;im.filepath_raw=str(png);im.file_format='PNG';im.save();im.filepath_raw=old
        subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f','BC7_UNORM_SRGB' if kind==27 else 'BC3_UNORM' if kind==1 else 'BC7_UNORM','-o',str(T),str(png)],check=True,stdout=subprocess.DEVNULL)
    path=BASE+'/tex/'+dest.name;report['textures'][path]=hashlib.sha256(dest.read_bytes()).hexdigest();return path

def bake_color(ob,stem):
    dest=T/(stem+'.dds')
    if dest.exists():
        p=BASE+'/tex/'+dest.name;report['textures'][p]=hashlib.sha256(dest.read_bytes()).hexdigest();return p
    mat=ob.data.materials[0];nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    previous=out.inputs['Surface'].links[0].from_socket;emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(emit.outputs[0],out.inputs['Surface'])
    image=bpy.data.images.new(stem,width=1024,height=1024,alpha=True);image.colorspace_settings.name='sRGB'
    target=nt.nodes.new('ShaderNodeTexImage');target.image=image
    for n in nt.nodes:n.select=False
    target.select=True;nt.nodes.active=target
    color=bs.inputs['Base Color']
    if color.is_linked:nt.links.new(color.links[0].from_socket,emit.inputs['Color'])
    else:emit.inputs['Color'].default_value=color.default_value
    select([ob]);bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.device='CPU';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=12
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    alpha=bs.inputs['Alpha']
    if alpha.is_linked:
        values=np.empty(1024*1024*4,dtype=np.float32);image.pixels.foreach_get(values)
        mask=bpy.data.images.new(stem+'_alpha',width=1024,height=1024,alpha=False);mask.colorspace_settings.name='Non-Color';target.image=mask
        nt.links.new(alpha.links[0].from_socket,emit.inputs['Color']);bpy.ops.object.bake(type='EMIT',use_clear=True)
        av=np.empty_like(values);mask.pixels.foreach_get(av);values[3::4]=av[0::4]
        image.pixels.foreach_set(values);image.update();bpy.data.images.remove(mask)
    result=dds(image,27,stem);nt.links.new(previous,out.inputs['Surface']);nt.nodes.remove(target);nt.nodes.remove(emit)
    print('BAKED',ob.name,flush=True);return result

def maps(ob,stem,needs_bake):
    mat=ob.data.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');alpha=bs.inputs['Alpha'].is_linked
    images={}
    for n in mat.node_tree.nodes:
        if n.type!='TEX_IMAGE' or not n.image:continue
        label=n.image.filepath.lower()
        typ=1 if '_normal' in label else 29 if '_material_map' in label else None
        if typ:images.setdefault(typ,n.image)
    bc=bs.inputs['Base Color'];direct=bc.links[0].from_node if bc.is_linked else None
    if direct and direct.type=='TEX_IMAGE' and not needs_bake:base=dds(direct.image,27)
    else:base=bake_color(ob,stem+'_base')
    paths={27:base,1:dds(images.get(1) or flat('General flat normal',(.5,.5,1,1)),1),29:dds(images.get(29) or flat('General default material',(.1,.65,1,1)),29)}
    ob.rmv2.textures.clear()
    for typ,path in sorted(paths.items()):slot=ob.rmv2.textures.add();slot.set_type_from_int(typ);slot.path=path
    ob.rmv2.textures_initialized=True;ob.rmv2.alpha_mode='TRANSPARENT' if alpha else 'OPAQUE';ob.rmv2.material_id='AUTO'
    return paths

for label,key,skeleton in [('Assault','mc_assault_general','humanoid01b'),('Bastion','mc_bastion_general','humanoid01e')]:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
    BASE='variantmeshes/wh_variantmodels/'+key;G=O/BASE;T=G/'tex';TMP=O/'png'/key;T.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith(label));root=rig.parent;scale=float(root.scale.x)
    bodies=[o for o in root.children if o.type=='MESH' and not o.hide_get() and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
    props=[o for o in bpy.data.collections['Weapons | '+label+' General'].objects if o.type=='MESH' and not o.hide_get()]
    rig.animation_data_clear();rig.parent=None;rig.matrix_world=Matrix.Identity(4);rig.data.pose_position='REST'
    for b in rig.pose.bones:b.matrix_basis.identity()
    body=[];weapons=[];rows=[]
    for source in bodies+props:
        for material_index in sorted({p.material_index for p in source.data.polygons}):
            ob=source.copy();ob.data=source.data.copy();scene.collection.objects.link(ob)
            bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=material_index],context='FACES')
            loose=[v for v in bm.verts if not v.link_faces]
            if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
            bm.to_mesh(ob.data);bm.free();ob.data.update()
            mat=source.data.materials[material_index].copy();ob.data.materials.clear();ob.data.materials.append(mat)
            for p in ob.data.polygons:p.material_index=0
            # Shift repeated UV tiles as entire triangles; source texture wrapping
            # remains equivalent and emission baking writes the used base tile.
            uv=ob.data.uv_layers.active
            for polygon in ob.data.polygons:
                coords=[uv.data[i].uv for i in polygon.loop_indices];sx=math.floor(sum(p.x for p in coords)/len(coords));sy=math.floor(sum(p.y for p in coords)/len(coords))
                for p in coords:p.x-=sx;p.y-=sy
            ob.name=key+' | '+source.name+' | '+str(material_index);ob.parent=None;ob.constraints.clear();ob.matrix_world=Matrix.Identity(4)
            weighted=source in bodies
            ob.rmv2.vertex_format='CINEMATIC' if weighted else 'STATIC'
            if not weighted:
                for mod in list(ob.modifiers):ob.modifiers.remove(mod)
            paths=maps(ob,'part_%03d'%len(rows),label=='Bastion')
            rows.append(dict(name=ob.name,source=source.name,vertices=len(ob.data.vertices),weighted=weighted,textures=paths,alpha=ob.rmv2.alpha_mode))
            (body if weighted else weapons).append(ob)
    # Preserve exact native bind geometry, weights, bone order and prop coordinates.
    select(body);bodyfile=G/'body.rigid_model_v2'
    assert bpy.ops.export_scene.rmv2(filepath=str(bodyfile),source='SELECTED',skeleton_name=skeleton,auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
    select(weapons);weaponfile=G/'weapon.rigid_model_v2'
    assert bpy.ops.export_scene.rmv2(filepath=str(weaponfile),source='SELECTED',skeleton_name='',auto_lods=True,auto_lod_count=4,apply_modifiers=True)=={'FINISHED'}
    lods={}
    for path in [bodyfile,weaponfile]:
        model=rf.load(path.read_bytes());assert len(model.lods)==4
        assert model.skeleton_name==(skeleton if path==bodyfile else '')
        counts=[]
        for lod in model.lods:
            counts.append(sum(len(part.mesh.indices)//3 for part in lod.models))
            for part in lod.models:
                if path==bodyfile:
                    assert part.mesh.bone_indices.max()<len(rig.data.bones)
                    assert abs(part.mesh.bone_weights.sum(axis=1)-1).max()<.025
        assert all(a>=b>0 for a,b in zip(counts,counts[1:])),counts
        lods[path.name]=counts
    # Save an export checkpoint with shader and per-part map metadata, separate
    # from both user source and the exact exported-RMV review created later.
    select(body+weapons)
    for ob in list(bpy.data.objects):
        if ob not in body+weapons+[rig]:ob.hide_set(True);ob.hide_render=True
    rig.hide_set(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(key+'-export.blend')),compress=True)
    report['models'].append(dict(key=key,skeleton=skeleton,scale=scale,bones=len(rig.data.bones),body=BASE+'/body.rigid_model_v2',weapon=BASE+'/weapon.rigid_model_v2',attachment='be_prop_0' if label=='Assault' else 'weapon_1',parts=rows,lod_triangles=lods))
    (O/'export-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('EXPORTED_GENERAL',key,lods,flush=True)
print('MOON_GENERAL_MODELS_EXPORTED',flush=True)
