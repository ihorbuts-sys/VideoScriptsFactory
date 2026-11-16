"""Shots that need real people, built with the CC0 MakeHuman cast instead of the schematic bust."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
import assets as A
import geometry as G
import venue_assets as V
import food_assets as F
import shot_motion as M
import people
import real_hands
from drink_scenes import pose,counter,camera,key_camera,smooth,frame


def head(root):
    """Centre of the skull: a little above and behind the eyes."""
    return people.landmark(root,'eyes')+root.matrix_world.to_3x3()@Vector((0,.07,.06))


def held(root,obj,side,frames,u,offset=(0,0,0)):
    """Keys `obj` at the raising hand's grip for each frame, with the raise following u(t)."""
    for f in frames:
        g=people.raise_to(root,f,u(f/15))[side]
        obj.location=g+Vector(offset);obj.keyframe_insert(data_path='location',frame=f)


def up_and_down(start,rise,hold,fall):
    return lambda t:smooth((t-start)/rise)-smooth((t-start-rise-hold)/fall)


def salon_before(scene,spec):
    # Client in the styling chair from behind, a door edge in the foreground; the mirror shows the face. The chair swivels a little.
    station=V.salon_station((0,0,0),0,sitter=('creator_f','seated'));mirror=station['mirror']
    swivel=A.empty('Swivelling chair and client')
    station['chair'].parent=swivel;station['sitter'].parent=swivel
    for t,a in [(0,0),(1.2,0),(2.6,18),(3.8,18),(5,0)]:pose(swivel,t,rotation=(0,0,math.radians(a)))
    V.pendant((0,-.2,2.85));V.pendant((.9,.6,2.85))
    V.tag(G.block('Doorway edge in the foreground',(.58,.80,1.05),(.10,.10,2.1),.01),'foreground_frame','A door edge in the foreground frames the station')
    target=mirror+Vector((0,0,1.20))
    # The slide stays on one side of the mirror axis so the camera never turns through straight ahead.
    cam=camera('Behind the chair, past the door edge',(.40,1.05,1.40),target,30)
    for t,x in [(0,.40),(1.2,.40),(4.4,.12),(5,.12)]:key_camera(cam,t,(x,1.05-.10*smooth((t-1.2)/3.2),1.40),target)
    return dict(custom=cam,focus=target,span=.9,down=10,actions=['The client sits in the styling chair; the mirror shows the face before the cut','The chair swivels a little to show the back of the hair while the phone slides past the door edge'])


def host(scene,spec,person,board):
    counter();A.menu_board((.55,.55,1.55),title=board,selected='RECEPTION' if board=='WELCOME' else 'TODAY',right='')
    root=people.place(person,'glass',(0,.75,0))
    for f in range(frame(5)+1):people.raise_to(root,f,up_and_down(1.2,.9,1.4,.9)(f/15))
    eyes=people.landmark(root,'eyes');span=.57
    return dict(focus=eyes-Vector((0,0,.267*span)),span=span,down=5,actions=['Behind the counter, the person answers with one explaining gesture','The phone holds at chest height; the gesture keeps the hold alive'])


def baker_answer(scene,spec):
    # The baker answers by holding up the croissant they recommend.
    plan=host(scene,spec,'creator_m','TODAY')
    root=next(o for o in bpy.data.objects if o.name.startswith('Person placement creator_m_glass'))
    croissant,_=A.pastry((0,0,0));croissant.scale=(.8,)*3
    for f in range(frame(5)+1):
        g=people.raise_to(root,f,up_and_down(1.2,.9,1.4,.9)(f/15))['R']
        croissant.location=g+Vector((-.05,-.07,-.11));croissant.keyframe_insert(data_path='location',frame=f)
    plan['actions']=['Behind the counter, the baker holds up the croissant they recommend','The phone holds at chest height while the answer is given']
    return plan


