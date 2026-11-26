"""Swap only the live right-hand knife using the donor's native prop grip."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix
R=Path('D:/Warhammer3_Modding/moon_cathay');O=R/'build/alchemist-11-no-back-cape'
data=json.loads((O/'death-squad-knife-grip.json').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(O/'before-death-squad-knife-live.blend'),copy=True)
rig=bpy.data.objects['Alchemist_11_NATIVE_RIG'];old_anchor=bpy.data.objects['Khainite dagger 01 | hand_right']
old=[o for o in old_anchor.children_recursive if o.type=='MESH'];assert old
for ob in old:ob.hide_set(True);ob.hide_render=True
with bpy.data.libraries.load(str(R/'build/cathay-ror-preview/dark-society-death-squad-models.blend'),link=False) as (src,dst):
    dst.objects=[data['source_object']]
knife=dst.objects[0];knife.constraints.clear();knife.parent=None
for m in list(knife.modifiers):
    if m.type=='ARMATURE':knife.modifiers.remove(m)
bpy.context.scene.collection.objects.link(knife)
anchor=bpy.data.objects.new('Death Squad knife | hand_right',None);bpy.context.scene.collection.objects.link(anchor)
con=anchor.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='hand_right'
knife.parent=anchor;knife.matrix_parent_inverse=Matrix.Identity(4);knife.matrix_basis=Matrix(data['relative_matrix'])
knife.name='Death Squad knife 01';knife.hide_set(False);knife.hide_render=False
knife['attachment']='Native ninja_knife_1 prop-to-hand transform, constrained to Alchemist hand_right'
frame=bpy.context.scene.frame_current;checks=[]
for f in (1,75,160,265,320,410):
    bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=knife.evaluated_get(dg)
    expected=rig.matrix_world@rig.pose.bones['hand_right'].matrix@Matrix(data['relative_matrix'])
    error=max(abs(expected[i][j]-ev.matrix_world[i][j]) for i in range(4) for j in range(4))
    assert error<1e-4,error
    assert all(math.isfinite(c) for row in ev.matrix_world for c in row)
    checks.append({'frame':f,'attachment_error':error})
bpy.context.scene.frame_set(frame);bpy.ops.file.pack_all()
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'alchemist-11-death-squad-knife.blend'),compress=True)
(O/'death-squad-knife-report.json').write_text(json.dumps({'new':knife.name,'hidden_old':[o.name for o in old],'handbow_unchanged':True,'checks':checks,'deployment':False},indent=2))
print('DEATH_SQUAD_KNIFE_OK')
