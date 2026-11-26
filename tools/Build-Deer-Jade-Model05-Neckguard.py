"""Separate editable model05 preview with only model06 rear neckguard."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-neckguard';O.mkdir(parents=True,exist_ok=True)
OUT=O/'deer24-model05-neckguard06.blend'
assert not OUT.exists(),'Preserve prior edit'
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-reskin-gallery/deer24-jade-warriors-reskin-gallery.blend'))
scene=bpy.context.scene
base=bpy.data.collections['05 | beitingsheshou5'];donor=bpy.data.collections['06 | beitingsheshou_lancer']
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE' and 'JADE 05' in o.name)
source=next(o for o in donor.objects if o.get('source_part_index')==5)
comps=json.loads((R/'build/deer-jade-reskin-gallery/donor-neck-components.json').read_text())
# The rear panel comprises five UV-split connected components behind the head.
rear=[c for c in comps if c['bounds'][1][0]>.06 and c['bounds'][2][1]>1.65 and max(abs(v) for v in c['bounds'][0])<.085]
ids=set(i for c in rear for i in c['ids']);assert len(ids)==144,len(ids)
ob=source.copy();ob.data=source.data.copy();base.objects.link(ob)
ob.name='Model05 | rear neckguard from Model06'
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in ids],context='VERTS');bm.to_mesh(ob.data);bm.free()
ob.parent=arm
for mod in ob.modifiers:
 if mod.type=='ARMATURE':mod.object=arm
ob['edit']='Rear panel only; original donor mesh coordinates, UV, material and weights retained'
arm.location.x=0
keep=set(base.objects)|{arm,scene.camera}
for x in list(scene.objects):
 if x.type=='LIGHT':keep.add(x)
for x in list(scene.objects):
 if x not in keep:bpy.data.objects.remove(x,do_unlink=True)
scene.frame_set(1);bpy.context.view_layer.update()
target=Vector((0,0,1.47));camera=scene.camera;camera.data.ortho_scale=1.15
camera.location=(2.8,3.5,1.95);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1100;scene.render.resolution_y=1100
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=target;sp.region_3d.view_distance=2.8;sp.region_3d.view_rotation=camera.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True);bpy.context.view_layer.objects.active=ob
note=bpy.data.texts.new('EDIT | Model05 + rear neckguard06')
note.write('Model05 body, helmet, face, original side panels and props preserved. Added only 144 vertices comprising rear panel from model06 part5. Same humanoid01e bind and native weights; no mesh offset, recolour, game export or integration. Gallery and Workshop source untouched. Preview pending user review.')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'neckguard-back.png');bpy.ops.render.render(write_still=True)
camera.location=(2.8,-3.5,1.95);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(O/'neckguard-front.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),base='gallery model05',donor='gallery model06 part5 rear panel only',added_vertices=len(ob.data.vertices),added_polygons=len(ob.data.polygons),donor_component_count=len(rear),game_integrated=False,packed_images=sum(bool(i.packed_file) for i in bpy.data.images)),indent=2))
print('MODEL05_NECKGUARD_READY',OUT,flush=True)
