"""Visitor-side bar scenes and physically connected cup pours with curved camera paths."""
import bpy
import math
from mathutils import Vector,Euler
import assets as A
import geometry as G
import real_hands as H
from drink_scenes import pose,glass,pour_stream,filling,counter
from motion_paths import camera_path,sequence

IDS=['cup_pour_eye_hold','cup_shot_eye_in_cd_through','cup_high_out_dm','glass_drink_high_hold',
     'glass_flight_high_truckr_cc','glass_outro_high_out_dm','glass_pour_eye_in_cd_through',
     'glass_pour_low_in_cd','glass_eye_tiltd_cc']


def review(gid):
    return dict(subject='Physically supported drink and its actual next resource',angle='Customer-side low/high view with smooth coordinated height and X-axis pitch change',
        motion='Curved handheld lean or small side step; no camera behind the bar',focal_point='Receiving cup/glass first, then its real table or board',
        composition='Near customer edge, glass support and distant taps make access direction explicit',golden_ratio='Clear flow endpoint and visitor access take precedence',
        lighting='Fixed side/venue light; no bloom or animated bar lighting',contacts='Vessel base rests on counter/saucer; flow starts at the actual spout and ends inside the opening',
        handover='Keep the drink and next board/table in one scene',mobile='All bar cameras stay in the customer aisle; ordinary reachable heights and short curved movements')


def customer_bar(board=None,pouring=False):
    A.tag(G.block('Customer-facing bar carcass',(0,.40,.55),(2.6,1.05,1.1),.02),'structure','The near vertical front identifies the visitor side')
    A.tag(G.block('Bar top with visible customer lip',(0,.40,1.105),(2.7,1.10,.07),.025),'support','Vessels rest near the customer edge at y=-0.15; staff space is beyond the taps')
    A.tag(G.tube('Customer foot rail',[(-1.2,-.32,.25),(1.2,-.32,.25)],.015),'background','Foot rail belongs to the public seating side')
    for x in [-.82,.82]:
        before=set(bpy.data.objects);G.stool('Customer bar stool',x,-.70)
        for obj in set(bpy.data.objects)-before:A.tag(obj,'background','Stools make the accessible filming side unambiguous')
    for x in [-.33,0,.33]:
        if not (pouring and x==0):A.tag(G.tube('Distant tap neck',[(x,.72,1.14),(x,.72,1.58),(x,.36,1.63),(x,.10,1.53)],.014),'background','Taps are across the bar, not behind the visitor camera')
        A.tag(G.tube('Distant tap handle',[(x,.67,1.60),(x,.67,1.79)],.016),'background','Staff-operated handle remains on the far side')
    for x in [-.8,-.55,.55,.8]:A.tag(G.bottle('Far-side bar bottle',x,.88,1.14,height=.29,radius=.034),'background','Quiet bar context stays beyond the served drink')
    if board:
        A.menu_board((0,.96,1.93),title='LIVE MUSIC' if board=='event' else 'HAPPY HOUR' if board=='hours' else 'ON TAP',
            selected='TONIGHT' if board=='event' else 'HOURS' if board=='hours' else 'YOUR PICK',right='TIME' if board in ['event','hours'] else 'PRICE',
            rows=[('DRINK','PRICE'),('SNACK','PRICE')] if board=='hours' else [('NEXT EVENT','TIME')] if board=='event' else [('TAP','PRICE')])
    A.fixed_side_light((0,.1,1.3))


def check_visitor_camera(cam,duration):
    positions=[]
    for f in range(1,round(duration*15)+1):
        bpy.context.scene.frame_set(f);positions.append(cam.location.y)
    assert max(positions)<-.20,'Camera must remain outside the customer edge of the bar'
    return dict(camera_max_y=max(positions),customer_edge_y=-.15,visitor_side=True)


def bar(scene,spec):
    gid=spec['id'];flight=gid=='glass_flight_high_truckr_cc';event=gid=='glass_drink_high_hold';hours=gid=='glass_pour_eye_in_cd_through';low=gid=='glass_pour_low_in_cd'
    board='taps' if flight else 'event' if event else 'hours' if hours else None;customer_bar(board,pouring=hours or low)
    if flight:
        A.tag(G.block('Supported flight paddle',(0,.03,1.15),(.93,.25,.02),.012),'support','Every tasting glass rests on the same paddle at the visitor edge')
        for x in [-.33,-.11,.11,.33]:root,liquid=glass((x,.03,1.16),name='Flight glass');root.scale=(.70,)*3
    else:
        root,liquid=glass((0,.03,1.14),name='Same ordered visitor-side glass',filled=not (hours or low))
        if hours or low:
            A.tag(G.tube('Serving spout to receiving glass',[(0,.72,1.58),(0,.20,1.58),(0,.06,1.51)],.012),'support','Actual serving spout reaches the glass near the customer edge')
            pour_stream((0,.06,1.51),(0,.03,1.30),3.25,1.25,'Flow inside the served glass');filling(liquid,3.2)
    focus=(0,.03,1.24);duration=10 if flight else 9 if event or hours else 8 if low else 5
    if flight:knots=[(0,(-.28,-.58,1.66),focus),(2.3,(.13,-.64,1.77),focus),(4,(.30,-.70,1.70),focus),(6.4,(.20,-.88,1.57),(0,.96,1.96)),(9.9,(.08,-.78,1.54),(0,.62,1.57))];nxt='tap_taps_low_tiltd_mm'
    elif event or hours:
        start=(0,-.55,1.69) if event else (-.035,-.53,1.25)
        knots=[(0,start,focus),(2.5,(.065,-.50,1.64) if event else (.04,-.48,1.31),focus),
               (4,(.16,-.61,1.60) if event else (.10,-.52,1.35),focus),(6.1,(.30,-.78,1.51),(0,.96,1.88)),(8.9,(.20,-.72,1.47),(0,.96,1.98))]
        nxt='menu_event_low_in_cd' if event else 'menu_hours_low_out_dc'
    elif low:
        knots=[(0,(-.04,-.55,1.23),focus),(2.3,(.045,-.48,1.30),focus),(4,(.09,-.52,1.35),focus),(6,(.20,-.60,1.64),(0,.03,1.33)),(7.9,(.09,-.55,1.51),(0,.03,1.21))];nxt='glass_eye_tiltd_cc'
    elif gid=='glass_eye_tiltd_cc':
        knots=[(0,(.20,-.60,1.64),(0,.03,1.33)),(2.1,(.08,-.57,1.53),(0,.03,1.25)),(4.9,(-.12,-.62,1.48),(0,.03,1.16))];nxt=None
    else:
        knots=[(0,(-.10,-.45,1.59),focus),(2.2,(.04,-.68,1.76),(0,.17,1.30)),(4.9,(.22,-1.02,1.71),(0,.35,1.40))];nxt=None
    cam=camera_path('Customer-side '+gid,knots,duration,31 if flight else 35)
    result=sequence(cam,duration,4 if nxt else None,['Served vessels stay physically supported at the customer edge','Smooth diagonal travel and changing pitch connect the drink to the same bar context'],next_guide=nxt,landing=4 if nxt else None)
    result['visitor_access_check']=check_visitor_camera(cam,duration)
    result['source_adaptations'].append('Uncertain glass-holding hands are omitted; the served glass stays on its support while the phone changes viewpoint')
    return result


