"""Counter, hand-off and pour family drafts of the 2026-11-10 regeneration (visitor side of the counter only)."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish

IDS = ('counter_over_shoulder_v2', 'counter_edge_to_pass_v2', 'counter_hand_receive', 'handoff_counter_cup_v2',
       'handoff_plate_lands_v2', 'pour_side_low_v2', 'pour_static_45')

TOP = 1.05
# counter_hand_receive barista (owner r8): feet behind the counter facing the customer, his right hand over the cup's
# path, and where the saucer starts (judgement).
BARISTA_FEET = (.12, .72, 0)
BARISTA_SLIDE_START = (0, .24, TOP)
BARISTA_TOP_BACK = .44                  # counter top 0.59 m deep here, 2 cm over the cabinet's back (was 0.90 m)
BARISTA_MACHINE_OFFSET = (0, -.135)     # out of frame; 0.65 m deep, 3 cm over each edge of the shallower top


def add_barista(P, machine, state, gid):
    """The working barista behind the counter (owner 2026-11-12), in guides whose frame shows the area behind the bar."""
    import barista
    barista.add(P, machine, state, gid)


def ramp(u, r=.15):
    """Trapezoid velocity: an even pace with short ease-in and ease-out; the peak is 1/(1-r) of the mean."""
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def window(u, a, b, r=.2):
    return ramp((u - a) / (b - a), r)


def remove(root):
    for obj in list(root.children_recursive) + [root]:
        bpy.data.objects.remove(obj, do_unlink=True)


def view(yaw, pitch):
    """Unit view direction: yaw from +Y toward +X, pitch below horizontal (degrees)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p)))


def reshape(hand, target, curl, squeeze):
    """Relax the relaxed pose in place: curl the outer finger joints toward the palm (+Z) by `curl` degrees, draw the
    fingers `squeeze` of the way toward the middle finger at the tips, then put the middle fingertip back on `target`."""
    import json
    mesh = next(o for o in hand.children_recursive if o.type == 'MESH')
    names = {g.index: g.name for g in mesh.vertex_groups}
    th = math.radians(curl)
    tip = Vector(json.loads(mesh['landmarks'])['f_middle.03'])
    def deform(co, weights):
        co = co.copy()
        outer = sum(w for n, w in weights.items() if n.startswith('f_') and (n[-4:-2] in ('02', '03') or '.02.' in n or '.03.' in n))
        finger = sum(w for n, w in weights.items() if n.startswith('f_'))
        if th and outer:
            yc, zc = .132, 0.
            a = th * min(1., outer)
            y, z = co.y - yc, co.z - zc
            if y > 0:
                co.y = yc + y * math.cos(a) - z * math.sin(a); co.z = zc + y * math.sin(a) + z * math.cos(a)
        if squeeze and finger:
            t = max(0., min(1., (co.y - .10) / .07))
            co.x += (.005 - co.x) * squeeze * t * min(1., finger)
        return co
    for v in mesh.data.vertices:
        v.co = deform(v.co, {names[g.group]: g.weight for g in v.groups})
    mesh.data.update()
    new_tip = deform(tip, {'f_middle.03.R': 1.})
    bpy.context.view_layer.update()
    hand.matrix_world.translation += target - mesh.matrix_world @ new_tip
    bpy.context.view_layer.update()
    hand['p0_hand_reshape'] = dict(curl_deg=curl, squeeze=squeeze)


