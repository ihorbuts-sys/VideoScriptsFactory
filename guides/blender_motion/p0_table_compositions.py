"""Reusable food/drink setups for the owner's three tabletop motion references."""
import hashlib,json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
import assets as A
import geometry as G
import venue_assets as V
import real_hands as H

IDS={'table_spread_orbit','glass_slide_close','pancake_clear_path'}
ROOT=Path(__file__).resolve().parents[2]
# The lighting_cues default source direction, so the stack's cues match the glasses' and salad plate's.
LIGHT=(-.65,-.18)
# Palm angle from the entry side toward the lens, (wrist extension, ulnar deviation) in degrees and palm height on the
# glass in metres (research/reference_shots/glass_grasp.md GG4-GG5; judgement so each forearm leaves frame on its side).
CLEAR_GRASP=dict(palm_deg=-30,wrist=(60,20),height=.075)
# The slide grasp turns the wrist about the forearm's axis so the hand sits on the forearm's line; the owner's sketch
# (2026-11-12) sends the forearm toward the lower left (40 deg extension, inside GG5's 60-70 deg range, 15 deg ulnar).
# The thenar pad fills the hollow the swung thumb metacarpal leaves, the fade starts 6 cm toward the elbow so the
# wrist stays drawn, and contacts keep 2 mm off the glass.
THENAR=dict(thenar=(.025,.2,.05),gap=.002)
SLIDE_GRASP=dict(palm_deg=25,wrist=(40,15),height=.06,pivot='axis',fade=.06,options=THENAR)
# Cocktail shell outer wall (height, radius), as built by `cocktail`.
WALL=((0.,.036),(.008,.040),(.19,.044))


def imported_food(name,position,role='support'):
    source=ROOT/'model_refferences/objects'/name/'tripo-generated/review/asset.blend'
    cache=source.parents[2]/'lineart';cache.mkdir(exist_ok=True)
    digest=hashlib.sha256(source.read_bytes()).hexdigest();meta=cache/'metadata.json';path=cache/'asset.blend'
    ready=path.exists() and meta.exists() and json.loads(meta.read_text()).get('source_sha256')==digest
    before=set(bpy.data.objects)
    with bpy.data.libraries.load(str(path if ready else source),link=False) as (src,dst):dst.objects=src.objects
    meshes=[o for o in dst.objects if o and o.type=='MESH']
    for obj in meshes:bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    for obj in meshes:
        world=obj.matrix_world.copy();obj.data.transform(world);obj.parent=None;obj.matrix_world=Matrix.Identity(4)
        obj.data.materials.clear();obj.data.materials.append(G.MAT)
        if not ready:
            bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
            bpy.context.view_layer.objects.active=obj
            mod=obj.modifiers.new('Clean native contours','REMESH');mod.mode='VOXEL';mod.voxel_size=.0015;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
            mod=obj.modifiers.new('Soften scan surface','SMOOTH');mod.factor=.5;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
            mod=obj.modifiers.new('Reduce contour topology','DECIMATE');mod.ratio=.4;bpy.ops.object.modifier_apply(modifier=mod.name)
        for face in obj.data.polygons:face.use_smooth=True
        A.tag(obj,role,'Existing clay-world '+name+' asset, cleaned for native contours')
    for obj in dst.objects:
        if obj and obj.type!='MESH':bpy.data.objects.remove(obj,do_unlink=True)
    bottom=min(v.co.z for o in meshes for v in o.data.vertices)
    for obj in meshes:
        for vertex in obj.data.vertices:vertex.co.z-=bottom
    if not ready:
        bpy.data.libraries.write(str(path),set(meshes),compress=True)
        meta.write_text(json.dumps(dict(source=str(source),source_sha256=digest,original_preserved=True,credits=0),indent=2)+'\n')
    return A.group('Reusable '+name,before,position,role,'Physical resting base at the supplied plate surface')


