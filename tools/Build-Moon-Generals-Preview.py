"""Preserve user-edited WWD bodies; build private Assault/Bastion review scene."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Matrix, Vector

R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-generals-preview'
SOURCE = O / 'user-edited-gallery-source.blend'
OUT = O / 'moon-generals-review.blend'
assert SOURCE.exists() and not OUT.exists(), 'Preserve existing checkpoints'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
roots = {n: next(o for o in bpy.data.objects if o.name.startswith('%02d |' % n)) for n in [1, 7, 8, 9]}
groups = {n: list(root.children) for n, root in roots.items()}
rigs = {n: next(o for o in group if o.type == 'ARMATURE') for n, group in groups.items()}
report = {'source': str(SOURCE), 'game_modified': False, 'models': [], 'weapons': []}

def collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent.children if parent else scene.collection.children).link(col)
    return col

def move(ob, col):
    for old in list(ob.users_collection):
        old.objects.unlink(ob)
    col.objects.link(ob)

def is_weapon(ob):
    return ob.type == 'MESH' and any(c.type == 'COPY_TRANSFORMS' for c in ob.constraints)

retained = set()
for num, title, x in [(8, 'Assault General', -1.65), (1, 'Bastion General', 1.65)]:
    root = roots[num]
    top = collection(title + ' | MODEL %02d' % num)
    body = collection('Body | ' + title, top)
    weapons = collection('Weapons | ' + title, top)
    alternatives = collection('Hidden originals | ' + title, top)
    visible_before = []
    for ob in groups[num]:
        hidden = ob.hide_get()
        if ob.type == 'MESH' and not hidden and not is_weapon(ob):
            visible_before.append(ob.name)
        ob['original_gallery_name'] = ob.name
        if is_weapon(ob):
            hidden = True
        move(ob, alternatives if hidden and ob.type != 'ARMATURE' else body)
        ob.hide_set(hidden)
        ob.hide_render = hidden
        retained.add(ob)
    move(root, top)
    root.name = title + ' | Root'
    root.location = (x, 0, 0)
    retained.add(root)
    rigs[num].name = title + ' | ' + ('Native humanoid01b' if num == 8 else 'Native humanoid01e')
    rigs[num].hide_set(True)
    rigs[num].hide_render = True
    root['role'] = 'Line breaker / assault' if num == 8 else 'Line holder / defence'
    root['skill_base'] = 'Celestial General (planned; no DB integration in this preview)'
    report['models'].append(dict(name=title, source_model=num, original_visible_body=visible_before,
                                 animation='cth_hu1b_elf_2handed_spear' if num == 8 else 'hu1e_dlc24_celestial_general'))
    root['weapons_collection'] = weapons.name

def weapon_copy(ob, num, bone, title, transform=None, visible=True):
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = title + ' | ' + ob.name
    new.parent = roots[num]
    new.matrix_parent_inverse.identity()
    new.matrix_basis.identity()
    for c in list(new.constraints):
        new.constraints.remove(c)
    if transform:
        new.data.transform(transform)
    c = new.constraints.new('COPY_TRANSFORMS')
    c.target = rigs[num]
    c.subtarget = bone
    col = bpy.data.collections[roots[num]['weapons_collection']]
    col.objects.link(new)
    new.hide_set(not visible)
    new.hide_render = not visible
    retained.add(new)
    new['donor_object'] = ob.name
    report['weapons'].append(dict(name=new.name, source_geometry=ob.get('source_geometry'), bone=bone, visible=visible))
    return new

# The complete long weapon from model09 follows model08's native two-handed
# weapon bone. The offhand sword is retained as a hidden option: that native
# two-handed animation needs the second hand on the shaft.
for ob in groups[9]:
    if is_weapon(ob):
        bone = ob.constraints[0].subtarget
        weapon_copy(ob, 8, 'be_prop_0' if bone == 'be_prop_1' else 'be_prop_5',
                    '09 Polearm' if bone == 'be_prop_1' else '09 Offhand sword option',
                    visible=bone == 'be_prop_1')

# Existing WWD model07 has a complete curved guandao assembly. Flip its local
# long axis so the cutting head replaces the negative-X head of the native
# Celestial General hammer, and extend its shaft to the original hammer reach.
guandao_transform = Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Diagonal((1.62, 1.20, 1.20, 1))
for ob in groups[7]:
    if is_weapon(ob):
        weapon_copy(ob, 1, 'weapon_1', 'Guandao', guandao_transform)

# Material-only monochrome treatment: private copied shader graphs preserve
# source texture pixels, alpha, normal/roughness maps, and engraved patterns.
recolors = {}
for ob in groups[1]:
    if ob.type != 'MESH' or is_weapon(ob):
        continue
    name = ob['original_gallery_name']
    if any(s in name for s in ['cst_luthor_harkon_head', 'cth_astromancer_head_01', 'cth_peasant_head', 'beard', 'ksl_streltsi_head']):
        continue
    dark = any(s in name for s in ['cth_alchemist_body', 'cth_dragon_jade_human', 'cth_nan_gau_warrior_body', 'cth_dragon_iron_human_body'])
    for slot in ob.material_slots:
        original = slot.material
        if not original or not original.use_nodes:
            continue
        key = (original.name, dark)
        if key not in recolors:
            mat = original.copy()
            mat.name = 'Bastion | ' + ('Charcoal | ' if dark else 'Ivory steel | ') + original.name
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bs = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
            color = bs.inputs['Base Color']
            if color.is_linked:
                source = color.links[0].from_socket
                bw = nodes.new('ShaderNodeRGBToBW')
                bw.label = 'Preserve original pattern'
                links.new(source, bw.inputs[0])
                ramp = nodes.new('ShaderNodeValToRGB')
                ramp.label = 'Bastion black and white palette'
                ramp.color_ramp.elements[0].color = (.008, .010, .014, 1) if dark else (.055, .065, .080, 1)
                ramp.color_ramp.elements[1].color = (.12, .14, .17, 1) if dark else (.90, .92, .95, 1)
                links.new(bw.outputs[0], ramp.inputs[0])
                links.new(ramp.outputs['Color'], color)
            recolors[key] = mat
        slot.material = recolors[key]

# Keep only the two review characters and their hidden alternatives. Original
# gallery and exact source checkpoint remain separate, untouched files.
for ob in list(bpy.data.objects):
    if ob not in retained:
        bpy.data.objects.remove(ob, do_unlink=True)
for col in list(bpy.data.collections):
    if not col.objects and not col.children:
        bpy.data.collections.remove(col)

for row in report['models']:
    n = row['source_model']
    after = [o['original_gallery_name'] for o in groups[n]
             if o.type == 'MESH' and not is_weapon(o) and not o.hide_get()]
    assert sorted(after) == sorted(row['original_visible_body']), 'User visibility changed'

scene.frame_start = 1
scene.frame_end = 100
scene.frame_set(1)
scene.render.fps = 30
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.13, .13, .13, 1)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.shading.type = 'MATERIAL'
            sp.overlay.show_overlays = True
            sp.overlay.show_floor = False
            sp.overlay.show_axis_x = False
            sp.overlay.show_axis_y = False
            sp.region_3d.view_location = Vector((0, 0, 1.1))
            sp.region_3d.view_distance = 6.8
            sp.region_3d.view_rotation = Vector((0, 12, -.15)).to_track_quat('-Z', 'Y')
            sp.region_3d.view_perspective = 'ORTHO'
        elif area.type == 'OUTLINER':
            area.spaces.active.filter_text = ''

notes = bpy.data.texts.new('MOON GENERALS - READ ME')
notes.write('Private appearance review. Assault preserves user-edited model08 body and uses model09 long weapon. '
            'Model09 offhand sword retained hidden because native model08 animation is two-handed. '
            'Bastion preserves model01 native rig and idle, swaps hammer for WWD guandao, and uses private '
            'black/white material copies. No skill/stat/recruitment/pack integration yet. '
            'Original hidden pieces remain available in Outliner.\n' + json.dumps(report, indent=2))
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
report['scene'] = str(OUT)
report['recolored_materials'] = len(recolors)
(O / 'preview-report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print('MOON_GENERALS_PREVIEW_READY', flush=True)