def palm_down(P, target, forward, side='R', floor=None, why='Cropped palm-down grip', cropped=True, tilt=0., extend=0., roll=0., toward=(0, -1, 0),
              palm_side_down=False, curl=0., squeeze=0.):
    """The approved relaxed palm-down rim grip (plate_turntable, pancake_clear_path): middle fingertip on the rim.
    `tilt` lowers the fingertips onto the rim and raises the wrist; `roll` leans the hand plane about the fingers'
    axis toward `toward` (degrees), so a low lens sees the back and fingers instead of an edge-on hand; `extend`
    lengthens the forearm cuff along its own axis (metres)."""
    flat = Vector(forward); flat.z = 0; flat.normalize()
    t = math.radians(tilt)
    fwd = flat * math.cos(t) + Vector((0, 0, -math.sin(t)))
    r = math.radians(roll)
    normal = Vector((0, 0, math.cos(r))) + Vector(toward).normalized() * math.sin(r)
    if palm_side_down:
        # The mesh's +Z is the palm side (the fingers curl toward it), so a palm-down hand needs the normal flipped.
        normal = -normal
    hand = P.H.place('relaxed', side, target=target, forward=fwd, normal=normal, anchor='f_middle.03')
    hand['p0_hand'] = True; hand['p0_cropped_grip'] = cropped; hand['p0_hand_tilt_deg'] = tilt
    if curl or squeeze:
        reshape(hand, Vector(target), curl, squeeze)
    if floor is not None:
        bpy.context.view_layer.update()
        mesh = next(o for o in hand.children_recursive if o.type == 'MESH')
        inverse = mesh.matrix_world.inverted()
        for vertex in mesh.data.vertices:
            p = mesh.matrix_world @ vertex.co
            if p.z < floor:
                p.z = floor; vertex.co = inverse @ p
    if extend:
        # A short cuff extension along the forearm's own axis keeps its real thickness (no thin stretched lines).
        bpy.context.view_layer.update()
        extension = -fwd * extend
        for mesh in [o for o in hand.children_recursive if o.type == 'MESH']:
            groups = {g.index for g in mesh.vertex_groups if g.name.startswith('forearm.')}
            inverse = mesh.matrix_world.inverted()
            cap = [v.index for v in mesh.data.vertices if v.co.y < -.110]
            for vertex in mesh.data.vertices:
                weight = max([g.weight for g in vertex.groups if g.group in groups] + [0.])
                if weight:
                    vertex.co = inverse @ (mesh.matrix_world @ vertex.co + extension * weight * weight)
            # Open the cut end of the cropped forearm: a closed cap draws as a stump instead of fading out.
            import bmesh
            bm = bmesh.new(); bm.from_mesh(mesh.data); bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.verts[i] for i in cap], context='VERTS'); bm.to_mesh(mesh.data); bm.free()
            mesh.data.update()
        hand['cuff_extension_m'] = extend
    for obj in hand.children_recursive:
        if obj.type == 'MESH':
            P.A.tag(obj, 'hand', why)
    return hand


def handle_pinch(P, cup, side='R', forward=(-.35, .94, 0), normal=(-1, 0, 0)):
    """The approved pinch pose, thumb and index meeting on the cup's open handle (+X side of the cup)."""
    bpy.context.view_layer.update()
    target = cup.matrix_world @ Vector((.090, .004, .066))
    hand = P.H.place('pinch', side, target=target, forward=forward, normal=normal, anchor='grip')
    hand['p0_hand'] = True; hand['p0_cropped_grip'] = True
    for obj in hand.children_recursive:
        if obj.type == 'MESH':
            P.A.tag(obj, 'hand', 'Cropped pinch on the real cup handle')
    return hand


def key(*objects):
    for obj in objects:
        obj.keyframe_insert('location'); obj.keyframe_insert('rotation_euler')
    bpy.context.view_layer.update()


def build(gid, record, P):
    state = new_state()
    if gid.startswith('counter_over_shoulder'):
        return over_shoulder(P, state, gid)
    if gid.startswith('counter_edge_to_pass'):
        return edge_to_pass(P, state, gid)
    if gid == 'counter_hand_receive':
        return hand_receive(P, state)
    if gid.startswith('handoff_counter_cup'):
        return counter_handoff(P, state)
    if gid.startswith('handoff_plate_lands'):
        return plate_lands(P, state)
    if gid.startswith('pour_'):
        return pour(gid, record, P, state)
    raise ValueError(gid)


def counter_cups(P, hero_xy, hero=True):
    """The counter_over_shoulder / counter_edge_to_pass counter: board, machine, three waiting cups, one hero cup."""
    top, machine = P.counter(); menu, columns = P.board()
    drink, saucer = P.cup(hero_xy[0], hero_xy[1], TOP, hero)
    for x in [-.6, -.4, -.2]:
        P.cup(x, .60, TOP, False)
    for obj in bpy.context.scene.objects:
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    return dict(top=top, machine=machine, menu=menu, columns=columns, drink=drink, saucer=saucer)


