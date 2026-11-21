"""Reversible shader-only black cloth preview from the user's live snapshot."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'build/alchemist-11-black-preview'
OUT=O/'alchemist-11-black-outfit-v2.blend';assert not OUT.exists()
# Keep a real 3D editor layout; the live snapshot was taken from the console.
bpy.ops.wm.open_mainfile(filepath=str(R/'build/more-alchemists-preview/more-alchemists-variants-03-to-12.blend'))
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
with bpy.data.libraries.load(str(O/'before-black-live-snapshot.blend'),link=False) as (source,target_objects):
    target_objects.objects=list(source.objects)
for ob in target_objects.objects:
    if ob:bpy.context.scene.collection.objects.link(ob)
root=bpy.data.objects['VARIANT 11'];keep=set(root.children_recursive)|{root}
for ob in bpy.data.objects:
    if ob not in keep:ob.hide_set(True);ob.hide_render=True
root.location=(0,0,0)
changed=[]
def mathnode(nt,op,a,b=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    if isinstance(a,(int,float)):n.inputs[0].default_value=a
    else:nt.links.new(a,n.inputs[0])
    if b is not None:
        if isinstance(b,(int,float)):n.inputs[1].default_value=b
        else:nt.links.new(b,n.inputs[1])
    return n.outputs[0]
for ob in keep:
    if ob.type!='MESH':continue
    for slot in ob.material_slots:
        mat=slot.material
        if not mat or not mat.use_nodes:continue
        image=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and
            ('cth_alchemist_body_01_base_colour' in n.image.name or 'hef_eltharion_body_base_colour' in n.image.name)),None)
        if not image:continue
        mat=mat.copy();mat.name='BLACK CLOTH | '+mat.name;slot.material=mat
        nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        original=bsdf.inputs['Base Color'].links[0].from_socket
        hsv=nt.nodes.new('ShaderNodeSeparateColor');hsv.mode='HSV';hsv.label='Separate cloth from saturated gold and red ornament'
        nt.links.new(original,hsv.inputs[0])
        mask=mathnode(nt,'LESS_THAN',hsv.outputs[1],.65)
        # Preserve blue/green jewellery even when its saturation is modest.
        cool=mathnode(nt,'MULTIPLY',mathnode(nt,'GREATER_THAN',hsv.outputs[0],.28),mathnode(nt,'GREATER_THAN',hsv.outputs[1],.22))
        mask=mathnode(nt,'MULTIPLY',mask,mathnode(nt,'SUBTRACT',1,cool))
        if 'hef_eltharion_body' in image.image.name:
            # This separate imported part is the grey hood, not the face/mask.
            mask=1
        if 'cth_alchemist_body' in image.image.name:
            # Anatomical weight mask follows both hands instead of confusing a
            # white sleeve UV island with skin. No vertex positions are changed.
            ob.data=ob.data.copy()
            attr=ob.data.attributes.new('preview_preserve_hands','FLOAT','POINT')
            groups={g.index for g in ob.vertex_groups if any(k in g.name for k in ['hand_','finger_','thumb_'])}
            for vertex in ob.data.vertices:
                weight=sum(g.weight for g in vertex.groups if g.group in groups)
                attr.data[vertex.index].value=min(1,weight*2)
            attribute=nt.nodes.new('ShaderNodeAttribute');attribute.attribute_name=attr.name
            mask=mathnode(nt,'MULTIPLY',mask,mathnode(nt,'SUBTRACT',1,attribute.outputs['Fac']))
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.label='Reversible black fabric tint'
        if isinstance(mask,(int,float)):mix.inputs[0].default_value=mask
        else:nt.links.new(mask,mix.inputs[0])
        nt.links.new(original,mix.inputs[1]);mix.inputs[2].default_value=(.025,.03,.04,1)
        nt.links.new(mix.outputs[0],bsdf.inputs['Base Color'])
        changed.append(dict(object=ob.name,material=mat.name))
assert changed,'No clothing materials selected'
scene=bpy.context.scene
camdata=bpy.data.cameras.new('Black outfit review');cam=bpy.data.objects.new('Black outfit review',camdata);scene.collection.objects.link(cam)
target=Vector((0,0,1.1));cam.location=(.45,-5,1.85);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=2.7;scene.camera=cam;cam.hide_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=next(s for s in area.spaces if s.type=='VIEW_3D');sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=3.5
            sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.object.select_all(action='DESELECT')
notes=bpy.data.texts.new('BLACK OUTFIT NOTES');notes.write('Variant 11 from live snapshot. Reversible shader tint: low-saturation cloth and hood to black, preserving saturated ornament, gold and skin UV islands. Source texture pixels and geometry unchanged. Other model variants hidden/preserved. Preview only; no game pack changes.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
(O/'black-preview.json').write_text(json.dumps(dict(scene=str(OUT),snapshot=str(O/'before-black-live-snapshot.blend'),material_changes=changed,texture_pixels_modified=False,geometry_modified=False,game_modified=False),indent=2))
print('BLACK_PREVIEW_READY',str(OUT),flush=True)
