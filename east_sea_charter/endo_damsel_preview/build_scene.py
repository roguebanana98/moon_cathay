import bpy,addon_utils,json,math,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;D=R/'reference';M=json.loads((R/'manifest.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import import_anim,import_rmv2,materials,skeleton
# Coherent Bretonnian preview colours instead of the importer's RGB test palette.
materials._PLAYER_COLOURS=((.025,.09,.32,1),(.75,.68,.48,1),(.65,.68,.72,1))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.2,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
def select(o=None):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o
    if o:o.select_set(True)
def load(path,prefix,rig=None,bone=None):
    xml=ET.parse(D/path);geometry=xml.findtext('geometry').strip().replace('\\','/').lower()
    mats={int(e.attrib['part_index']):e.text.strip().replace('\\','/').lower() for e in xml.findall('.//material') if e.attrib.get('lod_index')=='0'}
    select(rig);original=import_rmv2._build_mesh_object;counter=[0];objects=[]
    def build(model,version,name,scale,bone_names,options):
        i=counter[0];counter[0]+=1
        obj=original(model,version,name,scale,bone_names,{**options,'build_materials':False});obj.name=prefix+f' | part {i}'
        matpath=mats[i];tx=[]
        for t in ET.parse(D/matpath).findall('.//texture'):
            slot=t.findtext('slot');source=t.findtext('source','').strip().replace('\\','/').lower()
            ids={'t_xml_base_colour':27,'t_xml_normal':1,'t_xml_material_map':29,'t_xml_mask':3}
            if slot in ids and (D/source).exists():
                # Blender cannot decode some DX10 DDS variants; use lossless PNG previews.
                preview=str(Path(source).with_suffix('.png'))
                tx.append((ids[slot],preview if (D/preview).exists() else source))
        alpha='TRANSPARENT' if 'alpha_on' in matpath else 'OPAQUE'
        mat=materials.build_material(prefix+' | '+Path(matpath).stem,tx,alpha,str(D))
        for shader in mat.node_tree.nodes:
            if shader.type=='BSDF_PRINCIPLED':
                strength=shader.inputs['Emission Strength']
                for link in list(strength.links):mat.node_tree.links.remove(link)
                strength.default_value=0
        obj.data.materials.append(mat);obj.rmv2.alpha_mode=alpha;obj['source_model']=path
        objects.append(obj);return obj
    import_rmv2._build_mesh_object=build
    try:col,stats=import_rmv2.import_file(bpy.context,str(D/geometry),{'import_lods':'FIRST','attach_armature':rig is not None and bone is None,'texture_root':str(D),'build_materials':False})
    finally:import_rmv2._build_mesh_object=original
    col.name=prefix
    if bone:
        for obj in objects:
            assert not any(m.type=='ARMATURE' for m in obj.modifiers)
            con=obj.constraints.new('CHILD_OF');con.target=rig;con.subtarget=bone
            con.inverse_matrix=skeleton.bone_fix_quaternion(rig.data.bones[bone]).to_matrix().to_4x4().inverted()
    return objects
report=[];rigs=[]
for i,v in enumerate(M['variants']):
    select();rig,_,warn=import_anim.import_file(bpy.context,str(D/M['skeleton']),{'mode':'SKELETON'})
    rig.name=v['name']+' | humanoid01b';rig.data.display_type='STICK';rigs.append(rig)
    objects=[]
    for s in v['slots']:objects+=load(s['model'],v['name']+' | '+s['slot'],rig,s['bone'])
    select(rig);import_anim.import_file(bpy.context,str(D/M['pose']),{'mode':'ANIMATION','attach_meshes':True})
    rig.animation_data.action.name=v['name']+' | Native staff-and-sword pose'
    rig.location.x=(i-1.5)*1.65;rig.hide_render=True
    bpy.ops.object.text_add(location=(rig.location.x,-.35,-.13),rotation=(math.pi/2,0,0))
    label=bpy.context.object;label.name=v['name']+' | label';label.data.body=v['name'];label.data.align_x='CENTER';label.data.size=.16
    report.append({'variant':v['name'],'mesh_parts':len(objects),'triangles':sum(len(o.data.polygons) for o in objects),'skeleton_bones':len(rig.data.bones)})
    print('IMPORTED',v['name'],len(objects),'parts',flush=True)
scene.frame_set(1)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for pos,power,size in [((2,-5,6),1200,6),((-5,-2,3),900,5),((0,3,5),1400,5)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(.1,-12,2.3));cam=bpy.context.object;cam.name='CAM | Four Damsels';cam.data.type='ORTHO';cam.data.ortho_scale=7.5;aim(cam,(0,0,1));scene.camera=cam
scene.view_settings.view_transform='AgX'
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
select()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_location=Vector((0,0,1));sp.region_3d.view_distance=6
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
            sp.overlay.show_overlays=False;sp.shading.type='MATERIAL';sp.shading.studiolight_rotate_z=.6
            sp.clip_end=1000
scene['source_mod']='[Endo] Damsel / Workshop 3702690266 / @endo_damsel.pack'
scene['preview_notes']='4 campaign variants, native humanoid01b staff-and-sword pose. Default black hair masks missing in source are omitted (neutral no-tint).'
file=R/'Endo_Damsel_All_4_Variants.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(file))
(R/'preview_report.json').write_text(json.dumps({'variants':report,'packed_images':sum(bool(im.packed_file) for im in bpy.data.images),'blend':str(file)},indent=2))
print('READY',str(file),flush=True)
