"""Reusable native venue furnishings with explicit composition roles and contacts."""
import math
import bmesh
import bpy
from mathutils import Vector,Matrix
import assets as A
import geometry as G


def tag(obj,role='support',reason='Relevant venue landmark with a clear silhouette'):
    return A.tag(obj,role,reason)


def chair(position=(0,0,0),rotation=0,salon=False):
    # The backrest is on local +Y, so the seated person faces local -Y.
    before=set(bpy.data.objects)
    if salon:
        G.lathe('Salon chair foot',[(0,0),(.24,0),(.25,.02),(.05,.08),(.04,.43)],(0,0,0),32)
        G.block('Salon chair upholstered seat',(0,0,.47),(.48,.43,.09),.06)
        G.block('Salon chair upholstered back',(0,.18,.75),(.48,.08,.48),.05)
        for side in [-1,1]:G.tube('Salon chair arm',[(side*.24,-.15,.51),(side*.24,-.15,.68),(side*.24,.17,.68)],.025)
        G.tube('Salon footrest',[(-.18,-.42,.23),(-.18,-.30,.45),(.18,-.30,.45),(.18,-.42,.23)],.018)
    else:
        G.lathe('Dining chair seat',[(0,.43),(.20,.43),(.21,.46),(.19,.48),(0,.48)],(0,0,0),32,ellipse=.85)
        for x in [-.14,.14]:
            for y in [-.12,.12]:G.tube('Dining chair leg',[(x,y,.43),(x*1.2,y*1.2,.02)],.018)
        G.tube('Dining chair bent back',[(-.17,.12,.46),(-.20,.16,.83),(0,.20,.90),(.20,.16,.83),(.17,.12,.46)],.018)
    root=A.group('Reusable salon chair' if salon else 'Reusable dining chair',before,position,'support','Usable seat height and coherent legs/back; kept subordinate to the shot subject')
    root.rotation_euler.z=rotation;return root



def pendant(position,role_lit='lighting_cue'):
    """A lit ceiling pendant: cord from the ceiling point, shade, warm bulb and a thin warm lip line."""
    x,y,top=position
    tag(G.tube('Pendant cord',[(x,y,top),(x,y,top-.47)],.004),'background','Pendant rhythm locates the ceiling without drawing walls')
    tag(G.lathe('Pendant shade',[(.03,.09),(.065,.07),(.12,0),(.117,-.006)],(x,y,top-.55),32),'support','A grounded fixture silhouette; no glowing haze')
    A.ellipsoid('Warm switched-on bulb',(x,y,top-.56),(.025,.025,.018),role_lit,'A small warm bulb shows the room is lit')
    tag(G.tube('Warm lit pendant lip',[(x+.116*math.cos(k*math.tau/40),y+.116*math.sin(k*math.tau/40),top-.556) for k in range(41)],.0018),role_lit,'A thin warm line marks a lit fixture; no bloom or moving light')


def plant(position=(0,0,0),height=1.0):
    """A floor plant: tapered pot, soil disc and arching leaves of mixed length."""
    before=set(bpy.data.objects);s=height
    G.lathe('Plant pot',[(0,0),(.11*s,0),(.15*s,.30*s),(.16*s,.32*s),(0,.32*s)],(0,0,0),32)
    for k in range(9):
        a=k*2.4;lean=.18+.07*(k%3);top=(.55+.12*(k%4))*s
        tip=(lean*math.cos(a)*s,lean*math.sin(a)*s,top)
        leaf=A.ellipsoid('Plant leaf',(tip[0]*.6,tip[1]*.6,.32*s+(top-.32*s)*.6),(.035*s,.035*s,(top-.30*s)*.55),'support','Leaves give the room a lived-in detail')
        leaf.rotation_euler=(Vector((0,0,1)).rotation_difference(Vector(tip)-Vector((0,0,.32*s))).to_euler())
        G.tube('Plant stem',[(0,0,.31*s),tip],.004)
    return A.group('Potted floor plant',before,position,'background','Interior detail that reads the room as a cared-for cafe')


def daylight_patch(corners,name='Daylight on the floor'):
    """Warm outline of the light a glazed opening throws onto the floor, with a few rays inside it."""
    (a,b,c,d)=corners
    for start,end in [(b,c),(d,a),(c,d)]:
        tag(G.tube(name,[(*start,.004),(*end,.004)],.004),'lighting_cue','Fixed daylight through the opening marks where the room is brightest')
    for t in [.25,.5,.75]:
        start=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,.004);end=(d[0]+(c[0]-d[0])*t,d[1]+(c[1]-d[1])*t,.004)
        tag(G.tube(name+' ray',[start,end],.0025),'lighting_cue','Rays point back to the light source')


