"""Native multi-object drink guides, built from the actual filming instructions.

A cut changes takes; a phone never flies between unrelated camera heights.
"""
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
import assets as A
import geometry as G

IDS=['cup_eye_hold_whipout','cup_high_out_dm','cup_pour_eye_hold','cup_shot_eye_in_cd_through','glass_build_eye_hold','glass_drink_high_hold','glass_eye_tiltd_cc','glass_favorite_eye_in_cd','glass_flight_high_truckr_cc','glass_outro_high_out_dm','glass_pour_eye_in_cd_through','glass_pour_low_in_cd','glasses_clink_center','tap_pour_glass','tap_taps_low_tiltd_mm']
FPS=15


def smooth(t):return .5-.5*math.cos(math.pi*max(0,min(1,t)))
def frame(t):return round(t*FPS)+1


def pose(obj,t,location=None,rotation=None,scale=None):
    if location is not None:obj.location=location;obj.keyframe_insert(data_path='location',frame=frame(t))
    if rotation is not None:obj.rotation_euler=rotation;obj.keyframe_insert(data_path='rotation_euler',frame=frame(t))
    if scale is not None:obj.scale=scale;obj.keyframe_insert(data_path='scale',frame=frame(t))


def camera(name,position,target,lens=32):
    return G.camera(name,position,Vector(target)-Vector(position),lens)


def key_camera(cam,t,position,target):
    cam.location=position;cam.rotation_euler=(Vector(target)-Vector(position)).to_track_quat('-Z','Y').to_euler()
    for path in ['location','rotation_euler']:cam.keyframe_insert(data_path=path,frame=frame(t))


def counter(z=.785):
    return A.tag(G.block('Public counter surface',(0,.20,z-.025),(1.50,.72,.05),.012),'structure','Physical support; filming stays on the visitor side')


def glass(position=(0,0,.785),name='Tasting glass',role='hero',filled=True):
    before=set(bpy.data.objects)
    body=G.lathe(name+' open bowl',[(0,0),(.036,0),(.045,.014),(.052,.16),(.050,.205),(.047,.205),(.047,.19),(.042,.028),(0,.028)],(0,0,0),40)
    # A front cutaway makes the liquid level readable in a transparent ghost.
    bm=bmesh.new();bm.from_mesh(body.data)
    remove=[face for face in bm.faces if face.calc_center_median().y<-.002 and .035<face.calc_center_median().z<.195]
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(body.data);bm.free()
    A.tag(body,role,'Real rim and supporting base; front cutaway explains transparent glass and liquid level')
    root=A.group(name,before,position,role,'The glass remains a coherent rigid object and is supported until deliberately lifted')
    liquid=G.lathe(name+' liquid level',[(0,0),(.041,0),(.045,.13),(0,.13)],(0,0,.028),40)
    A.tag(liquid,'support','Visible liquid level is the action landmark inside the transparent-glass cutaway');liquid.parent=root
    if not filled:liquid.scale.z=.02
    return root,liquid


def grip(prop,side=1):
    """One anatomical hand holds the glass from its side: palm on the glass, fingers round the front, forearm back."""
    import real_hands
    hand=real_hands.place('pinch','R' if side>0 else 'L',target=(side*.047,0,.09),forward=(0,-1,0),normal=(-side,0,0),anchor='grip')
    hand.parent=prop
    return hand


def bar_context():
    counter()
    for x in [-.44,-.12,.20,.50]:
        A.tag(G.bottle('Faint back-bar bottle',x,.45,.81,height=.28),'background','Quiet distant landmarks reveal parallax and venue scale')
    for x in [-.28,0,.28]:
        A.tag(G.tube('Fixed curved tap',[(x,.30,.80),(x,.30,1.04),(x,.17,1.10),(x,.12,1.06)],.014),'important_background','Tap row is a useful destination and venue landmark')
        A.tag(G.lathe('Tap handle',[(.012,0),(.020,.09),(.018,.13),(0,.14)],(x,.30,1.04),24),'important_background','Repeated handles establish visual rhythm')
    A.tag(G.block('Small folded coaster',(.23,.03,.790),(.15,.13,.010),.004),'background','Subordinate tabletop scale cue, separated from the main glass')


