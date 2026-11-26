"""Render the actual exported-rig appearances for mod UI and visual review."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/da-anh-v8-appearance';P=O/'renders';P.mkdir(exist_ok=True)
for number in (1,):
    bpy.ops.wm.open_mainfile(filepath=str(O/'engine-da-anh.blend'))
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
    scene.render.threads_mode='FIXED';scene.render.threads=12;scene.render.film_transparent=True
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('Moonshadow studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
    for loc,power,size in [((3,-4,5),650,4),((-3,-2,3),420,3),((0,3,4),600,3)]:
        data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.shape='DISK';data.size=size
        light=bpy.data.objects.new('Studio',data);scene.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,1.1))-light.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('Card camera');cam=bpy.data.objects.new('Card camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
    for kind,target,location,scale,size in [('body',(0,0,1.03),(1.1,-6,2.1),2.45,(512,768)),('head',(0,-.01,1.60),(.25,-5,1.80),.72,(512,512))]:
        cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(P/('face_%02d_%s.png'%(number,kind)))
        bpy.ops.render.render(write_still=True);print('RENDERED',number,kind,flush=True)