def salon_tools(position,along=(1,0,0)):
    """Tools left on a styling shelf: hairdryer, aerosol hairspray, round brush, comb and a few cut hair strands."""
    origin=Vector(position);u=Vector(along).normalized();v=Vector((0,0,1)).cross(u)
    def at(a,b,z=0):return origin+u*a+v*b+Vector((0,0,z))
    before=set(bpy.data.objects)
    body=A.ellipsoid('Hairdryer body',at(-.20,0,.045),(.075,.045,.045),'hero','The hairdryer is the clearest salon tool on the shelf')
    body.rotation_euler.z=math.atan2(u.y,u.x)
    G.tube('Hairdryer nozzle',[at(-.27,0,.045),at(-.31,0,.045)],.024)
    G.tube('Hairdryer handle',[at(-.17,.0,.03),at(-.15,.02,.01),at(-.12,.06,.012)],.016)
    G.tube('Hairdryer cord',[at(-.12,.06,.012),at(-.05,.10,.004),at(.02,.13,.004)],.004)
    G.lathe('Hairspray aerosol can',[(0,0),(.024,0),(.025,.01),(.025,.17),(.02,.19),(0,.19)],at(-.02,-.06),32)
    G.lathe('Hairspray cap',[(0,0),(.018,0),(.018,.035),(0,.04)],at(-.02,-.06,.19),24)
    G.tube('Round brush handle',[at(.08,.02,.012),at(.22,.04,.012)],.008)
    for k in range(10):
        a=.11+k*.012
        G.tube('Round brush bristle ring',[at(a,.03,.012)+v*.018*math.cos(t)+Vector((0,0,.018*math.sin(t))) for t in [j*math.tau/12 for j in range(13)]],.0015)
    G.block('Comb spine',at(.12,-.07,.003),(.15,.018,.006),.002)
    for k in range(14):G.tube('Comb tooth',[at(.055+k*.01,-.078,.003),at(.055+k*.01,-.10,.003)],.0012)
    for k in range(7):
        a=.26+k*.018;b=-.05+(k%3)*.03
        G.tube('Cut hair strand',[at(a,b,.002),at(a+.03,b+.012,.002),at(a+.06,b-.004,.002)],.0008)
    return A.group('Salon tools on the shelf',before,(0,0,0),'support','Familiar salon tools give the station a recognisable purpose')


def salon_station(position,facing,sitter=None):
    """A styling chair facing its wall mirror, with a shelf of tools under the mirror and a faint reflection.
    `facing` is the chair yaw; a seated client faces local -Y, so the mirror stands in front of the chair.
    `sitter` is an optional (person, pose) seated in the chair. Returns the mirror centre, chair and sitter roots."""
    seat=Vector(position);forward=Matrix.Rotation(facing,3,'Z')@Vector((0,-1,0));side=Vector((0,0,1)).cross(forward)
    mirror=seat+forward*.62
    seat_root=chair(tuple(seat),facing,salon=True)
    import people
    person=people.place(*sitter,tuple(seat),facing) if sitter else None
    corners=[mirror+side*sx*.40+Vector((0,0,z)) for sx,z in [(-1,.60),(1,.60),(1,1.95),(-1,1.95),(-1,.60)]]
    for c1,c2 in zip(corners,corners[1:]):
        tag(G.tube('Styling mirror frame',[c1,c2],.012),'important_background','The mirror frame tells the viewer this is a styling station')
    shelf=mirror-forward*.14+Vector((0,0,.86))
    top=tag(G.block('Styling station shelf',tuple(shelf),(.85,.28,.035),.008),'support','The shelf carries the tools at the mirror')
    top.rotation_euler.z=facing
    salon_tools(tuple(shelf+Vector((0,0,.018))),tuple(side))
    eye=seat-forward*1.0+Vector((0,0,1.5-seat.z))
    image=mirror+forward*.62
    reflection(lambda:chair(tuple(image),facing+math.pi,salon=True),corners[:4],eye,forward)
    if sitter:reflection(lambda:people.place(*sitter,tuple(image),facing+math.pi),corners[:4],eye,forward,'Person seen in the mirror','important_background')
    return dict(mirror=mirror,chair=seat_root,sitter=person)


