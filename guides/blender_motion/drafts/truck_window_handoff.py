"""Truck window hand-off (catalog v3, 2026-11-16): the approved food truck turned as in truck_across_street, window to
the lens; static phone at standing eye level on the window ledge. Owner review 2026-11-17: the cook gives the order.
The approved barista rig inside the truck, in the serve pose of counter_hand_receive (barista.add_serve), leans over
the sill and slides the approved paper-lined tray with the closed paper wrap onto the ledge toward the lens with his
own right hand, lets go, turns away and walks out to the left. Stray dots removed per guide (drafts.truck_cook)."""
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from drafts.common import new_state, finish
from drafts.counter_v2 import window, key
from drafts.truck_across_street import food_truck, EYE

IDS = ('truck_window_handoff',)

TRAY_X = .65                # service window centre in the turned cache (truck_window_line probe)
TRAY_DEPTH = .27            # assets.paper_tray default (0.36 x 0.27 m), short side across the sill
# Tray centre y: the landing keeps the back rim on the sill crest and the front over the ledge edge (y -1.14). r2: the
# start moved from y -0.955 (6.4 deg, on the crest) to y -0.975, where the tray already rests at the landing tilt
# (11.7 deg): no tilt snap mid-slide and the cook's fixed hand shape stays on the rim; the slide is 4.5 in (was 5.3).
START_Y, LAND_Y = -.975, -1.09
# r2: the serve pose's own clock (counter_hand_receive releases at u 0.50; the pose straightens up from u 0.52, so the
# v1 release at 0.55 dragged the gripping hand back over the rim).
# r3 (owner review 2026-11-16 "slide the order slightly faster"): the slide ends at u 0.37 instead of 0.50 (1.55 s,
# was 2.2 s: 30% shorter); the serve pose's after-release clock moves 0.06 earlier with it (not the full 0.13), so the
# hand lifts off the rim for 0.35 s before he straightens up (r2 had 0.1 s and one frame of 2.4 mm finger dip into the rim).
RELEASE = .37
SERVE_SHIFT_U = -.06
# The cook (barista.add_serve): feet behind the tray's landing in the recess (template 0.12 m right, 0.68 m back; here
# 0.55 m back so his back clears the inner counter at y -0.35); counter_v2 top for his floor height. After the release
# he steps back 4 cm (the recess is shallow) and walks out along the window to the left instead of the template's
# diagonal, which would cross the inner counter (judgement).
TEMPLATE_TOP = 1.05
COOK_FEET = (.12, .55)
COOK_STEP_BACK_M = .04
COOK_WALK_DIR = (-1., 0.)
# The template walks 1.35 m in its 3 s guide (1.1 m/s); over this 5 s guide the same share of the move needs 2.2 m for
# the same pace (owner 0.8-1.2 m/s). He is out of the window by x -0.55 m; the rest is behind the truck wall.
COOK_WALK_M = 2.2
# The truck's sill hump stands above the template counter top where his left hand rests, and the tray tilts between
# start and landing: the left rest 3 cm higher and the right middle knuckle 5 mm higher keep the skin out of the sill
# and the tray rim (r2 depth check; judgement).
COOK_LEFT_LIFT = .03
COOK_KNUCKLE_LIFT = .005
WRAP_LOCAL = (.035, -.012)
WRAP_TURN_DEG = 12.
# Camera: standing eye level (truck_across_street EYE), 0.60 m in front of the landing in plan, 8 deg yaw as the template.
CAM_PLAN, CAM_YAW = .60, 8.


def truck_tree(meshes):
    bpy.context.view_layer.update()
    verts, polys = [], []
    for obj in meshes:
        base = len(verts)
        verts += [obj.matrix_world @ v.co for v in obj.data.vertices]
        polys += [[base + i for i in p.vertices] for p in obj.data.polygons]
    return BVHTree.FromPolygons(verts, polys)


def sill_profile(tree, x0, x1, y0, y1, step=.005):
    """Highest truck surface under the tray's width per y (downward rays from inside the window opening)."""
    profile = []
    n = int(round((y1 - y0) / step))
    for i in range(n + 1):
        y = y0 + i * step
        best = None
        for k in range(9):
            x = x0 + (x1 - x0) * k / 8
            hit = tree.ray_cast(Vector((x, y, 1.60)), Vector((0, 0, -1)), 1.2)[0]
            if hit is not None and (best is None or hit.z > best):
                best = hit.z
        if best is not None:
            profile.append((y, best))
    return profile


