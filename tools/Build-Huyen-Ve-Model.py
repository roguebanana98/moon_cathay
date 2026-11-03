"""Private model prototype: donor-surface weight transfer, LODs, RMV2 and posed QA.

Never writes to game/Workshop or overwrites the user's FBX. Donor geometry stays
only in the ignored build scene as hidden reference, never in exported meshes.
"""
import bpy, addon_utils, json, math, subprocess
import sys
if '--experimental-rebuild-hands' not in sys.argv:
    raise RuntimeError('Retired experimental hand generator. Use Build-Huyen-Ve-Animation-Scene.py with the approved manual sword snapshot. This script requires --experimental-rebuild-hands to run deliberately.')
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
import numpy as np

R=Path(__file__).resolve().parents[1]
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'))
REF=R/'reference/local/yuan-bo-model'
OUT=R/'build/huyen-ve-model-v1';OUT.mkdir(parents=True,exist_ok=True)
INTERNAL='variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve'
GEO=OUT/INTERNAL;GEO.mkdir(parents=True,exist_ok=True)
TMP=OUT/'texture-intermediate';TMP.mkdir(exist_ok=True)
report={'status':'prototype_in_progress','method':'UV-preserving decimation; posed donor barycentric weight transfer; inverse LBS to native bind pose', 'runtime_verified':False}
bpy.ops.wm.read_factory_settings(use_empty=True);addon_utils.enable('io_scene_rmv2')
from io_scene_rmv2 import materials

def select(objects,active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=active or objects[0]

def decimate(o,target):
    select([o]);o.data.calc_loop_triangles();count=len(o.data.loop_triangles)
    if count>target:
        m=o.modifiers.new('UV-preserving polygon reduction','DECIMATE');m.ratio=target/count;m.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=m.name)
    o.data.calc_loop_triangles()
    return len(o.data.loop_triangles)

def remove_small_islands(o,area_threshold):
    import bmesh
    bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);remove=[]
    while remaining:
        start=remaining.pop();stack=[start];component={start}
        while stack:
            vertex=stack.pop()
            for edge in vertex.link_edges:
                other=edge.other_vert(vertex)
                if other in remaining:remaining.remove(other);component.add(other);stack.append(other)
        faces={f for v in component for f in v.link_faces}
        if sum(f.calc_area() for f in faces)<area_threshold:remove.extend(component)
    bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()

def collection(name,parent=None):
    c=bpy.data.collections.new(name);(parent or bpy.context.scene.collection).children.link(c);return c

def move(o,c):
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o)

def normalize(o,limit):
    empty=0;maximum=0;error=0
    for v in o.data.vertices:
        weights=sorted([(g.group,g.weight) for g in v.groups if g.weight>1e-6],key=lambda x:-x[1])[:limit]
        for g in list(v.groups):o.vertex_groups[g.group].remove([v.index])
        if not weights:empty+=1;continue
        total=sum(w for _,w in weights)
        for group,w in weights:o.vertex_groups[group].add([v.index],w/total,'REPLACE')
        maximum=max(maximum,len(weights));error=max(error,abs(sum(g.weight for g in v.groups)-1))
    assert empty==0,(o.name,empty)
    return dict(unweighted=empty,max_influences=maximum,max_normalization_error=error)

# Source stays untouched; this scene is a derivative in ignored build/.
bpy.ops.import_scene.fbx(filepath=str(next((R/'assets/authored/ancient warrior armor 3d model').glob('*.fbx'))))
body=next(o for o in bpy.context.selected_objects if o.type=='MESH');body.name='mc_huyen_ve_body_lod0'
select([body]);body.scale*=1.96;body.location.y+=.025
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for v in body.data.vertices:
    p=v.co
    if abs(p.x)>.25 and p.z>.70:
        f=smooth(.25,.33,abs(p.x))*(1-smooth(.91,1.16,p.z))
        p.z-=.085*f;p.x-=math.copysign(.018*f,p.x)
