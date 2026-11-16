"""Reusable native food, cards and hand-held tools for action guides."""
import bpy
import bmesh
import math
from mathutils import Vector
import geometry as G
import assets as A
import venue_assets as V
from drink_scenes import pose


def burger(position=(0,0,.794),split=False):
    before=set(bpy.data.objects)
    G.lathe('Burger lower bun',[(0,0),(.08,0),(.092,.012),(.09,.026),(0,.027)],(0,0,0),40)
    G.lathe('Burger patty',[(0,.027),(.09,.027),(.094,.045),(.084,.053),(0,.053)],(0,0,0),40)
    G.lathe('Burger upper bun',[(0,.076),(.095,.076),(.09,.096),(.070,.119),(.03,.130),(0,.132)],(0,0,0),40)
    cheese=G.block('Thin cheese layer',(0,0,.058),(.18,.17,.005),.009);cheese.rotation_euler.z=.25
    points=[(.092*math.cos(i*math.pi/18),.092*math.sin(i*math.pi/18),.068+.006*math.sin(i*1.9)) for i in range(37)]
    G.tube('Lettuce folded edge',points,.004)
    for x,y in [(-.035,-.012),(.030,.014)]:G.lathe('Tomato slice',[(0,0),(.045,0),(.045,.008),(0,.008)],(x,y,.065),32)
    meshes=[obj for obj in set(bpy.data.objects)-before if obj.type=='MESH']
    halves=[]
    if split:
        for sign in [-1,1]:
            root=A.empty('Burger half rig')
            for source in meshes:
                obj=source.copy();obj.data=source.data.copy();bpy.context.collection.objects.link(obj)
                # Bake modifiers before creating a true flat cross-section.
                bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
                for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
                bm=bmesh.new();bm.from_mesh(obj.data)
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,0,0),plane_no=(1,0,0),clear_inner=sign>0,clear_outer=sign<0)
                edges=[edge for edge in bm.edges if edge.is_boundary and all(abs(v.co.x)<.0001 for v in edge.verts)]
                if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
                bm.to_mesh(obj.data);bm.free();obj.parent=root
                A.tag(obj,'hero','True cut cross-section keeps the bun, filling and patty coherent as the halves separate')
            halves.append(root)
        for obj in meshes:bpy.data.objects.remove(obj,do_unlink=True)
    root=A.group('Reusable sliced burger' if split else 'Reusable burger',before,position,'hero','Layered bun, patty, lettuce and cheese identify the item; the same object is reused through the action')
    return root,halves


def pointing_hand(position=(0,0,.85),side=1,forward=(0,-1,0),normal=(0,0,-1),pose='point'):
    """One life-size anatomical CC0 hand whose index fingertip touches this frame's origin, fingers along `forward`
    (the wrist trails behind them) and the palm facing `normal`."""
    import real_hands
    frame=A.empty('One pointing hand',(0,0,0))
    pointer=real_hands.place(pose,'L' if side<0 else 'R',target=(0,0,0),forward=forward,normal=normal,anchor='f_index.03')
    pointer.parent=frame;frame.location=position
    frame['visible_hand_count']=1;frame['hand_source']='para / MakeHuman CC0';return frame


def card(position=(0,0,.788),title='MENU',selected='YOUR PICK',price='PRICE',width=.28,height=.20):
    before=set(bpy.data.objects)
    A.tag(G.block('Paper resource',(0,0,0),(width,height,.003),.004),'support','Paper rests on its support; blank margins preserve text hierarchy')
    V.lettering(title,(0,.055,.003),.021,'hero',True)
    V.lettering(selected,(-.035,-.005,.003),.015,'hero',True)
    V.lettering(price,(.073,-.005,.003),.015,'hero',True)
    for y in [-.045,-.070]:A.tag(G.tube('Quiet resource row',[(-width*.40,y,.003),(width*.40,y,.003)],.0006),'background','Quiet rows establish resource context without invented personal or pricing data')
    return A.group('Reusable paper '+title,before,position,'support','Title, selected field and value form one flat resource, usable for different scripts')


