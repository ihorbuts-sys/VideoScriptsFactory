"""Venue review draft (catalog v3, 2026-11-16; rework owner review 2026-11-17): the order arrives. The
handoff_counter_cup_v2 scene with the approved Tripo takeaway cup: static chest-height phone; the barista's hand comes
from the counter's far side holding the cup round its body (the approved CC0 slide grasp of glass_slide_close, its
wrist, pivot, fade and thenar unchanged, fitted to the takeaway cup's wall and turned to the staff side), sets it at
the customer edge, opens and withdraws. Reuses counter_v2 (timing) and counter_case (library model). Owner review
2026-11-16 r3 ("mirror the hand with a cup, literally"): the hand-and-cup action is mirrored left-right about the
camera's vertical view plane: his right hand (the same grasp on the other CC0 arm) from the screen left, palm on the
cup's left, withdrawing to the top left; camera, counter and timing unchanged."""
import math
import bpy
import numpy as np
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.counter_v2 import TOP, view, window, key
from drafts.counter_case import library_model
import p0_table_compositions as T

IDS = ('venue_order_arrives',)

LAND = (-1.0, -.06, TOP)
START = (-1.0, .40, TOP)
# Palm side of the cup (world degrees from +X): the barista reaches from the far side, his left hand on the cup's right,
# fingers round the near side so their backs and knuckles face the lens (judgement, probes 2026-11-17).
# r3: mirrored about the camera's view plane (VIEW_DEG from +X): r2's -20 deg palm on the left hand becomes
# 2 * VIEW_DEG + 20 = 210 deg on the right hand.
SIDE = 'R'
GRIP_Z = .075   # palm height on the body, about mid-wall (judgement)
OPEN_MM = 14.
# Owner 2026-11-17 wants his forearm to read: the fade starts 9 cm toward the elbow (slide grasp 6 cm), crop 14 cm.
FADE = .09
FOREARM = .14                                        # fingers stop this far off the wall in the open pose
CAM_YAW = -5.   # template 8; 13 deg further right so the back of the hand faces the lens (judgement)
RELEASE, OPEN_END, WITHDRAW = .52, .62, .92
VIEW_DEG = 90. - CAM_YAW            # the camera's horizontal view direction, degrees from +X (counter_v2.view)
PALM_DEG = 2 * VIEW_DEG - (-20.)    # r2 palm side (-20 deg) mirrored


def mirrored(v):
    """Horizontal mirror of world vector `v` about the vertical plane along the camera's view direction."""
    a = math.radians(VIEW_DEG); d = Vector((math.cos(a), math.sin(a), 0.))
    h = Vector((v[0], v[1], 0.))
    m = 2 * h.dot(d) * d - h
    return Vector((m.x, m.y, v[2]))


# r2 withdrawal path (back over the counter and up out of the top right), mirrored to the top left.
WITHDRAW_PATH = mirrored((.30, .40, .35))


def wall_radius(meshes, z, band=.004):
    """Largest horizontal radius of the cup surface in a thin band around height z (cup local, base at 0)."""
    r = 0.
    for obj in meshes:
        for v in obj.data.vertices:
            if abs(v.co.z - z) < band:
                r = max(r, math.hypot(v.co.x, v.co.y))
    return r


def centre_xy(meshes):
    xs = [v.co.x for o in meshes for v in o.data.vertices]; ys = [v.co.y for o in meshes for v in o.data.vertices]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def clear_of(hand, meshes, out, gap=.001):
    """Moves the hand along `out` until no skin vertex is inside the cup and the nearest sits `gap` off its surface;
    returns the shift (metres). The fingertip anchor lands on the surface, so the pad would otherwise sink in."""
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    verts, polys = [], []
    for obj in meshes:
        base = len(verts)
        verts += [obj.matrix_world @ v.co for v in obj.data.vertices]
        polys += [[base + i for i in p.vertices] for p in obj.data.polygons]
    tree = BVHTree.FromPolygons(verts, polys)
    skin = [o for o in hand.children_recursive if o.type == 'MESH']
    shift = 0.
    for _ in range(40):
        bpy.context.view_layer.update()
        worst = gap
        for obj in skin:
            for v in obj.data.vertices:
                p = obj.matrix_world @ v.co
                hit, normal, _, d = tree.find_nearest(p)
                if hit is None or d > .02:
                    continue
                signed = d if (p - hit).dot(normal) >= 0 else -d
                worst = min(worst, signed)
        if worst >= gap:
            break
        step = gap - worst
        hand.location += out * step; shift += step
    return shift


