"""Plate family drafts of the 2026-11-10 regeneration (single example dish; pancake_clear_path keeps its shared spread)."""
import math
import bpy
from mathutils import Vector, Matrix
from drafts.common import new_state, finish

AROUND, ROLL = 75, 35
# Handle raised so the grip and hand start above the rim and table (was 10 deg).
FORK_PITCH = -20
# Owner decision 2026-11-10: glasses 20-25 cm from the lens (beyond the 5-15 cm blocker judgement) so the grips show.
LENS_Y, GLASS_Y = .70, .952

IDS = ('plate_low_push_in_v2', 'plate_high_orbit_v2', 'plate_rise_overhead_v2', 'plate_top_orbit', 'plate_turntable',
       'bite_pip_dish_v2', 'pancake_clear_path_v2')

FOOD_CENTRE = Vector((0, 0, .83))


def diner(distance, pitch=45, elevation=38):
    """Phone pitched `pitch` down; the food centre sits on a slightly shallower ray, about 45% from the top."""
    e, p = math.radians(elevation), math.radians(pitch)
    position = FOOD_CENTRE + distance * Vector((0, -math.cos(e), math.sin(e)))
    return position, position + Vector((0, math.cos(p), -math.sin(p))) * distance
DOWN45 = Vector((0, -math.cos(math.radians(45)), math.sin(math.radians(45))))


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


def rim_hand(P, angle, radius=.146, z=.817):
    """The approved palm-down rim grip of pancake_clear_path (relaxed pose, middle fingertip on the raised rim)."""
    H, A = P.H, P.A
    target = Vector((radius * math.cos(angle), radius * math.sin(angle), z))
    forward = (-math.cos(angle), -math.sin(angle), 0)
    hand = H.place('relaxed', 'L', target=target, forward=forward, normal=(0, 0, 1), anchor='f_middle.03')
    hand['p0_hand'] = True; hand['p0_cropped_grip'] = True; hand['p0_grip_style'] = 'plate_rim_turn'
    bpy.context.view_layer.update()
    mesh = next(o for o in hand.children_recursive if o.type == 'MESH')
    inverse = mesh.matrix_world.inverted()
    for vertex in mesh.data.vertices:
        p = mesh.matrix_world @ vertex.co
        if p.z < .789:
            p.z = .789; vertex.co = inverse @ p
    for obj in hand.children_recursive:
        if obj.type == 'MESH':
            A.tag(obj, 'hand', 'Cropped left grip on the plate rim turns the plate')
    return hand


