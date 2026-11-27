import bpy,json,importlib.util,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));D=R/'reference/local/moon-jade-expanded'
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_anim
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/working/moon-jade-warriors/moon-jade-exported-assets-review.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.hide_set(False);rig.animation_data_clear()
for p in rig.pose.bones:p.matrix_basis.identity()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
import_anim.import_file(bpy.context,str(D/'animations/battle/humanoid01e/rider/warhorse/lance_and_shield/stand/hu1e_hr1_jade_lancer_stand_01.anim'),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
report={'rider':{p.name:list(p.matrix.translation) for p in rig.pose.bones if p.name in ['animroot','root','foot_left','foot_right','hand_right']}}
bpy.ops.object.select_all(action='DESELECT');horse,_,_=import_anim.import_file(bpy.context,str(D/'animations/skeletons/horse01.anim'),dict(mode='SKELETON',attach_meshes=False,global_scale=1.0));bpy.context.view_layer.objects.active=horse;horse.select_set(True)
import_anim.import_file(bpy.context,str(D/'animations/battle/horse01/stand/hr1_stand_01.anim'),dict(mode='ANIMATION',attach_meshes=False,global_scale=1.0));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
report['horse']={p.name:list(p.matrix.translation) for p in horse.pose.bones}
(R/'build/moon-jade-reskin-v2/rider-space-audit.json').write_text(json.dumps(report,indent=2))
