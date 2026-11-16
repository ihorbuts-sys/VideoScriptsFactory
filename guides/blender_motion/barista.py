"""The approved barista rig at work behind the counter, as a supporting person.

Two performances:
- `add`: at the espresso machine's working face (p0_scenes.counter turns it to look left along the counter), body in
  profile, the right hand holding the approved milk pitcher by its handle and swirling it in a small loop (first frame =
  last frame), the left arm relaxed.
- `add_serve`: facing the customer across the counter (face toward the lens, an owner exception for that shot), he
  slides a saucer with its cup to the customer with his right hand, lets go, turns away, lowers the hand and walks
  out of frame to the left. The face of `add` stays in profile, turned away from the customer side.
Arms are solved with the creator's two-bone reach (p0_people.ArmPose); fingers close joint by joint until they touch
the held object (the real_hands.wrap idea, on the barista's own hand bones). Strokes use the character fade at the
supporting opacity.
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree
import p0_people as PP

SOURCE = Path(__file__).resolve().parents[2] / 'model_refferences/barista/tripo-rigged/review/asset.blend'
# Feet in the machine's frame (working face on local -Y, the counter's back on local -X): 0.70 m to the back of the
# machine centre, 0.62 m in front of its working face; his right side clears the counter's 0.75 m back edge.
FEET_LOCAL = Vector((-.70, -.62, 0.))
BODY_AWAY_DEG = 10.     # body turned past profile, away from the customer side (judgement)
HEAD_AWAY_DEG = 12.     # head turned further away, looking along the machine (judgement)
HEAD_DOWN_DEG = 16.     # looking down at the work (judgement)
LEAN_DEG = 7.           # trunk leans toward the machine (judgement)
# Strokes fade in over 22 cm above this height (render_p0 character fade); 7 cm under the counter top, so hands and a
# held pitcher just above the top stay drawn while the body below the top is hidden by the counter itself.
FADE_FLOOR = .98
# Milk pitcher (model_refferences/objects/milk_pitcher/functional, as in pour_top_down_latte): body axis and the
# handle bar centre in its own frame (bar measured 7.4-9.5 cm out, between 7 and 13 cm up).
PITCHER_AXIS = Vector((-.012, -.0016, 0.))
PITCHER_BAR = Vector((.085, -.055, .100))
PITCHER_BAR_HALF = .0105
# Handle bar centre relative to his right shoulder (ahead, to his right, height): the pitcher base 2-9 cm above the
# counter top, elbow 6-12 cm under the shoulder, wrist within 35 degrees of straight (judgement).
PITCHER_HOLD = (.44, 0., 1.17)
# Per guide, chosen so the hand and pitcher stay clear of the hero cup and board (r7 hold search over 18-30 holds).
HOLDS = {'counter_edge_to_pass': (.44, -.05, 1.24), 'counter_edge_to_pass_v2': (.44, -.05, 1.24),
         'counter_over_shoulder': (.38, .08, 1.22), 'counter_over_shoulder_v2': (.44, .08, 1.22)}
POLE_OUT_DEG = 60.      # elbow plane turned from straight down toward his right: a slightly raised elbow (judgement)
SWIRL_RADIUS = .010     # wrist circle of the milk swirl (judgement)
SWIRL_TURNS = 2
FINGER_RADIUS = .0085   # barista finger half-thickness (measured on the rig mesh, judgement within 1 mm)
FINGERS = ('Index', 'Middle', 'Ring', 'Pinky')
# counter_hand_receive (owner 2026-11-12, r8): he serves facing the customer across the counter, face toward the lens,
# leaning over the counter with soft knees so his eyes sit inside the frame; after the release he turns 135 deg
# clockwise (seen from above), lowers the hand and walks out to the left.
SERVE_LEAN_DEG = 34.            # trunk over the counter while serving (judgement)
SERVE_PUSH_LEAN_DEG = 6.        # extra lean at full push (judgement)
SERVE_KNEE_DROP_M = .09         # hips lower with bent knees, feet planted (judgement)
SERVE_TURN_DEG = 135.           # owner: clockwise seen from above
SERVE_UP_U = (.52, .60)         # straighten up off the counter and step back (0.35 s)
SERVE_STEP_BACK_M = .15         # room for his left arm as he turns (judgement)
SERVE_TURN_U = (.57, .71)       # then turn and lower the hand (0.6 s)
SERVE_WALK_U = (.58, .98)       # walk out, 1.2 s
SERVE_WALK_M = 1.35             # 1.1 m/s on average (owner 0.8-1.2)
SERVE_WALK_DIR = (-1., .25)     # to the screen left and a little away (judgement)
SERVE_WITHDRAW_U = .60
SERVE_ELBOW_DOWN = .22           # elbow plane mostly sideways: the forearm stays above the counter top
SERVE_ELBOW_BACK = 1.
SERVE_KNUCKLE = (.17, .075)      # middle knuckle 9 cm back from the rim and 5.8 cm above it: the forearm clears the edge
SERVE_LEFT_REST_Z = 1.15         # left wrist height: the hand rests just above the counter top
SERVE_SET_AT = .4                # share of the push where the hand shape is fitted to the forearm
SLIDE_FADE_FLOOR = .90          # the hands ride a few cm above the top; the counter cabinet hides the body below it

def load():
    with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
        dst.objects = [name for name in src.objects if name != 'Icosphere']
    for obj in dst.objects:
        bpy.context.scene.collection.objects.link(obj)
    root = next(o for o in dst.objects if o.type == 'EMPTY' and o.get('asset_id') == 'barista_rigged')
    arm = next(o for o in dst.objects if o.type == 'ARMATURE')
    meshes = [o for o in dst.objects if o.type == 'MESH']
    assert len(meshes) == 14 and not any(o.hide_render for o in meshes), [o.name for o in meshes]
    for obj in [root, arm, *meshes]:
        obj.animation_data_clear()
    for bone in arm.pose.bones:
        bone.matrix_basis.identity()
    # The objects-page preparation (lineart_render.prepare_meshes) without its recentring: welded seams, outward
    # normals, smooth shading; the armature keeps deforming the source weights.
    for obj in meshes:
        mesh = bmesh.new(); mesh.from_mesh(obj.data)
        bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=2e-6)
        bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
        mesh.to_mesh(obj.data); mesh.free()
        obj.data.polygons.foreach_set('use_smooth', [True] * len(obj.data.polygons))
        normal = obj.modifiers.new('Clean weighted normals', 'WEIGHTED_NORMAL'); normal.keep_sharp = True; normal.weight = 50
        # Auto-rig weight bleed: thigh skin under the resting fingertips also follows the finger bones, so a raised
        # hand drags a fold of thigh with it. Skin led by a leg or trunk bone drops its hand weights.
        groups = {g.index: g.name.split(':')[-1] for g in obj.vertex_groups}
        for vertex in obj.data.vertices:
            if not vertex.groups:
                continue
            lead = groups[max(vertex.groups, key=lambda g: g.weight).group]
            if 'Hand' in lead or 'Arm' in lead:
                continue
            for g in [g.group for g in vertex.groups if 'Hand' in groups[g.group]]:
                obj.vertex_groups[g].remove([vertex.index])
    return root, arm, meshes


def turn(arm, bone, rotation):
    """Rotate a pose bone in world space about its own head."""
    world = arm.matrix_world @ bone.matrix
    result = rotation.to_matrix().to_4x4() @ world
    result.translation = world.translation
    bone.matrix = arm.matrix_world.inverted() @ result
    bpy.context.view_layer.update()


def stand(feet, facing_angle, lean=LEAN_DEG, side_lean=0., head_away=HEAD_AWAY_DEG, head_down=HEAD_DOWN_DEG):
    """Load the rig standing at `feet` facing `facing_angle` (radians from +X); trunk leans `lean` degrees forward and
    `side_lean` degrees to its right, head turned `head_away` degrees to its left and `head_down` degrees down."""
    bpy.context.view_layer.update()
    root, arm, meshes = load()
    # The source root already turns the rig (canonical front -Y as loaded); a further turn of a about Z faces (sin a, -cos a).
    extra = facing_angle + math.pi / 2
    root.rotation_euler.z += extra
    root.location = feet
    bpy.context.view_layer.update()
    facing = Vector((math.cos(facing_angle), math.sin(facing_angle), 0))
    side = Vector((0, 0, 1)).cross(facing)          # its left; turning about it tips the trunk forward
    for name, share in [('Spine', .3), ('Spine1', .35), ('Spine2', .35)]:
        turn(arm, PP.named(arm, name), Quaternion(facing, math.radians(side_lean * share)) @ Quaternion(side, math.radians(lean * share)))
    for name, share in [('Neck', .4), ('Head', .6)]:
        away = Quaternion(Vector((0, 0, 1)), math.radians(head_away * share))
        turn(arm, PP.named(arm, name), away @ Quaternion(side, math.radians(head_down * share)))
    head = PP.named(arm, 'Head')
    rest_head = (arm.matrix_world @ head.bone.matrix_local).to_3x3()
    root['p0_supporting_person'] = 'barista'
    root['p0_face_forward_local'] = list(rest_head.inverted() @ Vector((math.sin(extra), -math.cos(extra), 0)))
    root['p0_eye_local'] = list((arm.matrix_world @ head.bone.matrix_local).inverted() @ (Matrix.Translation(root.location) @ Matrix.Rotation(extra, 4, 'Z') @ Vector((.01, -.12, 1.56))))
    return root, arm, facing, side


def relax_left(arm, facing, side):
    left = PP.ArmPose(arm, 'Left')
    shoulder = arm.matrix_world @ PP.named(arm, 'LeftArm').head
    rest = shoulder + facing * .10 + Vector((0, 0, -.40))
    return left.pose(rest, (facing * .3 + Vector((0, 0, -1))).normalized(), side, .3, 1, pole=-facing + Vector((0, 0, -.5)))


def world(arm, bone, end='head'):
    return arm.matrix_world @ getattr(bone, end)


def hand_frame(arm):
    """Right hand: wrist, forward (wrist to the middle of the index and pinky knuckles), radial (pinky to index
    knuckle) and palm normal (for the right hand radial x forward; ArmPose's forward x across is its back)."""
    named = lambda s: PP.named(arm, s)
    wrist = world(arm, named('RightHand'))
    index, pinky = world(arm, named('RightHandIndex1')), world(arm, named('RightHandPinky1'))
    forward = ((index + pinky) / 2 - wrist).normalized()
    radial = (index - pinky); radial = (radial - forward * radial.dot(forward)).normalized()
    return wrist, forward, radial, radial.cross(forward).normalized()


def finger_points(arm, finger, first):
    """Sample points along a finger from joint `first` to its tip, 4 mm apart."""
    points = []
    for j in range(first, 5):
        bone = PP.named(arm, 'RightHand' + finger + str(j))
        a, b = world(arm, bone), world(arm, bone, 'tail')
        steps = max(1, int((b - a).length / .004))
        points += [a.lerp(b, k / steps) for k in range(steps + 1)]
    return points


def clearance(tree, points, radius):
    """Smallest signed gap (m) between finger capsules and the obstacle surface; negative is penetration."""
    best = 1.
    for p in points:
        hit, normal, _, distance = tree.find_nearest(p, .2)
        if hit is None:
            continue
        signed = distance if (p - hit).dot(normal) >= 0 else -distance
        best = min(best, signed - radius)
    return best


def close_digits(arm, tree, axis_of, digits, limits, gap=.0015, step=3.):
    """Flex each digit joint by joint (proximal first) until its capsule touches the obstacle; stop one step short of
    penetration. `axis_of(finger)` gives the world flexion axis. Returns the final signed gaps per digit."""
    gaps = {}
    for finger in digits:
        for j, limit in zip((1, 2, 3), limits[finger]):
            bone = PP.named(arm, 'RightHand' + finger + str(j))
            bent = 0.
            # Already in the surface: open the joint until clear (at most 30 deg).
            while j == 1 and bent > -30 and clearance(tree, finger_points(arm, finger, j), FINGER_RADIUS) < gap:
                turn(arm, bone, Quaternion(axis_of(finger), math.radians(-step)))
                bent -= step
            if bent < 0:
                continue
            while bent < limit:
                turn(arm, bone, Quaternion(axis_of(finger), math.radians(step)))
                if clearance(tree, finger_points(arm, finger, j), FINGER_RADIUS) < gap:
                    turn(arm, bone, Quaternion(axis_of(finger), math.radians(-step)))
                    break
                bent += step
        gaps[finger] = clearance(tree, finger_points(arm, finger, 1), FINGER_RADIUS)
    return gaps


def settle(arm, meshes, tree, axis_of, digits, step=2., rounds=20):
    """Measure the real skin (the deformed mesh) against the held object and open each digit joint whose skin is inside
    it by `step` degrees until no skin vertex is more than 0.3 mm in; returns the deepest remaining penetration (m)."""
    bones = {('RightHand' + d + str(j)): (d, j) for d in digits for j in (1, 2, 3, 4)}
    worst = 0.
    for _ in range(rounds):
        deps = bpy.context.evaluated_depsgraph_get()
        deepest = {}
        for obj in meshes:
            names = {g.index: g.name.split(':')[-1] for g in obj.vertex_groups}
            if not any(n in bones for n in names.values()):
                continue
            ev = obj.evaluated_get(deps); mesh = ev.to_mesh(); m = ev.matrix_world
            for v, source in zip(mesh.vertices, obj.data.vertices):
                if not source.groups:
                    continue
                lead = names[max(source.groups, key=lambda g: g.weight).group]
                if lead not in bones:
                    continue
                p = m @ v.co
                hit, normal, _, distance = tree.find_nearest(p, .03)
                if hit is not None and (p - hit).dot(normal) < 0:
                    deepest[lead] = max(deepest.get(lead, 0.), distance)
            ev.to_mesh_clear()
        worst = max(deepest.values(), default=0.)
        if worst < .0003:
            break
        for lead, depth in deepest.items():
            if depth < .0003:
                continue
            digit, j = bones[lead]
            joint = PP.named(arm, 'RightHand' + digit + str(min(j, 3)))
            turn(arm, joint, Quaternion(axis_of(digit), math.radians(-step)))
    return worst


def tree_of(objects):
    deps = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for obj in objects:
        ev = obj.evaluated_get(deps); mesh = ev.to_mesh(); m = ev.matrix_world
        base = len(verts)
        verts += [m @ v.co for v in mesh.vertices]
        polys += [[base + i for i in p.vertices] for p in mesh.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def anatomy(arm):
    """Elbow height below the shoulder (m) and wrist bend (deg, forearm axis to the hand's forward)."""
    named = lambda s: PP.named(arm, s)
    shoulder, elbow, wrist = world(arm, named('RightArm')), world(arm, named('RightForeArm')), world(arm, named('RightHand'))
    _, forward, _, _ = hand_frame(arm)
    return dict(elbow_below_shoulder_m=round(shoulder.z - elbow.z, 4),
                wrist_bend_deg=round(math.degrees((wrist - elbow).angle(forward)), 1))


def finish(P, root, arm, state, contact, floor=FADE_FLOOR):
    P.role(root, 'character')
    # A supporting person, not the guide's character: the support opacity on the character layer (no creator here).
    P.ROLE_ALPHA['character'] = P.ROLE_ALPHA['support']
    state['character_fade_floor'] = floor
    contact.update(kind='supporting_person', person='barista (approved 65-bone rig)', source=str(SOURCE.relative_to(SOURCE.parents[3])),
                   opacity=P.ROLE_ALPHA['support'], fade_floor_m=floor)
    state['contacts'].append(contact)
    state['barista'] = dict(root=root, arm=arm, anatomy=[])


def key_bones(arm, frame):
    for bone in arm.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        bone.keyframe_insert('rotation_quaternion', frame=frame); bone.keyframe_insert('location', frame=frame)


def snapshot(arm, names):
    return {n: arm.pose.bones[n].matrix_basis.copy() for n in names}


def restore(arm, saved):
    for n, m in saved.items():
        arm.pose.bones[n].matrix_basis = m.copy()
    bpy.context.view_layer.update()


def digit_names(arm):
    return [b.name for b in arm.pose.bones if b.name.split(':')[-1].startswith('RightHand') and b.name.split(':')[-1] != 'RightHand']


def reach(arm, solver, wrist, forward, radial, pole, anchor, target, rounds=6):
    """Pose the right arm so the hand point `anchor(arm)` lands on `target`, hand oriented by forward/radial."""
    for _ in range(rounds):
        check = solver.pose(wrist, forward, radial, 1, bpy.context.scene.frame_current, pole=pole)
        error = target - anchor(arm)
        if error.length < .0005:
            break
        wrist = wrist + error
    return wrist, check


def add(P, machine, state, gid=None):
    """Place the barista at `machine` (the group p0_scenes.counter returns) holding the milk pitcher by its handle in the
    right hand and swirling it. The guide's hold (HOLDS) = (ahead, right, height): the handle bar centre relative to
    his right shoulder (m, along his facing, to his right, world height). The pitcher stays upright; its handle turns
    so the hand lines up with the forearm seen from above (no sideways wrist bend). Returns the rig root."""
    bpy.context.view_layer.update()
    place = machine.matrix_world
    facing_angle = place.to_euler().z + math.pi / 2 + math.radians(BODY_AWAY_DEG)
    root, arm, facing, side = stand(place @ FEET_LOCAL, facing_angle)
    checks = [relax_left(arm, facing, side)]
    right = -side
    ahead, aside, height = HOLDS.get(gid, PITCHER_HOLD)
    shoulder = world(arm, PP.named(arm, 'RightArm'))
    bar = Vector((shoulder.x, shoulder.y, height)) + facing * ahead + right * aside
    outward_local = Vector((PITCHER_BAR.x - PITCHER_AXIS.x, PITCHER_BAR.y - PITCHER_AXIS.y, 0)).normalized()
    pitcher = P.reused_pourer(True, Vector())
    pitcher['p0_held_by'] = 'barista right hand'
    solver = PP.ArmPose(arm, 'Right')
    mid = lambda a: world(a, PP.named(a, 'RightHandMiddle1'))
    forward = facing.copy()
    for rounds in range(4):
        out = forward.cross(Vector((0, 0, 1))).normalized()     # handle side; the palm faces the pitcher (-out)
        yaw = math.atan2(out.y, out.x) - math.atan2(outward_local.y, outward_local.x)
        pitcher.rotation_euler = (0, 0, yaw)
        pitcher.location = bar - Matrix.Rotation(yaw, 3, 'Z') @ PITCHER_BAR
        bpy.context.view_layer.update()
        # The bar lies across the proximal finger segments: middle knuckle 2 cm behind the bar, beside its outer face.
        target = bar - forward * .020 + out * (PITCHER_BAR_HALF + .012) + Vector((0, 0, .006))
        pole = Vector((0, 0, -1)) * math.cos(math.radians(POLE_OUT_DEG)) + out * math.sin(math.radians(POLE_OUT_DEG))
        wrist, check = reach(arm, solver, target - forward * .085, forward, Vector((0, 0, 1)), pole, mid, target)
        fore = wrist - world(arm, PP.named(arm, 'RightForeArm')); fore.z = 0
        if rounds < 3:
            forward = fore.normalized()
    tree = tree_of(P.members(pitcher))
    _, f, radial, palm = hand_frame(arm)
    gaps = close_digits(arm, tree, lambda finger: f.cross(palm).normalized(), FINGERS,
                        {k: (95, 100, 80) for k in FINGERS})
    # Thumb rests along the top of the handle: lower it from pointing up-forward until it touches.
    for j, d in [(1, f * .5 + Vector((0, 0, .7)) + palm * .4), (2, f * .8 + Vector((0, 0, .45)) + palm * .2), (3, f * .9 + Vector((0, 0, .35)))]:
        PP.orient_bone(arm, PP.named(arm, 'RightHandThumb' + str(j)), d.normalized())
    thumb_axis = lambda finger: f.cross(Vector((0, 0, -1))).normalized()
    gaps.update(close_digits(arm, tree, thumb_axis, ('Thumb',), {'Thumb': (40, 50, 40)}))
    skin = [o for o in root.children_recursive if o.type == 'MESH']
    flex = lambda finger: thumb_axis(finger) if finger == 'Thumb' else f.cross(palm).normalized()
    inside = settle(arm, skin, tree, flex, FINGERS + ('Thumb',))
    grip = snapshot(arm, digit_names(arm))
    hand_bone = PP.named(arm, 'RightHand')
    world_pitcher = pitcher.matrix_world.copy()
    pitcher.parent = arm; pitcher.parent_type = 'BONE'; pitcher.parent_bone = hand_bone.name
    bpy.context.view_layer.update(); pitcher.matrix_world = world_pitcher; bpy.context.view_layer.update()
    checks.append(check)
    record = state
    # Every frame starts from this pose, so the pose is a function of u alone (first frame = last frame).
    base = snapshot(arm, [b.name for b in arm.pose.bones])

    loop = {}

    def action(u):
        frame = bpy.context.scene.frame_current
        phase = u % 1.
        if phase == 0. and loop:
            # The loop's start and end key the very same values, so the target frame repeats bit for bit.
            restore(arm, loop)
        else:
            restore(arm, base)
            a = 2 * math.pi * SWIRL_TURNS * phase
            offset = (forward * (math.cos(a) - 1) + out * math.sin(a)) * SWIRL_RADIUS
            solver.pose(wrist + offset, forward, Vector((0, 0, 1)), 1, frame, pole=pole)
            restore(arm, grip)
            if phase == 0.:
                loop.update(snapshot(arm, [b.name for b in arm.pose.bones]))
        key_bones(arm, frame)
        record['barista']['anatomy'].append(dict(u=round(u, 4), **anatomy(arm)))
    finish(P, root, arm, state, dict(where='behind the counter at the machine working face',
                                     pose='right hand holds the milk pitcher by its handle and swirls it (%d turns, %.0f mm wrist circle); left arm relaxed' % (SWIRL_TURNS, SWIRL_RADIUS * 1000),
                                     face='profile, turned away from the customer side', held='milk pitcher (milk_pitcher/functional)',
                                     grip_gaps_mm={k: round(v * 1000, 1) for k, v in gaps.items()}, grip_skin_inside_mm=round(inside * 1000, 2),
                                     wrist_error_m=max(c['wrist_error_m'] for c in checks), loop_first_equals_last=True))
    state['actions'].append(action)
    state['adaptations'].append('The barista works at the machine behind the counter, face in profile and turned away, swirling the milk pitcher he holds by its handle; strokes fade toward the counter top at the supporting opacity.')
    return root


def legs_to(arm, feet_world, pole):
    """Two-bone leg solve keeping each foot joint on `feet_world[side]` (knees toward `pole`), foot bones kept level."""
    for side, target in feet_world.items():
        up, low, foot = (PP.named(arm, side + n) for n in ('UpLeg', 'Leg', 'Foot'))
        foot_dir = (arm.matrix_world.to_3x3() @ (foot.tail - foot.head)).normalized()
        hip = world(arm, up)
        a = (world(arm, low) - hip).length; b = (world(arm, foot) - world(arm, low)).length
        d = target - hip; dist = min(d.length, (a + b) * .999)
        along = (a * a - b * b + dist * dist) / (2 * dist); height = math.sqrt(max(0., a * a - along * along))
        n = d.normalized(); p = (pole - n * pole.dot(n)).normalized()
        knee = hip + n * along + p * height
        PP.orient_bone(arm, up, knee - hip)
        PP.orient_bone(arm, low, target - knee)
        PP.orient_bone(arm, foot, foot_dir)


def add_serve(P, state, feet, carrier, saucer, cup, release, lens):
    """The barista at `feet` faces the customer (the `lens`) across the counter and serves: leaning in with soft knees,
    face on the lens, his right hand palm down with fingertips on the saucer rim slides it to the landing spot (the
    carrier's own action, earlier in state['actions'], moves it) and lets go at u=`release`. Then he turns
    SERVE_TURN_DEG clockwise seen from above, lowers the hand to his side and walks out of frame to the left."""
    up = Vector((0, 0, 1))
    to_lens = Vector(lens) - Vector(feet); to_lens.z = 0
    angle0 = math.atan2(to_lens.y, to_lens.x)
    root, arm, facing0, side0 = stand(Vector(feet), angle0, lean=0., head_away=0., head_down=0.)
    checks = [relax_left(arm, facing0, side0)]
    rot0 = root.rotation_euler.z
    feet0 = root.location.copy()
    base = snapshot(arm, [b.name for b in arm.pose.bones])
    inv = root.matrix_world.inverted()
    feet_local = {s: inv @ world(arm, PP.named(arm, s + 'Foot')) for s in ('Left', 'Right')}
    hips, head, neck = PP.named(arm, 'Hips'), PP.named(arm, 'Head'), PP.named(arm, 'Neck')
    spine = [(PP.named(arm, n), share) for n, share in [('Spine', .3), ('Spine1', .35), ('Spine2', .35)]]
    walk = Vector((*SERVE_WALK_DIR, 0.)).normalized()

    def body(lean, drop, yaw, offset):
        """Whole-body pose: turned `yaw` deg clockwise, moved by `offset`, hips `drop` m lower on bent knees, trunk
        leaning `lean` deg forward. Returns the current facing."""
        restore(arm, base)
        root.rotation_euler.z = rot0 - math.radians(yaw)
        root.location = feet0 + offset
        bpy.context.view_layer.update()
        facing = Quaternion(up, -math.radians(yaw)) @ facing0
        if drop:
            m = arm.matrix_world @ hips.matrix; m.translation.z -= drop
            hips.matrix = arm.matrix_world.inverted() @ m
            bpy.context.view_layer.update()
            legs_to(arm, {s: root.matrix_world @ p for s, p in feet_local.items()}, facing)
        side = up.cross(facing)
        for bone, share in spine:
            turn(arm, bone, Quaternion(side, math.radians(lean * share)))
        return facing

    def look(weight):
        """Neck and head turn the face onto the lens (weight 1) from its neutral pose (0)."""
        for _ in range(2):
            bpy.context.view_layer.update()
            face = (arm.matrix_world @ head.matrix).to_3x3() @ Vector(root['p0_face_forward_local'])
            eye = arm.matrix_world @ head.matrix @ Vector(root['p0_eye_local'])
            q = face.normalized().rotation_difference((Vector(lens) - eye).normalized())
            for bone, share in [(neck, .4), (head, .6)]:
                turn(arm, bone, Quaternion().slerp(q, weight * share))

    def ramp(x, r=.3):
        x = max(0., min(1., x)); v = 1 / (1 - r)
        if x < r: return v * x * x / (2 * r)
        if x > 1 - r: return 1 - v * (1 - x) ** 2 / (2 * r)
        return v * (x - r / 2)

    solver = PP.ArmPose(arm, 'Right')
    left_solver = PP.ArmPose(arm, 'Left')
    knuckle = lambda r: world(r, PP.named(r, 'RightHandMiddle1'))
    # The hand is set SERVE_SET_AT into the slide in line with the forearm, the middle knuckle at SERVE_KNUCKLE (from the
    # saucer centre toward him, above the counter top); the fingers then close down onto the rim.
    middle = .06 + (release - .06) * SERVE_SET_AT
    for act in list(state['actions']):
        act(middle)
    facing = body(SERVE_LEAN_DEG + SERVE_PUSH_LEAN_DEG * SERVE_SET_AT, SERVE_KNEE_DROP_M, 0., Vector())
    side = up.cross(facing)
    pole = Vector((0, 0, -SERVE_ELBOW_DOWN)) - side * .6 - facing * SERVE_ELBOW_BACK   # elbow out and back, clear of the counter
    bpy.context.view_layer.update()
    centre = carrier.matrix_world.translation.copy()
    toward = -Vector(carrier['p0_slide_direction']); toward.z = 0; toward.normalize()
    local_contact = carrier.matrix_world.inverted() @ (centre + toward * SERVE_KNUCKLE[0] + Vector((0, 0, SERVE_KNUCKLE[1])))
    contact = carrier.matrix_world @ local_contact
    forward = (-toward * math.cos(math.radians(15)) - Vector((0, 0, math.sin(math.radians(15))))).normalized()
    for rounds in range(5):
        flat = Vector((forward.x, forward.y, 0)).normalized()
        radial = up.cross(flat).normalized()              # palm down: the index side on the hand's left
        wrist, check = reach(arm, solver, contact + toward * .09 + Vector((0, 0, .02)), forward, radial, pole, knuckle, contact)
        fore = (wrist - world(arm, PP.named(arm, 'RightForeArm'))).normalized()
        if rounds < 4:
            # In line with the forearm in 3D, dipping at least 15 deg.
            dip = max(math.radians(15), -math.asin(max(-1., min(1., fore.z))))
            h = Vector((fore.x, fore.y, 0)).normalized()
            forward = (h * math.cos(dip) - Vector((0, 0, math.sin(dip)))).normalized()
    surface = [o for o in bpy.context.scene.objects if o.name.startswith('Customer counter top')]
    tree = tree_of(P.members(saucer) + P.members(cup) + surface)
    _, f, radial_now, palm = hand_frame(arm)
    gaps = close_digits(arm, tree, lambda finger: f.cross(palm).normalized(), FINGERS, {k: (45, 60, 40) for k in FINGERS})
    for j, d in [(1, f * .6 + radial_now * .6 - palm * .2), (2, f * .9 + radial_now * .3 - palm * .3), (3, f * .9 + radial_now * .2 - palm * .3)]:
        PP.orient_bone(arm, PP.named(arm, 'RightHandThumb' + str(j)), d.normalized())
    gaps.update(close_digits(arm, tree, lambda finger: f.cross(palm).normalized(), ('Thumb',), {'Thumb': (30, 30, 30)}))
    skin = [o for o in root.children_recursive if o.type == 'MESH']
    inside = settle(arm, skin, tree, lambda finger: f.cross(palm).normalized(), FINGERS + ('Thumb',))
    digits = digit_names(arm)
    grip = snapshot(arm, digits)
    tip_offset = knuckle(arm) - wrist
    checks.append(check)
    for act in list(state['actions']):
        act(1.)                     # the carrier back on its landing spot for whatever is built next
    bpy.context.view_layer.update()
    record = state

    def action(u):
        frame = bpy.context.scene.frame_current
        push = ramp((u - .06) / (release - .06))
        off = ramp((u - release - .02) / (SERVE_WITHDRAW_U - release - .02))      # hand lifts off the saucer
        t = ramp((u - SERVE_TURN_U[0]) / (SERVE_TURN_U[1] - SERVE_TURN_U[0]))     # turn, arm down
        s_up = ramp((u - SERVE_UP_U[0]) / (SERVE_UP_U[1] - SERVE_UP_U[0]))        # straighten up off the counter first
        w = ramp((u - SERVE_WALK_U[0]) / (SERVE_WALK_U[1] - SERVE_WALK_U[0]), .15)      # short start and stop: even pace
        lean = (SERVE_LEAN_DEG + SERVE_PUSH_LEAN_DEG * push * (1 - off)) * (1 - s_up)
        facing = body(lean, SERVE_KNEE_DROP_M * (1 - s_up), SERVE_TURN_DEG * t,
                      -facing0 * SERVE_STEP_BACK_M * s_up + walk * SERVE_WALK_M * w)
        look(1 - t)
        bpy.context.view_layer.update()
        side = up.cross(facing)
        here = carrier.matrix_world @ local_contact
        target = here - tip_offset + toward * .06 * off + Vector((0, 0, .05 * off))
        shoulder = world(arm, PP.named(arm, 'RightArm'))
        hang = shoulder + facing * .08 - side * .06 + Vector((0, 0, -.40))
        hand_pole = Vector((0, 0, -SERVE_ELBOW_DOWN)) - side * .6 - facing * SERVE_ELBOW_BACK
        hang_pole = -facing + Vector((0, 0, -.5))
        # The hand comes in to his chest as he turns, and down to his side once he has straightened up.
        chest = shoulder + facing * .18 + side * .06 + Vector((0, 0, -.02))
        drop = ramp((t - .1) / .6)
        target = target.lerp(chest, s_up).lerp(hang, drop)
        pole_now = hand_pole.lerp(hang_pole, drop)
        solver.pose(target, forward, radial, 1, frame, pole=pole_now)
        if off:
            # Off the saucer the wrist relaxes in line with the forearm, then the hand hangs at his side.
            fore = (target - world(arm, PP.named(arm, 'RightForeArm'))).normalized()
            relaxed = (fore - Vector((0, 0, .15))).normalized()
            fwd = forward.lerp(relaxed, off).lerp((facing * .3 + Vector((0, 0, -1))).normalized(), drop).normalized()
            rad = radial.lerp(up.cross(Vector((relaxed.x, relaxed.y, 0))).normalized(), off).lerp(facing, drop).normalized()
            solver.pose(target, fwd, rad, 1, frame, pole=pole_now)
        # Left hand: palm down just above the counter top beside him while he leans in, then hangs at his side.
        sl = world(arm, PP.named(arm, 'LeftArm'))
        rest_on = Vector((sl.x, sl.y, 0)) + facing * .16 + side * .04 + Vector((0, 0, SERVE_LEFT_REST_Z))
        hang_l = sl + facing * .10 + side * .04 + Vector((0, 0, -.40))
        lift_l = s_up                               # off the counter first, then down to his side
        rest_on += Vector((0, 0, .06 * lift_l))
        drop_l = ramp((t - .05) / .55)             # once he has stepped back from the counter both hands drop as he turns
        left_fwd = (Vector((facing.x, facing.y, 0)) - Vector((0, 0, .05))).normalized().lerp((facing * .3 + Vector((0, 0, -1))).normalized(), drop_l).normalized()
        left_solver.pose(rest_on.lerp(hang_l, drop_l), left_fwd, (-up.cross(facing)).lerp(side, drop_l).normalized(), 1, frame,
                         pole=(side * .8 + Vector((0, 0, -.3)) - facing * .5).lerp(-facing + Vector((0, 0, -.5)), lift_l))
        for name in digits:
            arm.pose.bones[name].matrix_basis = grip[name] if not off else grip[name].lerp(base[name], off)
        bpy.context.view_layer.update()
        key_bones(arm, frame)
        record['barista']['anatomy'].append(dict(u=round(u, 4), **anatomy(arm)))
    finish(P, root, arm, state, dict(where='behind the counter, facing the customer across it',
                                     pose='leans in on soft knees, right hand palm down on the saucer rim slides it to the customer and lets go; turns %.0f deg clockwise (seen from above), lowers the hand and walks %.1f m out to the left' % (SERVE_TURN_DEG, SERVE_WALK_M),
                                     face='toward the lens while serving (owner exception for this shot), away after the turn',
                                     grip_gaps_mm={k: round(v * 1000, 1) for k, v in gaps.items()}, grip_skin_inside_mm=round(inside * 1000, 2),
                                     wrist_error_m=max(c['wrist_error_m'] for c in checks), release_u=release,
                                     turn_u=list(SERVE_TURN_U), walk_u=list(SERVE_WALK_U)),
           floor=SLIDE_FADE_FLOOR)
    state['actions'].append(action)
    state['adaptations'].append('The barista faces the customer across the counter, slides the cup over with his right hand and lets go, then turns away to his right, lowers the hand and walks out of frame to the left.')
    return root
