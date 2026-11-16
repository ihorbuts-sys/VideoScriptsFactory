"""A single supported takeaway order, reused for the handoff and overhead opening."""
import bpy
import math
from mathutils import Vector
import assets as A
import geometry as G
import food_assets as F
import real_hands as H
from motion_paths import camera_path
from drink_scenes import pose,smooth

REVIEW=dict(subject='One whole burger inside the same hinged takeaway box in both views',
    angle='Low public-side serving ledge, then a match cut to directly overhead',
    motion='A side-gripping hand carries the closed box down, sets it on a table, releases; one hand then opens the same lid',
    focal_point='Recognisable box corners through the cut, then the burger resting inside',
    composition='The serving ledge establishes origin, the visible receiving tabletop establishes support, and the single box anchors both shots',
    golden_ratio='Centred package and clear contact take precedence over an ornamental ratio',
    lighting='Steady broad side light; no glow, moving fixtures or opaque walls',
    contacts='Box base starts on the ledge and finishes on the table; the burger rests on the inner base and the lid stays hinged',
    handover='Same box, burger, table and scene; match cut to top-down opening, with no replacement pastry tray',
    mobile='Keep the phone still at the public window; record the second take overhead with one free hand opening the lid or a helper holding the phone')


def make_order():
    box,hinge=F.open_box((0,-.25,.785),pastries=False,height=.16)
    food,_=F.burger((0,0,.016));food.parent=box
    food['continuity_id']='takeaway-burger-01';box['continuity_id']='takeaway-box-01'
    for obj in box.children_recursive:
        if obj.type=='MESH' and not obj.name.startswith(('Burger','Thin cheese','Lettuce','Tomato')):
            A.tag(obj,'support','Same physical package and attached lid support the same order throughout')
    return box,hinge,food


def check_food_contact(scene,box,food):
    scene.frame_set(1);bpy.context.view_layer.update()
    base=next(o for o in box.children_recursive if o.name.startswith('Box base'))
    bun=next(o for o in food.children_recursive if o.name.startswith('Burger lower bun'))
    surface=max((base.matrix_world@v.co).z for v in base.data.vertices)
    bottom=min((bun.matrix_world@v.co).z for v in bun.data.vertices)
    assert abs(bottom-surface)<.0001,'The whole burger must rest inside the box'
    return dict(subject=bun.name,support=base.name,gap_m=bottom-surface)


def opening_hand(hinge,start):
    hand=H.place('pinch','R',target=(.19,0,.31),forward=(0,0,1),normal=(0,-1,0),anchor='grip');hand.parent=hinge
    # Parent to the lid hinge so the gripping fingers follow the actual lid edge.
    for t,a in [(0,90),(start,90),(start+1.5,0),(start+3.0,0)]:pose(hinge,t,rotation=(math.radians(a),0,0))
    return hand


def top_camera(start,duration):
    from build_scenes import camera,key_camera,frame
    focus=Vector((0,-.25,.86));cam=camera('Overhead same order',(0,-.25,1.65),focus,26)
    for f in range(1,frame(duration)):
        t=(f-1)/15;u=smooth((t-start-.6)/1.8)
        key_camera(cam,f,(0,-.25,1.65-.23*u),focus)
    return cam


def build(scene,spec,unwrap_only=False):
    from build_scenes import camera,frame
    A.table((0,-.25,0),radius=.55);box,hinge,food=make_order()
    contact=check_food_contact(scene,box,food)
    A.fixed_side_light((0,-.25,.9))
    if unwrap_only:
        opening_hand(hinge,.6);cam=top_camera(0,4)
        return dict(duration=4,take_end=4,cameras=[(0,cam)],scope='base_shot_with_action',handover_status='deferred_people',
                    intent='Open the supported takeaway box from above, revealing the whole burger resting on its base',
                    composition=[REVIEW['composition'],REVIEW['contacts']],subject_actions=['One hand opens the attached lid','The same whole burger remains supported inside'],
                    mobile_feasibility=REVIEW['mobile'],order_contact_checks=[contact],geometry_checks=dict(same_order=True,food_rests_on_box_base=True))
    A.tag(G.block('Public serving ledge',(0,.48,1.155),(1.35,.66,.05),.015),'structure','The package starts on this visible public ledge')
    for x in [-.65,.65]:A.tag(G.block('Serving window side',(x,.78,1.63),(.035,.035,.90),.004),'background','Only the public opening is drawn; no wall panel or restricted camera viewpoint')
    A.tag(G.block('Serving window top',(0,.78,2.08),(1.34,.035,.035),.004),'background','Window frame identifies the order pickup point')
    for t,p in [(0,(0,.33,1.18)),(.8,(0,.33,1.18)),(2.7,(0,-.25,.785)),(10.4,(0,-.25,.785))]:pose(box,t,location=p)
    carrier=H.place('pinch','R',target=(.25,0,.055),forward=(-.4,.9165,0),normal=(-.9165,-.4,0),anchor='grip');carrier.parent=box
    carrier_start=carrier.location.copy()
    for t,x in [(0,0),(2.9,0),(3.6,.65),(10.4,.65)]:pose(carrier,t,location=carrier_start+Vector((x,0,0)))
    # The opening hand belongs only to the overhead take, not the delivery view.
    hand=opening_hand(hinge,6.0);hand_start=hand.location.copy()
    for t,x in [(0,1.0),(4.2,1.0),(5.8,0),(10.4,0)]:pose(hand,t,location=hand_start+Vector((x,0,0)))
    for obj in [hand,*hand.children_recursive]:
        for f,hidden in [(1,True),(63,True),(64,False)]:
            obj.hide_render=hidden;obj.keyframe_insert(data_path='hide_render',frame=f)
    cam=camera_path('Continuous handoff to overhead opening',[(0,(0,-1.10,1.02),(0,.33,1.27)),(.8,(0,-1.10,1.02),(0,.33,1.27)),
        (2.7,(0,-1.10,1.02),(0,-.25,.89)),(4,(0,-1.10,1.04),(0,-.25,.89)),
        (5.2,(.13,-.62,1.46),(0,-.25,.88)),(6,(.08,-.35,1.66),(0,-.25,.86)),
        (8,(.02,-.35,1.52),(0,-.25,.86)),(10.3,(.05,-.33,1.42),(0,-.25,.86))],10.4,28)
    return dict(duration=10.4,take_end=4,cameras=[(0,cam)],scope='shot_and_handover',handover_status='included',
                shared_scene_handover=dict(next_guide='topdown_unwrap_top_in_cd',landing=6,method='one_camera_shared_scene'),
                probe_frames=[1,34,60,75,91,112,156],
                intent='Carry one burger box from its ledge to the table, then follow it with one smooth camera rise and open the same box overhead',
                composition=[REVIEW['composition'],REVIEW['contacts']],
                subject_actions=['One gripping hand carries and sets down the package before releasing it','The camera rises smoothly to the same box without a cut','One anatomical hand opens the hinged lid while food and box remain on their support'],
                continuity_objects={'package':'takeaway-box-01','food':'takeaway-burger-01'},
                order_contact_checks=[contact],
                mobile_feasibility=REVIEW['mobile'],source_adaptations=['Replace the unrelated pastry-tray insert and raised half-burger with a single coherent supported takeaway order'],
                geometry_checks=dict(same_order=True,food_rests_on_box_base=True,box_supported_before_release=True))
