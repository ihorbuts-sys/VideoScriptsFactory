"""Face-free verdict draft (catalog v3, 2026-11-16): a seated push-in over the finished example plate."""
import math
import bpy
from mathutils import Vector, Matrix
from drafts.common import new_state, finish
from drafts.plates_v2 import window

IDS = ('verdict_plate_after_push',)

PLATE_Z = .785
# Top surface of assets.plate, (radius, height) from the rim inward.
PLATE_TOP = [(.151, .029), (.139, .030), (.115, .015), (.09, .009), (0, .009)]


def plate_top(r):
    if r >= PLATE_TOP[0][0]:
        return None
    for (r0, z0), (r1, z1) in zip(PLATE_TOP, PLATE_TOP[1:]):
        if r1 <= r <= r0:
            return z1 + (z0 - z1) * (r - r1) / (r0 - r1)
    return PLATE_TOP[-1][1]


def finished_pasta(P, position=(0, 0, PLATE_Z)):
    """The example pasta plate after eating: an empty well with a three-streak sauce trace, a few crumbs and one short noodle end."""
    A, G = P.A, P.G
    before = set(bpy.data.objects)
    A.plate((0, 0, 0), role='hero')
    floor = .009
    # A fork-dragged swipe: three thin flattened streaks of unequal length along one curve.
    for lane, (offset, first, last) in enumerate([(-.007, .05, .80), (0, 0, 1.0), (.007, .15, .90)]):
        points = []
        for k in range(17):
            a = math.radians(205 + 95 * (first + (last - first) * k / 16))
            r = .058 + offset + .004 * math.sin(k / 16 * math.pi * 2)
            points.append((.010 + r * math.cos(a), .010 + r * math.sin(a), 0))
        smear = G.tube(f'Sauce trace streak {lane}', points, .0022)
        smear.scale.z = .4; smear.location.z = floor + .0010
        A.tag(smear, 'hero', 'A thin sauce trace left in the well shows the dish was eaten')
    for k, (x, y, s) in enumerate([(.030, -.040, .0050), (.046, -.022, .0038), (-.050, .028, .0045), (-.036, .050, .0034),
                                   (.010, .062, .0040), (.064, .030, .0032), (-.010, -.058, .0036)]):
        crumb = A.ellipsoid('Crumb', (x, y, floor + s * .55), (s, s * .8, s * .55), 'hero', 'A few crumbs left on the empty plate')
        crumb.rotation_euler.z = k * 1.3
    end = [(-.030 + .028 * k / 8, -.004 + .010 * math.sin(k / 8 * math.pi), floor + .004) for k in range(9)]
    A.tag(G.tube('Leftover noodle end', end, .0035), 'hero', 'One short noodle end left behind')
    return A.group('Finished pasta plate', before, position, 'hero', 'The finished plate is the verdict subject')


def resting_fork(P, angle, offset):
    """The approved fork laid across the plate along `angle`, handle on the far rim, tines in the well, clear of the plate."""
    A = P.A
    fork = A.fork((0, 0, 0))
    bpy.context.view_layer.update()
    mesh = next(o for o in fork.children_recursive if o.type == 'MESH')
    local = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
    d = Vector((math.cos(angle), math.sin(angle), 0)); n = Vector((-d.y, d.x, 0))
    centre = n * offset - d * .008
    best = None
    # Pitch about the plate chord: the handle end (local -Y) rests on the rim, the tines lie lower in the well.
    for pitch in [math.radians(a / 2) for a in range(0, 30)]:
        rot = Matrix.Rotation(angle - math.pi / 2, 3, 'Z') @ Matrix.Rotation(-pitch, 3, 'X')
        world = [rot @ p + centre for p in local]
        gaps = []
        for p in world:
            top = plate_top(math.hypot(p.x, p.y))
            gaps.append(p.z - (top if top is not None else 0))
        # The stamped body is solidified 2.2 mm about its outline: half of it lies below these vertices.
        lift = .0008 + .0011 - min(gaps)
        resting = sorted(g + lift for g in gaps)
        # Prefer the pitch that leaves both ends closest to their support (a real resting fork touches at two places).
        score = resting[len(resting) // 20]
        if best is None or score < best[0]:
            best = (score, pitch, lift)
    _, pitch, lift = best
    fork.rotation_euler = (-pitch, 0, angle - math.pi / 2)
    fork.location = (centre.x, centre.y, PLATE_Z + lift)
    return fork, math.degrees(pitch)


def build(gid, record, P):
    A, V = P.A, P.V
    state = new_state()
    A.table((.22, .18, 0), .70)
    plate = finished_pasta(P)
    # Handle toward the lower right on the rim, tines toward the upper left: the usual "finished" rest across the plate.
    fork, pitch = resting_fork(P, math.radians(125), .012)
    P.role(fork, 'support')
    P.cup(.20, .24, .785, False)
    P.role(V.chair((0, 1.0, 0)), 'background')
    state['triangle_points'] = [Vector((0, 0, .80)), Vector((.20, .24, .90)), Vector((.07, -.05, .812))]
    state['adaptations'].append(f'Finished state of the example pasta plate (this guide only): empty well, a three-streak sauce trace, seven crumbs, one noodle end; the approved fork rests across the plate at {pitch:.1f} degrees, handle on the near-right rim.')
    state['adaptations'].append('Seated, lens at chest height: a straight 20 cm (8 in) push along the view line from 61 cm (24 in) to 41 cm (16 in), a 0.5 s hold before it, an even pace.')
    aim = Vector((0, 0, .80))
    elevation, pitch_down = math.radians(30), math.radians(34)
    end_distance = .41
    position = aim + end_distance * Vector((0, -math.cos(elevation), math.sin(elevation)))
    target = position + Vector((0, math.cos(pitch_down), -math.sin(pitch_down))) * end_distance

    def sample(u, p, t):
        back = (p - aim).normalized() * .20 * (1 - window(u, .10, 1.0, .15))
        return p + back, t + back
    return finish(state, P.members(plate), position, target, sample)
