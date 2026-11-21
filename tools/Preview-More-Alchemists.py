"""Separate native-bind preview of all ten More Alchemists variants."""
import bpy,addon_utils,sys,json,subprocess,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/more-alchemists';O=R/'build/more-alchemists-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'more-alchemists-variants-03-to-12.blend';assert not OUT.exists(),'Keep user preview edits'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials,rmv2_format as rf
converted={};missing=[];audit=[]
# Reuse the established DDS conversion and comparison-label helpers only.
tree=ast.parse((R/'tools/Preview-Celestial-Concubines.py').read_text())
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['png','label','root']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'<preview helpers>','exec'))
paths=sorted(D.rglob('*.rigid_model_v2'));assert len(paths)==10
for i,path in enumerate(paths):
    number=int(path.stem.rsplit('_',1)[1]);x=(i%5-2)*2.4;z=3.55 if i<5 else 0
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE');rig.name='Alchemist_%02d_NATIVE_RIG'%number
    rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    before=set(bpy.data.objects)
    bpy.ops.import_scene.rmv2(filepath=str(path),build_materials=False,import_all_lods=False,attach_armature=True)
    meshes=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
    col=next(c for o in meshes for c in o.users_collection if 'lod0' in c.name)
    ordered=[o for o in col.objects if o.type=='MESH'];model=rf.load(path.read_bytes())
    assert len(ordered)==len(model.lods[0].models)
    for part,ob in zip(model.lods[0].models,ordered):
        pairs=[];hasbase=any(t==27 for t,p in part.material.textures)
        for typ,tx in part.material.textures:
            if typ not in ([27,1,29] if hasbase else [0,1,29]):continue
            convertedpath=png(tx)
            if convertedpath:pairs.append((typ,convertedpath))
        mat=materials.build_material('Alchemist_%02d_%s'%(number,part.material.model_name),pairs,ob.rmv2.alpha_mode,str(O))
        ob.data.materials.clear();ob.data.materials.append(mat)
        ob['source_model']=str(path);ob['variant_number']=number
    root('VARIANT %02d'%number,[rig]+meshes,x=x,z=z);rig.hide_set(True)
    label('ALCHEMIST %02d'%number,x,z-.22,.18)
    audit.append(dict(number=number,meshes=len(meshes),vertices=sum(len(o.data.vertices) for o in meshes),skeleton=model.skeleton_name,lods=len(model.lods)))
assert not missing,missing
label('MORE ALCHEMISTS! | ALL TEN MOD VARIANTS',0,6.8,.24)
label('Original geometry | Native bind pose | No mod changes',0,-.65,.15)
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral comparison');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
camdata=bpy.data.cameras.new('Overview');cam=bpy.data.objects.new('Overview',camdata);scene.collection.objects.link(cam)
target=Vector((0,0,3));cam.location=(0,-18,4.3);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=14;scene.camera=cam;cam.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=13.6
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
for im in bpy.data.images:
    if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT')
notes=bpy.data.texts.new('MODEL NOTES');notes.write('All ten original More Alchemists variants (03-12). Top: 03-07; bottom: 08-12. Native humanoid01e bind pose. LOD0 shown, four source LODs retained in read-only references. No head grafts, model edits, custom animations, or game-pack changes.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),models=audit,missing_textures=missing,geometry_modified=False,game_modified=False),indent=2))
print('READY',str(OUT),flush=True)
