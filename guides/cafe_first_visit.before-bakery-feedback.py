"""First-visit corrections: a real surface pour and a visitor-side ordering hold."""
import math
import bpy
from mathutils import Vector, Euler
import assets as A
import geometry as G
from drink_scenes import pose, smooth, pour_stream
from motion_paths import camera_path, sequence

IDS = ['latte_top_in_cd_whipout', 'over_shoulder_counter_os_hold', 'cup_eye_hold_whipout', 'room_lights_eye_hold']


def review(gid):
    if gid == 'room_lights_eye_hold':
        return dict(subject='The schematic cafe room: three tables, inward-facing chairs, two windows, rear counter and four pendants',
            angle='Fixed eye-level wide view from the public doorway',
            motion='Hold the room; the pendant lamps switch on once, then remain lit',
            focal_point='Pendant row above the main table; small warm bulb and shade-edge cues show lights coming on',
            composition='Reproduce the schematic horizontal room hierarchy in real depth; open aisle, repeated pendants, quiet rear furniture',
            golden_ratio='Use clear rhythm and balanced furnishing rather than an arbitrary spiral',
            lighting='One real opening-time switch-on event; fixtures never move, no bloom or travelling light',
            contacts='Tables and inward-facing chairs remain on the floor; no chair lowering without an actual person',
            handover='End at the cut; the following dial-in shot is a separate step and remains deferred',
            mobile='Prop or hold the phone still at the public entrance; ask staff before recording their opening routine')
    if gid == 'cup_eye_hold_whipout':
        return dict(subject='One cup and a filled croissant beside it on the same table',
            angle='Cup-height close-up rising into a high paired composition',
            motion='Steam rises, then a small diagonal lean and changing pitch reveal the pastry; continue toward its filling',
            focal_point='Cup rim first, then the cup-and-pastry pairing, then the pastry cut face',
            composition='Cup and plated pastry occupy the diner-side setting; both remain supported and visible during the reveal',
            golden_ratio='Asymmetric pairing and clear negative space, without centring the personal plate on the table',
            lighting='Fixed window-side light with restrained rim glints and faint background',
            contacts='Cup on saucer, croissant on plate, and both place settings fully supported by one tabletop',
            handover='One camera and unchanged props; the next pastry step reuses the exact landing frames',
            mobile='A seated or standing visitor makes a short upward diagonal lean; no hand action or staff access needed')
    pour = gid == IDS[0]
    return dict(
        subject='Milk poured onto coffee, forming one surface heart' if pour else 'Coffee brewing under the public-facing spout, with the order board above',
        angle='Reachable overhead close-up' if pour else 'Steady medium oblique view from the customer side of the counter',
        motion='Milk jug tips, a connected stream pours, a flat milk patch spreads, then the phone whips right' if pour else 'Hold the phone steady while espresso flows into the supported cup and steam rises',
        focal_point='The real milk landing point inside the rim' if pour else 'Cup and spout in the lower third; order board above',
        composition='Cup handle and saucer orient the overhead shot; no floating rosetta strokes' if pour else 'Rebuild the schematic cup/machine hierarchy in depth; omit a full person and keep background subdued',
        golden_ratio='Clear action and usable phone height take priority over forcing a mathematical ratio',
        lighting='Fixed broad side light and quiet rim highlights; no animated fixtures or bloom',
        contacts='Cup touches saucer, saucer touches counter, liquid stays below the cup rim, stream joins source to liquid',
        handover='Brief right-whip landing on the entrance; do not replay its whole shot' if pour else 'Spoken ordering shot; stop before the deferred front-camera sip',
        mobile='Film from visitor space; overhead phone stays below two metres; no staff-side access or equipment control')


def jug():
    before = set(bpy.data.objects)
    G.lathe('Open milk pitcher', [(0,0),(.037,0),(.043,.012),(.045,.09),(.040,.112),
            (.036,.112),(.037,.09),(.034,.009),(0,.009)], (0,0,0), 48)
    # A broad pouring lip, rather than the kettle spout used by unrelated guides.
    G.tube('Milk pitcher pouring lip', [(-.034,-.014,.110),(-.061,0,.115),(-.034,.014,.110)], .0024)
    G.tube('Milk pitcher handle', [(.038,0,.09),(.073,0,.086),(.075,0,.030),(.039,0,.026)], .004)
    return A.group('Milk pitcher entering from the edge', before, role='support',
                   reason='Pitcher and pouring lip stay rigid; the supporting hand is outside this tight crop')


