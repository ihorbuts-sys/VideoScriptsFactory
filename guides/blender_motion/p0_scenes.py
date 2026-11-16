"""One coherent, visitor-side scene per P0 guide; Z up, customer on -Y."""
import math
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
import assets as A
import geometry as G
import venue_assets as V
import real_hands as H

ROLE_ALPHA={'hero':1.,'character':1.,'hand':.65,'support':.60,'important_background':.76,'foreground':.36,'background':.20,'structure':.24,'lighting_cue':.55,'drink_contents':.72}


def smooth(u):
    u=max(0.,min(1.,u));return u*u*u*(10+u*(-15+6*u))


def members(root):
    return [root] if root.type=='MESH' else [o for o in root.children_recursive if o.type=='MESH']


def role(root,name):
    for obj in members(root):A.tag(obj,name,'P0 '+name+'; actual support and depth retained')
    return root


def attach(obj,root):
    bpy.context.view_layer.update()
    world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world


def light_edge(name,points,radius=.0008,parent=None,polyline=False):
    cue=A.tag(G.tube(name,points,radius,handle_type='VECTOR' if polyline else 'AUTO'),'lighting_cue','Fixed source-facing contour attached to a real surface')
    cue['p0_lighting_cue']=True
    if parent is not None:attach(cue,parent)
    return cue


def facade_ground_and_welcome():
    for a,b in [(-2.18,-.58),(.58,2.18)]:
        A.tag(G.tube('Facade ground junction',[(a,-.025,.012),(b,-.025,.012)],.0012),'structure','Wall meets ground; no filled wall or ground plane')
    before=set(bpy.data.objects);angle=-math.atan2(.26,.98)
    for x in [-.245,.245]:
        for side in [-1,1]:A.tag(G.tube('Welcome stand grounded leg',[(x,side*.26,.014),(x,0,.98)],.014),'support','Four feet rest on the ground outside the public doorway')
    for side in [-1,1]:
        panel=G.block('Welcome stand board',(0,side*.117,.55),(.50,.028,.70),.012);panel.rotation_euler.x=-angle if side>0 else angle
        A.tag(panel,'support','A real two-sided A-frame welcome board')
    A.tag(G.tube('Welcome stand hinge',[(-.25,0,.98),(.25,0,.98)],.018),'support','Boards and legs join at the hinge')
    transform=Matrix.Translation((0,-.117,.55))@Matrix.Rotation(angle,4,'X')
    paths=[[(-.09,.16),(-.08,.05),(-.04,.015),(.04,.015),(.08,.05),(.09,.16)],[(.09,.135),(.14,.13),(.14,.075),(.08,.065)],[(-.11,-.005),(.11,-.005)],[(-.15,-.14),(.15,-.14)],[(-.11,-.22),(.11,-.22)]]
    for path in paths:A.tag(G.tube('Welcome pictogram or blank field',[transform@Vector((x,-.019,z)) for x,z in path],.002),'support','Generic cup pictogram and blank welcome fields; no lettering')
    return A.group('Sidewalk welcome stand',before,(-1.,-.58,0),'support','Beside the entrance, clear of the doorway and walking path')


def entry_furnishings():
    """One public room seen through the glazed frontage; keep its central aisle clear."""
    for x in [-1.35,1.35]:
        frame=V.window((x,.035,1.20));frame.scale=(.88,1.,1.10);role(frame,'background')
    for x,y in [(-1.35,2.35),(1.35,3.5),(-.7,5.1)]:
        table=V.dining_table((x,y,0),settings=True);role(table,'background')
        V.pendant((x,y,2.65))
    role(V.plant((1.95,.90,0),height=1.12),'background')


def entry_sign(hanging=False):
    x,y,z=(0.,-.30,2.5) if hanging else (0.,0.,2.5)
    panel=A.tag(G.block('Blank venue name sign',(x,y,z),(.76,.055,.32),.025),'support','Unlettered venue-name resource above the public entrance')
    for dx,length in [(-.17,.12),(0,.13),(.17,.11)]:
        A.tag(G.block('Sign name field',(x+dx,y-.030,z),(length,.006,.035),.008),'support','Broad unlettered name shapes, no readable venue facts')
    light_edge('Sign upper illuminated rim',[(x-.31,y-.033,z+.146),(x,y-.033,z+.146),(x+.31,y-.033,z+.146)],.0014)
    light_edge('Sign lower reflected light',[(x-.22,y-.033,z-.144),(x+.22,y-.033,z-.144)],.0007)
    A.tag(G.block('Sign downlight housing',(x,y-.08,z+.25),(.15,.08,.035),.012),'background','A fixed lamp above the venue sign')
    light_edge('Sign lamp warm lip',[(x-.055,y-.12,z+.23),(x+.055,y-.12,z+.23)],.0012)
    if hanging:G.tube('Hanging sign bracket',[(0,.03,2.80),(0,-.3,2.80),(0,-.3,2.65)],.012)
    return panel


def cup(x=0,y=0,z=.785,hero=True,art='heart'):
    saucer=A.saucer((x,y,z));root=A.cup((x,y,z+.010),role='hero' if hero else 'support')
    # Coffee closes the cup interior; the handle cannot show through it.
    paths=[]
    if art=='rosetta':
        for row in range(4):
            for side in [-1,1]:
                width=.014-row*.0025;cy=-.018+row*.011
                paths.append([(x+side*(.002+width*.5)+width*.5*math.cos(a),y+cy+.005*math.sin(a),z+.1164) for a in [k*math.tau/40 for k in range(41)]])
        paths.append([(x,y-.029,z+.1164),(x,y+.027,z+.1164)])
    else:
        paths.append([(x+.0014*16*math.sin(t)**3,y+.0014*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)),z+.1164) for t in [k*math.tau/64 for k in range(65)]])
    for path in paths:
        obj=G.tube('Foam '+art+' contour',path,.0007);A.tag(obj,'hero' if hero else 'support','Simple contained latte-art geometry')
        attach(obj,root)
    root['support_surface_z']=z+.010
    return root,saucer


