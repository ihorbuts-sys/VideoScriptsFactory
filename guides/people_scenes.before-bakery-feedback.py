"""Mouthless human framing, supported hand actions and accessible service views."""
import math
import json
import bpy
from pathlib import Path
from mathutils import Vector,Matrix
import assets as A
import geometry as G
import venue_assets as V
import food_assets as F
import shot_motion as M
from drink_scenes import pose,counter,glass,grip,camera,key_camera,smooth,frame

REGISTRY={}
def add(ids,family,variant):
    for gid in ids.split():REGISTRY[gid]=(family,variant)
add('before_front_back','portrait','before')
add('talking_head_eye_level selfie_close_eye_hold selfie_close_high_hold selfie_one_high_hold','portrait','hold')
add('selfie_two_eye_hold selfie_two_high_hold','portrait','pair')
add('selfie_bag_high_hold','portrait','bag')
add('selfie_bite_eye_in_mc selfie_bite_eye_out_cm selfie_bite_reaction','portrait','bite')
add('selfie_sip_eye_in_mc selfie_sip_reaction','portrait','sip')
add('selfie_reveal_eye_reveal_cc selfie_reveal_eye_reveal_cm','portrait','reveal')
add('hair_blend_high_orbitr_cc hair_signature_high_orbitr_cc','hair','orbit')
add('hair_work_high_in_cd_through','hair','working')
add('person_barber_eye_hold','hair','clipper')
add('person_curtain_low_reveal_dm','full','curtain')
add('person_full_low_hold','full','rep')
add('person_mirror_eye_hold person_mirror_eye_out_cm','full','outfit')
add('person_group_eye_hold','portrait','group')
add('person_host_eye_whip_mm person_one_eye_hold','portrait','host')
add('person_player_eye_out_dm','service','player')
add('person_process_pov_in_mc_through','service','treatment')
add('counter_barista_side over_shoulder_counter_os_hold over_shoulder_machine_os_hold','service','coffee')
add('over_shoulder_menu_os_in_mc','service','menu')
add('over_shoulder_rail_os_hold','service','rail')
add('over_shoulder_till_os_in_md','service','till')
add('over_shoulder_hands_os_in_cd table_bench_eye_out_dw','service','work')
add('over_shoulder_hands_os_in_mc','service','hair')
add('hand_pov_garment_pov_in_mc hand_pov_item_pov_in_mc hand_pov_pastry_pov_in_mc','hands','choose')
add('hands_dough_top_hold','hands','dough')
add('hands_during_top_hold','hands','rest')
add('hands_garment_high_hold','hands','garment')
add('hands_griddle_high_hold','hands','grill')
add('hands_guitar_high_hold','hands','guitar')
add('hands_high_hold hands_tool_top_hold hands_tool_top_hold_whipout','hands','tool')
add('hands_stance_top_hold','hands','stance')
add('hands_top_hold','hands','plating')
add('hands_work_high_hold hands_work_high_hold_whipout hands_work_high_in_cd','hands','work')
add('hands_wrap_top_hold','hands','box')
add('nails_accent_top_hold nails_tech_pov_hold nails_turns_eye_hold','hands','nails')
add('details_salon_high_whip_dd_whipout','details','salon')


def explicit_review(gid,description,contexts):
    family,variant=REGISTRY[gid]
    subjects={'portrait':'Mouthless creator framing with '+variant+' action','hair':'The hair silhouette, ears and '+variant+' action','full':'Whole-person '+variant+' framing and movement','service':'Visible '+variant+' work, tool and public-side operator context','hands':'Exactly one or two hands performing the '+variant+' action on a supported object','details':'Connected salon details, followed by the real front desk'}
    return dict(subject=subjects[family],angle='Use the source selfie/high/top-down/over-shoulder angle; adapt staff-only viewpoints to the public side',motion='Preserve the filming instruction and actual subject action; prop the phone when the operator needs both hands',focal_point=subjects[family],composition='Keep eyes near the upper third for portraits, hands clear of the object silhouette, and tools visibly attached to the action; quiet surroundings explain context',golden_ratio='Useful headroom, thirds and negative space take priority over decorative ratios; centred gestures and grips retain their axis',lighting='Steady broad side/venue light with no bloom or required light changes; mouthless schematic face',contacts='Hands parent to held tools/resources; elbows/wrists connect to one arm; feet remain on a support during full-body movement',handover='Source next-step identity retained for contextual assembly; shared guide contexts requiring different resources remain explicitly tracked',mobile='Ordinary smartphone at arm length or supported on a bottle/shelf; a helper may hold the phone for two-hand work; no crane or staff-area access',ambiguities=[c['script'] for c in contexts] if len(contexts)>1 else [])


