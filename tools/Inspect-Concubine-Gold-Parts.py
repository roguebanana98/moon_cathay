import bpy,json,numpy as np,colorsys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives'
bpy.ops.wm.open_mainfile(filepath=str(O/'celestial-concubine-01-black-bodysuit.blend'));ob=bpy.data.objects['IronWarriors_01'];me=ob.data
parent=list(range(len(me.vertices)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in me.edges:
 a,b=map(find,e.vertices);parent[b]=a
parts={}
for v in me.vertices:parts.setdefault(find(v.index),[]).append(v.index)
mat=ob.data.materials[0];images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
print('IMAGES',[(im.name,list(im.size)) for im in images])
im=next(im for im in images if any(s in im.name.lower() for s in ['base','diffuse']))
pix=np.array(im.pixels[:]).reshape(im.size[1],im.size[0],4);uv=me.uv_layers.active.data
faces={}
for p in me.polygons:faces.setdefault(find(p.vertices[0]),[]).append(p)
rows=[]
for k,ids in parts.items():
 vs=[me.vertices[i] for i in ids];cols=[]
 for p in faces.get(k,[]):
  co=sum((uv[i].uv for i in p.loop_indices),__import__('mathutils').Vector((0,0)))/len(p.loop_indices)
  cols.append(pix[int(co.y%1*(im.size[1]-1)),int(co.x%1*(im.size[0]-1)),:3])
 if not cols:continue
 hsv=[colorsys.rgb_to_hsv(*map(float,c)) for c in cols]
 gold=sum(.055<h<.19 and s>.23 and v>.16 for h,s,v in hsv)/len(hsv)
 row=dict(key=k,vertices=len(ids),faces=len(faces[k]),lo=[min(v.co[j] for v in vs) for j in range(3)],hi=[max(v.co[j] for v in vs) for j in range(3)],gold=gold,mean=np.mean(cols,axis=0).tolist())
 rows.append(row)
print('COMPONENTS',len(rows))
for row in rows:
 if row['gold']>.25 or row['lo'][2]>1.4:print(json.dumps(row))
(O/'gold-components.json').write_text(json.dumps(rows,indent=2))