def plain_card(position=(0,0,.791),rows=7,vertical=False):
    before=set(bpy.data.objects);x,y,z=position
    board=G.block('Unlettered menu card',position,(.21,.148,.004),.006)
    for i in range(rows):
        A.tag(G.block('Menu price row %02d'%i,(x,y+.050-i*.016,z+.003),(.155 if i!=2 else .18,.0045 if i!=2 else .006,.001),.001),'hero','Simple broad row, no lettering or numerals')
    root=A.group('Menu card',before,role='hero',reason='Resource with clear rows; no readable text')
    root.rotation_euler.z=math.radians(8)
    return root,board


# Ragged line lengths per column (m): left-aligned text lines starting at the widest bar's left edge.
BOARD_LINE_WIDTHS=((.44,.30,.38,.24,.41,.33),(.36,.43,.31,.40,.26,.42),(.40,.27,.44,.35,.29,.38))


def align_left(row,width,left):
    """Resize the bar to width along x, with its left end at x = left."""
    for v in row.data.vertices:v.co.x=math.copysign(width/2,v.co.x)
    row.location.x=left+width/2


def board():
    before=set(bpy.data.objects)
    panel=A.tag(G.block('Menu board blank frame',(0,1.25,1.85),(1.8,.035,.9),.018),'support','Three-column customer-facing menu')
    columns=[]
    for col in range(3):
        rows=[]
        for row in range(6):
            obj=A.tag(G.block('Board column %s row %s'%(col,row),((col-1)*.57,1.221,2.16-row*.12),(.42 if row%2 else .45,.009,.025),.005),'hero','Names and prices shown as unlettered bars')
            rows.append(obj)
        columns.append(rows)
    root=A.group('Three-column menu',before,role='support')
    for col,rows in enumerate(columns):
        left=(col-1)*.57-max(BOARD_LINE_WIDTHS[col])/2
        for row,width in zip(rows,BOARD_LINE_WIDTHS[col]):align_left(row,width,left)
    # Sample the rounded rectangle explicitly: automatic Bezier handles bulge
    # away from a manufactured corner. Dimensions come from this actual board.
    hx,hz=panel.dimensions.x/2-.002,panel.dimensions.z/2-.002;r=.018
    front=-panel.dimensions.y/2-.001
    local=[(-hx,hz-.18)]+[(-hx+r+r*math.cos(a),hz-r+r*math.sin(a)) for a in [math.pi-j*math.pi/24 for j in range(13)]]+[(-hx+.40,hz)]
    bpy.context.view_layer.update()
    light_edge('Board top left warm edge',[panel.matrix_world@Vector((x,front,z)) for x,z in local],parent=panel,polyline=True)
    local=[(hx-.50,-hz)]+[(hx-r+r*math.cos(a),-hz+r+r*math.sin(a)) for a in [-math.pi/2+j*math.pi/24 for j in range(13)]]+[(hx,-hz+.17)]
    light_edge('Board lower right reflected edge',[panel.matrix_world@Vector((x,front,z)) for x,z in local],.0006,parent=panel,polyline=True)
    for x in [-.62,.62]:
        A.tag(G.block('Board downlight housing',(x,1.16,2.43),(.13,.12,.055),.012),'background','A fixed public menu-board light')
        light_edge('Board lamp lip',[(x-.043,1.095,2.40),(x+.043,1.095,2.40)],.0011)
    return root,columns


# Espresso machine on the counter, turned 90 deg clockwise (seen from above) from facing the client, so its working face
# looks left along the counter and the client sees its side panel; the body rests on the 1.05 m top, the drying cups on its
# 1.50 m top.
MACHINE_TURN,MACHINE_TOP=-math.radians(90),1.50
PASS_CUP_X=.52
# Guides whose frame shows the area behind the bar get the working barista; none in pour guides (owner 2026-11-12).
BARISTA_IDS={'counter_over_shoulder','counter_edge_to_pass'}


def counter(body=False,machine_offset=(0,0)):
    top=A.tag(G.block('Customer counter top',(0,.30,1.02),(2.8,.9,.06),.018),'support','Public near edge at y=-.15; camera remains on visitor side')
    A.tag(G.block('Counter front edge',(0,-.13,.94),(2.8,.05,.12),.009),'structure','Leading line along the customer edge')
    if body:
        A.tag(G.block('Customer counter cabinet',(0,.14,.51),(2.6,.56,1.02),.018),'support','A full-height supported counter below the overhanging serving surface')
        for x in [-1.05,-.55,0,.55,1.05]:
            A.tag(G.tube('Counter cabinet joint',[(x,-.141,.12),(x,-.141,.86)],.001),'background','Sparse vertical cabinet joints identify the serving counter')
    # Built around its footprint centre with the working face (group heads, portafilters) on local -Y,
    # then turned so that face looks left along the counter; the client sees the +X side panel square on.
    before=set(bpy.data.objects)
    G.block('Espresso machine body',(0,0,1.275),(.65,.40,.45),.06)
    G.block('Espresso machine drip shelf',(0,-.25,1.07),(.63,.20,.04),.009)
    for x in [-.17,.17]:
        G.lathe('Espresso group head',[(0,0),(.045,0),(.045,.055),(0,.055)],(x,-.26,1.275),24)
        G.lathe('Espresso portafilter basket',[(0,0),(.038,0),(.040,.035),(0,.035)],(x,-.26,1.24),24)
        G.tube('Espresso portafilter handle',[(x,-.30,1.255),(x,-.35,1.247),(x,-.40,1.235)],.011)
    # Clean cups and glasses dry upside down on the machine's flat top (z 1.50).
    for x,y,turn in [(-.18,-.07,.4),(-.03,.06,2.3)]:
        drying=A.cup((x,y,MACHINE_TOP+.118),name='Drying cup',role='background');drying.rotation_euler=(math.pi,0,turn)
        for obj in list(drying.children):
            if obj.name.startswith('Drying cup coffee surface'):bpy.data.objects.remove(obj,do_unlink=True)
    for x,y in [(.11,-.06),(.21,.07)]:
        G.glass('Drying glass',x,y,MACHINE_TOP+.125,water=False).rotation_euler.x=math.pi
    machine=A.group('Side-on espresso machine',before,(1.04+machine_offset[0],.28+machine_offset[1],0),'background')
    machine.rotation_euler.z=MACHINE_TURN
    A.tag(G.block('Counter card holder',(-.7,.04,1.17),(.19,.015,.22),.008),'background','Quiet order context')
    light_edge('Counter reflected upper lip',[(-1.05,-.148,1.052),(-.50,-.148,1.052),(.02,-.148,1.052)],.00055)
    bpy.context.view_layer.update()
    # The client-side panel's top edge, on the half towards the source (a vertical corner cue would read as a second edge).
    light_edge('Machine side panel highlight',[machine.matrix_world@Vector((.326,y,1.47)) for y in [-.15,-.075,0]],.0005)
    return top,machine


