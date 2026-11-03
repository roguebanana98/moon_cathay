"""Check actual exported model motion and exact prop-bone following across native clips."""
import bpy,addon_utils,json,sys,subprocess
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/huyen-ve-v22-da-lien-appearance';D=R/'reference/local/beautiful-neferata';stage=R/'reference/local/da-lien-v22-graphics'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/humanoid01ba.anim'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
bpy.ops.import_scene.rmv2(filepath=str(stage/'variantmeshes/wh_variantmodels/mc_da_lien/vmp_neferata/vmp_neferata_01.rigid_model_v2'),build_materials=False)
bodies=[o for o in bpy.data.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
before=set(bpy.data.objects)
bpy.ops.import_scene.rmv2(filepath=str(stage/'variantmeshes/wh_variantmodels/mc_da_lien/vmp_props/vmp_neferata_staff_01.rigid_model_v2'),build_materials=False,attach_armature=False)
props=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
assert len(props)==9
for obj in props:
    con=obj.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='be_prop_5'
    assert not obj.vertex_groups and not any(m.type=='ARMATURE' for m in obj.modifiers),'No double prop attachment'
manifest=json.loads((R/'build/da-lien-model-review/reference-manifest.json').read_text())['clips']
suffixes=['/stand/hu1ba_neferata_staff_and_sword_stand_01.anim',
 '/locomotion/hu1ba_neferata_staff_and_sword_run_01.anim',
 '/attacks/hu1ba_neferata_staff_and_sword_attack_01.anim',
 '/spell_casting/hu1ba_neferata_staff_and_sword_cast_short_02.anim',
 '/spell_casting/hu1ba_neferata_staff_and_sword_cast_medium_02.anim',
 '/spell_casting/hu1ba_neferata_staff_and_sword_cast_long_02.anim']
clips=[next(r for r in manifest if r['path'].endswith(s)) for s in suffixes]
for clip in clips:
    if not (D/clip['path']).exists():
        subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',clip['pack'],'-f',clip['path']+';'+str(D)],check=True,stdout=subprocess.DEVNULL)
rows=[];body=next(o for o in bodies if o.name=='Neferata_Body')
for clip in clips:
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.import_scene.tw_anim(filepath=str(D/clip['path']))
    action=rig.animation_data.action;action.use_fake_user=True
    start,end=map(int,action.frame_range);frames=sorted({start,start+(end-start)//3,start+2*(end-start)//3,end});samples=[];errors=[]
    for frame in frames:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        inv=(rig.matrix_world@rig.pose.bones['root'].matrix).inverted()
        for obj in bodies:
            ev=obj.evaluated_get(dg);m=ev.to_mesh()
            coords=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
            assert np.isfinite(coords).all(),(clip['path'],frame,obj.name)
            if obj==body:
                matrix=np.array(inv@obj.matrix_world);samples.append(coords@matrix[:3,:3].T+matrix[:3,3])
            ev.to_mesh_clear()
        expected=rig.matrix_world@rig.pose.bones['be_prop_5'].matrix
        for obj in props:
            actual=obj.evaluated_get(dg).matrix_world
            err=max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4));assert err<1e-5;errors.append(err)
    motion=max(float(np.linalg.norm(p-samples[0],axis=1).max()) for p in samples[1:]);assert motion>.0005,(clip['path'],motion)
    rows.append({'clip':clip['path'],'frames':frames,'body_actual_root_relative_motion':motion,'max_prop_transform_error':max(errors)})
    print('VERIFIED',clip['path'],flush=True)
report={'status':'passed','clips':rows,'sampled_poses':sum(len(r['frames']) for r in rows),'exported_body_meshes':len(bodies),
 'exported_staff_parts':len(props),'actual_body_motion_verified':True,'prop_attachment_verified':True,
 'scope':'Static exported-mesh/animation regression in Blender, not in-game testing','runtime_verified':False}
(O/'animation-validation.json').write_text(json.dumps(report,indent=2))
print('EXPORTED_ANIMATION_CHECK_PASSED',len(rows),'clips')
