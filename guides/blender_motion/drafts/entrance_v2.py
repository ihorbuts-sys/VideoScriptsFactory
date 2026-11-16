"""Entrance drafts after the 2026-11-10 audit: walk-in, sign tilt, friend-filmed walk-in (A4)."""
import math
import bpy
import numpy as np
from mathutils import Vector, Quaternion
from drafts.common import new_state, finish

IDS = ('entrance_walk_in_v2', 'entrance_sign_tilt_v2', 'entrance_friend_static')

CHEST = 1.30
ARM_SWING = 10.         # shoulder swing each way, deg: a slow walk swings the arms slightly (judgement, below the ~15-20 deg of a brisk walk)
ELBOW_BEND = (8., 12.)  # extra elbow flexion over the source pose, deg: always, and added on the forward swing (judgement)
WALK_FADE_FLOOR = .82   # strokes fade in over 22 cm above this: arms drawn to the wrists (hands .88 m), the static legs hidden
STEP = .60              # step length at about 1 m/s, m; one arm cycle is two steps (judgement)
THRESHOLD_Y = 0.        # door jambs (venue_assets.door): the walker's strokes start to fade here
FADE_DEPTH = 1.5        # owner: fade over the next 1-2 m inside; gone 1.5 m past the threshold
INSIDE_Y = 2.1          # she walks on to here, so her back has passed the fade before the final hold


def facade(P, open_angle=0, hanging=False, welcome=True):
    door, hinge = P.V.door(open_angle=open_angle)
    P.entry_sign(hanging)
    P.entry_furnishings()
    if welcome:
        P.facade_ground_and_welcome()
    P.V.pendant((0, 1.5, 2.55))
    return door


def walk_in(P, state):
    door = facade(P)
    P.role(door, 'support')
    handle = next(o for o in P.members(door) if o.name.startswith('Door pull handle'))
    P.A.tag(handle, 'hero', 'Door handle within reach is the cut point; the door fills the frame around it')
    # The phone keeps its chest-height, slightly lowered aim while walking; only the position moves.
    end = Vector((0, -1.5, CHEST))
    aim = Vector((0, 0, 1.20))
    walk = 3.0

    def sample(u, p, t):
        offset = Vector((0, -walk * (1 - u), 0))
        return p + offset, t + offset
    state['adaptations'].append('Constant 0.61 m/s walk from 4.5 m to 1.5 m at chest height; the phone does not re-aim.')
    return finish(state, [handle], end, aim, sample)


def sign_tilt(P, state):
    door = facade(P, hanging=True)
    P.role(door, 'hero')
    tilt = math.radians(20)
    end = Vector((0, -5.0, CHEST))
    aim = end + Vector((0, math.cos(math.radians(3)), -math.sin(math.radians(3)))) * 5.0

    def sample(u, p, t):
        d = t - p
        length = d.length
        flat = Vector((d.x, d.y, 0)).normalized()
        pitch = math.asin(d.z / length) + tilt * (1 - cubic(u))
        return p, p + (flat * math.cos(pitch) + Vector((0, 0, math.sin(pitch)))) * length
    state['adaptations'].append('Standing still 5 m out at chest height; one 20 degree tilt from the sign to the door.')
    return finish(state, P.members(door), end, aim, sample)


def cubic(u):
    u = max(0., min(1., u))
    return u * u * (3 - 2 * u)


def bezier(s, c, e, t):
    return s * (1 - t) ** 2 + c * 2 * t * (1 - t) + e * t * t