def profile(meshes, band=.004):
    """(heights, radii): the cup's outer radius per height band, a lathe hull of the scan (cup local, base at 0)."""
    co = np.array([tuple(v.co) for o in meshes for v in o.data.vertices])
    top = co[:, 2].max()
    heights = np.arange(0., top + band, band)
    radii = np.array([np.hypot(*co[np.abs(co[:, 2] - h) < band][:, :2].T).max() if (np.abs(co[:, 2] - h) < band).any() else 0.
                      for h in heights])
    # Widest of each band and its neighbours: the scan wall is not a true lathe, so the hull errs outward.
    radii = np.maximum(radii, np.maximum(np.r_[radii[1:], 0.], np.r_[0., radii[:-1]]))
    return heights, radii, top


def grasp(cup, meshes, offset=0.):
    """glass_slide_close's slide grasp (T.SLIDE_GRASP) on the takeaway cup's wall; `offset` (metres) keeps every link
    that far off the wall, which gives the same hand opened."""
    bpy.context.view_layer.update()
    world = cup.matrix_world.copy(); axes = world.to_3x3(); inverse = np.array(world.inverted())
    heights, radii, top = profile(meshes)
    s = T.SLIDE_GRASP

    def clearance(points):
        local = points @ inverse[:3, :3].T + inverse[:3, 3]
        h = local[:, 2]
        depth = np.hypot(local[:, 0], local[:, 1]) - np.interp(h, heights, radii) - offset
        return np.where((h > -.002) & (h < top + .002), depth, 1.)

    a = math.radians(PALM_DEG)
    hand = T.H.wrap(SIDE, world @ Vector((0, 0, GRIP_Z)), axes @ Vector((math.cos(a), math.sin(a), 0)), axes @ Vector((0, 0, 1)),
                    clearance, wrist=s['wrist'], pivot=s['pivot'], fade=FADE, forearm=FOREARM, **s['options'])
    return hand, clearance


