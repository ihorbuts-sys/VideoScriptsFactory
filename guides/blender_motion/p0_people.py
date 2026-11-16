"""Canonical creator performances, with separate selfie and friend-held cameras.

No new person geometry, detached hands or facial performance is synthesized.
The face-region mask measures real source geometry, independently of hair/shoulders.
"""
import math,sys,json
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector,Quaternion,Matrix

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model_refferences/objects/tools'))
from prepare_rigged_characters import named
from coffee_scene_details import orient_bone
from build_creator_guides import ArmPose

BASE_IDS={'bite_selfie_eye','sip_selfie_eye','sip_high_lean','verdict_eye_level','verdict_high_plate'}
FRIEND_IDS={'bite_friend_three_quarter','sip_friend_side','verdict_friend_eye'}
IDS=BASE_IDS|FRIEND_IDS
CUP_SCALE=1.10
CUP_FACE_GAP=.006


def world_points(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    points=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',points)
    m=np.array(evaluated.matrix_world);points=points.reshape(-1,3)@m[:3,:3].T+m[:3,3]
    evaluated.to_mesh_clear();return points


def forearm_forward(arm,solver,wrist,pole):
    shoulder=arm.matrix_world@solver.upper.head;delta=wrist-shoulder;distance=delta.length
    direction=delta.normalized();along=(solver.a**2-solver.b**2+distance**2)/(2*distance)
    height=math.sqrt(max(0,solver.a**2-along**2));pole=Vector(pole)
    pole=(pole-direction*pole.dot(direction)).normalized()
    elbow=shoulder+direction*along+pole*height
    return (wrist-elbow).normalized()


def distribute_palm_roll(arm,solver):
    """Put axial hand rotation into shoulder/forearm, preserving the IK joints."""
    upper,fore,hand=solver.upper,solver.fore,solver.hand
    upper_world=(arm.matrix_world@upper.matrix).copy()
    fore_world=(arm.matrix_world@fore.matrix).copy()
    hand_world=(arm.matrix_world@hand.matrix).copy()
    axis=(arm.matrix_world.to_3x3()@(fore.tail-fore.head)).normalized()
    # Transport the anatomical index-to-pinky direction with the forearm.
    rest_fore=(arm.matrix_world@fore.bone.matrix_local).to_3x3()
    neutral=fore_world.to_3x3()@rest_fore.inverted()@solver.frame.col[1]
    across=hand_world.to_3x3()@solver.rest.to_3x3().inverted()@solver.frame.col[1]
    neutral=(neutral-axis*neutral.dot(axis)).normalized()
    across=(across-axis*across.dot(axis)).normalized()
    angle=math.atan2(axis.dot(neutral.cross(across)),neutral.dot(across))
    upper_axis=(arm.matrix_world.to_3x3()@(upper.tail-upper.head)).normalized()
    for bone,world,direction,fraction in [(upper,upper_world,upper_axis,.35),(fore,fore_world,axis,.85)]:
        rotated=Quaternion(direction,angle*fraction).to_matrix().to_4x4()@world
        rotated.translation=world.translation;bone.matrix=arm.matrix_world.inverted()@rotated
        bpy.context.view_layer.update()
    hand.matrix=arm.matrix_world.inverted()@hand_world
    bpy.context.view_layer.update()
    return math.degrees(angle)


def grip_digits(arm,solver,kind):
    """Pose flexion into the measured left palm; thumb opposes above the grip."""
    wrist=arm.matrix_world@solver.hand.head
    index=arm.matrix_world@named(arm,'LeftHandIndex1').head
    pinky=arm.matrix_world@named(arm,'LeftHandPinky1').head
    forward=((index+pinky)/2-wrist).normalized()
    radial=(index-pinky).normalized();radial=(radial-forward*radial.dot(forward)).normalized()
    palm=forward.cross(radial).normalized()
    angles={'Index':(30,80,125),'Middle':(35,85,125),'Ring':(40,95,135),'Pinky':(40,95,135)}
    if kind=='cup':angles.update(Index=(35,75,100),Middle=(45,85,115),Ring=(30,50,65),Pinky=(35,55,70))
    if kind=='fork':angles.update(Index=(25,65,105),Middle=(35,80,115))
    for finger,flexion in angles.items():
        for joint,degrees in enumerate(flexion,1):
            theta=math.radians(degrees)
            orient_bone(arm,named(arm,'LeftHand'+finger+str(joint)),forward*math.cos(theta)+palm*math.sin(theta))
    # Opposition is a separate thumb motion, not another identical finger curl.
    # On a cup the thumb rides above the hooked index, so its outer joints lean to the radial side.
    lift=(.30,.15) if kind=='cup' else (.12,-.10)
    for joint,direction in enumerate([forward*.65+radial*.75+palm*.20,
                                      forward*.90+radial*lift[0]+palm*.30,
                                      forward*.90+radial*lift[1]+palm*.25],1):
        orient_bone(arm,named(arm,'LeftHandThumb'+str(joint)),direction)
    thumb_tip=arm.matrix_world@named(arm,'LeftHandThumb3').tail
    index_pad=arm.matrix_world@named(arm,'LeftHandIndex2').tail
    return (thumb_tip+index_pad)/2


def load_creator(P):
    path=ROOT/'model_refferences/creator/lineart/asset.blend'
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=[src.collections[0]]
    col=dst.collections[0];bpy.context.scene.collection.children.link(col)
    bpy.ops.object.select_all(action='DESELECT')
    root=next(o for o in col.objects if o.get('p0_character')=='creator')
    arm=next(o for o in root.children_recursive if o.type=='ARMATURE')
    for o in [root,*root.children_recursive]:o.animation_data_clear()
    for b in arm.pose.bones:b.matrix_basis.identity()
    P.role(root,'character')
    bpy.context.view_layer.update()
    # Face only: real source triangles around the eyes, nose, lips and chin.
    # Hair and shoulders may sit above/below the protected face zone.
    masks=[]
    for obj in list(P.members(root)):
        copy=obj.copy();copy.data=obj.data.copy();col.objects.link(copy)
        mesh=bmesh.new();mesh.from_mesh(copy.data)
        discard=[]
        for v in mesh.verts:
            p=obj.matrix_world@v.co
            if not (1.385<p.z<1.615 and abs(p.x)<.145 and p.y<-.045):discard.append(v)
        bmesh.ops.delete(mesh,geom=discard,context='VERTS');mesh.to_mesh(copy.data);mesh.free()
        if not len(copy.data.polygons):bpy.data.objects.remove(copy,do_unlink=True);continue
        copy.name='Face safety mask / '+obj.name
        copy['p0_framing_mask']=True;copy['composition_role']='framing_mask'
        copy.lineart.usage='EXCLUDE';copy.hide_render=True;masks.append(copy)
    assert masks,'Creator has no measurable face geometry'
    return root,arm,masks


def build(gid,record,P):
    A,G,V=P.A,P.G,P.V;scene=bpy.context.scene
    root,arm,face=load_creator(P)
    state=dict(hero=face,actions=[],contacts=[],adaptations=[],camera_height_support=0.,hand_count=2,
        silhouettes=0,detailed_people=1,framing_masks=face,character_root=root,
        preview_mirrored=record['camera']=='front',lens_mm=18 if record['camera']=='front' else 24,
        performance_checks=[],light_position=(-.8,-.7,2.0))
    friend=record['camera']=='back';bite=gid.startswith('bite_');sip=gid.startswith('sip_')
    high=gid in {'sip_high_lean','verdict_high_plate'}
    head=named(arm,'Head');neck=named(arm,'Neck');chest=named(arm,'Spine2')
    bases={b.name:(arm.matrix_world@b.matrix).to_3x3().copy() for b in [head,neck,chest]}
    face_mask=next(o for o in face if not o.get('p0_face_feature'))
    lip_points=world_points(face_mask)
    lip_points=lip_points[(np.abs(lip_points[:,0])<.022)&(lip_points[:,2]>1.412)&(lip_points[:,2]<1.435)]
    lip_y=float(lip_points[:,1].min())
    mouth_local=(arm.matrix_world@head.matrix).inverted()@Vector((.0,lip_y,1.425))
    rest={b.name:b.matrix_basis.copy() for b in arm.pose.bones}
    left=ArmPose(arm,'Left');right=ArmPose(arm,'Right')
    # Table beside the standing creator: a believable visitor-side support,
    # kept away from the torso rather than clipping through the body.
    table_pos=(.73,.24,0) if gid=='verdict_high_plate' else (-.55,-.04,0) if gid=='sip_friend_side' else (.52,-.25,0)
    table=A.table(table_pos,.34 if gid in {'verdict_high_plate','sip_friend_side'} else .38);P.role(table,'background')
    table_z=.785
    if gid=='verdict_high_plate':
        table.location.z=.31;table_z+=.31;table['p0_verdict_table']=True
    if gid=='sip_friend_side':
        table.location.z=.315;table_z+=.315;table['p0_sip_support_table']=True
    if bite or gid=='verdict_high_plate':
        dish=A.pasta((.62,.18,table_z) if gid=='verdict_high_plate' else (.43,-.33,table_z));P.role(dish,'support')
        if gid=='verdict_high_plate':dish['p0_verdict_dish']=True
    elif sip:
        saucer=A.saucer((-.61,-.21,table_z) if gid=='sip_friend_side' else (.43,-.33,table_z))
        if gid=='sip_friend_side':saucer['p0_empty_sip_saucer']=True
    else:
        d,s=P.cup(.43,-.33,.785,False);P.role(d,'support');P.role(s,'support')
    V.window((-.85,1.75,1.5));V.pendant((.75,1.4,2.3))
    P.role(V.plant((-.73,1.30,0),height=1.1),'background')
    # Friend shots use an accessible rear-camera distance, not arm-length zoom.
    if friend:
        pos=Vector((-.57,-.92,1.54)) if gid!='sip_friend_side' else Vector((-.78,-.72,1.53))
        target=Vector((.0,-.02,1.45))
    elif high:
        pos=Vector((.13,-.80,1.76)) if gid=='verdict_high_plate' else Vector((-.13,-.50,1.73))
        target=Vector((.20,.03,1.32)) if gid=='verdict_high_plate' else Vector((.025,-.02,1.46))
    else:
        pos=Vector((-.10,-.50,1.54));target=Vector((.0,-.02,1.465))
    state.update(target_position=pos,target_aim=target)
    def sample(u,p,t):
        # A friend's small curved approach is a useful angle demonstration.
        # Selfie examples keep the phone planted; the person performs the action.
        if friend:
            s=P.smooth(u);delta=Vector((.07*(1-s),-.035*(1-s),.025*(1-s)))
            return p+delta,t
        return p,t
    state['sample']=sample
    prop=None;prop_start=None
    if sip:
        prop,saucer=P.cup(.11,-.20,1.18,False)
        for o in [saucer,*saucer.children_recursive]:bpy.data.objects.remove(o,do_unlink=True)
        prop.scale=(CUP_SCALE,)*3;prop_start=prop.location.copy();P.role(prop,'support')
        prop['p0_held_cup']=True
        prop['p0_grip_style']='cup_handle_thumb_above'
        bpy.context.view_layer.update();inverse=np.array(prop.matrix_world.inverted());cloud=[]
        for obj in P.members(prop):
            points=world_points(obj);cloud.append(points@inverse[:3,:3].T+inverse[:3,3])
        cup_local_points=np.concatenate(cloud)
        prop['p0_face_gap_m']=CUP_FACE_GAP
    elif bite:
        prop=A.fork((.15,-.22,1.22),role='support')
        prop.rotation_euler.x=math.pi/2;prop_start=prop.location.copy()
        for n in range(3):
            food=A.tag(G.tube('Small pasta forkful',[(.005*math.sin(k*.7+n),.057+.009*math.cos(k*.7+n),.006+n*.002+.006*math.sin(k*.4)) for k in range(20)],.0015),'support','Small real forkful; stops beside lips')
            food.parent=prop
        prop['p0_held_fork']=True
        prop['p0_grip_style']='fork_tripod_side_lift'
    # Anatomical reach solve with original skinning; the source fingers start in
    # a relaxed curl. Props attach to the resulting grip, never float independently.
    previous_final_rotations={}
    if gid=='sip_friend_side':
        rest_surface=table_z
        # The wrist rests just inside the table's near edge, closest to her.
        right_rest=Vector((-.225,-.10,rest_surface+.025))
        root['p0_supported_right_hand']=True
        state['supported_hand_region']=[-.225,-.01,rest_surface+.025]
    def action(u):
        for b in arm.pose.bones:b.matrix_basis=rest[b.name].copy()
        phase=P.smooth((u-.12)/.35)*(1-P.smooth((u-.72)/.22))
        nod=math.sin(math.pi*P.smooth((u-.62)/.3))**2
        yaw=(math.radians(-28 if friend else -5))
        pitch_base=-12 if high else -2
        for b,pitch,turn in [(head,(pitch_base+2*nod)*.7,yaw*.7),(neck,(pitch_base+2*nod)*.3,yaw*.3),(chest,.25*math.sin(u*math.tau),0)]:
            b.rotation_mode='QUATERNION'
            ax=(bases[b.name].inverted()@Vector((1,0,0))).normalized()
            az=(bases[b.name].inverted()@Vector((0,0,1))).normalized()
            b.rotation_quaternion=Quaternion(az,turn)@Quaternion(ax,math.radians(pitch))
        bpy.context.view_layer.update()
        checks=[]
        if prop:
            # Lift first, then settle; the reverse path returns to the start.
            # The cup hides the static mouth during the sip. No lip-sync claim.
            # The friend-filmed bite rests the fork hand low, so its wrist stays in the fade below the chest.
            rest_z=1.05 if gid=='bite_friend_three_quarter' else 1.16
            wrist=Vector((.22,-.19,rest_z)).lerp(Vector((.13,-.19,1.385 if sip else 1.29)),phase)
            if bite:
                forward=Vector((-.72,-.15,.68)).normalized();across=Vector((0,0,1))
                if gid=='bite_friend_three_quarter':
                    # The low resting hand lies flatter and turns up into the bite angle as it rises.
                    forward=Vector((-.85,-.30,.25)).normalized().lerp(forward,phase).normalized()
            else:
                forward=Vector((-.94,0,.34)).normalized();across=Vector((0,0,1))
            mouth=arm.matrix_world@head.matrix@mouth_local
            goal=(Vector((-.02,-.18,1.30)) if sip else Vector((.04,-.12,rest_z+.18))).lerp(
                mouth+Vector((0,-.033,-.008)) if sip else mouth+Vector((.025,-.065,.003)),phase)
            point_local=Vector((0,0,.118)) if sip else Vector((0,.062,.01))
            if sip:
                prop.rotation_euler=(math.radians(-5)*phase,0,0)
                rotation=np.array(prop.rotation_euler.to_matrix())
                offsets=(cup_local_points*CUP_SCALE-np.array(point_local)*CUP_SCALE)@rotation.T
                face_cloud=world_points(face_mask)
                near=face_cloud[(face_cloud[:,0]>goal.x+offsets[:,0].min()-.003)&
                    (face_cloud[:,0]<goal.x+offsets[:,0].max()+.003)&
                    (face_cloud[:,2]>mouth.z-.08)&(face_cloud[:,2]<mouth.z+.005)]
                assert len(near),'No face surface found for cup clearance'
                goal.y=float(near[:,1].min()-CUP_FACE_GAP-offsets[:,1].max())
            for iteration in range(32 if sip else 8):
                for bone in [left.upper,left.fore,left.hand]:bone.matrix_basis=rest[bone.name].copy()
                bpy.context.view_layer.update()
                pole=Vector((.6,0,-1)) if sip else -forward
                actual_forward=forearm_forward(arm,left,wrist,pole) if sip else forward
                check=left.pose(wrist,actual_forward,across,1,scene.frame_current,pole=pole)
                check['distributed_palm_roll_degrees']=distribute_palm_roll(arm,left)
                contact=grip_digits(arm,left,'cup' if sip else 'fork')
                if sip:
                    local_contact=Vector((.081,.003,.096))*CUP_SCALE
                    prop.location=contact-prop.rotation_euler.to_matrix()@local_contact
                else:
                    prop.rotation_euler=Vector((-.65,.55,.52)).to_track_quat('Y','Z').to_euler()
                    prop.location=contact-prop.rotation_euler.to_matrix()@Vector((0,.005,0))
                bpy.context.view_layer.update()
                error=goal-prop.matrix_world@point_local
                if error.length<.0005:break
                step=error*(.65 if sip else 1)
                if step.length>.04:step=step.normalized()*.04
                wrist+=step
            assert error.length<.003,('Prop did not reach its face-relative target',gid,error.length)
            check.update(prop_target_error_m=error.length,prop_contact=list(contact),face_reference=list(mouth))
            checks.append(check)
        else:
            gesture=P.smooth((u-.10)/.32)*(1-P.smooth((u-.64)/.30))
            wrist=left.rest.translation.lerp(Vector((.22,-.16,1.12)),gesture)
            check=left.pose(wrist,Vector((0,0,1)),Vector((-1,0,0)),gesture,scene.frame_current)
            check['distributed_palm_roll_degrees']=distribute_palm_roll(arm,left)
            checks.append(check)
        if gid=='sip_friend_side':
            # The forearm rests on the table's near edge and the hand hangs over it, 60 degrees below level with the
            # palm upright; the solver's relaxed open palm gives the slight finger curl.
            along=forearm_forward(arm,right,right_rest,Vector((-.9,0,-.6)))
            level=Vector((along.x,along.y,0)).normalized()
            forward_right=(level*math.cos(math.radians(60))-Vector((0,0,1))*math.sin(math.radians(60))).normalized()
            check=right.pose(right_rest,forward_right,Vector((0,0,1)).cross(level),1,scene.frame_current,pole=Vector((-.9,0,-.6)))
            # A hanging hand relaxes: each finger curls a little more at every joint toward the palm.
            wrist=arm.matrix_world@right.hand.head
            index=arm.matrix_world@named(arm,'RightHandIndex1').head;pinky=arm.matrix_world@named(arm,'RightHandPinky1').head
            hand_forward=((index+pinky)/2-wrist).normalized()
            radial=(index-pinky).normalized();radial=(radial-hand_forward*radial.dot(hand_forward)).normalized()
            palm=radial.cross(hand_forward).normalized()
            for finger in ['Index','Middle','Ring','Pinky']:
                for joint,degrees in enumerate((20,45,60),1):
                    theta=math.radians(degrees)
                    orient_bone(arm,named(arm,'RightHand'+finger+str(joint)),hand_forward*math.cos(theta)+palm*math.sin(theta))
            check['support_surface_z']=rest_surface
            checks.append(check)
        for bone in arm.pose.bones:
            bone.rotation_mode='QUATERNION'
            previous=previous_final_rotations.get(bone.name)
            if previous and previous.dot(bone.rotation_quaternion)<0:bone.rotation_quaternion.negate()
            previous_final_rotations[bone.name]=bone.rotation_quaternion.copy()
            bone.keyframe_insert('rotation_quaternion',frame=scene.frame_current)
            bone.keyframe_insert('location',frame=scene.frame_current)
        if prop:prop.keyframe_insert('location',frame=scene.frame_current);prop.keyframe_insert('rotation_euler',frame=scene.frame_current)
        state['performance_checks'].append(dict(u=u,frame=scene.frame_current,arms=checks))
    state['actions']=[action]
    state['contacts']=[dict(kind='canonical_character',source='model_refferences/creator/lineart/asset.blend',
        skeleton_preserved=True,anatomical_hands=2,facial_animation=False),
        dict(kind='camera_mode',camera=record['camera'],preview_mirrored=not friend,
        intent='Eyes level and steady front camera' if not high else 'Front lens above the eyes, angled down')]
    state['adaptations']=[
        'Owner restored canonical character guides. Face geometry is the safety target; hair and shoulders are supporting silhouette.',
        'Original body rig and skinning; independent two-bone arm solves. No detached replacement hands.',
        'Approved open-palm verdict gestures are retained. Cup and fork use separate anatomical grips: index/thumb side upright, positive finger flexion into the palm, and explicit thumb opposition. Rotation is shared by shoulder and forearm.',
        'Fixed source smile: no jaw, lip sync, chewing or blink controls exist. The bite stops before mouth entry; the cup can cover the mouth.',
        '18 mm wide front-camera framing; 24 mm rear-camera framing for friend-filmed alternatives. Front previews are mirrored at export only.'
    ]
    return state
