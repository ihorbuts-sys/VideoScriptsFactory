"""Build and render native 3D filming-guide scenes from the existing descriptions.

Use Blender --background --factory-startup --python build_scenes.py -- GUIDE_ID
Add --probes for a small framing/action review before the full export.
"""
import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
sys.path.insert(0,str(ROOT))
import geometry as G
import assets as A
import scene_plans
import bar_transition
import order_handoff
import cinematic_resources
import cinematic_locations
import cinematic_drinks
import cafe_first_visit

FPS=15
SCHEMATIC_ARM=__import__("re").compile(r"^(Carrying wrist|Tongs attached wrist|Attached forearm|Tearing forearm|Fork attached wrist|Topping hand wrist)(\.\d+)?$")
TAKE_ONLY=False
ROLE={
    "hero":(1,.25,1.9), "support":(.68,.175,1.5),
    "important_background":(.78,.20,1.6), "foreground_frame":(.48,.125,1.5),
    "background":(.25,.0625,1.1), "structure":(.40,.10,1.3),
    "lighting_cue":(.65,0,1.3),
}


def smooth(t):
    t=max(0,min(1,t));return .5-.5*math.cos(math.pi*t)


def frame(t): return round(t*FPS)+1


def initialize(gid):
    bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.name="01 Ghost contours"
    scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=1
    scene.cycles.use_denoising=False;scene.render.threads_mode="FIXED";scene.render.threads=4
    scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.render.fps=FPS;scene.render.film_transparent=True;scene.render.use_sequencer=False
    scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA"
    scene.view_settings.view_transform="Standard";scene.view_settings.look="None"
    mat=bpy.data.materials.new("Neutral geometry; visible contours only")
    mat.use_nodes=True;mat.diffuse_color=(.60,.72,.78,1)
    nodes=mat.node_tree.nodes;nodes.clear();output=nodes.new("ShaderNodeOutputMaterial")
    shader=nodes.new("ShaderNodeBsdfPrincipled");shader.inputs["Base Color"].default_value=(.65,.72,.76,1)
    shader.inputs["Roughness"].default_value=.42
    mat.node_tree.links.new(shader.outputs[0],output.inputs[0]);G.MAT=mat
    world=bpy.data.worlds.new("Quiet ambient fill");world.use_nodes=True
    world.node_tree.nodes["Background"].inputs[0].default_value=(.72,.82,1,1)
    world.node_tree.nodes["Background"].inputs[1].default_value=.18;scene.world=world
    source=BASE/"guides/templates"/(gid+".json")
    data=json.loads(source.read_text())
    templates=json.loads((BASE/"guides/script_templates.json").read_text())["templates"]
    contexts=[]
    for template in templates:
        for index,step in enumerate(template["steps"]):
            if gid in step.get("overlays",[]):
                contexts.append(dict(script=template["id"],step=step,
                                     next_step=template["steps"][index+1] if index+1<len(template["steps"]) else None))
    return scene,dict(id=gid,description=data["description"],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      build_fingerprint=hashlib.sha256(b"".join((ROOT/name).read_bytes() for name in ["build_scenes.py","assets.py","geometry.py","scene_plans.py","drink_scenes.py","venue_assets.py","environment_scenes.py","food_assets.py","food_scenes.py","shot_motion.py","people_scenes.py","bar_transition.py","order_handoff.py","cinematic_resources.py","cinematic_locations.py","cinematic_drinks.py","cafe_first_visit.py","entrance_inside.py","motion_paths.py","real_hands.py","massage_scene.py","vendor/para-fps-arms/massage-hand.blend","table_composition.py","audit_place_settings.py","vendor/para-fps-arms/hand-poses.blend"])+source.read_bytes()).hexdigest(),
                      source_live=data.get("live"),contexts=contexts,
                      style="25% main fills, fainter context, slate-blue contours, no walls",status="render_pending")


def point_camera(camera,position,target):
    camera.location=position;camera.rotation_euler=(Vector(target)-Vector(position)).to_track_quat("-Z","Y").to_euler()


