"""Restore human skin and use black armour borders with white scale fields."""
import bpy, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]
O = R / 'build/moon-generals-preview'
SOURCE = O / 'before-palette-fix.blend'
OUT = O / 'moon-generals-skin-and-armour-v3.blend'
assert SOURCE.exists() and not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))

def math_node(nodes, links, operation, a, b=None):
    n = nodes.new('ShaderNodeMath'); n.operation = operation
    for socket, value in zip(n.inputs, [a, b]):
        if value is None: continue
        if isinstance(value, (int, float)): socket.default_value = value
        else: links.new(value, socket)
    return n.outputs[0]

def rect(nodes, links, u, v, bounds):
    x0,x1,y0,y1 = bounds
    x = math_node(nodes,links,'MULTIPLY',math_node(nodes,links,'GREATER_THAN',u,x0),math_node(nodes,links,'LESS_THAN',u,x1))
    y = math_node(nodes,links,'MULTIPLY',math_node(nodes,links,'GREATER_THAN',v,y0),math_node(nodes,links,'LESS_THAN',v,y1))
    return math_node(nodes,links,'MULTIPLY',x,y)

def polygon_mask(nodes, links, u, v, points):
    # Points measured on the original unmodified 1024px UV atlas, top-left origin.
    points=[(x/1024,1-y/1024) for x,y in points]
    signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    mask=1
    for a,b in zip(points,points[1:]+points[:1]):
        lhs=math_node(nodes,links,'MULTIPLY',b[0]-a[0],math_node(nodes,links,'SUBTRACT',v,a[1]))
        rhs=math_node(nodes,links,'MULTIPLY',b[1]-a[1],math_node(nodes,links,'SUBTRACT',u,a[0]))
        cross=math_node(nodes,links,'SUBTRACT',lhs,rhs)
        inside=math_node(nodes,links,'GREATER_THAN' if signed>0 else 'LESS_THAN',cross,0)
        mask=math_node(nodes,links,'MULTIPLY',mask,inside)
    return mask