def over_shoulder(P, state, gid):
    """C2: a friend films over the visitor's right shoulder from the customer side; a slow 20 cm push-in."""
    import p0_people as people
    c = counter_cups(P, (.50, .30))
    add_barista(P, c['machine'], state, gid)
    root, arm, masks = people.load_creator(P)
    for mask in masks:
        bpy.data.objects.remove(mask, do_unlink=True)
    # The visitor stands at the counter, facing the barista area, back to the friend's lens.
    root.rotation_euler.z = math.pi; root.location = Vector((-.02, -.52, 0))
    P.role(root, 'foreground')
    state['silhouettes'] = 1
    hero = P.members(c['drink']) + P.members(c['saucer'])
    for obj in P.members(c['machine']):
        P.A.tag(obj, 'hero', 'The machine and the served cup are the counter detail the push brings in')
    hero += P.members(c['machine'])
    for obj in P.members(c['menu']):
        P.A.tag(obj, 'support', 'Board above the counter detail')
    state['contacts'].append(dict(kind='over_shoulder', person='canonical creator (back view)', shoulder='visitor right',
                                  camera_side='customer side, friend behind the visitor'))
    state['adaptations'].append('A friend holds the phone at the visitor shoulder height, behind and to the right; the near shoulder and head stay in the left part of the frame, out of the hero. One 20 cm straight push toward the counter at an even pace, no turn.')
    # 29 cm right of the visitor's head (C2: 20-30 cm to the side), aimed so the turned machine stays whole in frame.
    end = Vector((.24, -.88, 1.42)); aim = Vector((.68, .44, 1.20))
    push = .20
    def sample(u, p, t):
        # The friend steps straight toward the counter behind the visitor; the view direction does not turn.
        back = Vector((0, -push * (1 - ramp(u)), 0))
        return p + back, t + back
    return finish(state, hero, end, aim, sample)


def edge_to_pass(P, state, gid):
    """C3 portrait alternative: lens 15 cm above the counter, 17 deg down, an 18 cm truck along the edge, no turn."""
    # Owner review r4: the cup handle sits 7.4 cm clear of the machine (as counter_edge_to_pass); the camera and the
    # counter light streaks move with the cup, so its framing stays.
    cx = P.PASS_CUP_X; dx = cx - .6
    c = counter_cups(P, (cx, .02))
    add_barista(P, c['machine'], state, gid)
    P.role(c['menu'], 'background')
    for obj in P.members(c['drink']):
        if 'hollow ceramic body' in obj.name:
            obj['p0_emphasize_light'] = True
    for y, a in [(-.06, .12), (.16, .18)]:
        P.light_edge('Counter surface reflected light', [(a + dx, y, 1.051), (a + dx + .42, y, 1.051)], .00055)
    cupc = Vector((cx, .02, 1.11)); yaw = 26; pitch = 17; dist = .48
    flat = Vector((math.sin(math.radians(31)), math.cos(math.radians(31)), 0))
    end = Vector((cupc.x, cupc.y, TOP + .15)) - flat * math.sqrt(dist ** 2 - (TOP + .15 - cupc.z) ** 2)
    aim = end + view(yaw, pitch)
    truck = .18
    state['adaptations'].append('Portrait, lens 15 cm above the counter top and in front of its edge, pitched 17 degrees down; an 18 cm truck to the right along the edge in 3 s at an even pace, no turn.')
    def sample(u, p, t):
        shift = Vector((-truck * (1 - ramp(u)), 0, 0))
        return p + shift, t + shift
    return finish(state, P.members(c['drink']), end, aim, sample)


