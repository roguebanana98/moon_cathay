"""Run inside the user's live Blender console; never reopen the stale disk file."""
import bpy,json,hashlib,struct,math
from pathlib import Path
from datetime import datetime,timezone
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
baseline_path=O/'sword-placement-baselines/20261102-205852-939967.json'
baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
assert Path(bpy.data.filepath).name=='huyen-ve-before-hand-fix.blend','Wrong working file'
obj=bpy.data.objects['mc_huyen_ve_sword_lod0'];assert obj.mode=='OBJECT'
rig=bpy.data.objects['humanoid01e_HuyenVe'];scene=bpy.context.scene;bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();world=obj.evaluated_get(dg).matrix_world.copy();weapon=rig.matrix_world@rig.pose.bones['weapon_2'].matrix
def mat(m):return [list(row) for row in m]
coords=[list(v.co) for v in obj.data.vertices]
mesh_hash=hashlib.sha256(b''.join(struct.pack('<3f',*v) for v in coords)).hexdigest()
before=baseline['objects'][obj.name];assert before['mesh_sha256']==mesh_hash,'Mesh changed too; do not treat this as an object-only offset'
basis_delta=obj.matrix_basis@Matrix(before['matrix_basis']).inverted()
attachment_before=Matrix(baseline['weapon_2_world']).inverted()@Matrix(before['matrix_world_evaluated'])
attachment_after=weapon.inverted()@world
attachment_delta=attachment_after@attachment_before.inverted()
t,q,s=basis_delta.decompose()
timestamp=datetime.now().strftime('%Y%m%d-%H%M%S')
saved_copy=O/f'huyen-ve-user-sword-placement-{timestamp}.blend'
result={'captured_at_utc':datetime.now(timezone.utc).isoformat(),'source_live_file':bpy.data.filepath,'saved_copy':str(saved_copy),'baseline':str(baseline_path),
 'frame':scene.frame_current,'action':rig.animation_data.action.name,'object':obj.name,'location':list(obj.location),'rotation_euler_degrees':[math.degrees(x) for x in obj.rotation_euler],'scale':list(obj.scale),
 'matrix_basis':mat(obj.matrix_basis),'matrix_world':mat(world),'weapon_2_world':mat(weapon),'delta_matrix_basis':mat(basis_delta),'delta_attachment_space':mat(attachment_delta),
 'delta_translation':list(t),'delta_rotation_degrees':[math.degrees(x) for x in q.to_euler('XYZ')],'delta_scale':list(s),'mesh_unchanged':True,'mesh_sha256':mesh_hash,
 'scope':'Capture only: no mesh, hand, bone, constraint or LOD changes; pose influence removed using weapon_2 matrix'}
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
assert bpy.ops.wm.save_as_mainfile(filepath=str(saved_copy),copy=True)=={'FINISHED'}
result['saved_copy_sha256']=hashlib.sha256(saved_copy.read_bytes()).hexdigest()
destination=O/f'sword-manual-adjustment-{timestamp}.json';destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
(O/'sword-manual-adjustment-latest.txt').write_text(str(destination),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k in ['saved_copy','frame','action','location','delta_translation','delta_rotation_degrees','mesh_unchanged']},indent=2))