def slice_round(root,slices=8,gap=.003,pulled=-90.,pull=.022,lift=.012,solid_cut=False):
    """Cuts a round food group (centred on its root, resting at z=0) into equal slices in memory, separated by a cut
    gap; the slice centred on `pulled` degrees slides `pull` metres outward and rests its crust `lift` higher (the
    serving plate's rim). With `solid_cut` every cut face is capped flat in its own plane and the faces either side of
    the pulled slice's gap carry a crust line and a sauce/cheese line. The source files are not touched."""
    source=next(o for o in root.children if o.type=='MESH');role=source.get('composition_role','support')
    width=math.tau/slices;parts=[]
    for k in range(slices):
        centre=math.radians(pulled)+k*width;bm=bmesh.new();bm.from_mesh(source.data);planes=[]
        for side in (-1,1):
            edge=centre+side*width/2
            # Normal of the cut plane, pointing away from the kept sector.
            normal=Vector((-math.sin(edge),math.cos(edge),0))*side
            bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],dist=1e-6,plane_co=(0,0,0),plane_no=normal,clear_outer=True)
            # One fill per plane: a single fill after both cuts spans the two planes with one non-planar face.
            if solid_cut:bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
            planes.append((side,edge,normal))
        if not solid_cut:bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
        mesh=bpy.data.meshes.new('Pizza slice %d'%k);bm.to_mesh(mesh);bm.free()
        obj=bpy.data.objects.new('Pizza slice %d'%k,mesh);bpy.context.collection.objects.link(obj)
        obj.data.materials.append(G.MAT);obj.parent=root
        for face in mesh.polygons:face.use_smooth=True
        out=Vector((math.cos(centre),math.sin(centre),0))
        obj.location=out*(gap/2+(pull if k==0 else 0))
        if k==0:
            # Tilt about the slice's tip so the crust end rests on the rim.
            obj.rotation_mode='AXIS_ANGLE';axis=Vector((-out.y,out.x,0))
            obj.rotation_axis_angle=(-math.atan2(lift/root.scale.z,.15),*axis)
        A.tag(obj,role,'Pizza cut into %d slices, one pulled out'%slices);parts.append(obj)
        if solid_cut:
            for side,edge,normal in planes:
                caps=[f for f in mesh.polygons if abs(Vector(f.normal).dot(normal))>.999 and all(abs(mesh.vertices[i].co.dot(normal))<1e-5 for i in f.vertices)]
                for face in caps:face.use_smooth=False
                # Only the faces bordering the pulled slice's gap show; lines on the others would peek through the seams.
                if k==0 or (k,side) in ((1,-1),(slices-1,1)):cut_lines(obj,mesh,caps,edge,normal,role)
    bpy.data.objects.remove(source,do_unlink=True)
    return parts


