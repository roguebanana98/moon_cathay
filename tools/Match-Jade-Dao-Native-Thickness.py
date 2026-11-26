"""Match new dao blade thickness to the preserved original Jade Warrior blade."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-dao-native-thickness';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-dao-native-thickness.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-reference-dao-thick/jade-model05-reference-dao-double-thickness.blend'))
scene=bpy.context.scene;dao=bpy.data.objects['Jade Warrior | reference ring-pommel dao'];dao.data=dao.data.copy()
native=next(o for o in scene.objects if o.type=='MESH' and o.get('source_geometry','').endswith('/cth_jade_warrior_sword_1h_01.rigid_model_v2'))
# The original blade lies below x=.20; hilt, guard and fittings lie above it.
native_points=[v.co for v in native.data.vertices if v.co.x<.20]
target=max(v.z for v in native_points)-min(v.z for v in native_points)
mats={i for i,m in enumerate(dao.data.materials) if m and m.name.startswith(('Dao | satin silver steel','Dao | polished cutting bevel'))}
ids={i for p in dao.data.polygons if p.material_index in mats for i in p.vertices}
before=[v.co.copy() for v in dao.data.vertices];original=max(before[i].z for i in ids)-min(before[i].z for i in ids)
ratio=target/original
for i in ids:dao.data.vertices[i].co.z*=ratio
actual=max(dao.data.vertices[i].co.z for i in ids)-min(dao.data.vertices[i].co.z for i in ids)
assert math.isclose(actual,target,abs_tol=1e-8)
assert all(v.co.x==before[i].x and v.co.y==before[i].y and (i in ids or v.co.z==before[i].z) for i,v in enumerate(dao.data.vertices))
dao.data.update();dao['blade_thickness_multiplier']=target/.007;dao['matched_native_blade_thickness_m']=target
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'jade-native-thickness-preview.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),native_blade_vertices_measured=len(native_points),native_blade_thickness_m=target,previous_blade_thickness_m=original,updated_blade_thickness_m=actual,length_width_hilt_attachment_unchanged=True,game_integrated=False),indent=2))
print('NATIVE_THICKNESS_READY',target,OUT,flush=True)