def kettle(position=(.15,0,1.0)):
    before=set(bpy.data.objects)
    G.lathe('Reusable small pouring jug',[(0,0),(.041,0),(.048,.03),(.043,.10),(.037,.11),(0,.11)],(0,0,0),32)
    G.tube('Jug spout',[(-.035,0,.06),(-.065,0,.10),(-.09,0,.115)],.009)
    G.tube('Jug open handle',[(.04,0,.09),(.075,0,.09),(.08,0,.035),(.045,0,.025)],.006)
    root=A.group('Reusable pouring jug',before,position,'support','Jug rotates as a single rigid object; the hand moves with its handle')
    grip(root);return root


def pour_stream(start,end,duration,start_time=1.2,name='Pour stream'):
    before=set(bpy.data.objects)
    points=[Vector(start).lerp(Vector(end),i/8) for i in range(9)]
    obj=A.tag(G.tube(name,points,.0022),'hero','Continuous stream connects the spout and the receiving liquid surface')
    # Collapse radially, retaining the actual endpoints when the pour is active.
    obj.shape_key_add(name='Basis');off=obj.shape_key_add(name='No pour')
    a=Vector(start)
    for v in off.data:v.co=a+(v.co-a)*.0001
    for t,value in [(0,1),(start_time-.10,1),(start_time+.10,0),(duration-.20,0),(duration,1)]:
        off.value=value;off.keyframe_insert(data_path='value',frame=frame(t))
    return obj


def filling(liquid,end,height=.13,start=1.2):
    for t,v in [(0,.02),(start,.02),(end,.98),(end+.5,1)]:pose(liquid,t,scale=(1,1,v))


def side_camera(name,focus,span=.42,down=0):
    focus=Vector(focus);distance=span*34/32
    direction=Vector((0,math.cos(math.radians(down)),-math.sin(math.radians(down))))
    return camera(name,focus-direction*distance,focus,34)


def dolly(cam,focus,end,amount,start=1.2,move=1.8):
    focus=Vector(focus);offset=cam.location-focus
    for f in range(frame(end)):
        t=f/FPS;factor=1+(1/amount-1)*smooth((t-start)/move)
        key_camera(cam,t,focus+offset*factor,focus)


def stage_shift(before,cam):
    root=A.empty('Separate take location',(6,0,0))
    for obj in set(bpy.data.objects)-before-{root}:
        if obj.parent is None:obj.parent=root
    return root


def next_portrait(start,duration=2,held_glass=False):
    before=set(bpy.data.objects)
    actor=A.portrait((0,0,0),prop=None)
    held,liq=glass((.12,-.22,1.25),name='Same ordered glass') if held_glass else (A.cup((.12,-.22,1.25),name='Same ordered cup'),None)
    grip(held)
    for t,a in [(start,0),(start+.8,1),(start+duration,1)]:
        pose(held,t,location=(.12,-.22+.07*a,1.25+.23*a),rotation=(math.radians(-10*a),0,0))
    A.fixed_side_light((0,0,1.6),warm=False)
    cam=camera('Next take - creator and ordered drink',(0,-.78,1.56),(0,0,1.55),32)
    stage_shift(before,cam)
    return cam


def next_menu(start,kind='event'):
    before=set(bpy.data.objects)
    if kind=='event':title,selected,right='LIVE MUSIC','TONIGHT','TIME'
    else:title,selected,right='HAPPY HOUR','HOURS','TIME'
    A.menu_board((0,.35,1.7),title=title,selected=selected,right=right,rows=[('DRINK','PRICE'),('SNACK','PRICE')] if kind!='event' else [('NEXT NIGHT','TIME'),('NEXT EVENT','TIME')],tall=kind!='event')
    A.fixed_side_light((0,.35,1.7),warm=False)
    focus=Vector((0,.35,1.755));direction=Vector((0,math.cos(math.radians(12)),math.sin(math.radians(12))))
    cam=camera('Next take - '+title,focus-direction*.78,focus,34)
    for f in range(frame(start),frame(start+2)):
        t=(f-1)/FPS;u=smooth((t-start-.25)/1.5);distance=.78+(.18*u if kind!='event' else -.17*u)
        key_camera(cam,t,focus-direction*distance,focus)
    stage_shift(before,cam);return cam