def friend_static(P, record):
    import p0_people as people
    facade(P, open_angle=90)
    root, arm, face = people.load_creator(P)
    # Seen from behind the eye marks would draw through the hair; they stay in the scene, out of the line art.
    for obj in P.members(root):
        if obj.get('p0_face_feature') and not obj.get('p0_framing_mask'):
            obj.lineart.usage = 'EXCLUDE'
    state = dict(hero=face, actions=[], contacts=[], adaptations=[], camera_height_support=0., hand_count=2,
                 silhouettes=0, detailed_people=1, framing_masks=face, character_root=root,
                 preview_mirrored=False, lens_mm=24, performance_checks=[],
                 character_fade_floor=WALK_FADE_FLOOR)
    start, bend, stop = Vector((-1.8, -1.9, 0)), Vector((0, -1.8, 0)), Vector((0, INSIDE_Y, 0))
    # Arc-length table so the walk is a constant pace along the curve.
    steps = [bezier(start, bend, stop, k / 400) for k in range(401)]
    lengths = [0.]
    for a, b in zip(steps, steps[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    empty = .05
    steps_taken = max(2, round(total / STEP))
    named = people.named
    swing_bones = {side: (named(arm, side + 'Arm'), named(arm, side + 'ForeArm')) for side in ('Left', 'Right')}
    rest_dirs = {b.name: (arm.matrix_world.to_3x3() @ (b.tail - b.head)).normalized() for pair in swing_bones.values() for b in pair}
    previous = {}

    def swing_arms(walked):
        """Arms swing opposite each other about the shoulders, elbows slightly bent; a whole number of steps ends at rest."""
        phase = math.sin(math.pi * walked / (total / steps_taken))
        turn = root.matrix_world.to_3x3().normalized()
        lateral = turn @ Vector((1, 0, 0))          # the creator faces -Y; + angle swings the arm forward
        # From the source pose every frame: orient_bone keeps the current roll, so equal poses must start equal.
        for upper_fore in swing_bones.values():
            for bone in upper_fore:
                bone.matrix_basis.identity()
        bpy.context.view_layer.update()
        for side, sign in (('Left', 1), ('Right', -1)):
            upper, fore = swing_bones[side]
            forward = sign * phase
            shoulder = Quaternion(lateral, -math.radians(ARM_SWING * forward))
            elbow = Quaternion(lateral, -math.radians(ELBOW_BEND[0] + ELBOW_BEND[1] * max(0., forward)))
            people.orient_bone(arm, upper, shoulder @ (turn @ rest_dirs[upper.name]))
            people.orient_bone(arm, fore, shoulder @ elbow @ (turn @ rest_dirs[fore.name]))
        for upper_fore in swing_bones.values():
            for bone in upper_fore:
                bone.rotation_mode = 'QUATERNION'
                if bone.name in previous and previous[bone.name].dot(bone.rotation_quaternion) < 0:
                    bone.rotation_quaternion.negate()
                previous[bone.name] = bone.rotation_quaternion.copy()
                bone.keyframe_insert('rotation_quaternion', frame=bpy.context.scene.frame_current)
        return phase

    def at(distance):
        for k in range(400):
            if lengths[k + 1] >= distance:
                f = (distance - lengths[k]) / max(1e-9, lengths[k + 1] - lengths[k])
                position = steps[k].lerp(steps[k + 1], f)
                tangent = steps[k + 1] - steps[k]
                return position, math.atan2(tangent.x, -tangent.y)
        tangent = steps[-1] - steps[-2]
        return steps[-1], math.atan2(tangent.x, -tangent.y)

    def action(u):
        walked = max(0., (u - empty) / (1 - empty)) * total
        position, yaw = at(walked)
        root.location = position
        root.rotation_euler = (0, 0, yaw)
        bpy.context.view_layer.update()
        phase = swing_arms(walked)
        state['performance_checks'].append(dict(u=u, frame=bpy.context.scene.frame_current,
                                                root=[round(v, 4) for v in position], yaw_degrees=round(math.degrees(yaw), 2),
                                                arm_swing_degrees=round(ARM_SWING * phase, 2)))
    state['actions'] = [action]
    fade_inside(state)
    state['walk_length_m'] = total
    state['walk_steps'] = steps_taken
    state['contacts'] = [dict(kind='canonical_character', source='model_refferences/creator/lineart/asset.blend',
                              skeleton_preserved=True, anatomical_hands=2, facial_animation=False, pose='source rest pose, unchanged'),
                         dict(kind='camera_mode', camera=record['camera'], preview_mirrored=False,
                              intent='Friend holds the rear camera still at chest height; the creator walks in')]
    state['adaptations'] = [
        f'Canonical creator in its source standing pose, placed and turned along the path; the arms swing {ARM_SWING:.0f} deg each way, '
        f'opposite each other, elbows bent {ELBOW_BEND[0]:.0f}-{sum(ELBOW_BEND):.0f} deg more, {steps_taken} steps; no leg cycle (the fade hides the legs).',
        f'The character fade starts at {WALK_FADE_FLOOR} m, so the swinging arms are drawn to the wrists and the legs stay hidden.',
        'Door open 90 degrees so the creator passes the threshold; the door is support, the head is the framing target.',
        f'She walks on {INSIDE_Y} m inside; past the threshold her strokes fade out over {FADE_DEPTH} m, so the loop opens and ends on the empty door.',
    ]
    return finish(state, face, (0, -3.5, CHEST), (0, 0, CHEST))


def fade_inside(state):
    """Fades the character strokes from the threshold to FADE_DEPTH inside (per point, by world depth)."""
    def opacity(points):
        fade = np.clip((points[:, 1] - THRESHOLD_Y) / FADE_DEPTH, 0, 1)
        return 1 - fade * fade * (3 - 2 * fade)
    state['character_stroke_opacity'] = opacity


def build(gid, record, P):
    if gid == 'entrance_friend_static':
        return friend_static(P, record)
    state = new_state()
    if gid == 'entrance_walk_in_v2':
        return walk_in(P, state)
    return sign_tilt(P, state)
