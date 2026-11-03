"""Read-only baseline for the user's manual sword placement in Blender."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-model-v1'
source=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else O/'huyen-ve-before-hand-fix.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
scene=bpy.context.scene;rig=bpy.data.objects['humanoid01e_HuyenVe'];dg=bpy.context.evaluated_depsgraph_get()
def matrix(m):return [list(row) for row in m]
result={'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,'frame':scene.frame_current,'action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
 'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},
 'rig_world':matrix(rig.matrix_world),'weapon_2_pose':matrix(rig.pose.bones['weapon_2'].matrix),
 'weapon_2_world':matrix(rig.matrix_world@rig.pose.bones['weapon_2'].matrix),'objects':{}}
for o in bpy.data.objects:
 if not o.name.startswith('mc_huyen_ve_sword_lod') or o.type!='MESH':continue
 evaluated=o.evaluated_get(dg);coordinates=[list(v.co) for v in o.data.vertices]
 result['objects'][o.name]={'location':list(o.location),'rotation_mode':o.rotation_mode,'rotation_euler':list(o.rotation_euler),'rotation_quaternion':list(o.rotation_quaternion),'scale':list(o.scale),
  'matrix_basis':matrix(o.matrix_basis),'matrix_local':matrix(o.matrix_local),'matrix_world_evaluated':matrix(evaluated.matrix_world),
  'parent':o.parent.name if o.parent else None,'matrix_parent_inverse':matrix(o.matrix_parent_inverse),
  'constraints':[{'name':c.name,'type':c.type,'target':c.target.name if getattr(c,'target',None) else None,'subtarget':getattr(c,'subtarget',None),'influence':c.influence,'mute':c.mute,'inverse_matrix':matrix(c.inverse_matrix) if hasattr(c,'inverse_matrix') else None} for c in o.constraints],
  'vertex_coordinates':coordinates,'mesh_sha256':hashlib.sha256(b''.join(struct.pack('<3f',*p) for p in coordinates)).hexdigest(),
  'world_bounds':[[min((evaluated.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],[max((evaluated.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]]}
assert 'mc_huyen_ve_sword_lod0' in result['objects']
folder=O/'sword-placement-baselines';folder.mkdir(exist_ok=True)
destination=folder/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.json')
destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
(O/'sword-placement-baseline-latest.txt').write_text(str(destination),encoding='utf-8')
print(json.dumps({'baseline':str(destination),'source':str(source),'frame':result['frame'],'action':result['action'],'lod0':{k:v for k,v in result['objects']['mc_huyen_ve_sword_lod0'].items() if k in ['location','rotation_euler','scale','matrix_world_evaluated']}},indent=2))
