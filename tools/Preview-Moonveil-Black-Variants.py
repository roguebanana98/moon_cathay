"""Original black Moonveil: all eight bodies with each of its two native heads."""
import bpy, addon_utils, ast, json, subprocess, sys, re, math
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parents[1]
C = json.loads((R / 'config/local.json').read_text(encoding='utf-8-sig'))
O = R / 'build/moonveil-v24'
D = O
DEST = R / 'build/moonveil-black-original-gallery'
DEST.mkdir(exist_ok=True)
OUT = DEST / 'moonveil-black-all-bodies-heads.blend'
assert not OUT.exists(), 'Preserve existing scene'
sys.path.insert(0, str(Path(C['blender']).parent / 'portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials, import_anim
converted = {}
missing = []
audit = []

def material_tree(path):
    tree = ET.Element('material')
    for slot, source in re.findall(r'<slot[^>]*>(.*?)</slot>\s*<source>(.*?)</source>', Path(path).read_text(encoding='utf8')):
        tx = ET.SubElement(tree, 'texture')
        ET.SubElement(tx, 'slot').text = slot
        ET.SubElement(tx, 'source').text = source
    return tree

helpers = ast.parse((R / 'tools/Preview-Celestial-Concubines.py').read_text().replace('ET.parse(D/matpath)', 'material_tree(D/matpath)'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in ['png', 'import_ws', 'label']], type_ignores=[]), '<preview helpers>', 'exec'))
model = next(m for m in json.loads((O / 'models.json').read_text())['models'] if m['palette'] == 'black')
root = ET.parse(O / model['vmd']).getroot()
bodies = []
for ref in root.find("SLOT[@name='body']"):
    bodies.extend(n.get('model') for n in ET.parse(O / ref.get('definition')).iter('VARIANT_MESH') if n.get('model'))
heads = [n.get('model') for n in root.find("SLOT[@name='head']")]
assert len(bodies) == 8 and len(heads) == 2
paths = json.loads((O / 'native-animation-paths.json').read_text())['hu1e_mage_female_hero']
idle = next(p for p in paths if '/alchemist/stand/' in p and 'stand_01' in p)
clip = R / 'reference/local/moonveil-animations' / idle
assert clip.exists()
scene = bpy.context.scene
entries = []
for i, body in enumerate(bodies):
    for j, head in enumerate(heads):
        n = i * 2 + j
        title = '%02d | Body %s | Head %d' % (n + 1, Path(body).stem.split('_body_')[1].split('_black')[0], j + 1)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_scene.tw_anim(filepath=str(R / 'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
        rig = next(o for o in bpy.context.selected_objects if o.type == 'ARMATURE')
        rig.name = title + ' | native rig'
        rig.animation_data_clear()
        meshes = import_ws(body, rig) + import_ws(head, rig)
        bpy.ops.object.select_all(action='DESELECT')
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        _, _, warnings = import_anim.import_file(bpy.context, str(clip), {'mode': 'ANIMATION', 'attach_meshes': False, 'global_scale': 1.0})
        assert not warnings
        group = bpy.data.collections.new(title)
        scene.collection.children.link(group)
        anchor = bpy.data.objects.new(title, None)
        group.objects.link(anchor)
        anchor.location = (((n % 4) - 1.5) * 2.0, 0, (3 - n // 4) * 2.6)
        for ob in [rig] + meshes:
            for collection in list(ob.users_collection):
                collection.objects.unlink(ob)
            group.objects.link(ob)
            ob.parent = anchor
        rig.hide_set(True)
        label(title, anchor.location.x, anchor.location.z - .25, .10)
        entries.append(dict(number=n + 1, body=body, head=head, collection=title))
        print('BLACK_VARIANT_READY', title, flush=True)
scene.frame_set(1)
scene.frame_start = 1
scene.frame_end = 100
scene.world = bpy.data.worlds.new('Moonveil black gallery')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.shading.type = 'MATERIAL'
            sp.overlay.show_overlays = False
            sp.clip_end = 500
            sp.region_3d.view_location = Vector((0, 0, 4.7))
            sp.region_3d.view_distance = 14
            sp.region_3d.view_rotation = Vector((0, 12, -.3)).to_track_quat('-Z', 'Y')
            sp.region_3d.view_perspective = 'ORTHO'
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = None
assert not missing, missing
bpy.data.texts.new('BLACK ORIGINAL MODELS - READ ME').write('Original black palette only: eight body styles, each with native head1 and head2 (16 combinations). Select the numbered collection in the Outliner to show/hide each model. These are two head geometries, not sixteen different faces. Original meshes, materials, weights and native Alchemist idle. Game mod unchanged.\n')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
(DEST / 'gallery.json').write_text(json.dumps(dict(scene=str(OUT), combinations=entries, original_bodies=8, original_heads=2, palette='black', missing_textures=missing, game_modified=False), indent=2))
print('BLACK_GALLERY_READY', OUT, flush=True)
