"""Create a textured, private Blender review scene without modifying source assets."""
import bpy, addon_utils, sys, json, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/beautiful-neferata'; O=R/'build/da-lien-model-review'
O.mkdir(parents=True,exist_ok=True)
OUT=O/'da-lien-beautiful-neferata-review.blend'
assert not OUT.exists(), 'Preserve existing review scene and user changes'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials

bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/skeletons/humanoid01ba.anim'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rig.name='Da_Lien_NATIVE_humanoid01ba'
rows=[];missing=[];converted={}
def png(path):
    path=path.replace('\\','/').lower()
    if path in converted:return converted[path]
    src=D/path
    if not src.exists():missing.append(path);return None
    dest=O/'preview-textures'/Path(path).parent
    dest.mkdir(parents=True,exist_ok=True)
    output=dest/(src.stem+'.png')
    if not output.exists():
        subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(src)],check=True,stdout=subprocess.DEVNULL)
    converted[path]=output.relative_to(O).as_posix()
    return converted[path]
def select_rig():
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True);bpy.context.view_layer.objects.active=rig
def import_ws(rel, bone=None):
    tree=ET.parse(D/rel)
    geom=tree.findtext('geometry').replace('\\','/').lower()
    if bone:
        bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    else: select_rig()
    old=set(bpy.data.objects)
    bpy.ops.import_scene.rmv2(filepath=str(D/geom),build_materials=False,import_all_lods=False,attach_armature=not bool(bone))
    meshes=[o for o in bpy.data.objects if o not in old and o.type=='MESH']
    col=next(c for o in meshes for c in o.users_collection if c.name.endswith('lod0'))
    ordered=[o for o in col.objects if o.type=='MESH']
    for ref in tree.findall('.//material'):
        if int(ref.get('lod_index'))!=0:continue
        obj=ordered[int(ref.get('part_index'))]
        matpath=ref.text.replace('\\','/').lower(); mt=ET.parse(D/matpath)
        types={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29}
        pairs=[]
        for tx in mt.findall('.//texture'):
            slot=tx.findtext('slot')
            if slot in types:
                p=png(tx.findtext('source'))
                if p:pairs.append((types[slot],p))
        alpha='CLIP' if 'alpha_on' in matpath else 'NONE'
        mat=materials.build_material('Da Lien | '+Path(matpath).stem,pairs,alpha,str(O))
        obj.data.materials.clear();obj.data.materials.append(mat)
        obj['source_wsmodel']=rel;obj['source_material']=matpath
        if bone:
            assert bone in rig.pose.bones, (bone,list(rig.pose.bones.keys()))
            con=obj.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget=bone
        obj.data.calc_loop_triangles()
        rows.append({'name':obj.name,'triangles':len(obj.data.loop_triangles),'vertices':len(obj.data.vertices),'attachment':bone,'material':matpath})
    return meshes
body='variantmeshes/wh_variantmodels/hu1ba/vmp/vmp_neferata/vmp_neferata_01.wsmodel'
meshes=import_ws(body)
meshes+=import_ws('variantmeshes/wh_variantmodels/hu1ba/vmp/vmp_props/vmp_neferata_dagger_1h_01.wsmodel','be_prop_0')
meshes+=import_ws('variantmeshes/wh_variantmodels/hu1ba/vmp/vmp_props/vmp_neferata_staff_01.wsmodel','be_prop_5')
select_rig()
bpy.ops.import_scene.tw_anim(filepath=str(D/'animations/battle/humanoid01ba/neferata/stand/hu1ba_neferata_staff_and_sword_stand_01.anim'))
action=rig.animation_data.action;action.name='DL_Native_Stand';action.use_fake_user=True
scene=bpy.context.scene
scene.frame_start=int(action.frame_range[0]);scene.frame_end=int(action.frame_range[1]);scene.frame_set(scene.frame_start)
scene.render.fps=30;bpy.context.view_layer.update()
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
center=(low+high)/2; span=max(high-low)
rig.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.shading.studiolight_rotate_z=0.35
            rv=sp.region_3d;rv.view_location=center;rv.view_distance=span*1.4
            rv.view_rotation=Vector((0,-1,.12)).to_track_quat('Z','Y');rv.view_perspective='ORTHO'
            sp.clip_end=1000
for im in bpy.data.images:
    if im.source=='FILE' and im.has_data and not im.packed_file: im.pack()
report={'identity':'Da Lien','role':'Living human wizard, Agents of the Moon; AOE damage, light healing, armour buff','source_mod':'Beautiful Neferata, Workshop 3809988722','scene':str(OUT),'blender':bpy.app.version_string,'bones':len(rig.data.bones),'body_lod_count':1,'body_triangles':sum(x['triangles'] for x in rows[:5]),'parts':rows,'missing_textures':missing,'preview_action':action.name,'source_geometry_modified':False,'runtime_verified':False}
(O/'model-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not missing,missing
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('DA_LIEN_REVIEW_READY',json.dumps(report),flush=True)