def water_to_cup(scene,spec):
    A.table(radius=.70);A.saucer();cup=A.cup();A.pasta((-.29,.16,.785));A.fixed_side_light((0,0,.9))
    for obj in list(cup.children_recursive):
        if obj.name.endswith('coffee surface'):bpy.data.objects.remove(obj,do_unlink=True)
    level=A.tag(G.lathe('Water rising inside cup',[(0,0),(.045,0),(.045,.075),(0,.075)],(0,0,.818),40),'hero','The water level is inside the receiving cup')
    for t,s in [(0,.05),(1.4,.05),(3.2,1),(8,1)]:pose(level,t,scale=(1,1,s))
    before=set(bpy.data.objects)
    G.lathe('Small kettle body',[(0,0),(.055,0),(.065,.06),(.053,.13),(.045,.14),(0,.14)],(0,0,0),40)
    G.tube('Kettle spout',[(-.045,0,.08),(-.085,0,.11),(-.12,0,.13)],.009)
    G.tube('Kettle handle',[(.05,0,.12),(.095,0,.12),(.105,0,.05),(.055,0,.035)],.007)
    kettle=A.group('Kettle with attached anatomical grip',before,(.18,0,1.06),'support','A single rigid kettle, spout and handle stay connected')
    hand=H.place('pinch','R',target=(.095,0,.09),forward=(0,0,1),normal=(0,-1,0),anchor='grip');hand.parent=kettle
    for t,a in [(0,0),(.9,0),(1.3,-25),(3.2,-25),(3.6,0),(8,0)]:pose(kettle,t,rotation=(0,math.radians(a),0))
    tip=Vector((.18,0,1.06))+Euler((0,math.radians(-25),0)).to_matrix()@Vector((-.12,0,.13))
    endpoint=Vector((tip.x,0,.89));assert abs(endpoint.x)<.04
    pour_stream(tip,endpoint,3.15,1.45,'Water from kettle spout into cup')
    cam=camera_path('Kettle fills cup beside plate',[(0,(.02,-.57,1.12),(0,0,.94)),(3.4,(.045,-.56,1.15),(0,0,.94)),
        (4,(.08,-.60,1.23),(0,0,.94)),(6.1,(.20,-.58,1.54),(-.12,.08,.85)),(8.9,(.29,-.41,1.69),(-.12,.08,.84))],9,33)
    result=sequence(cam,9,4,['Water starts at the actual tilted kettle spout and lands inside the cup','A diagonal rising arc reveals that cup and the neighbouring plate on the same table'],next_guide='plate_spread_top_out_cw',landing=4)
    result['pour_contact_check']=dict(spout=list(tip),endpoint=list(endpoint),inside_cup=True,opening_radius_m=.047)
    return result


def coffee(scene,spec):
    counter();A.saucer();A.cup();A.fixed_side_light((0,0,.87));gid=spec['id']
    if gid=='cup_shot_eye_in_cd_through':
        A.tag(G.block('Public machine spout',(0,.025,1.13),(.13,.09,.045),.012),'support','Only the publicly visible spout is needed')
        pour_stream((0,0,1.11),(0,0,.902),3.65,1.2,'Espresso into supported cup')
        knots=[(0,(-.04,-.36,.90),(0,0,.88)),(2.1,(.02,-.31,.96),(0,0,.88)),(4.9,(.06,-.27,1.03),(0,0,.88))]
    else:knots=[(0,(-.10,-.23,1.17),(0,0,.86)),(2.2,(.06,-.35,1.22),(0,0,.86)),(4.9,(.23,-.48,1.23),(0,.04,.87))]
    cam=camera_path('Supported coffee cup natural reveal',knots,5,38)
    return sequence(cam,5,actions=['The same cup rests on its saucer and public counter','A small curved rise changes pitch and reveals the coffee context without an unreliable pickup grip'])


def build(scene,spec):
    if spec['id']=='cup_pour_eye_hold':return water_to_cup(scene,spec)
    if spec['id'] in ['cup_shot_eye_in_cd_through','cup_high_out_dm']:return coffee(scene,spec)
    return bar(scene,spec)
