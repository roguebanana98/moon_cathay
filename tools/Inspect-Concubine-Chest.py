import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';bpy.ops.wm.open_mainfile(filepath=str(O/'celestial-concubine-01-no-gold-ornaments.blend'))
for name in ['Iron_Body','IronWarriors_01']:
 ob=bpy.data.objects[name];me=ob.data
 print(name)
 for z in [1.14,1.22,1.3,1.36,1.42]:
  vs=[v for v in me.vertices if abs(v.co.z-z)<.015 and abs(v.co.x)<.16 and v.co.y<-.04]
  print(z,len(vs),'y', (min(v.co.y for v in vs),max(v.co.y for v in vs)) if vs else None)