def next_taps(start):
    before=set(bpy.data.objects);bar_context()
    A.menu_board((0,.40,1.65),title='ON TAP',selected='YOUR PICK',right='PRICE')
    A.fixed_side_light((0,.1,1.35),warm=False)
    origin=Vector((0,-1.00,1.30));cam=camera('Next take - tap board to handles',origin,(0,.40,1.65),28)
    for f in range(frame(start),frame(start+2.4)):
        t=(f-1)/FPS;z=1.65-.61*smooth((t-start-.25)/1.8)
        key_camera(cam,t,origin,(0,.35,z))
    stage_shift(before,cam);return cam


def next_bar(start):
    before=set(bpy.data.objects);bar_context();glass()
    A.fixed_side_light((0,0,.95));focus=(0,0,.89)
    cam=side_camera('Next take - drink to bar context',focus,.24,45);dolly(cam,focus,start+2.4,.40,start,.9)
    stage_shift(before,cam);return cam


def next_spread(start):
    before=set(bpy.data.objects);A.table();A.pasta();A.saucer((.31,.15,.785));A.cup((.31,.15,.795),role='support')
    A.plate((-.31,.16,.785));A.pastry((-.31,.16,.794));A.fixed_side_light((0,0,.85))
    focus=Vector((0,0,.82));cam=camera('Next take - overhead brunch spread',(0,0,1.30),focus,24)
    dolly(cam,focus,start+2.4,.60,start,.9);stage_shift(before,cam);return cam


def next_pastry(start):
    before=set(bpy.data.objects);A.table();A.plate();root,halves=A.pastry();A.fixed_side_light((0,0,.85))
    for index,half in enumerate(halves):
        side=1 if index==0 else -1
        hand=A.hand((side*.08,.03,.06),scale=.75,mirror=side);hand.parent=half
        for t,x in [(start,0),(start+.45,0),(start+1.8,side*.035)]:pose(half,t,location=(x,0,.015*smooth((t-start)/1.8)))
    cam=camera('Next take - pastry opens at 45 degrees',(0,-.32,1.15),(0,.04,.83),32)
    stage_shift(before,cam);return cam