def reflection(build,corners,eye,normal,name='Chair seen in the mirror',role='background'):
    """A faint copy seen in the mirror, clipped to what a visitor at `eye` sees through the frame `corners`."""
    before=set(bpy.data.objects);build()
    bm=bmesh.new()
    for obj in [o for o in set(bpy.data.objects)-before if o.type=='MESH']:
        bpy.context.view_layer.update();data=obj.data.copy();data.transform(obj.matrix_world);bm.from_mesh(data);bpy.data.meshes.remove(data)
    for obj in set(bpy.data.objects)-before:bpy.data.objects.remove(obj,do_unlink=True)
    centre=sum(corners,Vector())/len(corners)
    planes=[(corners[0],-normal)]
    for c1,c2 in zip(corners,corners[1:]+corners[:1]):
        n=(c1-eye).cross(c2-eye).normalized()
        if n.dot(centre-eye)>0:n=-n
        planes.append((eye,n))
    for point,direction in planes:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=direction,clear_outer=True)
    # Flattened onto the glass along the visitor's sight lines, so from any phone position it stays inside the frame.
    for vertex in bm.verts:
        ray=vertex.co-eye;vertex.co=eye+ray*((corners[0]-eye).dot(normal)/ray.dot(normal))+normal*.003
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);G.finish(obj,obj.name)
    return tag(obj,role,'The reflection, clipped to the mirror frame, makes the glass read as a mirror')


def dining_table(position=(0,0,0),settings=True):
    before=set(bpy.data.objects);A.table(radius=.54)
    G.lathe('Table pedestal',[(.07,0),(.10,.03),(.04,.10),(.04,.75)],(0,0,0),24)
    chairs=[]
    for side in [-1,1]:
        chairs.append(chair((0,side*.73,0),rotation=math.pi if side<0 else 0))
        if settings:
            y=side*.27;A.plate((0,y,.785));A.fork((side*.20,y,.789))
            # Opposed diners have mirrored utensil sides and a clear shared centre.
            # Opposed diners: the knife turns with its diner, handle toward the chair and edge toward the plate.
            utensil=A.knife((side*-.20,y,.785),'Place-setting knife','background');utensil.rotation_euler.z=math.pi if side>0 else 0
            cup=A.cup((side*.25,y-side*.05,.795),role='background');A.saucer((side*.25,y-side*.05,.785))
    root=A.group('Two-person dining table',before,position,'structure','Two opposed practical settings; clear centre, no overlapping dinnerware')
    for seat in chairs:seat['dining_table_root']=root.name
    return root


def lettering(text,position,size=.12,role='important_background',flat=False):
    data=bpy.data.curves.new('Venue resource lettering','FONT');data.body=text;data.size=size;data.align_x='CENTER';data.extrude=.0005
    obj=bpy.data.objects.new('Venue resource '+text,data);bpy.context.collection.objects.link(obj);obj.location=position
    if not flat:obj.rotation_euler.x=math.pi/2
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');G.finish(bpy.context.object,obj.name)
    return tag(bpy.context.object,role,'Identifies the resource or destination without inventing venue facts')


def window(position=(-1.4,1.6,1.4)):
    before=set(bpy.data.objects)
    for x in [-.55,.55]:G.block('Window side',(x,0,0),(.035,.04,1.6),.005)
    for z in [-.80,0,.80]:G.block('Window crossbar',(0,0,z),(1.13,.04,.035),.005)
    G.block('Window mullion',(0,0,0),(.025,.04,1.60),.004)
    return A.group('Window frame only',before,position,'background','Window frame motivates fixed side lighting; wall and glass wash are omitted')


def door(position=(0,0,0),open_angle=0):
    before=set(bpy.data.objects)
    for x in [-.55,.55]:tag(G.block('Door jamb',(x,0,1.10),(.045,.05,2.2),.006),'structure','Door edge is required to explain the entrance or occlusion')
    tag(G.block('Door lintel',(0,0,2.20),(1.15,.05,.05),.006),'structure','Only the opening frame is drawn; no broad wall fill')
    hinge=A.empty('Opening door hinge',(-.52,0,0));leaf_before=set(bpy.data.objects)
    for x in [0,1.04]:G.block('Glazed door vertical frame',(x,0,1.08),(.03,.035,2.1),.004)
    for z in [.04,1.0,2.12]:G.block('Glazed door rail',(.52,0,z),(1.05,.035,.03),.004)
    G.tube('Door pull handle',[(.91,-.05,.93),(.91,-.08,.95),(.91,-.08,1.17),(.91,-.05,1.19)],.012)
    for obj in set(bpy.data.objects)-leaf_before:
        if obj.parent is None:obj.parent=hinge
        if obj.type=='MESH':tag(obj,'support','A coherent door rotates around its real hinge; no opaque wall masks the room')
    hinge.rotation_euler.z=math.radians(open_angle)
    root=A.group('Public entry door',before,position,'structure','The public opening remains accessible throughout the filming move')
    return root,hinge


