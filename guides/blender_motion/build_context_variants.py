"""Render only the reusable contextual object variants required by actual script steps."""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parents[1]
sys.path.insert(0,str(ROOT))
import build_scenes as B
import people_scenes as P
import assets as A
import geometry as G
import food_assets as F
import venue_assets as V
import shot_motion as M
from drink_scenes import pose,glass,counter,smooth,frame
OUT=BASE/'catalog/context-variants';OUT.mkdir(exist_ok=True)
recipes=json.loads((BASE/'catalog/context-animations/context-recipes.json').read_text())
args=sys.argv[sys.argv.index('--')+1:];probes='--probes' in args
selected=[s for s in args if not s.startswith('--')]
groups={}
for key,row in recipes.items():groups.setdefault((row['guide_id'],row['recipe']),[]).append(key)
original_initialize=B.initialize
active_keys=[];active_recipe=''


def initialize(gid):
    scene,spec=original_initialize(gid)
    spec['contexts']=[c for c in spec['contexts'] if c['script']+'.'+c['step']['id'] in active_keys]
    assert spec['contexts'],(gid,active_keys)
    spec['context_recipe']=active_recipe;spec['context_step_keys']=active_keys
    spec['build_fingerprint']=hashlib.sha256((spec['build_fingerprint']+active_recipe+Path(__file__).read_text()).encode()).hexdigest()
    scene.render.threads=2
    return scene,spec
B.initialize=initialize


def resource_portrait(scene,spec,recipe):
    result=P.build(scene,spec);actor=next(o for o in scene.objects if o.name.startswith('Reusable creator bust'))
    if recipe=='portrait_group':
        actor.location.x=-.22
        for x in [0,.22]:other=A.portrait((x,0,0),None);P.eyes(other);P.hair(other)
        result=M.apply(scene,spec,(0,0,1.646-.267),span=1,down=22)
    else:
        grip=A.empty('Context resource grip',(.16,-.17,1.24));grip.parent=actor
        hand=A.hand(scale=.85);hand.parent=grip
        arm=A.tag(G.tube('Resource-holding arm',[(.19,0,1.35),(.24,-.08,1.13),(.16,-.17,1.24)],.026),'support','One connected arm holds the actual script resource');arm.parent=actor
        if recipe=='portrait_cup':resource=A.cup((-.06,-.03,-.008));resource.scale=(.75,)*3
        elif recipe=='portrait_glass':resource,liquid=glass((-.055,-.025,-.035))
        elif recipe=='portrait_plate':resource=A.pasta((-.06,-.03,-.015));resource.scale=(.65,)*3
        elif recipe=='portrait_pastry':resource,halves=A.pastry((-.055,-.025,-.01));resource.scale=(.75,)*3
        elif recipe=='portrait_tool':resource=F.tool('brush',(-.02,-.02,.02))
        elif recipe=='portrait_find':resource=V.garment((-.05,-.03,-.15),'hero');resource.scale=(.25,)*3
        elif recipe=='portrait_bag':
            resource=A.tag(G.block('Held order bag',(-.05,-.02,-.10),(.18,.08,.22),.012),'hero','One hand supports the actual bag handle')
            for x in [-.10,0]:
                handle=A.tag(G.tube('Held bag handle',[(x,-.02,.01),(x,-.02,.06),(x+.04,-.02,.06),(x+.04,-.02,.01)],.003),'support','Handle is attached to the same bag and grip');handle.parent=grip
        else:raise AssertionError(recipe)
        resource.parent=grip
    result.update(subject_actions=['The actual script resource appears beside the correctly framed face','One connected hand/arm supports it; the phone remains at practical arm length'],composition=['Clear eye line and resource separation','No unrelated default resource substituted'],intent='Creator framing with the actual script resource')
    return result


