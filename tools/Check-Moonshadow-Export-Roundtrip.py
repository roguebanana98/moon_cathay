"""Reimport actual RMVs, then exercise their native engine skeleton and clips."""
import bpy,addon_utils,json,sys,math,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moonshadow-v7-appearance'
sys.path.insert(0,str(Path(C['blender']).parent/'portable/scripts/addons'));addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim
clips=json.loads((R/'build/moonshadow-animation-preview/clips.json').read_text());D=R/'reference/local/khainite-weapons';report=[]
for number in (8,11,3,12):
    bpy.ops.wm.open_mainfile(filepath=str(O/('engine-face-%02d.blend'%number)))
    native=bpy.data.objects['REFERENCE Khainite prop attachment frames'];native.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT');native.select_set(True);bpy.context.view_layer.objects.active=native
    before=set(bpy.data.objects)
    path=O/('variantmeshes/wh_variantmodels/mc_moonshadow_assassin/moonshadow_face_%02d.rigid_model_v2'%number)
    file_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.import_scene.rmv2(filepath=str(path),build_materials=False,import_all_lods=False,attach_armature=True)
    imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert imported
    assert all(any(m.type=='ARMATURE' and m.object==native for m in o.modifiers) for o in imported)
    entries=[]
    for clip in clips:
        bpy.ops.object.select_all(action='DESELECT');native.select_set(True);bpy.context.view_layer.objects.active=native
        rig,stats,warnings=import_anim.import_file(bpy.context,str(D/clip['path']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0});assert rig==native
        first,last=map(int,native.animation_data.action.frame_range);motion=[]
        for f in sorted({first,(first+last)//2,last}):
            bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();pts=[]
            for ob in imported:
                ev=ob.evaluated_get(dg);me=ev.to_mesh();p=np.asarray([tuple(v.co) for v in me.vertices]);assert np.isfinite(p).all();pts.append(p);ev.to_mesh_clear()
            motion.append(np.concatenate(pts))
        delta=max(float(np.linalg.norm(p-motion[0],axis=1).max()) for p in motion[1:]);assert delta>1e-5
        entries.append({'clip':clip['path'],'motion':delta})
    assert hashlib.sha256(path.read_bytes()).hexdigest()==file_hash
    report.append({'face':number,'sha256':file_hash,'imported_parts':len(imported),'clips':entries})
(O/'roundtrip-animation-check.json').write_text(json.dumps({'status':'passed','variants':report,'sampled_poses':len(report)*len(clips)*3,'game_runtime_verified':False},indent=2));print('ROUNDTRIP_ANIMATION_OK',len(report)*len(clips)*3)
