import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'build/moonveil-v32-approved-variants'
bpy.ops.wm.open_mainfile(filepath=str(R/'build/moonveil-black-original-gallery/moonveil-black-all-bodies-heads.blend'))
keep={2,6,10,14}
for col in list(bpy.data.collections):
    if ' | Body ' in col.name:
        number=int(col.name.split(' | ')[0])
        if number not in keep:
            for ob in list(col.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
            bpy.data.collections.remove(col)
for ob in list(bpy.data.objects):
    if ob.type=='FONT' and ' | Body ' in ob.name and int(ob.name.split(' | ')[0]) not in keep:bpy.data.objects.remove(ob,do_unlink=True)
# Selected models occupy a single column in the original grid; retain their labels.
from mathutils import Vector
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=Vector((-1,0,4.7))
bpy.data.texts.new('APPROVED MOONVEIL 02 06 10 14').write('User-selected 2026-11-24: gallery 02,06,10,14 only. Black bodies01,03,01a,03a with native head2. Original gallery unchanged. New v32 runtime uses these exact pairs; all four prior palette IDs are retained for compatibility. All native rig/weights/LODs unchanged.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'moonveil-approved-02-06-10-14.blend'),compress=True)
