"""Swap only Bastion's visible weapon to the actual vanilla Celestial hammer."""
import bpy, addon_utils, sys, json, subprocess, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-generals-preview'
D=R/'reference/local/vanilla-celestial-hammer'
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
SOURCE=O/'moon-generals-skin-and-armour-v3.blend'
OUT=O/'moon-generals-bastion-native-hammer.blend'
assert not OUT.exists(), 'Preserve review checkpoints'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
root=bpy.data.objects['Bastion General | Root'];rig=bpy.data.objects['Bastion General | Native humanoid01e']
col=bpy.data.collections['Weapons | Bastion General'];hidden=bpy.data.collections['Hidden originals | Bastion General']
for ob in list(col.objects):
    col.objects.unlink(ob);hidden.objects.link(ob);ob.hide_set(True);ob.hide_render=True
component=json.loads((O/'vanilla-hammer.json').read_text(encoding='utf8'))
converted={}
for _,path in {tuple(p) for part in component['parts'] for p in part['textures']}:
    folder=O/'preview-textures'/hashlib.sha256(('vanilla/'+path).encode()).hexdigest()[:12];folder.mkdir(parents=True,exist_ok=True)
    dest=folder/(Path(path).stem+'.png')
    if not dest.exists():
        subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-w','1024','-h','1024','-o',str(folder),str(D/path)],check=True,stdout=subprocess.DEVNULL)
    converted[path]=dest.relative_to(O).as_posix()
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
before=set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(D/component['geometry']),build_materials=False,import_all_lods=False,attach_armature=False)
objs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
assert len(objs)==len(component['parts'])==1
for ob,part in zip(objs,component['parts']):
    for old in list(ob.users_collection):old.objects.unlink(ob)
    col.objects.link(ob);ob.name='Bastion | VANILLA Celestial General hammer'
    ob.parent=root;ob.matrix_parent_inverse.identity();ob.matrix_basis.identity()
    con=ob.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='weapon_1'
    mat=materials.build_material('VANILLA Celestial General hammer',[(typ,converted[path]) for typ,path in part['textures']],'OPAQUE',str(O))
    ob.data.materials.clear();ob.data.materials.append(mat)
    ob['source_geometry']=component['geometry'];ob['source_reference']='Native game pack; not WWD override';ob.hide_set(False);ob.hide_render=False
assert len([o for o in col.objects if not o.hide_get()])==1
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='OUTLINER':area.spaces.active.filter_text=''
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'native-hammer-preview.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),weapon=component['path'],attachment='weapon_1',hidden_previous_weapon=True,body_and_palette_changed=False,game_modified=False),indent=2),encoding='utf8')
print('NATIVE_HAMMER_PREVIEW_READY',flush=True)
