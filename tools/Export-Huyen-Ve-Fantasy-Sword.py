"""Export four UV-preserving sword LODs from the approved Blender-only preview."""
import bpy,addon_utils,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-fantasy-longsword'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.open_mainfile(filepath=str(O/'huyen-ve-fantasy-sword-preview.blend'));addon_utils.enable('io_scene_rmv2')
source=bpy.data.objects['HuyenVe_Fantasy_Longsword_PREVIEW'];rig=bpy.data.objects['humanoid01e_NATIVE_BIND'];source.hide_set(True);source.hide_render=True
root=bpy.data.collections.new('HuyenVe_Fantasy_Sword_EXPORT');bpy.context.scene.collection.children.link(root)
root.rmv2.is_rmv2_root=True;root.rmv2.version='8';root.rmv2.skeleton_name=''
files=json.loads((O/'texture-conversion.json').read_text())['files'];lods=[];rows=[]
for i,target in enumerate([12000,6000,3000,1200]):
 col=bpy.data.collections.new('fantasy_sword_lod'+str(i));root.children.link(col);col.rmv2.lod_level=i;col.rmv2.camera_distance=[10,20,30,10000][i];col.rmv2.lod_values_set=True
 obj=source.copy();obj.data=source.data.copy();obj.name='fantasy_sword_lod'+str(i);col.objects.link(obj)
 obj.hide_set(False);obj.hide_render=False;obj.constraints.clear();obj.parent=None;obj.matrix_world=Matrix.Identity(4)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 dec=obj.modifiers.new('Game_LOD_reduction','DECIMATE');dec.ratio=target/466979;dec.use_collapse_triangulate=True
 bpy.ops.object.modifier_apply(modifier=dec.name);obj.data.calc_loop_triangles()
 assert len(obj.data.loop_triangles)<=target+4 and len(obj.data.uv_layers)==1
 obj.rmv2.vertex_format='STATIC';obj.rmv2.material_id='AUTO';obj.rmv2.alpha_mode='OPAQUE';obj.rmv2.textures.clear()
 for typ,suffix in [(27,'base_colour'),(29,'material_map'),(1,'normal'),(3,'mask')]:
  slot=obj.rmv2.textures.add();slot.set_type_from_int(typ);slot.path=next(p for p in files if p.endswith('_'+suffix+'.dds'))
 obj.rmv2.textures_initialized=True
 lods.append(obj);rows.append(dict(level=i,vertices=len(obj.data.vertices),triangles=len(obj.data.loop_triangles),distance=col.rmv2.camera_distance))
 print('LOD_READY',rows[-1],flush=True)
def layer_find(layer):
 if layer.collection==root:return layer
 for child in layer.children:
  result=layer_find(child)
  if result:return result
bpy.context.view_layer.active_layer_collection=layer_find(bpy.context.view_layer.layer_collection)
bpy.ops.object.select_all(action='DESELECT');lods[0].select_set(True);bpy.context.view_layer.objects.active=lods[0]
path=O/'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_sword.rigid_model_v2';path.parent.mkdir(parents=True,exist_ok=True)
assert bpy.ops.export_scene.rmv2(filepath=str(path),source='COLLECTION',skeleton_name='',auto_lods=False,apply_modifiers=True)=={'FINISHED'}
# Attach only for review after exporting; the game uses the existing VMD attachment.
for i,obj in enumerate(lods):
 con=obj.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='weapon_2'
 obj.hide_set(i>0);obj.hide_render=i>0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'huyen-ve-fantasy-sword-game-lods.blend'))
(O/'lod-export.json').write_text(json.dumps(dict(status='exported',lods=rows,preview_source_sha256=hashlib.sha256((O/'huyen-ve-fantasy-sword-preview.blend').read_bytes()).hexdigest(),rmv2_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_source_preserved=True),indent=2))
