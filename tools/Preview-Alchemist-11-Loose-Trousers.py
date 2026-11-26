"""Reversible black trousers fitted from the model's native weighted legs."""
import bpy, math, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'build/alchemist-11-black-trousers';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/alchemist-11-short-outfit/alchemist-11-short-outfit-animation.blend'))
source=bpy.data.objects['wef_wardancers_legs_01_submesh_1.003']
trousers=source.copy();trousers.data=source.data.copy();trousers.name='Model 11 | Loose black trousers'
for col in source.users_collection:col.objects.link(trousers)
trousers.hide_set(False);trousers.hide_render=False
source.hide_set(True);source.hide_render=True
source['restore']='Original legs retained under loose trousers; hidden to avoid clipping.'
material=bpy.data.materials.new('Moonshadow | Matte black woven cloth');material.use_nodes=True
nodes=material.node_tree.nodes;links=material.node_tree.links
bsdf=nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.012,.014,.019,1)
bsdf.inputs['Roughness'].default_value=.87
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=210
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.001
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
trousers.data.materials.clear();trousers.data.materials.append(material)
for p in trousers.data.polygons:p.material_index=0;p.use_smooth=True
for v in trousers.data.vertices:
    x,y,z=v.co
    # Loose thigh/knee volume; taper into existing boots and underneath belt.
    t=max(0,min(1,(z-.37)/.18))*max(0,min(1,(1.075-z)/.22))
    v.co.x=x*(1+.72*t)
    v.co.y=(y-.025)*(1+1.0*t)+.025
    # Small relaxed folds, kept symmetrical and attached to original bone weights.
    ripple=.0035*t*math.sin(z*66+abs(x)*12)
    v.co.y+=ripple if y>.025 else -ripple
trousers.data.update()
trousers['construction']='Native leg topology and bone weights; widened thigh/knee and tapered boot cuff.'
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
assert any(m.type=='ARMATURE' and m.object==rig for m in trousers.modifiers)
assert len(trousers.data.vertices)==len(source.data.vertices)
report={'output':'alchemist-11-loose-black-trousers-v2.blend','vertices':len(trousers.data.vertices),'faces':len(trousers.data.polygons),'original_hidden':source.name,'sample_frames':[],'deployment':False}
for frame in (1,75,160,264,320,410):
    bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
    evaluated=trousers.evaluated_get(deps);mesh=evaluated.to_mesh()
    assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
    report['sample_frames'].append({'frame':frame,'finite':True})
    evaluated.to_mesh_clear()
bpy.context.scene.frame_set(1)
from mathutils import Quaternion,Vector
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_rotation=Quaternion((.8001,.5599,-.1222,-.1746))
            space.region_3d.view_distance=3.0
            space.region_3d.view_location=rig.matrix_world.translation+Vector((0,0,.9))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(O/report['output']),compress=True)
(O/'trousers-report.json').write_text(json.dumps(report,indent=2))
print('TROUSERS_OK',report)