def build(gid, record, P):
    A = P.A
    state = new_state()
    if gid == 'pancake_clear_path_v2':
        return pancakes(P, state)
    setting = P.place_setting(); food = setting['food']; plate = setting['plate']
    state['triangle_points'] = [Vector((.02, .01, .862)), Vector((-.04, -.144, .815)), Vector((.18, .225, .795))]

    if gid == 'plate_low_push_in_v2':
        state['adaptations'].append('3/4 diner view, phone 45 degrees down: a straight 20 cm push toward the food, elbows on the table, even pace.')
        def sample(u, p, t):
            back = (p - FOOD_CENTRE).normalized() * .20 * (1 - ramp(u))
            return p + back, t + back
        return finish(state, food, *diner(.27), sample)

    if gid == 'plate_high_orbit_v2':
        A.plate((-.22, .24, .785))
        state['triangle_points'][1] = Vector((-.17, .06, .805))
        pitch = math.radians(40); radius = .38; arc = 40
        state['adaptations'].append('Orbit at a constant 0.38 m slant radius and 40 degrees pitch, 40 degrees of arc at an even pace.')
        def sample(u, p, t):
            angle = math.radians(-arc / 2 + arc * ramp(u)); v = p - t; flat = math.hypot(v.x, v.y)
            return t + Vector((flat * math.sin(angle), -flat * math.cos(angle), v.z)), t
        a = math.radians(arc / 2)
        # Orbit about a point 3 cm under the food centre so the food sits a little above the frame centre.
        centre = FOOD_CENTRE - Vector((0, 0, .03))
        end = centre + radius * Vector((math.cos(pitch) * math.sin(a), -math.cos(pitch) * math.cos(a), math.sin(pitch)))
        return finish(state, food, end, centre, sample)

    if gid in ('plate_rise_overhead_v2', 'plate_top_orbit'):
        # Layout of the pending plate_rise_overhead draft: cup at one o'clock, straight fork on the left.
        setting['table'].location = (0, .40, 0); setting['chair'].location.y = 1.22
        for root in [setting['cup'], setting['saucer']]:
            root.location += Vector((.12, .236, 0)) - Vector((.20, .24, 0))
        setting['fork'].location = Vector((-.2015, .0378, .795))
        # Mirrors the fork's 4 cm rim gap on the right; cutting edge (-X) faces the plate.
        A.knife((.2015, .02, .785))
        state['triangle_points'] = [Vector((0, 0, .80)), Vector((.12, .236, .90)), Vector((-.2015, 0, .797))]
        state['camera_up'] = (0, 1, 0)
        if gid == 'plate_top_orbit':
            arc = 45
            state['adaptations'].append(f'Phone flat (90 degrees) at the end height of plate_rise_overhead_v2, standing; it turns {arc} degrees about the vertical axis through the plate centre, no rise, no tilt.')
            def sample(u, p, t):
                # The world Z axis passes through the plate centre; the screen-up reference turns with the phone.
                turn = Matrix.Rotation(math.radians(-arc * (1 - window(u, .15, .95))), 3, 'Z')
                state['camera_up'] = tuple(turn @ Vector((0, 1, 0)))
                return turn @ p, turn @ t
            aim = Vector((0, -.04, .80))
            return finish(state, P.members(plate), aim + Vector((0, 0, .52)), aim, sample)
        state['adaptations'].append('Pedestal rise with the phone flat (90 degrees) the whole way, standing; the lens climbs straight up from 0.28 m above the plate.')
        start_height = .28
        def sample(u, p, t):
            h = p.z - t.z
            z = t.z + start_height + (h - start_height) * ramp(u)
            pos = Vector((p.x, p.y, z))
            return pos, pos + Vector((0, 0, -1))
        # Frame centre 4 cm below the plate centre puts the plate at about 45% from the top.
        aim = Vector((0, -.04, .80))
        return finish(state, P.members(plate), aim + Vector((0, 0, .52)), aim, sample)

    if gid == 'plate_turntable':
        # The lathe plate is round, so the food turns on it; the rim and its light cue stay fixed.
        pivot = A.empty('Turntable food pivot', (0, 0, .785))
        for obj in [o for o in P.members(plate) if not o.name.startswith('Plate with formed rim')]:
            P.attach(obj, pivot)
        # The grip starts at the near rim (280 deg, in frame) and ends at 190 deg, left of the frame.
        end_angle = math.radians(190)
        hand = rim_hand(P, end_angle)
        bpy.context.view_layer.update(); rest = hand.matrix_world.copy()
        state['hand_count'] = 1
        def action(u):
            turn = window(u, .05, .80)
            spin = Matrix.Rotation(math.radians(90 * (1 - turn)), 4, 'Z')
            pivot.rotation_euler.z = math.radians(90 * (1 - turn))
            away = window(u, .82, 1., .3)
            hand.matrix_world = Matrix.Translation((-.45 * away, -.05 * away, .02 * math.sin(math.pi * away))) @ spin @ rest
            for obj in [pivot, hand]:
                obj.keyframe_insert('location'); obj.keyframe_insert('rotation_euler')
            bpy.context.view_layer.update()
        state['actions'].append(action)
        state['contacts'].append(dict(kind='plate_rim_turn', hand=hand.name, surface_z=.785, turn_degrees=90,
                                      grip='approved pancake_clear_path rim grip, palm down on the left rim'))
        state['adaptations'].append('Phone still at 45 degrees; one cropped left hand on the near-left rim turns the plate 90 degrees clockwise, then slides out to the left.')
        return finish(state, food, *diner(.27))

    if gid == 'bite_pip_dish_v2':
        for root in [setting['cup'], setting['saucer'], setting['chair'], setting['fork']]:
            remove(root)
        H = P.H
        fork = A.fork((.055, -.015, .846), role='hero'); fork.rotation_euler = (math.radians(FORK_PITCH), 0, math.pi / 2)
        bpy.context.view_layer.update(); grip = fork.matrix_world @ Vector((0, -.09, .005))
        wrist = H.place('pinch', 'L', target=grip, forward=(-1, 0, 0), normal=(0, 0, -1), anchor='grip')
        P.role(wrist, 'hand'); wrist['p0_hand'] = True; wrist['p0_cropped_grip'] = True; P.attach(wrist, fork)
        hanging = A.empty('Fork pasta hanging under gravity'); strands = []
        for k in range(3):
            points = [((k - 1) * (.004 + .015 * j / 20) + .003 * math.sin(j / 20 * math.tau + k), .004 * math.sin(j / 20 * math.pi + k), -.13 * j / 20) for j in range(21)]
            strand = A.tag(P.G.tube('Hanging pasta strand', points, .0016), 'hero', 'One end remains on the fork; the lower part hangs downward')
            strand.parent = hanging; strands.append(strand)
        start = fork.location.copy()
        lift = Vector((0, -.05, .10))
        def action(u):
            progress = window(u, .12, .82)
            fork.location = start + lift * progress; fork.rotation_euler.x = math.radians(FORK_PITCH + 12 * progress)
            bpy.context.view_layer.update(); hanging.location = fork.matrix_world @ Vector((0, .054, .010))
            length = min(.13, max(.008, hanging.location.z - .848)); hanging.scale.z = length / .13
            hanging.keyframe_insert('scale'); fork.keyframe_insert('location'); fork.keyframe_insert('rotation_euler')
        state['actions'].append(action); state['hand_count'] = 1
        state['contacts'].append(dict(kind='fork_grip', hand=wrist.name, prop=fork.name, grip=list(grip), crop='Only the small grip at the right edge; palm, wrist and arm extend out of frame'))
        state['adaptations'].append('Food only, phone static at 45 degrees: the fork lifts a bite 10 cm up and 5 cm toward the lens; three strands hang from it.')
        aim = Vector((.04, -.03, .88))
        return finish(state, food + [o for o in P.members(fork) if o.get('composition_role') == 'hero'] + strands, aim + .40 * DOWN45, aim)
    raise ValueError(gid)