def pour(scene, spec):
    from drink_scenes import counter
    counter(); A.saucer(); A.cup(); A.fixed_side_light((0,0,.91))
    pitcher = jug()
    milk_z = .902
    # The milk is a thin patch ON the coffee plane. Never scale world-space Z:
    # that made the old rosetta rise through the liquid and cup as it appeared.
    n = 96
    points = []
    for i in range(n):
        t = 2*math.pi*i/n
        points.append((.0018*16*math.sin(t)**3,
                       .0018*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))+.005,
                       0))
    mesh = bpy.data.meshes.new('Flat milk heart mesh')
    mesh.from_pydata([(0,0,0)]+points, [], [(0,i+1,(i+1)%n+1) for i in range(n)])
    mesh.update()
    milk = bpy.data.objects.new('Milk spreading on coffee surface', mesh)
    bpy.context.collection.objects.link(milk); G.finish(milk,milk.name)
    milk.location=(0,0,milk_z)
    A.tag(milk,'hero','One flat milk patch spreads at the receiving liquid surface; no detached floating strokes')
    for t,s in [(0,.0001),(.75,.0001),(1.3,.28),(2.15,.76),(2.85,1),(4.8,1)]:
        pose(milk,t,scale=(s,s,1))
    # One connected tapered stream, oriented from the actual moving lip each frame.
    stream=A.tag(G.lathe('Milk stream from pitcher lip',[(.0019,0),(.0014,1)],(0,0,0),12),
                 'hero','The stream begins at the actual lip and ends on the coffee, inside its rim')
    contacts=[]
    for f in range(1,73):
        t=(f-1)/15
        active=.68<=t<=2.90
        tilt=math.radians(-31*smooth((t-.15)/.55)*(1-smooth((t-2.9)/.55)))
        # Keep the pouring lip at the same horizontal contact point while tipping.
        lip=Euler((0,tilt,0)).to_matrix()@Vector((-.061,0,.115))
        aim=Vector((.008,.012,1.032+.035*(1-smooth((t-.1)/.65))+.045*smooth((t-2.9)/.6)))
        pos=aim-lip
        pos.x+=.10*(1-smooth((t-.10)/.55))
        pos.x+=.13*smooth((t-3.05)/.6)
        pose(pitcher,t,location=pos,rotation=(0,tilt,0))
        tip=pos+lip; end=Vector((.008,.012,milk_z))
        direction=end-tip
        pose(stream,t,location=tip,rotation=direction.to_track_quat('Z','Y').to_euler(),
             scale=(1 if active else .0001,1 if active else .0001,direction.length if active else .0001))
        if active:contacts.append(dict(frame=f,lip=list(tip),landing=list(end),inside_cup=end.xy.length<.045))
    cam=camera_path('Overhead milk pour then right whip',[
        (0,(.015,-.015,1.30),(0,0,.90)),(1.2,(.015,-.015,1.30),(0,0,.90)),
        (3.5,(.018,-.012,1.26),(0,0,.902)),(4.25,(.018,-.012,1.26),(0,0,.902)),
        (4.733,(.018,-.012,1.26),(.56,0,1.15))],4.8,43)
    result=sequence(cam,4.8,actions=[
        'A visible pitcher tips and pours onto the supported coffee; one flat milk heart spreads inside the rim',
        'After a short hold the phone whips right; the contextual guide lands briefly on the actual entrance'])
    result.update(pour_contacts=contacts, milk_surface_z=milk_z, milk_patch_local_z=0,
                  milk_patch_max_radius_m=max(math.hypot(x,y) for x,y,_ in points),
                  transition_out='right_whip', probe_frames=[1,14,25,38,48,64,72])
    result['source_adaptations']=['Replace rising rosetta geometry with a planar milk patch and real pouring source',
                                 'The cropped pitcher is operated by a person outside the frame; no full person is generated']
    return result


