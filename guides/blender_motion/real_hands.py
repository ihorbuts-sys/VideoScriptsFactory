"""Anatomical CC0 hand meshes by para / MakeHuman, with explicit contact landmarks."""
import bpy
import json
from pathlib import Path
from mathutils import Vector,Matrix
import assets as A
import geometry as G

LIBRARY=Path(__file__).resolve().parent/'vendor/para-fps-arms/hand-poses.blend'


def place(pose='point',side='R',target=(0,0,0),forward=(0,1,0),normal=(0,0,1),anchor='f_index.03',library=None):
    name=pose+'_'+side
    with bpy.data.libraries.load(str(library or LIBRARY),link=False) as (src,dst):dst.objects=[name]
    mesh=dst.objects[0];bpy.context.collection.objects.link(mesh)
    mesh.name='Anatomical '+pose+' hand '+side
    mesh.data.materials.clear();mesh.data.materials.append(G.MAT)
    A.tag(mesh,'support','Continuous anatomical CC0 hand mesh; wrist, palm and five fingers stay connected')
    landmarks=json.loads(mesh['landmarks'])
    local=(Vector(landmarks['f_index.03'])+Vector(landmarks['thumb.03']))/2 if anchor=='grip' else Vector(landmarks[anchor]) if anchor in landmarks else Vector((0,0,0))
    y=Vector(forward).normalized();z=Vector(normal);z=(z-y*z.dot(y)).normalized();x=y.cross(z)
    rotation=Matrix((x,y,z)).transposed()
    root=A.empty('Anatomical hand placement',Vector(target)-rotation@local);root.rotation_euler=rotation.to_euler()
    mesh.parent=root;mesh.location=(0,0,0);mesh.rotation_euler=(0,0,0)
    root['visible_hand_count']=1;root['hand_source']='para / MakeHuman CC0';root['contact_landmark']=anchor
    return root


def point_on_page(page,target=(.03,.18,.007)):
    import math
    hand=place(target=target,forward=(0,math.cos(math.radians(28)),-math.sin(math.radians(28))),
               normal=(0,-math.sin(math.radians(28)),-math.cos(math.radians(28))))
    hand.parent=page
    return hand