def key_camera(camera,number,position,target):
    point_camera(camera,position,target)
    camera.keyframe_insert(data_path="location",frame=number)
    camera.keyframe_insert(data_path="rotation_euler",frame=number)


def camera(name,position,target,lens=36):
    return G.camera(name,position,Vector(target)-Vector(position),lens)


def portrait_handover(start,end,prop="cup",high=False):
    policy=ROOT/"people-policy.json"
    if TAKE_ONLY or policy.exists():return None,None
    actor=A.portrait(prop=prop)
    centre=(8,-.78,1.64 if high else 1.48)
    target=(8,0,1.45)
    cam=camera("Next shot - creator",centre,target,33)
    for f in range(frame(start),frame(end)):
        u=smooth((f/FPS-start-.15)/max(.1,end-start-.4))
        if prop:A.pose_portrait(actor,f,u)
    return cam,actor


def steam(cup_position,end):
    before=set(bpy.data.objects)
    objects=[]
    for index in range(2):
        points=[(cup_position[0]+(index-.5)*.025+.009*math.sin(j*.85+index),cup_position[1],
                 cup_position[2]+.12+j*.013) for j in range(10)]
        obj=G.tube("Steam curl",points,.0008)
        A.tag(obj,"background","Quiet rising steam is the subject action; the camera stays still")
        obj.shape_key_add(name="Basis");wind=obj.shape_key_add(name="Rising curl")
        for vertex in wind.data:
            vertex.co.x+=.010*math.sin((vertex.co.z-cup_position[2])*45+index)
            vertex.co.z+=.012
        for f in range(1,frame(end),3):
            wind.value=.5+.5*math.sin(f/FPS*3+index)
            wind.keyframe_insert(data_path="value",frame=f)
        objects.append(obj)
    return objects


def cup_orbit(scene,spec):
    A.table();A.saucer();subject=A.cup();focus=Vector((0,0,.854))
    A.fixed_side_light(focus);A.rim_light_cue((0,0,.914),.0533)
    cam=camera("Cup orbit right",(-.16,-.277,.855),focus,44)
    for f in range(1,frame(4)):
        t=(f-1)/FPS;angle=math.radians(-30+60*smooth((t-1.2)/1.8))
        key_camera(cam,f,(.32*math.sin(angle),-.32*math.cos(angle),.854),focus)
    nxt,actor=portrait_handover(4,6,"cup")
    return dict(duration=6,take_end=4,cameras=[(0,cam),(4,nxt)],
                intent="Show the actual changing cup side and handle, then the first sip",
                geometry_checks=dict(orbit_arc_deg=60,orbit_direction="right",radius_m=.32,stationary_subject=True),
                composition=["Centred product keeps scale stable during orbit","Open handle supplies a viewpoint landmark","Saucer and quiet support stay subordinate"],
                subject=subject)


def cup_whip(scene,spec):
    A.table(radius=.70);A.saucer();A.cup();steam((0,0,.797),4.1)
    A.plate((.32,.03,.785));pastry,halves=A.pastry((.32,.03,.794))
    for j,half in enumerate(halves):
        side=1 if j==0 else -1
        for t,dx in [(0,0),(5,0),(6,side*.042)]:
            half.location.x=dx;half.keyframe_insert(data_path="location",frame=frame(t))
        hand=A.hand((side*.115,.055,.025),scale=.65,mirror=side)
        hand.parent=half
    cam=camera("Cup hold then right whip",(0,-.32,.855),(0,0,.855),44)
    for f in range(1,frame(4.34)):
        t=(f-1)/FPS;angle=math.radians(70*smooth((t-4.10)/.24))
        key_camera(cam,f,(0,-.32,.855),(.5*math.sin(angle),-.32+.5*math.cos(angle),.855))
    nxt=camera("Whip landing - high pastry",(.32,-.30,1.16),(.32,.06,.825),37)
    return dict(duration=6,take_end=4.34,cameras=[(0,cam),(4.34,nxt)],
                intent="Hold the cup while steam moves; whip right and land on the pastry as its halves start opening",
                transition="Whip-assisted cut joins eye-level and high-angle takes; no impossible continuous camera rise",
                composition=["Steam supplies motion during a fixed camera hold","Pastry belongs to the same public tabletop","Two hands stay attached to the same pastry halves"],
                geometry_checks=dict(camera_fixed_until_s=4.1,whip_direction="right",visible_hands_at_landing=2))