def reveal(scene,spec):
    root=people.place('creator_f','stand',eyes_at=(0,-.078,1.646))
    span=.30 if gid_close(spec) else .57
    cloth=V.tag(G.block('Lens-covering cape' if not gid_close(spec) else 'Palm over the lens',(0,0,0),(.60,.025,.65),.03),'foreground_frame','Only the required occluder is drawn; the phone remains still')
    return dict(focus=Vector((0,-.02,1.646-.267*span)),span=span,down=15,fixed=True,occluder=cloth,landmarks=eye_line(root),actions=['The occluder slides off the fixed phone and the finished look appears','Same framing as the before shot'])


def gid_close(spec):return spec['id'].endswith('_cc')


def orbit(scene,spec):
    person='creator_m' if 'blend' in spec['id'] else 'creator_f'
    V.chair((0,0,0),0,salon=True);root=people.place(person,'seated',(0,0,0))
    focus=head(root)
    source=json.loads((Path(__file__).resolve().parents[2]/'guides/templates'/(spec['id']+'.json')).read_text())
    arc=next(s.get('arc',70) for s in source['live']['steps'] if s.get('action')=='orbit')
    cam=camera('Rear hair orbit',focus+Vector((0,.34,.24)),focus,42)
    for f in range(frame(5)):
        t=f/15;angle=math.radians(-arc/2+arc*smooth((t-1.2)/2.4));key_camera(cam,t,focus+Vector((.34*math.sin(angle),.34*math.cos(angle),.24)),focus)
    return dict(custom=cam,focus=focus,span=.30,down=25,actions=['A rear orbit shows the cut from ear to ear','The camera stays behind the client'])


def clipper(scene,spec):
    V.chair((0,0,0),math.pi/2,salon=True);root=people.place('creator_m','seated',(0,0,0),math.pi/2)
    centre=head(root);side=Vector((0,-1,0))
    rig=A.empty('Clipper hand',centre+side*.085+Vector((0,0,-.06)))
    tool=F.tool('clippers',(0,0,0));tool.parent=rig;tool.rotation_euler=(math.radians(-90),0,0)
    hand=real_hands.place('pinch','R',target=(0,-.035,-.03),forward=(0,0,1),normal=(0,-1,0),anchor='grip');hand.parent=rig
    for t,z in [(0,-.06),(1.2,-.06),(3.4,.05),(4.2,.05),(5,-.06)]:pose(rig,t,location=centre+side*.085+Vector((0,0,z)))
    return dict(focus=centre,span=.45,down=0,actions=['The clipper climbs the side of the head in the barber hand','The phone holds still at eye level'])


def hair_work(scene,spec):
    # No person: a cape, a lock of hair, scissors in one hand, and cut hair falling onto the cape and floor.
    A.tag(G.lathe('Client cape over the shoulders',[(0,1.32),(.10,1.31),(.30,1.18),(.42,.95),(.44,.75)],(0,0,0),48),'support','The cape catches the cut hair')
    strands=[]
    for k in range(14):
        x=-.04+k*.006;s=A.tag(G.tube('Lock of hair',[(x,.02,1.62),(x+.004,.015,1.56),(x-.002,.01,1.50)],.0011),'hero','The lock being cut');strands.append(s)
    hand_rig=A.empty('Scissor hand',(.09,-.02,1.53))
    # Blades point at the lock (-X); the hand holds the finger loops behind them.
    tool=F.tool('scissors',(0,0,0));tool.parent=hand_rig;tool.rotation_euler=(0,0,math.radians(-90))
    hand=real_hands.place('pinch','R',target=(.06,0,0),forward=(-1,0,0),normal=(0,0,-1),anchor='grip');hand.parent=hand_rig
    for t,x in [(0,.09),(1.2,.09),(2.0,.02),(2.4,.02),(3.0,.09),(5,.09)]:pose(hand_rig,t,location=(x,-.02,1.53))
    for k in range(10):
        a=k*2.3;start=Vector((-.03+k*.007,.01,1.50));land=Vector((.25*math.cos(a),.25*math.sin(a),.55 if k%2 else .02))
        cut=A.tag(G.tube('Cut hair falling',[(0,0,0),(.006,.002,-.03),(.002,0,-.06)],.0009),'hero','Cut pieces fall after the snip');cut.location=start
        for t,p,r in [(0,start,0),(2.2,start,0),(3.2+k*.06,start.lerp(land,.55)+Vector((0,0,.05)),1.2),(4.0+k*.05,land,2.6),(5,land,2.6)]:pose(cut,t,location=tuple(p),rotation=(r,0,r*.6))
    for k in range(18):
        a=k*1.7;A.tag(G.tube('Cut hair on the floor',[(.35*math.cos(a),.35*math.sin(a),.002),(.35*math.cos(a)+.03,.35*math.sin(a)+.01,.002)],.0009),'support','Earlier clippings lie on the floor')
    return dict(focus=Vector((0,.01,1.48)),span=.40,down=20,actions=['Scissors in one hand snip the lock; the cut hair falls onto the cape and floor','The phone eases in over the cape'])


