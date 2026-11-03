"""Extract approved authored prop geometry in prop-local space for native RMV2 writing."""
import bpy,bmesh,json,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v22-da-lien-appearance';O.mkdir(parents=True,exist_ok=True)
scene=R/'build/da-lien-moon-staff/da-lien-moon-staff.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene))
rig=bpy.data.objects['Da_Lien_NATIVE_humanoid01ba'];parts=[]
for obj in bpy.data.collections['Da Lien - Moon Staff Head'].objects:
    assert obj.type=='MESH' and len(obj.constraints)==1
    c=obj.constraints[0];assert c.type=='COPY_TRANSFORMS' and c.target==rig and c.subtarget=='be_prop_5'
    assert max(abs(obj.matrix_basis[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    me=obj.data.copy()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    me.calc_loop_triangles();me.calc_tangents(uvmap=me.uv_layers[0].name)
    for material_index in sorted({p.material_index for p in me.polygons}):
        mat=obj.data.materials[material_index];p=mat.node_tree.nodes.get('Principled BSDF')
        triangles=[t for t in me.loop_triangles if t.material_index==material_index]
        if not triangles:continue
        # Expand corners: this preserves hard/bevel normals and UV seams unambiguously.
        positions=[];normals=[];tangents=[];binormals=[]
        for tri in triangles:
            for i in tri.loops:
                loop=me.loops[i];n=me.corner_normals[i].vector;t=loop.tangent
                positions.append(list(me.vertices[loop.vertex_index].co));normals.append(list(n))
                tangents.append(list(t));binormals.append(list(n.cross(t)*loop.bitangent_sign))
        parts.append({'name':obj.name+'_m'+str(material_index),'material':mat.name,
          'linear_color':list(p.inputs['Base Color'].default_value[:3]),'metallic':p.inputs['Metallic'].default_value,
          'roughness':p.inputs['Roughness'].default_value,'positions':positions,'normals':normals,
          'tangents':tangents,'binormals':binormals})
report={'approved_scene':str(scene),'approved_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),
 'parts':parts,'attachment':'be_prop_5','body_tint':list(bpy.data.materials['Da Lien | Warm Human Skin'].node_tree.nodes['DL_Subtle_Human_Skin'].inputs[2].default_value[:3])}
(O/'moon-head-geometry.json').write_text(json.dumps(report,separators=(',',':')))
print('APPROVED_HEAD_EXTRACTED',len(parts),'parts',sum(len(p['positions'])//3 for p in parts),'triangles')