def build(gid, record, P):
    if gid != 'venue_order_arrives':
        return None
    state = new_state()
    P.counter(body=True)
    P.light_edge('Served counter corner light', [(-1.39, .12, 1.051), (-1.39, -.148, 1.051), (-.78, -.148, 1.051)], .00065, polyline=True)
    cup, meshes = library_model(P, 'takeaway_cup', LAND, 'hero')
    cx, cy = centre_xy(meshes)
    for obj in meshes:
        for v in obj.data.vertices:
            v.co.x -= cx; v.co.y -= cy
        obj.data.update()
    height = max(v.co.z for o in meshes for v in o.data.vertices)
    state['cup_dims'] = dict(height=height, grip_radius=wall_radius(meshes, GRIP_Z))
    carrier = P.A.empty('Takeaway cup carried to the counter edge', Vector(LAND)); P.attach(cup, carrier)
    bpy.context.view_layer.update()

    # Grip 1 mm further off the hull than the slide grasp's 2 mm: the subdivided skin settles about 1 mm inward.
    hand, clearance = grasp(cup, meshes, .001)
    opened, _ = grasp(cup, meshes, .001 + OPEN_MM / 1000)
    skin = next(o for o in hand.children_recursive if o.type == 'MESH')
    other = next(o for o in opened.children_recursive if o.type == 'MESH')
    bpy.context.view_layer.update()
    assert len(skin.data.vertices) == len(other.data.vertices), 'open pose topology differs'
    # The open pose as a shape key of the grip mesh, in the grip mesh's own frame.
    to_local = skin.matrix_world.inverted() @ other.matrix_world
    skin.shape_key_add(name='Basis')
    key_open = skin.shape_key_add(name='Open hand')
    for k, v in enumerate(other.data.vertices):
        key_open.data[k].co = to_local @ v.co
    for obj in [other] + list(opened.children_recursive) + [opened]:
        if obj.name in bpy.data.objects and obj != other:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.objects.remove(other, do_unlink=True)
    P.A.tag(skin, 'hand', "Barista's right hand from the counter's far side: approved slide grasp round the cup body, mirrored")
    hand['p0_hand'] = True; hand['p0_cropped_grip'] = True; hand['p0_entry_side'] = -1
    hand['p0_grip_style'] = 'cylindrical_power_grasp'

    # Withdraw along the level direction (with a lift) that the open hand sweeps least through the wall.
    bpy.context.view_layer.update()
    rest = np.array([tuple(skin.matrix_world @ (v.co)) for v in skin.data.vertices])
    opened_pts = np.array([tuple(skin.matrix_world @ b.co) for b in key_open.data])

    def swept(direction):
        return max(-min(float(clearance(opened_pts + direction * t).min()), 0.) for t in np.linspace(0, .30, 61))
    candidates = [np.array((math.cos(math.radians(d)) * math.cos(math.radians(e)), math.sin(math.radians(d)) * math.cos(math.radians(e)),
                            math.sin(math.radians(e)))) for d in range(0, 360, 5) for e in (0, 15, 30, 45)]
    candidates = [c for c in candidates if c[1] > -.2]   # never toward the customer
    out = min(candidates, key=lambda c: (round(swept(c) * 1e4), -c[1]))
    state['hand_withdraw'] = dict(direction=[round(float(x), 3) for x in out], sweep_mm=round(swept(out) * 1000, 2),
                                  open_sweep_mm=round(-min(float(clearance(opened_pts).min()), 0.) * 1000, 2),
                                  grip_inside_mm=round(-min(float(clearance(rest).min()), 0.) * 1000, 2))
    P.attach(hand, carrier)
    hand_rest = hand.location.copy()
    offset = mirrored(Vector(START) - Vector(LAND))   # r3: the carry path mirrored too
    out_v = Vector(tuple(out))
    blocks = skin.data.shape_keys.key_blocks

    def action(u):
        carrier.location = Vector(LAND) + offset * (1 - window(u, .06, RELEASE, .25))
        blocks['Open hand'].value = window(u, RELEASE + .01, OPEN_END, .3)
        w = window(u, OPEN_END, WITHDRAW, .3)
        # Clear of the wall first, then back over the counter and up out of the frame's top left (r3 mirror).
        hand.location = hand_rest + out_v * .45 * w + WITHDRAW_PATH * P.smooth((w - .25) / .75)
        blocks['Open hand'].keyframe_insert('value')
        key(carrier, hand)
    state['actions'].append(action)
    state['hand_count'] = 1
    state['contacts'].append(dict(kind='served_counter_takeaway', cup=cup.name, support_surface_z=TOP, cup_supported=True,
                                  grip='approved slide grasp (glass_slide_close), barista right hand round the cup body at %.3f m (r2 left-hand grip mirrored)' % GRIP_Z,
                                  hand_leaves_before_target=True, **state['hand_withdraw']))
    state['adaptations'].append('Phone still at chest height, about 25 degrees down and 20 in from the landing spot; the barista '
                                'carries the takeaway cup in from the far side holding it round its body, sets it at the customer '
                                'edge of the counter, opens his hand and withdraws.')
    aim = Vector((LAND[0], LAND[1], TOP + height * .5))
    end = aim - view(CAM_YAW, 25) * .52
    return finish(state, meshes, end, aim)
