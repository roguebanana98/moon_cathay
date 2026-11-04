"""Sariwa based on Endo campaign variant 02; private texture and Blender preview."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
SOURCE=R.parent/'endo_damsel_preview/Endo_Damsel_White_Outfits.blend'
TEXTURE=R/'textures/edh_sariwa_body_base_colour_v1.png'
RAW=R/'textures/edh_sariwa_body_ai_atlas_v1.png'
assert RAW.exists(),RAW
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
for obj in list(bpy.data.objects):
    if obj.name.startswith(('Damsel 01','Damsel 03','Damsel 04')):
        bpy.data.objects.remove(obj,do_unlink=True)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.startswith('Damsel 02'))
rig.location.x=0
meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Damsel 02')]
assert len(meshes)==5
def fingerprint(o):
    h=hashlib.sha256()
    for v in o.data.vertices:
        h.update(struct.pack('<3f',*v.co))
        for g in v.groups:h.update(struct.pack('<If',g.group,g.weight))
    for uv in o.data.uv_layers.active.data:h.update(struct.pack('<2f',*uv.uv))
    return h.hexdigest()
before={o.name:fingerprint(o) for o in meshes}
body=next(o for o in meshes if ' | body | ' in o.name)
image=bpy.data.images.load(str(RAW),check_existing=False)
image.name='Sariwa | ivory jade bronze textile v1';image.colorspace_settings.name='sRGB';image.pack()
for mat in body.data.materials:
    mat.name='Sariwa | Southeast Asian textile | ivory jade bronze'
    nodes=mat.node_tree.nodes
    base=next(n for n in nodes if n.type=='TEX_IMAGE' and n.name=='BaseColour')
    original_image=base.image
    new_tex=nodes.new('ShaderNodeTexImage');new_tex.image=image;new_tex.label='Edited clothing atlas';new_tex.location=(-1000,600)
    mask=next(n for n in nodes if n.type=='TEX_IMAGE' and n.name=='Mask')
    separate=nodes.new('ShaderNodeSeparateColor');separate.mode='RGB'
    mat.node_tree.links.new(mask.outputs['Color'],separate.inputs['Color'])
    maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM'
    mat.node_tree.links.new(separate.outputs['Red'],maximum.inputs[0]);mat.node_tree.links.new(separate.outputs['Green'],maximum.inputs[1])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.label='Clothing only; original skin and sandals'
    mat.node_tree.links.new(maximum.outputs[0],mix.inputs[0]);mat.node_tree.links.new(base.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(new_tex.outputs['Color'],mix.inputs[2])
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    mat.node_tree.links.new(mix.outputs['Color'],shader.inputs['Base Color'])
    mat['source_body']='Endo Damsel body 02';mat['palette']='ivory, jade, muted bronze; no faction colour override'
# Bake the Blender material to the original UV layout, isolating the edit with
# the source garment mask so original skin/feet/belt stay on their native texture.
baked=bpy.data.images.new('Sariwa | final clothing-only albedo',width=2048,height=2048,alpha=False)
baked.generated_color=(0,0,0,1);baked.colorspace_settings.name='sRGB'
for mat in body.data.materials:
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=baked;node.label='Final UV bake target';mat.node_tree.nodes.active=node
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=4,use_clear=True)
baked.filepath_raw=str(TEXTURE);baked.file_format='PNG';baked.save();baked.pack()
for mat in body.data.materials:
    nodes=mat.node_tree.nodes;base=next(n for n in nodes if n.type=='TEX_IMAGE' and n.name=='BaseColour');base.image=baked
    base['rmv2_path']='variantmeshes/wh_variantmodels/edh/sariwa/tex/edh_sariwa_body_base_colour_v1.dds'
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');mat.node_tree.links.new(base.outputs['Color'],shader.inputs['Base Color'])
image=baked
for o in meshes:
    assert fingerprint(o)==before[o.name]
    o.name=o.name.replace('Damsel 02','Sariwa')
rig.name='Sariwa | Damsel 02 | humanoid01b'
rig['identity']='Sariwa, human Khuresh scholar-priestess'
rig['source_head']='endo_damsel_head_04.wsmodel'
for c in bpy.data.collections:
    if c.name.startswith('Damsel 02'):c.name=c.name.replace('Damsel 02','Sariwa')
for obj in list(bpy.data.objects):
    if obj.type=='FONT':bpy.data.objects.remove(obj,do_unlink=True)
scene=bpy.context.scene;scene.frame_set(1)
scene.render.resolution_x=1200;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.cycles.samples=32
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=scene.camera;cam.name='CAM | Sariwa front';cam.location=(0,-8,1.15);aim(cam,(0,0,1.15));cam.data.ortho_scale=2.95
for name,pos in [('back',(0,8,1.15)),('side',(8,0,1.15))]:
    obj=cam.copy();obj.data=cam.data.copy();scene.collection.objects.link(obj);obj.name='CAM | Sariwa '+name;obj.location=pos;aim(obj,(0,0,1.15))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.region_3d.view_location=Vector((0,0,1.15));s.region_3d.view_distance=2.7
            s.region_3d.view_rotation=cam.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO'
            s.overlay.show_overlays=False;s.shading.type='MATERIAL';s.shading.studiolight_rotate_z=.6
scene['character']='Sariwa';scene['base_model']='[Endo] Damsel, campaign variant 02: head 04 + body 02'
scene['texture_design']='White linen, jade/bronze geometric woven borders, Naga scales, stylized sun and birds inspired by Southeast Asian textiles and Dong Son bronze motifs.'
scene['scope']='Clothing albedo edit only. Face, hair, skin mesh, UVs, weights, sword and staff preserved. No live game files changed.'
file=R/'Sariwa_Damsel02_Textile_v1.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(file))
report={'blend':str(file),'texture':str(TEXTURE),'base_variant':'Damsel 02','body':'endo_damsel_body_02','head':'endo_damsel_head_04','mesh_parts':len(meshes),'bones':len(rig.data.bones),'mesh_uv_weight_fingerprints_before':before,'mesh_uv_weights_unchanged':True,'texture_size':list(image.size),'game_deployed':False}
(R/'asset_report.json').write_text(json.dumps(report,indent=2))
scene.render.filepath=str(R/'Sariwa_front_v1.png');bpy.ops.render.render(write_still=True)
print('SARIWA_READY',str(file),flush=True)
