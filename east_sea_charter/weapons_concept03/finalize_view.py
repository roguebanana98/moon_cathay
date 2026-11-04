import bpy,os,math
from mathutils import Quaternion
out=os.path.dirname(os.path.abspath(__file__))
path=os.path.join(out,'EDH_concept03_weapons.blend')
bpy.ops.wm.open_mainfile(filepath=path)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2)
            space.region_3d.view_perspective='ORTHO'
            space.region_3d.view_location=(0,0,1.12)
            space.region_3d.view_distance=3.7
            space.shading.type='MATERIAL'
            space.overlay.show_floor=False
            space.overlay.show_extras=False
ref=bpy.data.images.load(os.path.join(out,'concept03_reference.png'),check_existing=True)
ref.name='APPROVED | Concept 03 reference';ref.pack()
bpy.context.scene['design_reference']='Concept 03 - Viceroy, approved; Sariwa sword included'
bpy.context.scene['status']='Editable concept geometry, not final WH3 export'
bpy.ops.wm.save_as_mainfile(filepath=path)
