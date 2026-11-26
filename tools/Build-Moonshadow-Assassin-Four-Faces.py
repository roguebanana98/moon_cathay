"""Four editable Moonshadow Assassin appearances from the approved live body."""
import bpy,bmesh,json,math,hashlib,struct
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];O=R/'build/moonshadow-assassin-four-faces'
bpy.ops.wm.open_mainfile(filepath=str(O/'approved-body-live.blend'))
source_root=bpy.data.objects['VARIANT 11'];source_rig=bpy.data.objects['Alchemist_11_NATIVE_RIG']
original_objects=list(bpy.data.objects)
source_body=[o for o in source_root.children_recursive if o.type=='MESH' and not o.hide_get()]
def isface(o):return o.name.startswith('cth_alchemist_head_') or o.name.startswith('hef_eltharion_body_submesh_92')
common=[o for o in source_body if not isface(o)]
heads={}
for n in (8,11,3,12):
    meshes=[o for o in bpy.data.objects['VARIANT %02d'%n].children_recursive if o.type=='MESH']
    if n in (8,3):heads[n]=[o for o in meshes if o.name.startswith('cth_alchemist_head_')]
    elif n==11:heads[n]=[o for o in source_body if isface(o)]
    else:heads[n]=[o for o in meshes if not o.name.startswith('cth_alchemist_body_') and o.name!='cth_nan_gau_warrior_head_02_subm.001']
    assert heads[n]
    donor=next(o for o in bpy.data.objects['VARIANT %02d'%n].children_recursive if o.type=='ARMATURE')
    for bone in donor.data.bones:
        target=source_rig.data.bones.get(bone.name);assert target
        assert max(abs(bone.matrix_local[i][j]-target.matrix_local[i][j]) for i in range(4) for j in range(4))<1e-5
anchors=[bpy.data.objects['Death Squad knife | hand_right'],bpy.data.objects['Khainite handbow | hand_left']]
props=[o for a in anchors for o in a.children_recursive if o.type=='MESH' and not o.hide_get()]
assert len(props)==2
def fingerprint(me):return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in me.vertices)).hexdigest()
models=[];new_objects=set();scene=bpy.context.scene
for index,n in enumerate((8,11,3,12),1):
    col=bpy.data.collections.new('Moonshadow Assassin %02d | face %02d'%(index,n));scene.collection.children.link(col)
    root=bpy.data.objects.new('Moonshadow Assassin %02d | Face %02d'%(index,n),None);col.objects.link(root);new_objects.add(root)
    root.location=((index-2.5)*1.65,0,0);root['hero']='Moonshadow Assassin';root['face_source']=n
    mapping={}
    for old in [source_rig]+common+anchors+props:
        ob=old.copy()
        if old.data:ob.data=old.data.copy()
        ob.name='MSA %02d | %s'%(index,old.name);col.objects.link(ob);mapping[old]=ob;new_objects.add(ob)
    rig=mapping[source_rig]
    for old,ob in mapping.items():
        ob.parent=mapping.get(old.parent,root);ob.matrix_parent_inverse=old.matrix_parent_inverse.copy();ob.matrix_basis=old.matrix_basis.copy()
        for m in ob.modifiers:
            if m.type=='ARMATURE':m.object=rig
        for con in ob.constraints:
            if hasattr(con,'target') and con.target in mapping:con.target=mapping[con.target]
        ob.hide_set(ob.type=='ARMATURE');ob.hide_render=False
        if ob.type=='MESH':assert fingerprint(ob.data)==fingerprint(old.data)
    face_objects=[]
    for old in heads[n]:
        ob=old.copy();ob.data=old.data.copy();ob.name='MSA %02d | Face %02d | %s'%(index,n,old.name)
        col.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
        if n in (3,12):
            # Native hair bun/hairpin islands extend above the common hood.
            # Remove whole accessory islands only, never cut across the face.
            bm=bmesh.new();bm.from_mesh(ob.data);unseen=set(bm.verts);remove=[]
            while unseen:
                seed=unseen.pop();part={seed};stack=[seed]
                while stack:
                    v=stack.pop()
                    for edge in v.link_edges:
                        other=edge.other_vert(v)
                        if other in unseen:unseen.remove(other);part.add(other);stack.append(other)
                if min(v.co.z for v in part)>1.70:remove.extend(part)
            bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);bm.free()
            ob['hood_fit']='Separate bun/hairpin islands above 1.70m omitted; original face surface retained.'
        for m in ob.modifiers:
            if m.type=='ARMATURE':m.object=rig
        ob.hide_set(False);ob.hide_render=False;new_objects.add(ob);face_objects.append(ob)
    # Labels are outside each model collection, so individual model files have no floating title.
    curve=bpy.data.curves.new('MSA label','FONT');curve.body='Moonshadow Assassin\nFace %02d'%n;curve.align_x='CENTER';curve.size=.115
    label=bpy.data.objects.new('LABEL | Face %02d'%n,curve);scene.collection.objects.link(label)
    label.location=(root.location.x,-.18,-.1);label.rotation_euler=(math.pi/2,0,0);new_objects.add(label)
    models.append(dict(index=index,face=n,root=root,rig=rig,objects=list(mapping.values())+face_objects+[root],heads=face_objects,label=label,x=root.location.x))