def order(scene,spec):
    # Same visual hierarchy as the original schematic: cup below a subdued machine.
    A.tag(G.block('Customer counter top',(0,.27,.99),(1.65,.95,.055),.014),
          'structure','Cup and saucer rest on the accessible front counter')
    A.tag(G.block('Public counter front',(0,-.18,.74),(1.65,.045,.47),.010),
          'background','The front face identifies the customer side')
    A.tag(G.block('Coffee machine public face',(.06,.39,1.30),(.58,.26,.48),.035),
          'background','Quiet machine outline matches the schematic without a full staff actor')
    A.tag(G.block('Machine drip tray',(.06,.17,1.028),(.42,.26,.025),.008),
          'support','Cup and saucer have a continuous physical support under the spout')
    A.saucer((-.035,.095,1.0405)); cup=A.cup((-.035,.095,1.0505),name='Ordered coffee')
    spout=(-.035,.095,1.325)
    A.tag(G.tube('Public-facing espresso outlet',[(.02,.275,1.35),(-.035,.19,1.35),spout],.007),
          'support','Outlet physically reaches above the receiving cup')
    liquid=next(o for o in cup.children_recursive if o.name.endswith('coffee surface'))
    for t,z in [(0,.045),(.7,.045),(3.9,.106),(5.4,.106)]:pose(liquid,t,location=(0,0,z-.106))
    # Flow ends at the rising liquid plane, not through it or above empty air.
    stream=A.tag(G.lathe('Espresso into ordered cup',[(.0019,0),(.0016,1)],(0,0,0),12),
                 'hero','Espresso joins the machine outlet to the actual rising liquid')
    samples=[]
    for f in range(1,82):
        t=(f-1)/15;u=smooth((t-.7)/3.2);z=1.0505+.045+.061*u
        end=Vector((-.035,.095,z));delta=end-Vector(spout);on=.7<=t<=3.9
        pose(stream,t,location=spout,rotation=delta.to_track_quat('Z','Y').to_euler(),
             scale=(1 if on else .0001,1 if on else .0001,delta.length if on else .0001))
        # Match the interpolated surface exactly, frame by frame.
        pose(liquid,t,location=(0,0,z-1.0505-.106))
        if on:samples.append(dict(frame=f,start=list(spout),end=list(end),liquid_z=z))
    board=A.menu_board((-.06,.24,1.71),title='COFFEE',selected='HOUSE LATTE',right='PRICE',rows=[('ESPRESSO','PRICE'),('FILTER','PRICE')])
    board.scale=(.60,)*3
    for j in range(2):
        steam=A.tag(G.tube('Steam from the ordered coffee',[
            (-.035+.005*math.sin(k*.7+j),.095+j*.008,1.17+k*.012) for k in range(9)],.0007),
            'background','Gentle rising steam makes the supported hold readable')
        for t,z in [(0,0),(1,.010),(2,.003),(3,.014),(4,.004),(5.4,.012)]:pose(steam,t,location=(0,0,z))
    A.fixed_side_light((0,.1,1.35))
    cam=camera_path('Visitor-side schematic ordering hold',[
        (0,(.08,-.62,1.49),(-.015,.19,1.30)),(5.333,(.08,-.62,1.49),(-.015,.19,1.30))],5.4,43)
    result=sequence(cam,5.4,actions=[
        'Hold the phone from the visitor side with the menu above and receiving cup below',
        'Espresso runs from the actual outlet into the supported cup; its liquid rises and steam drifts'])
    result.update(order_pour_contacts=samples,probe_frames=[1,15,30,45,60,72,81],static_hold=False)
    result['source_adaptations']=['Object-only remake of the schematic cup/machine composition; no shoulder, face or full staff model',
                                 'Do not append a front-camera sip while people scenes remain deferred']
    return result


def build(scene,spec):
    if spec['id']=='room_lights_eye_hold':return lights_on(scene,spec)
    if spec['id']=='cup_eye_hold_whipout':return morning_pair(scene,spec)
    return pour(scene,spec) if spec['id']==IDS[0] else order(scene,spec)


