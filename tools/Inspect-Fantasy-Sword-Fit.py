import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-fantasy-longsword'
bpy.ops.wm.open_mainfile(filepath=str(O/'source-review.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');pts=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices])
rows=[]
for z in np.linspace(0,.98,41):
 a=pts[np.abs(pts[:,2]-z)<.0125]
 if len(a):rows.append(dict(z=round(float(z),4),n=len(a),xmin=float(a[:,0].min()),xmax=float(a[:,0].max()),ymin=float(a[:,1].min()),ymax=float(a[:,1].max())))
(O/'source-sections.json').write_text(json.dumps(rows,indent=2));print('SECTIONS',json.dumps(rows))
bpy.ops.wm.open_mainfile(filepath=str(R/'build/huyen-ve-v16-approved/huyen-ve-v16-animation-review.blend'))
print('VISIBLE',json.dumps([dict(name=o.name,type=o.type,render=o.hide_render,hidden=o.hide_get()) for o in bpy.context.scene.objects if not o.hide_get()]))
print('CAMERA',bpy.context.scene.camera.name if bpy.context.scene.camera else None)
print('ACTIONS',[(a.name,a.get('native_path','')) for a in bpy.data.actions if 'sword_stand' in str(a.get('native_path',''))])
