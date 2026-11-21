"""Build a separate textured native-model comparison scene; no game edits."""
import bpy, addon_utils, sys, json, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
D=R/'reference/local/celestial-concubines';O=R/'build/celestial-concubines-preview';O.mkdir(parents=True,exist_ok=True)
OUT=O/'celestial-concubines-model-comparison.blend';assert not OUT.exists()
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials
P='variantmeshes/wh_variantmodels/hu1e/cth/cth_celestial_concubines/'
converted={};missing=[];audit=[]
def png(path):
    path=path.replace('\\','/').lower()
    if path in converted:return converted[path]
    src=D/path
    if not src.exists():missing.append(path);return None
    dest=O/'textures'/Path(path).parent;dest.mkdir(parents=True,exist_ok=True)
    output=dest/(src.stem+'.png')
    if not output.exists():subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-o',str(dest),str(src)],check=True,stdout=subprocess.DEVNULL)
    converted[path]=output.relative_to(O).as_posix();return converted[path]
def import_ws(rel,rig=None):
    tree=ET.parse(D/rel);geom=tree.findtext('geometry').replace('\\','/').lower()
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=rig
    if rig:rig.select_set(True)
    old=set(bpy.data.objects)
    bpy.ops.import_scene.rmv2(filepath=str(D/geom),build_materials=False,import_all_lods=False,attach_armature=rig is not None)
    meshes=[o for o in bpy.data.objects if o not in old and o.type=='MESH']
    col=next(c for o in meshes for c in o.users_collection if 'lod0' in c.name)
    ordered=[o for o in col.objects if o.type=='MESH']
    for ref in tree.findall('.//material'):
        if ref.get('lod_index')!='0':continue
        obj=ordered[int(ref.get('part_index'))];matpath=ref.text.replace('\\','/').lower()
        pairs=[]
        for tx in ET.parse(D/matpath).findall('.//texture'):
            typ={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29}.get(tx.findtext('slot'))
            if typ is not None:
                txpath=png(tx.findtext('source'))
                if txpath:pairs.append((typ,txpath))
        mat=materials.build_material(Path(matpath).stem,pairs,'TRANSPARENT' if 'alpha_on' in matpath else 'OPAQUE',str(O))
        obj.data.materials.clear();obj.data.materials.append(mat)
        obj['source_wsmodel']=rel;obj['source_material']=matpath
        audit.append(dict(object=obj.name,source=geom,vertices=len(obj.data.vertices)))
    return meshes
def label(text,x,z,size=.14):
    curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.size=size;curve.align_x='CENTER'
    ob=bpy.data.objects.new(text,curve);bpy.context.scene.collection.objects.link(ob)
    ob.location=(x,-.35,z);ob.rotation_euler=(1.5707963,0,0)
    mat=bpy.data.materials.get('Label white')
    if not mat:mat=bpy.data.materials.new('Label white');mat.diffuse_color=(.85,.9,1,1)
    curve.materials.append(mat)
def root(name,objects,x=0,z=0):
    e=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(e)
    for ob in objects:ob.parent=e
    e.location=(x,0,z);return e
for i,x in enumerate([-2.2,0,2.2],1):
    bpy.ops.import_scene.tw_anim(filepath=str(R/'reference/local/yuan-bo-model/animations/skeletons/humanoid01e.anim'))
    rig=next(o for o in bpy.context.selected_objects if o.type=='ARMATURE')
    rig.name='Body_%02d_native_humanoid01e'%i;rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    meshes=import_ws(P+'celestial_concubines_%02d.wsmodel'%i,rig)
    meshes+=import_ws(P+'celestial_concubines_head_%02d.wsmodel'%i,rig)
    root('BODY %02d + HEAD %02d'%(i,i),[rig]+meshes,x=x);rig.hide_set(True)
    label('BODY %02d + HEAD %02d'%(i,i),x,-.2)
for i,x in enumerate([-1.65,-.55,.55,1.65],1):
    meshes=import_ws(P+'celestial_concubines_head_%02d.wsmodel'%i)
    root('HEAD %02d'%i,meshes,x=x,z=1.25)
    label('HEAD %02d'%i,x,2.65,.13)
for i,kind in enumerate(['sword','shield']):
    meshes=import_ws('variantmeshes/wh_variantmodels/hu1e/cth/cth_props/celestial_concubines_'+kind+'.wsmodel')
    points=[ob.matrix_world@Vector(v) for ob in meshes for v in ob.bound_box]
    center=(Vector([min(p[k] for p in points) for k in range(3)])+Vector([max(p[k] for p in points) for k in range(3)]))/2
    e=root(kind.upper(),meshes);e.location=Vector((3.65,0,.65+i*1.1))-center
    label(kind.upper(),3.65,.05+i*1.1,.13)
label('CELESTIAL CONCUBINES | ORIGINAL MODEL VARIANTS',.5,3.95,.17)
label('Native bind pose | LOD0 preview | No mod changes',.5,-.48,.12)
assert not missing,missing
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
scene.render.engine='CYCLES';scene.cycles.samples=24
camdata=bpy.data.cameras.new('Comparison camera');cam=bpy.data.objects.new('Comparison camera',camdata);scene.collection.objects.link(cam)
target=Vector((.6,0,1.7));cam.location=(.6,-15,3.4);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=8.4;scene.camera=cam;cam.hide_set(True)
for name,pos,power in [('Key',(0,-5,6),1500),('Fill',(-5,-2,3),1000),('Rim',(3,4,5),1600)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=5
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=pos
    ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();ob.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=8
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
for im in bpy.data.images:
    if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT')
notes=bpy.data.texts.new('READ ME');notes.write('Private source-model comparison. Three original body variants paired with heads 01/02/03. Four independent heads above. Sword and shield at right. Native humanoid01e bind pose, LOD0 only for preview; original source has four LODs. No body/head edits or campaign/game changes.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),bodies=3,heads=4,props=2,parts=audit,missing_textures=missing,source_geometry_modified=False,game_modified=False),indent=2))
print('PREVIEW_READY',str(OUT),flush=True)