def eyes(actor):
    # Minimal eyes/brows provide a framing landmark; no mouth, lips or teeth.
    for side in [-1,1]:
        for name,z in [('Eye alignment',1.646),('Quiet brow',1.673)]:
            obj=A.tag(G.tube(name,[(side*.035-.014,-.075,z),(side*.035,-.080,z+.002),(side*.035+.014,-.075,z)],.001),'hero','Minimal eye/brow line makes upper-third portrait alignment readable without a mouth')
            obj.parent=actor['root']


def hair(actor):
    before=set(bpy.data.objects)
    vertices=[];faces=[];rings=12;segments=32
    for j in range(rings+1):
        for k in range(segments):
            az=k/segments*math.tau;back=(math.sin(az)+1)/2
            theta=.03+j/rings*(1.22+.60*back)
            vertices.append((.099*math.sin(theta)*math.cos(az),.085*math.sin(theta)*math.sin(az),1.65+.145*math.cos(theta)))
    for j in range(rings):
        for k in range(segments):
            a=j*segments+k;b=j*segments+(k+1)%segments;faces.append((a,b,b+segments,a+segments))
    mesh=bpy.data.meshes.new('Curved hair cap');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('Hair silhouette',mesh);bpy.context.collection.objects.link(obj);G.finish(obj,obj.name)
    A.tag(obj,'hero','A curved hairline and rear volume make an actual orbit legible; no client face is needed')
    for k in range(9):
        az=.1+k*math.pi/8
        points=[(.100*math.sin(t)*math.cos(az),.086*math.sin(t)*math.sin(az),1.65+.146*math.cos(t)) for t in [.15+j*.12 for j in range(12)]]
        A.tag(G.tube('Quiet hair flow',points,.00065),'support','Sparse hair flow reveals surface direction without individual-strand clutter')
    for obj in set(bpy.data.objects)-before:
        if obj.parent is None:obj.parent=actor['root']


def bone(name,radius=.035):
    return A.tag(G.lathe(name,[(0,0),(radius,0),(radius*.75,1),(0,1)],(0,0,0),20),'support','One continuous limb segment connects its two joints')


def stretch(obj,a,b,t):
    a=Vector(a);b=Vector(b);obj.location=a;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=(b-a).to_track_quat('Z','Y');obj.scale=(1,1,(b-a).length)
    for path in ['location','rotation_quaternion','scale']:obj.keyframe_insert(data_path=path,frame=frame(t))


def full_actor(rep=False):
    before=set(bpy.data.objects);actor=A.portrait((0,0,0),None);eyes(actor);hair(actor)
    limbs=[]
    for side in [-1,1]:
        arm=A.tag(G.tube('Connected whole-person arm',[(side*.19,0,1.35),(side*.28,-.06,1.16),(side*.24,-.12,1.02)],.030),'support','Arm connects shoulder, elbow and wrist; the phone is propped for the full-body action');arm.parent=actor['root']
        hand=A.hand((side*.24,-.12,1.01),scale=.85,mirror=side);hand.parent=actor['root']
        thigh=bone('Trouser thigh',.065);shin=bone('Trouser lower leg',.046);limbs.append((side,thigh,shin))
        A.ellipsoid('Grounded shoe',(side*.18,-.055,.045),(.07,.14,.045),'support','Feet remain in contact with the floor plane while the knees and hips move')
    for f in range(frame(5)):
        t=f/15;amount=(.5-.5*math.cos(math.tau*max(0,min(1,(t-1.2)/2.5)))) if rep else 0
        pose(actor['root'],t,location=(0,0,-.25*amount))
        for side,thigh,shin in limbs:
            hip=Vector((side*.09,0,.98-.25*amount));ankle=Vector((side*.18,0,.10));axis=(ankle-hip).normalized();distance=(ankle-hip).length
            length=.49;along=distance/2;perp=Vector((0,-1,0));perp=(perp-axis*perp.dot(axis)).normalized();knee=hip+axis*along+perp*math.sqrt(max(0,length*length-along*along))
            stretch(thigh,hip,knee,t);stretch(shin,knee,ankle,t)
    root=A.group('Whole person rig',before,(0,0,0),'support','Whole-person silhouette and grounded feet make a phone-propped full-body shot feasible')
    return root,actor