def fingertips(root):
    """World nail seats of a placed hand, thumb to little finger: (centre on the back of the tip, finger direction,
    back-of-hand direction). Read from the rig's last-joint vertex groups."""
    bpy.context.view_layer.update()
    mesh=next(c for c in root.children_recursive if c.type=='MESH')
    back=-(root.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    names={g.name:g.index for g in mesh.vertex_groups}
    seats=[]
    for finger in ['thumb','f_index','f_middle','f_ring','f_pinky']:
        def points(joint):
            for side in ('R','L'):
                index=names.get(f'{finger}.{joint}.{side}')
                if index is None:continue
                found=[mesh.matrix_world@v.co for v in mesh.data.vertices if any(g.group==index and g.weight>.5 for g in v.groups)]
                if found:return found
            return []
        tip,middle=points('03'),points('02')
        if not tip or not middle:continue
        base=sum(middle,Vector())/len(middle)
        end=max(tip,key=lambda p:(p-base).length)
        along=(end-base).normalized()
        top=max(p.dot(back) for p in tip)
        centre=end-along*.007
        centre+=back*(top-centre.dot(back))
        seats.append((centre,along,back))
    return seats


RIG=LIBRARY.parent/'FPS ARMS RIG 1.blend'
FINGERS=('index','middle','ring','pinky')
# Flexion limits in degrees per joint (MCP, PIP, DIP; thumb CMC-MCP-IP), common adult active ranges.
FINGER_LIMIT=(90,105,80)
THUMB_LIMIT=(60,60,80)


def wrap(side,origin,radial,up,clearance,wrist=(30,10),thumb_lift=.35,contact=.095,gap=.001,forearm=.12,pivot='bone',fade=0.,thenar=(0.,.35,.035)):
    """Cylindrical power grasp (palm opposition, thumb abducted) posed from the original CC0 rig around a convex
    object whose surface `clearance(points)` measures (signed metres, negative inside). The palm lies against the
    object on the `radial` side of `origin` with the thumb toward `up`; every phalanx closes until it touches the
    surface, so the grip has real contact and no penetration. `wrist` is (extension, ulnar deviation) in degrees,
    turned about the hand bone head (`pivot='bone'`) or about the forearm's axis at the wrist (`pivot='axis'`, no step
    between hand and forearm). `fade` moves the line-art fade centre that many metres from the grip toward the wrist,
    so the wrist and the start of the forearm stay drawn. `thenar` (bulge, place along the thumb metacarpal, radius in
    metres) restores the thenar pad the swung metacarpal leaves hollow on this low-poly mesh. Returns a placement root
    like `place`."""
    import math,bmesh
    import numpy as np
    with bpy.data.libraries.load(str(RIG),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('caucasian')]
    for obj in dst.objects:bpy.context.collection.objects.link(obj)
    arm=next(o for o in dst.objects if o.type=='ARMATURE');body=next(o for o in dst.objects if o.type=='MESH')
    arm.animation_data_clear();body.animation_data_clear()
    for bone in arm.pose.bones:
        for con in list(bone.constraints):bone.constraints.remove(con)
        bone.rotation_mode='XYZ';bone.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    s=side;W=arm.matrix_world;Wi=W.inverted();W3=W.to_3x3()
    def head(name):return W@arm.data.bones[name+'.'+s].head_local
    wrist_point=head('hand');tip=W@arm.data.bones['f_middle.03.'+s].tail_local
    forward=(tip-wrist_point).normalized();across=(head('f_index.01')-head('f_pinky.01')).normalized()
    across=(across-forward*across.dot(forward)).normalized();normal=across.cross(forward).normalized()
    scale=.19/(tip-wrist_point).length
    # The palm side is where a flexed finger goes (the mesh is mirrored between arms).
    probe=arm.pose.bones['f_middle.01.'+s];probe.rotation_euler.x=math.radians(30);bpy.context.view_layer.update()
    palm=normal if (W@arm.pose.bones['f_middle.03.'+s].tail-tip).dot(normal)>0 else -normal
    probe.rotation_euler.x=0;bpy.context.view_layer.update()
    def rotate(name,matrix,pivot):
        bone=arm.pose.bones[name+'.'+s];pivot_arm=Wi@pivot
        rot=(Wi.to_3x3()@matrix@W3).to_4x4()
        bone.matrix=Matrix.Translation(pivot_arm)@rot@Matrix.Translation(-pivot_arm)@bone.matrix
        bpy.context.view_layer.update()
    ext,dev=wrist
    joint=wrist_point
    if pivot=='axis':
        # The rig's hand bone head sits about 6 mm off the forearm's axis; turning about it shifts the hand along its
        # own axis. The axis is the line through the rest skin's cross-section centres 1-4 cm up the forearm.
        elbow=head('forearm');along=(elbow-wrist_point).normalized()
        groups={g.name:g.index for g in body.vertex_groups};hand_ids={groups[n+'.'+s] for n in ['hand','palm_index','palm_middle','palm_ring','palm_pinky'] if n+'.'+s in groups}
        rest=[body.matrix_world@v.co for v in body.data.vertices if (body.matrix_world@v.co).x*wrist_point.x>0 and not any(g.group in hand_ids and g.weight>.5 for g in v.groups)]
        rows=[]
        for k in range(6):
            lo,hi=(.01+k*.005)/scale,(.015+k*.005)/scale
            ring=[p for p in rest if lo<=(p-wrist_point).dot(along)<hi]
            if len(ring)>5:rows.append(((lo+hi)/2,sum(ring,Vector())/len(ring)))
        t=np.array([r[0] for r in rows]);c=np.array([tuple(r[1]) for r in rows])
        slope,intercept=np.polyfit(t,c,1)
        joint=Vector(intercept)
    rotate('hand',Matrix.Rotation(math.radians(dev),3,forward.cross(-across))@Matrix.Rotation(math.radians(ext),3,forward.cross(-palm)),joint)
    hand_rot=W3@arm.pose.bones['hand.'+s].matrix.to_3x3()@arm.data.bones['hand.'+s].matrix_local.to_3x3().inverted()@W3.inverted()
    # Hand-local frame of the posed hand: x radial (thumb side), y toward the fingers, z the palm-side normal.
    basis=Matrix((hand_rot@across,hand_rot@forward,hand_rot@normal))
    up=Vector(up).normalized();radial=Vector(radial).normalized();radial=(radial-up*radial.dot(up)).normalized()
    z_world=-radial if palm.dot(normal)>0 else radial
    rotation=Matrix((up,z_world.cross(up),z_world)).transposed()
    origin=Vector(origin);placement=[origin+radial*.06]
    palm_local=Vector((-.004,contact,0))
    def world(points):
        local=(np.array(basis)@(points-np.array(wrist_point)).T).T*scale
        return (np.array(rotation)@(local-np.array(palm_local)).T).T+np.array(placement[0])
    groups={g.name:g.index for g in body.vertex_groups}
    def members(names):
        ids={groups[n+'.'+s] for n in names}
        return np.array([v.index for v in body.data.vertices if any(g.group in ids and g.weight>.5 for g in v.groups)])
    def skin():
        deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);mesh=ev.to_mesh()
        co=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',co);ev.to_mesh_clear()
        co=co.reshape(-1,3);return (np.array(body.matrix_world)@np.c_[co,np.ones(len(co))].T).T[:,:3]
    def least(index):return float(clearance(world(skin()[index])).min())
    # Seat the palm on the surface.
    palm_ids=members(['hand','palm_index','palm_middle','palm_ring','palm_pinky'])
    for _ in range(3):placement[0]=placement[0]-radial*(least(palm_ids)-gap)
    def close(names,axis,limit,index,coupling=.8):
        """Largest flexion (degrees) of the first joint of `names`, the later joints following at `coupling`, at
        which the skin `index` stays outside the surface, by bisection (a link stops at its first contact)."""
        bones=[arm.pose.bones[n+'.'+s] for n in names];starts=[b.matrix_basis.copy() for b in bones]
        def at(angle):
            for bone,start in zip(bones,starts):bone.matrix_basis=start
            bpy.context.view_layer.update()
            for k,(n,bone) in enumerate(zip(names,bones)):
                rotate(n,Matrix.Rotation(math.radians(angle*(coupling if k else 1)),3,axis(n)),W@bone.head)
            return least(index)
        low,high=-15.,float(limit)
        if at(high)>=gap:return high
        if at(low)<gap:at(low);return low
        for _ in range(9):
            mid=(low+high)/2
            if at(mid)>=gap:low=mid
            else:high=mid
        at(low);return low
    angles={}
    curl=lambda n:(W3@arm.pose.bones[n+'.'+s].matrix.to_3x3().col[0]).normalized()
    for finger in FINGERS:
        chain=[f'f_{finger}.{k:02d}' for k in (1,2,3)]
        for j,limit in enumerate(FINGER_LIMIT):angles[chain[j]]=close(chain[j:],curl,limit,members(chain[j:]))
    # Thumb: swing the metacarpal around the object opposite the fingers, lifted toward the radial side, then close
    # its joints about the object's axis the same way.
    thumb=arm.pose.bones['thumb.01.'+s]
    base=W@thumb.head;target=hand_rot@(across*thumb_lift+palm-forward*.35)
    rotate('thumb.01',(W3@thumb.matrix.to_3x3().col[1]).normalized().rotation_difference(target.normalized()).to_matrix(),base)
    hinge=lambda n:-(hand_rot@across) if palm.dot(normal)>0 else hand_rot@across
    chain=['thumb.01','thumb.02','thumb.03']
    for j,limit in enumerate(THUMB_LIMIT):angles[chain[j]]=close(chain[j:],hinge,limit,members(chain[j:]))
    # Bake the posed arm, keep this side and crop the forearm.
    points=skin()
    deps=bpy.context.evaluated_depsgraph_get();data=bpy.data.meshes.new_from_object(body.evaluated_get(deps))
    bm=bmesh.new();bm.from_mesh(data);bm.verts.ensure_lookup_table()
    for v in bm.verts:v.co=Vector(points[v.index])
    bulge,place,radius=thenar
    if bulge:
        # Linear blend skinning stretches the palm-facing skin between the swung metacarpal and the heel of the hand into
        # a hollow; push it out along its normals with a smooth falloff, then relax the patch into one rounded pad.
        out=(hand_rot@palm).normalized();bone=arm.pose.bones['thumb.01.'+s]
        centre=W@bone.head+(W@bone.tail-W@bone.head)*place+out*(radius*.4/scale)
        bm.normal_update()
        def smooth(x):x=min(max(x,0.),1.);return x*x*(3-2*x)
        falloff={v:smooth(1-(v.co-centre).length*scale/radius)*smooth(v.normal.dot(out)+.3) for v in bm.verts}
        patch=[v for v,f in falloff.items() if f>0]
        for v in patch:v.co+=v.normal*(bulge/scale)*falloff[v]
        for _ in range(3):
            moved={v:sum((e.other_vert(v).co for e in v.link_edges),Vector())/len(v.link_edges) for v in patch if v.link_edges}
            for v,mean in moved.items():v.co=v.co.lerp(mean,.5*falloff[v])
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x*wrist_point.x<0],context='VERTS')
    elbow=head('forearm');direction=(elbow-wrist_point).normalized()
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=wrist_point+direction*(forearm/scale),plane_no=direction,clear_outer=True,dist=1e-5)
    local=lambda p:basis@(p-wrist_point)*scale-palm_local
    for v in bm.verts:v.co=local(v.co)
    # Skin that the joint closure left a fraction of a millimetre inside (blended joint weights) rests on the surface.
    R=np.array(rotation);at=np.array(placement[0]);co=np.array([tuple(v.co) for v in bm.verts]);P=co@R.T+at
    depth=clearance(P);inside=depth<0;root_depth=float(-depth.min()) if inside.any() else 0.
    for _ in range(4):
        if not inside.any():break
        Q=P[inside];step=1e-4;d0=clearance(Q)
        grad=np.stack([(clearance(Q+np.eye(3)[k]*step)-d0)/step for k in range(3)],axis=1)
        grad/=np.maximum(np.linalg.norm(grad,axis=1,keepdims=True),1e-9)
        P[inside]=Q+grad*(gap-d0)[:,None];depth=clearance(P);inside=depth<0
    for v,p in zip(bm.verts,(P-at)@R):v.co=Vector(p)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    landmarks={n:list(local(W@arm.pose.bones[n+'.'+s].tail)) for n in ['hand','f_index.03','f_middle.03','thumb.03']}
    if fade:
        grip=(Vector(landmarks['f_index.03'])+Vector(landmarks['thumb.03']))/2
        landmarks['fade']=list(grip+(local(wrist_point)-grip).normalized()*fade)
    for obj in (body,arm):bpy.data.objects.remove(obj,do_unlink=True)
    data.materials.clear();data.materials.append(G.MAT)
    for p in data.polygons:p.use_smooth=True
    mesh=bpy.data.objects.new('Anatomical wrap hand '+s,data);bpy.context.collection.objects.link(mesh)
    mesh.modifiers.new('Smooth anatomical hand surface','SUBSURF').levels=1
    mesh['landmarks']=json.dumps(landmarks);mesh['source']='OpenGameArt: para, FPS arms; MakeHuman-based mesh';mesh['license']='CC0-1.0'
    A.tag(mesh,'support','Continuous anatomical CC0 hand closed around the object')
    root=A.empty('Anatomical hand placement',placement[0]);root.rotation_euler=rotation.to_euler()
    mesh.parent=root
    root['visible_hand_count']=1;root['hand_source']='para / MakeHuman CC0';root['contact_landmark']='fade' if fade else 'grip'
    root['wrap_angles']=json.dumps({k:round(v,1) for k,v in angles.items()});root['wrap_skin_settled_mm']=round(root_depth*1000,2)
    return root
