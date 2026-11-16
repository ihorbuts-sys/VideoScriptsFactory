"""Readable resources, physical table context and smooth changes of camera pitch."""
import bpy
import math
from mathutils import Vector
import assets as A
import geometry as G
import venue_assets as V
import food_assets as F
import real_hands as H
from drink_scenes import pose,smooth,glass
from motion_paths import camera_path,sequence

IDS=['card_menu_high_in_cd_whipout','card_menu_top_hold','card_pricelist_top_hold',
     'card_label_high_hold_whipout','card_tag_high_hold','card_tag_top_in_cd','card_tag_top_in_cd_through',
     'hands_garment_high_hold','hands_during_top_hold','hands_guitar_high_hold','rail_guitar_pov_truckr_mm']


def review(gid):
    if gid=='hands_during_top_hold':
        from massage_scene import REVIEW
        return dict(REVIEW)
    return dict(subject='Readable '+gid.replace('_',' ')+' in a clear supported physical setting',
        angle='Natural high oblique or overhead view, with coordinated position and X-axis pitch changes',
        motion='Continuous curved handheld path with gentle acceleration and settling; no fixed-point rotation',
        focal_point='Selected line, maker label or attached price tag stays readable before the context reveal',
        composition='Clear silhouettes, purposeful negative space, real supporting surfaces; no abstract upside-down garment placeholder',
        golden_ratio='Use clear hierarchy rather than forcing a ratio onto resource text',lighting='Fixed broad side light; no bloom',
        contacts='Paper, garment and dishes have real support; imported hand meshes use explicit fingertip/contact landmarks',
        handover='Same-scene handover where the script continues to a related resource',
        mobile='Short diagonal lean or small step with the phone; prop the phone or use a helper for the two-hand held-menu demonstration')


def page(kind='lunch'):
    before=set(bpy.data.objects);w=.34;h=.39
    A.tag(G.block('Paper '+kind,(0,h/2,.002),(w,h,.004),.003),'support','One readable sheet with a real supporting edge')
    if kind=='lunch':title='LUNCH MENU';rows=[('MAIN + SIDE','LUNCH PRICE'),('DRINK','INCLUDED'),('TODAY','ASK TEAM')]
    elif kind=='treatment':title='TREATMENTS';rows=[('SIGNATURE CARE','BOOKED'),('RELAXATION','DURATION'),('FACE + BODY','DETAILS')]
    else:title='PRICE LIST';rows=[('STARTING FROM','PRICE'),('CONSULTATION','FROM'),('EXTRAS','PRICE')]
    V.lettering(title,(0,.335,.006),.029,'hero',True)
    for i,(left,right) in enumerate(rows):
        y=.245-i*.075;V.lettering(left,(-.055,y,.006),.016,'hero' if i==0 else 'background',True)
        V.lettering(right,(.105,y,.006),.012,'hero' if i==0 else 'background',True)
    if kind=='price':V.lettering('BOOKING / OPTIONS',(0,.045,.006),.014,'background',True)
    elif kind=='treatment':V.lettering('SELECT YOUR CARE',(0,.045,.006),.014,'background',True)
    return A.group('Readable '+kind+' sheet',before,(0,0,0),'support','Distinct title and row hierarchy identify the resource')


def folded_garment():
    before=set(bpy.data.objects)
    A.tag(G.block('Folded garment body',(0,0,.020),(.42,.38,.04),.025),'support','Right-way-up folded shirt: collar at the top, hem at the bottom')
    for side in [-1,1]:
        sleeve=G.block('Folded sleeve',(side*.16,.025,.044),(.11,.27,.012),.012);sleeve.rotation_euler.z=side*.12;A.tag(sleeve,'background','Folded sleeves have visible seams rather than a broken hanger')
    A.tag(G.tube('Readable folded collar',[(-.075,.15,.047),(-.045,.10,.052),(0,.115,.055),(.045,.10,.052),(.075,.15,.047)],.006),'hero','Collar makes garment orientation immediately recognisable')
    for x in [-.13,.13]:A.tag(G.tube('Fabric fold seam',[(x,-.17,.045),(x,.10,.045)],.0008),'background','Subtle seams explain folded fabric')
    A.tag(G.tube('Button placket',[(0,.10,.046),(0,-.15,.046)],.0012),'background','Straight placket connects collar to hem')
    for y in [.06,-.01,-.08]:A.tag(G.lathe('Shirt button',[(0,0),(.004,0),(.004,.002),(0,.002)],(0,y,.047),16),'background','Small button detail reinforces orientation')
    return A.group('Recognisable folded shirt',before,(0,0,.785),'support','No hanger is drawn for a garment lying on the table')


