"""Render a high-resolution editable portrait from the approved model, preserving game files."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/da-lien-portrait-edit'
SOURCE=R/'build/da-lien-moon-staff/da-lien-moon-staff.blend'
OUT=O/'Da_Lien_portrait_2048.png';assert not OUT.exists(),'Keep any user-edited image'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
for obj in bpy.data.objects:
    if obj.type=='MESH' and obj.name not in {'Neferata_Body','Neferata_Boots','Neferata_Hair_Lashes','Neferata_Outfit_Dress','Neferata_Outfit_Sleeves_Collar'}:obj.hide_render=True
    if obj.type=='ARMATURE':obj.hide_render=True
# Match the native alpha-on hair/eyelash material in the render scene only.
for slot in bpy.data.objects['Neferata_Hair_Lashes'].material_slots:
    mat=slot.material;nodes=mat.node_tree.nodes
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    image=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.lower()=='neferata_hair.png')
    mat.node_tree.links.new(image.outputs['Alpha'],bsdf.inputs['Alpha'])
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Da Lien Portrait Camera');cam=bpy.data.objects.new('Da Lien Portrait Camera',cam_data);scene.collection.objects.link(cam)
target=Vector((0,-.025,1.48));cam.location=target+Vector((.18,-3.2,.045));aim(cam,target)
cam_data.type='ORTHO';cam_data.ortho_scale=.70;scene.camera=cam
def light(name,location,energy,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=location;aim(obj,target)
light('Portrait Soft Key',(-1.4,-2.2,2.8),350,2.0,(1.0,.94,.90))
light('Portrait Soft Fill',(1.6,-1.4,1.8),110,2.0,(.87,.92,1.0))
light('Portrait Hair Rim',(.5,1.4,2.5),350,1.4,(.78,.86,1.0))
world=bpy.data.worlds.new('Portrait neutral world');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.3,.3,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3;scene.world=world
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025
scene.cycles.max_bounces=8;scene.cycles.transparent_max_bounces=12
scene.render.film_transparent=True;scene.render.resolution_x=2048;scene.render.resolution_y=2048;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.render.filepath=str(OUT);scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
device='CPU'
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    if any(d.type=='CUDA' for d in prefs.devices):scene.cycles.device='GPU';device='CUDA'
except Exception:scene.cycles.device='CPU'
print('RENDER_START',device,str(OUT),flush=True)
try:bpy.ops.render.render(write_still=True)
except RuntimeError:
    if device=='CPU':raise
    scene.cycles.device='CPU';device='CPU fallback';bpy.ops.render.render(write_still=True)
report={'source_scene':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'image':str(OUT),'size':[2048,2048],'mode':'RGBA','source':'Fresh model render, not an enlargement of the 60x130 UI image',
 'samples':96,'device':device,'transparent_background':True,'model_edits_preserved':['warm skin','removed collar'],
 'game_pack_changed':False,'user_edit_pending':True}
(O/'high-resolution-render.json').write_text(json.dumps(report,indent=2))
print('DA_LIEN_PORTRAIT_READY',json.dumps(report),flush=True)