def morning_pair(scene,spec):
    from cinematic_locations import filled_pastry
    A.table((0,.40,0),radius=.68)
    A.saucer((-.16,-.11,.785));A.cup((-.16,-.11,.795))
    A.plate((.16,.09,.785));filled_pastry((.16,.09,.794))
    A.fixed_side_light((0,0,.88))
    for j in range(2):
        steam=A.tag(G.tube('Cup steam beside the pastry',[
            (-.16+.006*math.sin(k*.7+j),-.11+j*.009,.925+k*.014) for k in range(8)],.0008),
            'background','Steam is the real action during the opening supported hold')
        for t,z in [(0,0),(1,.012),(2,.004),(3,.018),(4,.006),(5,.014),(6,.003),(7,.016),(8.4,.006)]:pose(steam,t,location=(0,0,z))
    cam=camera_path('One table cup to neighbouring croissant',[
        (0,(-.18,-.63,1.03),(-.16,-.11,.89)),(1.5,(-.18,-.63,1.03),(-.16,-.11,.89)),
        (3.6,(-.16,-.65,1.42),(-.005,-.015,.86)),(5,(-.12,-.60,1.44),(.01,-.01,.85)),
        (6.3,(.035,-.43,1.30),(.13,.075,.84)),(8.333,(.12,-.32,1.22),(.16,.09,.84))],8.4,36)
    result=sequence(cam,8.4,5,[
        'Hold on the steaming cup, then rise diagonally to reveal the filled croissant beside it on the same table',
        'Continue toward that pastry and its filling, without moving props, adding hands or cutting to another scene'],
        next_guide='pastry_tear_open',landing=5)
    result.update(probe_frames=[1,23,46,69,76,96,126],
                  framing_landmarks=['Cup hollow ceramic body','Plate with formed rim'])
    result['source_adaptations']=['Owner replaces disconnected whip/pastry takes with one coherent cup-and-pastry table scene',
                                 'Use the supported filled-pastry alternative; do not pretend a hand-free pastry is tearing itself']
    return result


def lights_on(scene,spec):
    import venue_assets as V
    for x,y in [(0,.65),(-1.45,2.0),(1.45,2.0)]:
        root=V.dining_table((x,y,0),settings=False)
        for o in root.children_recursive:
            if o.type=='MESH':A.tag(o,'hero' if x==0 else 'background','Table and inward-facing seats follow the existing schematic; keep the aisle clear')
    V.window((-1.50,3.10,1.55));V.window((1.50,3.10,1.55))
    A.tag(G.block('Schematic rear cafe counter',(0,3.20,.54),(1.65,.52,1.08),.018),
          'background','Subdued rear counter in the schematic room; camera stays outside the work area')
    A.tag(G.tube('Pendant ceiling track',[(-2.25,1.65,2.85),(2.25,1.65,2.85)],.006),
          'background','A single open structural line locates the pendants without adding walls')
    events=[]
    for i,x in enumerate([-1.8,-.6,.6,1.8]):
        A.tag(G.tube('Pendant cord',[(x,1.65,2.85),(x,1.65,2.38)],.004),
              'background','Pendant rhythm follows the original schematic')
        A.tag(G.lathe('Pendant shade',[(.03,.09),(.065,.07),(.12,0),(.117,-.006)],(x,1.65,2.30),32),
              'support','A grounded fixture silhouette; no glowing haze around the room')
        bulb=A.ellipsoid('Warm switched-on bulb',(x,1.65,2.29),(.025,.025,.018),
                         'lighting_cue','This small warm bulb explicitly shows the opening-time switch-on')
        rim=A.tag(G.tube('Warm lit pendant lip',[(x+.116*math.cos(k*math.tau/40),1.65+.116*math.sin(k*math.tau/40),2.294) for k in range(41)],.0018),
                  'lighting_cue','A thin yellow line indicates a lit fixture; no bloom, moving light or broad opaque fill')
        # A gentle visibility transition of warm annotations, not moving furniture.
        events.append(dict(index=i,starts=1.25+i*.12,ends=1.65+i*.12,objects=[bulb.name,rim.name]))
    A.fixed_side_light((0,1.2,1.4))
    cam=camera_path('Fixed doorway view of schematic cafe opening',[
        (0,(0,-3.0,1.52),(0,1.45,1.42)),(5.133,(0,-3.0,1.52),(0,1.45,1.42))],5.2,32)
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    for event in events:
        rim=bpy.data.objects[event['objects'][1]]
        projected=[world_to_camera_view(scene,cam,rim.matrix_world@v.co).x for v in rim.data.vertices]
        event['pixel_x_range']=[max(0,math.floor(min(projected)*540)-3),min(540,math.ceil(max(projected)*540)+3)]
    result=sequence(cam,5.2,actions=[
        'Hold the same wide room arrangement as the schematic: tables, inward chairs, windows, counter and repeated pendants',
        'The lamps switch on once, shown by restrained warm bulb and lip highlights; the camera and furniture stay fixed'])
    result.update(lights_on_events=events,probe_frames=[1,19,24,28,34,55,78],static_hold=False)
    result['source_adaptations']=['The schematic description mentions a baker but its actual elements contain only furnishings; preserve that object-only composition',
                                 'Omit chair-lowering and people until a believable model/action is explicitly resumed',
                                 'Warm contour visibility marks a single staff-operated opening-time switch; no moving illumination is invented']
    return result
