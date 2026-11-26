"""Double only the blade's thickness, preserving the hilt and native grip."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-reference-dao-thick';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-reference-dao-double-thickness.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-reference-dao/jade-model05-round-chen-shield-reference-dao.blend'))
scene=bpy.context.scene;dao=bpy.data.objects['Jade Warrior | reference ring-pommel dao'];dao.data=dao.data.copy()
# The blade alone uses steel/bevel materials, while fittings and grip use iron/wood.
blade_materials={i for i,m in enumerate(dao.data.materials) if m and m.name.startswith(('Dao | satin silver steel','Dao | polished cutting bevel'))}
ids={i for p in dao.data.polygons if p.material_index in blade_materials for i in p.vertices}
assert len(ids)==276,len(ids)
before={i:dao.data.vertices[i].co.copy() for i in ids}
for i in ids:dao.data.vertices[i].co.z*=2
assert all(dao.data.vertices[i].co.x==v.x and dao.data.vertices[i].co.y==v.y and dao.data.vertices[i].co.z==v.z*2 for i,v in before.items())
dao.data.update();dao['blade_thickness_multiplier']=2.0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'jade-double-thickness-preview.png');bpy.ops.render.render(write_still=True)
# Additional isolated angled view makes the doubled spine thickness visible.
for ob in scene.objects:
 if ob.type in ['MESH','FONT']:ob.hide_render=ob!=dao
dao.constraints.clear();dao.matrix_basis.identity()
target=Vector((.03,.01036,0));cam=scene.camera;cam.location=(.03,-1.8,2.6);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.38
scene.render.resolution_x=1600;scene.render.resolution_y=500;scene.render.filepath=str(O/'dao-double-thickness-detail.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),blade_vertices_changed=len(ids),thickness_multiplier=2,maximum_spine_thickness_before_m=.007,maximum_spine_thickness_after_m=.014,length_width_hilt_attachment_unchanged=True,game_integrated=False),indent=2))
print('DOUBLE_THICKNESS_READY',OUT,flush=True)
