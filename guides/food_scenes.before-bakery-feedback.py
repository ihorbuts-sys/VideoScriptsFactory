"""Food, paper resources and tabletop action scenes with reusable physical props."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
import assets as A
import geometry as G
import venue_assets as V
import food_assets as F
import shot_motion as M
from drink_scenes import pose,grip,glass,counter,smooth as smooth_local

REGISTRY={}
def add(ids,family,variant):
    for gid in ids.split():REGISTRY[gid]=(family,variant)
add('burger_cut_high_in_cd_through burger_cut_high_in_cd_whipout burger_cut_low_in_cd','burger','split')
add('burger_low_in_mc','burger','whole')
add('pastry_break_eye_hold pastry_tear_open','pastry','tear')
add('card_label_high_hold_whipout','card','label')
add('card_menu_high_in_cd_whipout card_menu_top_hold','card','menu')
add('card_pricelist_top_hold','card','price')
add('card_receipt_top_hold','card','receipt')
add('card_tag_high_hold card_tag_top_in_cd card_tag_top_in_cd_through','card','tag')
add('card_ticket_eye_in_cd','card','ticket')
add('latte_top_in_cd latte_top_in_cd_whipout','latte','art')
add('oven_tray_eye_in_mc oven_tray_eye_in_md_through tray_high_in_mc','tray','bakery')
add('bag_handoff_low_hold','tray','handoff')
add('plate_bite_top_hold','plate','bar_bite')
add('plate_kids_top_hold','plate','kids')
add('plate_low_in_cd_through plate_low_in_cd_whipout','plate','hero')
add('plate_sizzle_low_in_cd','plate','grill')
add('plate_spread_eye_out_dw plate_spread_top_hold plate_spread_top_out_dw','plate','spread')
add('plate_yolk_high_in_cd','plate','yolk')
add('topdown_bag_top_hold','layout','sauna')
add('topdown_box_top_out_cm','layout','pastry_box')
add('topdown_first_top_hold_whipout','layout','pickup')
add('topdown_haul_top_out_dw','layout','shopping')
add('topdown_kidstuff_high_in_cd_whipout','layout','kids')
add('topdown_unwrap_top_in_cd','layout','unwrap')
add('tools_closeup_hands tools_tray_top_hold','tools','salon')
add('menu_schedule_low_tiltd_mm','schedule','classes')


def explicit_review(gid,description,contexts):
    family,variant=REGISTRY[gid]
    subjects={'burger':'Layered burger with a true cut cross-section and coherent support','pastry':'Laminated pastry opening toward the phone','card':'Selected '+variant+' resource field and its surrounding physical context','latte':'Latte surface, applied topping and cup/saucer support','tray':'Same coherent food tray and its public-side handoff','plate':'The '+variant+' dish and its associated table objects','layout':'The '+variant+' arrangement and individual object actions','tools':'Recognisable salon tools, working end and associated tray','schedule':'Class name, then prices and times below'}
    return dict(subject=subjects[family],angle='Use the source low/high/top-down camera angle; frame entirely from ordinary visitor space',motion='Source camera move plus the described physical subject action; do not substitute a zoom for a tear, pickup or plating action',focal_point=subjects[family],composition='Separate the hero silhouette from its supports; meaningful surrounding objects explain the context and give the move a destination',golden_ratio='Use a balanced supporting triangle and resource field hierarchy where relevant; keep centred contact/actions easy to copy',lighting='Fixed broad side/window light, faint context, no bloom or time-dependent lighting trick',contacts='All food and tools rest on their support before deliberate handling; preserve hand/prop parenting',handover='Next source step recorded for contextual assembly; no unrelated destination is invented',mobile='Phone at reachable table/edge height; elbows supported for holds. Use a propped phone or a helper when both visible hands manipulate the item',source_subject_variant=variant)


def steam(position):
    for j in range(2):
        obj=A.tag(G.tube('Quiet food steam',[(position[0]+.008*math.sin(k*.8+j),position[1],position[2]+k*.014) for k in range(8)],.0006),'background','Steam supplies visible subject movement while existing lighting stays fixed')
        for t,z in [(0,0),(1,.012),(2,0),(3,.014),(4,0)]:pose(obj,t,location=(0,0,z))


def build(scene,spec):
    gid=spec['id'];family,variant=REGISTRY[gid];A.table(radius=.65)
    focus=Vector((0,0,.87));span=.48;down=None;actions=[];dynamic=True
    if family=='burger':
        A.plate();root,halves=F.burger(split=variant=='split')
        A.fork((.23,.02,.789));V.tag(G.block('Folded food napkin',(-.22,.11,.79),(.15,.13,.010),.004),'background','Napkin supports the commercial food context without crossing the burger')
        if halves:
            for half,side in zip(halves,[-1,1]):
                hand=A.hand((side*.12,.035,.045),scale=.85,mirror=side);hand.parent=half;hand.rotation_euler.y=-side*math.pi/2
                arm=A.tag(G.tube('Tearing forearm',[(0,0,-.04),(0,0,-.20)],.020),'background','Forearm enters from the frame edge and remains attached to the gripping hand');arm.parent=hand
                for t,x in [(0,0),(1.2,0),(2.7,side*.075),(4,side*.075)]:
                    amount=smooth_local((t-1.2)/1.5)
                    normal=Vector((0,-.70710678,.70710678)) if '_high_' in gid else Vector((0,-.97,.24))
                    rotation=Vector((-side,0,0)).rotation_difference(normal).to_euler()
                    pose(half,t,location=(x,-.025*(t/4),.10*amount),rotation=tuple(v*amount for v in rotation))
            if '_high_' in gid:span=.28 if '_through' in gid else .32
            actions=['Two physically consistent burger halves separate to show the filling','The low/high phone view keeps bun, patty and cheese in a clear layered cross-section']
        else:
            # Whole item is stable on its plate; handheld variant is shown in contextual use.
            steam((0,0,.93));actions=['Phone approaches the layered item while the item stays on its plate','Napkin, rim and fork give scale and context without distracting from the food']
        if '_low_' in gid:down=-8;focus=Vector((0,0,.89));span=.38
    elif family=='pastry':
        A.plate();root,halves=A.pastry();span=.35
        for half,side in zip(halves,[1,-1]):
            hand=A.hand((side*.08,.03,.045),scale=.75,mirror=side);hand.parent=half;hand.rotation_euler.y=-side*math.pi/2
            arm=A.tag(G.tube('Tearing forearm',[(0,0,-.04),(0,0,-.20)],.020),'background','Forearm stays attached as the pastry opens');arm.parent=hand
            for t,p in [(0,(0,0,0)),(1.2,(0,0,0)),(2.9,(side*.09,-.04,.05)),(4,(side*.09,-.04,.05))]:pose(half,t,location=p,rotation=(0,0,side*math.radians(40)*smooth_local((t-1.2)/1.7)))
        down=45 if gid=='pastry_tear_open' else 0
        focus=Vector((0,0,.86));actions=['Two hands open the same pastry halves toward the lens','Laminated seams and the cut faces reveal the crumb while the plate remains a quiet support']
    elif family=='card':
        title,selected,value={'label':('MAKER','DETAIL','MARK'),'menu':('MENU','YOUR PICK','PRICE'),'price':('PRICE LIST','SERVICE','PRICE'),'receipt':('RECEIPT','TOTAL','PRICE'),'tag':('ITEM TAG','ITEM','PRICE'),'ticket':('TICKET','ENTRY','PRICE')}[variant]
        if variant in ['label','tag']:
            cloth=V.garment((0,0,.798));cloth.rotation_euler.x=math.pi/2;cloth.scale=(.5,)*3
        paper=F.card((0,0,.808 if variant in ['label','tag'] else .788),title,selected,value)
        focus=Vector((.015,-.005,paper.location.z+.003));span=.34
        if variant in ['menu','price']:
            hand=F.pointing_hand((.035,.18,.85))
            for t,y in [(0,.27),(1.2,.27),(2,.10),(4,.10)]:pose(hand,t,location=(.035,y,.85 if t<2 else .797))
            actions=['One index settles beside the selected resource line','The complete name/value field stays readable while margins and neighbouring rows establish context']
        else:
            dynamic=False;actions=['Hold the selected '+variant+' field clearly and still','The resource stays physically supported; no fake camera drift or invented personal data']
        if variant=='ticket':
            paper.rotation_euler.x=math.pi/2;paper.location.z=1.20;focus=Vector((0,0,1.20));down=0
            V.tag(G.tube('Ticket price-board stand',[(0,.02,.785),(0,.02,1.10)],.008),'background','The ticket-price resource is supported as a public placard')
            V.tag(G.block('Placard foot',(0,.02,.79),(.10,.10,.01),.005),'background')
    elif family=='latte':
        A.saucer();cup=A.cup();focus=Vector((0,0,.902));span=.19;down=90
        for j in range(4):
            points=[]
            for k in range(25):
                t=k/24*math.pi;points.append((.031*math.sin(t)*math.cos(t),-.027+j*.011+.014*math.sin(t),.903))
            obj=A.tag(G.tube('Latte rosetta leaf',points,.0014),'hero','Sequential milk-art strokes reveal the topping action on the actual coffee surface')
            for t,s in [(0,.001),(1.1+j*.25,.001),(1.45+j*.25,1)]:pose(obj,t,scale=(s,s,1))
        actions=['Milk-art strokes appear sequentially on the coffee surface','A short overhead approach reveals the completed rosetta, with handle and saucer preserving orientation']
    elif family=='tray':
        tray_before=set(bpy.data.objects)
        V.tag(G.block('Food tray base',(0,0,.80),(.49,.32,.025),.012),'support','One rigid tray supports all items during handoff')
        for x in [-.13,.13]:
            root,parts=A.pastry((x,0,.815));root.scale=(.85,)*3
        tray=A.group('Coherent order tray',tray_before,(0,0,0),'support','Tray and food move as one object without sliding through their support')
        if variant=='handoff':
            hand=A.hand((.24,.05,.78),scale=1);hand.parent=tray
            for t,p in [(0,(0,.20,.20)),(1.2,(0,.20,.20)),(2.7,(0,0,0)),(4,(0,0,0))]:pose(tray,t,location=p)
            down=-8;span=.62;focus=Vector((0,0,.9));actions=['Tray comes down from the public serving ledge toward the customer','Food, tray and one supporting hand stay attached throughout the handoff']
        elif gid.startswith('oven'):
            # Oven front only, filmed from a public viewing position; never enter the kitchen.
            V.tag(G.block('Public-view oven front frame',(0,.4,1.10),(.80,.06,.50),.03),'background','Only the public-facing oven opening is context; the camera remains outside the working area')
            for t,y in [(0,.22),(1.2,.22),(2.8,0),(4,0)]:pose(tray,t,location=(0,y,0))
            steam((0,0,.87));down=0;span=.66;actions=['The coherent hot tray emerges toward the public viewing side','Steam and crust are the action landmarks; phone makes only a short approach']
        else:actions=['Baked items remain grouped on the same supported tray','The high approach picks one item while neighbouring pastries supply context']
    elif family=='plate':
        if variant=='bar_bite':
            A.plate((-.14,0,.785));root,parts=F.burger((-.14,0,.794));root.scale=(.60,)*3
            drink,liq=glass((.17,.08,.785));grip(drink)
            for t,z in [(0,.785),(1.2,.785),(2.7,1.02),(4,1.02)]:pose(drink,t,location=(.17,.08,z))
            span=.70;down=90;actions=['Drink and bite form a clear two-item composition from overhead','One hand picks up the glass while the plate stays supported']
        elif variant=='kids':
            before=set(bpy.data.objects);A.pasta();meal=A.group('Kids plate landing',before,(0,0,0),'hero','Food remains on its plate while it is set down')
            F.landing_grip(meal,(.15,0,.808))
            down=90;span=.50;actions=['The complete kids plate lands under the fixed overhead phone','Clear plate rim and simple food grouping make the landing easy to copy']
        elif variant=='grill':
            V.tag(G.block('Tabletop grill',(0,0,.82),(.38,.29,.07),.025),'support','Public tabletop cooking surface is accessible from the seated diner side')
            for x in [i*.035 for i in range(-4,5)]:V.tag(G.tube('Grill bar',[(x,-.13,.86),(x,.13,.86)],.003),'background','Grill rhythm establishes the cooking surface')
            meat=A.ellipsoid('Meat portion',(0,0,.883),(.10,.065,.02),'hero','Food lands on the grill rather than hovering above it')
            F.held_tongs(meat)
            for t,z in [(0,1.03),(1.2,1.03),(1.8,.883),(4,.883)]:pose(meat,t,location=(0,0,z))
            steam((0,0,.91));focus=Vector((0,0,.90));down=-5;span=.44;actions=['Food lands on a supported tabletop grill and steam rises','The low phone approach stays on the diner side and keeps the grill in context']
        elif variant=='spread':
            A.pasta();saucer=A.saucer((.35,.13,.785));cup=A.cup((.35,.13,.795),role='support');plate=A.plate((-.35,.13,.785));pastry,_=A.pastry((-.35,.13,.794))
            span=.85;down=90 if '_top_' in gid else 0
            if gid=='plate_spread_top_hold':
                left=A.empty('Carried pastry plate');plate.parent=left;pastry.parent=left
                right=A.empty('Carried cup and saucer');cup.parent=right;saucer.parent=right
                F.landing_grip(left,(-.50,.13,.808),start=.5,end=1.5,lift=.12,side=-1)
                F.landing_grip(right,(.415,.13,.85),start=1.6,end=2.6,lift=.12)
            actions=['Hero plate, pastry and drink form a non-overlapping supporting triangle','The specified hold or pullback explains the whole spread, not an isolated product scale change']
        elif variant=='yolk':
            A.plate();white=A.ellipsoid('Egg white',(0,0,.808),(.10,.07,.012),'hero');yolk=A.ellipsoid('Egg yolk',(0,0,.831),(.032,.032,.023),'hero')
            fork=A.fork((0,-.15,.92),role='support')
            # Palm down on the handle, fingers toward the tines; the forearm leaves to the back right, out of frame.
            import real_hands
            hand=real_hands.place('pinch','R',target=(0,-.09,.012),forward=(-.45,1,-.15),normal=(0,0,-1),anchor='grip');hand.parent=fork
            wrist=V.tag(G.tube('Fork attached wrist',[(0,-.10,.01),(0,-.20,.02),(0,-.29,.03)],.018),'background','The fork is held while pressing the yolk');wrist.parent=fork
            for t,p in [(0,(0,-.15,.92)),(1.2,(0,-.15,.92)),(2.1,(0,-.05,.83)),(4,(0,-.05,.83))]:pose(fork,t,location=p)
            pool=A.ellipsoid('Opened yolk',(0,-.02,.821),(.060,.045,.0015),'hero')
            for t,s in [(0,.001),(2.0,.001),(2.9,1)]:pose(pool,t,scale=(s,s,1))
            span=.36;down=45;actions=['Fork meets the yolk and a low pool opens on the same plate','The camera approaches the actual contact point from a reachable high angle']
        else:
            A.pasta();A.fork((.20,.02,.789));steam((0,0,.87));span=.40;down=-7;focus=Vector((0,0,.85))
            actions=['Food, formed plate rim and fork give a coherent low commercial angle','Steam supplies subject motion while the short phone approach reveals food texture']
    elif family=='layout':
        down=45 if variant=='kids' else 90;span=.68
        if variant in ['pastry_box','unwrap']:
            box,hinge=F.open_box(pastries=variant=='pastry_box')
            if variant=='unwrap':
                root,parts=F.burger((0,0,.81),split=True);root.scale=(.9,)*3
                for obj in list(parts[0].children):bpy.data.objects.remove(obj,do_unlink=True)
                bpy.data.objects.remove(parts[0],do_unlink=True)
                parts[1].rotation_euler.y=math.pi/2;parts[1].location.z=.10
                for t,a in [(0,90),(1.2,90),(2.8,0),(4,0)]:pose(hinge,t,rotation=(math.radians(a),0,0))
            actions=['The hinged box and its contents remain physically connected','Opening or overhead pullback reveals the food together with its packaging']
        elif variant=='sauna':
            towel=V.tag(G.block('Folded towel',(-.17,0,.81),(.30,.22,.05),.035),'hero','Towel, footwear and water bottle are practical kit for the visit')
            for side in [-1,1]:
                shoe=A.ellipsoid('Flip-flop sole',(.12+side*.055,0,.80),(.045,.12,.012),'support');G.tube('Flip-flop strap',[(.12+side*.055-.025,-.02,.815),(.12+side*.055,.02,.83),(.12+side*.055+.025,-.02,.815)],.004)
            bottle=V.tag(G.bottle('Water bottle',.02,.23,.785,height=.22,radius=.035),'support')
            F.landing_grip(towel,(-.15,0,0),start=1.1,end=1.7,lift=.16,side=-1)
            F.landing_grip(bottle,(.045,0,.10),start=2.0,end=2.6,lift=.16)
            actions=['Visit essentials enter one at a time and settle onto the bench/table support','The fixed overhead phone keeps the layout clear without extra hands']
        elif variant=='shopping':
            # The script picks two shelf bottles and a garment: keep those identities.
            for x in [-.20,.20]:
                bottle=G.bottle('Purchased shelf bottle',x,.25,.820,height=.25,radius=.035);bottle.rotation_euler.x=math.pi/2
                V.tag(bottle,'hero','Same bottle type selected from the public shelf; laid on the table rather than replaced by clothing')
                F.card((x-.085,.15,.788),'ITEM','PICK','PRICE',.12,.09)
            cloth=V.garment((0,-.25,.80));cloth.scale=(.30,)*3;cloth.rotation_euler.x=math.pi/2
            F.card((0,-.25,.82),'ITEM','PICK','PRICE',.13,.10)
            span=.60;actions=['The two selected bottles and one garment remain the same three purchases in the haul','The overhead lift connects the first tag to the complete supported layout']
        elif variant=='pickup':
            A.plate();root,parts=F.burger();grip(root)
            for t,z in [(0,.794),(1.3,.794),(2.8,1.03),(4,1.03)]:pose(root,t,location=(0,0,z))
            span=.38;actions=['One hand takes the first item from its plate','The phone stays overhead, then makes the prescribed outgoing whip']
        else:
            F.card((-.10,.06,.788),'KIDS MENU','ACTIVITY','',.26,.20)
            for j in range(5):
                pencil=G.lathe('Crayon',[(0,0),(.006,.01),(.006,.09),(0,.105)],(.08+j*.025,-.02,.793),12);pencil.rotation_euler.x=math.pi/2;V.tag(pencil,'hero','Repeated crayons and activity card identify the kid-friendly feature')
            span=.40;actions=['Crayons and activity menu form one small, usable table arrangement','Short high approach then outgoing whip links the detail to the family table']
    elif family=='tools':
        focus=Vector((0,0,.84));span=.38
        if gid=='tools_closeup_hands':
            F.tool('clippers',(-.08,0,.82));comb=G.block('Comb spine',(.12,0,.80),(.025,.19,.008),.003);V.tag(comb,'support')
            for j in range(12):V.tag(G.tube('Comb tooth',[(.12,-.08+j*.014,.80),(.16,-.08+j*.014,.80)],.0012),'support')
            dynamic=False;actions=['Clipper blade, guards and comb stay on the public styling shelf','The short high approach makes the working end readable without an artificial object pulse']
        else:
            bowl=V.tag(G.lathe('Tint bowl',[(0,0),(.07,0),(.075,.04),(.070,.045),(.060,.01),(0,.01)],(0,0,.785),32),'support')
            brush=F.tool('brush',(.02,0,.83));hand=A.hand((0,.08,.02),scale=.75);hand.parent=brush
            for t,a in [(0,0),(1.2,0),(2.0,60),(2.8,120),(4,170)]:pose(brush,t,rotation=(0,0,math.radians(a)))
            F.tool('brush',(.18,.02,.80));actions=['A single held brush stirs the tint in a supported bowl','Spare brush and tray context stay still; phone remains overhead']
    elif family=='schedule':
        # Class name is above concrete time/price fields; this is not a board-to-cup template.
        A.menu_board((0,.4,1.70),title='CLASS SCHEDULE',selected='YOUR CLASS',right='TIME',rows=[('SESSION','PRICE'),('NEXT CLASS','TIME')],tall=True)
        focus=Vector((0,.4,1.90));span=.74;down=-12
        actions=['Downward wrist pitch moves from class name to its times and prices','Source cup/counter drawing is replaced with the actual schedule resource required by the script']
    else:raise AssertionError(gid)
    if family in ['burger','pastry','plate'] and variant not in ['grill','spread']:
        A.rim_light_cue((0,0,.816),.149)
    elif family=='latte':A.rim_light_cue((0,0,.914),.0533)
    A.fixed_side_light(focus)
    sequence=M.apply(scene,spec,focus,span,down,lens=24 if family=='plate' and variant=='spread' and down==90 else 30,action_objects=dynamic)
    if family=='burger' and variant=='split' and '_high_' in gid:
        cam=sequence['cameras'][0][1]
        for f in range(1,round(sequence['duration']*15)+1):
            scene.frame_set(f);amount=smooth_local(((f-1)/15-1.2)/1.5)
            cam.location.x+=.12*amount;cam.location.z+=.07*amount
            cam.keyframe_insert(data_path='location',frame=f)
        sequence.setdefault('source_adaptations',[]).append('Follow the lifted cut face with a 12 cm lateral and 7 cm vertical reframe, instead of pushing into the gap between the halves')
    sequence.update(intent='; '.join(actions),composition=actions,subject_actions=actions,
                    geometry_checks=dict(family=family,variant=variant,physical_actions=dynamic),
                    contextual_next_steps=[dict(script=c['script'],next_step=c['next_step']) for c in spec['contexts']])
    if family in ['burger','pastry']:sequence['mobile_feasibility']['two_hand_action']='Phone propped or held by a helper; no floating camera while both operator hands are occupied'
    return sequence


def register(factories):
    for gid in REGISTRY:factories[gid]=build