def pancakes(P, state):
    """Portrait still view of the stack; two cropped hands slide the two near glasses out sideways."""
    A, G = P.A, P.G
    import p0_table_compositions as T
    A.tag(G.block('Long commercial dining tabletop', (0, .55, .752), (1.4, 2.65, .066), .025), 'structure', 'A continuous supported tabletop')
    T.background(long_table=True)
    T.platter((.16, 1.15, .785), .15); stack = T.pancakes((.16, 1.15, .793))
    left = T.cocktail((.112, GLASS_Y, .785), 0); right = T.cocktail((.208, GLASS_Y, .785), 1)
    state['actions'] += [left['action'], right['action']]
    hands = []
    for drink, is_right in [(right, True), (left, False)]:
        hand = T.turned_glass_grip(drink, is_right, AROUND, ROLL); P.attach(hand, drink['root']); hands.append(hand)
    state['hand_count'] = 2
    def action(u):
        r = window(u, .06, .42); l = window(u, .48, .84)
        right['root'].location.x = .208 + .32 * r; left['root'].location.x = .112 - .32 * l
        for d in [right, left]:
            d['root'].keyframe_insert('location'); d['root'].keyframe_insert('rotation_euler')
        bpy.context.view_layer.update()
    state['actions'].append(action)
    state['contacts'].append(dict(kind='companion_clears_path', surface_z=.785, sequence=['right hand slides the right glass right', 'left hand slides the left glass left'],
                                  maximum_hands=2, all_props_stay_on_table=True, phone_static=True))
    state['adaptations'].append('Phone still in portrait, lens 15 cm above the table and about 42 cm from the stack; two glasses about 22 cm in front of the lens slide out sideways one by one, each by the hand on its own side.')
    # Aim 2.5 cm under the stack centre so the stack sits a little above the frame centre.
    aim = Vector((.16, 1.15, .825))
    lens = Vector((.16, LENS_Y, .935))
    return finish(state, P.members(stack), lens, aim)
