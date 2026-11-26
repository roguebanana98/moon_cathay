"""Fit WWD Guan Yu's guandao to the native Celestial General weapon frame."""
import bpy, addon_utils, sys, json, subprocess, hashlib, math
from pathlib import Path
from mathutils import Matrix
R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-generals-preview'
D = R / 'reference/local/wwd-all-lords'
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
OUT = O / 'moon-generals.blend'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(O / 'moon-generals-review.blend'))
sys.path.insert(0, str(R.parent / 'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
root = bpy.data.objects['Bastion General | Root']
rig = bpy.data.objects['Bastion General | Native humanoid01e']
col = bpy.data.collections['Weapons | Bastion General']
hidden = bpy.data.collections['Hidden originals | Bastion General']
for ob in list(col.objects):
    col.objects.unlink(ob)
    hidden.objects.link(ob)
    ob.hide_set(True)
    ob.hide_render = True
c = json.loads((O / 'guandao.json').read_text(encoding='utf8'))
converted = {}
for typ, path in {tuple(t) for p in c['parts'] for t in p['textures']}:
    folder = O / 'preview-textures' / hashlib.sha256(path.encode()).hexdigest()[:12]
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / (Path(path).stem + '.png')
    if not dest.exists():
        subprocess.run([C['texconv'], '-nologo', '-y', '-ft', 'png', '-w', '1024', '-h', '1024', '-o', str(folder), str(D/path)], check=True, stdout=subprocess.DEVNULL)
    converted[path] = dest.relative_to(O).as_posix()
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None
before = set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(D/c['geometry']), build_materials=False, import_all_lods=False, attach_armature=False)
objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
lod = next(k for o in objs for k in o.users_collection if 'lod0' in k.name)
ordered = [o for o in lod.objects if o.type == 'MESH']
assert len(ordered) == len(c['parts'])
transform = Matrix.Translation((-.65, 0, 0)) @ Matrix.Rotation(math.pi/2, 4, 'X') @ Matrix.Diagonal((.75, 1, 1, 1))
for ob, part in zip(ordered, c['parts']):
    for old in list(ob.users_collection):
        old.objects.unlink(ob)
    col.objects.link(ob)
    ob.name = 'Guan Yu guandao | ' + ob.name
    ob.data.transform(transform)
    ob.parent = root
    ob.matrix_parent_inverse.identity()
    ob.matrix_basis.identity()
    con = ob.constraints.new('COPY_TRANSFORMS')
    con.target = rig
    con.subtarget = 'weapon_1'
    ob['source_geometry'] = c['geometry']
    ob['source_wsmodel'] = c['path']
    pairs = [(typ, converted[path]) for typ, path in part['textures']]
    mat = materials.build_material('Bastion guandao | ' + part['name'], pairs, 'TRANSPARENT' if part['alpha'] else 'OPAQUE', str(O))
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    # Keep weapon ornamentation, normal maps and metal response; remove jade/gold hue.
    bs = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if bs.inputs['Base Color'].is_linked:
        source = bs.inputs['Base Color'].links[0].from_socket
        bw = mat.node_tree.nodes.new('ShaderNodeRGBToBW')
        mat.node_tree.links.new(source, bw.inputs[0])
        mat.node_tree.links.new(bw.outputs[0], bs.inputs['Base Color'])

# Donor's decorative pommel is separated from the shaft. Bridge only that
# existing gap with a narrow continuation of the shaft; retain original parts.
verts = [(x, .012*math.cos(a*math.tau/16), .012*math.sin(a*math.tau/16))
         for x in (1.08, 1.75) for a in range(16)]
faces = [(a, (a+1)%16, (a+1)%16+16, a+16) for a in range(16)]
mesh = bpy.data.meshes.new('Guandao shaft continuation')
mesh.from_pydata(verts, [], faces)
mesh.transform(transform)
shaft = bpy.data.objects.new('Guan Yu guandao | Shaft continuation', mesh)
col.objects.link(shaft)
shaft.parent = root
con = shaft.constraints.new('COPY_TRANSFORMS'); con.target = rig; con.subtarget = 'weapon_1'
mat = bpy.data.materials.new('Bastion guandao | Blackened shaft'); mat.use_nodes = True
bs = mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value = (.045,.05,.06,1)
bs.inputs['Metallic'].default_value = .65
bs.inputs['Roughness'].default_value = .42
shaft.data.materials.append(mat)

# Desaturate only yellow/gold pixels in the preserved head texture. Skin outside
# that hue interval keeps its original colour; no texture file is edited.
for ob in bpy.data.collections['Body | Bastion General'].objects:
    if ob.type != 'MESH':
        continue
    for slot in ob.material_slots:
        original = slot.material
        if not original or original.name.startswith('Bastion |') or not original.use_nodes:
            continue
        mat = original.copy()
        mat.name = 'Bastion | Preserve skin, silver ornament | ' + original.name
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        color = bs.inputs['Base Color']
        if color.is_linked:
            source = color.links[0].from_socket
            hsv = nodes.new('ShaderNodeSeparateColor'); hsv.mode = 'HSV'
            links.new(source, hsv.inputs[0])
            mask = nodes.new('ShaderNodeValToRGB'); mask.color_ramp.interpolation = 'CONSTANT'
            mask.color_ramp.elements[0].position = 0; mask.color_ramp.elements[0].color = (0,0,0,1)
            mask.color_ramp.elements[1].position = .085; mask.color_ramp.elements[1].color = (1,1,1,1)
            stop = mask.color_ramp.elements.new(.20); stop.color = (0,0,0,1)
            links.new(hsv.outputs[0], mask.inputs[0])
            bw = nodes.new('ShaderNodeRGBToBW'); links.new(source, bw.inputs[0])
            mix = nodes.new('ShaderNodeMixRGB')
            links.new(mask.outputs['Color'], mix.inputs[0]); links.new(source, mix.inputs[1]); links.new(bw.outputs[0], mix.inputs[2]); links.new(mix.outputs[0], color)
        slot.material = mat

while True:
    empty = [k for k in bpy.data.collections if not k.objects and not k.children]
    if not empty: break
    for k in empty: bpy.data.collections.remove(k)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.overlay.show_extras = False
            area.spaces.active.region_3d.view_distance = 5.3
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None
bpy.context.scene.frame_set(1)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
report = json.loads((O/'preview-report.json').read_text())
report.update(scene=str(OUT), bastion_weapon=c['path'], bastion_weapon_transform=[list(row) for row in transform])
(O/'checkpoint.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print('REFINED_MOON_GENERALS_READY', flush=True)
