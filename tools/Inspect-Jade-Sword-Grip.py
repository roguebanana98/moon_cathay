import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'build/deer-jade-model05-round-shield/deer24-model05-round-chen-shield.blend'))
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'sword' in o.get('source_geometry',''))
data=dict(name=ob.name,matrix_basis=[list(row) for row in ob.matrix_basis],constraints=[dict(type=c.type,target=c.target.name,subtarget=c.subtarget) for c in ob.constraints],vertices=[list(v.co) for v in ob.data.vertices],bones={})
arm=ob.constraints[0].target
for name in ['weapon_2','r_hand','hand_r','RightHand']:
 bone=arm.pose.bones.get(name)
 if bone:data['bones'][name]=dict(head=list(bone.head),tail=list(bone.tail),matrix=[list(row) for row in bone.matrix])
(R/'build/deer-jade-model05-round-shield/sword-grip-audit.json').write_text(json.dumps(data))