def slide_in(P, state, drink, saucer, land, start, angle, release, withdraw, why):
    """The barista's palm-down hand slides the saucer with its cup across the counter top to the landing spot;
    fingertips on the saucer rim at `angle` (degrees from +X), the arm reaching in from beyond that rim."""
    cup_root = drink
    carrier = P.A.empty('Saucer slide on the counter', Vector(land)); P.attach(cup_root, carrier); P.attach(saucer, carrier)
    bpy.context.view_layer.update()
    a = math.radians(angle)
    target = Vector(land) + Vector((.084 * math.cos(a), .084 * math.sin(a), .014))
    hand = palm_down(P, target, (-math.cos(a), -math.sin(a), 0), 'R', floor=TOP + .004, why=why, cropped=False, extend=.10,
                     palm_side_down=True, curl=22, squeeze=.30, tilt=15, roll=20)
    P.attach(hand, carrier)
    offset = Vector(start) - Vector(land)
    hand_rest = hand.location.copy()
    def action(u):
        ang = math.radians(angle + 10)
        s = window(u, .06, release, .25)
        carrier.location = Vector(land) + offset * (1 - s)
        a = window(u, release + .02, withdraw, .3)
        hand.location = hand_rest + Vector((.40 * math.cos(ang), .40 * math.sin(ang), .20)) * a
        key(carrier, hand)
    state['actions'].append(action)
    return hand, carrier


def hand_receive(P, state):
    """C1: static POV at chest height; the barista slides the cup across with his own right hand, the visitor's hand
    takes it; cut on the grab."""
    import barista
    top, machine = P.counter(body=True, machine_offset=BARISTA_MACHINE_OFFSET)
    # Owner r7/r8: the barista's own arm delivers the cup while he leans in low enough for his eyes to stay in frame;
    # the top's back edge comes forward to BARISTA_TOP_BACK so his elbow passes behind it (the machine with it).
    for vertex in top.data.vertices:
        if vertex.co.y > 0:
            vertex.co.y -= .75 - BARISTA_TOP_BACK
    top.data.update()
    drink, saucer = P.cup(0, .04, TOP)
    for obj in P.members(drink):
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    land = Vector((0, .04, TOP)); start = Vector(BARISTA_SLIDE_START)
    carrier = P.A.empty('Saucer slide on the counter', land); P.attach(drink, carrier); P.attach(saucer, carrier)
    carrier['p0_slide_direction'] = list((land - start).normalized())
    release = .50
    def slide(u):
        carrier.location = land + (start - land) * (1 - window(u, .06, release, .25))
        key(carrier)
    state['actions'].append(slide)
    aim = Vector((.02, .04, 1.11)); dist = .50; pitch = 25
    end = aim - view(0, pitch) * dist
    # Owner 2026-11-12 (r8): in this guide only he serves facing the customer, then turns away and walks out left.
    barista.add_serve(P, state, BARISTA_FEET, carrier, saucer, drink, release, end)
    visitor = handle_pinch(P, drink)
    bpy.context.view_layer.update(); grip = visitor.matrix_world.translation.copy()
    fwd = Vector((-.35, .94, 0)).normalized()
    state['hand_count'] = 2
    def action(u):
        # The visitor's hand approaches along its own forward axis from the lower frame edge, kept above the counter top.
        back = 1 - window(u, .60, 1., .3)
        visitor.location = grip - fwd * .32 * back + Vector((0, 0, .02 * back))
        key(visitor)
    state['actions'].append(action)
    state['contacts'].append(dict(kind='counter_hand_receive', surface_z=TOP, saucer_supported=True,
                                  sequence=['barista, facing the customer, slides the saucer across with his right hand', 'barista lets go, turns away and walks out left', 'visitor hand pinches the handle'],
                                  maximum_hands=2, visible_hands='barista right hand (rig) + visitor right hand', cut_on='grab'))
    state['adaptations'].append('Phone still at chest height about 25 degrees down; the barista, facing the customer, slides the cup on its saucer across the counter with his own right hand, lets go, turns away and walks out of frame to the left, and the visitor\'s right hand takes the handle. The guide ends on the grab.')
    return finish(state, P.members(drink) + P.members(saucer), end, aim)