def place_setting():
    table=A.table((.22,.18,0),.70)
    plate=A.pasta((0,0,.785))
    food=[o for o in members(plate) if o.get('composition_role')=='hero']
    fork=A.fork((-.17,0,.795));cup_root,saucer=cup(.20,.24,.785,False)
    chair=V.chair((0,1.0,0));role(chair,'background')
    return dict(table=table,plate=plate,food=food,fork=fork,cup=cup_root,saucer=saucer,chair=chair)


def reused_pourer(latte,start):
    """Reuse the project's inspected real vessel, aligned by its actual outlet."""
    import json,hashlib
    assets=Path(__file__).resolve().parents[2]/'model_refferences/objects'
    source=assets/('milk_pitcher/functional/asset.blend' if latte else 'kettle/tripo-generated/review/asset.blend')
    before=set(bpy.data.objects)
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
    imported=[o for o in dst.objects if o and o.type=='MESH']
    for obj in imported:bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    for obj in imported:
        world=obj.matrix_world.copy();obj.data.transform(world);obj.parent=None;obj.matrix_world=Matrix.Identity(4)
        obj.data.materials.clear();obj.data.materials.append(G.MAT)
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        bpy.context.view_layer.objects.active=obj
        clean=obj.modifiers.new('Merge generated internal surfaces','REMESH');clean.mode='VOXEL';clean.voxel_size=.0012;clean.use_smooth_shade=True
        bpy.ops.object.modifier_apply(modifier=clean.name)
        smooth_mod=obj.modifiers.new('Soft vessel surface','SMOOTH');smooth_mod.factor=.6;smooth_mod.iterations=4
        bpy.ops.object.modifier_apply(modifier=smooth_mod.name)
        for face in obj.data.polygons:face.use_smooth=True
        A.tag(obj,'support','Reused inspected vessel mesh, with textures omitted for native line art')
        mod=obj.modifiers.new('Contour-friendly vessel simplification','DECIMATE');mod.ratio=.35
    for obj in dst.objects:
        if obj and obj.type!='MESH':bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.view_layer.update()
    points=[o.matrix_world@v.co for o in imported for v in o.data.vertices]
    if latte:tip=Vector(json.loads((assets/'milk_pitcher/functional/metadata.json').read_text())['anchors']['spout'])
    else:
        cutoff=min(v.x for v in points)*.68
        left=[p for p in points if p.x<cutoff];top=max(p.z for p in left)
        rim=[p for p in left if p.z>top-.004];tip=sum(rim,Vector())/len(rim)
    root=A.group('Reusable hollow milk pitcher' if latte else 'Reusable gooseneck kettle',before,role='support')
    root.rotation_euler.z=math.pi
    root.location=Vector(start)-Matrix.Rotation(math.pi,3,'Z')@tip
    root['reused_source']=str(source);root['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    root['spout_local']=list(tip)
    return root


def hand(target,forward=(0,-1,0),normal=(0,0,1),side='R',pose='pinch'):
    root=H.place(pose=pose,side=side,target=target,forward=forward,normal=normal,anchor='grip')
    role(root,'hand')
    # Extend only the existing forearm-weighted cuff below the picture.
    # The anatomical palm/fingers and the grip landmarks remain unchanged.
    bpy.context.view_layer.update()
    extension=Vector((-.10,0,-.35)) if forward[2]>.9 else -Vector(forward).normalized()*.70+Vector((-.12,0,0))
    for obj in members(root):
        groups={g.index for g in obj.vertex_groups if g.name.startswith('forearm.')}
        inverse=obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            weight=max([g.weight for g in vertex.groups if g.group in groups]+[0.])
            if weight:
                world=obj.matrix_world@vertex.co
                world+=extension*weight*weight
                vertex.co=inverse@world
        obj.data.update()
    root['cuff_extension_m']=extension.length
    root['p0_hand']=True
    return root


def lighting_cues(scene,state):
    """Selected source-facing surface contours; no broad illuminated surfaces."""
    source=Vector(state.get('light_position',(-.65,-.18,1.5)))
    bpy.context.view_layer.update()
    cues=[o.name for o in scene.objects if o.get('p0_lighting_cue')]
    for obj in list(scene.objects):
        if obj.type!='MESH':continue
        path=None
        if 'hollow ceramic body' in obj.name and (obj.get('composition_role')=='hero' or obj.get('p0_light_rim')):
            inverse=obj.matrix_world.inverted();direction=inverse@source
            angle=math.atan2(direction.y,direction.x)
            spread=90 if obj.get('p0_emphasize_light') else 50
            path=[(.0535*math.cos(a),.0535*math.sin(a),.1184) for a in [angle+math.radians(-spread/2+j*spread/24) for j in range(25)]]
            if obj.get('p0_emphasize_light'):
                phi=angle+math.radians(30)
                profile=[(.0438,.022),(.0479,.045),(.0537,.080),(.0538,.108)]
                edge=light_edge('Cup light-facing body contour',[obj.matrix_world@Vector((r*math.cos(phi),r*math.sin(phi),z)) for r,z in profile],.00045,parent=obj)
                cues.append(edge.name)
        elif obj.name.startswith('Plate with formed rim'):
            angle=math.atan2(-.18,-.65)
            path=[(.1392*math.cos(a),.1392*math.sin(a),.0304) for a in [angle+math.radians(-25+j*50/24) for j in range(25)]]
        elif (obj.name.startswith('Window side') and obj.location.x<0) or (obj.name.startswith('Window crossbar') and obj.location.z>.5):
            A.tag(obj,'lighting_cue','Selected window-frame edges locate the useful daylight source')
            obj['p0_lighting_cue']=True;cues.append(obj.name);continue
        elif obj.name.startswith('Steam strand'):
            # Extract a short light-facing curve from the actual strand geometry.
            points=obj.get('p0_steam_points')
            if points:
                import json
                path=[tuple(Vector(p)+Vector((.0005,.0005,0))) for p in json.loads(points)]
        if path:
            points=[obj.matrix_world@Vector(point) for point in path]
            cue=A.tag(G.tube('Steam light contour' if obj.name.startswith('Steam') else 'Surface light contour',points,.0003),'lighting_cue','Fixed-light rim accent attached to the actual surface')
            attach(cue,obj);cue['p0_lighting_cue']=True;cues.append(cue.name)
    state['light_cues']=cues
    if state['hero']:
        centre=sum((obj.matrix_world@Vector(corner) for obj in state['hero'] for corner in obj.bound_box),Vector())/(8*len(state['hero']))
        light=A.fixed_side_light(centre)
        if 'light_position' in state:
            light.location=source;light.rotation_euler=(centre-source).to_track_quat('-Z','Y').to_euler()
    return cues


def room():
    groups=[]
    for i,(x,y) in enumerate([(-.8,2.5),(1.0,3.5),(-.45,5)]):
        table=V.dining_table((x,y,0),settings=True);role(table,'support')
        tops=[o for o in members(table) if o.name.startswith('Quiet tabletop')]
        for obj in tops:A.tag(obj,'hero','Rhythm of supported table tops; legs remain subordinate')
        groups+=tops
        A.tag(G.glass('Table water glass',x+.16,y+.02,.785),'support','Water glass in the free shared corner, away from both place settings')
        menu,_=plain_card((x+.32,y+.03,.791),rows=4);role(menu,'background')
        V.pendant((x,y,2.7))
    win=V.window((1.5,6,1.5));role(win,'important_background')
    role(V.plant((.65,5.7,0),height=1.25),'background')
    role(V.plant((-1.65,3.7,0),height=1.05),'background')
    # Sparse architectural planes supply depth, with no shaded wall/floor wash.
    for x,y in [(-1.95,4.65),(2.05,5.35)]:
        A.tag(G.block('Faint partition plane',(x,y,.48),(.045,1.25,.96),.015),'background','A low room divider separates seating bays while the public aisle stays clear')
    return groups


def build(gid,record):
    """Return target camera, move sampler and geometry/action callbacks."""
    scene=bpy.context.scene
    material=bpy.data.materials.new('Opaque sources for contour occlusion');G.MAT=material
    import drafts
    built=drafts.build(gid,record,__import__(__name__))
    if built is not None:return built
    import p0_people as people
    if gid in people.IDS:return people.build(gid,record,__import__(__name__))
    import p0_table_compositions as tables
    if gid in tables.IDS:return tables.build(gid,record,__import__(__name__))
    state=dict(hero=[],actions=[],contacts=[],adaptations=[],camera_height_support=0.,hand_count=0,silhouettes=0)
    def finish(hero,position,target,sample=None):
        state['hero']=hero;state['target_position']=Vector(position);state['target_aim']=Vector(target)
        state['sample']=sample or (lambda u,p,t:(p,t))
        return state
    if gid=='counter_through_cup_handle':
        counter();drink,saucer=cup(0,0,1.05,False)
        role(drink,'foreground');role(saucer,'foreground')
        handle=next(o for o in members(drink) if 'open handle' in o.name)
        A.tag(handle,'hero','The real open handle frames the distant counter and barista')
        bust=A.portrait((.079,1.40,0),prop=None);role(bust['root'],'background');state['silhouettes']=1
        for obj in members(bust['root']):
            if 'schematic head' in obj.name:A.tag(obj,'support','Faint static background barista, framed by the handle')
        state['adaptations'].append('Only a faint static barista bust is authorized in the background. No face details, arms or hands. Camera stays outside the public counter edge and focuses beyond the real handle opening.')
        V.window((-.75,2.0,1.5))
        return finish([handle],(.079,-.24,1.040),(.079,1.4,1.62),lambda u,p,t:(p+Vector((-.011*(1-smooth(u)),-.06*(1-smooth(u)),-.0212*(1-smooth(u)))),t))
    if gid.startswith('entrance_'):
        door,hinge=V.door(open_angle=90 if gid=='entrance_door_low' else 0);role(door,'hero')
        entry_sign(gid=='entrance_sign_tilt');entry_furnishings()
        if gid in ['entrance_walk_in','entrance_sign_tilt']:facade_ground_and_welcome()
        V.pendant((0,1.5,2.55))
        if gid=='entrance_sign_tilt':
            role(door,'support')
            handle=next(o for o in members(door) if o.name.startswith('Door pull handle'))
            A.tag(handle,'hero','Door handle is the close final target; the complete doorway supplies context')
            def sample(u,p,t):
                s=smooth(u)
                return p+Vector((0,0,.45*(1-s))),Vector((0,-.30,2.5)).lerp(t,s)
            state['adaptations'].append('Stay close at a fixed 1.4 m visitor-side distance. Lower the phone 45 cm while tilting smoothly from the centered sign to the door; do not pull back.')
            return finish([handle],(0,-1.4,1.20),(0,0,1.12),sample)
        if gid=='entrance_door_low':
            table=A.table((0,2.7,0),.48);role(table,'hero')
            A.tag(G.lathe('Entry table pedestal',[(.10,0),(.10,.03),(.04,.1),(.04,.75)],(0,2.7,0),24),'support','Table top stands on a real pedestal')
            for x in [-.65,.65]:role(V.chair((x,2.7,0),rotation=math.pi/2 if x<0 else -math.pi/2),'support')
            for x,y in [(-.13,2.55),(.13,2.85)]:A.plate((x,y,.785))
            for x,y in [(.20,2.56),(-.20,2.84)]:cup(x,y,.785,False)
            A.fork((-.33,2.55,.795))
            role(A.table((1,4.5,0),.48),'background');V.window((0,6.7,1.5))
            role(V.plant((-.72,6.1,0),height=1.3),'support')
            state['adaptations'].append('Frame-only open door; glass is excluded as an opaque blocker.')
            return finish(members(table),(0,.6,1.0),(0,2.7,.785),lambda u,p,t:(Vector((0,-1+1.6*smooth(u),1.0)),t))
        return finish(members(door),(0,-1.2,1.4),(0,0,1.1),lambda u,p,t:(p+Vector((0,-2.8*(1-smooth(u)),0)),t))
    if gid in ['menu_board_truck','menu_board_tilt_up','counter_over_shoulder','counter_edge_to_pass']:
        # Owner review r2: the counter_edge_to_pass cup handle sits 7.4 cm clear of the machine (its drip shelf);
        # r4: the counter_over_shoulder handle 5 cm clear.
        cx={'counter_edge_to_pass':PASS_CUP_X,'counter_over_shoulder':.543}.get(gid,.6)
        _,machine=counter();menu,columns=board();drink,saucer=cup(cx,.02,1.05,gid=='counter_edge_to_pass')
        if gid in BARISTA_IDS:import barista;barista.add(__import__(__name__),machine,state,gid)
        for x in [-.6,-.4,-.2]:cup(x,.60,1.05,False)
        for obj in scene.objects:
            if 'hollow ceramic body' in obj.name:obj['p0_light_rim']=True
        if gid=='menu_board_truck':
            for obj in members(menu):A.tag(obj,'support','Other columns remain subordinate to the chosen drinks column')
            for obj in columns[-1]:A.tag(obj,'hero','Chosen drinks column')
            return finish(columns[-1],(.57,-.4,1.85),(.57,1.25,1.85),lambda u,p,t:(p+Vector((-1.14*(1-u),0,0)),t+Vector((-1.14*(1-u),0,0))))
        if gid=='menu_board_tilt_up':
            return finish(sum(columns,[]),(0,-.95,1.13),(0,1.25,1.85),lambda u,p,t:(p,Vector((.4,.0,1.14)).lerp(t,smooth(u))))
        if gid=='counter_over_shoulder':
            state['adaptations'].append('Shoulder not drawn. A small customer-side diagonal slide changes the board/cup perspective without staging staff action.')
            return finish(columns[0]+members(drink),(.6,-1.1,1.5),(.15,.5,1.55),lambda u,p,t:(t+(p-t)*(1+.12*(1-smooth(u)))+Vector((-.42*(1-smooth(u)),0,0)),t+Vector((-.12*(1-smooth(u)),0,0))))
        role(menu,'background')
        for obj in members(drink):
            if 'hollow ceramic body' in obj.name:obj['p0_emphasize_light']=True
        for y,a,z in [(-.06,.12,1.051),(.16,.18,1.051)]:light_edge('Counter surface reflected light',[(a+cx-.6,y,z),(a+cx-.18,y,z)],.00055)
        return finish(members(drink),(cx-.35,-.55,1.2),(cx,.02,1.11),lambda u,p,t:(p+Vector((-.95*(1-smooth(u)),0,0)),t))
    if gid.startswith('menu_card_'):
        A.table((.22,.18,0),.65);card,panel=plain_card();drink,saucer=cup(.22,.18,.785,False);A.fork((-.2,0,.79))
        selected=next(o for o in members(card) if o.name.startswith('Menu price row 02'))
        bpy.context.view_layer.update()
        light_edge('Selected menu position',[selected.matrix_world@Vector((x,0,.0013)) for x in [-.087,.087]],.001,parent=selected,polyline=True)
        if gid=='menu_card_top':
            state['adaptations'].append('A 12 cm sideways phone slide and a small pitch change replace the fixed overhead hold. The card stays flat and supported.')
            return finish(members(card),(0,-.035,1.24),(0,0,.79),lambda u,p,t:(p+Vector((-.12*(1-smooth(u)),-.05*(1-smooth(u)),-.025*math.sin(math.pi*u))),t))
        for obj in members(card):A.tag(obj,'support','Card gives the selected line context')
        A.tag(selected,'hero','Dish-name row is the target, not a full menu zoom')
        for obj in members(card):
            if obj.get('p0_lighting_cue'):A.tag(obj,'lighting_cue','Selected menu line')
        for obj in members(drink):
            if 'hollow ceramic body' in obj.name:obj['p0_light_rim']=True
        # Window light from the far left, so the lit stretch of the round top's edge is the far edge the push keeps in
        # view; the cue follows the edge on its chamfer.
        state['light_position']=(-.8,1.4,1.4)
        centre,radius=Vector((.22,.18)),.65;facing=math.atan2(1.4-centre.y,-.8-centre.x)
        light_edge('Table edge light',[(centre.x+(radius-.004)*math.cos(a),centre.y+(radius-.004)*math.sin(a),.781) for a in [facing+math.radians(-40+j*80/32) for j in range(33)]],.0005)
        return finish([selected],(0,-.25,.99),(0,.018,.794),lambda u,p,t:(t+(p-t)*(1+1.1*(1-smooth(u)))+Vector((-.07*(1-smooth(u)),0,.02*math.sin(math.pi*u))),t+Vector((.045*(1-smooth(u)),0,0))))
    if gid.startswith('plate_') or gid=='handoff_plate_lands' or gid=='bite_pip_dish':
        setting=place_setting();food=setting['food'];plate=setting['plate']
        # Food, visible near-left rim, and the near side of the cup base.
        # Supporting corners may lie below the hero band, but stay on screen.
        corner=(-.17,.06,.805) if gid=='plate_high_orbit' else (-.04,-.144,.815)
        state['triangle_points']=[Vector((.02,.01,.862)),Vector(corner),Vector((.18,.225,.795))]
        if gid=='plate_high_orbit':
            A.plate((-.22,.24,.785));r=math.sqrt(.45**2+.45**2)
            def sample(u,p,t):
                angle=math.radians(-30+60*u);v=p-t;radius=math.hypot(v.x,v.y)
                return t+Vector((radius*math.sin(angle),-radius*math.cos(angle),v.z)),t
            return finish(food,(.225,-.3897,1.235),(0,0,.83),sample)
        if gid=='handoff_plate_lands':
            for root in [setting['cup'],setting['saucer']]:
                for obj in list(root.children_recursive)+[root]:bpy.data.objects.remove(obj,do_unlink=True)
            glass=G.glass('Water glass',.22,.25,.785);A.tag(glass,'support','Water glass outside the plate footprint')
            knife=A.knife((.163,-.02,.785))
            state['adaptations'].append('Hand delivery is deferred. The plate stays on the table after service while a short diagonal phone move reveals its rim, glass and cutlery. No airborne plate or invisible carrier is animated.')
            return finish(food,(0,-.5,1.235),(0,0,.83),lambda u,p,t:(p+Vector((-.12*(1-smooth(u)),-.05*(1-smooth(u)),-.03*(1-smooth(u)))),t))
        if gid=='bite_pip_dish':
            for root in [setting['cup'],setting['saucer'],setting['chair'],setting['fork']]:
                for obj in list(root.children_recursive)+[root]:bpy.data.objects.remove(obj,do_unlink=True)
            fork=A.fork((.055,-.015,.846),role='hero');fork.rotation_euler=(math.radians(10),0,math.pi/2)
            bpy.context.view_layer.update();grip=fork.matrix_world@Vector((0,-.09,.005))
            wrist=H.place('pinch','L',target=grip,forward=(-1,0,0),normal=(0,0,-1),anchor='grip')
            role(wrist,'hand');wrist['p0_hand']=True;wrist['p0_cropped_grip']=True;attach(wrist,fork)
            # Each strand follows the fork at its upper end but hangs along
            # world gravity. Its exposed length grows clear of the food.
            hanging=A.empty('Fork pasta hanging under gravity');strands=[]
            for k in range(3):
                points=[((k-1)*(.004+.015*j/20)+.003*math.sin(j/20*math.tau+k),.004*math.sin(j/20*math.pi+k),-.13*j/20) for j in range(21)]
                strand=A.tag(G.tube('Hanging pasta strand',points,.0016),'hero','One end remains on the fork; the lower part hangs downward')
                strand.parent=hanging;strands.append(strand)
            start=fork.location.copy()
            def action(u):
                progress=smooth((u-.12)/.70)
                fork.location=start+Vector((.045*progress,-.02*progress,.145*progress));fork.rotation_euler.x=math.radians(10+12*progress)
                bpy.context.view_layer.update();hanging.location=fork.matrix_world@Vector((0,.054,.010))
                length=min(.13,max(.008,hanging.location.z-.848));hanging.scale.z=length/.13
                hanging.keyframe_insert('scale');fork.keyframe_insert('location');fork.keyframe_insert('rotation_euler')
            state['actions'].append(action);state['hand_count']=1
            state['contacts'].append(dict(kind='fork_grip',hand=wrist.name,prop=fork.name,grip=list(grip),crop='Only the small grip at the right edge; palm, wrist and arm extend out of frame'))
            state['adaptations'].append('Owner explicitly restored one tightly cropped grip. No full hand, extended arm, face or PiP portrait. Three pasta strands remain attached to the fork and lengthen downward clear of the plate as it rises.')
            return finish(food+[o for o in members(fork) if o.get('composition_role')=='hero']+strands,(0,-.48,1.12),(.02,0,.94))
        if gid=='plate_rise_overhead':
            # Flat-lay reveal: plate, cup at one o'clock, straight fork; layout set here only.
            setting['table'].location=(0,.40,0);setting['chair'].location.y=1.22
            for root in [setting['cup'],setting['saucer']]:root.location+=Vector((.12,.236,0))-Vector((.20,.24,0))
            setting['fork'].location=Vector((-.2015,.0378,.795))
            state['triangle_points']=[Vector((0,0,.80)),Vector((.12,.236,.90)),Vector((-.2015,0,.797))]
            state['camera_up']=(0,1,0)
            state['adaptations'].append('Crane up with tilt in the seat-side vertical plane: pitch 45 to 90 degrees, the plate held at 55% of the frame height; a fixed tabletop up reference keeps the overhead end free of roll.')
            centre=Vector((0,0,.80));offset=math.atan(.1*.75)
            def pose(s):
                pitch=math.radians(45+45*s);r=.45+(.668-.45)*s;line=pitch-offset
                position=centre+r*Vector((0,-math.cos(line),math.sin(line)))
                return position,position+Vector((0,math.cos(pitch),-math.sin(pitch)))
            end_position,end_aim=pose(1.)
            return finish(members(plate),end_position,end_aim,lambda u,p,t:pose(smooth(u)))
        if gid=='plate_tissue_slide':
            state['adaptations'].append('Rest the phone bottom edge on a napkin and slide sideways across the near edge of the table. No forward slide into the plate, face-flat handset or napkin under the lens is drawn.')
            state['camera_height_support']=.785
            return finish(food,(.04,-.30,.86),(0,0,.83),lambda u,p,t:(p+Vector((-.18*(1-smooth(u)),0,0)),t))
        return finish(food,(0,-.22,.885),(0,0,.84),lambda u,p,t:(t+(p-t)*(1+1.2*(1-smooth(u))),t))
    if gid=='handoff_counter_cup':
        counter(body=True);drink,saucer=cup(-1.0,-.02,1.05)
        light_edge('Served counter corner light',[(-1.39,.12,1.051),(-1.39,-.148,1.051),(-.78,-.148,1.051)],.00065,polyline=True)
        for obj in members(drink):
            if 'hollow ceramic body' in obj.name:obj['p0_light_rim']=True
        state['contacts'].append(dict(kind='served_counter_corner',cup=drink.name,saucer=saucer.name,support_surface_z=1.05))
        state['adaptations'].append('Show the serving counter corner, thick overhanging top and full-height cabinet underneath. The served cup and saucer stay stationary on its 1.05 m surface during a customer-side diagonal reveal.')
        return finish(members(drink),(-1.13,-1.0,1.25),(-1.0,-.02,1.12),lambda u,p,t:(p+Vector((-.22*(1-smooth(u)),-.06*(1-smooth(u)),-.05*(1-smooth(u)))),t))
    if gid.startswith('pour_') or gid.startswith('steam_'):
        support=1.05 if gid.startswith('pour_') else .785
        if gid.startswith('pour_'):counter()
        else:A.table((.22,.18,0),.65)
        drink,saucer=cup(0,0,support,art='rosetta' if gid=='pour_top_down_latte' else 'heart')
        heroes=members(drink)
        V.window((.3,1.5,support+.60));role(V.chair((0,1,0)),'background')
        if gid.startswith('steam_'):
            plant=V.plant((-.48,1.18,0),height=1.6);role(plant,'background');plant['p0_window_plant']=True
        state['light_position']=(.3,1.45,support+.60)
        if gid.startswith('pour_'):
            # One rigid pitcher pivots about its real spout; stream endpoints stay connected.
            if gid!='pour_top_down_latte':
                for obj in list(members(drink)):
                    if obj.name.startswith('Foam'):bpy.data.objects.remove(obj,do_unlink=True)
                heroes=members(drink)
            start=Vector((-.033,.005,support+.20));end=Vector((-.033,.005,support+.116))
            pitcher=reused_pourer(gid=='pour_top_down_latte',start)
            stream=A.tag(G.tube('Milk stream / spout to coffee',[start,end],.002),'support','Straight flow falls vertically from the fixed spout to a point inside the cup')
            stream.shape_key_add(name='Basis');off=stream.shape_key_add(name='Flow has not started');tail=stream.shape_key_add(name='Last drop lands')
            for point in off.data:point.co=start
            for point in tail.data:point.co=end
            pivot=A.empty('Pitcher spout pivot',start);attach(pitcher,pivot)
            growth_keys=[]
            for foam in [o for o in members(drink) if o.name.startswith('Foam')]:
                foam.shape_key_add(name='Basis');growth=foam.shape_key_add(name='Milk art growth');growth_keys.append(growth)
                original=[v.co.copy() for v in foam.data.vertices]
                for point,source in zip(foam.data.shape_keys.key_blocks[0].data,original):
                    point.co.x=source.x*.15;point.co.y=source.y*.15
            def pour_action(u):
                tilt=smooth((u-.05)/.26)*(1-smooth((u-.78)/.22))
                pivot.rotation_euler.y=math.radians((32 if gid=='pour_top_down_latte' else 58)*tilt)
                pivot.keyframe_insert('rotation_euler')
                # A gravity-led front reaches the coffee in sqrt(2*h/g).
                fall_seconds=math.sqrt(2*(start.z-end.z)/9.81)
                front=min(1,max(0,(u-.18)*record['durationSec']/fall_seconds))**2
                last_drop=min(1,max(0,(u-.84)*record['durationSec']/fall_seconds))**2
                off.value=1-front;tail.value=last_drop
                off.keyframe_insert('value');tail.keyframe_insert('value')
                for index,growth in enumerate(growth_keys):
                    growth.value=smooth((u-.10-index*.025)/.55);growth.keyframe_insert('value')
            state['actions'].append(pour_action)
            state['contacts'].append(dict(kind='stream',source=list(start),receiver=list(end),cup_radius=.045,receiver_within_cup=True,
                gravity_axis=[0,0,-1],straight_stream_vertical=True,flow_start_u=.18,flow_stop_u=.84,fall_seconds=math.sqrt(2*(start.z-end.z)/9.81),pitcher_tilts_toward_cup=True))
            state['adaptations'].append('Pitcher stays beside the cup, tilts toward it, starts a vertical gravity-led stream after tilting, then stops flow and returns upright. The last drop lands before the final target hold.')
            if gid=='pour_top_down_latte':
                return finish(heroes,(0,-.025,support+.43),(0,0,support+.10),lambda u,p,t:(t+(p-t)*(1+.18*(1-smooth(u))),t))
            if gid=='pour_upside_down':
                state['adaptations'].append('The inverted handset puts its lens 18 mm above the counter. An 18 cm lateral slide looks upward through the handle side of the cup; camera height stays fixed.')
                return finish(heroes,(.16,-.27,support+.018),(0,0,support+.07),lambda u,p,t:(p+Vector((-.18*(1-smooth(u)),0,0)),t))
            return finish(heroes,(-.38,-.42,support+.15),(0,0,support+.07),lambda u,p,t:(p+Vector((.10*(1-smooth(u)),-.05*(1-smooth(u)),.015*(1-smooth(u)))),t))
        curls=[]
        for side in [-1,1]:
            points=[(side*.012+.007*math.sin(k*.8),0,support+.13+k*.016) for k in range(9)]
            curls.append(A.tag(G.tube('Steam strand',points,.00075),'hero','Steam remains attached above the coffee, visible from the first frame'))
            import json
            curls[-1]['p0_steam_points']=json.dumps(points)
        heroes+=curls
        def action(u):
            for k,obj in enumerate(curls):
                obj.location.x=.003*math.sin(u*math.tau+k);obj.keyframe_insert('location')
        state['actions'].append(action)
        if gid=='steam_slide_pull_out':
            A.plate((.24,-.08,support));pastry=A.pastry((.24,-.08,support+.009));role(pastry[0] if isinstance(pastry,tuple) else pastry,'support')
            return finish(heroes,(.23,-.45,support+.18),(0,0,support+.14),lambda u,p,t:(t+(p-t)*(.46+.54*smooth(u))+Vector((-.12*(1-smooth(u)),0,0)),t))
        if gid=='steam_low_backlit':return finish(heroes,(.10,-.4,support+.075),(0,0,support+.075),lambda u,p,t:(p+Vector((-.14*(1-smooth(u)),0,0)),t))
        if gid=='steam_push_in_high':
            A.plate((.24,.22,support));pastry=A.pastry((.24,.22,support+.009));role(pastry[0] if isinstance(pastry,tuple) else pastry,'support')
            return finish(heroes,(0,-.25,support+.30),(0,0,support+.11),lambda u,p,t:(t+(p-t)*(1+.75*(1-smooth(u)))+Vector((-.08*(1-smooth(u)),0,0)),t))
        def sample(u,p,t):
            angle=math.radians(-30+60*u);v=p-t;r=math.hypot(v.x,v.y)
            return t+Vector((r*math.sin(angle),-r*math.cos(angle),v.z)),t
        return finish(heroes,(.15,-.2598,support+.08),(0,0,support+.08),sample)
    if gid.startswith('room_'):
        heroes=room()
        if gid=='room_reveal_plant':
            plant=V.plant((-.22,.85,0),height=1.5);role(plant,'foreground');plant['p0_reveal_plant']=True
            state['contacts'].append(dict(kind='floor_plant_reveal',plant=plant.name,no_foreground_table=True))
            state['adaptations'].append('Floor plant and room tables occupy separate areas. Film through the near leaves from the aisle, then slide 40 cm to the right; there is no table beneath the camera or intersecting the plant.')
            return finish(heroes,(.27,-.15,1.18),(.15,3.5,1.0),lambda u,p,t:(p+Vector((-.40*(1-smooth(u)),0,0)),t+Vector((-.40*(1-smooth(u)),0,0))))
        A.table((.1,0,0),.55);drink,saucer=cup(-.25,.22,.785,False);role(drink,'foreground')
        if gid=='room_reveal_cup':
            def sample(u,p,t):
                v=Vector((-.35*(1-u),0,0));return p+v,t+v
            state['adaptations'].append('Lower the seated phone to cup height for real foreground occlusion; a lens 35 cm above the table cannot reveal from directly behind this short cup.')
            return finish(heroes,(.10,-.05,.865),(.10,3.4,.865),sample)
        before=set(bpy.data.objects);counter();role(A.group('Counter at left of room',before,(-2.5,2,0)),'background')
        def sample(u,p,t):
            angle=math.radians(-55*(1-smooth(u)));delta=t-p
            return p,p+Vector((delta.x*math.cos(angle)-delta.y*math.sin(angle),delta.x*math.sin(angle)+delta.y*math.cos(angle),delta.z))
        delta=Vector((-4.25*math.sin(math.radians(15)),4.25*math.cos(math.radians(15)),-4.25*math.tan(math.radians(12))))
        state['adaptations'].append('Lower the seated phone to 95 cm and angle it down 12 degrees so the foreground cup body and handle both remain visible above the app controls.')
        return finish(heroes,(0,-.25,.95),Vector((0,-.25,.95))+delta,sample)
    # The P0 people decision authorizes silhouettes, not detailed people.
    bust=A.portrait((0,0,0),prop=None);state['silhouettes']=1
    head=next(o for o in members(bust['root']) if 'schematic head' in o.name)
    role(bust['root'],'support');A.tag(head,'hero','Faceless, mouthless framing silhouette; no regenerated character')
    state['hero']=[head]
    if gid.startswith('bite_') or gid.startswith('sip_'):
        prop=A.fork((.12,-.15,1.34),role='support') if gid.startswith('bite_') else cup(.12,-.15,1.30)[0]
        if gid.startswith('bite_'):
            prop.rotation_euler.x=math.pi/2
            bite=A.ellipsoid('One forkful',(.12,-.15,1.42),(.02,.015,.025),'hero');attach(bite,prop)
        else:
            # A held cup has no floating saucer in a selfie.
            for obj in [o for o in scene.objects if o.name.startswith('Saucer')]:bpy.data.objects.remove(obj,do_unlink=True)
        h=hand((.12,-.15,1.26) if gid.startswith('bite_') else (.20,-.15,1.366),forward=(0,0,1),normal=(0,1,0) if gid.startswith('bite_') else (0,-1,0));attach(h,prop);state['hand_count']=1
        start=prop.location.copy()
        def action(u):
            progress=smooth((u-.2)/.4)
            prop.location=start+Vector((-.09*progress,(.05 if gid.startswith('bite_') else -.02)*progress,(.21 if gid=='sip_high_lean' else .18)*progress))
            prop.keyframe_insert('location')
        state['actions'].append(action)
    if gid=='verdict_high_plate':
        A.table((.22,.18,0),.65);role(A.pasta((.24,-.27,.785)),'support')
    if gid=='verdict_high_plate':
        # A seated diagonal selfie can include a reachable side setting without
        # putting the phone beyond arm's length or hiding the plate below frame.
        for obj in [o for o in scene.objects if o.name.startswith('Reusable table') or o.name.startswith('Pasta plate')]:
            for child in list(obj.children_recursive)+[obj]:bpy.data.objects.remove(child,do_unlink=True)
        bust['root'].location.z=-.30
        A.table((.55,0,0),.55);role(A.pasta((.25,0,.785)),'support')
        state['adaptations'].append('Seated bust and a diagonal above-eye phone position reveal the reachable side place setting; the standing straight-on layout left the plate outside the image.')
        return finish([head],(-.55,-.40,1.75),(0,0,1.26))
    high=gid=='sip_high_lean'
    # Aim slightly below eye height so the eyes land above frame centre while
    # the lens itself remains at eye height and within normal arm reach.
    target=Vector((0,0,1.58));position=target+Vector((0,-.60,.25)) if high else Vector((0,-.65,1.62))
    if gid=='sip_high_lean':return finish([head],position,target,lambda u,p,t:(t+(p-t)*(1+.08*(1-smooth(u))),t))
    return finish([head],position,target)