def rep(scene,spec):
    root=people.place('creator_m','curl',(0,0,0))
    bells=[]
    for side in 'LR':bells.append((side,V.dumbbell((0,0,0))));bells[-1][1].scale=(.45,)*3
    cycle=lambda t:up_and_down(1.2,.8,.2,.8)(t)+up_and_down(3.2,.8,.2,.8)(t)
    for f in range(frame(5)+1):
        grips=people.raise_to(root,f,cycle(f/15))
        for side,bell in bells:
            bell.location=grips[side]+Vector((0,0,-.02));bell.keyframe_insert(data_path='location',frame=f)
    return dict(focus=Vector((0,0,1.0)),span=1.25,down=-8,actions=['Two dumbbell curls from the hip to the shoulder','The phone is propped low and holds still'])


def outfit(scene,spec):
    root=people.place('creator_f','stand',(0,0,0))
    for t,a in [(0,0),(1.2,0),(3,35),(4.3,-25),(5,0)]:pose(root,t,rotation=(0,0,math.radians(a)))
    return dict(focus=Vector((0,0,1.0)),span=1.25,down=-8,actions=['The person turns once to show the outfit','The phone holds; feet stay on the floor'])


def barista(scene,spec):
    counter();A.menu_board((.35,.65,1.65),title='MENU',selected='YOUR PICK',right='PRICE')
    V.tag(G.block('Public coffee machine',(0,.45,1.04),(.45,.28,.48),.04),'support','Machine seen from the visitor side')
    A.cup((0,.05,.795));A.saucer((0,.05,.785))
    people.place('creator_m','work',(-.42,.66,0),-math.pi/2)
    return dict(focus=Vector((0,.15,1.08)),span=.95,down=10,actions=['The barista works at the machine in profile','The phone holds, then walks in toward the hands'])


def till(scene,spec):
    counter();A.menu_board((.35,.65,1.65),title='RECEIPT',selected='TOTAL',right='PRICE')
    V.tag(G.block('Public till',(.45,.45,1.04),(.30,.24,.30),.03),'support','The till faces the customer')
    people.place('queue_c','work',(.26,-.32,0),math.pi,role='foreground_frame',reason='The shopper at the till frames the shot from behind')
    return dict(focus=Vector((.50,.65,1.705)),span=1.25,down=10,actions=['Over the shopper shoulder, the total on the till grows in frame','The phone stays on the customer side'])


def stylist(scene,spec):
    station=V.salon_station((0,.30,0),math.pi,sitter=('creator_f','seated'))
    hands=people.place('creator_m','work',(.30,-.22,0),math.pi,role='foreground_frame',reason='The stylist shoulder frames the shot from behind')
    F.tool('scissors',tuple(people.landmark(hands,'grip_R')+Vector((0,.03,.02))))
    return dict(focus=head(station['sitter']),span=.48,down=20,actions=['Over the stylist shoulder, the scissors work at the client hair','The mirror ahead shows the client'])