def label_and_tag():
    garment=folded_garment()
    def card(title,width,height,position):
        before=set(bpy.data.objects)
        A.tag(G.block('Attached '+title+' paper',(0,0,0),(width,height,.003),.003),'support','Small resource text fits its physical label')
        V.lettering(title,(0,height*.18,.003),height*.17,'hero',True)
        V.lettering('DETAIL' if title=='MAKER' else 'PRICE',(0,-height*.20,.003),height*.16,'hero',True)
        return A.group('Attached '+title,before,position,'support','Resource belongs to the garment and remains supported')
    label=card('MAKER',.12,.075,(-.075,.075,.827))
    tag=card('PRICE TAG',.13,.11,(.19,-.06,.837));tag.rotation_euler.z=-.16
    A.tag(G.tube('Attached tag string',[(.12,.07,.836),(.18,.03,.839),(.19,-.005,.840)],.001),'support','The price tag belongs to this same garment')
    return garment,label,tag


def lunch(scene,spec):
    A.table(radius=.74);paper=page('lunch');paper.location=(-.34,-.30,.79);paper.rotation_euler.x=math.radians(50)
    holder=H.place('pinch','L',target=(-.15,.055,0),forward=(0,1,0),normal=(math.sin(math.radians(40)),0,math.cos(math.radians(40))),anchor='grip');holder.parent=paper
    pointer=H.point_on_page(paper,(.03,.245,.009));initial=pointer.location.copy()
    for t,lift in [(0,.045),(1.0,.045),(1.8,0),(3.4,0),(4.5,.06),(9,.06)]:pose(pointer,t,location=initial+Vector((0,0,lift)))
    A.pasta((.13,.11,.785));A.plate((-.31,.28,.785));A.pastry((-.31,.28,.794))
    glass((.44,.15,.785),name='Lunch water');A.fork((.31,-.04,.79))
    A.fixed_side_light((0,0,.95))
    cam=camera_path('Held menu to same lunch table',[
        (0,(-.31,-.80,1.29),(-.31,-.16,1.02)),(2.2,(-.23,-.70,1.34),(-.29,-.14,1.03)),
        (4,(-.14,-.66,1.39),(-.26,-.10,1.00)),(6,(.10,-.65,1.63),(.03,.08,.87)),
        (8.9,(.24,-.49,1.76),(.04,.08,.84))],9,lens=29)
    result=sequence(cam,9,4,['A menu is held at 50 degrees while the other hand points to the lunch offer',
        'A diagonal rising arc changes pitch and reveals all dishes on the same table'],next_guide='plate_spread_top_hold',landing=5)
    result['probe_frames']=[1,25,55,70,91,115,135]
    return result