def cut_lines(obj,mesh,caps,edge,normal,role):
    """Draws a flat cut face of a round food as a solid cross-section, parented to its slice: its crust-side outline
    (contour-only line art skips the fold to the crust wall) and a crust line and a sauce/cheese line running level
    from near the tip to that outline (judgement: a 45/72% split of the inner thickness)."""
    radial=Vector((math.cos(edge),math.sin(edge),0))
    segments=[[(mesh.vertices[i].co.dot(radial),mesh.vertices[i].co.z) for i in key] for f in caps for key in f.edge_keys]
    def cross(value,axis):
        # Positions along the other axis where the face's outline crosses `value` on `axis` (0 radius, 1 height).
        return [a[1-axis]+(b[1-axis]-a[1-axis])*(value-a[axis])/(b[axis]-a[axis]) for a,b in segments if (a[axis]-value)*(b[axis]-value)<0]
    reach=max(p[0] for s in segments for p in s)
    inner=[cross(reach*f,0) for f in (.1,.2,.3,.4,.5,.6,.7)];inner=[z for z in inner if z]
    bottom=sorted(min(z) for z in inner)[len(inner)//2];top=sorted(max(z) for z in inner)[len(inner)//2]
    radius=.0007;lift=normal*radius*1.5
    outer=[p[1] for s in segments for p in s if p[0]>reach*.85];low,high=min(outer)+2*radius,max(outer)-2*radius
    lines=[('Pizza cut face crust outline',[radial*(max(cross(z,1))-radius)+Vector((0,0,z)) for z in (low+(high-low)*j/8 for j in range(9))])]
    for name,share in (('Pizza crust line',.45),('Pizza sauce and cheese line',.72)):
        z=bottom+share*(top-bottom);end=max(cross(z,1))-radius
        lines.append((name,[radial*(reach*.08+(end-reach*.08)*j/6)+Vector((0,0,z)) for j in range(7)]))
    for name,points in lines:
        line=G.tube(name,[p+lift for p in points],radius);line.parent=obj
        A.tag(line,role,'Cut-face line on the pulled slice\'s gap, so the cut reads solid')


def platter(position,radius=.17,role='support'):
    return A.tag(G.lathe('Broad flat serving plate',[(0,0),(radius*.86,0),(radius,.012),(radius,.019),(radius*.91,.021),(radius*.86,.008),(0,.008)],position,64),role,'A flat support with a small raised rim')


def bread(position):
    before=set(bpy.data.objects)
    loaf=A.ellipsoid('Soft scored bread loaf',(0,0,.03),(.045,.10,.04),'support')
    for v in loaf.data.vertices:v.co.z=max(v.co.z,-.03)
    for y in [-.045,0,.045]:
        points=[]
        for j in range(13):
            x=-.028+j*.056/12;yy=y+x*.20
            z=.03+.04*math.sqrt(max(0,1-(x/.045)**2-(yy/.10)**2))+.0005
            points.append((x,yy,z))
        A.tag(G.tube('Bread score',points,.0008),'support','Three broad scored marks identify the loaf')
    return A.group('Reusable bread loaf',before,position,'support')


def pancakes(position,role='hero'):
    before=set(bpy.data.objects)
    for i in range(4):
        r=.082+(i%2)*.003;z=i*.016
        A.tag(G.lathe('Rounded pancake layer',[(0,z),(r-.006,z),(r,z+.004),(r,z+.011),(r-.006,z+.016),(0,z+.016)],(0,0,0),48),role,'Rounded stack gives a clear low-angle silhouette')
    butter=A.tag(G.block('Butter on pancakes',(.033,-.022,.071),(.028,.025,.012),.005),role,'One readable topping');butter.rotation_euler.z=.25
    A.ellipsoid('Soft cream on pancakes',(-.020,.024,.080),(.025,.023,.018),role,'A broad soft cream dollop adds a readable vertical focal point')
    A.ellipsoid('Berry on cream',(-.018,.023,.105),(.009,.009,.010),role,'One simple topping; no photographic microdetail')
    for x in [-.025,.03]:A.tag(G.tube('Syrup drip',[(x,-.035,.065),(x,-.069,.064),(x,-.082,.040),(x+.004,-.079,.018)],.0018),role,'A small connected syrup contour')
    return A.group('Reusable pancake stack',before,position,role)


def cocktail(position,index=0,role='support',primary=False):
    before=set(bpy.data.objects)
    shell=A.tag(G.lathe('Clear cocktail glass shell',[(0,0),(.036,0),(.040,.008),(.044,.19),(.040,.19),(.034,.014),(0,.014)],(0,0,0),64),role,'A clear highball glass with a real wall and base')
    shell['clear_vessel_shell']=True
    rim=None
    if primary:
        rim=A.tag(G.tube('Primary cocktail rim',[(.042*math.cos(k*math.tau/48),.042*math.sin(k*math.tau/48),.1904) for k in range(49)],.00055),'hero','The rim and ice are the protected focal area; the glass body supplies close foreground context')
    volume=G.lathe('Transparent drink volume',[(0,0),(.033,0),(.0384,.131),(0,.131)],(0,0,.014),48)
    A.tag(volume,'background','Physical liquid volume; only its surface contour is drawn');volume.lineart.usage='EXCLUDE';volume['liquid_volume']=True
    ring=[(.0384*math.cos(k*math.tau/48),.0384*math.sin(k*math.tau/48),.145) for k in range(49)]
    A.tag(G.tube('Liquid surface contour',ring,.0005),'drink_contents','Transparent liquid boundary')
    warm=A.tag(G.tube('Drink surface light',[(.0384*math.cos(a),.0384*math.sin(a),.1455) for a in [math.radians(-150+j*60/20) for j in range(21)]],.0004),'lighting_cue','Fixed window reflection on the transparent liquid surface');warm['p0_lighting_cue']=True
    warm=A.tag(G.tube('Glass side light',[(-.027,-.027,.025),(-.030,-.029,.10),(-.031,-.030,.17)],.00035),'lighting_cue','Restrained fixed light along the glass surface');warm['p0_lighting_cue']=True
    A.tag(G.tube('Cocktail straw',[(.026,.020,.025),(.027,.020,.19),(.043,.025,.266)],.0024),'drink_contents','Straw continues into the drink beside the ice')
    ice=[]
    # Three cubes at three depths: one floating at the surface, one mid-glass, one low, clear of the straw.
    cubes=[(-.014,.004,.137),(.009,-.007,.109),(-.013,-.011,.081)]
    for k,(x,y,z) in enumerate(cubes):
        cube=A.tag(G.block('Floating ice cube',(x,y,z),(.020,.020,.020),.0025),'drink_contents','Separated ice cubes at different depths inside the glass')
        cube['ice_cube']=True;cube['ice_index']=k;ice.append(cube)
    root=A.group('Reusable cocktail glass',before,position,role,'Glass base stays supported on the tabletop')
    root['cocktail_index']=index
    def action(u):
        for k,cube in enumerate(ice):
            cube.rotation_euler=(.12*math.sin(u*math.tau+k),.10*math.cos(u*math.tau+k),(-1 if k%2 else 1)*(u*1.15+index*.3))
            cube.location.z=cubes[k][2]+.0012*math.sin(u*math.tau+k+index)
            cube.keyframe_insert('rotation_euler');cube.keyframe_insert('location')
    return dict(root=root,shell=shell,ice=ice,action=action,rim=rim)


def glass_grasp(drink,right,palm_deg,wrist,height=.075,pivot='bone',fade=0.,options=None):
    """Cylindrical power grasp on the cocktail wall (research/reference_shots/glass_grasp.md): palm on the entry side
    turned `palm_deg` toward the lens, fingers wrapped round the far side, thumb opposed across the near side, every
    phalanx resting on the wall. `wrist` is (extension, ulnar deviation) in degrees, turned about `pivot`; `fade` moves the
    line-art fade centre toward the wrist; `options` passes further `real_hands.wrap` options (thenar pad, contact gap)."""
    import numpy as np
    root=drink['root'];bpy.context.view_layer.update();world=root.matrix_world.copy();side=1 if right else -1
    angle=math.radians(palm_deg);axes=world.to_3x3()
    inverse=np.array(world.inverted())
    heights,radii=zip(*WALL)
    def clearance(points):
        local=points@inverse[:3,:3].T+inverse[:3,3];h=local[:,2]
        wall=np.interp(h,heights,radii);depth=np.hypot(local[:,0],local[:,1])-wall
        return np.where((h>-.002)&(h<WALL[-1][0]+.002),depth,1.)
    hand=H.wrap('R' if right else 'L',world@Vector((0,0,height)),axes@Vector((side*math.cos(angle),-math.sin(angle),0)),
                axes@Vector((0,0,1)),clearance,wrist=wrist,pivot=pivot,fade=fade,**(options or {}))
    meshes=[o for o in hand.children_recursive if o.type=='MESH']
    for mesh in meshes:
        A.tag(mesh,'hand','Power grasp on the glass wall: palm on the entry side, fingers round the far side, thumb across the near side')
    # The one level direction the wrap can let go along without sweeping through the wall (25 cm path, 2 deg steps).
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();skin=[]
    for mesh in meshes:
        ev=mesh.evaluated_get(deps);data=ev.to_mesh();co=np.empty(len(data.vertices)*3);data.vertices.foreach_get('co',co);ev.to_mesh_clear()
        skin.append(np.c_[co.reshape(-1,3),np.ones(len(co)//3)]@np.array(ev.matrix_world).T[:,:3])
    skin=np.concatenate(skin)
    def swept(direction):return max(-min(float(clearance(skin+direction*t).min()),0.) for t in np.linspace(0,.25,51))
    level=[axes@Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0)) for a in range(0,360,2)]
    release=min(level,key=lambda v:swept(np.array(v)))
    hand['p0_release']=list(release);hand['p0_release_sweep_mm']=round(swept(np.array(release))*1000,2)
    hand['p0_hand']=True;hand['p0_cropped_grip']=True
    hand['p0_entry_side']=side;hand['p0_grip_style']='cylindrical_power_grasp'
    return hand


def turned_glass_grip(drink,right,around_deg,roll_deg):
    """The library pinch, swung `around_deg` about the glass toward the lens and rolled about the forearm so the
    back of the hand, knuckles and fingers face the lens (not edge-on); fingers are kept outside the glass wall."""
    root=drink['root'];bpy.context.view_layer.update();world=root.matrix_world
    side=1 if right else -1
    swing=Matrix.Rotation(math.radians(-side*around_deg),3,'Z')
    forward=swing@Vector((-side,0,0));normal=swing@Vector((0,-side,0))
    normal=Matrix.Rotation(math.radians(roll_deg),3,forward)@normal
    target=world@Vector((0,0,.10))-forward*.047
    hand=H.place('pinch','R' if right else 'L',target=target,forward=forward,normal=normal,anchor='grip')
    inverse=world.inverted()
    # Rigidly back the whole hand off the wall (no vertex flattening): the pinch pads rest on the glass.
    for _ in range(12):
        bpy.context.view_layer.update()
        local=[inverse@(m.matrix_world@v.co) for m in hand.children_recursive if m.type=='MESH' for v in m.data.vertices]
        inner=min([math.hypot(p.x,p.y) for p in local if -.005<p.z<.205]+[1.])
        low=min(p.z for p in local)
        if inner>=.046 and low>=.004:break
        hand.location+=-forward*max(0.,.0465-inner)+Vector((0,0,max(0.,.0045-low)))
    for mesh in [o for o in hand.children_recursive if o.type=='MESH']:
        A.tag(mesh,'hand','Cropped grip fitted outside the glass wall, back of the hand toward the lens')
    hand['p0_hand']=True;hand['p0_cropped_grip']=True
    hand['p0_entry_side']=side;hand['p0_grip_style']='turned_side_grip'
    return hand


def background(long_table=False):
    V.window((.8,2.6,1.45));V.plant((1.4,2.1,0),1.45)
    for x in [-.4,.4] if long_table else [-.7,.7]:
        chair=V.chair((x,2.15 if long_table else 1.55,0))
        for obj in chair.children_recursive:
            if obj.type=='MESH':A.tag(obj,'background','Faint seated context, clear of the tabletop and filming path')


def stack_light_cues(position,radius,stack_base):
    """Source-facing yellow rim arcs on the platter rim and on each pancake layer's upper edge."""
    x,y,z=position;angle=math.atan2(LIGHT[1],LIGHT[0])
    def arc(name,r,height,span):
        points=[(x+r*math.cos(a),y+r*math.sin(a),z+height) for a in [angle+math.radians(-span/2+j*span/24) for j in range(25)]]
        cue=A.tag(G.tube(name,points,.00045),'lighting_cue','Fixed source-facing contour attached to a real surface');cue['p0_lighting_cue']=True
    arc('Platter window-facing rim light',radius*1.003,.019,70)
    for i in range(4):arc('Pancake layer light edge',.082+(i%2)*.003+.0004,stack_base+i*.016+.011,70)


def build(gid,record,P):
    state=dict(hero=[],actions=[],contacts=[],adaptations=[],camera_height_support=0.,hand_count=0,silhouettes=0)
    def finish(hero,p,t,sample):
        state.update(hero=hero,target_position=Vector(p),target_aim=Vector(t),sample=sample)
        return state
    if gid=='table_spread_orbit':
        A.table((.14,.18,0),.65);background()
        platter((-.13,.06,.785),.175);pizza=imported_food('pizza',(-.13,.06,.793),'hero');pizza.scale.z=.55;slice_round(pizza,pulled=180.,pull=.025)
        A.plate((.28,-.22,.785));imported_food('salad_portion',(.28,-.22,.794))
        pasta=A.pasta((-.17,.43,.785))
        for obj in P.members(pasta):A.tag(obj,'support','Pasta plate shares the spread; the pizza stays the hero')
        drinks=[cocktail((.33,.20,.785),0),cocktail((-.31,-.12,.785),1)]
        state['actions']+=[d['action'] for d in drinks]
        state['triangle_points']=[Vector((-.13,.06,.83)),Vector((-.17,.43,.84)),Vector((.28,-.22,.84))]
        state['contacts'].append(dict(kind='table_spread',primary='pizza',all_plates_off_table_center=True))
        state['camera_up']=(0,1,0)
        state['adaptations'].append('A fixed tabletop up reference prevents roll snapping as the camera reaches overhead, without raising the phone beyond normal reach.')
        return finish(P.members(pizza),(0,.16,1.98),(0,.16,.82),lambda u,p,t:(p+Vector((-.30*(1-P.smooth(u)), -.61*(1-P.smooth(u)), -.43*(1-P.smooth(u)))),t))
    if gid=='glass_slide_close':
        A.table((.12,.20,0),.65);background()
        A.plate((.27,.40,.785));bread((.27,.40,.794))
        drink=cocktail((-.08,-.05,.785),0,'support',primary=True);hand=glass_grasp(drink,False,**SLIDE_GRASP)
        P.attach(hand,drink['root']);state['hand_count']=1;state['actions'].append(drink['action'])
        def action(u):
            s=P.smooth(u);drink['root'].location=Vector((-.08,-.05,.785))+Vector((-.18*(1-s),.16*(1-s),0))
            drink['root'].rotation_euler.z=.15*(1-s);drink['root'].keyframe_insert('location');drink['root'].keyframe_insert('rotation_euler')
        state['actions'].append(action)
        state['contacts'].append(dict(kind='supported_drink_slide',glass=drink['root'].name,hand=hand.name,surface_z=.785))
        # The surface cube keeps the published framing; the two submerged cubes are drawn as drink contents.
        heroes=[drink['rim']]+drink['ice'][:1]
        state['adaptations'].append('Close framing protects the rim and visible ice in the middle band; the supporting glass body can extend below it, as in the reference.')
        return finish(heroes,(.015,-.40,1.02),(-.08,-.05,.945),lambda u,p,t:(p+Vector((.06*(1-P.smooth(u)),0,.015*(1-P.smooth(u)))),t))
    # Two cropped hands stay on opposite sides and pull toward themselves.
    A.tag(G.block('Long commercial dining tabletop',(0,.55,.752),(1.4,2.65,.066),.025),'structure','A continuous supported path; the creator walks beside the long table')
    background(long_table=True)
    platter((.16,1.15,.785),.15);stack=pancakes((.16,1.15,.793));stack_light_cues((.16,1.15,.785),.15,.008)
    A.plate((.14,.10,.785));salad=imported_food('salad_portion',(.14,.10,.794))
    # Couple the salad and its actual plate as a single supported prop.
    plate=next(o for o in bpy.context.scene.objects if o.name.startswith('Plate with formed rim'))
    bowl=A.empty('Sliding salad and plate');P.attach(salad,bowl);P.attach(plate,bowl)
    near=cocktail((.16,-.35,.785),0);far=cocktail((.16,.55,.785),1)
    state['actions'] += [near['action'],far['action']]
    right=glass_grasp(near,True,**CLEAR_GRASP);bpy.context.view_layer.update();relative=near['root'].matrix_world.inverted()@right.matrix_world
    # The hand arrives and lets go along its open direction, from and to off frame.
    release=Vector(right['p0_release']);reach=.9
    left=H.place('relaxed','L',target=(-.006,.10,.817),forward=(1,0,0),normal=(0,0,1),anchor='f_middle.03');left['p0_hand']=True;left['p0_cropped_grip']=True
    left['p0_entry_side']=-1;left['p0_grip_style']='plate_rim_pull'
    bpy.context.view_layer.update()
    mesh=next(o for o in left.children_recursive if o.type=='MESH')
    # Palm down above the tabletop, fingers curled over the left raised rim.
    inverse=mesh.matrix_world.inverted()
    for vertex in mesh.data.vertices:
        p=mesh.matrix_world@vertex.co
        if p.z<.789:p.z=.789;vertex.co=inverse@p
    for obj in left.children_recursive:
        if obj.type=='MESH':A.tag(obj,'hand','Left-side grip holds the left plate rim and pulls toward itself')
    left_start=left.location.copy();state['hand_count']=2
    def action(u):
        a=P.smooth((u-.08)/.19);b=P.smooth((u-.33)/.19);c=P.smooth((u-.60)/.20)
        near['root'].location.x=.16+.40*a;far['root'].location.x=.16+.40*c;bowl.location.x=-.38*b
        bpy.context.view_layer.update()
        if u<.32:
            right.matrix_world=near['root'].matrix_world@relative;away=P.smooth((u-.27)/.05)
        elif u<.54:
            right.matrix_world=far['root'].matrix_world@relative;away=1.
        else:
            right.matrix_world=far['root'].matrix_world@relative
            away=1-P.smooth((u-.54)/.06)+P.smooth((u-.82)/.08)
        right.location+=release*reach*away
        left.location=left_start+Vector((-.38*b-.55*(1-P.smooth((u-.27)/.06))-.55*P.smooth((u-.53)/.08),0,0))
        for obj in [near['root'],far['root'],bowl,right,left]:obj.keyframe_insert('location');obj.keyframe_insert('rotation_euler')
        bpy.context.view_layer.update()
    state['actions'].append(action)
    state['contacts'].append(dict(kind='companion_clears_path',surface_z=.785,sequence=['right hand pulls near drink right','left hand pulls salad left','right hand pulls far drink right'],maximum_hands=2,all_props_stay_on_table=True,left_hand=left.name,right_hand=right.name,plate_root=bowl.name,near_drink=near['root'].name,far_drink=far['root'].name))
    state['adaptations'].append('One hand enters from each side. The right hand pulls both drinks right; the left hand grips the left plate rim and pulls it left. Neither hand crosses the row or pushes from the opposite side. The creator films beside the table at pancake height.')
    return finish(P.members(stack),(.16,.65,.87),(.16,1.15,.85),lambda u,p,t:(p+Vector((0,-1.55*(1-P.smooth(u)),.012*math.sin(math.pi*u))),t))
