"""Generate authored hand topology on native finger landmarks; no donor mesh copy."""
import math,bmesh,bpy
import numpy as np
from mathutils import Vector

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)

def rebuild_hands(body,rig,output):
    image=bpy.data.images.load(str(output/'texture-intermediate/mc_huyen_ve_body_base_colour.png'),check_existing=True)
    w,h=image.size;pixels=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(h,w,4)
    bm=bmesh.new();bm.from_mesh(body.data);uv=bm.loops.layers.uv.active
    layer=bm.verts.layers.int.new('authored_hand_skin_id');weights_by_id={};serial=0;report={};skin_samples=[]
    for f in bm.faces:
        p=f.calc_center_median()
        if abs(p.x)<.30 or p.z>.98 or p.z<.66:continue
        coord=sum((loop[uv].uv for loop in f.loops),Vector((0,0)))/len(f.loops)
        rgb=pixels[min(h-1,max(0,int(coord.y*h))),min(w-1,max(0,int(coord.x*w))),:3]
        if rgb[0]>rgb[1]*1.08 and rgb[1]>rgb[2]*1.05 and rgb[0]>.15:skin_samples.append((coord.copy(),rgb.copy()))
    if not skin_samples:raise RuntimeError('No authored skin texture samples')
    median=np.median([rgb for _,rgb in skin_samples],axis=0)
    skin_uv=min(skin_samples,key=lambda pair:float(np.linalg.norm(pair[1]-median)))[0]
    def vertex(p,weights):
        nonlocal serial
        v=bm.verts.new(p);serial+=1;v[layer]=serial;weights_by_id[serial]=weights;return v
    def face(vs):
        f=bm.faces.new(vs);f.smooth=True
        for loop in f.loops:loop[uv].uv=skin_uv
        return f
    def rings(centers,radii,lateral,normal,weights,segments=10):
        rows=[]
        for c,(r1,r2),skin in zip(centers,radii,weights):
            row=[vertex(c+lateral*(r1*math.cos(2*math.pi*j/segments))+normal*(r2*math.sin(2*math.pi*j/segments)),skin) for j in range(segments)]
            if rows:
                for j in range(segments):face([rows[-1][j],rows[-1][(j+1)%segments],row[(j+1)%segments],row[j]])
            rows.append(row)
        first=vertex(centers[0],weights[0]);last=vertex(centers[-1],weights[-1])
        for j in range(segments):face([first,rows[0][(j+1)%segments],rows[0][j]]);face([last,rows[-1][j],rows[-1][(j+1)%segments]])
    for side,sign in [('left',1),('right',-1)]:
        hand=rig.pose.bones['hand_'+side];inv=hand.matrix.inverted();boundary=[]
        remove=[v for v in bm.verts if v.co.x*sign>.295 and .64<v.co.z<.935 and -.155<v.co.y<.08 and v[layer]==0]
        selected=set(remove)
        for edge in bm.edges:
            if sum(v in selected for v in edge.verts)==1:boundary += [v.co.copy() for v in edge.verts if v not in selected]
        wrist=hand.head.copy();forearm=(wrist-rig.pose.bones['lowerarm_'+side].head).normalized()
        cuff=wrist-forearm*.035
        upper_boundary=[p for p in boundary if p.z>.925]
        source_cuff=sum(upper_boundary,Vector())/len(upper_boundary) if upper_boundary else cuff
        delta=cuff-source_cuff
        # Fit the distal gauntlet to the wrist too; a floating source cuff
        # cannot be repaired by stretching a skin tube across the gap.
        for v in bm.verts:
            p=v.co
            if v not in selected and v[layer]==0 and p.x*sign>.27 and .925<p.z<1.23:
                p+=delta*smooth(1.20,.945,p.z)
        removed_count=len(remove);bmesh.ops.delete(bm,geom=remove,context='VERTS')
        isolated=[v for v in bm.verts if not v.link_faces]
        if isolated:bmesh.ops.delete(bm,geom=isolated,context='VERTS')
        index=rig.pose.bones['finger_index_'+side+'_0'].head.copy();ring=rig.pose.bones['finger_ring_'+side+'_0'].head.copy()
        knuckles=(index+ring)*.5;direction=(knuckles-wrist).normalized();lateral=(index-ring).normalized();normal=direction.cross(lateral).normalized();lateral=normal.cross(direction).normalized()
        palm_length=(knuckles-wrist).length;center=(wrist+knuckles)*.5
        centers=[];radii=[]
        for t in [-1,-.90,-.65,-.25,.25,.65,.90,1]:
            cross=math.sqrt(max(.006,1-t*t));centers.append(center+direction*(palm_length*.59*t));radii.append((.039*cross,.018*cross))
        rings(centers,radii,lateral,normal,[{'hand_'+side:1}]*len(centers),12)
        rings([cuff-forearm*.018,cuff,wrist+direction*.020,wrist+direction*.045],[(.026,.018),(.026,.018),(.029,.018),(.034,.018)],lateral,normal,[{'lowerarm_'+side:1},{'lowerarm_'+side:1},{'hand_'+side:1},{'hand_'+side:1}],12)
        for family,offset,radius in [('finger_index',.009,.0085),('finger_index',-.011,.009),('finger_ring',.006,.0085),('finger_ring',-.013,.0075),('thumb',0,.0105)]:
            names=[family+'_'+side+'_'+str(i) for i in range(3)];bones=[rig.pose.bones[n] for n in names]
            points=[b.head.copy()+lateral*offset for b in bones]+[bones[-1].tail.copy()+lateral*offset]
            centers=[];radii=[];skins=[]
            for k in range(3):
                for t in ([0,.28,.72] if k<2 else [0,.32,.70,1]):
                    centers.append(points[k].lerp(points[k+1],t));r=radius*(1-.12*k)*(1-.38*t if k==2 else 1)
                    radii.append((r,r*.90))
                    if t==0:
                        previous=names[k-1] if k else 'hand_'+side;skins.append({previous:.45,names[k]:.55})
                    else:skins.append({names[k]:1})
            rows=[];segments=10
            for i,(c,rad,skin) in enumerate(zip(centers,radii,skins)):
                tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
                u=(lateral-tangent*lateral.dot(tangent)).normalized();v=tangent.cross(u).normalized()
                row=[vertex(c+u*(rad[0]*math.cos(2*math.pi*j/segments))+v*(rad[1]*math.sin(2*math.pi*j/segments)),skin) for j in range(segments)]
                if rows:
                    for j in range(segments):face([rows[-1][j],rows[-1][(j+1)%segments],row[(j+1)%segments],row[j]])
                rows.append(row)
            tip=vertex(centers[-1]+(points[-1]-points[-2]).normalized()*.003,skins[-1])
            base=vertex(centers[0]-(points[1]-points[0]).normalized()*.003,skins[0])
            for j in range(segments):face([tip,rows[-1][j],rows[-1][(j+1)%segments]]);face([base,rows[0][(j+1)%segments],rows[0][j]])
        report[side]={'removed_vertices':removed_count,'cuff_center':list(cuff),'gauntlet_fit_delta':list(delta),'replacement':'authored palm, wrist bridge, four articulated fingers and thumb'}
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free();body.data.update()
    attr=body.data.attributes['authored_hand_skin_id'];overrides={i:weights_by_id[a.value] for i,a in enumerate(attr.data) if a.value}
    report['authored_vertices']=len(overrides);report['skin_uv']=list(skin_uv)
    return report,overrides

def finger_preservation(position,rig):
    return 0
