"""One public-aisle camera connects the bar and its best table in shared space."""
import math
import bpy
from mathutils import Vector
import assets as A
import geometry as G
import venue_assets as V


REVIEW = dict(
    subject="Bar seating and bottle rhythm, then the best two-person table in the same room",
    angle="Counter-height view becomes a reachable high oblique table view",
    motion="0.6 m truck right, lift and turn through the public seating aisle, then a short table lean",
    focal_point="Bar counter edge leads into the room; the window-side table becomes the destination",
    composition="Counter and stools establish depth; repeated tables lead to a clearer two-person setting with negative space around it",
    golden_ratio="Use a readable progression of near bar, middle seating and far window; no imposed decorative spiral",
    lighting="Fixed window-side light and restrained attached rim cue; no moving fixtures or bloom",
    contacts="Glasses sit on the counter; opposed place settings and chairs share one dining table; camera remains in the aisle",
    handover="Continuous shared-room movement into table_seat_high_in_mc, including its short high-angle lean; no cut or scene relocation",
    mobile="One ordinary phone, 1.18–1.57 m high, under two metres of total travel, slow turn and small steps; keep the aisle clear",
)


def ease(t):
    t=max(0,min(1,t));return (1-math.cos(math.pi*t))/2


def build(scene,spec):
    from build_scenes import camera,key_camera,frame
    # All furniture shares one coordinate system. The bar front is y=0.05.
    A.tag(G.block('Bar counter front',(-.65,.54,.55),(3.0,.90,1.1),.018),
          'structure','A single coherent counter leads toward its right end')
    A.tag(G.block('Continuous bar top',(-.65,.53,1.105),(3.18,1.0,.07),.025),
          'hero','Near counter edge supplies the truck-right leading line')
    for x in [-1.85,-1.05,-.25,.55]:
        A.tag(G.block('Bar front panel stile',(x,.08,.59),(.025,.02,.78),.003),
              'background','Quiet joinery adds scale without a wall wash')
    A.tag(G.tube('Customer foot rail',[(-1.95,-.16,.24),(.70,-.16,.24)],.014),
          'background','Public side of the counter stays identifiable')
    for j,x in enumerate([-1.45,-.65,.15]):
        before=set(bpy.data.objects);G.stool('Bar seat '+str(j+1),x,-.39)
        for obj in set(bpy.data.objects)-before:
            A.tag(obj,'foreground_frame','Stools slide against distant bottles with genuine depth; no camera collision')
    for x in [-.85,.35]:
        A.tag(G.glass('Counter tumbler',x,.22,1.14,1.1),'support','Glass base rests exactly on the bar top')
    for z in [1.40,1.98]:
        A.tag(G.block('Backbar shelf',(-.65,1.22,z),(3.0,.25,.035),.007),
              'background','Repeated shelves remain quiet context without lighting strips')
        for j,x in enumerate([-1.90,-1.71,-1.52,-1.08,-.89,-.70,-.22,-.03,.16,.60]):
            A.tag(G.bottle('Backbar bottle',x,1.20,z+.018,.25+.035*(j%3),.035),
                  'important_background' if j in [3,4,5] else 'background',
                  'Grouped bottle silhouettes give rhythm and tower over the low counter view')
    # The destination sits to the right of the bar, across an open customer aisle.
    table=V.dining_table((1.48,-1.65,0))
    for obj in table.children_recursive:
        if obj.type=='MESH' and obj.name.startswith('Plate with formed rim'):
            A.tag(obj,'hero','Opposed dinner plates anchor the final high-angle composition')
        elif obj.type=='MESH' and ('Quiet tabletop' in obj.name or 'Dining chair' in obj.name):
            A.tag(obj,'support','The usable two-person table is the destination, not an isolated prop')
    for position in [(2.50,-.15,0),(3.20,-3.30,0)]:
        context=V.dining_table(position,settings=False)
        for obj in context.children_recursive:
            if obj.type=='MESH':A.tag(obj,'background','Fainter neighbouring seating establishes one continuous interior')
    window=V.window((2.55,-1.65,1.48));window.rotation_euler.z=math.pi/2
    A.fixed_side_light((1.48,-1.65,.85));A.fixed_side_light((-.65,.55,1.45),warm=False)
    A.rim_light_cue((1.48,-1.65,.787),.52,angle=0,span=35)
    # Sparse floor seams give orientation through the turn, without an opaque room shell.
    for y in [-2.6,-.95]:
        A.tag(G.tube('Quiet floor seam',[(-2.3,y,.004),(3.7,y,.004)],.0008),
              'background','Sparse floor perspective helps connect bar and table without filling the room')
    origin0=Vector((-.70,-.95,1.18));origin1=Vector((-.10,-.95,1.18))
    origin2=Vector((.48,-1.65,1.57));origin3=Vector((.68,-1.65,1.43))
    target0=Vector((-.70,.65,1.52));target1=Vector((-.10,.65,1.52))
    target2=Vector((1.48,-1.65,.81))
    cam=camera('Continuous bar to best table',origin0,target0,26)
    for f in range(1,frame(12)):
        t=(f-1)/15
        if t<4:
            u=ease((t-.8)/2.2);origin=origin0.lerp(origin1,u);target=target0.lerp(target1,u)
        elif t<8.0:
            u=ease((t-4)/4.0);origin=origin1.lerp(origin2,u)
            # Spherical direction interpolation makes an intentional interior pan,
            # rather than pointing through an interpolated target behind the lens.
            start=(target1-origin1).normalized();finish=(target2-origin2).normalized()
            direction=start.slerp(finish,u);target=origin+direction
        elif t<8.6:
            origin=origin2;target=target2
        else:
            u=ease((t-8.6)/1.8);origin=origin2.lerp(origin3,u);target=target2
        key_camera(cam,f,origin,target)
    return dict(duration=12,take_end=4,cameras=[(0,cam)],scope='shot_and_handover',handover_status='included',
                continuous_handover=dict(next_guide='table_seat_high_in_mc',transition_start=4,landing=8.0,
                                         table_lean_start=8.6,table_lean_end=10.4,method='one_camera_shared_interior'),
                probe_frames=[1,46,61,76,91,106,121,145,180],
                intent='Slide along the bar, turn through its connected seating area and settle into a high view of the best table',
                composition=[REVIEW['composition'],'Foreground stools, bottle groups and window remain physical landmarks through the turn',
                             'The destination table has two opposed usable settings and is never relocated between takes'],
                subject_actions=['0–4 s: low rightward bar truck','4–8 s: lift, turn and walk through the customer aisle',
                                 '8–12 s: settle, lean over the same table and hold'],
                mobile_feasibility=REVIEW['mobile'],
                source_adaptations=['Owner replaces the original hard cut with a connected interior walk and table landing'],
                geometry_checks=dict(single_camera=True,stationary_furniture=True,public_aisle=True,
                                     two_person_table=True,lens_fixed=True,no_cut=True))
