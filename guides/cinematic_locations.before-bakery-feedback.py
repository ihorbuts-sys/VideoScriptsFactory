"""Connected public interiors and supported food reveals with handheld camera curves."""
import bpy
import math
from mathutils import Vector
import assets as A
import geometry as G
import venue_assets as V
import food_assets as F
from drink_scenes import pose
from motion_paths import camera_path,sequence

IDS=['case_eye_in_mc_through','hand_pov_pastry_pov_in_mc','pastry_tear_open','pastry_break_eye_hold',
     'door_eye_in_wd_through','door_pov_in_wc_through','door_pov_in_wd_through',
     'facade_eye_hold','facade_truck_eye_in_wm','facade_window_pov_hold','facade_window_eye_in_wm_whipout']


def review(gid):
    return dict(subject='Connected '+gid.replace('_',' ')+' in public visitor space',angle='Camera height and pitch change together along a continuous curved path',
        motion='Smooth diagonal travel and natural settling; keep visible landmarks through the transition',
        focal_point='The next resource is a real object in the same scene',composition='Foreground frame, clear public aisle and quieter distant context establish depth',
        golden_ratio='Practical sight lines and a clear destination take precedence',lighting='Fixed window/venue side light; no animated fixtures or bloom',
        contacts='Food rests on shelves or plates, furniture stays grounded; omit uncertain hand manipulation',
        handover='Continue into the real next resource in the same interior',mobile='Visitor-side phone; normal slow walking, a short lean and coordinated pitch; never enter staff workspace')


def filled_pastry(position=(0,0,.794)):
    before=set(bpy.data.objects);root,halves=A.pastry((0,0,0))
    for j,half in enumerate(halves):
        sign=1 if j==0 else -1
        for title,radii in [('Cream filling cross-section',(.0018,.020,.013)),('Chocolate filling centre',(.0022,.010,.007))]:
            patch=A.ellipsoid(title,(0,.072,.0272),radii,'hero','Visible filling sits inside the cut face, with a surrounding pastry crust');patch.parent=half
        # Explicit visible cut-face contours keep filling readable in a monochrome ghost.
        for name,ry,rz in [('Cream filling rim',.020,.013),('Chocolate filling contour',.010,.007)]:
            points=[(-sign*.004,.072+ry*math.cos(k*math.tau/32),.0272+rz*math.sin(k*math.tau/32)) for k in range(33)]
            ring=A.tag(G.tube(name,points,.001),'hero','A front-facing filling boundary stays visible on the opened cross-section');ring.parent=half
        half.location.x=sign*.10;half.rotation_euler.z=sign*math.radians(44)
    group=A.group('Opened filled croissant on plate',before,position,'hero','Both halves remain on the plate; no unverified hand grip or floating food')
    group.scale=(.85,.85,1)
    return group


def pastry_scene(scene,spec):
    A.table(radius=.54);A.plate();filled_pastry();A.fixed_side_light((0,0,.84))
    cam=camera_path('Filled croissant curved crumb reveal',[(0,(-.15,-.34,1.03),(0,.04,.83)),(2.1,(.03,-.31,1.17),(0,.04,.83)),(4.9,(.17,-.24,1.21),(0,.04,.83))],5,39)
    result=sequence(cam,5,actions=['Opened croissant halves show crust and filling while supported by a plate','A smooth rising arc changes X-axis pitch and reveals the cut faces without uncertain hands'])
    result['source_adaptations'].append('Owner permits a supported opened-pastry alternative instead of an unconvincing grip or simulated tear')
    return result


def pastry_case(scene,spec):
    V.pastry_case((0,.60,0));A.table((.65,-.25,0),radius=.53);A.plate((.65,-.25,.785));filled_pastry((.65,-.25,.794))
    A.fixed_side_light((.25,.1,1.0))
    cam=camera_path('Case to supported filled pastry',[(0,(-.35,-.90,1.22),(-.26,.60,1.18)),(3.2,(-.26,-.55,1.28),(-.26,.60,1.18)),
        (4.5,(-.08,-.60,1.38),(.25,.08,1.0)),(6.2,(.40,-.61,1.50),(.65,-.25,.84)),(8.9,(.79,-.65,1.48),(.65,-.25,.83))],9,32)
    return sequence(cam,9,4,['Select the pastry from the customer side of the case','Move along the same public counter to an opened filled croissant resting on its plate'],next_guide='pastry_tear_open',landing=5.5)


