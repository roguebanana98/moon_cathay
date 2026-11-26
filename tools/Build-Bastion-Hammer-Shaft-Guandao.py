"""Keep vanilla hammer shaft; replace only its head with the guandao blade."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'build/moon-generals-preview'
SOURCE=O/'moon-generals-bastion-native-hammer.blend'
OUT=O/'moon-generals-bastion-hammer-shaft-guandao.blend'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
hammer=bpy.data.objects['Bastion | VANILLA Celestial General hammer']
root=hammer.parent;rig=bpy.data.objects['Bastion General | Native humanoid01e']
weapons=bpy.data.collections['Weapons | Bastion General'];hidden=bpy.data.collections['Hidden originals | Bastion General']

def duplicate_part(source,name,keep,collection):
    ob=source.copy();ob.data=source.data.copy();ob.name=name
    collection.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not keep(v.index)],context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    return ob

# Identify disconnected gold head surfaces, including its separate end caps.
adj=[set() for v in hammer.data.vertices]
for e in hammer.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
seen=set();head=set()
for start in range(len(adj)):
    if start in seen:continue
    pending=[start];seen.add(start);component=[]
    while pending:
        i=pending.pop();component.append(i)
        for j in adj[i]-seen:seen.add(j);pending.append(j)
    if min(hammer.data.vertices[i].co.x for i in component)<-.80:head.update(component)
assert 300<len(head)<len(hammer.data.vertices)-100
shaft=duplicate_part(hammer,'Bastion | Original hammer shaft',lambda i:i not in head,weapons)
shaft.hide_set(False);shaft.hide_render=False
gold=duplicate_part(hammer,'OPTION | Original golden hammer head',lambda i:i in head,hidden)
gold.hide_set(True);gold.hide_render=True
weapons.objects.unlink(hammer);hidden.objects.link(hammer);hammer.hide_set(True);hammer.hide_render=True

donor=bpy.data.objects['Guan Yu guandao | cth_terracotta_sentinel_spear_to']
old_transform=Matrix.Translation((-.65,0,0))@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Diagonal((.75,1,1,1))
inverse=old_transform.inverted()
original={v.index:inverse@v.co for v in donor.data.vertices}
blade=duplicate_part(donor,'Bastion | Guandao blade on native hammer shaft',lambda i:original[i].x<.15,weapons)
blade.data.transform(Matrix.Translation((-.80,0,0))@Matrix.Rotation(math.pi/2,4,'X')@inverse)
blade.parent=root;blade.matrix_parent_inverse.identity();blade.matrix_basis.identity()
blade.hide_set(False);blade.hide_render=False
for c in blade.constraints:
    if c.type=='COPY_TRANSFORMS':c.target=rig;c.subtarget='weapon_1'
assert len(blade.data.vertices)==416
shaft['edit']='Only disconnected golden head surfaces removed; native shaft vertices and UV unchanged'
blade['edit']='Guandao blade surfaces only; donor shaft and pommel excluded'
assert all(c.subtarget=='weapon_1' for ob in [shaft,blade] for c in ob.constraints if c.type=='COPY_TRANSFORMS')
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'hammer-shaft-guandao.json').write_text(json.dumps(dict(scene=str(OUT),source=str(SOURCE),head_vertices_hidden=len(head),native_shaft_vertices=len(shaft.data.vertices),blade_vertices=len(blade.data.vertices),native_shaft_unchanged=True,body_palette_and_rig_changed=False,game_modified=False),indent=2),encoding='utf8')
print('HAMMER_SHAFT_GUANDAO_READY',flush=True)