changes=[]
for ob in bpy.data.collections['Body | Bastion General'].objects:
    if ob.type != 'MESH': continue
    for slot in ob.material_slots:
        old = slot.material
        if not old or not old.use_nodes: continue
        mat = old.copy(); mat.name = 'Bastion corrected | ' + ob.name
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        image_nodes = [n for n in nodes if n.type=='TEX_IMAGE' and n.image]
        base = next(n for n in image_nodes if not any(w in n.image.filepath.lower() for w in ['_normal','_material_map']))
        original = base.outputs['Color']
        atlas = base.image.filepath.lower()
        if 'cth_celestial_general_body_base.' in atlas:
            replacement = nodes.new('ShaderNodeTexImage')
            replacement.image = next(i for i in bpy.data.images if 'cth_celestial_guard_white.' in i.filepath.lower())
            replacement.label = 'Exact compatible white armour atlas from model08'
            palette_source = replacement.outputs['Color']
        elif 'cth_celestial_general_body_jinjun.' in atlas:
            replacement = nodes.new('ShaderNodeTexImage')
            replacement.image = bpy.data.images.load(str(O/'palette-audit/cth_celestial_general_body_iron_white.png'),check_existing=True)
            replacement.label = 'Compatible native General white steel atlas'
            palette_source = replacement.outputs['Color']
        elif 'cth_alchemist_green.' in atlas:
            replacement=nodes.new('ShaderNodeTexImage')
            replacement.image=next(i for i in bpy.data.images if 'cth_alchemist_white.' in i.filepath.lower())
            replacement.label='Exact compatible white Alchemist atlas from model08'
            palette_source=replacement.outputs['Color']
        else:
            palette_source = original
        bw = nodes.new('ShaderNodeRGBToBW'); links.new(palette_source,bw.inputs[0])
        ramp = nodes.new('ShaderNodeValToRGB'); ramp.label = 'White scales / black original borders'
        stops = [(0,(.004,.004,.005,1)),(.025,(.009,.009,.011,1)),(.09,(.035,.035,.04,1)),(.18,(.54,.55,.56,1)),(.45,(.90,.91,.92,1)),(1,(.97,.97,.97,1))]
        for e in list(ramp.color_ramp.elements)[2:]: ramp.color_ramp.elements.remove(e)
        ramp.color_ramp.elements[0].position=0; ramp.color_ramp.elements[0].color=stops[0][1]
        ramp.color_ramp.elements[1].position=1; ramp.color_ramp.elements[1].color=stops[-1][1]
        for position,color in stops[1:-1]: ramp.color_ramp.elements.new(position).color=color
        links.new(bw.outputs[0],ramp.inputs[0]); result = ramp.outputs['Color']
        if 'cth_dragon_jade_human_guanyu_base_colour.' in atlas:
            # Keep the actual raised scale fields pale; leather/rims around them black.
            uv=nodes.new('ShaderNodeTexCoord');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs['UV'],sep.inputs[0])
            masks=[]
            for points in [
                [(452,35),(488,35),(495,170),(470,365),(455,353),(418,176)],
                [(536,37),(570,38),(609,178),(564,368),(538,354),(523,180)],
                [(653,33),(797,33),(802,139),(653,139)],
                [(844,61),(971,61),(971,94),(844,94)],
                [(730,295),(800,295),(800,406),(730,406)],
                [(138,466),(238,466),(238,548),(138,548)],
                [(680,580),(755,580),(755,727),(680,727)],
                [(837,618),(1018,618),(1018,970),(837,970)]]:
                masks.append(polygon_mask(nodes,links,sep.outputs['X'],sep.outputs['Y'],points))
            mask=masks[0]
            for m in masks[1:]:mask=math_node(nodes,links,'MAXIMUM',mask,m)
            low=nodes.new('ShaderNodeMixRGB');low.blend_type='MULTIPLY';low.inputs[0].default_value=1;links.new(bw.outputs[0],low.inputs[1]);low.inputs[2].default_value=(.10,.10,.10,1)
            power=math_node(nodes,links,'POWER',bw.outputs[0],.30)
            pale=math_node(nodes,links,'ADD',math_node(nodes,links,'MULTIPLY',power,.55),.35)
            mix=nodes.new('ShaderNodeMixRGB');links.new(mask,mix.inputs[0]);links.new(low.outputs[0],mix.inputs[1]);links.new(pale,mix.inputs[2]);result=mix.outputs[0]
        skin_mode='none'
        if 'cth_celestial_guard_head_02' in ob.name:
            # Exact two face islands in the original shared face/helmet atlas.
            uv=nodes.new('ShaderNodeTexCoord'); sep=nodes.new('ShaderNodeSeparateXYZ'); links.new(uv.outputs['UV'],sep.inputs[0])
            a=rect(nodes,links,sep.outputs['X'],sep.outputs['Y'],(.50,1.01,.38,.74))
            b=rect(nodes,links,sep.outputs['X'],sep.outputs['Y'],(.53,1.01,-.01,.33))
            mask=math_node(nodes,links,'MAXIMUM',a,b)
            mix=nodes.new('ShaderNodeMixRGB'); links.new(mask,mix.inputs[0]); links.new(result,mix.inputs[1]); links.new(original,mix.inputs[2]); result=mix.outputs[0]
            skin_mode='original colour within two face UV islands'
        elif any(s in ob.name for s in ['cth_alchemist_body_01','cth_celestial_guard_body_01 - Cl']):
            # Preserve original texture on hands only, using existing rig weights.
            attr=ob.data.color_attributes.get('Bastion original hand colour') or ob.data.color_attributes.new(name='Bastion original hand colour',type='FLOAT_COLOR',domain='POINT')
            names={g.index:g.name for g in ob.vertex_groups}
            for vertex in ob.data.vertices:
                weight=sum(g.weight for g in vertex.groups if any(s in names.get(g.group,'') for s in ['hand_','finger_','thumb_']))
                strength=max(0,min(1,(weight-.35)/.4))*max(0,min(1,(abs(vertex.co.x)-.60)/.035))
                attr.data[vertex.index].color=(strength,strength,strength,1)
            node=nodes.new('ShaderNodeVertexColor'); node.layer_name=attr.name
            mix=nodes.new('ShaderNodeMixRGB'); links.new(node.outputs['Color'],mix.inputs[0]); links.new(result,mix.inputs[1]); links.new(original,mix.inputs[2]);result=mix.outputs[0]
            skin_mode='original texture on hand and finger weights'
        elif any(s in ob.name for s in ['cth_peasant_head','beard','ksl_streltsi_head']):
            # These pieces contain skin, eyes, teeth, or natural hair. No global tint.
            result=original;skin_mode='original texture restored unchanged'
        links.new(result,bs.inputs['Base Color']);slot.material=mat
        changes.append(dict(object=ob.name,base_texture=base.image.filepath,skin=skin_mode))

# Pose, visibility, weapon placement and the entire Assault General remain intact.
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'palette-fix.json').write_text(json.dumps(dict(scene=str(OUT),changes=changes,assault_changed=False,geometry_changed=False),indent=2),encoding='utf8')
print('BASTION_PALETTE_FIXED',flush=True)
