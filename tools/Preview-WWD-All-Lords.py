"""Build a separate texture-packed Blender gallery of the 22 WWD lord appearances."""
import bpy,addon_utils,json,subprocess,sys,hashlib,math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
O=R/'build/wwd-all-lords-preview';M=json.loads((O/'manifest.json').read_text(encoding='utf8'));D=Path(M['reference'])
OUT=O/'wwd-all-lords-gallery.blend';assert not OUT.exists(),'Preserve existing review scene'
sys.path.insert(0,str(R.parent/'tooling/model-workbench/blender-4.5.15-windows-x64/portable/scripts/addons'))
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials,import_anim
texture_paths=sorted({p for l in M['lords'] for c in l['components'] for part in c['parts'] for _,p in part['textures']})
converted={}
def convert(path):
    folder=O/'preview-textures'/hashlib.sha256(path.encode()).hexdigest()[:12];folder.mkdir(parents=True,exist_ok=True)
    dest=folder/(Path(path).stem+'.png')
    if not dest.exists():
        subprocess.run([C['texconv'],'-nologo','-y','-ft','png','-w','1024','-h','1024','-o',str(folder),str(D/path)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return path,dest.relative_to(O).as_posix()
with ThreadPoolExecutor(max_workers=8) as pool:
    for path,dest in pool.map(convert,texture_paths):converted[path]=dest
print('TEXTURES_READY',len(converted),flush=True)
scene=bpy.context.scene;scene.render.fps=30
matcache={};rigs=[];checks=[];missing_bones=[]
def text(body,location,size,color):
    curve=bpy.data.curves.new(body,'FONT');curve.body=body;curve.size=size;curve.align_x='CENTER'
    ob=bpy.data.objects.new(body,curve);scene.collection.objects.link(ob);ob.location=location;ob.rotation_euler=(math.pi/2,0,0)
    mat=bpy.data.materials.get('Label '+str(color))
    if mat is None:
        mat=bpy.data.materials.new('Label '+str(color));mat.diffuse_color=(*color,1);mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=.5
    curve.materials.append(mat);return ob
for i,lord in enumerate(M['lords']):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    bpy.ops.import_scene.tw_anim(filepath=str(D/('animations/skeletons/'+lord['skeleton']+'.anim')))
    rig=next(ob for ob in bpy.context.selected_objects if ob.type=='ARMATURE');rig.name='%02d %s | %s'%(i+1,lord['name'] or 'Zhao Yixuan',lord['skeleton']);rig.animation_data_clear()
    for bone in rig.pose.bones:bone.matrix_basis.identity()
    meshes=[]
    for component in lord['components']:
        bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=rig
        if component['skeleton']:rig.select_set(True)
        old=set(bpy.data.objects)
        bpy.ops.import_scene.rmv2(filepath=str(D/component['geometry']),build_materials=False,import_all_lods=False,attach_armature=bool(component['skeleton']))
        objs=[ob for ob in bpy.data.objects if ob not in old and ob.type=='MESH']
        col=next(c for ob in objs for c in ob.users_collection if 'lod0' in c.name)
        ordered=[ob for ob in col.objects if ob.type=='MESH'];assert len(ordered)==len(component['parts'])
        for ob,part in zip(ordered,component['parts']):
            key=json.dumps([part['textures'],part['alpha']])
            if key not in matcache:
                pairs=[(typ,converted[path]) for typ,path in part['textures']]
                matcache[key]=materials.build_material(part['name'],pairs,'TRANSPARENT' if part['alpha'] else 'OPAQUE',str(O))
            ob.data.materials.clear();ob.data.materials.append(matcache[key])
            ob['source_geometry']=component['geometry'];ob['source_wsmodel']=component['path']
            if not component['skeleton'] and component['attach']:
                bone=component['attach']
                if bone in rig.pose.bones:
                    constraint=ob.constraints.new('COPY_TRANSFORMS');constraint.target=rig;constraint.subtarget=bone
                else:missing_bones.append(dict(model=lord['unit'],geometry=component['geometry'],bone=bone))
        meshes.extend(ordered)
    if lord['idle']:
        bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
        import_anim.import_file(bpy.context,str(D/lord['idle']),{'mode':'ANIMATION','attach_meshes':False,'global_scale':1.0})
        rig.animation_data.action.name='%02d %s | ORIGINAL IDLE'%(i+1,lord['name'] or 'Zhao Yixuan');rig.animation_data.action.use_fake_user=True
    root=bpy.data.objects.new('%02d | %s'%(i+1,lord['name'] or 'Zhao Yixuan'),None);scene.collection.objects.link(root)
    for ob in [rig]+meshes:ob.parent=root
    root.location=((i%6-2.5)*3.5,0,(3-i//6)*3.8);root.scale=(lord['scale'],)*3
    lord['preview_number']=i+1;lord['collection_root']=root.name
    short=lord['name'].split(',')[0] if lord['name'] else 'Zhao Yixuan'
    label=text('%02d  %s'%(i+1,short),(root.location.x,-.5,root.location.z-.25),.15,(.95,.95,.95))
    cg=lord['anim']=='hu1e_dlc24_celestial_general'
    sub=text('CELESTIAL GENERAL' if cg else lord['skeleton'],(root.location.x,-.5,root.location.z-.47),.095,(1,.65,.18) if cg else (.55,.65,.75))
    rig.hide_set(True);rigs.append(rig)
    print('LORD_READY',i+1,lord['unit'],len(meshes),'meshes',flush=True)
scene.frame_set(1);bpy.context.view_layer.update()
for rig in rigs:
    for bone in rig.pose.bones:assert all(math.isfinite(v) for row in bone.matrix for v in row)
scene.world=bpy.data.worlds.new('Neutral model gallery');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1)
target=Vector((0,0,6.5));orientation=Vector((0,12,-.45)).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.clip_end=500
            sp.region_3d.view_location=target;sp.region_3d.view_distance=24;sp.region_3d.view_rotation=orientation;sp.region_3d.view_perspective='ORTHO'
scene.frame_start=1;scene.frame_end=100
notes=bpy.data.texts.new('WWD LORD GALLERY - READ ME');notes.write('Original mod models and original/native idle poses. No retarget or mod changes. Numbered roots identify each lord. Gold labels mark the original Celestial General animation users. Body/weapon/rig selection is independent of the planned Celestial General skill tree. Preview textures downsampled to1024, source DDS unchanged.\n\n'+json.dumps(M['lords'],indent=2))
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'preview-report.json').write_text(json.dumps(dict(scene=str(OUT),lords=M['lords'],models=len(M['lords']),textures=len(converted),missing_attachments=missing_bones,game_modified=False),indent=2),encoding='utf8')
print('WWD_ALL_LORDS_READY',flush=True)
