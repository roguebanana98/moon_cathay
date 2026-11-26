"""Blender shader bake, native animation checks and cards for three caster models."""
import bpy, addon_utils, ast, json, subprocess, sys, re
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/moon-casters-v13';D=O;P=O/'renders';P.mkdir(exist_ok=True)
manifest=json.loads((O/'models.json').read_text(encoding='utf8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.threads_mode='FIXED';scene.render.threads=12
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
for b in manifest['shader_bakes']:
    src=Path(b['source']);folder=O/'bake-source';folder.mkdir(exist_ok=True)
    subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(folder),str(src)],check=True,stdout=subprocess.DEVNULL)
    im=bpy.data.images.load(str(folder/(src.stem+'.png')),check_existing=False)
    bpy.ops.mesh.primitive_plane_add();plane=bpy.context.object
    mat=bpy.data.materials.new('Moon silver cloth bake');mat.use_nodes=True;plane.data.materials.append(mat)
    nt=mat.node_tree;nt.nodes.clear()
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im
    grey=nt.nodes.new('ShaderNodeHueSaturation');grey.inputs['Saturation'].default_value=b.get('saturation',0);grey.inputs['Value'].default_value=b.get('value',1)
    nt.links.new(tex.outputs['Color'],grey.inputs['Color'])
    emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(grey.outputs['Color'],emit.inputs['Color'])
    output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(emit.outputs[0],output.inputs['Surface'])
    target=bpy.data.images.new('Moon cloth baked',width=im.size[0],height=im.size[1],alpha=True)
    bake=nt.nodes.new('ShaderNodeTexImage');bake.image=target;nt.nodes.active=bake
    bpy.ops.object.bake(type='EMIT',margin=0)
    # Preserve the authored garment cutout channel while packing baked RGB.
    rgb=np.empty(len(target.pixels),dtype=np.float32);target.pixels.foreach_get(rgb)
    original=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(original)
    rgb[3::4]=original[3::4];target.pixels.foreach_set(rgb);target.update()
    dest=O/b['target'];dest.parent.mkdir(parents=True,exist_ok=True)
    png=O/'bake-source'/(dest.stem+'.png');target.filepath_raw=str(png);target.file_format='PNG';target.save()
    subprocess.run([C['texconv'],'-nologo','-y','-f','BC7_UNORM_SRGB','-o',str(dest.parent),str(png)],check=True,stdout=subprocess.DEVNULL)
    assert dest.exists();manifest['files'].append(b['target'])
    bpy.data.objects.remove(plane,do_unlink=True)
    print('BAKED',dest.name,flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import materials,import_anim
import xml.etree.ElementTree as ET
converted={};missing=[];audit=[]
def material_tree(path):
    tree=ET.Element('material')
    for slot,source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>',Path(path).read_text(encoding='utf8')):
        tx=ET.SubElement(tree,'texture');ET.SubElement(tx,'slot').text=slot;ET.SubElement(tx,'source').text=source
    return tree
helpers=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text(encoding='utf8').replace('ET.parse(D/matpath)','material_tree(D/matpath)'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['png','import_ws','root']],type_ignores=[]),'<preview helpers>','exec'))
clips=[
 'animations/battle/humanoid01e/storm_dragon/stand/hu1e_strom_dragon_stand_01.anim',
 'animations/battle/humanoid01e/storm_dragon/locomotion/hu1e_strom_dragon_walk_02.anim',
 'animations/battle/humanoid01e/storm_dragon/locomotion/hu1e_strom_dragon_run_01.anim',
 'animations/battle/humanoid01e/storm_dragon/spell_casting/hu1e_storm_dragon_cast_spell_frwd_short_01.anim',
 'animations/battle/humanoid01e/storm_dragon/spell_casting/hu1e_storm_dragon_cast_spell_up_long_01.anim',
 'animations/battle/humanoid01e/storm_dragon/attacks/hu1e_storm_dragon_attack_01.anim',
 'animations/battle/humanoid01e/storm_dragon/campaign/cam_hu1e_storm_dragon_run_01.anim']
ref=R/'reference/local/moon-casters-animation'
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f',*[p+';'+str(ref) for p in clips]],check=True,stdout=subprocess.DEVNULL)
rigs=[];roots=[];checks=[]
for i,m in enumerate(manifest['models']):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name=m['name']+' native humanoid01e'
    rig.animation_data_clear();meshes=import_ws(m['wsmodel'],rig)
    group=root(m['name'],[rig]+meshes,x=(i-1)*1.8);roots.append(group);rigs.append(rig)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    for clip in clips:
        import_anim.import_file(bpy.context,str(ref/clip),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
        action=rig.animation_data.action;action.use_fake_user=True;action.name=m['name']+' | '+Path(clip).stem
        first,last=map(int,action.frame_range)
        snapshots=[]
        for frame in sorted({first,(first+last)//2,last}):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
            for ob in meshes:
                ev=ob.evaluated_get(dg);mesh=ev.to_mesh();co=np.array([tuple(v.co) for v in mesh.vertices]);ev.to_mesh_clear()
                assert np.isfinite(co).all() and abs(co).max()<50,(m['key'],clip,ob.name)
                if ob==meshes[0]:snapshots.append(co.copy())
        if 'stand/' not in clip:assert max(np.max(abs(x-snapshots[0])) for x in snapshots)>1e-6,clip
        checks.append(dict(model=m['key'],clip=clip,samples=3))
    import_anim.import_file(bpy.context,str(ref/clips[0]),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
    rig.animation_data.action.use_fake_user=True;rig.hide_set(True)
assert not missing,missing
scene=bpy.context.scene;scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.threads_mode='FIXED';scene.render.threads=12
scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Caster studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
for location,power,size in [((3,-4,5),650,4),((-3,-2,3),420,3),((0,3,4),600,3)]:
    data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.size=size
    ob=bpy.data.objects.new('Studio',data);scene.collection.objects.link(ob);ob.location=location;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
for i,m in enumerate(manifest['models']):
    x=(i-1)*1.8
    for j,group in enumerate(roots):
        for ob in group.children_recursive:ob.hide_render=j!=i or ob.type=='ARMATURE'
    for kind,z,scale,size in [('body',1.05,2.65,(512,768)),('head',1.65,.8,(512,512))]:
        cam.location=(x+.35,-6,z+.2);cam.rotation_euler=(Vector((x,0,z))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(P/(m['key']+'_'+kind+'.png'));bpy.ops.render.render(write_still=True)
for group in roots:
    for ob in group.children_recursive:ob.hide_render=ob.type=='ARMATURE'
cam.location=(0,-10,2.5);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=6.1
scene.render.resolution_x=1400;scene.render.resolution_y=800;scene.render.filepath=str(P/'three-casters.png');bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'moon-casters-models.blend'),compress=True)
manifest['files']=sorted(set(manifest['files']));manifest['animation_samples']=len(checks)*3
(O/'models.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(O/'model-review.json').write_text(json.dumps(dict(checks=checks,samples=len(checks)*3,missing_textures=missing,native_skeleton='humanoid01e',battle_animation='hu1e_mage_storm_dragon',campaign_animation='cam_hu1e_mage_storm_dragon',runtime_verified=False),indent=2),encoding='utf8')
print('MOON_CASTER_REVIEW_READY',flush=True)