for ob in original_objects:ob.hide_set(True);ob.hide_render=True
report={'hero':'Moonshadow Assassin','source':'approved-body-live.blend','variants':[],'deployment':False,'animation_status':'Existing preview retarget retained; finger closure and cloth remain unfinished.'}
for model in models:
    tests=[];motion=[]
    for frame in (1,75,160,265,391,441):
        scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();rig=model['rig']
        for head in model['heads']:
            ev=head.evaluated_get(dg);me=ev.to_mesh();assert all(math.isfinite(c) for v in me.vertices for c in v.co);ev.to_mesh_clear()
        motion.append(tuple(rig.pose.bones['head_0'].matrix.translation));tests.append(frame)
        for old_anchor in anchors:
            anchor=next(o for o in model['objects'] if o.name.endswith(old_anchor.name))
            con=anchor.constraints[0];actual=anchor.evaluated_get(dg).matrix_world;expected=rig.matrix_world@rig.pose.bones[con.subtarget].matrix
            assert max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-4
    assert max((Vector(p)-Vector(motion[0])).length for p in motion)>1e-3
    report['variants'].append({'number':model['index'],'face_source':model['face'],'head_objects':[o.name for o in model['heads']],'samples':tests,'file':'moonshadow-assassin-face-%02d.blend'%model['face']})
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='CONSOLE':area.type='VIEW_3D'
bpy.ops.file.pack_all();layout=O/'comparison-layout.blend';bpy.ops.wm.save_as_mainfile(filepath=str(layout),copy=True,compress=True)
# Reopen before touching SpaceView3D after conversion from console layout.
bpy.ops.wm.open_mainfile(filepath=str(layout))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.overlay.show_overlays=False;sp.shading.type='MATERIAL'
            sp.region_3d.view_location=Vector((0,0,.95));sp.region_3d.view_distance=7.0
            sp.region_3d.view_rotation=Quaternion((math.sqrt(.5),math.sqrt(.5),0,0));sp.region_3d.view_perspective='ORTHO'
comparison=O/'moonshadow-assassin-four-faces.blend';bpy.ops.wm.save_as_mainfile(filepath=str(comparison),compress=True)
# Each file opens on one complete appearance, at the origin. Other variants remain hidden backups.
for variant in report['variants']:
    bpy.ops.wm.open_mainfile(filepath=str(comparison))
    root_name='Moonshadow Assassin %02d | Face %02d'%(variant['number'],variant['face_source'])
    root=bpy.data.objects[root_name]
    keep={root}|set(root.children_recursive)
    for ob in bpy.data.objects:
        if ob not in keep:ob.hide_set(True);ob.hide_render=True
    root.location=(0,0,0)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=3.0
    bpy.ops.wm.save_as_mainfile(filepath=str(O/variant['file']),compress=True)
(O/'four-faces-report.json').write_text(json.dumps(report,indent=2));print('FOUR_FACES_OK',flush=True)