def supported_hands(target=(0,0,.85),two=True):
    hands=[]
    for side in ([-1,1] if two else [1]):
        hand=F.pointing_hand((target[0]+side*.10,target[1]+.10,target[2]),side)
        hands.append(hand)
    return hands


def build(scene,spec):
    gid=spec['id'];family,variant=REGISTRY[gid]
    focus=Vector((0,0,.85));span=.50;down=None;actions=[];dynamic=True;custom=None
    if family=='portrait':
        prop='cup' if variant=='sip' else 'fork' if variant=='bite' else None
        actor=A.portrait((0,0,0),prop);eyes(actor);hair(actor)
        focus=Vector((0,-.02,1.57));span=.57 if 'close' not in gid else .30
        down=22 if '_high_' in gid else 0
        if variant in ['sip','bite']:
            for f in range(frame(5.5)):
                t=f/15;u=smooth((t-1.2)/2.0)
                if '_out_' in gid:u=1-u
                wrist=None
                if variant=='bite' and '_out_' in gid:
                    v=smooth((t-1.2)/2.0);wrist=Vector((.03,-.44,1.53)).lerp(Vector((.13,-.10,1.41)),v)
                A.pose_portrait(actor,frame(t),u,wrist)
            if variant=='bite':
                morsel=A.ellipsoid('Bite on the fork',(-.02,-.03,.105),(.018,.018,.017),'hero','One bite stays attached to the fork throughout the approach');morsel.parent=actor['grip']
            actions=['One hand raises the same '+('cup' if variant=='sip' else 'fork and bite')+' while the front camera stays at a practical arm-length angle','Mouthless eyes/brows retain the upper-third framing; the resource is not detached from its grip']
            # It is the resource that approaches. Keep the phone supported rather than requiring two simultaneous tasks.
            custom='portrait_fixed'
        elif variant=='pair' or variant=='group':
            offsets=[-.20,.20] if variant=='pair' else [-.32,0,.32]
            actor['root'].location.x=offsets[0]
            for x in offsets[1:]:
                other=A.portrait((x,0,0),None);eyes(other);hair(other)
            span=.95 if variant=='pair' else 1.25
            actions=['Consenting faces share one readable eye-level grouping','No extra hands enter; each face has headroom and separation']
        elif variant=='reveal':
            cloth=V.tag(G.block('Lens-covering cape',(0,-.35,1.57),(.60,.025,.65),.03),'foreground_frame','Only the required cape occluder is drawn; the phone remains still')
            for t,x in [(0,0),(1.2,0),(2.8,.80),(5,.80)]:pose(cloth,t,location=(x,-.35,1.57))
            actions=['Cape moves away from the fixed phone to reveal the finished head in the same framing','The same head and camera alignment are retained; no fake room truck is added'];custom='portrait_fixed'
        elif variant=='bag':
            bag=V.tag(G.block('Paper order bag',(.17,-.20,1.25),(.18,.10,.24),.014),'support','Bag sits beside the face without hiding the eye line')
            hand=A.hand((.20,-.20,1.38),scale=.85)
            A.tag(G.tube('Bag-holding connected arm',[(.19,0,1.35),(.28,-.10,1.26),(.20,-.20,1.38)],.026),'support','One hand grips the actual bag handle; the forearm connects it to the shoulder')
            G.tube('Paper bag handle',[(.11,-.20,1.37),(.11,-.20,1.44),(.23,-.20,1.44),(.23,-.20,1.37)],.004)
            actions=['Creator, order bag and readable eye line share the frame','Hold the phone steady from slightly above; no decorative camera oscillation']
        else:
            for t,a in [(0,0),(1.2,0),(2.5,10 if variant=='before' else 2),(3.5,-10 if variant=='before' else -2),(5,0)]:pose(actor['root'],t,rotation=(0,0,math.radians(a)))
            if variant=='host':counter();A.menu_board((.50,.50,1.45),title='WELCOME',selected='RECEPTION',right='')
            actions=['Stable mouthless head-and-shoulders framing keeps eyes near the upper third','Small natural head movement makes the hold legible without moving the phone']
    elif family=='hair':
        actor=A.portrait((0,0,0),None);hair(actor);focus=Vector((0,0,1.66));span=.30;down=25
        if variant=='orbit':
            source=json.loads((Path(__file__).resolve().parents[2]/'guides/templates'/(gid+'.json')).read_text())
            arc=next(s.get('arc',70) for s in source['live']['steps'] if s.get('action')=='orbit')
            cam=camera('Rear hair orbit - phone in public client space',(0,.34,1.90),focus,42)
            for f in range(frame(5)):
                t=f/15;angle=math.radians(-arc/2+arc*smooth((t-1.2)/2.4));p=focus+Vector((.34*math.sin(angle),.34*math.cos(angle),.24));key_camera(cam,t,p,focus)
            custom=cam;actions=['Actual rear orbit reveals changing hair shape and ear landmarks','Camera stays on the rear semicircle so no client face is shown']
        else:
            tool=F.tool('clippers' if variant=='clipper' else 'brush',(.10,.02,1.62));hand=A.hand((.02,.05,0),scale=.8);hand.parent=tool
            for t,z in [(0,1.55),(1.2,1.55),(2.8,1.70),(4.2,1.57)]:pose(tool,t,location=(.10,.02,z))
            actions=['One attached hand moves the working end along the hair surface','Phone holds or makes the prescribed short approach from a visitor-accessible client-side angle']
    elif family=='full':
        root,actor=full_actor(rep=variant=='rep');focus=Vector((0,0,1.0));span=1.25;down=-8
        if variant in ['outfit','curtain']:
            cloth=V.garment((0,0,1.1),'hero');cloth.parent=root;cloth.scale=(.62,)*3
            for t,a in [(0,0),(1.2,0),(3,35),(4.3,-25),(5,0)]:pose(root,t,rotation=(0,0,math.radians(a)))
            if variant=='curtain':
                for side in [-1,1]:
                    curtain=V.tag(G.block('Necessary changing curtain',(side*.26,-.30,1.05),(.52,.025,2.0),.02),'foreground_frame','Curtains are required occluders for this outfit reveal; no broad room walls are drawn')
                    for t,x in [(0,side*.26),(1.2,side*.26),(2.7,side*.90),(5,side*.90)]:pose(curtain,t,location=(x,-.30,1.05))
            actions=['The same outfit and full-person silhouette turn while the phone is propped low','A curtain reveals the person before the turn' if variant=='curtain' else 'Clothing seams and grounded feet keep the turn physically coherent']
        else:actions=['A complete squat-like rep uses fixed feet and connected knee/hip joints','Low propped phone keeps the whole person in frame without requiring a camera operator to move']
    elif family=='hands':
        if variant!='stance':A.table(radius=.65)
        down=90 if '_top_' in gid else 45
        if variant=='choose':
            if 'garment' in gid:V.rack('garment',(0,.7,0));focus=Vector((0,.5,1.25));down=10
            elif 'pastry' in gid:V.pastry_case((0,.6,0));focus=Vector((-.26,.6,1.18));down=10
            else:V.rack('bottle',(0,.5,0));focus=Vector((0,.5,1.12));down=10
            # Point of view: fingers reach into the shelf, the forearm enters from the lower right of the frame.
            # A life-size arm needs room: the fingertip starts about 40 cm in front of the phone and ends at the product.
            hand=F.pointing_hand((.10,.30,focus.z-.04),forward=(.35,-.9,.25),normal=(.2,0,-1));hand.rotation_euler.z=math.pi;
            # The fingertip stops just short of the chosen product; the reaching hand is the shot's subject.
            reach=.62 if 'garment' in gid else .44
            x=.10 if 'garment' in gid else .06
            for t,y in [(0,.30),(1.2,.30),(2.6,reach),(4,reach)]:pose(hand,t,location=(x,y,focus.z-.04))
            for obj in hand.children_recursive:
                if obj.type=='MESH':A.tag(obj,'hero','The reaching hand shows which product is chosen')
            span=.65;actions=['One hand reaches toward the chosen supported product','The neighbouring products and shelf remain in place as the phone makes a short POV approach']
        elif variant=='dough':
            dough=A.ellipsoid('Dough being folded',(0,0,.825),(.13,.09,.04),'hero');hands=supported_hands((0,0,.86))
            for side,hand in zip([-1,1],hands):
                for t,x in [(0,side*.11),(1.2,side*.11),(2.0,side*.04),(2.8,side*.11),(4,side*.04)]:pose(hand,t,location=(x,.10,.86))
            for t,s in [(0,(1,1,1)),(1.2,(1,1,1)),(2,(.8,1.2,.9)),(2.8,(1,1,1)),(4,(.8,1.2,.9))]:pose(dough,t,scale=s)
            actions=['Exactly two hands fold a coherent dough volume on its bench support','The phone is propped overhead or held by a helper, never moved by the occupied hands']
        elif variant in ['tool','work']:
            phone=V.tag(G.block('Repair workpiece',(0,0,.799),(.16,.29,.025),.018),'hero','Workpiece lies on the bench; the tool action has a clear target')
            if gid=='hands_work_high_in_cd':
                for points in [[(-.05,-.08,.814),(0,.01,.814),(.04,.10,.814)],[(0,.01,.814),(.07,-.03,.814)]]:V.tag(G.tube('Visible problem crack',points,.0009),'hero','The initial problem is legible before the repair')
            elif variant=='tool':
                tool=F.tool('brush',(.05,0,.83));hand=A.hand((0,.06,.015),scale=.75);hand.parent=tool
                for t,x in [(0,-.04),(1.2,-.04),(2.1,.04),(3,-.04),(4,.04)]:pose(tool,t,location=(x,0,.83))
            F.card((.20,.04,.788),'SERVICE','WORK','',.14,.12);span=.40
            actions=['A supported workpiece, attached tool and single hand identify the task','The source hold or short approach preserves the result/problem comparison; no detached moving parts']
            dynamic=variant=='tool'
        elif variant=='guitar':
            guitar=V.guitar((0,0,.81));guitar.rotation_euler.x=math.pi/2;guitar.scale=(.55,)*3
            for obj in guitar.children_recursive:
                if obj.type=='MESH':A.tag(obj,'hero','Strings and the played instrument are the main subject')
            hands=supported_hands((0,-.20,.87));span=.80
            for index,hand in enumerate(hands):
                for t,z in [(0,.87),(1.2,.87),(1.8,.86),(2.3,.87),(3.1,.86),(4,.87)]:pose(hand,t,location=(.02 if index==0 else -.01,-.18 if index==0 else -.39,z))
            focus=Vector((0,-.20,.85));actions=['Two attached hands fret and pluck the same instrument','Strings, fretboard and curved body make the task identifiable from the supported high phone angle']
        elif variant=='box':
            box,hinge=F.open_box(pastries=False,height=.16)
            burger,_=F.burger((0,0,.016));burger.parent=box
            hand=A.hand((.19,-.015,.30),scale=.8);hand.parent=hinge
            for t,a in [(0,0),(1.2,0),(2.8,90),(4,90)]:pose(hinge,t,rotation=(math.radians(a),0,0))
            span=.70;actions=['One hand closes a lid about its physical hinge around the coherent order','The supported overhead phone shows the whole box and keeps the fingers out of the food silhouette']
        elif variant=='grill':
            V.tag(G.block('Public-side grill surface',(0,0,.81),(.46,.32,.04),.015),'support')
            meat=A.ellipsoid('Cooking portion',(0,0,.85),(.12,.08,.025),'hero')
            for t,s in [(0,(1,1,1)),(1.2,(1,1,1)),(3.5,(.97,1.02,.98))]:pose(meat,t,scale=s)
            for j in range(2):
                steam=V.tag(G.tube('Cooking steam',[(j*.04,0,.88),(j*.04+.01,0,.98),(j*.04-.01,0,1.08)],.0007),'background')
                for t,z in [(0,0),(1.2,.01),(2.6,0),(4,.02)]:pose(steam,t,location=(0,0,z))
            actions=['Cooking surface, food contact and steam are shown from a public viewing side','The camera stays still; do not enter a staff-only griddle area']
        elif variant=='stance':
            for side in [-1,1]:
                foot=A.ellipsoid('Coach shoe',(side*.13,0,.05),(.07,.15,.05),'hero')
                for t,x in [(0,side*.08),(1.2,side*.08),(2.3,side*.15),(4,side*.15)]:pose(foot,t,location=(x,0,.05))
            focus=Vector((0,0,.05));span=.70;actions=['Two feet settle into a stable stance from above','Phone is held above the actor\'s own feet at a natural reachable height']
        elif variant=='nails' or variant=='rest':
            towel=V.tag(G.block('Treatment towel',(0,0,.795),(.48,.34,.02),.025),'background','Neutral towel supports the hand and keeps context faint')
            if variant=='nails':
                # A relaxed hand rests palm-down on the towel; one nail plate sits on the back of each fingertip.
                hand=F.pointing_hand((0,-.02,.828),pose='relaxed',normal=(0,0,-1))
                import real_hands
                for centre,along,back in real_hands.fingertips(hand):
                    nail=A.ellipsoid('Schematic nail plate',centre,(.0058,.0085,.0016),'hero')
                    side=along.cross(back).normalized()
                    nail.rotation_euler=Matrix((side,along,back)).transposed().to_euler()
                    world=nail.matrix_world.copy();nail.parent=hand;nail.matrix_world=world
            else:
                hand=F.pointing_hand((0,.03,.835))
            span=.25 if 'accent' in gid else .42
            if variant=='nails':
                for t,a in [(0,0),(1.2,0),(2.5,18),(3.5,-12),(4,0)]:pose(hand,t,rotation=(0,math.radians(a),0))
                if gid=='nails_tech_pov_hold':
                    brush=F.tool('brush',(.08,-.04,.85));worker=A.hand((0,.06,.015),scale=.6);worker.parent=brush
                    for t,x in [(0,.11),(1.2,.11),(2.8,.005),(4,.005)]:pose(brush,t,location=(x,-.04,.85))
                actions=['Finished hand turns about its wrist while the phone remains supported','Minimal nail surfaces and a steady light-facing edge explain the finish without moving a lamp']
            else:
                dynamic=False
                for obj in hand.children_recursive:
                    if obj.type=='MESH':A.tag(obj,'hero',"The owner's resting hand is the primary subject")
                actions=['One relaxed hand rests on the towel; film only the owner\'s body','An overhead supported phone shows the treatment context without extra people or hands']
        elif variant=='garment':
            cloth=V.garment((0,0,.80));cloth.rotation_euler.x=math.pi/2;cloth.scale=(.48,)*3;F.card((.08,.05,.82),'ITEM','YOUR PICK','PRICE',.16,.12)
            dynamic=False;actions=['Garment, maker detail and attached tag form one supported find','Hold the high phone angle steady so the tag remains readable']
        else:
            A.pasta();hand=F.pointing_hand((.09,.15,.91));leaf=A.ellipsoid('Garnish placed on food',(.02,0,.91),(.018,.009,.002),'hero')
            for t,p in [(0,(.09,.06,.91)),(1.2,(.09,.06,.91)),(2.6,(.02,0,.868)),(4,(.02,0,.868))]:
                pose(leaf,t,location=p);pose(hand,t,location=Vector(p)+Vector((0,.09,0)))
            actions=['One hand places a garnish onto the same supported dish','Overhead phone remains on the public pass side or above the creator\'s own task']
    elif family=='service':
        counter();focus=Vector((0,.15,1.08));span=.95;down=10
        if variant in ['coffee','menu','till']:
            A.menu_board((.35,.65,1.65),title='MENU' if variant!='till' else 'RECEIPT',selected='YOUR PICK' if variant!='till' else 'TOTAL',right='PRICE')
            V.tag(G.block('Public coffee machine',(0,.45,1.04),(.45,.28,.48),.04),'support','Machine is viewed from the visitor-facing side; camera never crosses the counter')
            A.cup((0,.05,.795));A.saucer((0,.05,.785))
            if variant=='coffee':
                operator=A.portrait((0,.80,0),None);operator['root'].rotation_euler.z=math.pi/2
                tamper=F.tool('tamper',(.07,.05,.90));hand=A.hand((0,.06,.015),scale=.8);hand.parent=tamper
                for t,z in [(0,.98),(1.2,.98),(2.2,.90),(3.4,.98),(4,.90)]:pose(tamper,t,location=(.07,.05,z))
            if variant=='menu':focus=Vector((.35,.65,1.65));span=.75
            elif variant=='till':focus=Vector((.50,.65,1.705));span=.75
            actions=['Visitor-side oblique framing shows the public resource, operator task and receiving cup','A cropped visitor shoulder may frame the view; the phone never stands behind a staff member']
        elif variant=='rail':
            V.rack('garment',(0,.65,0));focus=Vector((0,.65,1.25));hand=F.pointing_hand((.15,.20,1.25))
            for t,y in [(0,.20),(1.2,.20),(2.8,.50),(4,.30)]:pose(hand,t,location=(.15,y,1.25))
            actions=['One hand selects a coherent garment from the public rail','Neighbouring pieces remain on their supports, giving the choice a clear context']
        elif variant=='hair':
            client=A.portrait((0,.30,0),None);hair(client)
            tool=F.tool('scissors',(.13,.22,1.65));hand=A.hand((.01,.06,0),scale=.8);hand.parent=tool
            for t,z in [(0,1.60),(1.2,1.60),(2.6,1.70),(4,1.63)]:pose(tool,t,location=(.13,.22,z))
            focus=Vector((.08,.30,1.65));span=.48;down=20
            actions=['Scissors and an attached hand work beside the same hair silhouette','The public/client-side oblique view preserves the task without standing in a staff-only position']
        elif variant=='player':
            actor=A.portrait((0,.3,0),None);eyes(actor);guitar=V.guitar((0,.12,.65));guitar.scale=(.70,)*3
            for obj in guitar.children_recursive:
                if obj.type=='MESH':A.tag(obj,'hero','Player and the supported instrument are the primary reveal')
            for x,z in [(.04,1.20),(-.02,.90)]:
                hand=A.hand((x,.05,z),scale=.8)
                A.tag(G.tube('Player attached forearm',[(x,.05,z),(x+.12,.12,1.10),(.19 if x>0 else -.19,.30,1.35)],.025),'support','Hand is connected to the player while touching the instrument')
            focus=Vector((0,.10,.97));span=.80;down=0
            actions=['Instrument strings and hand region start the shot; the short pullback reveals the player','Curved instrument body and quiet mouthless face stay in one coherent scene']
        elif variant=='treatment':
            focus=Vector((0,.15,1.65));span=.80;down=-35
            lamp=V.tag(G.tube('Treatment lamp rim',[(.22*math.cos(i*math.pi/16),.3,1.90+.22*math.sin(i*math.pi/16)) for i in range(33)],.012),'hero','Fixed lamp identifies the patient-side treatment view')
            hand=F.pointing_hand((.12,.1,1.65));custom='portrait_fixed'
            hand.scale=(1.35,)*3
            for t,y in [(0,.1),(1.2,.1),(2.8,-.25),(4,-.45)]:pose(hand,t,location=(.12,y,1.65))
            actions=['Patient-side chest-height phone looks toward a fixed lamp and one artist hand','A palm approaches to cover the lens at the end; no operator enters a restricted working area']
        else:
            V.tag(G.block('Public repair bench',(0,.2,.79),(1.2,.60,.04),.01),'structure');work=V.tag(G.block('Repair object',(0,.15,.83),(.20,.28,.03),.015),'hero')
            tool=F.tool('brush',(.04,.15,.86));hand=A.hand((0,.06,.015),scale=.8);hand.parent=tool
            for t,x in [(0,-.03),(1.2,-.03),(2.5,.07),(4,-.03)]:pose(tool,t,location=(x,.15,.86))
            actor=A.portrait((0,.7,0),None);eyes(actor)
            focus=Vector((0,.15,.90));span=.70;actions=['The supported workpiece and attached tool lead attention before the owner/workplace reveal','Camera stays in the client-accessible viewing space; the worker and task share one coherent bench']
        if gid.startswith('over_shoulder'):
            shoulder=A.portrait((-.38,-.38,-.20),None)
            for obj in shoulder['root'].children_recursive:
                if obj.type=='MESH':A.tag(obj,'foreground_frame','Cropped visitor shoulder frames the public view; it is not a staff-side camera position')
    else:
        # Internal multi-detail sequence: tools, chair and front desk in real spatial order.
        F.tool('clippers',(-.22,0,.82));F.tool('scissors',(0,0,.82));V.chair((.75,.9,0),salon=True)
        counter();A.menu_board((1.45,1,1.45),title='WELCOME',selected='RECEPTION',right='')
        focus=Vector((-.22,0,.84));span=.38;down=45
        actions=['First tool detail flicks to the next detail, then the front desk','All destinations are native scene objects; use separate short takes for the final desk framing']
        cam=camera('Salon detail sequence',(-.22,-.38,1.2),focus,30)
        for t,target in [(0,(-.22,0,.84)),(1.2,(-.22,0,.84)),(1.45,(0,0,.84)),(2.8,(0,0,.84)),(3.05,(.75,.9,1.1)),(4.4,(.75,.9,1.1)),(4.65,(1.45,1,1.45)),(6.2,(1.45,1,1.45))]:key_camera(cam,t,(-.22,-.38,1.2),target)
        custom=cam
    if family=='portrait':
        focus.z=1.646-.267*span
        down=22 if '_high_' in gid else 15
    A.fixed_side_light(focus)
    sequence=M.apply(scene,spec,focus,span,down,action_objects=dynamic)
    if isinstance(custom,bpy.types.Object):
        sequence['cameras']=[(0,custom)]
        if family=='details':sequence.update(duration=6.4,take_end=6.4)
    elif custom=='portrait_fixed':
        # Use the generated camera's initial pose without its compiled proxy truck/dolly.
        cam=sequence['cameras'][0][1];scene.frame_set(1);p=cam.location.copy();target=focus.copy();cam.animation_data_clear();key_camera(cam,0,p,target)
        if family=='service' and variant=='treatment':
            direction=(focus-p).normalized();hand.rotation_euler=(-direction).to_track_quat('Z','Y').to_euler()
            for t,position in [(0,Vector((.12,.1,1.65))),(1.2,Vector((.12,.1,1.65))),(sequence['duration']-.15,p+direction*.07)]:pose(hand,t,location=position)
        sequence.setdefault('source_adaptations',[]).append('Phone remains fixed; subject/resource/occluder supplies the source-script movement instead of an infeasible simultaneous phone move')
    sequence.update(intent='; '.join(actions),composition=actions,subject_actions=actions,
                    geometry_checks=dict(family=family,variant=variant),
                    contextual_next_steps=[dict(script=c['script'],next_step=c['next_step']) for c in spec['contexts']])
    if family=='service':sequence.setdefault('source_adaptations',[]).append('Any staff-only over-shoulder position is adapted to a visitor-side oblique view')
    return sequence


def register(factories):
    for gid in REGISTRY:factories[gid]=build