def counter_handoff(P, state):
    """Hand-off 3: static at chest height on the counter corner; the barista slides the served cup in and leaves."""
    P.counter(body=True); drink, saucer = P.cup(-1.0, -.02, TOP)
    P.light_edge('Served counter corner light', [(-1.39, .12, 1.051), (-1.39, -.148, 1.051), (-.78, -.148, 1.051)], .00065, polyline=True)
    for obj in P.members(drink):
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    land = (-1.0, -.02, TOP)
    slide_in(P, state, drink, saucer, land, (-1.0, .44, TOP), 168, .55, .90,
             'Barista hand from the far side slides the served saucer, fingertips on its far rim')
    state['hand_count'] = 1
    state['contacts'].append(dict(kind='served_counter_corner', cup=drink.name, saucer=saucer.name, support_surface_z=TOP,
                                  saucer_supported=True, hand_leaves_before_target=True))
    state['adaptations'].append('Phone still at chest height, about 25 degrees down and 50 cm from the landing spot; the barista slides the cup on its saucer to the counter corner, lets go and withdraws.')
    aim = Vector((-1.0, -.02, 1.11)); dist = .50; pitch = 25
    end = aim - view(8, pitch) * dist
    return finish(state, P.members(drink), end, aim)


def plate_lands(P, state):
    """Hand-off 1: static POV 45 deg down on the place setting; the server slides the plate onto the spot and leaves."""
    G, A = P.G, P.A
    setting = P.place_setting(); food = setting['food']; plate = setting['plate']
    for root in [setting['cup'], setting['saucer']]:
        remove(root)
    glass = G.glass('Water glass', .22, .25, .785); A.tag(glass, 'support', 'Water glass outside the plate footprint')
    knife = A.knife((.163, -.02, .785))
    state['triangle_points'] = [Vector((.02, .01, .862)), Vector((-.04, -.144, .815)), Vector((.22, .25, .86))]
    # Server's palm-down fingertips on the far rim (the approved plate_turntable rim grip), arm from the far side.
    angle = math.radians(100)
    target = Vector((.146 * math.cos(angle), .146 * math.sin(angle), .817))
    hand = palm_down(P, target, (-math.cos(angle), -math.sin(angle), 0), 'R', floor=.789,
                     why='Server hand from the far side, fingertips on the far plate rim', cropped=False, extend=.10,
                     palm_side_down=True, curl=22, squeeze=.30, tilt=30)
    carrier = A.empty('Plate slide on the table', Vector((0, 0, .785)))
    P.attach(plate, carrier); P.attach(hand, carrier)
    hand_rest = hand.location.copy(); state['hand_count'] = 1
    def action(u):
        s = window(u, .06, .55, .25)
        carrier.location = Vector((-.04 * (1 - s), .26 * (1 - s), .785))
        a = window(u, .58, .90, .3)
        hand.location = hand_rest + Vector((-.05, .60, .28)) * a
        key(carrier, hand)
    state['actions'].append(action)
    state['contacts'].append(dict(kind='plate_served_slide', surface_z=.785, plate_supported=True, hand=hand.name,
                                  hand_leaves_before_target=True))
    state['adaptations'].append('Phone still 45 degrees down from the seated eye line, focus locked on the empty spot; the server slides the plate the last 26 cm onto the spot with fingertips on its far rim, then lets go and leaves.')
    aim = Vector((0, 0, .80)); dist = .40
    end = aim - view(0, 45) * dist
    return finish(state, food, end, aim)


