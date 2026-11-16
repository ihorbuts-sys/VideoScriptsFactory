"""Continuous handheld-scale camera curves; both position and view direction travel."""
from mathutils import Vector
import geometry as G


def interpolate(knots,t,column):
    if t<=knots[0][0]:return Vector(knots[0][column])
    if t>=knots[-1][0]:return Vector(knots[-1][column])
    i=next(j for j in range(len(knots)-1) if knots[j][0]<=t<knots[j+1][0])
    a,b=knots[i:i+2];dt=b[0]-a[0];u=(t-a[0])/dt;p=Vector(a[column]);q=Vector(b[column])
    m=Vector((0,0,0)) if i==0 else (q-Vector(knots[i-1][column]))/(b[0]-knots[i-1][0])
    n=Vector((0,0,0)) if i+2==len(knots) else (Vector(knots[i+2][column])-p)/(knots[i+2][0]-a[0])
    return (2*u**3-3*u*u+1)*p+(u**3-2*u*u+u)*dt*m+(-2*u**3+3*u*u)*q+(u**3-u*u)*dt*n


def camera_path(name,knots,duration,lens=30):
    cam=G.camera(name,knots[0][1],Vector(knots[0][2])-Vector(knots[0][1]),lens)
    previous=None
    for f in range(1,round(duration*15)+1):
        t=(f-1)/15;position=interpolate(knots,t,1);target=interpolate(knots,t,2)
        rotation=(target-position).to_track_quat('-Z','Y').to_euler()
        if previous:rotation.make_compatible(previous)
        cam.location=position;cam.rotation_euler=rotation;previous=rotation.copy()
        cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
    return cam


def sequence(cam,duration=5,take_end=None,actions=None,next_guide=None,landing=None):
    result=dict(duration=duration,take_end=duration if take_end is None else take_end,cameras=[(0,cam)],
                scope='shot_and_handover' if next_guide else 'base_shot_with_action',
                handover_status='included' if next_guide else 'pending_contextual_sequence',
                intent='; '.join(actions or []),composition=actions or [],subject_actions=actions or [],
                mobile_feasibility=dict(visitor_space=True,max_phone_height_m=1.95,curved_handheld_path=True),
                source_adaptations=['Owner requests combined translation and X-axis pitch changes on smooth handheld curves'])
    if next_guide:result['shared_scene_handover']=dict(next_guide=next_guide,landing=landing or take_end,method='one_camera_shared_scene')
    return result