def plate_orbit(scene,spec):
    A.table();subject=A.pasta();utensil=A.fork((.18,-.02,.789))
    A.fixed_side_light((0,0,.83));A.rim_light_cue((0,0,.816),.149)
    focus=Vector((0,0,.825));radius=.38;vertical=.38
    cam=camera("High plate orbit left",(.19,-.329,1.205),focus,38)
    for f in range(1,frame(5)):
        t=(f-1)/FPS;angle=math.radians(30-60*smooth((t-1.2)/2.4))
        key_camera(cam,f,(radius*math.sin(angle),-radius*math.cos(angle),focus.z+vertical),focus)
    if not TAKE_ONLY:
        for t,z in [(0,.789),(4.5,.789),(4.97,.90)]:
            utensil.location.z=z;utensil.keyframe_insert(data_path="location",frame=frame(t))
    nxt,actor=portrait_handover(5,6.8,"fork")
    return dict(duration=6.8,take_end=5,cameras=[(0,cam),(5,nxt)],
                intent="Reveal the far side of the pasta plate from a real high orbit, then hand over to the first bite",
                transition="Cut on the lifting fork into the next creator shot; match anchor requires visual review",
                composition=["The plate stays centred while genuine perspective changes","Compact noodle mound reveals depth without filling the frame with detail","The fork motivates the transition"],
                geometry_checks=dict(orbit_arc_deg=60,orbit_direction="left",elevation_deg=45,stationary_subject=True),subject=subject)


def menu_tilt(scene,spec):
    A.table((0,.25,.315),radius=.70)
    A.menu_board((0,.72,1.92));A.saucer((0,-.04,1.10));A.cup((0,-.04,1.110),name="Seasonal drink")
    A.fixed_side_light((0,.40,1.65),warm=False)
    origin=Vector((0,-.50,1.36));cam=camera("Tilt board to drink",origin,(0,.72,1.92),36)
    for f in range(1,frame(4)):
        t=(f-1)/FPS;pitch=math.radians(25-48*smooth((t-1.2)/1.8))
        key_camera(cam,f,origin,origin+Vector((0,math.cos(pitch),math.sin(pitch))))
    nxt,actor=portrait_handover(4,5.8,"cup",high=True)
    return dict(duration=5.8,take_end=4,cameras=[(0,cam),(4,nxt)],
                intent="Connect the menu's name/price line to the actual drink below, then show the verdict framing",
                composition=["Menu and drink share a clear vertical action path","No wall is needed to explain the tilt","The price field is marked without fabricating a venue price"],
                source_conflict="Original live scenario repeats the low starting tilt in its final hold; new camera correctly finishes looking down at the drink",
                geometry_checks=dict(camera_position_fixed=True,tilt_start_up_deg=25,tilt_end_down_deg=23))