def pour(gid, record, P, state):
    """Static pours at the counter, reusing the pour_* stream and vessel builders of p0_scenes."""
    A, G, V = P.A, P.G, P.V
    latte = gid == 'pour_static_45'
    P.counter()
    drink, saucer = P.cup(0, 0, TOP, art='heart')
    V.window((.3, 1.5, TOP + .60)); P.role(V.chair((0, 1, 0)), 'background')
    state['light_position'] = (.3, 1.45, TOP + .60)
    if not latte:
        for obj in list(P.members(drink)):
            if obj.name.startswith('Foam'):
                bpy.data.objects.remove(obj, do_unlink=True)
    heroes = P.members(drink)
    start = Vector((-.033, .005, TOP + .20)); end = Vector((-.033, .005, TOP + .116))
    pitcher = P.reused_pourer(latte, start)
    stream = A.tag(G.tube('Milk stream / spout to coffee', [start, end], .002), 'support', 'Straight flow falls vertically from the fixed spout to a point inside the cup')
    stream.shape_key_add(name='Basis'); off = stream.shape_key_add(name='Flow has not started'); tail = stream.shape_key_add(name='Last drop lands')
    for point in off.data:
        point.co = start
    for point in tail.data:
        point.co = end
    pivot = A.empty('Pitcher spout pivot', start); P.attach(pitcher, pivot)
    growth_keys = []
    for foam in [o for o in P.members(drink) if o.name.startswith('Foam')]:
        foam.shape_key_add(name='Basis'); growth = foam.shape_key_add(name='Milk art growth'); growth_keys.append(growth)
        original = [v.co.copy() for v in foam.data.vertices]
        for point, source in zip(foam.data.shape_keys.key_blocks[0].data, original):
            point.co.x = source.x * .15; point.co.y = source.y * .15
    fall = math.sqrt(2 * (start.z - end.z) / 9.81)
    away = Vector((-.27, .33, .05))
    # Owner review r4: the kettle is carried in from where it leaves, over an arc that lowers it onto the cup, tilting
    # as it comes; the flow starts once it holds the pour pose.
    arrive, tilted = .24, .26
    flow_start = .18 if latte else tilted
    # Starts just outside the top-left corner, so the whole carry reads in frame instead of the last 0.4 s.
    enter = start + Vector((-.16, .18, .10)); lift = start + Vector((-.08, .07, .12))
    def pour_action(u):
        if latte:
            tilt = P.smooth((u - .05) / .26)
        else:
            tilt = P.smooth((u - .08) / (tilted - .08))
        tilt *= 1 - P.smooth((u - .78) / .22)
        pivot.rotation_euler.y = math.radians((32 if latte else 58) * tilt)
        pivot.keyframe_insert('rotation_euler')
        if not latte:
            s = window(u, 0., arrive)
            carried = enter * (1 - s) ** 2 + lift * 2 * s * (1 - s) + start * s * s
            # The kettle leaves the moment the flow stops at the spout and is out of frame before the final hold.
            pivot.location = carried + away * window(u, .84, .985)
            pivot.keyframe_insert('location')
        front = min(1, max(0, (u - flow_start) * record['durationSec'] / fall)) ** 2
        last_drop = min(1, max(0, (u - .84) * record['durationSec'] / fall)) ** 2
        off.value = 1 - front; tail.value = last_drop
        off.keyframe_insert('value'); tail.keyframe_insert('value')
        for index, growth in enumerate(growth_keys):
            growth.value = P.smooth((u - .10 - index * .025) / .55); growth.keyframe_insert('value')
    state['actions'].append(pour_action)
    state['contacts'].append(dict(kind='stream', source=list(start), receiver=list(end), cup_radius=.045, receiver_within_cup=True,
        gravity_axis=[0, 0, -1], straight_stream_vertical=True, flow_start_u=flow_start, flow_stop_u=.84, fall_seconds=fall, pitcher_tilts_toward_cup=True))
    state['adaptations'].append('Pitcher stays beside the cup, tilts toward it, starts a vertical gravity-led stream after tilting, then stops flow and returns upright. The last drop lands before the final target hold.')
    if latte:
        state['adaptations'].append('Phone still at 45 degrees down on the cup, 27 cm away on 1x; the milk stream enters from the top edge and the heart grows in a still frame.')
        # Lens on the 45 degree line through the cup centre; the aim sits 3 cm lower so the cup rides in the upper
        # part of the hero band (centre about 42% from the top) instead of forcing the lens back.
        centre = Vector((0, 0, TOP + .075)); end_pos = centre - view(-12, 45) * .31
        aim = centre - Vector((0, 0, .03))
        return finish(state, heroes, end_pos, aim)
    state['adaptations'].append('Kettle carried in from the left, back and above along an arc that lowers it onto the cup (u 0 to 0.24), tilting from u 0.08 into the 58 deg pour pose at u 0.26, where the flow starts.')
    state['adaptations'].append('Kettle slides out to the left of the frame, back and slightly up, away from the cup and the phone, from the frame the flow stops (u 0.84) and is out of frame by u 0.985.')
    state['adaptations'].append('Phone still in portrait, lens 8 cm above the counter top just below the cup rim, held in front of the counter edge, 30 cm from the cup on 1x; the kettle stream carries the action.')
    aim = Vector((0, 0, TOP + .065)); flat = Vector((.67, .74, 0)).normalized()
    end_pos = Vector((0, 0, TOP + .08)) - flat * .30
    return finish(state, heroes, end_pos, aim)
