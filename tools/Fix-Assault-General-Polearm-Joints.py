"""Make model09's offset polearm collar coaxial with its shaft and blade."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-generals-preview'
SOURCE=O/'moon-generals-bastion-guandao-aligned.blend'
OUT=O/'moon-generals-assault-polearm-connected.blend'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
col=bpy.data.collections['Weapons | Assault General']
hidden=bpy.data.collections['Hidden originals | Assault General']
originals=[o for o in col.objects if o.type=='MESH' and not o.hide_get()]
assert len(originals)==4
collar=next(o for o in originals if 'halberd_2h__.003' in o.name)
pole=next(o for o in originals if 'sword_1h_01_' in o.name)
# Main shaft is the existing 18-vertex cylindrical section from x=-.666 to1.106.
shaft_vertices=[v.co for v in pole.data.vertices if -.67<v.co.x<1.11 and .005<v.co.y<.041 and abs(v.co.z)<.022]
shaft_y=(.0068359375+.0399169921875)/2
collar_y=(min(v.co.y for v in collar.data.vertices)+max(v.co.y for v in collar.data.vertices))/2
offset=Vector((-.003,shaft_y-collar_y,0))
copies=[]
for source in originals:
    ob=source.copy();ob.data=source.data.copy();col.objects.link(ob)
    ob.name='Connected polearm part | '+source.name
    if source==collar or 'shape_0_weighted' in source.name:
        for v in ob.data.vertices:v.co+=offset
    ob.hide_set(False);ob.hide_render=False;copies.append(ob)
    col.objects.unlink(source);hidden.objects.link(source);source.hide_set(True);source.hide_render=True
# Preserve separate original pieces hidden. All copied parts have the exact
# same weapon frame, so joining introduces no transforms or grip displacement.
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.object.join()
weapon=bpy.context.object;weapon.name='Assault | Connected model09 polearm'
assert len(weapon.constraints)==1 and weapon.constraints[0].subtarget=='be_prop_0'
weapon['joint_fix']='Collar and tied banner moved onto original shaft axis; collar overlaps blade base by1.5mm'
weapon['original_parts']='Hidden originals | Assault General'
weapon['source_geometry']='1/shizi/deershizishuo.rigid_model_v2'
bpy.ops.object.select_all(action='DESELECT');weapon.select_set(True);bpy.context.view_layer.objects.active=weapon
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'assault-polearm-joint-fix.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),collar_offset=list(offset),visible_weapon_objects=1,originals_retained_hidden=True,shaft_and_blade_original_dimensions=True,body_and_bastion_changed=False,game_modified=False),indent=2),encoding='utf8')
print('ASSAULT_POLEARM_JOINTS_CONNECTED',flush=True)
