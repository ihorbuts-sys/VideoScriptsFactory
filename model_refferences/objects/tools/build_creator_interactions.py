"""Pastry selection, a real cup grip, and a coupled tongs-to-box transfer."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector,Matrix,Quaternion,Euler
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
import build_coffee_glass_batch as G
import build_creator_guides as F
import prepare_creator_tripo as B
from prepare_rigged_characters import named
from coffee_scene_details import Grip,orient_bone
from build_coffee_work_guides import bind
from build_primary_food_scenes import soften_background

SOURCE=G.ROOT/'creator-bakery/scene.blend'
SELECT='Film from the customer aisle at display height. Move the phone slowly right as the creator leans toward the pastries and indicates her choice. Keep her pointing hand and the same display together, settle, then cut to the picks.'
PICK='From a reachable high angle on the customer self-service worktop, keep the tongs, tray and open box together. Follow the selected croissant as the tongs close, lift it clear of the tray and place it in the box. Continue raising the phone into the overhead box view.'
BOX='Continue from the packing view on the same worktop. Lift and centre the phone above the open box until both selected pastries and their support are clear. Keep the filled box supported, hold the final arrangement, then cut to the total.'
CUP='Use the front camera slightly above eye height, with your cup resting on its saucer. Reach for the handle, lift the cup into the lower part of the frame, show it briefly while looking into the lens, then return it to the same saucer. Keep the phone steady and finish with a short hold.'
TOTAL='Use the front camera a little above eye height with the filled box supported in the foreground. Keep your face and the same two pastries in frame, look into the lens and give the total and your favourite. Hold the final framing and finish the script.'


def route(points,t):
    if t<=points[0][0]:return Vector(points[0][1])
    if t>=points[-1][0]:return Vector(points[-1][1])
    i=next(i for i in range(len(points)-1) if points[i][0]<=t<points[i+1][0])
    a,p=points[i];b,q=points[i+1]
    return Vector(p).lerp(Vector(q),C.smooth(t,a,b))


def clear_root(root):
    for obj in [root,*root.children_recursive]:obj.animation_data_clear()


def station(scene):
    old=[o for o in scene.objects if o.get('asset_family') in ['dining_table','dining_chair'] or
         (o.get('asset_family') in ['saucer','latte_cup','croissant'] and o.location.y<2.5)]
    for obj in old:G.remove(obj)
    top=C.load('bar_counter',(.5,1.70,0))
    lo,hi=B.bounds(C.meshes(top));dims=hi-lo
    top.scale=(1.5/dims.x,.65/dims.y,1.0/dims.z)
    bpy.context.view_layer.update();lo,hi=B.bounds(C.meshes(top))
    top.location.z-=lo.z;bpy.context.view_layer.update()
    top['public_self_service_worktop']=True;C.role(top,'support')
    return top


class Hand:
    def __init__(self,arm,side):
        self.arm=arm;self.side=side;self.open=F.ArmPose(arm,side);self.grip=Grip(arm,side)
        self.fingers=[b for b in arm.pose.bones if side+'Hand' in b.name and b!=self.grip.hand]
        self.rest={b.name:b.matrix_basis.copy() for b in self.fingers};self.previous={}

    def grasp(self,point,frame,curl=1,forward=Vector((-1,0,0)),across=Vector((0,0,1)),offset=.06):
        for b in self.fingers:b.matrix_basis=self.rest[b.name].copy()
        check=self.grip.pose(Vector(point),frame,forward=forward,across=across,wrist_offset=offset)
        for b in self.fingers:
            b.rotation_mode='QUATERNION'
            q=self.rest[b.name].to_quaternion().slerp(b.rotation_quaternion,curl)
            prev=self.previous.get(b.name)
            if prev and prev.dot(q)<0:q.negate()
            b.rotation_quaternion=q;self.previous[b.name]=q.copy();b.keyframe_insert('rotation_quaternion',frame=frame)
        check['curl']=curl
        return check


def anchor(root,name):
    return next(o for o in root.children_recursive if o.get('function')==name).matrix_world.translation.copy()


def coffee_fill(cup):
    data=json.loads((P.ROOT/'latte_cup/functional/metadata.json').read_text())['anchors']
    rim=anchor(cup,'rim');z=rim.z-(data['rim'][2]-data['liquid_final_z'])
    before=set(bpy.data.objects)
    liquid=P.lathe('Presentation / contained coffee',[(0,-.002),(data['radius']*.89,-.002),(data['radius']*.89,0),(0,0)],(rim.x,rim.y,z),'coffee')
    liquid.parent=cup;liquid.matrix_parent_inverse=cup.matrix_world.inverted()
    C.role(cup,'hero')


def articulated_tongs():
    root=C.load('kitchen_tongs',scale=.55)
    meshes=C.meshes(root);vertices=np.array([root.matrix_world.inverted()@(o.matrix_world@v.co) for o in meshes for v in o.data.vertices])
    low,high=vertices.min(0),vertices.max(0);length=high[1]-low[1]
    bands=[]
    for q in [.10,.30,.50,.70,.90]:
        band=vertices[np.abs(vertices[:,1]-(low[1]+q*length))<length*.09]
        bands.append((q,float(np.ptp(band[:,2]))))
    positive=max(bands,key=lambda row:row[1])[0]>.5
    end=high[1] if positive else low[1];hinge=low[1] if positive else high[1]
    tips=vertices[(vertices[:,1]>high[1]-.17*length) if positive else (vertices[:,1]<low[1]+.17*length)]
    jaw=Vector(np.mean(tips,axis=0).tolist());jaw.z=(float(tips[:,2].min())+float(tips[:,2].max()))/2
    grip=Vector((0,hinge+(end-hinge)*.30,(low[2]+high[2])/2))
    for obj in meshes:
        obj.data=obj.data.copy();basis=obj.shape_key_add(name='Basis');closed=obj.shape_key_add(name='Close / spring tongs')
        to_root=root.matrix_world.inverted()@obj.matrix_world;inverse=to_root.inverted()
        for i,v in enumerate(basis.data):
            p=to_root@v.co;u=max(0,min(1,(p.y-hinge)/(end-hinge)))
            weight=u*u*(3-2*u)
            p.z=grip.z+(p.z-grip.z)*(1-.40*weight)
            closed.data[i].co=inverse@p
    root.rotation_euler=Euler((0,math.pi/2,math.pi if positive else 0),'XYZ')
    bpy.context.view_layer.update()
    return root,jaw,grip,dict(jaw_local=list(jaw),grip_local=list(grip),jaw_positive_y=positive,bands=bands)


def open_box_lid(root):
    """Open the existing paper lid farther around its own rear hinge."""
    hinge=Vector((0,.075,.045))
    for obj in C.meshes(root):
        obj.data=obj.data.copy();matrix=root.matrix_world.inverted()@obj.matrix_world;inverse=matrix.inverted()
        for vertex in obj.data.vertices:
            p=matrix@vertex.co
            weight=C.smooth(p.z,.045,.075)*C.smooth(p.y,.015,.055)
            if weight:
                p=hinge+Quaternion(Vector((1,0,0)),math.radians(-78)*weight)@(p-hinge)
                vertex.co=inverse@p
        obj.data.update()
    root['lid_pose']='Opened farther around the existing rear hinge, within the public worktop'
    bpy.context.view_layer.update()


def reset_actor(scene,base,turn=0):
    root=next(o for o in scene.objects if o.get('asset_family')=='creator')
    clear_root(root);root.location=base;root.rotation_euler.z=turn
    arm=next(o for o in root.children_recursive if o.type=='ARMATURE')
    for bone in arm.pose.bones:bone.matrix_basis.identity()
    bpy.context.view_layer.update();C.role(root,'hero')
    return root,arm


def setup(scene,key,row):
    P.MATS.clear();C.CACHE.clear();C.CONTACTS.clear();soften_background(scene)
    top=station(scene)
    base=Vector((-.10,3.32,0)) if key=='creator-pastry-select' else Vector((.5,2.18,0))
    turn=math.radians(128) if key=='creator-pastry-select' else 0
    root,arm=reset_actor(scene,base,turn)
    side='Right' if key=='creator-pastry-select' else 'Left';hand=Hand(arm,side)
    head=named(arm,'Head');neck=named(arm,'Neck');chest=named(arm,'Spine2')
    bases={b.name:(arm.matrix_world@b.matrix).to_3x3() for b in [head,neck,chest]}
    def axis(b,v):return (bases[b.name].inverted()@Vector(v)).normalized()
    records=[];scene.camera.data.shift_x=0;scene.camera.data.shift_y=0
    props={}
    if key=='creator-pastry-select':
        case=next(o for o in scene.objects if o.get('asset_family')=='display_case');C.role(case,'hero')
        camera=[(0,(1.45,2.20,1.5),(.15,3.55,1.14)),(1.2,(1.45,2.20,1.5),(.15,3.55,1.14)),
                (5.3,(1.65,2.40,1.58),(.30,3.72,1.10)),(8,(1.65,2.40,1.58),(.30,3.72,1.10))]
        scene.camera.data.lens=18
    elif key=='creator-coffee-present':
        saucer=C.supported('saucer',top,.54,1.89,quality='local');C.role(saucer,'support')
        cup=C.supported('latte_cup',saucer,.54,1.89,quality='functional');C.role(cup,'hero');coffee_fill(cup)
        start=cup.location.copy();rough=anchor(cup,'grip');rim=anchor(cup,'rim')
        direction=rough-rim;direction.z=0;direction.normalize()
        points=np.array([o.matrix_world@v.co for o in C.meshes(cup) for v in o.data.vertices])
        band=points[np.abs(points[:,2]-rough.z)<.018];projection=band[:,:2]@np.array(direction[:2])
        outer=band[projection>np.quantile(projection,.95)];grip=Vector(np.mean(outer,axis=0).tolist());grip.z=rough.z
        local_grip=cup.matrix_world.inverted()@grip
        marker=P.empty('Contact / calibrated presentation handle',tuple(local_grip));marker.parent=cup;marker['interaction_anchor']='cup_handle_contact'
        camera=[(0,(.42,1.54,1.64),(.515,2.18,1.46)),(11,(.42,1.54,1.64),(.515,2.18,1.46))]
        scene.camera.data.lens=18
        props.update(cup=cup,saucer=saucer,start=start,local_grip=local_grip)
    else:
        tray=C.supported('serving_tray',top,.77,1.78);C.role(tray,'support')
        box=C.supported('pastry_box',top,.36,1.80,turn=math.pi);C.role(box,'hero')
        open_box_lid(box)
        fixed=C.supported('croissant',box,.29,1.81,turn=math.pi/2,scale=.62,quality='approved-v2');C.role(fixed,'hero')
        pastry=C.supported('croissant',tray,.77,1.80,turn=math.pi/2,scale=.62,quality='approved-v2');C.role(pastry,'hero')
        start=pastry.location.copy();lo,hi=B.bounds(C.meshes(pastry));centre=(lo+hi)/2
        final=start.copy();final.x=.43;final.y=1.81;final.z+=C.surface(box,.43,1.81)-lo.z+.0005
        tongs,jaw,grip,calibration=articulated_tongs();C.role(tongs,'hero')
        for name,point in [('jaw',jaw),('grip',grip)]:
            marker=P.empty('Contact / tongs '+name,tuple(point));marker.parent=tongs;marker['interaction_anchor']='tongs_'+name
        camera=[(0,(.18,1.65,1.68),(.70,1.80,1.06)),(1.2,(.18,1.65,1.68),(.70,1.80,1.06)),
            (6.5,(.25,1.60,1.60),(.43,1.81,1.06)),(8,(.42,1.60,1.50),(.43,1.81,1.04)),
            (11.5,(.58,1.65,1.70),(.58,1.67,1.02)),(13,(.58,1.65,1.70),(.58,1.67,1.02))]
        scene.camera.data.lens=18
        props.update(tray=tray,box=box,pastry=pastry,start=start,final=final,centre=centre,
            tongs=tongs,jaw=jaw,grip=grip,calibration=calibration)
    row['sample_camera']=lambda t:(route([(a,p) for a,p,_ in camera],t),route([(a,q) for a,_,q in camera],t))
    rest=hand.open.rest.translation.copy()
    for frame in range(1,round(row['duration']*15)+1):
        t=(frame-1)/15
        down=18 if key=='creator-pastry-select' else 28 if key=='creator-pack-box' else 25*(1-C.smooth(t,3,4.4)+C.smooth(t,6,7.4))-5
        for bone,amount in [(head,down*.7),(neck,down*.3),(chest,3 if key!='creator-pastry-select' else 2)]:
            bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion(axis(bone,(math.cos(turn),math.sin(turn),0)),math.radians(amount))
            bone.keyframe_insert('rotation_quaternion',frame=frame)
        bpy.context.view_layer.update()
        if key=='creator-pack-box':
            weight=C.smooth(t,8,10)
            for obj in C.meshes(root):
                obj.color=(.050876*(1-weight)+.002708978*weight,1*(1-weight)+.03968191*weight,0,1)
                obj.keyframe_insert('color',frame=frame)
        if key=='creator-pastry-select':
            lift=C.smooth(t,1.2,2.8)*(1-C.smooth(t,5.4,7.0));target=Vector((.18,3.52,1.18))
            wrist=rest.lerp(target,lift);forward=(Vector((.35,3.72,.92))-target).normalized();across=Vector((0,0,1)).cross(forward).normalized()
            pole=Vector((-.9*math.cos(turn),-.9*math.sin(turn),-.8))
            check=hand.open.pose(wrist,forward,across,lift,frame,pole=pole)
            records.append(dict(frame=frame,phase='point',**check))
        elif key=='creator-coffee-present':
            cup=props['cup'];u=C.smooth(t,2.9,4.5)*(1-C.smooth(t,6,7.6))
            cup.location=props['start']+Vector((0,-.035*u,.25*u));bpy.context.view_layer.update()
            grip=cup.matrix_world@props['local_grip'];forward=Vector((-1,0,0));across=Vector((0,0,1))
            wrist=grip-forward*.06-Vector((0,1,0))*.021
            if t<2.4 or t>8.1:
                path=[(0,rest),(1.2,rest),(1.9,base+Vector((.24,-.04,1.18))),(2.4,wrist),
                      (8.1,wrist),(8.7,base+Vector((.24,-.04,1.18))),(9.5,rest),(11,rest)]
                lift=C.smooth(t,1.2,2.4)*(1-C.smooth(t,8.1,9.5))
                check=hand.open.pose(route(path,t),forward,across,lift,frame,pole=Vector((.9,.15,-.7)))
            else:
                curl=C.smooth(t,2.4,2.9)*(1-C.smooth(t,7.6,8.1))
                check=hand.grasp(grip,frame,curl=curl)
            cup.keyframe_insert('location',frame=frame)
            records.append(dict(frame=frame,phase='held' if 2.9<=t<=7.6 else 'supported',cup_position=list(cup.location),**check))
        else:
            p=props;pastry=p['pastry'];tongs=p['tongs']
            bread=route([(0,p['start']),(2.7,p['start']),(3.8,p['start']+Vector((0,0,.17))),
                (5.1,p['final']+Vector((0,0,.17))),(6.1,p['final']),(13,p['final'])],t)
            pastry.location=bread;pastry.keyframe_insert('location',frame=frame)
            jaw_world=p['centre']+(bread-p['start'])+Vector((0,0,.008))
            if t<2.2:jaw_world.z+=.05*(1-C.smooth(t,1.2,2.2))
            retract=C.smooth(t,6.5,7.8)
            if t>6.5:jaw_world+=Vector((0,.12,.12))*retract
            turn=-math.pi/2*retract
            tongs.rotation_euler.z=(math.pi if p['calibration']['jaw_positive_y'] else 0)+turn
            bpy.context.view_layer.update()
            tongs.location=jaw_world-tongs.matrix_world.to_3x3()@p['jaw'];bpy.context.view_layer.update()
            close=C.smooth(t,2.2,2.7)*(1-C.smooth(t,6.1,6.5))
            for obj in C.meshes(tongs):
                block=obj.data.shape_keys.key_blocks['Close / spring tongs'];block.value=close;block.keyframe_insert('value',frame=frame)
            rotation=Quaternion(Vector((0,0,1)),turn)
            grip=tongs.matrix_world@p['grip'];check=hand.grasp(grip,frame,curl=.72+.13*close,
                forward=rotation@Vector((0,-1,0)),across=rotation@Vector((-1,0,0)),offset=.045)
            tongs.keyframe_insert('location',frame=frame)
            tongs.keyframe_insert('rotation_euler',frame=frame)
            records.append(dict(frame=frame,phase='tray' if t<2.7 else 'held' if t<6.1 else 'box',
                pastry_position=list(bread),jaw_world=list(jaw_world),tongs_close=close,**check))
    row['interaction_checks']=dict(status='staged',frames=records,
        contacts=list(C.CONTACTS),tongs_calibration=props.get('calibration'),source_models_reused=True)
    return camera,list(C.CONTACTS)


def total_setup(scene,key,row):
    P.MATS.clear();C.CACHE.clear();C.CONTACTS.clear();soften_background(scene)
    root=next(o for o in scene.objects if o.get('asset_family')=='creator');C.role(root,'hero')
    arm=next(o for o in root.children_recursive if o.type=='ARMATURE')
    for obj in scene.objects:
        if obj.type=='MESH' and obj.data.shape_keys:obj.data.shape_keys.animation_data_clear()
    for obj in scene.objects:
        if obj.get('asset_family') in ['pastry_box','croissant'] and obj.location.y<2.5:C.role(obj,'hero')
    records=[]
    for frame in range(1,106):
        t=(frame-1)/15;nod=math.sin(math.pi*C.smooth(t,1.8,3.5))**2
        for suffix,share in [('Head',.7),('Neck',.3)]:
            bone=named(arm,suffix);basis=(arm.matrix_world@bone.bone.matrix_local).to_3x3()
            yaw=(basis.inverted()@Vector((0,0,1))).normalized();pitch=(basis.inverted()@Vector((1,0,0))).normalized()
            bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion(yaw,math.radians(-8*share))@Quaternion(pitch,math.radians((-8+2*nod)*share))
            bone.keyframe_insert('rotation_quaternion',frame=frame)
        records.append(dict(frame=frame,phase='total'))
    scene.camera.data.lens=18;scene.camera.data.shift_x=scene.camera.data.shift_y=0
    camera=[(0,(.38,1.35,1.64),(.48,2.0,1.35)),(7,(.38,1.35,1.64),(.48,2.0,1.35))]
    row['interaction_checks']=dict(status='staged',frames=records,contacts=[],source_models_reused=True,
        continuity='Same creator pose, supported box, two pastries and withdrawn tongs as the packing scene final frame')
    return camera,[]


SCENES={
 'creator-pastry-select':dict(duration=8,guide='case_eye_truckr_mm',template='bakery-box',step='case',title='Creator / choose a pastry',capture=6,
    direction=SELECT,bindings=[bind('case_eye_truckr_mm','bakery-box','case','shot',6,SELECT,'truck','image_motion',.25,'right',5.3,update_global=False,anchor_type='case',anchor_kind='none')]),
 'creator-coffee-present':dict(duration=11,guide='selfie_one_high_hold',template='cafe-seasonal-drink',step='verdict',title='Creator / lift, present and return coffee',capture=10,
    direction=CUP,bindings=[bind('selfie_one_high_hold','cafe-seasonal-drink','verdict','shot',10,CUP,'still',None,move_end=9.4,
       subject_motion='cup pickup, presentation and return',update_global=False,anchor_type='face',anchor_kind='face',variant_key='cafe-seasonal-drink.verdict')]),
 'creator-pack-box':dict(duration=13,guide='hand_pov_pastry_pov_in_mc',template='bakery-box',step='pick',title='Creator / tongs to box, then overhead reveal',capture=6.5,
    direction=PICK,phases=[dict(id='pick',start_s=0,end_s=8,capture_seconds=6.5,handover_seconds=1.5,handover_tail_seconds=0),
                         dict(id='box',start_s=8,end_s=13,capture_seconds=4,handover_seconds=0)],
    bindings=[bind('hand_pov_pastry_pov_in_mc','bakery-box','pick','pick',6.5,PICK,'pan','gyro_yaw',.5,'left',6.0,update_global=False,anchor_type='bread'),
              bind('topdown_box_top_out_cm','bakery-box','box','box',4,BOX,'dolly_out','image_scale',.70,move_end=3.5,update_global=False,anchor_type='box')]),
 'creator-box-total':dict(duration=7,guide='selfie_one_high_hold',template='bakery-box',step='total',title='Creator / the filled box and total',capture=6,
    direction=TOTAL,setup=total_setup,bindings=[bind('selfie_one_high_hold','bakery-box','total','shot',6,TOTAL,'still',None,move_end=5.2,
       subject_motion='small acknowledgement beside the filled box',update_global=False,anchor_type='face',anchor_kind='face',variant_key='bakery-box.total')])}
for key,row in SCENES.items():
    row.update(freeze=True,locked_camera=True,revision='creator-interactions-2026-11-02-v1')
    row.setdefault('setup',setup)
    for binding in row['bindings']:binding['update_capture_seconds']=True
    row['probe_frames']=[1,round(row['duration']*15*.35),round(row['duration']*15*.60),round(row['duration']*15)]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',choices=SCENES);p.add_argument('--scenes');p.add_argument('--build',action='store_true');p.add_argument('--probes',action='store_true');p.add_argument('--resume',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);G.SCENES.update(SCENES);G.SOURCE=SOURCE
    for key in a.scenes.split(',') if a.scenes else [a.scene] if a.scene else SCENES:
        G.SOURCE=G.ROOT/'creator-pack-box/scene.blend' if key=='creator-box-total' else SOURCE
        if a.build:
            scene,spec,folder=G.build(key)
            spec.update(color_samples=16,denoise_color=True,generation_credits_used=0,canonical_character='creator',
                interaction_checks=SCENES[key]['interaction_checks'],venue='coffee' if key=='creator-coffee-present' else 'bakery',
                venue_kinds=['coffee' if key=='creator-coffee-present' else 'bakery'],
                scope='connected_step_sequence' if key=='creator-pack-box' else 'complete_final_shot',
                handover_status='continuous_same_worktop' if key=='creator-pack-box' else 'cut_to_next_step')
            if key=='creator-coffee-present':
                spec['framing_probe_frames']=[1,75,165];F.finish_framing(scene,spec)
                bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
            (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        if a.probes or not a.build:G.render(key,a.probes,a.resume)
