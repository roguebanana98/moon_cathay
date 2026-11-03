"""Portable Blender-only preview; retain the RMV2 texture slot paths."""
from pathlib import Path
import bpy
from mathutils import Vector

def prepare_preview(output):
    output=Path(output);packed=[]
    for material in bpy.data.materials:
        if not material.use_nodes or not material.name.startswith('mc_huyen_ve'):
            continue
        for node in material.node_tree.nodes:
            if node.type!='TEX_IMAGE' or node.image is None:
                continue
            original=node.image
            png=output/'texture-intermediate'/(Path(original.filepath).stem+'.png')
            if not png.is_file():
                raise FileNotFoundError(png)
            colour_space=original.colorspace_settings.name
            image=bpy.data.images.load(str(png),check_existing=True)
            image.colorspace_settings.name=colour_space
            image.alpha_mode='STRAIGHT'
            image.pack()
            node.image=image;packed.append(image.name)
    orientation=(Vector((0,0,1))-Vector((3,-5,2.3))).to_track_quat('-Z','Y')
    count=0
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type!='VIEW_3D':continue
            space=area.spaces.active
            space.shading.type='MATERIAL'
            space.shading.use_scene_lights=False
            space.shading.use_scene_world=False
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=orientation
            space.region_3d.view_location=(0,0,1)
            space.region_3d.view_distance=3.4
            space.region_3d.view_perspective='PERSP'
            count+=1
    return dict(packed_preview_images=sorted(set(packed)),material_viewports=count)