def menu_whip(scene,spec):
    A.table(radius=.78)
    menu=A.menu_board((-.22,0,.800),flat=True);menu.scale=(.55,)*3
    tray=A.empty("Lunch tray",(.39,.02,.785))
    before=set(bpy.data.objects)
    G.block("Tray base",(0,0,.008),(.44,.30,.016),.012)
    for x in [-.22,.22]:G.block("Tray side rim",(x,0,.020),(.012,.30,.025),.004)
    for y in [-.15,.15]:G.block("Tray end rim",(0,y,.020),(.44,.012,.025),.004)
    for obj in set(bpy.data.objects)-before:
        obj.parent=tray;A.tag(obj,"structure","Tray groups the meal components into one clear lunch offer")
    meal=A.pasta((.31,.02,.817));meal.scale=(.66,)*3
    drink=A.cup((.52,.03,.809),name="Lunch drink",role="support");drink.scale=(.75,)*3
    for t,z in [(0,.817),(4.34,.87),(4.9,.817),(5.8,.817)]:
        meal.location.z=z;meal.keyframe_insert(data_path="location",frame=frame(t))
    focus=Vector((-.22+.105,.03,.800));cam=camera("Menu price push then whip",focus+Vector((0,-.38,.38)),focus,30)
    for f in range(1,frame(4.0)):
        t=(f-1)/FPS;distance=1-(1-1/1.908)*smooth((t-1.2)/1.8)
        origin=focus+Vector((0,-.38,.38))*distance
        angle=math.radians(70*smooth((t-3.7)/.30))
        direction=Vector((math.sin(angle),math.cos(angle),-1)).normalized()
        key_camera(cam,f,origin,origin+direction)
    nxt=camera("Whip landing - overhead lunch",(.39,.02,1.48),(.39,.02,.80),31)
    return dict(duration=5.8,take_end=4.0,cameras=[(0,cam),(4.0,nxt)],
                intent="Push into the menu price field, whip right and land overhead on the included lunch items",
                transition="Whip-assisted cut changes from high menu framing to a true overhead tray",
                composition=["Price field gets the initial attention","Tray unifies the included items","Dish and drink have clear, non-overlapping places"],
                geometry_checks=dict(push_scale_factor=1.908,whip_direction="right",landing_top_down=True))


def spread_pull(scene,spec):
    A.table(radius=.64);A.pasta((0,-.12,.785))
    A.plate((-.43,.18,.785));A.cup((.43,.12,.795),name="Brunch cup",role="support")
    A.saucer((.43,.12,.785));A.pastry((-.43,.18,.794))
    A.fixed_side_light((0,-.12,.83));A.rim_light_cue((0,-.12,.816),.149)
    focus=Vector((0,-.12,.825));cam=camera("Overhead plate to spread",focus+Vector((0,0,.40)),focus,24)
    for f in range(1,frame(5)):
        t=(f-1)/FPS;height=.40+(1.10-.40)*smooth((t-1.2)/2.4)
        key_camera(cam,f,focus+Vector((0,0,height)),focus)
    nxt,actor=portrait_handover(5,6.6,None)
    return dict(duration=6.6,take_end=5,cameras=[(0,cam),(5,nxt)],
                intent="Lift straight above the hero plate to reveal the complete brunch arrangement, then cut to its introduction",
                composition=["Hero dish begins alone","Supporting dish and cup balance a three-part spread","Quiet gaps preserve each silhouette"],
                geometry_checks=dict(orientation_top_down=True,vertical_pull_m=.70))


def menu_truck(scene,spec,left=False,low=False):
    review=spec["pre_render_review"]
    A.menu_board((0,.35,1.70),title=review["resource_title"],selected=review["resource_selected"])
    A.fixed_side_light((0,.35,1.70),warm=False)
    elevation=1.30 if low else 1.70
    direction=Vector((0,1,.33 if low else 0))
    start_x=.22 if left else -.22;end_x=-start_x
    cam=camera("Menu lateral move",(start_x,-.85,elevation),Vector((start_x,-.85,elevation))+direction,35)
    for f in range(1,frame(4)):
        t=(f-1)/FPS;x=start_x+(end_x-start_x)*smooth((t-1.2)/1.8)
        origin=Vector((x,-.85,elevation));key_camera(cam,f,origin,origin+direction)
    return dict(duration=4,take_end=4,cameras=[(0,cam)],
                intent="Move laterally across the menu with a fixed lens and orientation",
                composition=["Selected name/price line is the priority","Quiet menu rows make the lateral shift readable","Support is faint and walls are absent"],
                geometry_checks=dict(truck_direction="left" if left else "right",travel_m=.44,camera_orientation_fixed=True),
                handover_status="pending_contextual_sequence")


