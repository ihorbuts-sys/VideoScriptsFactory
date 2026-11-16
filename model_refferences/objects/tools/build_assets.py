"""Native, editable clay prop library. Run with Blender in background mode.

Generated turnarounds are design input; these meshes are authored geometry, not
automatic image-to-mesh reconstructions. All exports use metres and Z-up.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[1]
sys.path.insert(0,str(BASE/'guides/blender_motion'))
sys.path.insert(0,str(ROOT/'tools'))
import geometry as G
from catalog import ASSETS

PALETTE={'yellow':'F6BC27','sage':'7F987D','teal':'447D78','pink':'DB9E92',
         'cream':'F6E9D3','white':'FFF7E8','charcoal':'333B39','brown':'946549',
         'crust':'DFAA41','gold':'F3B548','chocolate':'69402C','coffee':'A76C3E',
         'leaf':'5F8454','glass':'C9D6C9'}
MATS={}

def material(key):
    if key in MATS:return MATS[key]
    h=PALETTE[key];rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m=bpy.data.materials.new('Loca clay / '+key);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=.58;p.inputs['Specular IOR Level'].default_value=.28
    if key=='glass':
        p.inputs['Transmission Weight'].default_value=.7;p.inputs['Roughness'].default_value=.22
        p.inputs['IOR'].default_value=1.35
    m.diffuse_color=(*rgb,1);MATS[key]=m;return m

def finish(o,name,color):
    o.name=name;o.data.materials.clear();o.data.materials.append(material(color))
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
    return o

def block(n,p,d,c='cream',r=.01):
    G.MAT=material(c);o=G.block(n,p,d,r)
    for f in o.data.polygons:f.use_smooth=False
    if r:
        o.modifiers[-1].segments=5
        norm=o.modifiers.new('Weighted clay normals','WEIGHTED_NORMAL');norm.keep_sharp=True
    return o

def ball(n,p,d,c='cream'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p)
    o=bpy.context.object;o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,n,c)

def lathe(n,profile,p=(0,0,0),c='cream',ellipse=1):
    G.MAT=material(c);return G.lathe(n,profile,p,64,ellipse)

def tube(n,pts,r=.01,c='cream'):
    G.MAT=material(c);o=G.tube(n,pts,r)
    # Fill open ends, preserving a continuous solid tube for reusable props.
    bm=bmesh.new();bm.from_mesh(o.data)
    edges=[e for e in bm.edges if e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bm.normal_update();bm.to_mesh(o.data);bm.free();return o

def empty(n,p=(0,0,0)):
    o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.location=p;return o

def group(n,before):
    parts=set(bpy.data.objects)-before;o=empty(n)
    for item in parts:
        if item.parent not in parts:item.parent=o
    return o

def anchor(root,name,p):
    a=empty('Anchor / '+name,p);a.parent=root;a.empty_display_size=.015;a.hide_render=True
    a['anchor_type']=name;return a

def move(root,p,scale=1,turn=0):
    root.location=p;root.scale=(scale,)*3;root.rotation_euler.z=turn;return root

def ring(n,p,r,thick,c):
    pts=[(p[0]+r*math.cos(t*math.tau/32),p[1]+r*math.sin(t*math.tau/32),p[2]) for t in range(33)]
    return tube(n,pts,thick,c)

def plate(p=(0,0,0)):
    return lathe('Plate / formed rim',[(0,0),(.038,0),(.041,.004),(.105,.008),(.119,.022),(.118,.028),(.112,.029),(.092,.014),(0,.011)],p)

def croissant(broken=False,oozing=False):
    before=set(bpy.data.objects)
    for side in [-1,1] if broken else [0]:
        start=set(bpy.data.objects)
        # Seven overlapping bent rolls, with a flattened support underneath.
        for i in range(-3,4):
            x=i*.022;size=1-abs(i)*.16;y=.010*abs(i)-.006
            o=ball('Croissant / broad rolled lobe',(x,y,.028*size),(.027*size,.047*size,.030*size),'gold' if i%2==0 else 'crust')
            o.rotation_euler.z=-i*.15
            if broken:
                bm=bmesh.new();bm.from_mesh(o.data)
                # Owner correction: two equal halves, never a small broken end.
                bpy.context.view_layer.update()
                plane=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((1,0,0))
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,
                    plane_co=plane,plane_no=normal,clear_outer=side<0,clear_inner=side>0)
                edge=[e for e in bm.edges if e.is_boundary]
                if edge:bmesh.ops.holes_fill(bm,edges=edge,sides=0)
                bm.normal_update();bm.to_mesh(o.data);bm.free()
                if not len(o.data.vertices):bpy.data.objects.remove(o,do_unlink=True)
        if broken:
            x=-side*.0008
            ball('Croissant / cream exposed crumb',(x,-.001,.028),(.0018,.035,.023),'cream')
            ball('Filling / chocolate core',(x-side*.0018,-.003,.029),(.0025,.023,.013),'chocolate')
            part=group('Break / left half' if side<0 else 'Break / right half',start)
            part.location.x=side*.033
            part.rotation_euler.z=side*math.radians(50)
            anchor(part,'broken_face',(0,0,.028))
            if oozing and side<0:
                fill_start=set(bpy.data.objects)
                ball('Filling / bulging from cavity',(.006,-.004,.028),(.011,.022,.014),'chocolate')
                tube('Filling / thick downward ooze',[(.007,-.005,.03),(.016,-.004,.024),(.017,-.004,.014),(.015,-.004,.006)],.0055,'chocolate')
                ball('Filling / drip tip',(.015,-.004,.007),(.007,.008,.007),'chocolate')
                ooze=group('Filling control / length',fill_start);ooze.parent=part
                ooze['animation_control']='Scale Z about broken-face anchor for a slow thick ooze; no water-like stream'
    root=group('Croissant assembly',before);anchor(root,'support',(0,0,0));return root

def build(id):
    before=set(bpy.data.objects)
    if id in ['croissant','filled_croissant','croissant_oozing']:
        return croissant(id!='croissant',id=='croissant_oozing')
    if id=='cup_saucer':
        lathe('Saucer',[(0,0),(.045,0),(.082,.008),(.087,.014),(.084,.018),(.069,.010),(0,.009)])
        lathe('Cup / hollow body',[(0,.009),(.028,.009),(.032,.015),(.049,.070),(.054,.108),(.051,.114),(.046,.113),(.044,.104),(.035,.035),(.022,.019),(0,.019)])
        tube('Cup / open handle',[(.046,0,.094),(.079,0,.093),(.088,0,.061),(.073,0,.037),(.039,0,.042)],.0065)
        lathe('Coffee surface',[(0,.101),(.046,.101),(.046,.103),(0,.103)],c='coffee')
        # A soft clay heart, not a detailed photographic latte pattern.
        for x in [-.008,.008]:ball('Latte heart lobe',(x,-.002,.104),(.012,.015,.0007),'cream')
        ball('Latte heart tip',(0,.011,.104),(.010,.014,.0007),'cream')
    elif id=='dining_table':
        block('Tabletop',(0,0,.725),(1,.72,.05),'brown',.045)
        lathe('Table / pedestal',[(0,0),(.24,0),(.26,.025),(.23,.055),(.055,.09),(.045,.68),(.12,.70),(0,.70)],c='charcoal')
    elif id in ['dining_chair','bar_stool']:
        tall=id=='bar_stool';seat=.73 if tall else .445;w=.32 if tall else .42
        for x in [-1,1]:
            for y in [-1,1]:
                tube('Chair / splayed leg',[(x*w*.34,y*.13,seat+.012),(x*w*.44,y*.19,seat*.48),(x*w*.54,y*.23,.025)],.022,'brown')
        block('Chair / rounded sculpted seat',(0,0,seat+.005),(w+.035,.43 if not tall else .37,.060),'yellow',.029)
        # Bent backrest follows the sitter's back (+Y), visibly open above seat.
        for x in [-1,1]:tube('Chair / back support',[(x*w*.42,.11,seat-.01),(x*w*.44,.17,seat+.20),(x*w*.39,.18,seat+.29)],.019,'yellow')
        block('Chair / broad rounded backrest',(0,.174,seat+.26),(w,.075,.19),'yellow',.034)
        if tall:ring('Stool / foot ring',(0,0,.29),.22,.012,'charcoal')
    elif id=='bar_counter':
        block('Counter / top',(0,0,1.04),(2.4,.75,.08),'brown',.038)
        block('Counter / front',(0,-.30,.52),(2.26,.10,.98),'sage',.024)
        for x in [-1.1,1.1]:block('Counter / side',(x,.015,.51),(.08,.62,.98),'sage',.02)
        for z in [.065,.47,.94]:block('Counter / staff storage shelf',(0,.02,z),(2.2,.58,.035),'brown',.012)
        for x in [-.74,0,.74]:block('Counter / recessed front panel',(x,-.356,.52),(.66,.018,.76),'teal',.025)
        tube('Counter / customer foot rail',[(-1.08,-.46,.22),(1.08,-.46,.22)],.019,'yellow')
        for x in [-.9,.9]:tube('Counter / rail support',[(x,-.3,.2),(x,-.46,.22)],.018,'yellow')
    elif id in ['pastry_rack','display_case']:
        case=id=='display_case';w=1.25 if case else 1.;depth=.65 if case else .48;h=1.15 if case else 1.55
        for x in [-1,1]:
            for y in [-1,1]:block('Rack / upright',(x*(w/2-.035),y*(depth/2-.035),h/2),(.055,.055,h),'sage',.022)
        levels=[.46,.83] if case else [.14,.50,.86,1.22]
        if case:
            block('Case / base',(0,0,.21),(w,depth,.42),'sage',.04)
            block('Case / counter lip',(0,-.01,.435),(w+.04,depth+.04,.045),'yellow',.018)
            block('Case / rear panel',(0,depth/2-.012,.77),(w-.07,.025,.60),'sage',.009)
            for x in [-1,1]:block('Case / side glass',(x*(w/2-.04),0,.79),(.009,depth-.08,.62),'glass',.004)
            block('Case / front pane',(0,-depth/2+.025,.79),(w-.09,.009,.62),'glass',.003)
            block('Case / rounded roof',(0,0,1.12),(w,depth,.06),'cream',.025)
        for z in levels:
            block('Rack / shelf',(0,0,z),(w-.05,depth,.035),'brown',.014)
            tray=move(build('serving_tray'),(0,0,z+.018))
            tray.scale=((w-.10)/.36,(depth-.07)/.26,1)
            # Trays and food share a physical support plane.
            for x in [-.30,-.10,.10,.30]:move(build('croissant'),(x,-.045,z+.035),.86)
    elif id=='pastry_box':
        block('Box / base',(0,0,.006),(.30,.23,.012),'cream',.006)
        for x in [-1,1]:block('Box / end',(x*.145,0,.046),(.01,.23,.08),'cream',.006)
        for y in [-1,1]:block('Box / side',(0,y*.11,.046),(.28,.01,.08),'cream',.005)
        lid=empty('Lid hinge',(0,.112,.087));lid.rotation_euler.x=math.radians(-110)
        o=block('Box / hinged lid',(0,-.112,0),(.30,.23,.012),'pink',.008);o.parent=lid
        for x in [-.072,.072]:
            for y in [-.052,.052]:
                lathe('Sweet / paper cup',[(0,0),(.039,0),(.043,.021),(.038,.023),(.036,.006),(0,.006)],(x,y,.012))
                ball('Sweet / chunky bun',(x,y,.037),(.034,.029,.023),'gold')
                ball('Sweet / chocolate top',(x,y,.054),(.026,.023,.008),'chocolate')
    elif id=='kitchen_tongs':
        tube('Tongs / joined spring',[(-.015,.20,.014),(-.023,.23,.018),(0,.25,.022),(.023,.23,.018),(.015,.20,.014)],.007,'charcoal')
        for side in [-1,1]:
            tube('Tongs / arm',[(side*.015,.21,.014),(side*.022,.13,.014),(side*.026,.035,.014)],.007,'charcoal')
            block('Tongs / grip',(side*.022,.14,.015),(.016,.075,.018),'sage',.006)
            ball('Tongs / spoon jaw',(side*.026,.020,.014),(.016,.026,.008),'charcoal')
    elif id=='kettle':
        lathe('Kettle / body',[(0,0),(.055,0),(.075,.022),(.079,.086),(.064,.132),(.039,.145),(.035,.134),(.047,.12),(.061,.081),(.056,.025),(0,.02)],c='yellow')
        lathe('Kettle / removable lid',[(0,.143),(.041,.143),(.044,.15),(.035,.159),(0,.159)],c='yellow')
        ball('Kettle / lid knob',(0,0,.169),(.018,.018,.012),'charcoal')
        tube('Kettle / open handle',[(-.061,0,.13),(-.107,0,.15),(-.115,0,.092),(-.077,0,.044)],.012,'charcoal')
        # Open gooseneck: hollow shell and an actual lumen at the tip.
        G.MAT=material('yellow');o=G.tube('Kettle / hollow gooseneck',[(.063,0,.045),(.100,0,.063),(.115,0,.16),(.143,0,.179),(.158,0,.164)],.007)
        solid=o.modifiers.new('Spout wall','SOLIDIFY');solid.thickness=.0015
    elif id=='espresso_machine':
        block('Machine / housing',(0,.025,.25),(.58,.34,.42),'charcoal',.055)
        block('Machine / fascia',(0,-.16,.352),(.53,.035,.115),'yellow',.018)
        block('Machine / tray',(0,-.16,.035),(.54,.28,.055),'charcoal',.018)
        for x in [-.19,-.095,0,.095,.19]:block('Machine / broad tray slot',(x,-.19,.064),(.055,.16,.005),'cream',.004)
        for x in [-.17,.17]:
            o=lathe('Machine / control',[(0,0),(.029,0),(.03,.02),(0,.025)],(x,-.19,.35),'yellow');o.rotation_euler.x=math.pi/2
        lathe('Machine / group head',[(0,0),(.064,0),(.069,.045),(.061,.075),(0,.075)],(0,-.18,.205),'cream')
        tube('Machine / portafilter handle',[(0,-.19,.22),(0,-.35,.21),(0,-.40,.21)],.023,'charcoal')
        tube('Machine / steam wand',[(.23,-.15,.29),(.24,-.25,.18),(.20,-.26,.11)],.009,'cream')
    elif id in ['drinking_glass','bottle']:
        if id=='bottle':
            lathe('Bottle / body',[(0,0),(.027,0),(.035,.012),(.035,.16),(.027,.184),(.014,.20),(.013,.239),(0,.239)],c='sage')
            lathe('Bottle / cap',[(0,.235),(.016,.235),(.016,.25),(0,.25)],c='yellow')
            block('Bottle / blank label',(0,-.034,.103),(.043,.006,.067),'cream',.006)
        else:
            lathe('Glass / hollow wall',[(0,0),(.029,0),(.035,.008),(.038,.103),(.035,.107),(.032,.103),(.029,.016),(0,.016)],c='glass')
            lathe('Glass / liquid',[(0,.016),(.029,.016),(.032,.078),(0,.078)],c='coffee')
    elif id=='pendant':
        lathe('Pendant / dome',[(.17,.26),(.168,.28),(.156,.34),(.12,.40),(.06,.43),(.012,.44),(.012,.42),(.055,.414),(.111,.386),(.145,.33),(.155,.273),(.17,.26)],c='yellow')
        lathe('Pendant / cream diffuser',[(0,.265),(.157,.265),(.157,.27),(0,.27)],c='cream')
        tube('Pendant / cord',[(0,0,.43),(0,0,.58)],.005,'charcoal')
        lathe('Pendant / ceiling rose',[(0,.58),(.05,.58),(.05,.60),(0,.60)],c='charcoal')
    elif id=='plant':
        lathe('Pot',[(0,0),(.055,0),(.073,.11),(.077,.12),(.073,.127),(.063,.121),(.051,.015),(0,.015)],c='yellow')
        lathe('Soil',[(0,.11),(.064,.11),(0,.112)],c='brown')
        for i in range(10):
            t=i*2.399;z=.17+(i%4)*.045;p=(math.cos(t)*.064,math.sin(t)*.064,z)
            tube('Plant / stem',[(0,0,.105),(p[0]*.35,p[1]*.35,z-.035),p],.005,'leaf')
            o=ball('Plant / chunky leaf',p,(.026,.014,.061),'leaf');o.rotation_euler=(.38*math.cos(t),.65*math.sin(t),t)
    elif id=='serving_tray':
        block('Tray / recessed base',(0,0,.006),(.36,.26,.012),'cream',.015)
        for y in [-1,1]:block('Tray / long rim',(0,y*.124,.016),(.36,.012,.022),'brown',.006)
        for x in [-1,1]:
            block('Tray / end rim',(x*.174,0,.016),(.012,.26,.022),'brown',.006)
            tube('Tray / raised handle',[(x*.169,-.054,.021),(x*.18,-.045,.040),(x*.18,.045,.040),(x*.169,.054,.021)],.007,'brown')
    elif id=='cutlery':
        for x in [-.04,0,.04]:block('Utensil / sage handle',(x,0,.008),(.012,.115,.014),'sage',.006)
        tube('Fork / neck',[(-.04,.045,.009),(-.04,.068,.011)],.006)
        for x in [-.051,-.044,-.036,-.029]:tube('Fork / tine',[(x,.065,.012),(x,.105,.012)],.0028)
        block('Knife / rounded blade',(0,.074,.01),(.019,.075,.006),'charcoal',.004)
        ball('Spoon / bowl',(.04,.079,.011),(.018,.027,.005),'cream')
    elif id=='laptop':
        block('Laptop / base',(0,0,.009),(.30,.22,.018),'cream',.012)
        block('Laptop / touchpad',(0,-.059,.020),(.072,.039,.003),'yellow',.004)
        for y in [.001,.024,.047,.070]:block('Laptop / key row',(0,y,.020),(.24,.014,.005),'sage',.003)
        hinge=empty('Laptop / screen hinge',(0,.099,.019));hinge.rotation_euler.x=math.radians(-15)
        for o in [block('Laptop / screen body',(0,0,.102),(.30,.016,.205),'sage',.014),block('Laptop / screen',(0,-.009,.107),(.269,.004,.17),'charcoal',.007)]:o.parent=hinge
    elif id=='wall_shelf':
        block('Shelf / board',(0,0,.215),(1.2,.28,.05),'brown',.023)
        for x in [-.4,.4]:tube('Shelf / bracket',[(x,.10,.025),(x,.10,.19),(x,-.09,.19),(x,.10,.025)],.019,'sage')
    elif id in ['menu_board','signboard']:
        if id=='menu_board':
            block('Menu / framed board',(0,0,.325),(1.05,.055,.65),'brown',.033)
            block('Menu / face',(0,-.033,.325),(.98,.014,.58),'sage',.022)
            for x in [-.31,0,.31]:
                block('Menu / icon panel',(x,-.044,.38),(.25,.014,.33),'pink' if x>0 else 'yellow' if x==0 else 'teal',.025)
                for z in [.20,.16]:block('Menu / broad resource mark',(x,-.055,z),(.19,.008,.014),'cream',.006)
                # Pictograms are genuine relief; no words or numerals.
                if x<0:
                    o=lathe('Menu / cup pictogram',[(0,0),(.042,0),(.063,.08),(0,.08)],(x,-.058,.36));o.scale.y=.18
                elif x==0:block('Menu / glass pictogram',(x,-.06,.40),(.10,.012,.14),'brown',.015)
                else:
                    o=move(build('croissant'),(x,-.065,.40),1.0);o.rotation_euler.x=math.pi/2
        else:
            tube('Sign / bracket',[(0,.07,.57),(0,.20,.57),(0,.20,.20)],.026,'sage')
            o=lathe('Sign / disc',[(0,0),(.25,0),(.26,.022),(.25,.055),(0,.055)],(0,-.025,.30),'yellow');o.rotation_euler.x=math.pi/2
            for side in [-1,1]:
                block('Sign / cup pictogram',(0,side*.033,.30),(.20,.015,.13),'cream',.045)
                tube('Sign / steam',[(0,side*.044,.40),(-.02,side*.044,.44),(0,side*.044,.48)],.012)
    elif id in ['glazed_door','window','storefront']:
        if id=='storefront':
            # Real apertures: wall assembled around openings, not a solid blocker.
            for x,w in [(-1.74,.12),(-.60,.12),(1.73,.14)]:block('Facade / wall pier',(x,0,1.4),(w,.25,2.8),'cream',.02)
            block('Facade / lintel',(0,0,2.65),(3.6,.25,.30),'cream',.02)
            block('Facade / window sill wall',(.57,0,.43),(2.15,.25,.86),'cream',.02)
            move(build('glazed_door'),(-1.16,-.08,0),.99)
            move(build('window'),(.56,-.04,.89),1.47)
            block('Facade / awning',(0,-.45,2.56),(3.67,.85,.08),'yellow',.035)
            block('Facade / awning valance',(0,-.86,2.46),(3.67,.05,.20),'yellow',.03)
        elif id=='glazed_door':
            for x in [-.47,.47]:block('Door / jamb',(x,0,1.15),(.06,.18,2.3),'sage',.016)
            block('Door / lintel',(0,0,2.27),(1.,.18,.06),'sage',.012)
            block('Door / threshold',(0,0,.015),(1,.18,.03),'cream',.01)
            hinge=empty('Door hinge',(-.425,0,.04))
            start=set(bpy.data.objects)
            for x in [0,.84]:block('Door / leaf stile',(x,0,1.08),(.055,.055,2.16),'sage',.014)
            for z in [0,2.14]:block('Door / leaf rail',(.42,0,z),(.84,.055,.06),'sage',.012)
            block('Door / clear pane',(.42,0,1.07),(.78,.012,2.05),'glass',.003)
            for s in [-1,1]:tube('Door / pull handle',[(.72,s*.035,.90),(.72,s*.09,.94),(.72,s*.09,1.20),(.72,s*.035,1.24)],.014,'yellow')
            for o in set(bpy.data.objects)-start:o.parent=hinge
        else:
            for x in [-.67,0,.67]:block('Window / upright',(x,0,.75),(.06,.16,1.5),'sage',.014)
            for z in [.03,.75,1.47]:block('Window / crossbar',(0,0,z),(1.4,.16,.06),'sage',.014)
            block('Window / sill',(0,-.035,.025),(1.48,.24,.05),'cream',.014)
            for x in [-.335,.335]:
                for z in [.39,1.11]:block('Window / pane',(x,0,z),(.60,.012,.65),'glass',.003)
    else:raise KeyError(id)
    root=group('Loca / '+id,before)
    anchors={'cup_saucer':{'support':(0,0,0),'handle':(.080,0,.065),'liquid':(0,0,.103)},
        'kettle':{'support':(0,0,0),'grip':(-.108,0,.10),'spout':(.158,0,.164)},
        'dining_table':{'tabletop':(0,0,.75),'setting_near':(0,-.21,.75),'setting_far':(0,.21,.75)},
        'dining_chair':{'seat':(0,0,.48),'front':(0,-.25,.48)},'bar_stool':{'seat':(0,0,.765)},
        'bar_counter':{'worktop':(0,0,1.08),'customer_edge':(0,-.375,1.08)},
        'espresso_machine':{'outlet':(0,-.18,.205),'tray':(0,-.19,.064)},
        'pastry_box':{'floor':(0,0,.012)},'serving_tray':{'floor':(0,0,.012)}}
    for name,p in anchors.get(id,{'support':(0,0,0)}).items():anchor(root,name,p)
    return root

def studio(scene):
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=6
    scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.7
    world=bpy.data.worlds.new('Loca / neutral studio');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.82,.88,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.3;scene.world=world

def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def bounds(objects):
    bpy.context.view_layer.update();coords=[o.matrix_world@Vector(v) for o in objects if o.type=='MESH' for v in o.bound_box]
    lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
    return lo,hi

def lighting(center,extent):
    for name,offset,power,size in [('Key',(-2,-3,4),550,3),('Fill',(3,-1,2),240,3),('Rim',(0,3,3),400,2)]:
        data=bpy.data.lights.new('Studio '+name,'AREA');data.energy=power*extent**2;data.shape='DISK';data.size=size*extent
        o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o)
        o.location=center+Vector(offset)*extent;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()

def export(id,render=True):
    clear();scene=bpy.context.scene;scene.name='Loca clay asset / '+id;studio(scene)
    root=build(id);root['asset_id']=id;root['style']='hand-moulded-plasticine-v2'
    root['units']='metres';root['front_direction']='-Y';root['editable']=True
    lo,hi=bounds(root.children_recursive);center=(lo+hi)/2;extent=max(hi-lo)
    coll=bpy.data.collections.new('Loca clay / '+id);scene.collection.children.link(coll)
    for o in [root,*root.children_recursive]:
        for old in list(o.users_collection):old.objects.unlink(o)
        coll.objects.link(o)
    coll.asset_mark();coll.asset_data.description=ASSETS[id][1]
    out=ROOT/id;out.mkdir(exist_ok=True)
    bpy.data.libraries.write(str(out/'asset.blend'),{coll},fake_user=True,compress=True)
    lighting(center,extent)
    data=bpy.data.cameras.new('Projection camera');cam=bpy.data.objects.new('Projection camera',data);scene.collection.objects.link(cam);scene.camera=cam
    cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.27
    cam.location=center+Vector((1,-1.7,1.1)).normalized()*extent*4
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True)
    views={'front':(0,-1,0),'back':(0,1,0),'left':(-1,0,0),'right':(1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(1,-1.7,1.1)}
    if render:
        viewsdir=out/'rendered';viewsdir.mkdir(exist_ok=True)
        for name,v in views.items():
            cam.location=center+Vector(v).normalized()*extent*4
            up='Y' if name not in ['top','bottom'] else 'Y'
            cam.rotation_euler=(center-cam.location).to_track_quat('-Z',up).to_euler()
            scene.render.filepath=str(viewsdir/(name+'.png'));bpy.ops.render.render(write_still=True)
    metadata=dict(id=id,category=ASSETS[id][0],description=ASSETS[id][1],style=root['style'],
        model='model.blend',status='model_rendered_pending_review' if render else 'model_built',
        dimensions_m=list(hi-lo),bbox_min=list(lo),bbox_max=list(hi),mesh_count=sum(o.type=='MESH' for o in root.children_recursive),
        anchors={o['anchor_type']:list(o.location) for o in root.children_recursive if o.get('anchor_type')},
        views=list(views),projection='orthographic; front=-Y, back=+Y, left=-X, right=+X, top=+Z, bottom=-Z',
        design_reference='design/sheet.png' if (out/'design/sheet.png').exists() else None,
        provenance='Native Blender mesh authored from the saved AI design and approved clay art direction; no automatic image-to-mesh reconstruction')
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('ASSET_EXPORTED',id,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(ASSETS)
    if '--prototype' not in args:
        raise SystemExit('Archived prototype builder: owner rejected reference fidelity. Use image-driven reconstruction. To inspect this old experiment explicitly pass --prototype.')
    no_render='--no-render' in args
    for id in [a for a in args if not a.startswith('--')]:export(id,not no_render)
