"""Source camera timing constrained to normal smartphone filming."""
import json
import math
from pathlib import Path
from mathutils import Vector,Matrix
from drink_scenes import camera,key_camera,smooth,frame
BASE=Path(__file__).resolve().parents[2]


def apply(scene,spec,focus,span=.55,down=None,lens=30,action_objects=True):
    data=json.loads((BASE/'guides/templates'/(spec['id']+'.json')).read_text())
    steps=data.get('live',{}).get('steps',[])
    move=next((s for s in steps if s.get('kind')=='follow' and s.get('action')!='whip'),None)
    timeline=data.get('timeline',[]);duration=max(4,max([x['t'] for x in timeline] or [4.2]))
    duration=min(duration,7.2);focus=Vector(focus)
    if down is None:
        tilt=next((s['tilt']['target'] for s in steps if s.get('tilt')),0)
        down=90 if tilt>=80 else tilt
    direction=Vector((0,math.cos(math.radians(down)),-math.sin(math.radians(down))))
    distance=span*lens/32
    # A phone can reach the top-down view without a boom; use a wider fixed lens if necessary.
    if down>30 and focus.z+distance*math.sin(math.radians(down))>1.95:
        distance=(1.95-focus.z)/math.sin(math.radians(down));lens=distance*32/span
    origin=focus-direction*distance
    cam=camera('Phone '+spec['id'],origin,focus,lens)
    amount=move.get('amount',1.0) if move else 1.0
    end_distance=distance/amount if move else distance
    adaptations=[]
    if abs(end_distance-distance)>.65:
        end_distance=distance+math.copysign(.65,end_distance-distance);adaptations.append('Framing scale adapted to a short handheld lean while preserving move direction')
    if down>30 and focus.z+end_distance*math.sin(math.radians(down))>1.95:
        end_distance=(1.95-focus.z)/math.sin(math.radians(down));adaptations.append('Final phone height bounded to a reachable raised-phone position')
    if end_distance<.12:end_distance=.12;adaptations.append('Minimum phone working distance retained; use the detail cut rather than moving through the object')
    for f in range(frame(duration)):
        t=f/15;u=smooth((t-1.2)/(move.get('duration',1.8) if move else 1.8));p=origin.copy();target=focus.copy()
        action=move.get('action') if move else None
        if action in ['dolly_in','dolly_out']:p=focus-direction*(distance+(end_distance-distance)*u)
        elif action=='truck':p.x+=(-1 if move.get('direction')=='left' else 1)*.45*u;target.x+=p.x-origin.x
        elif action=='orbit':
            sign=-1 if move.get('direction')=='left' else 1;angle=math.radians(sign*move.get('arc',60)*(u-.5))
            offset=origin-focus;p=focus+Matrix.Rotation(angle,3,'Z')@offset
        elif action=='tilt':target.z-=.20*u
        key_camera(cam,t,p,target)
    whip=next((s for s in steps if s.get('action')=='whip'),None)
    if whip:
        scene.frame_set(frame(duration-.4));p=cam.location.copy();d=cam.rotation_euler.to_quaternion()@Vector((0,0,-1))
        # Top-down whips are a fast wrist pitch rather than yaw around the optical axis.
        axis='X' if down>75 else 'Z'
        for t,a in [(duration-.4,0),(duration-.05,65)]:key_camera(cam,t,p,p+Matrix.Rotation(math.radians(a),3,axis)@d)
    if not move and not action_objects:spec['static_hold']=True
    return dict(duration=duration,take_end=duration,cameras=[(0,cam)],source_adaptations=adaptations,
                mobile_feasibility=dict(phone_only=True,max_height_m=1.95,max_lean_m=.65,support='Elbows or phone propped when both subject hands are used',visitor_side_only=True),
                scope='base_shot_with_action',handover_status='pending_contextual_sequence')