def menu_push(scene,spec,outward=False):
    review=spec["pre_render_review"]
    board_height=1.50 if outward else 1.70
    A.menu_board((0,.35,board_height),title=review["resource_title"],selected=review["resource_selected"])
    A.fixed_side_light((0,.35,board_height),warm=False)
    if outward:
        A.studio_sign((-.43,.35,1.73))
        obj=G.block("Public studio desk",(0,.42,1.10),(1.18,.50,.04),.012)
        A.tag(obj,"structure","The desk appears around the price board as the camera pulls back, exactly as the source describes")
    focus=Vector((-.02,.35,board_height+.055));cam=camera("Price-list pull" if outward else "Price-list push",(-.02,-.85,board_height+.055),focus,38)
    for f in range(1,frame(4)):
        t=(f-1)/FPS;u=smooth((t-1.2)/1.8)
        distance=(.52+.76*u) if outward else (1.20-.64*u)
        key_camera(cam,f,focus+Vector((0,-distance,0)),focus)
    return dict(duration=4,take_end=4,cameras=[(0,cam)],
                intent="Start on a price detail and reveal its desk context" if outward else "Move from the price-list context to the selected line",
                composition=["The selected resource line is stable in the frame","The camera changes distance, not lens","Relevant supporting context stays lighter"],
                geometry_checks=dict(direction="pull-out" if outward else "push-in",lens_fixed=True),
                handover_status="pending_contextual_sequence")



def lunch_plate_push(scene,spec):
    A.table();subject=A.pasta((0,-.36,.785));A.fork((.18,-.36,.789))
    focus=Vector((0,-.36,.845));A.fixed_side_light(focus);A.rim_light_cue((0,-.36,.816),.149)
    direction=Vector((0,math.cos(math.radians(12)),math.sin(math.radians(12))))
    cam=camera("Low lunch plate push",focus-direction*.30,focus,22)
    for f in range(1,frame(4)):
        u=smooth(((f-1)/FPS-1.2)/1.8);distance=.30*(1-(1-1/1.357)*u)
        key_camera(cam,f,focus-direction*distance,focus)
    return dict(duration=4,take_end=4,cameras=[(0,cam)],subject=subject,
                intent="Move slowly from the table edge toward the lunch plate",
                geometry_checks=dict(direction="push-in",scale_factor=1.357,pitch_up_deg=12,stationary_subject=True),
                composition=["Near-edge food placement makes the low view accessible","Compact food silhouette above the formed plate rim","Subordinate fork does not cross the food"])


def resource_move(scene,spec):
    review=spec["pre_render_review"];gid=spec["id"]
    outward="_out_" in gid
    A.menu_board((0,.35,1.70),title=review["resource_title"],selected=review["resource_selected"],
                 right=review["resource_right"],rows=review["resource_rows"],tall=outward)
    A.fixed_side_light((0,.35,1.70),warm=False)
    source_move=next(s for s in spec["source_live"]["steps"] if s.get("action") in ["dolly_in","dolly_out"])
    amount=source_move["amount"];outward=source_move["action"]=="dolly_out"
    pitch=0 if "_eye_" in gid else 12
    direction=Vector((0,math.cos(math.radians(pitch)),math.sin(math.radians(pitch))))
    focus=Vector((.02 if outward else -.02,.35,1.755))
    start=.66 if outward else .82
    finish=start/amount
    cam=camera("Resource pull" if outward else "Resource push",focus-direction*start,focus,38)
    for f in range(1,frame(4)):
        u=smooth(((f-1)/FPS-1.2)/1.8);distance=start+(finish-start)*u
        key_camera(cam,f,focus-direction*distance,focus)
    return dict(duration=4,take_end=4,cameras=[(0,cam)],
                intent=review["motion"],geometry_checks=dict(direction="pull-out" if outward else "push-in",source_scale_factor=amount,pitch_up_deg=pitch,lens_fixed=True),
                composition=[review["composition"],"Resource labels are placeholders, not invented prices or times"])


FACTORIES={"cup_eye_orbitr_cc":cup_orbit,"cup_eye_hold_whipout":cup_whip,
           "plate_high_orbitl_cc":plate_orbit,"menu_board_low_tiltd_mm":menu_tilt,
           "card_menu_high_in_cd_whipout":menu_whip,"plate_spread_top_out_cw":spread_pull}
