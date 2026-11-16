"""Canonical creator performances for two context-specific front-camera guides."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_coffee_glass_batch as G
import build_shared_venue as C
import build_assets as P
import prepare_creator_tripo as B
from build_coffee_counter_v2 import add_cast
from prepare_rigged_characters import named
from coffee_scene_details import orient_bone
from build_primary_food_scenes import soften_background
from build_coffee_work_guides import bind

INTRO='Use the front camera at eye height and about an arm length away. Keep your eyes near the upper third and the cafe behind one shoulder. Look into the lens, give a small natural acknowledgement, then finish your recommendation. Keep the phone steady and cut after the final hold.'
BAKERY='Stand on the customer side in front of the pastry display. Hold the front camera a little above eye height, leaving the case visible beside your shoulder. Introduce who the box is for and your budget; use one small open-hand gesture toward the display, then return your attention to the lens. Hold and cut.'


class ArmPose:
    """Two-bone reach with an explicit elbow pole and the original hand anatomy."""
    def __init__(self,arm,side):
        self.arm,self.side=arm,side
        self.upper=named(arm,side+'Arm');self.fore=named(arm,side+'ForeArm');self.hand=named(arm,side+'Hand')
        self.a=(arm.matrix_world.to_3x3()@(self.upper.tail-self.upper.head)).length
        self.b=(arm.matrix_world.to_3x3()@(self.fore.tail-self.fore.head)).length
        self.rest=(arm.matrix_world@self.hand.matrix).copy()
        wrist=arm.matrix_world@self.hand.head
        index=arm.matrix_world@named(arm,side+'HandIndex1').head
        pinky=arm.matrix_world@named(arm,side+'HandPinky1').head
        forward=((index+pinky)/2-wrist).normalized()
        across=(index-pinky).normalized();across=(across-forward*across.dot(forward)).normalized()
        self.frame=Matrix((forward,across,forward.cross(across))).transposed()
        self.fingers=[named(arm,side+'Hand'+finger+str(i)) for finger in ['Index','Middle','Ring','Pinky'] for i in [1,2,3]]
        self.finger_rest={b.name:b.matrix_basis.copy() for b in self.fingers}
        self.previous_rotations={}

    def pose(self,wrist,forward,across,blend,frame,pole=None):
        arm=self.arm;shoulder=arm.matrix_world@self.upper.head;target=wrist-shoulder
        for bone in self.fingers:bone.matrix_basis=self.finger_rest[bone.name].copy()
        distance=target.length
        assert abs(self.a-self.b)+.008<distance<(self.a+self.b)*.995,(self.side,'unreachable',distance,self.a+self.b)
        direction=target.normalized();along=(self.a*self.a-self.b*self.b+distance*distance)/(2*distance)
        height=math.sqrt(max(0,self.a*self.a-along*along))
        pole=Vector((.9 if self.side=='Left' else -.9,.08,-.8)) if pole is None else Vector(pole)
        pole=(pole-direction*pole.dot(direction)).normalized()
        elbow=shoulder+direction*along+pole*height
        orient_bone(arm,self.upper,elbow-shoulder)
        orient_bone(arm,self.fore,wrist-elbow)
        forward=forward.normalized();across=(across-forward*across.dot(forward)).normalized()
        desired=Matrix((forward,across,forward.cross(across))).transposed()@self.frame.inverted()@self.rest.to_3x3()
        rotation=self.rest.to_quaternion().slerp(desired.to_quaternion(),blend)
        world=rotation.to_matrix().to_4x4()@Matrix.Diagonal((*self.rest.to_scale(),1.))
        world.translation=wrist
        self.hand.matrix=arm.matrix_world.inverted()@world
        bpy.context.view_layer.update()
        knuckles=sum((arm.matrix_world@named(arm,self.side+'Hand'+finger+'1').head for finger in ['Index','Pinky']),Vector())/2
        actual_forward=(knuckles-wrist).normalized()
        fore_direction=(wrist-elbow).normalized()
        bend=fore_direction.angle(actual_forward)
        if bend>math.radians(75):
            comfortable=fore_direction.slerp(actual_forward,math.radians(75)/bend)
            correction=actual_forward.rotation_difference(comfortable)
            world=correction.to_matrix().to_4x4()@world;world.translation=wrist
            self.hand.matrix=arm.matrix_world.inverted()@world
            forward=correction@forward;across=correction@across
            bpy.context.view_layer.update()
        # Relax the source's curled fingers into a soft open palm. Preserve the
        # original thumb and every real joint; no replacement hand geometry.
        normal=forward.cross(across).normalized()
        directions={b.name:(arm.matrix_world.to_3x3()@(b.tail-b.head)).normalized() for b in self.fingers}
        for n,bone in enumerate(self.fingers):
            spread=[-.08,0,.04,.10][n//3]
            flex=math.radians([5,8,12][n%3])
            desired=(forward*math.cos(flex)+normal*math.sin(flex)+across*spread).normalized()
            orient_bone(arm,bone,directions[bone.name].lerp(desired,blend).normalized())
        for bone in [self.upper,self.fore,self.hand]+self.fingers:
            bone.rotation_mode='QUATERNION'
            previous=self.previous_rotations.get(bone.name)
            if previous and previous.dot(bone.rotation_quaternion)<0:bone.rotation_quaternion.negate()
            self.previous_rotations[bone.name]=bone.rotation_quaternion.copy()
            bone.keyframe_insert('rotation_quaternion',frame=frame);bone.keyframe_insert('location',frame=frame)
        error=((arm.matrix_world@self.hand.head)-wrist).length
        assert error<.002,error
        scale_error=max(abs(v-1) for v in self.hand.scale)
        assert scale_error<.005,('Hand scale changed',scale_error)
        return dict(side=self.side,reach_m=distance,reach_limit_m=self.a+self.b,wrist_error_m=error,
            hand_scale_error=scale_error,wrist=list(wrist))


def reduce_scene_meshes(root):
    rows=[]
    for obj in C.meshes(root):
        before=sum(len(p.vertices)-2 for p in obj.data.polygons)
        if before>180000:
            obj.data=obj.data.copy()
            bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
            modifier=obj.modifiers.new('Scene-only controlled simplification','DECIMATE');modifier.ratio=140000/before
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        rows.append(dict(mesh=obj.name,source_triangles=before,scene_triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)))
    return rows


def setup(scene,key,row):
    P.MATS.clear();C.CACHE.clear();C.CONTACTS.clear()
    soften_background(scene)
    if key=='creator-bakery':
        remove_ids={'barista','bar_counter','espresso_machine','coffee_grinder','milk_pitcher',
            'coffee_tamper','knock_box','serving_tray','takeaway_cup','pastry_box','portafilter',
            'cup_riser_local','espresso_liquid_local','espresso_stream_local','milk_liquid_local'}
        remove=[o for o in scene.objects if o.get('asset_family') in remove_ids or
            (o.get('asset_family')=='latte_cup' and o.location.y>3.5) or
            (o.get('asset_family')=='croissant' and o.location.y>3.5 and o.location.x<1.3)]
        def has_removed_parent(obj):
            parent=obj.parent
            while parent:
                if parent in remove:return True
                parent=parent.parent
            return False
        roots=[o for o in remove if not has_removed_parent(o)]
        for obj in roots:G.remove(obj)
        case=C.load('display_case',(.6,4.10,0))
        C.role(case,'support')
    base=Vector((-.70,2.55,0)) if key=='creator-cafe' else Vector((-.45,3.00,0))
    creator,arm=add_cast('creator',tuple(base),0)
    for obj in creator.children_recursive:obj.animation_data_clear()
    for bone in arm.pose.bones:bone.matrix_basis.identity()
    bpy.context.view_layer.update()
    meshes=reduce_scene_meshes(creator)
    C.role(creator,'hero')
    left,right=ArmPose(arm,'Left'),ArmPose(arm,'Right')
    head=named(arm,'Head');neck=named(arm,'Neck');chest=named(arm,'Spine2')
    bases={b.name:(arm.matrix_world@b.matrix).to_3x3() for b in [head,neck,chest]}
    def local(bone,axis):return (bases[bone.name].inverted()@Vector(axis)).normalized()
    high=key=='creator-bakery'
    camera_start=base+Vector((-.14,-.54,1.64 if high else 1.54))
    target=base+Vector((.015,0,1.46 if high else 1.51))
    scene.camera.data.lens=18 if high else 20
    scene.camera.data.shift_x=0
    def camera_pose(t):
        p=camera_start+Vector((.006*math.sin(t*.8),.004*math.sin(t*.9),.003*math.sin(t*1.1)))
        return p,target.copy()
    row['sample_camera']=camera_pose
    rest_left=left.rest.translation.copy()
    checks=[];head_samples=[]
    for frame in range(1,round(row['duration']*15)+1):
        t=(frame-1)/15
        # Hips, legs and feet stay planted; breathing comes from the chest.
        for bone in [head,neck,chest]:bone.rotation_mode='QUATERNION'
        chest.rotation_quaternion=Quaternion(local(chest,(1,0,0)),math.radians(.35*math.sin(t*1.7)))
        chest.keyframe_insert('rotation_quaternion',frame=frame)
        nod=math.sin(math.pi*C.smooth(t,1.8,3.2))**2
        glance=(C.smooth(t,1.5,2.5)-C.smooth(t,3.1,4.2)) if high else 0
        yaw=-14+10*glance+1.2*math.sin(t*.8)
        pitch=(-7 if high else -1)+3.0*nod
        head.rotation_quaternion=Quaternion(local(head,(0,0,1)),math.radians(yaw*.7))@Quaternion(local(head,(1,0,0)),math.radians(pitch*.7))@Quaternion(local(head,(0,1,0)),math.radians(.8*math.sin(t*1.1)))
        neck.rotation_quaternion=Quaternion(local(neck,(0,0,1)),math.radians(yaw*.3))@Quaternion(local(neck,(1,0,0)),math.radians(pitch*.3))
        for bone in [head,neck]:bone.keyframe_insert('rotation_quaternion',frame=frame)
        bpy.context.view_layer.update()
        lift=C.smooth(t,1.2,2.2)*(1-C.smooth(t,3.4,5.0))
        wave=math.radians(10)*math.sin((t-2.2)*math.tau*.7)*lift if not high else 0
        lifted=base+Vector((.08 if not high else .12,-.16,1.21 if not high else 1.10))
        wrist=rest_left.lerp(lifted,lift)
        fingers=Vector((math.sin(wave),0,math.cos(wave))) if not high else Vector((.35,-.1,.75))
        normal=Vector((-.14,-.54,0)).normalized()
        across=normal.cross(fingers).normalized()
        checks.append(left.pose(wrist,fingers,across,lift,frame))
        # Frame the pose and the free-hand gesture. The other hand stays below
        # the portrait crop; it must never become a giant foreground occluder.
        head_samples.append(dict(frame=frame,head=list(arm.matrix_world@head.tail),left_wrist=checks[-1]['wrist']))
    row['performance_checks']=dict(status='posed',rig_bones=len(arm.pose.bones),
        source_preserved=True,mesh_reduction=meshes,max_wrist_error_m=max(c['wrist_error_m'] for c in checks),
        max_reach_fraction=max(c['reach_m']/c['reach_limit_m'] for c in checks),
        facial_animation='Original expression; no lip-sync or facial shape keys',
        action='Small open-hand display gesture and a glance back to lens' if high else 'Small open-hand acknowledgement, nod and steady eye contact',
        hands_visible_at_most=2,samples=head_samples)
    return [(0,tuple(camera_start),tuple(target)),(row['duration'],tuple(camera_start),tuple(target))],[]


SCENES={
    'creator-cafe':dict(duration=7,guide='talking_head_eye_level',template='cafe-first-visit',step='outro',
        title='Creator / eye-level cafe recommendation',capture=6,freeze=True,locked_camera=True,setup=setup,direction=INTRO,
        bindings=[bind('talking_head_eye_level','cafe-first-visit','outro','shot',6,INTRO,'still',None,
            move_end=5.2,subject_motion='natural acknowledgement and small greeting',update_global=False,anchor_type='face',anchor_kind='face')]),
    'creator-bakery':dict(duration=7,guide='selfie_one_high_hold',template='bakery-box',step='hook',
        title='Creator / bakery-box introduction',capture=6,freeze=True,locked_camera=True,setup=setup,direction=BAKERY,
        bindings=[bind('selfie_one_high_hold','bakery-box','hook','shot',6,BAKERY,'still',None,
            move_end=5.2,subject_motion='open-hand display gesture and glance back to lens',update_global=False,anchor_type='face',anchor_kind='face')]),
}


def finish_framing(scene,spec):
    creator=next(o for o in scene.objects if o.get('asset_family')=='creator')
    hair=next(o for o in C.meshes(creator) if o.name.split('.')[0]=='tripo_part_0')
    def bounds():
        deps=bpy.context.evaluated_depsgraph_get()
        obj=hair.evaluated_get(deps);mesh=obj.to_mesh()
        coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords)
        points=np.ones((len(mesh.vertices),4));points[:,:3]=coords.reshape(-1,3)
        matrix=scene.camera.calc_matrix_camera(deps,x=405,y=720)@scene.camera.matrix_world.inverted()@obj.matrix_world
        clip=points@np.array(matrix).T;xy=clip[:,:2]/clip[:,3,None]*.5+.5
        obj.to_mesh_clear()
        return [float(xy[:,0].min()),float(xy[:,0].max()),float(xy[:,1].min()),float(xy[:,1].max())]
    samples=[]
    frames=spec.get('framing_probe_frames',[1,39,105])
    for frame in frames:scene.frame_set(frame);samples.append(bounds())
    minimum=min(b[0] for b in samples)
    if minimum<.035:
        scene.frame_set(1);before=bounds()[0]
        old=scene.camera.data.shift_x;scene.camera.data.shift_x+=.01
        slope=(bounds()[0]-before)/.01
        scene.camera.data.shift_x=old+(.035-minimum)/slope
    samples=[]
    for frame in frames:
        scene.frame_set(frame);b=bounds()
        assert .02<b[0]<b[1]<.98 and .02<b[2]<b[3]<.98,('Hair outside portrait',frame,b)
        samples.append(dict(frame=frame,normalized_bounds=b))
    scene.frame_set(1)
    spec['hair_framing']=samples
    spec['camera']['shift_x']=scene.camera.data.shift_x
    spec['camera']['lens_mm']=scene.camera.data.lens


for row in SCENES.values():
    row['probe_frames']=[1,39,105]
    row['revision']='creator-glass-2026-10-30-v1'
    row['composition']=['Canonical creator from the existing 65-bone rig',
        'Planted feet, natural neck and chest movement, anatomically jointed arms',
        'Fixed public-side phone lens with slight hand drift',
        'Hero creator and softer background context; a clear eye line and readable free-hand gesture']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',choices=SCENES);p.add_argument('--build',action='store_true');p.add_argument('--probes',action='store_true');p.add_argument('--resume',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);G.SCENES.update(SCENES)
    for key in [a.scene] if a.scene else SCENES:
        if a.build:
            scene,spec,folder=G.build(key)
            spec.update(color_samples=16,denoise_color=True,generation_credits_used=0,canonical_character='creator',
                performance_checks=SCENES[key]['performance_checks'],camera_facing='front',
                venue='bakery' if key=='creator-bakery' else 'coffee',
                composition=SCENES[key]['composition'],
                venue_kinds=['bakery'] if key=='creator-bakery' else ['coffee'])
            scene.frame_set(1)
            # Keep the estimated eye line on the upper third with fixed film shift.
            creator=next(o for o in scene.objects if o.get('asset_family')=='creator')
            arm=next(o for o in creator.children_recursive if o.type=='ARMATURE')
            eye=(arm.matrix_world@named(arm,'Head').tail)+Vector((0,-.10,-.01))
            for _ in range(4):
                y=world_to_camera_view(scene,scene.camera,eye).y
                scene.camera.data.shift_y+=(y-.67)*.5625
            spec['eye_line_start']=list(world_to_camera_view(scene,scene.camera,eye))
            spec['camera']['lens_mm']=scene.camera.data.lens
            spec['camera']['shift_y']=scene.camera.data.shift_y
            spec['camera']['shift_x']=scene.camera.data.shift_x
            finish_framing(scene,spec)
            bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
            (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        if a.probes or not a.build:G.render(key,a.probes,a.resume)
