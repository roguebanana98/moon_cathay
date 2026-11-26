"""Inspect the RoR pack's two native humanoid01d human assassin variants."""
import bpy,addon_utils,sys,json,subprocess,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/cathay-ror';O=R/'build/cathay-ror-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'dark-society-death-squad-models.blend';assert not OUT.exists()
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials,rmv2_format as rf
converted={};missing=[];audit=[]
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','label','root']],type_ignores=[]),'<preview helpers>','exec'))
def import_part(stem,rig=None):
    path=D/('variantmeshes/wh_variantmodels/'+stem+'.rigid_model_v2')
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=rig
    if rig:rig.select_set(True)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.rmv2(filepath=str(path),build_materials=False,import_all_lods=False,attach_armature=rig is not None)
    meshes=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
    col=next(c for o in meshes for c in o.users_collection if 'lod0' in c.name)
    ordered=[o for o in col.objects if o.type=='MESH'];model=rf.load(path.read_bytes())
    assert len(ordered)==len(model.lods[0].models)
    for part,ob in zip(model.lods[0].models,ordered):
        hasbase=any(t==27 for t,p in part.material.textures);pairs=[]
        for typ,tx in part.material.textures:
            if typ not in ([27,1,29] if hasbase else [0,1,29]):continue
            rel=png(tx)
            if rel:pairs.append((typ,rel))
        mat=materials.build_material(stem+' | '+part.material.model_name,pairs,ob.rmv2.alpha_mode,str(O))
        ob.data.materials.clear();ob.data.materials.append(mat);ob['source_model']=str(path)
    audit.append(dict(file=stem,skeleton=model.skeleton_name,parts=len(meshes),lods=len(model.lods)))
    return meshes
clip=D/'animations/battle/humanoid01d/def_dual_sword/stand/hu1d_dsw_stand_01.anim'
for index,(stem,head,x) in enumerate([('cth_ninja_ds','cth_ninja_head_4',-1.25),('cth_ninja_2_ds','cth_ninja_head_5',1.25)],1):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/khainite-weapons/animations/skeletons/humanoid01d.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Ninja %02d | native humanoid01d'%index
    meshes=import_part(stem,rig)+import_part(head,rig)
    weapons=[]
    for knife,bone in [('ninja_knife_1','be_prop_1'),('ninja_knife_2','be_prop_5')]:
        parts=import_part(knife)
        for ob in parts:
            con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=bone
        weapons+=parts
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.import_scene.tw_anim(filepath=str(clip))
    rig.animation_data.action.name='Ninja %02d native dual-sword stand'%index;rig.animation_data.action.use_fake_user=True
    root('NINJA %02d'%index,[rig]+meshes+weapons,x=x);rig.hide_set(True)
    label('BODY %02d + HEAD %02d'%(index,4 if index==1 else 5),x,-.2,.17)
for head,x in [('cth_ninja_head_4',-.6),('cth_ninja_head_5',.6)]:
    meshes=import_part(head);root(head,meshes,x=x,z=1.05)
    label('HEAD '+head[-1],x,2.5,.13)
scene=bpy.context.scene;scene.frame_set(0);scene.frame_start=0;scene.frame_end=54
label('DARK SOCIETY DEATH SQUAD | CATHAY RoR',0,3.3,.16)
assert not missing,missing
scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
camdata=bpy.data.cameras.new('Comparison');cam=bpy.data.objects.new('Comparison',camdata);scene.collection.objects.link(cam)
target=Vector((0,0,1.4));cam.location=(.3,-8,2);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=5.6;scene.camera=cam;cam.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=5.7
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),source_workshop='2817585623',body_variants=2,heads=2,knife_models=2,native_animation='hu1d_elf_dual_sword',native_clip=str(clip),parts=audit,source_geometry_modified=False,model_11_unchanged=True,game_modified=False),indent=2))
print('ROR_NINJAS_READY',str(OUT),flush=True)
