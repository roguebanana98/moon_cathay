import bpy,addon_utils,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'reference'
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,rmv2_format as rf
rig,stats,warnings=import_anim.import_file(bpy.context,str(D/'animations/skeletons/humanoid01.anim'),{'mode':'SKELETON'})
out={'bones':[{'name':b.name,'index':b.get('rmv2_bone_index'),'parent':b.parent.name if b.parent else None} for b in rig.data.bones],'models':[]}
for name in ['emp_karl_franz/emp_karl_franz','emp_generals/emp_generals_body_01','emp_props/emp_general_sword_1h_01','emp_props/emp_general_shield_01']:
    p=D/('variantmeshes/wh_variantmodels/hu1/emp/'+name+'.rigid_model_v2');rm=rf.load(p.read_bytes())
    out['models'].append({'path':name,'skeleton':rm.skeleton_name,'parts':len(rm.lods[0].models),'bone_ids':sorted(set(int(x) for m in rm.lods[0].models for row in m.mesh.bone_indices for x in row)),'attachments':[{'name':a.name,'bone':a.bone_index,'matrix':list(a.matrix)} for a in rm.lods[0].models[0].material.attachment_points]})
(R/'rig_probe.json').write_text(json.dumps(out,indent=2))
print('PROBE',json.dumps(out))

