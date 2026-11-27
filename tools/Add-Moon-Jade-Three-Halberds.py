"""Add three native halberds to a new copy of the four-unit gallery."""
import bpy,json,math,sys,ast,importlib.util
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-reskin-v2';D=R/'reference/local/moon-jade-expanded';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
OUT=O/'moon-jade-four-units-three-halberds-upright.blend';assert not OUT.exists()
addon_dir=Path(C['rpfm']).parent.parent/'rmv2-addon';spec=importlib.util.spec_from_file_location('io_scene_rmv2',addon_dir/'__init__.py',submodule_search_locations=[str(addon_dir)]);addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
from io_scene_rmv2 import import_rmv2,materials
import subprocess
bpy.ops.wm.open_mainfile(filepath=str(O/'moon-jade-four-unit-gallery.blend'));scene=bpy.context.scene
converted={};tree=ast.parse((R/'tools/Review-Moon-Jade-Family-V2.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='model'],type_ignores=[]),'<native model preview helper>','exec'))
data=json.loads((O/'three-halberds-assets.json').read_text());col=bpy.data.collections.new('05 | NATIVE HALBERDS | 01 - 02 - 03');scene.collection.children.link(col)
mat=bpy.data.materials.new('Three halberds | labels');mat.use_nodes=True;s=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');s.inputs['Base Color'].default_value=(.85,.92,1,1)
if 'Emission Color' in s.inputs:s.inputs['Emission Color'].default_value=(.85,.92,1,1)
if 'Emission Strength' in s.inputs:s.inputs['Emission Strength'].default_value=.8
orientation=Matrix(((0,1,0,0),(0,0,-1,0),(-1,0,0,0),(0,0,0,1)))
added=[]
for i,entry in enumerate(data['models']):
 before=set(bpy.data.collections);obs=model(entry);x=6.2+1.4*i
 for ob in obs:
  basis=ob.matrix_basis.copy();ob.parent=None;ob.constraints.clear();ob.matrix_world=orientation@basis
 bpy.context.view_layer.update();low=min((ob.matrix_world@Vector(c)).z for ob in obs for c in ob.bound_box)
 for ob in obs:
  ob.matrix_world=Matrix.Translation((x,0,.03-low))@ob.matrix_world
  for parent in list(ob.users_collection):parent.objects.unlink(ob)
  col.objects.link(ob);ob.name='HALBERD %02d | %s'%(i+1,ob.name);ob['native_source']=entry['path'];added.append(ob)
 for collection in list(set(bpy.data.collections)-before):
  if not collection.all_objects:bpy.data.collections.remove(collection)
 cv=bpy.data.curves.new('HALBERD %02d'%(i+1),'FONT');cv.body='HALBERD %02d'%(i+1);cv.align_x='CENTER';cv.size=.11;cv.materials.append(mat);label=bpy.data.objects.new(cv.body,cv);col.objects.link(label);label.location=(x,-.15,-.17);label.rotation_euler=(math.pi/2,0,0)
cd=bpy.data.cameras.new('Compare | Halberds 01-03');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;target=Vector((7.6,0,1.3));cam.location=(7.8,-12,2.0);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=4.25;cam.hide_set(True)
scene.render.resolution_x=1600;scene.render.resolution_y=1250;scene.cycles.samples=8
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT')
note=bpy.data.texts.new('Three native halberds');note.write('Native Jade Warrior halberd models01/02/03, at original scale with native material pivots retained. Separate comparison display to the right of the four existing units. No mod/game changes. Previous gallery and live window preserved.')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'three-halberds-comparison.png');bpy.ops.render.render(write_still=True)
(O/'three-halberds-gallery.json').write_text(json.dumps(dict(scene=str(OUT),halberds=[m['path'] for m in data['models']],original_four_units_preserved=True,game_changed=False),indent=2));print('THREE_HALBERDS_GALLERY_READY',OUT,flush=True)