def facade(truck=False):
    before=set(bpy.data.objects)
    if truck:
        tag(G.block('Food truck body',(0,.6,1.23),(3.1,1.30,1.85),.12),'structure','Truck body is the subject, not an incidental wall')
        for x in [-1,1]:
            wheel=G.lathe('Truck wheel',[(0,0),(.26,0),(.28,.10),(.24,.14),(0,.14)],(x,-.08,.33),32);wheel.rotation_euler.x=math.pi/2;tag(wheel,'background','Wheels identify the public serving truck')
        tag(G.block('Open serving window',(0,-.08,1.55),(1.8,.06,.85),.025),'support','Serving window is viewed from the customer side')
        tag(G.block('Serving ledge',(0,-.25,1.10),(1.95,.40,.055),.01),'support','Public order ledge supplies the destination')
        lettering('ORDER HERE',(0,-.13,1.83),.12)
    else:
        door();window((-1.25,0,1.25));window((1.25,0,1.25))
        tag(G.block('Venue name sign',(0,0,2.58),(2.6,.07,.40),.018),'important_background','Venue sign establishes the destination; nearby walls are omitted')
        lettering('VENUE',(0,-.05,2.48),.22)
    return A.group('Reusable public shopfront',before,(0,0,0),'structure','Entrance, sign and windows establish the venue from the public street')


def garment(position=(0,0,1.2),role='support'):
    before=set(bpy.data.objects)
    # A fitted garment with sloped shoulders, sleeves and a neckline.
    vertices=[(-.08,0,.45),(-.28,0,.35),(-.40,0,.12),(-.27,0,.06),(-.18,0,.21),(-.20,0,-.40),(.20,0,-.40),(.18,0,.21),(.27,0,.06),(.40,0,.12),(.28,0,.35),(.08,0,.45),(.05,0,.37),(-.05,0,.37)]
    mesh=bpy.data.meshes.new('Garment cut');mesh.from_pydata(vertices,[],[tuple(range(len(vertices)))]);mesh.update();obj=bpy.data.objects.new('Garment with sleeves',mesh);bpy.context.collection.objects.link(obj);G.finish(obj,obj.name)
    solid=obj.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.015
    G.tube('Garment hem',[(-.19,-.012,-.37),(0,-.025,-.39),(.19,-.012,-.37)],.002)
    G.tube('Garment centre seam',[(0,-.015,.34),(.005,-.023,-.15),(0,-.018,-.39)],.0012)
    G.tube('Hanger',[(-.26,0,.38),(0,0,.51),(.26,0,.38),(-.26,0,.38)],.004)
    G.tube('Hanger hook',[(0,0,.51),(0,0,.58),(.025,0,.61),(.045,0,.59)],.004)
    return A.group('Reusable garment and hanger',before,position,role,'Recognisable clothing silhouette and folds, kept attached to one hanger')


def dumbbell(position=(0,0,0)):
    before=set(bpy.data.objects)
    G.tube('Dumbbell grip',[(-.12,0,0),(.12,0,0)],.018)
    for side in [-1,1]:
        obj=G.lathe('Dumbbell weight',[(0,0),(.085,0),(.085,.06),(0,.06)],(side*.12,0,0),24);obj.rotation_euler.y=math.pi/2
    return A.group('Reusable dumbbell',before,position,'hero','Two weights and one grip form a stable complete object on the rack')