FACTORIES['bar_low_truckr_mm']=bar_transition.build
FACTORIES.update(menu_board_eye_truckr_mm=lambda s,p:menu_truck(s,p),
                 menu_board_low_truckl_mm=lambda s,p:menu_truck(s,p,left=True,low=True),
                 menu_pricelist_eye_in_mc=lambda s,p:menu_push(s,p),
                 menu_pricelist_eye_out_dm=lambda s,p:menu_push(s,p,outward=True))

FACTORIES.update(plate_low_in_mc=lunch_plate_push)
for _gid in ['menu_schedule_eye_in_mc', 'menu_event_low_in_cd', 'menu_hours_low_out_dc', 'menu_score_low_out_dc']:
    FACTORIES[_gid]=resource_move


import drink_scenes
drink_scenes.register(FACTORIES)
import environment_scenes
environment_scenes.register(FACTORIES)
import food_scenes
food_scenes.register(FACTORIES)
import people_scenes
people_scenes.register(FACTORIES)
FACTORIES['bag_handoff_low_hold']=order_handoff.build
FACTORIES['topdown_unwrap_top_in_cd']=lambda scene,spec:order_handoff.build(scene,spec,unwrap_only=True)
for _gid in cinematic_resources.IDS:FACTORIES[_gid]=cinematic_resources.build
for _gid in cinematic_locations.IDS:FACTORIES[_gid]=cinematic_locations.build
for _gid in cinematic_drinks.IDS:FACTORIES[_gid]=cinematic_drinks.build
for _gid in cafe_first_visit.IDS:FACTORIES[_gid]=cafe_first_visit.build
import entrance_inside
for _gid in entrance_inside.IDS:FACTORIES[_gid]=entrance_inside.build

def configure_style(scene):
    collections={}
    for role in ROLE:
        collection=bpy.data.collections.new("Role - "+role);scene.collection.children.link(collection);collections[role]=collection
    objects=[]
    for obj in list(bpy.data.objects):
        if obj.type!="MESH":continue
        role=obj.get("composition_role","support")
        if "composition_role" not in obj:A.tag(obj,role,"Relevant supporting geometry")
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        collections[role].objects.link(obj)
        objects.append(dict(name=obj.name,role=role,reason=obj["placement_reason"]))
    scene.render.use_freestyle=True;settings=scene.view_layers[0].freestyle_settings
    settings.as_render_pass=True;settings.crease_angle=math.radians(100);settings.use_smoothness=True
    for lines in list(settings.linesets):settings.linesets.remove(lines)
    for role,(alpha,fill,width) in ROLE.items():
        if not collections[role].objects:continue
        lines=settings.linesets.new(role);lines.select_by_collection=True;lines.collection=collections[role]
        lines.collection_negation="INCLUSIVE";lines.select_by_visibility=True;lines.visibility="VISIBLE"
        lines.select_silhouette=True;lines.select_border=True;lines.select_crease=True
        lines.linestyle.color=(.78,.48,.08) if role=="lighting_cue" else (.12,.24,.34)
        lines.linestyle.alpha=alpha;lines.linestyle.thickness=width;lines.linestyle.caps="ROUND"
    tree=bpy.data.node_groups.new("Transparent visible contour output","CompositorNodeTree")
    scene.compositing_node_group=tree;tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
    layers=tree.nodes.new("CompositorNodeRLayers");layers.scene=scene
    output=tree.nodes.new("NodeGroupOutput");tree.links.new(layers.outputs["Freestyle"],output.inputs["Image"])
    return objects