def guitar_in_hands(root):
    """Hangs the CC0 guitar across a person in the guitar pose: body at the strumming hand, neck toward the fretting hand."""
    body=people.landmark(root,'grip_R')+Vector((-.06,-.05,-.04));neck=people.landmark(root,'grip_L')
    guitar=V.guitar((0,0,0))
    z=(neck-body).normalized();y=Vector((0,1,0));y=(y-z*y.dot(z)).normalized();x=y.cross(z)
    guitar.matrix_world=Matrix.Translation(body-Matrix((x,y,z)).transposed()@Vector((0,0,.30*.70)))@Matrix((x,y,z)).transposed().to_4x4()@Matrix.Scale(.70,4)
    for obj in guitar.children_recursive:
        if obj.type=='MESH' and obj.get('composition_role')!='hero':A.tag(obj,'support','Played instrument')
    return guitar


def player(scene,spec):
    guitar_in_hands(people.place('creator_m','guitar',(0,.30,0)))
    return dict(focus=Vector((0,.15,1.05)),span=.80,down=0,actions=['From the hands on the strings the player and guitar appear','A short pull-back'])


PORTRAIT_EYES=Vector((0,-.078,1.646))


def portrait_focus(spec,span):
    return PORTRAIT_EYES-Vector((0,0,.267*span)),22 if '_high_' in spec['id'] else 15


def eye_line(root):
    # Close portraits frame the face, so the eye line, not the whole body, is the framing landmark.
    mark=A.ellipsoid('Eye line landmark',tuple(people.landmark(root,'eyes')),(.01,.01,.01));mark.hide_render=True
    return [mark.name]


def sway(root,amount=2):
    for t,a in [(0,0),(1.2,0),(2.5,amount),(3.5,-amount),(5,0)]:pose(root,t,rotation=(0,0,math.radians(a)))


def talking(scene,spec):
    root=people.place('creator_f','selfie',eyes_at=PORTRAIT_EYES);sway(root)
    span=.30 if 'close' in spec['id'] else .57;focus,down=portrait_focus(spec,span)
    return dict(focus=focus,span=span,down=down,landmarks=eye_line(root),actions=['The creator talks to the front camera, eyes near the upper third','A small natural head movement keeps the hold alive'])


def pair(scene,spec):
    a=people.place('creator_f','selfie',eyes_at=(-.16,-.078,1.646));b=people.place('creator_m','stand',eyes_at=(.18,-.03,1.62))
    sway(a,1.5);sway(b,-1.5);focus,down=portrait_focus(spec,.70)
    return dict(focus=focus,span=.70,down=down,landmarks=eye_line(a)+eye_line(b),actions=['Two faces share the frame at arm length','Both stay in frame while they talk'])


def group(scene,spec):
    roots=[people.place(p,'stand',eyes_at=(x,-.05,z)) for p,x,z in [('queue_b',-.42,1.58),('creator_m',0,1.65),('queue_c',.42,1.62)]]
    for root,amount in zip(roots,[3,-2,2.5]):sway(root,amount)
    focus,down=portrait_focus(spec,1.25)
    return dict(focus=focus,span=1.25,down=down,landmarks=sum([eye_line(r) for r in roots],[]),actions=['The group reacts together, held still','Each face keeps headroom and separation'])


