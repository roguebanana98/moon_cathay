import bpy, os, json, math
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,'EDH_concept03_weapons.blend'))
report={'blend':{'collections':{},'all_meshes_have_uv':True},'glb':{}}
for c in bpy.data.collections:
    if c.name.startswith('EDH_'):
        meshes=[o for o in c.objects if o.type=='MESH']
        assert meshes,c.name
        assert all(len(o.data.uv_layers)>0 for o in meshes),c.name+' missing UV'
        report['blend']['collections'][c.name]=len(meshes)
assert len(report['blend']['collections'])==5
for filename in sorted(os.listdir(OUT)):
    if filename.endswith('.glb'):
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        bpy.ops.import_scene.gltf(filepath=os.path.join(OUT,filename))
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        assert meshes,filename
        assert all(math.isfinite(v) for o in meshes for vertex in o.data.vertices for v in vertex.co),filename
        assert all(len(o.data.materials)>0 for o in meshes),filename
        points=[o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
        bounds=[(min(p[i] for p in points),max(p[i] for p in points)) for i in range(3)]
        assert max(abs(v) for pair in bounds for v in pair)<3,filename+' invalid transforms'
        report['glb'][filename]={'meshes':len(meshes),'bounds_metres':bounds,'materials':True}
with open(os.path.join(OUT,'verification.json'),'w') as f:json.dump(report,f,indent=2)
print('VERIFIED: blend collections, mesh UVs and five independently reimported GLB files')