def guitar(position=(0,0,0)):
    from pathlib import Path
    source=Path(__file__).resolve().parent/'vendor/innerscene-guitar/guitar.glb'
    if source.exists():
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source))
        for obj in set(bpy.data.objects)-before:
            if obj.type!='MESH':continue
            obj.data.materials.clear();obj.data.materials.append(G.MAT)
            role='hero' if any(word in obj.name.lower() for word in ['soundboard','soundhole','string ','fingerboard','bridge base']) else 'support'
            A.tag(obj,role,'Detailed CC0 acoustic guitar by Innerscene; actual body, sound hole, bridge, frets and six strings')
        return A.group('Reusable acoustic guitar CC0',before,position,'support','Original openly licensed guitar geometry at real-world scale')
    before=set(bpy.data.objects)
    A.ellipsoid('Guitar lower bout',(0,0,.31),(.18,.055,.22));A.ellipsoid('Guitar upper bout',(0,0,.54),(.13,.05,.16))
    G.block('Guitar fretboard',(0,-.01,.91),(.055,.035,.68),.008)
    G.block('Guitar headstock',(.012,0,1.27),(.075,.045,.16),.01)
    for x in [-.015,0,.015]:G.tube('Guitar string',[(x,-.059,.29),(x,-.032,1.30)],.0007)
    for z in [.68,.74,.80,.86,.92,1.0,1.09,1.16]:G.tube('Guitar fret',[(-.027,-.031,z),(.027,-.031,z)],.0008)
    return A.group('Reusable guitar',before,position,'support','Curved bouts, strings and frets identify the instrument, not a generic rectangle')


def rack(kind='garment',position=(0,1,0)):
    before=set(bpy.data.objects)
    if kind=='garment':
        for x in [-1.0,1.0]:G.tube('Clothing rail upright',[(x,0,0),(x,0,1.82)],.018)
        G.tube('Clothing rail',[(-1.0,0,1.82),(1.0,0,1.82)],.018)
        for j,x in enumerate([-.75,-.25,.25,.75]):
            root=garment((x,.06*(j%2),1.22),role='hero' if j==1 else 'support');root.rotation_euler.z=.15*(j%2)
    elif kind=='guitar':
        for x in [-.75,0,.75]:
            instrument=guitar((x,0,.10))
            if x==0:
                for obj in instrument.children_recursive:
                    if obj.type=='MESH':tag(obj,'hero','Selected middle instrument stays clear during the row move')
        G.tube('Instrument stand rail',[(-1,0,.1),(1,0,.1)],.02)
    else:
        for z in [.50,.95]:
            G.block('Shelf supporting surface',(0,0,z),(2.2,.40,.04),.008)
            for j,x in enumerate([-.75,-.25,.25,.75]):
                if kind=='dumbbell':dumbbell((x,0,z+.10))
                else:tag(G.bottle('Display bottle',x,0,z+.02,height=.25,radius=.035),'hero' if j==1 else 'support','Shelf products share a real support; selected item is clearer')
    return A.group('Reusable '+kind+' rack',before,position,'structure','Repeated objects establish rhythm and real near/far parallax')


def pastry_case(position=(0,1,0)):
    before=set(bpy.data.objects)
    for z in [.78,1.12]:
        tag(G.block('Pastry shelf',(0,0,z),(2.3,.50,.035),.008),'structure','Real shelf supports a readable row of baked goods')
        for j,x in enumerate([-.78,-.26,.26,.78]):
            A.plate((x,0,z+.0175),'background');A.pastry((x,0,z+.0265))
            lettering('PRICE',(x,-.28,z-.065),.035,role='background')
    for x in [-1.16,1.16]:tag(G.tube('Case side support',[(x,-.26,.6),(x,-.26,1.42),(x,.30,1.42)],.012),'background','Case edges supply depth without an opaque front glass layer')
    return A.group('Reusable public pastry case',before,position,'structure','Pastries and labels appear from the customer side; glass fill is omitted')


def bench(position=(0,0,0),sauna=False):
    before=set(bpy.data.objects)
    for y in [-.19,-.06,.07,.20]:G.block('Bench board',(0,y,.47),(1.6,.115,.06),.012)
    for x in [-.60,.60]:
        for y in [-.15,.15]:G.block('Bench support',(x,y,.24),(.08,.08,.44),.012)
    if sauna:
        for z in [.7,.9,1.1]:G.block('Sauna backrest board',(0,.30,z),(1.65,.05,.10),.009)
    return A.group('Reusable bench',before,position,'support','A coherent usable seat with boards showing linear perspective')