def raise_to_mouth(scene,spec,item):
    root=people.place('creator_m','glass',eyes_at=PORTRAIT_EYES)
    if item=='cup':thing=A.cup((0,0,0),name='Held cup');offset=Vector((.01,-.03,-.01))
    else:
        thing=A.fork((0,0,0),role='hero');offset=Vector((0,-.05,.0))
        A.ellipsoid('Bite on the fork',(0,.025,.012),(.016,.016,.014),'hero','One bite stays on the fork').parent=thing
    gid=spec['id']
    if gid.endswith('_out_cm'):u=lambda t:1-smooth((t-1.2)/2.0)
    elif gid.endswith('_reaction'):u=up_and_down(1.2,1.2,.8,1.0)
    else:u=lambda t:smooth((t-1.2)/2.0)
    held(root,thing,'R',range(frame(5.5)+1),u,offset)
    span=.57;focus,down=portrait_focus(spec,span)
    return dict(focus=focus,span=span,down=down,fixed=True,landmarks=eye_line(root),actions=['One hand brings the '+('cup' if item=='cup' else 'fork and bite')+' up to the mouth','The phone holds at arm length while the creator reacts'])


def shoulder(scene,cam,person):
    """A real person just ahead and left of the opening camera, back to the lens, so the shot is over their shoulder."""
    scene.frame_set(1);bpy.context.view_layer.update()
    p=cam.matrix_world.translation;d=cam.matrix_world.to_3x3()@Vector((0,0,-1));d.z=0;d.normalize();left=Vector((-d.y,d.x,0))
    position=p+d*.45+left*.32;position.z=0
    return people.place(person,'stand',tuple(position),math.atan2(d.x,-d.y),role='foreground_frame',reason='The shoulder in front of the lens frames the view')


def bench(scene,spec):
    # Counter-height bench so the standing owner's working hands rest on the workpiece.
    V.tag(G.block('Public repair bench',(0,.2,.93),(1.2,.60,.04),.01),'structure');V.tag(G.block('Repair object',(0,.15,.97),(.20,.28,.03),.015),'hero')
    owner=people.place('creator_m','bench',(0,.58,0))
    F.tool('brush',tuple(people.landmark(owner,'grip_R')+Vector((0,-.04,0))))
    return dict(shoulder='queue_a' if spec['id'].startswith('over_shoulder') else None,focus=Vector((0,.15,1.02)),span=.70,down=10,actions=['The owner works at the bench with the tool on the workpiece','The phone stays on the visitor side of the bench'])


def machine(scene,spec):
    counter();A.menu_board((.35,.65,1.65),title='MENU',selected='YOUR PICK',right='PRICE')
    V.tag(G.block('Public coffee machine',(0,.45,1.04),(.45,.28,.48),.04),'support','Machine seen from the visitor side')
    A.cup((0,.05,.795));A.saucer((0,.05,.785))
    sway(people.place('creator_m','work',(.12,.98,0)),8)
    plan=dict(shoulder='queue_a',focus=Vector((0,.30,1.15)),span=.95,down=10)
    plan['actions']=['From behind a shoulder, the barista works at the machine','The phone holds on the visitor side'];return plan


def menu(scene,spec):
    counter();A.menu_board((.35,.65,1.65),title='MENU',selected='YOUR PICK',right='PRICE')
    return dict(shoulder='creator_f',focus=Vector((.35,.65,1.65)),span=.75,down=10,actions=['Over the creator shoulder, the menu grows in frame','The phone pushes in to the chosen line'])


def rail(scene,spec):
    V.rack('garment',(0,.65,0));hand=F.pointing_hand((.15,.20,1.25))
    for t,y in [(0,.20),(1.2,.20),(2.8,.50),(4,.30)]:pose(hand,t,location=(.15,y,1.25))
    return dict(shoulder='creator_m',focus=Vector((0,.65,1.25)),span=.95,down=10,actions=['Over the shoulder, the owner hand finds the piece on the rail','Neighbouring pieces stay on the rail'])