def open_box(position=(0,0,.785),pastries=True,height=.10):
    before=set(bpy.data.objects)
    G.block('Box base',(0,0,.008),(.50,.34,.016),.006)
    for x in [-.25,.25]:G.block('Box side',(x,0,.016+height/2),(.012,.34,height),.004)
    for y in [-.17,.17]:G.block('Box end',(0,y,.016+height/2),(.50,.012,height),.004)
    hinge=A.empty('Box lid hinge',(0,.17,.016+height))
    lid=G.block('Box hinged lid',(0,0,0),(.50,.34,.012),.005);lid.parent=hinge;lid.location=(0,0,.17);lid.rotation_euler.x=math.pi/2
    if pastries:
        for x,y in [(-.12,-.06),(.12,.06)]:
            root,halves=A.pastry((x,y,.016));root.scale=(.80,)*3
    return A.group('Reusable open food box',before,position,'support','Food rests inside a real base and connected walls; the lid rotates about its hinge'),hinge


def landing_grip(root,position,start=1.2,end=2.4,lift=.14,side=1):
    """One anatomical hand pinches the prop's rim from its side, carries it down to its support, and lets go only
    after contact; palm down, fingers pointing into the prop, forearm leaving outward."""
    import real_hands
    hand=A.empty('Carrying hand',(0,0,0))
    held=real_hands.place('pinch','L' if side<0 else 'R',target=(0,0,0),forward=(-side,0,-.25),normal=(0,0,-1),anchor='grip')
    held.parent=hand;hand.location=position;hand.parent=root
    hand['visible_hand_count']=1;hand['hand_source']='para / MakeHuman CC0'
    initial=root.location.copy()
    for t,z in [(0,lift),(start,lift),(end,0),(5,0)]:pose(root,t,location=initial+Vector((0,0,z)))
    for t,dx in [(0,0),(end+.1,0),(end+.7,side*.45),(5,side*.45)]:pose(hand,t,location=Vector(position)+Vector((dx,0,0)))
    return hand


def held_tongs(food):
    before=set(bpy.data.objects)
    for side in [-1,1]:
        A.tag(G.tube('Food tongs arm',[(side*.10,0,.018),(side*.07,.12,.045),(0,.28,.12)],.004),'support','Tongs meet both sides of the food; the hand stays away from the hot surface')
    hand=A.hand((0,.28,.12),scale=.80);hand.rotation_euler.x=math.pi/2
    A.tag(G.tube('Tongs attached wrist',[(0,.30,.12),(0,.40,.14),(0,.52,.15)],.018),'background','One wrist remains attached to the tongs grip')
    rig=A.group('Held tongs',before,(0,0,0),'support','Tongs carry the food until it contacts the grill');rig.parent=food
    for t,p in [(0,(0,0,0)),(2.0,(0,0,0)),(2.8,(0,.20,.14)),(5,(0,.20,.14))]:pose(rig,t,location=p)
    return rig


def tool(kind='brush',position=(0,0,.84)):
    before=set(bpy.data.objects)
    if kind=='tamper':
        G.lathe('Tamper flat pressing foot',[(0,0),(.027,0),(.027,.012),(0,.012)],(0,0,0),32)
        G.lathe('Tamper shaped handle',[(.012,.012),(.010,.04),(.020,.065),(.018,.09),(0,.10)],(0,0,0),32)
    elif kind=='clippers':
        A.ellipsoid('Clipper contoured body',(0,0,.03),(.035,.075,.028),'hero')
        G.block('Clipper metal blade',(0,-.08,.03),(.065,.027,.008),.003)
        for x in [i*.008 for i in range(-3,4)]:G.tube('Clipper blade tooth',[(x,-.085,.034),(x,-.105,.034)],.0018)
    elif kind=='scissors':
        for side in [-1,1]:
            G.tube('Scissors blade',[(side*.024,.06,0),(0,0,0),(side*.013,-.09,0)],.003)
            G.tube('Scissors finger loop',[(side*.024+.013*math.cos(i*math.pi/12),.06+.018*math.sin(i*math.pi/12),0) for i in range(25)],.003)
    else:
        G.tube('Brush or driver handle',[(0,.09,0),(0,-.04,0)],.006)
        for x in [-.008,-.004,0,.004,.008]:G.tube('Applicator bristle',[(x,-.04,0),(x,-.072,0)],.0012)
    return A.group('Reusable '+kind,before,position,'hero','Recognisable working end and handle stay together during the tool action')