def create_fill(scene):
    fill=scene.copy();fill.name="02 Flat fill masks";fill.use_fake_user=True
    fill.render.engine="BLENDER_EEVEE";fill.eevee.taa_render_samples=16
    fill.render.use_freestyle=False;fill.render.use_compositing=False;fill.render.use_sequencer=False
    mat=bpy.data.materials.new("Role fill opacity mask");mat.use_nodes=True
    mat.node_tree.nodes.clear();info=mat.node_tree.nodes.new("ShaderNodeObjectInfo")
    shader=mat.node_tree.nodes.new("ShaderNodeEmission");output=mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(info.outputs["Color"],shader.inputs["Color"]);mat.node_tree.links.new(shader.outputs[0],output.inputs[0])
    fill.view_layers[0].material_override=mat
    for obj in bpy.data.objects:
        if obj.type=="MESH":
            value=ROLE[obj.get("composition_role","support")][1]*2
            linear=value/12.92 if value<=.04045 else ((value+.055)/1.055)**2.4
            obj.color=(linear,linear,linear,1)
    return fill


def selected_camera(sequence,t):
    return [camera for start,camera in sequence["cameras"] if round(start*FPS)<=round(t*FPS)][-1]


def check_contacts(scene):
    bpy.context.view_layer.update();checks=[]
    saucers=[o for o in scene.objects if o.type=="MESH" and o.name.startswith("Saucer")]
    for body in [o for o in scene.objects if o.type=="MESH" and "hollow ceramic body" in o.name]:
        centre=body.matrix_world.translation
        for saucer in saucers:
            if (centre.xy-saucer.matrix_world.translation.xy).length<.001:
                surface=max((saucer.matrix_world@v.co).z for v in saucer.data.vertices if v.co.xy.length<1e-6)
                base=min((body.matrix_world@v.co).z for v in body.data.vertices)
                assert abs(base-surface)<.0002,"Cup must touch its saucer"
                checks.append(dict(subject=body.name,support=saucer.name,gap_m=base-surface))
    for light in [o for o in scene.objects if o.type=="LIGHT"]:
        assert light.animation_data is None,"Ordinary shot lighting must stay fixed"
    return checks