def curtain(scene,spec):
    root=people.place('creator_f','stand',(0,0,0))
    for t,a in [(0,0),(1.2,0),(3,35),(4.3,-25),(5,0)]:pose(root,t,rotation=(0,0,math.radians(a)))
    for side in [-1,1]:
        cloth=V.tag(G.block('Necessary changing curtain',(side*.26,-.30,1.05),(.52,.025,2.0),.02),'foreground_frame','The curtain is the occluder for this reveal')
        for t,x in [(0,side*.26),(1.2,side*.26),(2.7,side*.90),(5,side*.90)]:pose(cloth,t,location=(x,-.30,1.05))
    return dict(focus=Vector((0,0,1.0)),span=1.25,down=-8,actions=['The curtain slides away and the outfit appears','The person turns once while the phone is propped low'])


SHOTS={'before_front_back':salon_before,'person_host_eye_whip_mm':lambda s,p:host(s,p,'creator_f','WELCOME'),
       'person_one_eye_hold':lambda s,p:host(s,p,'creator_m','TODAY'),
       'selfie_reveal_eye_reveal_cc':reveal,'selfie_reveal_eye_reveal_cm':reveal,
       'hair_blend_high_orbitr_cc':orbit,'hair_signature_high_orbitr_cc':orbit,'person_barber_eye_hold':clipper,
       'hair_work_high_in_cd_through':hair_work,'person_full_low_hold':rep,
       'person_mirror_eye_hold':outfit,'person_mirror_eye_out_cm':outfit,'counter_barista_side':barista,
       'over_shoulder_till_os_in_md':till,'over_shoulder_hands_os_in_mc':stylist,'person_player_eye_out_dm':player,
       'talking_head_eye_level':talking,'selfie_close_eye_hold':talking,'selfie_close_high_hold':talking,
       'selfie_two_eye_hold':pair,'selfie_two_high_hold':pair,'person_group_eye_hold':group,
       'selfie_sip_eye_in_mc':lambda s,p:raise_to_mouth(s,p,'cup'),'selfie_sip_reaction':lambda s,p:raise_to_mouth(s,p,'cup'),
       'selfie_bite_eye_in_mc':lambda s,p:raise_to_mouth(s,p,'fork'),'selfie_bite_eye_out_cm':lambda s,p:raise_to_mouth(s,p,'fork'),
       'selfie_bite_reaction':lambda s,p:raise_to_mouth(s,p,'fork'),'over_shoulder_hands_os_in_cd':bench,'table_bench_eye_out_dw':bench,
       'over_shoulder_machine_os_hold':machine,'over_shoulder_menu_os_in_mc':menu,'over_shoulder_rail_os_hold':rail,
       'person_curtain_low_reveal_dm':curtain}


def build(scene,spec,shot=None):
    plan=(shot or SHOTS[spec['id']])(scene,spec)
    A.fixed_side_light(plan['focus'])
    sequence=M.apply(scene,spec,plan['focus'],plan['span'],plan['down'])
    if plan.get('custom') is not None:sequence['cameras']=[(0,plan['custom'])]
    if plan.get('shoulder'):shoulder(scene,sequence['cameras'][0][1],plan['shoulder'])
    elif plan.get('fixed'):
        cam=sequence['cameras'][0][1];scene.frame_set(1);p=cam.location.copy();cam.animation_data_clear();key_camera(cam,0,p,plan['focus'])
        if plan.get('occluder'):
            # The occluder starts a few centimetres in front of the lens and slides off sideways.
            near=p+(plan['focus']-p).normalized()*.06
            for t,x in [(0,0),(1.2,0),(2.8,.80),(5,.80)]:pose(plan['occluder'],t,location=tuple(near+Vector((x,0,0))))
    actions=plan['actions']
    if plan.get('landmarks'):sequence['framing_landmarks']=plan['landmarks']
    sequence.update(intent='; '.join(actions),composition=actions,subject_actions=actions,geometry_checks=dict(family='people',variant=spec['id']),
                    contextual_next_steps=[dict(script=c['script'],next_step=c['next_step']) for c in spec['contexts']])
    return sequence