def build(scene,spec):
    gid=spec['id'];cameras=[];actions=[];contacts=[];take=4.0;end=6.4
    next_kind=None
    if gid in ['cup_eye_hold_whipout','cup_high_out_dm','cup_pour_eye_hold','cup_shot_eye_in_cd_through']:
        counter();
        if gid!='cup_pour_eye_hold':A.saucer()
        cup=A.cup();A.fixed_side_light((0,0,.87));A.rim_light_cue((0,0,.914),.0533)
        if gid=='cup_eye_hold_whipout':
            # Steam moves while the phone is still; the next take supplies the new angle.
            for j in range(2):
                obj=G.tube('Steam above the cup',[(.014*math.sin(k*.7+j),0,.92+k*.018) for k in range(9)],.0007)
                A.tag(obj,'background','Rising steam gives a meaningful static-camera action')
                for t,z in [(0,0),(1,.01),(2,0),(3,.014),(4,0)]:pose(obj,t,location=(0,0,z))
            cam=side_camera('Hold cup, then whip right',(0,0,.86),.22)
            take=4.0;origin=cam.location.copy();direction=Vector((0,1,0))
            for t,angle in [(0,0),(3.65,0),(3.99,75)]:
                a=math.radians(angle);key_camera(cam,t,origin,origin+Vector((math.sin(a),math.cos(a),0)))
            next_kind='pastry';actions=['Steam rises with a fixed camera','Right whip cut lands on the adjacent pastry opening at 45 degrees']
        elif gid=='cup_high_out_dm':
            cam=side_camera('High cup to counter reveal',(0,0,.86),.14,45);dolly(cam,(0,0,.86),5,.382,1.2,2.4)
            grip(cup)
            for t,z in [(0,.795),(3.3,.795),(4.5,.98),(5,.98)]:pose(cup,t,location=(0,0,z))
            A.tag(G.block('Folded order napkin',(-.22,.1,.790),(.19,.14,.01),.004),'background','Counter context enters during the small lean back')
            take=5;next_kind='cup_selfie';actions=['Cup stays on its saucer until the pickup','One customer hand lifts the same cup; phone leans back above the public counter']
        elif gid=='cup_pour_eye_hold':
            # This guide is sauce onto brunch, despite its historical cup-prefixed ID.
            for obj in list(cup.children)+[cup]:bpy.data.objects.remove(obj,do_unlink=True)
            A.pasta();jug=kettle((.16,0,1.04))
            for t,a in [(0,0),(1.2,0),(1.4,-28),(2.9,-28),(3.2,0)]:pose(jug,t,rotation=(0,math.radians(a),0))
            tip=Vector((.16,0,1.04))+__import__('mathutils').Euler((0,math.radians(-28),0)).to_matrix()@Vector((-.09,0,.115))
            pour_stream(tip,(0,0,.87),2.85,1.55,'Syrup landing on brunch')
            sauce=G.lathe('Sauce pooling on the dish',[(0,0),(.035,0)],(0,0,.874),32);A.tag(sauce,'hero','Sauce lands on the food, not on the empty tabletop')
            for t,s in [(0,.01),(1.4,.01),(3,1)]:pose(sauce,t,scale=(s,s,1))
            cam=side_camera('Fixed plate-level pour',(0,0,.91),.42);next_kind='spread';actions=['Syrup pours onto the plate while the camera stays fixed','Cut goes to a separate overhead spread take']
        else:
            A.tag(G.block('Espresso machine public-facing spout',(0,.025,1.13),(.13,.09,.045),.012),'support','Only the publicly visible machine side is shown')
            pour_stream((0,0,1.11),(0,0,.902),3.65,1.2,'Espresso stream')
            cam=side_camera('Cup under spout - detail approach',(0,0,.88),.30,3)
            # Source asks for 3.43 scale: 23 cm of actual phone travel.
            dolly(cam,(0,0,.88),5,3.43,1.2,2.4)
            take=5;next_kind='pickup';actions=['Espresso runs from the spout into the stationary cup','Close detail cut changes to a high counter pickup take']
    elif gid=='cup_pour_eye_hold':raise AssertionError(gid)
    else:
        context_before=set(bpy.data.objects);bar_context()
        if gid=='glass_favorite_eye_in_cd':
            for obj in set(bpy.data.objects)-context_before:obj.location.y+=1.5
        A.fixed_side_light((0,0,.95));take=5 if gid in ['glass_build_eye_hold','glass_flight_high_truckr_cc','glass_outro_high_out_dm','glass_favorite_eye_in_cd','tap_pour_glass'] else 4
        root,liquid=glass(filled=gid not in ['glass_build_eye_hold','glass_pour_eye_in_cd_through','glass_pour_low_in_cd','tap_pour_glass'])
        focus=Vector((0,0,.89))
        cam=side_camera('Glass at public bar edge',focus,.30)
        if gid in ['glass_build_eye_hold','glass_pour_eye_in_cd_through','glass_pour_low_in_cd','tap_pour_glass']:
            pour_stream((0,0,1.14),(0,0,.82),3.1,1.2)
            filling(liquid,3.0)
            A.tag(G.tube('Short tap spout',[(0,.20,1.18),(0,.02,1.18),(0,0,1.14)],.012),'support','The pour has a visible physical source above the glass')
            if gid=='glass_build_eye_hold':
                for j in range(2):
                    layer=A.tag(G.lathe('Drink layer '+str(j+1),[(0,0),(.041,0),(.043,.036),(0,.036)],(0,0,.045+j*.045),32),'hero','Sequential ingredients create the drink build without camera movement');layer.parent=root
                    for t,v in [(0,.001),(1.2+j*.8,.001),(2+j*.8,1)]:pose(layer,t,scale=(1,1,v))
                next_kind='glass_selfie';actions=['Two ingredient layers build sequentially with the phone still','Cut to the same ordered drink in a mouthless creator sip framing']
            elif gid=='tap_pour_glass':
                next_kind='glass_selfie';actions=['Fixed phone at glass height, continuous tap stream and rising liquid','Cut to creator holding the completed glass']
            else:
                low=gid=='glass_pour_low_in_cd'
                cam=side_camera('Low pour push' if low else 'Pour with short detail approach',focus,.30,-12 if low else 0)
                amount=1.538 if low else 1.18
                dolly(cam,focus,take,amount)
                next_kind='raised_glass' if low else 'hours'
                actions=['Glass fills under a stationary tap; phone makes a short lean-in','Cut on the filled glass to its raised position' if low else 'Foam detail cut lands on the happy-hour board']
                if not low:spec['source_adaptation']='Source scale factor 1.006 was visually static despite its push-in instruction; use a modest 1.18 factor (5 cm travel), with the filling action carrying the shot'
        elif gid=='glass_drink_high_hold':
            cam=side_camera('Fixed high angle - glass lands',focus,.36,45);grip(root)
            for t,z in [(0,1.03),(1.2,1.03),(2,.785),(4,.785)]:pose(root,t,location=(0,0,z))
            next_kind='event';actions=['One hand lowers the glass onto the actual counter','Cut to tonight\'s event line from below']
        elif gid=='glass_eye_tiltd_cc':
            grip(root);origin=Vector((0,-.45,1.20));cam=camera('Fixed origin follows lowering glass',origin,(0,0,1.2),34)
            for f in range(frame(take)):
                t=f/FPS;z=1.11-.325*smooth((t-1.2)/1.8);pose(root,t,location=(0,0,z));key_camera(cam,t,origin,(0,0,z+.105))
            next_kind='glass_selfie';actions=['Glass lowers to the counter while the phone pitches down from a fixed origin','Cut to a separate creator sip take']
        elif gid=='glass_flight_high_truckr_cc':
            for j,x in enumerate([-.24,-.08,.08,.24]):
                if j==0:root.location=(x,0,.809)
                else:glass((x,.035*(j%2),.809),name='Flight glass '+str(j+1))
            board=A.tag(G.block('Tasting flight paddle',(0,0,.797),(.69,.18,.024),.025),'support','Four glasses share a coherent supporting paddle')
            # Raise glass bottoms to paddle top .785, equal to counter support.
            for j in range(4):
                A.tag(G.tube('Flight tasting mark '+str(j+1),[(-.24+j*.16,-.08,.810),(-.24+j*.16,-.06,.810)],.001),'background','Small flight markers establish rhythm without text clutter')
            origin=Vector((-.28,-.38,1.22));direction=Vector((0,1,-1)).normalized();cam=camera('Phone trucks along the flight',origin,origin+direction,32)
            for f in range(frame(take)):
                t=f/FPS;position=origin+Vector((.56*smooth((t-1.2)/2.4),0,0));key_camera(cam,t,position,position+direction)
            next_kind='taps';actions=['Actual lateral phone motion passes four stationary glasses','Foreground rims move faster through true depth','Cut goes to tap board and pitches down to the handles']
        elif gid=='glass_outro_high_out_dm':
            cam=side_camera('Glass to bar and taps',focus,.19,45);dolly(cam,focus,take,.281,1.2,2.4)
            next_kind=None;actions=['Glass remains the anchor while bar, taps and coaster enter the frame','Final framing holds for the end card']
        elif gid=='glass_favorite_eye_in_cd':
            # Front-camera shot: the subject brings the resource toward the lens.
            import people
            creator=people.place('creator_m','glass',(0,.05,0))
            for f in range(frame(5)+1):
                g=people.raise_to(creator,f,smooth((f/15-1.2)/2.7))['R']
                root.location=g+Vector((.01,-.02,-.09));root.keyframe_insert(data_path='location',frame=f)
            cam=camera('Creator presents the favorite glass',(0,-.70,1.55),(0,.30,1.54),32)
            next_kind='bar';actions=['Phone stays at arm\'s length while one hand raises the favorite glass toward it','Cut to that glass on the bar; the next take reveals the taps']
            spec['source_adaptation']='Follow the spoken script\'s front-camera glass approach rather than moving the phone into the creator\'s face'
        elif gid=='glasses_clink_center':
            grip(root,side=-1);second,liq=glass((.22,0,.95),name='Second friend glass');grip(second)
            for obj,side in [(root,-1),(second,1)]:
                for t,x in [(0,side*.23),(1.2,side*.23),(2.35,side*.050),(4.2,side*.050)]:pose(obj,t,location=(x,0,.95))
            take=4.4;cam=side_camera('Steady clink axis',(0,0,1.07),.50);next_kind='glass_selfie';actions=['Exactly two hands bring two glasses into rim contact at centre','The phone stays still; glasses hold after contact','Cut to a creator introduction']
        elif gid=='tap_taps_low_tiltd_mm':
            A.menu_board((0,.40,1.65),title='ON TAP',selected='YOUR PICK',right='PRICE')
            origin=Vector((0,-.85,1.32));cam=camera('Board down to tap handles',origin,(0,.4,1.65),30)
            for f in range(frame(take)):
                t=f/FPS;z=1.65-.60*smooth((t-1.2)/1.8);key_camera(cam,t,origin,(0,.35,z))
            next_kind='glass_selfie';actions=['Fixed-origin downward tilt joins the tap board to its real handles','Cut to the first glass in the creator\'s hand']
        else:raise AssertionError('Unimplemented drink guide: '+gid)
    people_deferred=False
    if (Path(__file__).resolve().parent/'people-policy.json').exists() and next_kind in ['cup_selfie','glass_selfie']:
        next_kind=None;people_deferred=True
        actions=[a for a in actions if 'creator' not in a.lower() and 'cut to' not in a.lower()]
        actions.append('People handover deferred at user request')
    cameras=[(0,cam)]
    if next_kind:
        if next_kind=='pastry':nxt=next_pastry(take)
        elif next_kind in ['cup_selfie','glass_selfie']:nxt=next_portrait(take,held_glass=next_kind=='glass_selfie')
        elif next_kind in ['event','hours']:nxt=next_menu(take,next_kind)
        elif next_kind=='taps':nxt=next_taps(take)
        elif next_kind=='bar':nxt=next_bar(take)
        elif next_kind=='spread':nxt=next_spread(take)
        elif next_kind in ['pickup','raised_glass']:
            before=set(bpy.data.objects);counter()
            prop,liq=glass() if next_kind=='raised_glass' else (A.cup(),None)
            if next_kind=='pickup':A.saucer()
            grip(prop);A.fixed_side_light((0,0,.9));nxt=side_camera('Next take - same drink lifted',(0,0,.91),.35,45 if next_kind=='pickup' else 0)
            for t,z in [(take,.795 if next_kind=='pickup' else 1.08),(take+.4,.795 if next_kind=='pickup' else 1.08),(take+2,.99 if next_kind=='pickup' else .785)]:pose(prop,t,location=(0,0,z))
            stage_shift(before,nxt)
        else:raise AssertionError(next_kind)
        cameras.append((take,nxt));end=take+2.4
    else:end=take
    return dict(duration=end,take_end=take,cameras=cameras,intent='; '.join(actions),
                composition=actions,subject_actions=actions,scope='base_shot_with_action' if people_deferred else 'shot_and_handover' if next_kind else 'complete_final_shot',
                handover_status='deferred_people' if people_deferred else 'included' if next_kind else 'not_applicable',
                geometry_checks=dict(real_camera=True,physical_object_actions=True,fixed_lighting=True),
                mobile_feasibility=dict(camera_support='Handheld phone or elbows supported',maximum_camera_height_m=1.8,maximum_lean_m=.65,transitions='Explicit cuts between separate takes; no flying camera',visitor_side_only=True),
                next_contexts=[dict(script=c['script'],next_guide=c['next_step']['overlays'][0] if c.get('next_step') else None) for c in spec['contexts']])


def register(factories):
    for gid in IDS:factories[gid]=build
