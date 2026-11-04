import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Sariwa_Damsel02_Textile_v1.blend'))
o=next(o for o in bpy.data.objects if o.type=='MESH' and 'Sariwa | weapon_5' in o.name)
print('STAFF',o.name,'BOUNDS',[(min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)])
print('MATRIX',list(o.matrix_world),'CONSTRAINT',[(c.type,c.subtarget,list(c.inverse_matrix)) for c in o.constraints])
print('UPPER',[(round(z,3),sum(1 for v in o.data.vertices if abs(v.co.z-z)<.01)) for z in sorted({round(v.co.z,2) for v in o.data.vertices})[-16:]])
for i in range(18):
    x=-1.10+i*.025;vs=[v.co for v in o.data.vertices if x<=v.co.x<x+.025]
    if vs:print('BIN',round(x,3),len(vs),'YZ',max(abs(v.y) for v in vs),max(abs(v.z) for v in vs))
