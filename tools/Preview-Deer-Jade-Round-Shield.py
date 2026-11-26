"""Round existing shield in its native mesh plane; preserve UV and attachment."""
import bpy,json,math
import bmesh
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-round-shield';O.mkdir(parents=True,exist_ok=True)
OUT=O/'deer24-model05-round-chen-shield.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-chen-shield/deer24-model05-neckguard06-chen-shield.blend'))
scene=bpy.context.scene
ob=next(o for o in scene.objects if o.type=='MESH' and 'shield' in o.get('source_geometry',''))
me=ob.data.copy();ob.data=me
# Native shield lies in XY. Audit rings before any mesh change.
verts=[v.co.copy() for v in me.vertices]
report=[]
for v in me.vertices:
 r=math.hypot(v.co.x,v.co.y)
 if r>.20:
  report.append([v.index,*v.co,r,math.atan2(v.co.y,v.co.x)])
(O/'ring-audit.json').write_text(json.dumps(report))
print('RING_AUDIT',len(report),flush=True)
# Add segments to the original rim, interpolating its existing texture UVs.
bm=bmesh.new();bm.from_mesh(me)
edges=[e for e in bm.edges if e.calc_length()>.045 and all(math.hypot(v.co.x,v.co.y)>.19 for v in e.verts) and math.hypot(*((e.verts[0].co+e.verts[1].co)*.5)[:2])>.19]
bmesh.ops.subdivide_edges(bm,edges=edges,cuts=7,use_grid_fill=True)
bm.to_mesh(me);bm.free()
outline=[Vector((verts[i].x,verts[i].y)) for i in [419,376,375,379,381,384,427,423]]
def cross(a,b):return a.x*b.y-a.y*b.x
def boundary(direction):
 hits=[]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  edge=b-a;den=cross(direction,edge)
  if abs(den)<1e-8:continue
  t=cross(a,edge)/den;u=cross(a,direction)/den
  if t>0 and -.0001<=u<=1.0001:hits.append(t)
 assert hits
 return min(hits)
changed=0
for v in me.vertices:
 r=math.hypot(v.co.x,v.co.y)
 if r<.15:continue
 direction=Vector((v.co.x/r,v.co.y/r));factor=.28/boundary(direction)
 influence=min(1,max(0,(r-.15)/.065));factor=1+(factor-1)*influence
 v.co.x*=factor;v.co.y*=factor;changed+=1
me.update();ob.name='Model05 | round shield | Chen'
ob['edit']='Original polygon rim subdivided and reshaped to circle; original UVs/material/prop pivot preserved'
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'round-shield-preview.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),original_vertices=len(verts),vertices=len(me.vertices),reshaped_vertices=changed,round_radius=.28,original_UV_interpolated=True,attachment_unchanged=True,game_integrated=False),indent=2))
print('ROUND_SHIELD_READY',OUT,flush=True)
