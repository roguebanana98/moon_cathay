"""Reverse the custom blade bevel, preserving silhouette and native attachment."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/deer-jade-model05-dao-edge-corrected';O.mkdir(parents=True,exist_ok=True)
OUT=O/'jade-model05-dao-correct-cutting-edge.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-dao-flat-spine/jade-model05-dao-flat-thick-spine.blend'))
scene=bpy.context.scene
targets=[bpy.data.objects['Jade Warrior | reference ring-pommel dao'],bpy.data.objects['CUSTOM | Reference dao | native thickness']]
for ob in targets:
 ob.data=ob.data.copy();me=ob.data
 steel=next(i for i,m in enumerate(me.materials) if m and m.name.startswith('Dao | satin silver steel'))
 edge=next(i for i,m in enumerate(me.materials) if m and m.name.startswith('Dao | polished cutting bevel'))
 spine=next(i for i,m in enumerate(me.materials) if m and m.name.startswith('Dao | flat unsharpened spine'))
 for k in range(46):
  ring=[me.vertices[k*6+j] for j in range(6)]
  high=max(v.co.y for v in ring);low=min(v.co.y for v in ring)
  h=max(abs(v.co.z) for v in ring);bevel=min(.013,(high-low)*.38)
  # Native blade sharpens toward +Y. Keep current outline, reverse section wedge.
  coords=[(high,.00005),(high-bevel,h*.92),(low,h),(low,-h),(high-bevel,-h*.92),(high,-.00005)]
  for v,(y,z) in zip(ring,coords):v.co.y=y;v.co.z=z
 for p in me.polygons:
  if all(i<276 for i in p.vertices) and len(p.vertices)==4:
   sides={i%6 for i in p.vertices}
   p.material_index=spine if sides=={2,3} else edge if sides in [{0,1},{4,5},{0,5}] else steel
   p.use_smooth=False
 me.update();ob['cutting_edge_side']='Corrected to native +Y; opposite -Y is flat blunt spine'
 # Both section extremes now have explicitly different thicknesses.
 assert abs(me.vertices[0].co.z-me.vertices[5].co.z)<.00011
 assert abs(me.vertices[2].co.z-me.vertices[3].co.z)>.0094
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');targets[1].select_set(True);bpy.context.view_layer.objects.active=targets[1]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
scene.render.filepath=str(O/'correct-edge-comparison.png');bpy.ops.render.render(write_still=True)
(O/'edit-report.json').write_text(json.dumps(dict(scene=str(OUT),cutting_edge_side='+Y matches native Jade sword',blunt_spine_side='-Y',silhouette_hilt_attachment_unchanged=True,held_and_comparison_updated=True,game_integrated=False),indent=2))
print('CORRECT_EDGE_READY',OUT,flush=True)
