"""Import the user's FBX into a new inspection scene; leave original inputs untouched."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/authored/ancient warrior armor 3d model'
OUT=ROOT/'build/model-intake/huyen-ve-tripo-20261102'
OUT.mkdir(parents=True,exist_ok=True)
files=list(SOURCE.glob('*.fbx'))
assert len(files)==1, 'Expected one FBX'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(files[0]),use_image_search=True)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
assert meshes,'No mesh imported'
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
low=Vector([min(p[i] for p in points) for i in range(3)])
high=Vector([max(p[i] for p in points) for i in range(3)])
center=(low+high)/2
height=max(high-low)
report=dict(date='2026-11-02',source=str(files[0]),objects=[],rigs=[],
            bounds_min=list(low),bounds_max=list(high),dimensions=list(high-low),
            images=[],actions=[a.name for a in bpy.data.actions],
            input_hashes={p.relative_to(SOURCE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob('*') if p.is_file()})
for o in meshes:
    o.data.calc_loop_triangles()
    report['objects'].append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),
         triangles=len(o.data.loop_triangles),uv_layers=[u.name for u in o.data.uv_layers],
         vertex_groups=len(o.vertex_groups),weighted_vertices=sum(bool(v.groups) for v in o.data.vertices),
         materials=[m.name if m else None for m in o.data.materials],
         modifiers=[dict(type=m.type,name=m.name) for m in o.modifiers],
         location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale)))
for o in rigs:report['rigs'].append(dict(name=o.name,bones=len(o.data.bones)))
for im in bpy.data.images:
    if im.source!='FILE':continue
    path=Path(bpy.path.abspath(im.filepath))
    if not path.is_file():
        matches=list(SOURCE.rglob(path.name))
        if len(matches)==1:im.filepath=str(matches[0]);im.reload();path=matches[0]
    report['images'].append(dict(name=im.name,path=str(path),exists=path.is_file(),size=list(im.size),has_data=im.has_data))
report['totals']={k:sum(o[k] for o in report['objects']) for k in ['vertices','polygons','triangles','weighted_vertices']}
report['material_nodes']={m.name:[dict(type=n.type,label=n.label,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes] for m in bpy.data.materials if m.use_nodes}
(ROOT/'reports/huyen-ve-tripo-intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Inspection World');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=900;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def aim(o,p):o.rotation_euler=(p-o.location).to_track_quat('-Z','Y').to_euler()
for loc,energy in [((-1.4,-2,1.7),220),((1.6,-.7,.8),130),((0,1.4,1.6),180)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(loc)*height)
    o=bpy.context.object;o.data.energy=energy*height**2;o.data.size=height*1.4;aim(o,center)
bpy.ops.object.camera_add(location=center+Vector((0,-3.0,.05))*height)
camera=bpy.context.object;aim(camera,center);camera.data.type='ORTHO';camera.data.ortho_scale=height*1.15;scene.camera=camera
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'huyen-ve-tripo-inspection.blend'))
for name,offset in [('front',(0,-3,.05)),('side',(3,0,.05))]:
    camera.location=center+Vector(offset)*height;aim(camera,center)
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('INTAKE_REPORT',json.dumps({k:report[k] for k in ['totals','rigs','actions','dimensions','images']}))
