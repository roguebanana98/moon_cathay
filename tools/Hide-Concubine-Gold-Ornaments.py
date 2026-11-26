"""Retain shoulder plates, hide separate gold ornament islands and dragon heads."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/celestial-concubines-dual-knives';SOURCE=O/'celestial-concubine-01-black-bodysuit.blend';OUT=O/'celestial-concubine-01-no-gold-ornaments.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));ob=bpy.data.objects['IronWarriors_01'];me=ob.data
rows=json.loads((O/'gold-components.json').read_text());selected={r['key'] for r in rows if r['gold']>.8 and r['lo'][2]>.2};shoes={r['key'] for r in rows if r['gold']>.8 and r['lo'][2]<=.2}
parent=list(range(len(me.vertices)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in me.edges:
 a,b=map(find,e.vertices);parent[b]=a
ids={v.index for v in me.vertices if find(v.index) in selected}
assert len(ids)>1000
assert 2408 not in selected and 2600 not in selected
# Structural footwear remains fully closed while losing its gold colour.
ob.data=me.copy();me=ob.data;mat=bpy.data.materials['Black fitted leg fabric'].copy();mat.name='Charcoal footwear';idx=len(me.materials);me.materials.append(mat)
for f in me.polygons:
 if find(f.vertices[0]) in shoes:f.material_index=idx
backup=ob.copy();backup.data=me.copy();backup.name='HIDDEN | Gold ornaments and shoulder dragon heads'
for col in ob.users_collection:col.objects.link(backup)
def subset(mesh,keep):
 bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(mesh);bm.free();mesh.update()
subset(backup.data,ids);backup.hide_set(True);backup.hide_render=True
subset(me,set(range(len(me.vertices)))-ids)
scene=bpy.context.scene;scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=(0,0,.97);sp.region_3d.view_distance=2.8;sp.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'hidden-gold-report.json').write_text(json.dumps(dict(scene=str(OUT),hidden_object=backup.name,hidden_vertices=len(ids),hidden_components=len(selected),hidden_faces=len(backup.data.polygons),retained_shoulder_plate_components=[2408,2600],structural_footwear_gold_components_recoloured=len(shoes),weapons_unchanged=True,game_modified=False),indent=2))
print('GOLD_ORNAMENTS_HIDDEN',len(selected),len(ids),flush=True)