def held_replacement(scene,spec,recipe):
    result=P.build(scene,spec)
    grip=next(o for o in scene.objects if o.name.startswith('Resource grip'))
    actor_root=next(o for o in scene.objects if o.name.startswith('Reusable creator bust'))
    for root in list(grip.children):
        if root.get('visible_hand_count')==1:continue
        for obj in list(root.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.objects.remove(root,do_unlink=True)
    if recipe=='sip_glass':resource,liquid=glass((-.06,-.025,-.008))
    else:resource,parts=F.burger((-.055,-.025,-.01));resource.scale=(.65,)*3
    resource.parent=grip
    actor=dict(root=actor_root,grip=grip,arm=[next(o for o in actor_root.children_recursive if o.name.startswith('Upper arm')),next(o for o in actor_root.children_recursive if o.name.startswith('Forearm'))])
    for f in range(1,round(result['duration']*15)+1):
        t=(f-1)/15;u=smooth((t-1.2)/2)
        wrist=(.16,-.20+.13*u,1.15+.18*u) if recipe=='sip_glass' else (.16,-.20+.13*u,1.22+.24*u)
        A.pose_portrait(actor,f,u,wrist)
    result.update(subject_actions=['The correct glass or handheld burger replaces the generic cup/fork','Grip, wrist and connected arm follow the same resource into the sip/bite framing'],intent='Present and approach the actual ordered resource')
    return result


def work_variant(scene,spec,recipe):
    counter();focus=Vector((0,0,.86));span=.65
    if recipe=='plating':
        A.pasta();hand=F.pointing_hand((.16,.11,.91));leaf=A.ellipsoid('Garnish',(.16,.02,.91),(.018,.009,.002),'hero')
        for t,p in [(0,(.16,.02,.91)),(1.2,(.16,.02,.91)),(2.6,(.02,0,.87)),(4,(.02,0,.87))]:
            pose(leaf,t,location=p);pose(hand,t,location=Vector(p)+Vector((0,.09,0)))
        actions=['A hand places a garnish on the supported dish','The visitor-side view shows food and the public pass, not unrelated hair scissors']
    elif recipe=='burger_build':
        A.plate();root,parts=F.burger();bun=next(o for o in root.children_recursive if o.name.startswith('Burger upper bun'))
        hand=A.hand((.10,.01,.12),scale=.85);hand.parent=bun
        for t,z in [(0,.12),(1.2,.12),(2.8,0),(4,0)]:pose(bun,t,location=(0,0,z))
        actions=['The same upper bun and attached hand settle onto the layered burger','Food, plate and public counter stay coherent through assembly']
    elif recipe=='grip':
        weight=V.dumbbell((0,0,.87));hand=A.hand((.01,-.02,.01),scale=.8);hand.parent=weight
        for t,z in [(0,.87),(1.2,.87),(2.5,.97),(3.6,.87),(4,.87)]:pose(weight,t,location=(0,0,z))
        actions=['One hand settles onto an actual exercise grip and makes one small supported rep','Phone remains supported above the kit; no unrelated repair tool is shown']
    elif recipe=='worksheet':
        F.card((0,0,.788),'LESSON','YOUR TASK','',.38,.28)
        pointer=F.pointing_hand((.04,.12,.81))
        for t,x in [(0,-.06),(1.2,-.06),(2.8,.06),(4,.06)]:pose(pointer,t,location=(x,.12,.81))
        actions=['Own hands point out the lesson task on a worksheet','Supported high/overhead phone view shows the actual learning context']
    else:raise AssertionError(recipe)
    if spec['id'].startswith('over_shoulder'):
        visitor=A.portrait((-.36,-.30,-.20),None)
        for obj in visitor['root'].children_recursive:
            if obj.type=='MESH':A.tag(obj,'foreground_frame','Cropped visitor shoulder frames the public work view')
    A.fixed_side_light(focus)
    result=M.apply(scene,spec,focus,span,action_objects=True)
    result.update(subject_actions=actions,composition=actions,intent='; '.join(actions));return result


def walking(scene,spec):
    root,actor=P.full_actor();V.door((0,.40,0),open_angle=-80);V.venue('sauna')
    thighs=[o for o in root.children_recursive if o.name.startswith('Trouser thigh')];shins=[o for o in root.children_recursive if o.name.startswith('Trouser lower leg')];shoes=[o for o in root.children_recursive if o.name.startswith('Grounded shoe')]
    for items in [thighs,shins,shoes]:items.sort(key=lambda o:o.location.x)
    for f in range(1,round(5*15)+1):
        t=(f-1)/15;elapsed=max(0,min(3,t-1.2));root_y=.80-.28*elapsed;pose(root,t,location=(0,root_y,0))
        for index,side in enumerate([-1,1]):
            phase=elapsed/.90+(0 if index==0 else .50);cycle=math.floor(phase);u=phase-cycle
            swing=max(0,(u-.55)/.45);world_y=.80-.252*(cycle+smooth(swing));lift=.07*math.sin(math.pi*swing)
            ankle=Vector((side*.18,world_y-root_y,.10+lift));hip=Vector((side*.09,0,.98));axis=(ankle-hip).normalized();distance=(ankle-hip).length;drop=Vector((0,-1,0));drop=(drop-axis*drop.dot(axis)).normalized();knee=hip+axis*(distance/2)+drop*math.sqrt(max(0,.49**2-(distance/2)**2))
            P.stretch(thighs[index],hip,knee,t);P.stretch(shins[index],knee,ankle,t);pose(shoes[index],t,location=(side*.18,ankle.y-.055,.045+lift))
    A.fixed_side_light((0,0,1.0));result=M.apply(scene,spec,(0,0,1.0),span=1.25,down=-8,action_objects=True)
    result.update(subject_actions=['One person walks through the already open sauna door','Planted feet and alternating swing phases replace the unrelated squat used by other scripts'],composition=['Clear door opening and grounded feet','Propped visitor-side phone; empty private space'],intent='Film the actual walk through the empty-room door')
    return result


def seasonal_drink(scene,spec,recipe):
    if recipe=='seasonal_board':
        counter(z=1.10);A.menu_board((0,.72,1.92));glass((0,-.04,1.10),name='Same seasonal drink')
        origin=Vector((0,-.50,1.36));cam=B.camera('Menu to same seasonal glass',origin,(0,.72,1.92),36)
        for f in range(1,61):
            t=(f-1)/15;pitch=math.radians(25-48*smooth((t-1.2)/1.8))
            B.key_camera(cam,f,origin,origin+Vector((0,math.cos(pitch),math.sin(pitch))))
        actions=['Menu and the same seasonal glass share one visible counter','A wrist tilt connects the name/price line to the same vessel used for the build and topping']
        result=dict(duration=4,take_end=4,cameras=[(0,cam)])
    else:
        counter();glass(name='Same seasonal drink');focus=Vector((0,0,.943))
        before=set(bpy.data.objects)
        A.ellipsoid('Topping spoon bowl',(0,0,0),(.018,.026,.005),'support')
        G.tube('Topping spoon handle',[(0,.015,0),(0,.10,.008)],.003)
        hand=A.hand((0,.10,.015),scale=.65);hand.rotation_euler.x=math.pi/2
        G.tube('Topping hand wrist',[(0,.12,.015),(0,.22,.025)],.014)
        spoon=A.group('Held topping spoon',before,(.02,.035,1.075),'support','One hand dusts the drink from a supported spoon')
        for t,a in [(0,0),(1.2,0),(2.3,30),(3.0,0),(4,0)]:pose(spoon,t,rotation=(0,math.radians(a),0))
        for j in range(9):
            x=.026*math.cos(j*2.4);y=.026*math.sin(j*2.4)
            dot=A.ellipsoid('Topping on the same drink',(x,y,.945),(.002,.002,.001),'hero')
            for t,s in [(0,.001),(1.4+j*.08,.001),(1.6+j*.08,1),(4,1)]:pose(dot,t,scale=(s,s,s))
        result=M.apply(scene,spec,focus,span=.44,down=90)
        actions=['One held spoon adds topping to the same seasonal glass','The glass base remains on the counter throughout the overhead lean']
    A.fixed_side_light((0,0,1.0));result.update(scope='base_shot_with_action',handover_status='pending_contextual_sequence',
        subject_actions=actions,composition=actions,intent='; '.join(actions),
        mobile_feasibility='Short supported phone lean or wrist tilt; only one subject hand is shown')
    return result


mapping={};results=[]
for (gid,recipe),keys in groups.items():
    variant_id=gid+'__'+recipe
    if selected and variant_id not in selected:continue
    policy=ROOT/'people-policy.json'
    if policy.exists() and (gid in json.loads(policy.read_text())['deferred_guides'] or recipe.startswith('portrait_') or recipe in ['sip_glass','bite_burger','walk']):continue
    active_keys=keys;active_recipe=recipe
    bpy.ops.wm.read_factory_settings(use_empty=True)
    stage=OUT/'.build'/variant_id;stage.mkdir(parents=True,exist_ok=True)
    link=stage/'guides'
    if not link.exists():link.symlink_to(BASE/'guides',target_is_directory=True)
    destination=OUT/variant_id;destination.mkdir(exist_ok=True)
    parent=stage/'catalog/blender-animations';parent.mkdir(parents=True,exist_ok=True)
    if not (parent/gid).exists():(parent/gid).symlink_to(destination,target_is_directory=True)
    B.BASE=stage
    if recipe.startswith('portrait_'):factory=lambda scene,spec:resource_portrait(scene,spec,active_recipe)
    elif recipe in ['sip_glass','bite_burger']:factory=lambda scene,spec:held_replacement(scene,spec,active_recipe)
    elif recipe=='walk':factory=walking
    elif recipe in ['seasonal_finish','seasonal_board']:factory=lambda scene,spec:seasonal_drink(scene,spec,active_recipe)
    elif recipe.startswith('hall_'):
        import cinematic_locations
        factory=lambda scene,spec:cinematic_locations.entrance(scene,spec,kind=active_recipe.split('_',1)[1])
    elif recipe in ['baker_pick','baker_inside']:
        import cinematic_locations
        factory=lambda scene,spec:cinematic_locations.baker_pastry(scene,spec,active_recipe.split('_')[1])
    elif recipe=='baker_answer':
        import people_shots
        factory=lambda scene,spec:people_shots.build(scene,spec,people_shots.baker_answer)
    elif recipe.startswith('room_'):
        import environment_scenes
        environment_scenes.REGISTRY[gid]=('room',recipe.split('_',1)[1]);factory=environment_scenes.make_scene
    elif recipe=='work':
        P.REGISTRY[gid]=('service','work');factory=P.build
    else:factory=lambda scene,spec:work_variant(scene,spec,active_recipe)
    B.FACTORIES[gid]=factory
    plan=P.explicit_review(gid,'Contextual scene',[]) if gid in P.REGISTRY else B.scene_plans.review(gid,'Contextual seasonal drink',[])
    plan.update(subject='Script-specific '+recipe.replace('_',' '),handover='Actual next step is assembled separately from the matching contextual source',composition='Correct resource for these script steps, with physical contacts and usable phone framing')
    B.scene_plans.PLANS[gid]=plan
    try:
        B.run(gid,probes=probes,build_only='--build-only' in args,take_only=False)
        result=dict(id=variant_id,status='probes_rendered' if probes else 'frames_rendered',steps=keys)
        for key in keys:mapping[key]=str(destination.relative_to(BASE))
    except Exception as error:
        import traceback;traceback.print_exc();result=dict(id=variant_id,status='failed',error=str(error))
    results.append(result);print('CONTEXT_VARIANT_PROGRESS',json.dumps(result),flush=True)
    (OUT/('probe-progress.json' if probes else 'render-progress.json')).write_text(json.dumps(results,indent=2)+'\n')
map_path=BASE/'catalog/context-animations/variant-sources.json';previous=json.loads(map_path.read_text()) if map_path.exists() else {};previous.update(mapping);map_path.write_text(json.dumps(previous,indent=2)+'\n')
if any(r['status']=='failed' for r in results):sys.exit(1)
