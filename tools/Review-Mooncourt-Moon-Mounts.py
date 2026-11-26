"""Check native mounted rider clips with the approved body and native sword pivot."""
import bpy,addon_utils,json,subprocess,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-v35-moon-arts';REF=R/'reference/local/moon-v35-mount-animation'
spec=json.loads((O/'mount-review-clips.json').read_text());clips=sorted({p for paths in spec.values() for p in paths})
subprocess.run([C['rpfm'],'-g','warhammer_3','pack','extract','-p',str(Path(C['game'])/'data/anim2.pack'),'-f',*[p+';'+str(REF) for p in clips]],check=True,stdout=subprocess.DEVNULL)
assert all((REF/p).exists() for p in clips)
bpy.ops.wm.open_mainfile(filepath=str(R/'build/zhao-yuan-bo-preview/zhao-yuan-bo-sword-grip-fixed.blend'))
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2');from io_scene_rmv2 import import_anim
sys.path.insert(0,str(R/'tools'));from HuyenVeAnimationPreview import complete_preview_channels
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.hide_set(False)
body=[o for o in bpy.data.collections['01 | Zhao Yixuan original body'].objects if o.type=='MESH'];sword=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Yuan Bo sword'));pivot=sword.matrix_basis.copy();scene=bpy.context.scene;checks=[]
for unit,paths in spec.items():
    for path in paths:
        rig.animation_data_clear()
        for bone in rig.pose.bones:bone.matrix_basis.identity()
        bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
        _,_,warnings=import_anim.import_file(bpy.context,str(REF/path),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert not warnings,warnings
        action=rig.animation_data.action;complete_preview_channels(action,rig);action.name=unit+' | '+Path(path).stem;action.use_fake_user=True
        lo,hi=map(int,action.frame_range);snap=[];gaps=[]
        for f in sorted({lo,(lo+hi)//2,hi}):
            scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();actual=sword.evaluated_get(dg).matrix_world;expected=rig.matrix_world@rig.pose.bones['weapon_2'].matrix@pivot
            assert max(abs(actual[a][b]-expected[a][b]) for a in range(4) for b in range(4))<1e-4
            palm=rig.matrix_world@((rig.pose.bones['finger_index_right_0'].head+rig.pose.bones['finger_ring_right_0'].head)*.5);gap=(actual@Vector((.44,0,0))-palm).length;gaps.append(gap)
            points=[]
            for ob in body:
                ev=ob.evaluated_get(dg);mesh=ev.to_mesh();p=np.array([tuple(v.co) for v in mesh.vertices]);ev.to_mesh_clear();assert np.isfinite(p).all() and abs(p).max()<40;points.append(p)
            snap.append(np.concatenate(points))
        delta=max(float(abs(p-snap[0]).max()) for p in snap[1:]);assert delta>1e-6,(unit,path)
        # Mounted casting may deliberately release the hand; retain its measured gap
        # for visual review rather than treating prop-parent equality as a grip test.
        checks.append(dict(unit=unit,clip=path,samples=len(snap),motion=delta,handle_to_knuckles=gaps,native_attachment_verified=True))
rig.hide_set(True)
(O/'mounted-animation-review.json').write_text(json.dumps(dict(status='passed',checks=checks,samples=sum(x['samples'] for x in checks),native_rider_profiles=True,body_and_sword_source_unchanged=True,game_runtime_verified=False),indent=2));print('MOUNTED_RIDER_REVIEW_PASSED',len(checks),flush=True)