def run(gid,probes=False,build_only=False,take_only=False):
    global TAKE_ONLY
    TAKE_ONLY=take_only
    policy_path=ROOT/"people-policy.json"
    if policy_path.exists() and gid in json.loads(policy_path.read_text())["deferred_guides"]:
        raise ValueError("People generation is deferred by the user: "+gid)
    out=BASE/"catalog/blender-animations"/gid;out.mkdir(parents=True,exist_ok=True)
    scene,spec=initialize(gid)
    spec["pre_render_review"]=scene_plans.review(gid,spec["description"],spec["contexts"])
    (out/"pre-render-review.json").write_text(json.dumps(spec["pre_render_review"],indent=2)+"\n")
    sequence=FACTORIES[gid](scene,spec)
    # Anatomical hands carry their own forearm; the separate tubes drawn for the old schematic hands would double it.
    for obj in [o for o in scene.objects if o.type=="MESH" and SCHEMATIC_ARM.match(o.name)]:
        bpy.data.objects.remove(obj,do_unlink=True)
    if policy_path.exists():
        if any(obj.type=="MESH" and obj.name.startswith("Mouthless schematic head") for obj in scene.objects):
            raise ValueError("Scene contains a person; generation deferred by the user")
        if any(cam is None for _,cam in sequence["cameras"]):
            sequence["duration"]=sequence["take_end"]
            sequence["cameras"]=[(t,cam) for t,cam in sequence["cameras"] if cam is not None and t<sequence["take_end"]]
            sequence.update(scope="base_shot_with_action",handover_status="deferred_people")
    import table_composition
    spec["table_composition_review"]=table_composition.enforce(scene)
    scene.frame_set(1);bpy.context.view_layer.update()
    spec["physical_contact_checks"]=check_contacts(scene)
    if take_only:
        sequence["full_instruction_intent"]=sequence["intent"]
        sequence["intent"]=spec["pre_render_review"]["subject"]+". "+spec["pre_render_review"]["motion"]+"."
        sequence["duration"]=sequence["take_end"]
        sequence["cameras"]=[(t,c) for t,c in sequence["cameras"] if c is not None and t<sequence["take_end"]]
        sequence["handover_status"]="pending_contextual_sequence"
        sequence["scope"]="Reusable base shot; contextual handover will be assembled separately"
    scene.frame_start=1;scene.frame_end=round(sequence["duration"]*FPS)
    objects=configure_style(scene);fill=create_fill(scene)
    spec.update({k:v for k,v in sequence.items() if k not in ["cameras","subject"]})
    spec.update(frame_count=scene.frame_end,fps=FPS,objects=objects,
                camera_stages=[dict(t=t,name=c.name) for t,c in sequence["cameras"]],
                hand_limit=2,mouths_drawn=False,visitor_viewpoint=True,
                fill_alpha_by_role={k:v[1] for k,v in ROLE.items()})
    spec["lighting"]=dict(fixed=True,sources=[obj.name for obj in scene.objects if obj.type=="LIGHT"],
                           ghost_cues=[obj.name for obj in scene.objects if obj.get("composition_role")=="lighting_cue"],
                           bloom=False,walls_visible=False)
    camera_samples=[]
    for f in range(1,scene.frame_end+1):
        scene.frame_set(f);bpy.context.view_layer.update();cam=selected_camera(sequence,(f-1)/FPS)
        camera_samples.append(dict(frame=f,camera=cam.name,position=list(cam.matrix_world.translation),rotation=list(cam.matrix_world.to_euler())))
    spec["camera_samples"]=camera_samples
    scene.frame_set(1);scene.camera=sequence["cameras"][0][1];fill.camera=scene.camera
    for start,cam in sequence["cameras"]:
        marker=scene.timeline_markers.new(cam.name,frame=frame(start));marker.camera=cam
    fill.timeline_markers.clear();bpy.context.window.scene=scene
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_perspective="CAMERA"
                area.spaces.active.shading.type="SOLID";area.spaces.active.shading.color_type="MATERIAL"
                area.spaces.active.overlay.show_floor=False
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"scene.blend"))
    (out/"scene-spec.json").write_text(json.dumps(spec,indent=2)+"\n")
    if build_only:return
    indices=sorted(set(min(scene.frame_end,f) for f in [1,frame(1.2),frame(min(2.4,sequence["take_end"]-.2)),frame(sequence["take_end"]-.08),frame(sequence["take_end"]+.25),frame(sequence["take_end"]+1.2),scene.frame_end])) if probes else range(1,scene.frame_end+1)
    if probes and sequence.get('probe_frames'):indices=sequence['probe_frames']
    for current,folder in [(scene,"contours"),(fill,"fills")]:
        destination=out/("probes-"+folder if probes else folder);destination.mkdir(exist_ok=True)
        for old in destination.glob("frame_*.png"):old.unlink()
        bpy.context.window.scene=current
        if current==fill:current.timeline_markers.clear()
        rendered={}
        for index in indices:
            current.frame_set(index);current.camera=selected_camera(sequence,(index-1)/FPS)
            bpy.context.view_layer.update()
            current.render.filepath=str(destination/("frame_%04d.png"%index))
            signature=tuple(round(v,7) for row in current.camera.matrix_world for v in row)
            for obj in sorted((o for o in current.objects if o.type=="MESH"),key=lambda o:o.name):
                signature+=tuple(round(v,7) for row in obj.matrix_world for v in row)
                if obj.data.shape_keys:signature+=tuple(round(k.value,6) for k in obj.data.shape_keys.key_blocks)
            if signature in rendered:
                shutil.copy2(rendered[signature],current.render.filepath)
            else:
                bpy.ops.render.render(write_still=True,scene=current.name)
                rendered[signature]=current.render.filepath
            print("GUIDE_PROGRESS",gid,folder,index,scene.frame_end,flush=True)
    spec["status"]="probes_rendered" if probes else "frames_rendered"
    (out/"scene-spec.json").write_text(json.dumps(spec,indent=2)+"\n")


if __name__=="__main__":
    args=sys.argv[sys.argv.index("--")+1:]
    run(args[0],"--probes" in args,"--build-only" in args,"--take-only" in args)