def entrance(scene,spec,kind=None):
    gid=spec['id'];kind=kind or ('dining' if gid=='door_eye_in_wd_through' else 'waiting' if gid=='door_pov_in_wc_through' else 'salon')
    door,hinge=V.door()
    for t,a in [(0,0),(.6,0),(2.0,-82),(11,-82)]:pose(hinge,t,rotation=(0,0,math.radians(a)))
    target=(.9,3.0,.95)
    if kind=='dining':
        for x in [-1.28,1.28]:
            for y in [1.65,3.35]:V.dining_table((x,y,0))
        target=(1.28,3.35,.85)
    elif kind=='salon':
        for x,y in [(-1.20,1.8),(1.20,3.0)]:
            V.chair((x,y,0),salon=True);A.tag(G.block('Salon station shelf',(x,y+.4,.85),(.8,.3,.04),.01),'background','Station belongs to the same public salon interior')
        target=(1.20,3.0,.90)
    elif kind=='waiting':
        for x in [-1.25,1.25]:
            for y in [1.6,2.6]:V.chair((x,y,0),rotation=-math.pi/2 if x<0 else math.pi/2)
        A.tag(G.block('Reception counter',(0,3.65,.55),(1.2,.55,1.10),.025),'support','Public reception remains the destination beyond the clear waiting aisle')
        target=(0,3.65,1.12)
    elif kind=='shop':
        for x in [-1.25,1.25]:rail=V.rack('garment',(x,2.4,0));rail.rotation_euler.z=math.pi/2
        target=(1.25,2.8,1.2)
    else:
        A.tag(G.block('Public welcome desk',(1.2,2.8,.55),(1.0,.6,1.10),.025),'structure','Price list is seen from the visitor side of reception')
        A.menu_board((1.2,2.51,1.50),title='CLASS PRICES',selected='YOUR CLASS',right='PRICE')
        target=(1.2,2.51,1.50)
    window=V.window((-2,2.8,1.45));window.rotation_euler.z=math.pi/2;A.fixed_side_light((0,1.8,1.1))
    cam=camera_path('Open door and walk through '+kind,[(0,(-.10,-1.60,1.50),(0,0,1.25)),(2,(-.04,-1.10,1.52),(0,.8,1.25)),
        (4,(.06,.12,1.50),(0,2.0,1.15)),(7,(.14,1.30,1.54),(.20,3.0,1.10)),(10.9,(.22,2.0,1.48),target)],11,28)
    nxt={'dining':'room_dining_eye_reveal_cw' if gid=='door_eye_in_wd_through' else 'room_dining_eye_reveal_cw_whipout',
         'salon':'chair_reveal_frame','waiting':'room_waiting_eye_reveal_cw','shop':'room_shop_eye_out_cw','fitness':'menu_pricelist_eye_out_dm'}[kind]
    result=sequence(cam,11,4,['The hinged door opens while the camera waits outside','Walk through the same doorway and along its clear public '+kind+' aisle'],next_guide=nxt,landing=4)
    result['mobile_feasibility']['max_walk_m']=4.5;result['interior_kind']=kind
    result['framing_landmarks']=[obj.name for obj in scene.objects if obj.type=='MESH' and obj.name.startswith(('Door jamb','Door lintel','Door pull'))]
    return result


def truck_geometry():
    A.tag(G.block('Truck lower body',(0,1.15,.70),(2.9,1.2,.90),.08),'structure','The body stops beneath an actual open serving window')
    for x in [-1.4,1.4]:A.tag(G.block('Truck window side pillar',(x,.83,1.65),(.12,.18,1.25),.02),'structure','Side pillars frame the open visitor-facing window')
    A.tag(G.block('Truck roof',(0,1.15,2.29),(2.95,1.25,.12),.045),'background','Quiet truck outline establishes the vehicle')
    A.tag(G.block('Public serving ledge',(0,.48,1.155),(1.35,.66,.05),.015),'support','Same accessible ledge used for the order handoff')
    for x in [-.65,.65]:A.tag(G.block('Serving window jamb',(x,.78,1.63),(.035,.035,.90),.004),'support','A real opening reveals food behind it')
    V.lettering('ORDER HERE',(0,.69,2.04),.10)
    for z in [1.21,1.62]:
        A.tag(G.block('Visible food rack',(0,1.28,z),(1.30,.42,.035),.008),'important_background','Food is visible through the window; the camera remains outside')
        for x in [-.40,0,.40]:
            A.plate((x,1.28,z+.0175),'background');burger,_=F.burger((x,1.28,z+.0265));burger.scale=(.8,)*3
    for x in [-1.0,1.0]:
        wheel=G.lathe('Truck grounded wheel',[(0,0),(.26,0),(.27,.10),(0,.10)],(x,.55,.28),32);wheel.rotation_euler.x=math.pi/2;A.tag(wheel,'background','Wheels identify the public truck exterior')
    A.fixed_side_light((0,1.0,1.5))


def truck(scene,spec):
    truck_geometry();gid=spec['id'];wide=gid=='facade_truck_eye_in_wm';duration=8 if wide else 4
    knots=[(0,(-.45,-2.1,1.45),(0,.9,1.48)),(2.2,(-.12,-1.45,1.55),(0,1.1,1.48)),(4,(.12,-.80,1.58),(0,1.28,1.48))] if wide else [(0,(.12,-.80,1.58),(0,1.28,1.48))]
    knots.extend([(5.8 if wide else 1.8,(.20,-.66,1.65),(0,1.28,1.48)),(7.9 if wide else 3.9,(-.04,-.53,1.57),(0,1.28,1.48))])
    cam=camera_path('Customer-side open truck window',knots,duration,30)
    return sequence(cam,duration,4 if wide else None,['An open serving window reveals the real food rack inside the truck','A curved approach changes height and pitch entirely outside the visitor-facing ledge'],next_guide='facade_window_pov_hold' if wide else None,landing=4)


def build(scene,spec):
    gid=spec['id']
    if gid=='case_eye_in_mc_through':return pastry_case(scene,spec)
    if gid in ['hand_pov_pastry_pov_in_mc','pastry_tear_open','pastry_break_eye_hold']:return pastry_scene(scene,spec)
    if gid.startswith('door_'):return entrance(scene,spec)
    if gid.startswith('facade_') and gid!='facade_eye_hold':return truck(scene,spec)
    V.facade();A.fixed_side_light((0,0,1.6))
    cam=camera_path('Frontage diagonal sign-to-door approach',[(0,(.60,-3.0,1.46),(0,0,2.05)),(2.4,(.20,-2.74,1.57),(0,0,1.85)),(4.9,(-.20,-2.50,1.51),(0,0,1.24))],5,31)
    result=sequence(cam,5,actions=['A curved public-side approach reveals sign, entrance and window depth','Camera height and X-axis pitch change together as attention moves toward the door'])
    result['framing_landmarks']=[obj.name for obj in scene.objects if obj.type=='MESH' and obj.name.startswith(('Venue name sign','Venue resource VENUE'))]
    return result