report['body_scale_from_fbx']=1.96
report['forearm_fit_adjustment']='smooth distal extension -0.085 Z, 0.018 inward to match donor wrist landmarks'
report['body_lod0_triangles']=decimate(body,24000)
body.data.update()
# Preserve joined Tripo surfaces. A continuous leg/robe weight field avoids
# opening seams at the ankles or tearing triangles across an arbitrary cut.
regions=[0]*len(body.data.vertices)
report['leg_weight_method']='continuous ankle-to-robe transition; no geometric cuts'
select([body]);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
bpy.ops.import_scene.tw_anim(filepath=str(REF/'animations/skeletons/humanoid01e.anim'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.name='humanoid01e_HuyenVe'
select([rig]);bpy.ops.import_scene.rmv2(filepath=str(REF/'variantmeshes/wh_variantmodels/hu1e/cth/cth_dragon_jade_human/cth_dragon_jade_human_01.rigid_model_v2'),build_materials=False)
donors=[o for o in bpy.data.objects if o.type=='MESH' and o!=body]
donor=max(donors,key=lambda o:len(o.data.vertices))

# Match the donor to the input's low-A pose before finding corresponding skin.
def point_bone(name,direction):
    pb=rig.pose.bones[name];bpy.context.view_layer.update()
    q=(pb.tail-pb.head).rotation_difference(Vector(direction))
    pb.matrix=Matrix.Translation(pb.head)@q.to_matrix().to_4x4()@Matrix.Translation(-pb.head)@pb.matrix
    bpy.context.view_layer.update()
for side,sgn in [('left',1),('right',-1)]:
    point_bone('upperarm_'+side,(sgn*.125,-.015,-.26))
    point_bone('lowerarm_'+side,(sgn*.06,-.02,-.245))
    point_bone('hand_'+side,(sgn*.025,-.01,-.09))
fit_matrices={b.name:(rig.pose.bones[b.name].matrix@b.matrix_local.inverted()).copy() for b in rig.data.bones}
import sys
sys.path.insert(0,str(R/'tools'))
from HuyenVeHands import rebuild_hands,finger_preservation
report['hand_fit'],hand_weights=rebuild_hands(body,rig,OUT)
regions=[0]*len(body.data.vertices)
dg=bpy.context.evaluated_depsgraph_get();evaluated=donor.evaluated_get(dg)
dm=evaluated.to_mesh();dm.calc_loop_triangles()
coords=[donor.matrix_world@v.co for v in dm.vertices]
tris=[tuple(t.vertices) for t in dm.loop_triangles]
tree=BVHTree.FromPolygons(coords,tris,all_triangles=True)
donor_weights=[{donor.vertex_groups[g.group].name:g.weight for g in v.groups} for v in donor.data.vertices]
for b in rig.data.bones:body.vertex_groups.new(name=b.name)
distances=[];inverse_error=[];fit_positions=[];cloth_strengths=[]
for v in body.data.vertices:
    p=v.co.copy();fit_positions.append(p.copy());near,normal,idx,dist=tree.find_nearest(p);distances.append(dist)
    tri=tris[idx];bc=barycentric_transform(near,*[coords[i] for i in tri],Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
    weights={}
    for i,factor in zip(tri,bc):
        for name,w in donor_weights[i].items():weights[name]=weights.get(name,0)+max(0,float(factor))*w
    # A compact topknot and clean-shaven face must not inherit beard/crown bones.
    if p.z>1.53 and abs(p.x)<.135:weights={'head_0':1}
    elif p.z>1.45 and abs(p.x)<.13:
        t=max(0,min(1,(p.z-1.45)/.08));weights={'neck_1':1-t,'head_0':t}
    else:
        for name in list(weights):
            if any(t in name for t in ('beard','crest','feather','ponytail','eyelid','eyebrow','jaw')):
                weights['head_0']=weights.get('head_0',0)+weights.pop(name)
    for name in list(weights):
        if 'cape_' in name:
            replacement='spine_0' if p.z<1.10 else 'spine_2'
            weights[replacement]=weights.get(replacement,0)+weights.pop(name)
    # Long robe panels: skirt chains instead of a rigid torso or one lower leg.
    strength=0
    if .15<p.z<.98 and not (abs(p.x)>.265 and p.z>.68):
        side='left' if p.x>=0 else 'right'
        t=max(0,min(1,(.63-p.z)/.25))
        def smooth(a,b,x):
            t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
        strength=max(smooth(.085,.13,-p.y),smooth(.075,.12,p.y),smooth(.145,.20,abs(p.x)))
        strength*=smooth(.15,.24,p.z)*(1-smooth(.90,.98,p.z))
        weights={k:w*(1-strength) for k,w in weights.items()}
        back=smooth(-.08,.12,p.y);left=smooth(-.16,.16,p.x)
        prefixes={'skirt_back_left':back*left,'skirt_back_right':back*(1-left),'skirt_front_center':1-back}
        for prefix,factor in prefixes.items():
            for k,w in {prefix+'_0':1-t,prefix+'_1':t}.items():weights[k]=weights.get(k,0)+w*strength*factor
    if v.index in hand_weights:weights=hand_weights[v.index];strength=0
    cloth_strengths.append(strength)
    weights=dict(sorted([(k,w) for k,w in weights.items() if w>1e-5],key=lambda x:-x[1])[:4])
    total=sum(weights.values());assert total>0
    weights={k:w/total for k,w in weights.items()}
    matrix=Matrix([[0.0]*4 for _ in range(4)])
    for name,w in weights.items():matrix+=fit_matrices[name]*w
    bind=matrix.inverted()@p;inverse_error.append((matrix@bind-p).length);v.co=bind
    for name,w in weights.items():body.vertex_groups[name].add([v.index],w,'REPLACE')
evaluated.to_mesh_clear()
# Smooth weights across neighbouring triangles and coincident UV seam vertices.
# Recompute inverse bind afterwards so the approved low-A pose remains unchanged.
names=[g.name for g in body.vertex_groups];W=np.zeros((len(body.data.vertices),len(names)),dtype=np.float64)
for v in body.data.vertices:
    for g in v.groups:W[v.index,g.group]=g.weight
edges=[tuple(e.vertices) for e in body.data.edges]
from mathutils.kdtree import KDTree
kd=KDTree(len(fit_positions))
for i,p in enumerate(fit_positions):kd.insert(p,i)
kd.balance()
for i,p in enumerate(fit_positions):
    for co,j,d in kd.find_range(p,.001):
        if j>i and regions[i]==regions[j]:edges.append((i,j))
original_W=W.copy();edge_array=np.array(edges,dtype=np.int32);src=np.concatenate((edge_array[:,0],edge_array[:,1]));dst=np.concatenate((edge_array[:,1],edge_array[:,0]));degree=np.bincount(src,minlength=len(W)).clip(1)
for _ in range(18):
    sums=np.zeros_like(W);np.add.at(sums,src,W[dst]);W=.35*W+.65*sums/degree[:,None]
keep_cloth=np.array([smooth(.75,1,x) for x in cloth_strengths])[:,None]
W=W*(1-keep_cloth)+original_W*keep_cloth
keep_fingers=np.array([1 if i in hand_weights else finger_preservation(p,rig) for i,p in enumerate(fit_positions)])[:,None]
W=W*(1-keep_fingers)+original_W*keep_fingers
for i,p in enumerate(fit_positions):
    allowed=None
    arm_zone=(abs(p.x)>.30 and p.z>.65) or (abs(p.x)>.24 and p.z>1.10)
    if arm_zone:
        side='_left' if p.x>0 else '_right'
        allowed=[j for j,n in enumerate(names) if side in n and n.startswith(('clav_','upperarm_','lowerarm_','hand_','finger_','thumb_','shoulderpad_'))]
    elif abs(p.x)<.20 and .98<p.z<1.28:
        allowed=[j for j,n in enumerate(names) if n.startswith(('spine_','armour_side_')) or n=='root']
    if allowed is not None:
        mask=np.zeros(W.shape[1]);mask[allowed]=1;W[i]*=mask
        if W[i].sum()<1e-8:
            fallback=(('hand'+side) if p.z<.9 else ('lowerarm'+side) if p.z<1.15 else ('upperarm'+side)) if arm_zone else 'spine_2'
            W[i,names.index(fallback)]=1
        W[i]/=W[i].sum()
    # Boots/trouser legs must never inherit nearby long-coat or cape weights.
    leg_zone=p.z<.93
    if leg_zone:
        # Entire boots, including wide soles, follow legs. Higher up only the
        # inner trouser volume does so; exterior cloth keeps skirt animation.
        inner=(1-smooth(.12,.21,abs(p.x)))*(1-smooth(.075,.15,abs(p.y)))
        influence=max(1-smooth(.30,.46,p.z),inner)*(1-smooth(.86,.96,p.z))
        legweights=np.zeros(W.shape[1])
        foot=1-smooth(.12,.25,p.z);upper=smooth(.43,.60,p.z)
        left=smooth(-.045,.045,p.x)
        for side,factor in [('_left',left),('_right',1-left)]:
            weights={'foot'+side:foot,'lowerleg'+side:(1-foot)*(1-upper),'upperleg'+side:(1-foot)*upper}
            for name,w in weights.items():legweights[names.index(name)]=w*factor
        W[i]=W[i]*(1-influence)+legweights*influence
# Smooth the final leg/cloth mixture as well as the donor weights. Applying
# the analytic field after smoothing otherwise leaves steep gradients around
# fused cloth/trouser contacts. Keep the boots and upper body anchored.
relax=np.array([smooth(.23,.34,p.z)*(1-smooth(.84,.97,p.z)) if abs(p.x)<.265 or p.z<.65 else 0 for p in fit_positions])[:,None]
for _ in range(32):
    sums=np.zeros_like(W);np.add.at(sums,src,W[dst])
    W=W*(1-.65*relax)+(sums/degree[:,None])*(.65*relax)
report['leg_cloth_relaxation_iterations']=32
inverse_error=[]
for v,p,row in zip(body.data.vertices,fit_positions,W):
    keep=np.argsort(row)[-4:];rowkeep=row[keep];rowkeep/=rowkeep.sum()
    for g in list(v.groups):body.vertex_groups[g.group].remove([v.index])
    matrix=Matrix([[0.0]*4 for _ in range(4)])
    for i,w in zip(keep,rowkeep):
        if w>1e-6:body.vertex_groups[int(i)].add([v.index],float(w),'REPLACE');matrix+=fit_matrices[names[int(i)]]*float(w)
    v.co=matrix.inverted()@p;inverse_error.append((matrix@v.co-p).length)
report['weight_smoothing_iterations']=18
for pb in rig.pose.bones:pb.matrix_basis.identity()
bpy.context.view_layer.update()
body.parent=rig;mod=body.modifiers.new('humanoid01e native skin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False
report['donor_transfer_distance']={'p50':float(np.percentile(distances,50)),'p95':float(np.percentile(distances,95)),'max':max(distances)}
report['inverse_bind_max_error']=max(inverse_error)
report['body_weights']=normalize(body,4)

# Dedicated export roots exclude hidden native reference meshes.
refcol=collection('REFERENCE_NATIVE_DO_NOT_EXPORT')
for o in donors:move(o,refcol);o.hide_render=True;o.hide_set(True)
root=collection('mc_huyen_ve_body');root.rmv2.is_rmv2_root=True;root.rmv2.skeleton_name='humanoid01e';root.rmv2.version='8';move(rig,root)
def texture_slots(o,stem,fmt):
    o.rmv2.vertex_format=fmt;o.rmv2.material_id='AUTO';o.rmv2.alpha_mode='OPAQUE';o.rmv2.textures.clear()
    pairs=[]
    for typ,suffix in [(27,'base_colour'),(29,'material_map'),(1,'normal'),(3,'mask')]:
        path=INTERNAL+'/tex/'+stem+'_'+suffix+'.dds';s=o.rmv2.textures.add();s.set_type_from_int(typ);s.path=path;pairs.append((typ,path))
    o.rmv2.textures_initialized=True
    mat=materials.build_material(stem,pairs,'OPAQUE',str(OUT));o.data.materials.clear();o.data.materials.append(mat)
    for p in o.data.polygons:p.material_index=0
texture_slots(body,'mc_huyen_ve_body','CINEMATIC')
body_lods=[]
for level,target in enumerate([24000,14000,8000,4000]):
    col=collection('body_lod'+str(level),root);col.rmv2.lod_level=level;col.rmv2.camera_distance=[10,20,30,10000][level];col.rmv2.lod_values_set=True
    if level==0:o=body;decimate(o,target);normalize(o,4)
    else:o=body.copy();o.data=body.data.copy();col.objects.link(o);o.name='mc_huyen_ve_body_lod'+str(level);decimate(o,target);normalize(o,4 if level<2 else 2)
    move(o,col);o.rmv2.vertex_format='CINEMATIC' if level<2 else 'WEIGHTED';body_lods.append(o)
    o.hide_render=level>0;o.hide_set(level>0)
report['body_lods']=[{'level':i,'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices)} for i,o in enumerate(body_lods)]

# Load only authored sword meshes, never native sword geometry.
with bpy.data.libraries.load(str(R/'assets/authored/moon-warden/concept03-v1/moon-warden-lotus-sword-v1.blend'),link=False) as (src,dst):dst.objects=list(src.objects)
loaded=[o for o in dst.objects if o and o.type=='MESH']
# Extend only the authored handle/pommel to support the native two-hand grip.
for o in loaded:
    if any(part in o.name.lower() for part in ('grip','pommel')):
        inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            p=o.matrix_world@v.co;p.z=-.095+(p.z+.095)*1.30;v.co=inv@p
report['sword_grip_fit']={'prop_translation':[-.035,.020,0],'handle_length_scale':1.30}
swroot=collection('mc_huyen_ve_sword');swroot.rmv2.is_rmv2_root=True;swroot.rmv2.version='8';swroot.rmv2.skeleton_name=''
swcol=collection('sword_lod0',swroot)
for o in loaded:swcol.objects.link(o)
select(loaded);bpy.ops.object.join();sword=bpy.context.object;sword.name='mc_huyen_ve_sword_lod0'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
decimate(sword,1800)
rotation=Matrix(((0,0,1),(1,0,0),(0,1,0)))
for v in sword.data.vertices:v.co=rotation@v.co*1.3+Vector((-.035,.020,0))
sword.data.update()
select([sword]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8
for kind in ['base_colour','material_map']:
    image=bpy.data.images.new('sword_bake_'+kind,width=1024,height=1024,alpha=True);image.colorspace_settings.name='sRGB' if kind=='base_colour' else 'Non-Color'
    for mat in sword.data.materials:
        mat.use_nodes=True;nodes=mat.node_tree.nodes;bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        color=tuple(bsdf.inputs['Base Color'].default_value) if kind=='base_colour' else (bsdf.inputs['Metallic'].default_value,bsdf.inputs['Roughness'].default_value,1,1)
        emission=nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=color
        mat.node_tree.links.new(emission.outputs[0],next(n for n in nodes if n.type=='OUTPUT_MATERIAL').inputs['Surface'])
        tex=nodes.new('ShaderNodeTexImage');tex.image=image;nodes.active=tex
    select([sword]);bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True)
    image.filepath_raw=str(TMP/('mc_huyen_ve_sword_'+kind+'.png'));image.file_format='PNG';image.save()
    subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f','BC7_UNORM_SRGB' if kind=='base_colour' else 'BC7_UNORM','-o',str(GEO/'tex'),image.filepath_raw],check=True)
for kind,color in [('normal',(1,.5,0,.5)),('mask',(0,0,0,0))]:
    im=bpy.data.images.new('sword_'+kind,width=512,height=512,alpha=True);im.generated_color=color;im.colorspace_settings.name='Non-Color';im.filepath_raw=str(TMP/('mc_huyen_ve_sword_'+kind+'.png'));im.file_format='PNG';im.save()
    subprocess.run([C['texconv'],'-nologo','-y','-m','0','-f','BC3_UNORM','-o',str(GEO/'tex'),im.filepath_raw],check=True)
texture_slots(sword,'mc_huyen_ve_sword','STATIC')
# Export as a local static prop first; the display-only bone attachment comes later.
sword_lods=[sword]
for level,target in enumerate([1800,1100,600,300]):
    if level==0:col=swcol;o=sword
    else:
        col=collection('sword_lod'+str(level),swroot);o=sword.copy();o.data=sword.data.copy();col.objects.link(o);o.name='mc_huyen_ve_sword_lod'+str(level)
        if level>=2:remove_small_islands(o,.00010 if level==2 else .00075)
        decimate(o,target);sword_lods.append(o)
    col.rmv2.lod_level=level;col.rmv2.camera_distance=[10,20,30,10000][level];col.rmv2.lod_values_set=True;o.hide_render=level>0;o.hide_set(level>0)
report['sword_lods']=[{'level':i,'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices)} for i,o in enumerate(sword_lods)]

# Export from the two explicit model roots, excluding armature deformation.
def activate_collection(col):
    def find(layer):
        if layer.collection==col:return layer
        for child in layer.children:
            found=find(child)
            if found:return found
    bpy.context.view_layer.active_layer_collection=find(bpy.context.view_layer.layer_collection)
for col,filename,skel in [(root,'mc_huyen_ve_body.rigid_model_v2','humanoid01e'),(swroot,'mc_huyen_ve_sword.rigid_model_v2','')]:
    activate_collection(col);select([body if col==root else sword])
    assert bpy.ops.export_scene.rmv2(filepath=str(GEO/filename),source='COLLECTION',skeleton_name=skel,auto_lods=False,apply_modifiers=True)=={'FINISHED'}

# VMD props use the animated bone transform, not the skinning deformation matrix.
for o in sword_lods:
    con=o.constraints.new('CHILD_OF');con.name='VMD weapon_2 preview';con.target=rig;con.subtarget='weapon_2';con.inverse_matrix=Matrix.Identity(4)

# Use embedded PNGs for Blender previews; exported game textures remain DDS.
import sys
sys.path.insert(0,str(R/'tools'))
from HuyenVePreview import prepare_preview
report['blender_preview']=prepare_preview(OUT)

# Test native clips; no new animation exports or edits to CA animations.
clips={'stand':'stand/hu1e_dlc24_yuan_bo_sword_stand_01.anim','run':'locomotion/hu1e_dlc24_yuan_bo_sword_run_02.anim','attack':'attack/hu1e_dlc24_yuan_bo_sword_attack_01.anim','cast':'spell_cast/hu1e_dlc24_yuan_bo_sword_spell_cast_long_01.anim'}
actions={}
for name,path in clips.items():
    activate_collection(root);select([rig]);assert bpy.ops.import_scene.tw_anim(filepath=str(REF/'animations/battle/humanoid01e/yuan_bo_human'/path))=={'FINISHED'}
    action=rig.animation_data.action;action.name='QA_'+name;action.use_fake_user=True;actions[name]=action
report['animations']={name:list(a.frame_range) for name,a in actions.items()}

scene.world=bpy.data.worlds.new('Huyen Ve QA World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power in [((-3,-4,5),550),((3,-2,2),350),((0,3,4),450)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=4;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(3,-5,2.6));cam=bpy.context.object;aim(cam,(0,0,1));cam.data.type='ORTHO';cam.data.ortho_scale=2.65;scene.camera=cam
scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.cycles.samples=16
scene.render.image_settings.file_format='PNG'
checks={}
for name,action in actions.items():
    rig.animation_data.action=action;start,end=map(int,action.frame_range);frame=(start+end)//2
    max_extent=0;max_edge_ratio=0
    for f in sorted({start,frame,end}):
        scene.frame_set(f);bpy.context.view_layer.update();de=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=de.to_mesh()
        positions=np.array([list(v.co) for v in mesh.vertices]);assert np.isfinite(positions).all();max_extent=max(max_extent,float(np.ptp(positions,axis=0).max()))
        for edge in body.data.edges:
            i,j=edge.vertices;rest=(body.data.vertices[i].co-body.data.vertices[j].co).length
            if rest>.004:max_edge_ratio=max(max_edge_ratio,float(np.linalg.norm(positions[i]-positions[j])/rest))
        de.to_mesh_clear()
    scene.frame_set(frame);bpy.context.view_layer.update()
    de=body.evaluated_get(bpy.context.evaluated_depsgraph_get());points=[de.matrix_world@Vector(p) for p in de.bound_box]
    se=sword.evaluated_get(bpy.context.evaluated_depsgraph_get());points += [se.matrix_world@Vector(p) for p in se.bound_box]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2
    cam.location=center+Vector((3,-5,2.2));aim(cam,center);cam.data.ortho_scale=max(hi-lo)*1.35
    scene.render.filepath=str(OUT/('qa_'+name+'.png'));bpy.ops.render.render(write_still=True)
    checks[name]={'sampled_frames':sorted({start,frame,end}),'max_axis_extent':max_extent,'max_edge_stretch_ratio':max_edge_ratio}
report['deformation_checks']=checks
rig.animation_data.action=actions['stand'];scene.frame_set(1)
select([body])
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'huyen-ve-rigged-prototype.blend'))
report['status']='built_needs_visual_review';report['bone_count']=len(rig.data.bones)
(OUT/'model-build-report.json').write_text(json.dumps(report,indent=2))
print('MODEL_BUILD_REPORT',json.dumps(report))
