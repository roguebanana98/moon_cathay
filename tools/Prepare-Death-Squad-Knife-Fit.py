import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-no-back-cape'
bpy.ops.wm.open_mainfile(filepath=str(R/'build/cathay-ror-preview/dark-society-death-squad-models.blend'))
rig=bpy.data.objects['Ninja 01 | native humanoid01d'];bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
ob=next(o for o in bpy.data.objects if o.type=='MESH' and 'ninja_knife_1.rigid' in str(o.get('source_model','')) and any(c.type=='COPY_TRANSFORMS' and c.target==rig for c in o.constraints))
prop=rig.pose.bones['be_prop_1'];hand=rig.pose.bones['hand_right'];relative=hand.matrix.inverted()@prop.matrix
assert relative.translation.length<.3
report={'source_object':ob.name,'relative_matrix':[list(r) for r in relative],'source':'ninja_knife_1','hand':'hand_right','vertices':len(ob.data.vertices)}
(O/'death-squad-knife-grip.json').write_text(json.dumps(report,indent=2));print(report)