def resource(scene,spec):
    gid=spec['id']
    if gid=='hands_during_top_hold':
        from massage_scene import build as massage
        return massage(scene,spec)
    A.table(radius=.61);A.fixed_side_light((0,0,.9))
    if gid in ['card_menu_top_hold','card_pricelist_top_hold']:
        kind='treatment' if gid=='card_menu_top_hold' else 'price';paper=page(kind);paper.location=(0,-.18,.788)
        pointer=H.point_on_page(paper,(.055,.245,.009));p=pointer.location.copy()
        for t,lift in [(0,.055),(.9,.055),(1.8,0),(3.1,0),(4.8,0)]:pose(pointer,t,location=p+Vector((0,0,lift)))
        glass((-.30,.14,.785),name='Quiet water glass',role='background')
        if kind=='treatment':G.block('Folded treatment towel',(.29,.11,.80),(.20,.27,.03),.025)
        focus=(0,.04,.80);cam=camera_path('Readable '+kind+' diagonal overhead lean',[(0,(-.06,-.17,1.50),focus),(2.1,(.015,-.12,1.46),focus),(4.8,(.08,-.18,1.48),focus)],5,31)
        return sequence(cam,5,actions=['One anatomical index settles beside the selected '+kind+' line','Menu categories and price-list hierarchy remain visibly distinct and readable'])
    if gid=='hands_guitar_high_hold':
        guitar=V.guitar((0,-.24,.822));guitar.rotation_euler.x=-math.pi/2;guitar.scale=(.55,)*3
        for obj in guitar.children_recursive:
            if obj.type=='MESH':A.tag(obj,'hero' if any(word in obj.name for word in ['bout','string','fretboard']) else 'support','The supported instrument is the primary subject of the detail move')
        cam=camera_path('Supported guitar strings to body',[(0,(-.09,.03,1.52),(0,.13,.86)),(2.2,(.10,-.13,1.46),(0,-.04,.86)),(5.9,(.17,-.43,1.36),(0,-.22,.86))],6,34)
        return sequence(cam,6,actions=['The instrument remains supported on the table','A curved pitch-changing detail move follows strings toward the body; no unverified playing hands are drawn'])
    garment,label,tag=label_and_tag();A.fixed_side_light((0,0,.86))
    if gid=='hands_garment_high_hold':
        focus=(0,0,.84);cam=camera_path('Folded garment collar to attached tag',[(0,(-.12,-.43,1.24),(0,.09,.84)),(2.1,(.02,-.40,1.34),(0,.02,.84)),(4.9,(.15,-.36,1.31),(.15,-.045,.84))],5,32)
        return sequence(cam,5,actions=['Collar, folded sleeves and placket show the garment right way up','The tag remains physically attached; no hanger floats beneath the garment'])
    label_start=gid=='card_label_high_hold_whipout';focus=Vector((-.075,.075,.848) if label_start else (.19,-.06,.848))
    duration=8 if label_start else 5
    knots=[(0,focus+Vector((-.12,-.28,.32)),focus),(2.2,focus+Vector((.015,-.23,.40)),focus),(4,focus+Vector((.12,-.25,.35)),focus)]
    if label_start:knots.extend([(5.4,(.28,-.32,1.25),(.19,-.06,.848)),(7.9,(.36,-.30,1.20),(.19,-.06,.848))])
    else:knots[-1]=(4.9,focus+Vector((.13,-.25,.40)),focus)
    cam=camera_path('Maker label to price tag' if label_start else 'Attached tag curved detail move',knots,duration,35)
    return sequence(cam,duration,4 if label_start else None,actions=['Maker detail and price tag belong to the same recognisable folded garment',
        'A curved diagonal move changes distance and pitch while the text remains readable'],next_guide='card_tag_high_hold' if label_start else None,landing=4)


def build(scene,spec):
    if spec['id']=='rail_guitar_pov_truckr_mm':
        V.rack('guitar',(0,.55,.52));A.fixed_side_light((0,.55,1.15))
        for x in [-.75,0,.75]:
            A.tag(G.tube('Guitar wall neck support',[(x,.62,1.43),(x,.54,1.43),(x+.025,.51,1.43)],.006),'background','Each instrument has a real neck support on the display rail')
        cam=camera_path('Instrument wall customer-side curved truck',[
            (0,(-.80,-.70,1.43),(-.72,.55,1.14)),
            (2.0,(-.42,-.76,1.48),(-.36,.55,1.16)),
            (3.9,(.02,-.69,1.40),(.04,.55,1.13))],4,28)
        return sequence(cam,4,actions=['Detailed CC0 guitars remain supported on one customer-facing display',
            'A short curved rightward walk changes height and pitch while keeping bodies and headstocks together in frame'])
    return lunch(scene,spec) if spec['id']=='card_menu_high_in_cd_whipout' else resource(scene,spec)