def rest(profile, yc, depth=TRAY_DEPTH):
    """Rigid flat base resting on the profile: the upper convex hull segment under the centre (z at centre, slope)."""
    pts = [p for p in profile if abs(p[0] - yc) <= depth / 2]
    hull = []
    for p in pts:
        while len(hull) >= 2 and (hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1]) - (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0]) >= 0:
            hull.pop()
        hull.append(p)
    for a, b in zip(hull, hull[1:]):
        if a[0] <= yc <= b[0]:
            m = (b[1] - a[1]) / (b[0] - a[0])
            return a[1] + m * (yc - a[0]), m, (a, b)
    raise ValueError('Tray centre is outside its support at y %.3f' % yc)


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    import assets
    A = P.A
    state = new_state()
    truck = food_truck(P)
    for obj in truck:
        A.tag(obj, 'support', 'The approved food truck, window ledge to the lens: the place of the hand-off')
    tree = truck_tree(truck)
    profile = sill_profile(tree, TRAY_X - .18, TRAY_X + .18, -1.40, -.60)

    def pose(yc):
        z, m, contacts = rest(profile, yc)
        return Vector((TRAY_X, yc, z + .0006)), math.atan(m), contacts

    land, land_tilt, land_contacts = pose(LAND_Y)
    start, start_tilt, start_contacts = pose(START_Y)
    carrier = A.empty('Paper tray slide on the truck window ledge', land)
    carrier.rotation_euler.x = land_tilt
    tray = assets.paper_tray(role='hero')
    wrap = assets.paper_wrap(role='hero')
    tray.parent = carrier; tray.location = (0, 0, 0)
    wrap.parent = carrier; wrap.location = (WRAP_LOCAL[0], WRAP_LOCAL[1], .0056)
    wrap.rotation_euler.z = math.radians(WRAP_TURN_DEG)
    bpy.context.view_layer.update()
    hero = [o for o in tray.children_recursive + wrap.children_recursive if o.type == 'MESH']

    aim = land + Vector((0, 0, .03))
    yaw = math.radians(CAM_YAW)
    lens = Vector((land.x - CAM_PLAN * math.sin(yaw), land.y - CAM_PLAN * math.cos(yaw), EYE))
    carrier['p0_slide_direction'] = list((land - start).normalized())

    def slide(u):
        s = window(u, .06, RELEASE, .25)
        p, tilt, _ = pose(START_Y + (LAND_Y - START_Y) * s)
        carrier.location = p; carrier.rotation_euler.x = tilt
        key(carrier)
    state['actions'].append(slide)
    # Owner review 2026-11-17: the cook gives the order. The approved serve pose of counter_hand_receive (barista.add_serve)
    # with the template's proportions: his floor sits as far under the tray's landing as the template floor under its
    # counter top; the template's absolute heights, walk and step move with it, in memory for this guide only.
    import barista
    floor = land.z - TEMPLATE_TOP
    barista.SERVE_LEFT_REST_Z += floor + COOK_LEFT_LIFT
    barista.SERVE_KNUCKLE = (barista.SERVE_KNUCKLE[0], barista.SERVE_KNUCKLE[1] + COOK_KNUCKLE_LIFT)
    barista.SERVE_WALK_DIR = COOK_WALK_DIR
    barista.SERVE_STEP_BACK_M = COOK_STEP_BACK_M
    barista.SERVE_WALK_M = COOK_WALK_M
    barista.SERVE_WITHDRAW_U += SERVE_SHIFT_U
    barista.SERVE_UP_U = tuple(u + SERVE_SHIFT_U for u in barista.SERVE_UP_U)
    barista.SERVE_TURN_U = tuple(u + SERVE_SHIFT_U for u in barista.SERVE_TURN_U)
    barista.SERVE_WALK_U = tuple(u + SERVE_SHIFT_U for u in barista.SERVE_WALK_U)
    feet = Vector((TRAY_X + COOK_FEET[0], LAND_Y + COOK_FEET[1], floor))
    from drafts.truck_cook import install_stroke_treatment
    install_stroke_treatment(truck)
    barista.add_serve(P, state, feet, carrier, tray, wrap, RELEASE, lens)
    state['character_fade_floor'] = barista.SLIDE_FADE_FLOOR + floor
    state['contacts'][-1].update(where='inside the food truck, behind the service window, leaning over the sill',
                                 template_pose='counter_hand_receive serve (barista.add_serve)', feet_world=[round(c, 3) for c in feet],
                                 fade_floor_m=round(state['character_fade_floor'], 3), walk_dir=list(COOK_WALK_DIR), walk_m=COOK_WALK_M,
                                 step_back_m=COOK_STEP_BACK_M)
    state['hand_count'] = 2
    state['tray_poses'] = dict(start=[list(start), math.degrees(start_tilt), start_contacts],
                               land=[list(land), math.degrees(land_tilt), land_contacts])
    state['clearance_meshes'] = dict(tray=hero, truck=truck)
    state['contacts'].append(dict(kind='truck_window_tray_slide', tray_supported=True, support='truck window sill crest and ledge',
                                  land_tilt_deg=round(math.degrees(land_tilt), 1),
                                  grip='the cook\'s own right hand, approved serve pose (palm down, fingers closed onto the tray back rim)',
                                  hand_leaves_before_target=False, short_stroke_filter_px=12))
    state['adaptations'].append(
        f'Phone still at standing eye level (lens {EYE} m), about {CAM_PLAN / .0254:.0f} in in front of the window ledge, '
        'pitched down onto it; the cook inside the truck, facing the lens, leans over the sill and slides the paper-lined '
        'tray with the wrapped handheld onto the ledge toward the lens, lets go, turns away and walks out of the window '
        'to the left.')
    return finish(state, hero, lens, aim)
