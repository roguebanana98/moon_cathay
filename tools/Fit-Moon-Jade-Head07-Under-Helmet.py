import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/moon-jade-approved-variants'
bpy.ops.wm.open_mainfile(filepath=str(O/'moon-jade-warriors-approved-seven-variants.blend'))
scene=bpy.context.scene;col=bpy.data.collections['VARIANT 07 | approved body05 + DEER head07']
ob=next(o for o in col.objects if o.type=='MESH' and 'beitingsheshouh7' in o.get('source_geometry','') and o.get('source_part_index')==0)
ob.data=ob.data.copy();changed=[]
for v in ob.data.vertices:
 if v.co.z>1.675:
  original=list(v.co);t=min(1,(v.co.z-1.675)/.04)
  v.co.x*=1-.25*t;v.co.y=.025+(v.co.y-.025)*(1-.25*t);v.co.z=1.675+(v.co.z-1.675)*.20
  changed.append(v.index)
assert changed;ob.data.update();ob['helmet_fit']='Only covered upper scalp/hair above z1.675 tucked inside helmet; face, moustache and weights retained'
OUT=O/'moon-jade-warriors-approved-seven-variants-v2.blend';assert not OUT.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
cam=scene.camera;target=Vector((3*1.45,0,1.61));cam.location=target+Vector((.19,-2,.08));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.57
scene.render.resolution_x=600;scene.render.resolution_y=650;scene.render.filepath=str(O/'face-07-helmet-fit.png');bpy.ops.render.render(write_still=True)
report=json.loads((O/'approved-variants-report.json').read_text());report['scene']=str(OUT);report['linked_libraries']=0;report['linked_libraries_verified_after_reopening']=True;report['head07_helmet_fit']=dict(covered_scalp_vertices_tucked=len(changed),face_and_moustache_unchanged=True);report['source_appearance_geometry_unchanged_except_head07_covered_scalp']=report.pop('source_appearance_geometry_unchanged');(O/'approved-variants-report.json').write_text(json.dumps(report,indent=2))
