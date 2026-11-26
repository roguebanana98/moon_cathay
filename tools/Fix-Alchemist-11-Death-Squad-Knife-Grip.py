"""Place the actual handle midpoint in the target palm instead of its prop origin."""
import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path('D:/Warhammer3_Modding/moon_cathay/build/alchemist-11-no-back-cape')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-knife-grip-fix-live.blend'),copy=True)
knife=bpy.data.objects['Death Squad knife 01'];rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
handle=Vector(((.2482+.3970)/2,(-.0303+.0285)/2,0))
# Palm space: between thumb tip and curled finger bases, not bone origin.
grip=Vector((-.033,.115,-.005))
old=knife.matrix_basis.copy();fixed=old.copy();fixed.translation=grip-fixed.to_3x3()@handle
knife.matrix_basis=fixed
assert (knife.matrix_basis@handle-grip).length<1e-5
report={'handle_local':list(handle),'palm_grip':list(grip),'before_matrix':[list(r) for r in old],'after_matrix':[list(r) for r in fixed],'checks':[]}
for f in (1,75,160,265,320,410):
    bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
    actual=knife.evaluated_get(dg).matrix_world@handle
    expected=rig.matrix_world@rig.pose.bones['hand_right'].matrix@grip
    error=(actual-expected).length;assert error<1e-4
    report['checks'].append({'frame':f,'handle_to_palm_error':error})
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
target=rig.matrix_world@rig.pose.bones['hand_right'].matrix@grip
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D' or area==bpy.context.area:
            sp=next((s for s in area.spaces if s.type=='VIEW_3D'),None)
            if sp:sp.region_3d.view_location=target;sp.region_3d.view_distance=.72
knife['grip_fix']='Actual handle midpoint aligned to target palm; native prop-origin offset was incorrect.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-death-squad-knife-v2-grip.blend'),compress=True)
(O/'knife-grip-fix-report.json').write_text(json.dumps(report,indent=2));print('KNIFE_GRIP_FIXED')
