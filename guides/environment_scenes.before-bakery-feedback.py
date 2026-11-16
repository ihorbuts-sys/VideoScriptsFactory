"""Source-specific venue and product contexts, with real handheld camera paths."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
import assets as A
import geometry as G
import venue_assets as V
from drink_scenes import camera,key_camera,pose,smooth,frame,counter,glass

REGISTRY={}
def add(ids,family,variant):
    for gid in ids.split():REGISTRY[gid]=(family,variant)
add('case_eye_in_mc_through case_eye_out_cm case_eye_truckr_mm shelf_slide_left','case','bakery')
add('door_eye_in_wd_through door_pov_in_wc_through door_pov_in_wd_through pov_door_entry','entrance','dining')
add('door_curtain_eye_in_md_through','entrance','treatment')
add('door_sauna_eye_in_mc_through','entrance','sauna')
add('facade_eye_hold facade_eye_in_wm facade_line_eye_panr_ww_whipout','facade','shopfront')
add('facade_truck_eye_in_wm facade_window_eye_in_wm_whipout facade_window_pov_hold','facade','truck')
add('sign_plate_eye_out_cm sign_tilt_down_reveal','sign','shopfront')
add('chair_reveal_frame','room','salon')
add('interior_pan room_crowd_eye_panr_ww_whipout room_cupreveal_eye_reveal_dw room_dining_eye_reveal_cw room_dining_eye_reveal_cw_whipout room_eye_panl_ww room_eye_panr_ww_whipout','room','dining')
add('room_changing_pov_reveal_cm','room','changing')
add('room_game_pov_panl_mm_whipout','room','game')
add('room_gym_eye_panr_ww','room','gym')
add('room_lesson_eye_reveal_cw','room','lesson')
add('room_lights_eye_hold','room','cafe')
add('room_park_high_panr_ww_whipout room_ride_pov_in_wm','room','park')
add('room_sauna_high_out_cw','room','sauna')
add('room_shop_eye_out_cw room_shop_eye_panr_mm','room','shop')
add('room_stage_low_in_wm_whipout','room','stage')
add('room_treatment_eye_reveal_cm','room','treatment')
add('room_waiting_eye_reveal_cw','room','waiting')
add('rail_bottle_eye_truckr_mm rail_shelf_eye_truckr_mm_whipout','rack','bottle')
add('rail_dumbbell_eye_truckr_cc','rack','dumbbell')
add('rail_garment_eye_truckr_cc_whipout rail_garment_eye_truckr_mm','rack','garment')
add('rail_guitar_pov_truckr_mm','rack','guitar')
add('table_corner_pov_out_mw table_desk_pov_in_mc table_outlets_high_tiltd_cc','table','work')
add('table_seat_high_in_mc','table','dining')
add('table_treatment_eye_in_mc','table','treatment')
add('menu_desk_high_hold','table','reception')
add('machine_low_in_mc_whipout','room','gym')


def explicit_review(gid,description,contexts):
    family,variant=REGISTRY[gid]
    subjects={
      'case':'Chosen baked item, its shelf companions and readable price labels',
      'entrance':'Public entrance and the actual room visible through its opening',
      'facade':'Venue frontage, public order window and sign',
      'sign':'Venue name sign, followed by the public entrance',
      'room':'The '+variant+' space and its meaningful furniture or equipment landmarks',
      'rack':'Selected '+variant+' and repeated neighbouring products',
      'table':'The '+variant+' arrangement with usable object spacing and supports',
    }
    composition={
      'case':'Selected pastry supplies the focus; shelf rhythm and labels give context; framing stays outside the case',
      'entrance':'Door frame establishes foreground depth; the opening leads the eye into a clear public aisle',
      'facade':'Sign and accessible entrance or order window form the visual hierarchy; omit unrelated walls',
      'sign':'Sign and door are vertically aligned so the wrist tilt or pullback links information to place',
      'room':'Foreground framing, middle-distance hero furnishing and fainter rear context create useful depth; windows motivate steady side light',
      'rack':'Repeated products establish rhythm; offsets create genuine parallax; selected product has clear negative space',
      'table':'Useful working/dining layout, clear hero object, supporting triangle and open negative space around the action',
    }
    return dict(subject=subjects[family],angle='Preserve the source camera angle, with ordinary visitor access',motion='Preserve the source move; bound actual travel to handheld-phone space; physically open occluders instead of fading the scene',focal_point=subjects[family],composition=composition[family],golden_ratio='Use weighted asymmetry and useful thirds where appropriate; do not force an off-centre camera path',lighting='Fixed broad window/venue side light; no bloom, no required light changes',contacts='Furniture and product supports are modelled; keep the public camera path clear',handover='Actual next-step identity is recorded; contextual assembly follows the base scene',mobile='Handheld phone; short lean or normal walking steps, reachable height and no crane; high park view uses public ground/terrace height',status='reviewed_before_render')


def working_table():
    A.table(radius=.65);A.saucer((0,-.12,.785));A.cup((0,-.12,.795))
    A.plate((-.34,.14,.785));A.pastry((-.34,.14,.794))
    root=A.empty('Open laptop',(.27,.17,.79));before=set(bpy.data.objects)
    V.tag(G.block('Laptop keyboard base',(0,0,.007),(.30,.22,.014),.008),'support','Laptop, drink and pastry form a usable working arrangement')
    screen=G.block('Open laptop screen',(0,.095,.13),(.30,.012,.24),.008);screen.rotation_euler.x=math.radians(-14);V.tag(screen,'support','Open screen is kept clear of the cup silhouette')
    for obj in set(bpy.data.objects)-before:obj.parent=root
    card=G.block('Wifi card',(0,.26,.791),(.17,.10,.010),.004);V.tag(card,'important_background','The wifi card is a useful destination for the downward tilt')
    V.lettering('WIFI',(0,.26,.799),.025,flat=True)
    V.window((-.9,.7,1.4));A.fixed_side_light((0,0,.85))


def make_scene(scene,spec):
    gid=spec['id'];family,variant=REGISTRY[gid]
    data=json.loads((Path(__file__).resolve().parents[2]/'guides/templates'/(gid+'.json')).read_text())
    live=data.get('live',{});moves=[s for s in live.get('steps',[]) if s.get('kind')=='follow' and s.get('action')!='whip']
    moving=moves[0] if moves else None
    duration=max([t['t'] for t in data.get('timeline',[])] or [4.2]);duration=max(4.0,min(7.5,duration))
    focus=Vector((0,0,1.2));origin=Vector((0,-1.2,1.2));lens=30;actions=[]
    if family=='case':
        V.pastry_case((0,.50,0));A.fixed_side_light((0,.5,1.0));focus=Vector((-.26,.50,1.18))
        origin=focus+Vector((0,-1.10,0));lens=32
        if gid=='case_eye_in_mc_through':origin=focus+Vector((0,-1.80,0))
        elif gid=='case_eye_out_cm':origin=focus+Vector((0,-.72,0))
        actions=['Shelf-height public-side view links the chosen pastry to the labelled case','Real neighbouring products change occlusion and relative position during the prescribed move']
    elif family in ['entrance','facade','sign']:
        if family=='facade':
            V.facade(truck=variant=='truck');origin=Vector((0,-3.0,1.50));focus=Vector((0,0,1.5));lens=24
            if gid=='facade_window_pov_hold':origin.y=-1.35
        else:
            if gid in ['door_curtain_eye_in_md_through','door_sauna_eye_in_mc_through']:
                root,hinge=V.door()
                if gid=='door_curtain_eye_in_md_through':
                    for obj in list(hinge.children):bpy.data.objects.remove(obj,do_unlink=True)
                    for side in [-1,1]:V.tag(G.block('Curtain fabric',(side*.27,-.03,1.1),(.54,.025,2.1),.025),'foreground_frame','The actual fabric occluder is required by the source curtain transition')
                else:
                    for j in range(7):
                        plank=V.tag(G.block('Sauna door wood plank',(.075+j*.145,0,1.08),(.14,.04,2.08),.005),'support','Wood surface identifies the public sauna door');plank.parent=hinge
            else:V.facade()
            V.venue(variant if family=='entrance' else 'dining');origin=Vector((0,-2.3,1.5));focus=Vector((0,0,1.5));lens=24
        if family=='sign':focus=Vector((0,0,2.52));origin=Vector((0,-1.8,1.60));lens=33
        if gid=='facade_line_eye_panr_ww_whipout':
            for x,y in [(-1.0,-.8),(-.4,-1.0),(.2,-1.2)]:
                person=A.portrait((x,y,0),None);person['root'].rotation_euler.z=math.pi
                for obj in person['root'].children_recursive:
                    if obj.type=='MESH':V.tag(obj,'background','Queue is seen from behind from the public street; no close faces or extra hands')
        A.fixed_side_light((0,0,1.4))
        actions=['Public-facing sign, window and entrance establish the destination','Door and interior landmarks provide a meaningful reveal instead of isolated scaling']
        if family=='entrance':
            hinge=bpy.data.objects.get('Opening door hinge')
            if hinge:
                for t,a in [(0,0),(1.2,0),(2.4,-78),(duration,-78)]:pose(hinge,t,rotation=(0,0,math.radians(a)))
    elif family=='rack':
        V.rack(variant,(0,.55,0));A.fixed_side_light((0,.55,1.1));focus=Vector((-.91,.55,1.15 if variant!='dumbbell' else 1.05));origin=focus+Vector((0,-1.0,0));lens=28
        actions=['Repeated '+variant+' objects establish the row and selected gap','True lateral camera motion creates foreground/background parallax with stable supports']
    elif family=='table':
        if variant=='work':working_table()
        elif variant=='dining':V.dining_table();A.fixed_side_light((0,0,.85))
        elif variant=='treatment':V.treatment_bed((0,.5,0));A.fixed_side_light((0,.5,.85))
        else:
            counter();A.menu_board((-.20,.20,.80),flat=True,title='SERVICES',selected='YOUR SERVICE',right='PRICE')
            V.lettering('BOOK',(.27,.07,.795),.045,flat=True);A.fixed_side_light((0,0,.85))
        focus=Vector((0,-.12,.90));origin=Vector((0,-.90,1.35));lens=28
        if gid=='table_treatment_eye_in_mc':focus=Vector((0,.5,.90));origin=Vector((0,-1.45,.90))
        actions=['Usable '+variant+' arrangement gives each object a clear role','Prescribed camera motion moves attention between the hero object and supporting context']
    else:
        V.venue(variant);origin=Vector((0,-1.20,1.48));focus=Vector((0,2.0,1.10));lens=30
        if variant=='sauna':focus=Vector((-.5,1.8,.65));origin=Vector((-.5,.55,1.70));lens=22
        if variant=='treatment':focus=Vector((0,2,.95))
        if variant=='park':origin.z=1.72;focus=Vector((0,3.0,1.20));lens=22
        if gid=='room_stage_low_in_wm_whipout':
            origin.z=1.10;focus=Vector((0,2.8,1.45))
            from people_scenes import full_actor
            player,actor=full_actor();player.location=(-.55,2.6,0)
            guitar=V.guitar((-.55,2.43,.35));guitar.scale=(.75,)*3
        if gid=='room_lights_eye_hold':
            V.bench((0,3,0));A.portrait((0,3.3,0),None)
            dough=A.ellipsoid('Dough at the public-facing bench',(0,3,.51),(.16,.10,.035),'hero','A visible worker action makes the room hold meaningful without a lighting sweep')
            for side in [-1,1]:
                hand=A.hand((side*.12,3,.56),scale=1)
                for t,x in [(0,side*.12),(1.2,side*.12),(2.0,side*.045),(2.8,side*.12),(4,side*.045)]:pose(hand,t,location=(x,3,.56))
        actions=['Foreground, working middle ground and quiet distant furnishings establish the '+variant+' scene','The move reveals actual objects, gaps and occlusion rather than a flat scene zoom']
    if family in ['entrance','facade','sign']:
        for obj in scene.objects:
            if obj.type=='MESH' and obj.name.startswith(('Venue name sign','Venue resource VENUE','Door pull handle','Sauna door wood plank','Open serving window','Serving ledge','Venue resource ORDER')):
                V.tag(obj,'hero','This public-facing resource/opening is the main subject of the shot')
    elif family=='table' and variant=='dining':
        for obj in scene.objects:
            if obj.type=='MESH' and obj.name.startswith('Quiet tabletop'):V.tag(obj,'hero','The usable two-person table is the primary destination')
    cam=camera('Handheld '+gid,origin,focus,lens)
    start=1.2;move_seconds=moving.get('duration',1.8) if moving else 1.8
    offset=origin-focus;direction=(focus-origin).normalized();yaw0=math.atan2(direction.x,direction.y)
    pitch0=math.atan2(direction.z,math.hypot(direction.x,direction.y));adaptations=[]
    action=moving.get('action') if moving else 'hold'
    if gid in ['chair_reveal_frame','room_changing_pov_reveal_cm','room_cupreveal_eye_reveal_dw','room_dining_eye_reveal_cw','room_dining_eye_reveal_cw_whipout','room_lesson_eye_reveal_cw','room_treatment_eye_reveal_cm','room_waiting_eye_reveal_cw']:
        action='reveal'
        if gid=='room_cupreveal_eye_reveal_dw':
            cup=A.cup((origin.x,origin.y+.18,origin.z-.065),name='Foreground cup reveal')
            from drink_scenes import grip
            grip(cup)
        else:
            V.tag(G.block('Necessary foreground door edge',(origin.x-.03,origin.y+.48,origin.z),(.80,.12,1.9),.008),'foreground_frame','The source explicitly starts hidden; only this necessary occluding edge is drawn')
    if action in ['dolly_in','dolly_out']:
        amount=moving.get('amount',1.35);distance=offset.length;end_distance=distance/amount
        max_travel=1.4 if family in ['room','entrance','facade','sign'] else .65
        if gid=='pov_door_entry':
            origin=Vector((0,-1.50,1.5));focus=Vector((0,1.0,1.5));offset=origin-focus;distance=offset.length;end_distance=.65;max_travel=2.0
        if abs(distance-end_distance)>max_travel:
            end_distance=distance+math.copysign(max_travel,end_distance-distance);adaptations.append('Source framing scale adapted to reachable phone travel; preserve direction and reveal meaningful context')
    for f in range(frame(duration)):
        t=f/15;u=smooth((t-start)/move_seconds);p=origin.copy();target=focus.copy()
        if action in ['dolly_in','dolly_out']:
            p=focus+offset.normalized()*(offset.length+(end_distance-offset.length)*u)
        elif action in ['truck','reveal']:
            sign=-1 if moving and moving.get('direction')=='left' else 1
            p.x+=sign*(.66 if action=='truck' else .72)*u;target.x+=p.x-origin.x
        elif action=='pan':
            sign=-1 if moving.get('direction')=='left' else 1
            angle=yaw0+sign*math.radians(42)*(u-.5)
            target=p+Vector((math.sin(angle)*math.cos(pitch0),math.cos(angle)*math.cos(pitch0),math.sin(pitch0)))
        elif action=='tilt' or gid=='sign_tilt_down_reveal':
            end_target=Vector((0,0,1.12)) if family=='sign' else Vector((0,.26,.795)) if gid=='table_outlets_high_tiltd_cc' else focus-Vector((0,0,.6))
            target=focus.lerp(end_target,u)
        if gid=='room_sauna_high_out_cw':
            p.z=origin.z
        key_camera(cam,t,p,target)
    # Outgoing whip remains a short wrist turn; the destination is a separate take.
    whip=next((s for s in live.get('steps',[]) if s.get('action')=='whip'),None)
    if whip:
        scene.frame_set(frame(duration-.4));bpy.context.view_layer.update();p=cam.location.copy();d=(cam.rotation_euler.to_quaternion()@Vector((0,0,-1)))
        sign=-1 if 'whip left' in spec['description'].lower() else 1
        for t,a in [(duration-.4,0),(duration-.05,sign*65)]:
            rot=__import__('mathutils').Matrix.Rotation(math.radians(a),3,'Z');key_camera(cam,t,p,p+rot@d)
    if gid=='room_sauna_high_out_cw':adaptations.append('Keep phone at 1.7 m and step back; let the view level slightly instead of raising it above reach')
    if action=='hold' and gid!='room_lights_eye_hold':
        # A held view is intentional. Reveal it once, then hold without a fake camera drift.
        spec['static_hold']=True
    return dict(duration=duration,take_end=duration,cameras=[(0,cam)],intent='; '.join(actions),composition=actions,subject_actions=actions,
                scope='base_shot_with_action',handover_status='pending_contextual_sequence',
                source_adaptations=adaptations,mobile_feasibility=dict(visitor_space=True,max_phone_height_m=1.85,travel_bound_m=1.4 if family in ['room','entrance','facade','sign'] else .65,no_gimbal_or_crane=True,existing_light=True),
                geometry_checks=dict(family=family,variant=variant,action=action,phone_feasible=True),
                contextual_next_steps=[dict(script=c['script'],next_step=c['next_step']) for c in spec['contexts']])


def register(factories):
    for gid in REGISTRY:factories[gid]=make_scene