def treatment_bed(position=(0,0,0)):
    before=set(bpy.data.objects)
    G.block('Treatment bed mattress',(0,0,.76),(.70,1.85,.14),.065)
    G.block('Treatment pillow',(0,.60,.86),(.51,.36,.08),.06)
    for x in [-.27,.27]:
        for y in [-.65,.65]:G.tube('Bed support',[(x,y,.7),(x,y,.05)],.03)
    G.tube('Draped towel edge',[(-.34,-.48,.84),(0,-.50,.85),(.34,-.48,.84),(.35,-.48,.56)],.003)
    return A.group('Reusable treatment bed',before,position,'hero','Made bed and pillow identify the treatment destination without medical screens or private data')


def venue(kind='dining'):
    before=set(bpy.data.objects);primary=None
    if kind in ['dining','cafe','waiting']:
        for x,y in [(-.65,1.0),(.85,2.3),(-.8,3.5)]:
            if kind=='waiting':
                furnishing=chair((x,y,0));chair((x+.6,y,0))
                if primary is None:primary=furnishing
            else:
                furnishing=dining_table((x,y,0))
                if primary is None:primary=furnishing
        window((-2.0,2.3,1.5))
    elif kind in ['shop','changing']:
        primary=rack('garment',(-.65,1.6,0));rack('bottle',(1.0,3.0,0))
        if kind=='changing':bench((.6,1.4,0));tag(G.block('Mirror edge only',(1.35,2,1.15),(.04,.04,1.8),.005),'background','Mirror edge identifies a changing area without drawing broad walls')
    elif kind=='salon':
        before_station=set(bpy.data.objects)
        salon_station((-.55,1.9,0),-math.pi/2)
        primary=next(o for o in set(bpy.data.objects)-before_station if o.name.startswith('Reusable salon chair'))
        salon_station((.55,2.5,0),math.pi/2)
        for y in [1.4,2.6]:pendant((0,y,2.85))
    elif kind=='treatment':treatment_bed((0,2.0,0));tag(G.block('Small kit trolley',(.8,2.1,.67),(.40,.45,.04),.008),'support','Trolley is placed beside the bed, clear of the visitor path')
    elif kind=='gym':
        rack('dumbbell',(-1.0,2.8,0));bench((.9,1.6,0))
        for x in [-1.8,1.8]:tag(G.tube('Training frame',[(x,3.5,0),(x,3.5,2.0),(0,3.5,2.0)],.025),'background','Sparse training-frame structure gives scale and perspective')
    elif kind=='sauna':
        primary=bench((-.8,1.8,0),True);bench((.8,3.2,0),True)
        tag(G.block('Sauna stove',(1.0,1.4,.43),(.45,.45,.70),.045),'important_background','Fixed stove is a recognisable destination; visitor stays in the clear aisle')
        for j in range(5):A.ellipsoid('Sauna stone',(1+(j%2-.5)*.12,1.4+(j//2-1)*.10,.84),(.09,.07,.05),'support')
    elif kind in ['lesson','stage']:
        primary=guitar((-.65,2.5,0));bench((.65,2.8,0))
        tag(G.block('Keyboard body',(.9,2.8,1.0),(1.2,.40,.12),.015),'support','Instrument and bench identify the music scene')
        for x in [-.5,.1]:tag(G.tube('Microphone stand',[(x,2.4,.02),(x,2.4,1.5),(x+.16,2.4,1.6)],.01),'background','Microphone stands support the stage story without animated lighting')
    elif kind=='game':
        tag(G.block('Game table',(0,2,.80),(1.9,1.05,.10),.04),'hero','Game surface is the subject and stays clear of visitor walkways')
        for x in [-.8,.8]:tag(G.tube('Game goal',[(x,1.6,.9),(x,1.6,1.2),(x,2.4,1.2),(x,2.4,.9)],.015),'support','Goals identify the play direction')
    elif kind=='park':
        for x,y in [(-1,3),(1.2,5)]:
            tag(G.tube('Public attraction arch',[(x-1,y,0),(x-1,y,2),(x,y,3),(x+1,y,2),(x+1,y,0)],.045),'hero','Ride/arena outline is seen from a public path, never a restricted elevated platform')
    else:raise AssertionError(kind)
    if primary is not None:
        for obj in primary.children_recursive:
            if obj.type=='MESH':
                tag(obj,'hero' if obj.name.startswith(('Quiet tabletop','Garment with sleeves','Bench board','Dining chair seat','Salon chair upholstered','Guitar')) else 'important_background','Primary room landmark stays legible; farther context is fainter')
    A.fixed_side_light((0,2,1.0))
    return A.group('Reusable '+kind+' venue',before,(0,0,0),'background','Sparse venue landmarks establish depth; unnecessary walls and ceilings are absent')
