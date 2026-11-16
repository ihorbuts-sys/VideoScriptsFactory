"""First sip, glass only (catalog v3, 2026-11-16): sip_cup_only's static phone and lift-out-of-frame, with the approved
water glass (`geometry.glass`) for the cup and the approved slide grasp of glass_slide_close (variant a, SLIDE_GRASP):
same CC0 wrap, left hand, palm angle, wrist, height, pivot, fade and thenar pad, fitted to this glass's wall."""
import math

import bpy
from mathutils import Vector

from drafts.common import new_state, finish
import p0_table_compositions as T

IDS = ('glass_sip_lift',)

SUPPORT = .785
IN = .0254
# Request: phone static at table height (portrait, resting on its bottom edge: lens about 5.5 in up), about 14 in away.
LENS_HEIGHT = .14
LENS_DISTANCE = 14 * IN
# glass_slide_close's camera sits about 15 degrees right of the glass's -Y side; the approved grasp faces that lens.
AZIMUTH = 15
# Water glass outer wall (height, radius), as built by `geometry.glass`.
WALL = ((0., .0385), (.003, .040), (.122, .040), (.125, .0395))
# Beats on the 5 s move: rest, lift from 1.0 s out of the top of the frame, sip out of frame, set back from 3.5 s.
LIFT = (.20, .46)
SET_BACK = (.70, .94)
# Toward the drinker's mouth (above and behind the phone, the left hand's side) and tipped toward the lips.
PATH = Vector((-.05, -.20, .44))
TILT_DEG = 18
# Owner review 2026-11-17: thumb and hand slightly lower than SLIDE_GRASP; .055 keeps the little finger 3 mm above the
# table, and the 10 cm forearm crop (fade already ends above it) keeps the cut end above the table.
HEIGHT = .055
THUMB_LIFT = .2
FOREARM = .10


def grasp(glass):
    """glass_grasp (p0_table_compositions) with the water glass's wall in place of the cocktail's; palm angle, wrist,
    pivot, fade and thenar unchanged; grip height and thumb lift lowered, forearm crop shortened."""
    import numpy as np
    bpy.context.view_layer.update()
    world = glass.matrix_world.copy()
    axes = world.to_3x3()
    inverse = np.array(world.inverted())
    heights, radii = zip(*WALL)
    s = T.SLIDE_GRASP

    def clearance(points):
        local = points @ inverse[:3, :3].T + inverse[:3, 3]
        h = local[:, 2]
        depth = np.hypot(local[:, 0], local[:, 1]) - np.interp(h, heights, radii)
        return np.where((h > -.002) & (h < WALL[-1][0] + .002), depth, 1.)

    angle = math.radians(s['palm_deg'])
    hand = T.H.wrap('L', world @ Vector((0, 0, HEIGHT)), axes @ Vector((-math.cos(angle), -math.sin(angle), 0)),
                    axes @ Vector((0, 0, 1)), clearance, wrist=s['wrist'], pivot=s['pivot'], fade=s['fade'],
                    thumb_lift=THUMB_LIFT, forearm=FOREARM, **s['options'])
    for mesh in [o for o in hand.children_recursive if o.type == 'MESH']:
        T.A.tag(mesh, 'hand', 'Approved slide grasp on the glass wall: palm on the entry side, fingers round the far side, thumb across the near side')
    hand['p0_hand'] = True
    hand['p0_cropped_grip'] = True
    hand['p0_entry_side'] = -1
    hand['p0_grip_style'] = 'cylindrical_power_grasp'
    return hand


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    A, G = P.A, P.G
    state = new_state()
    A.table((.05, .22, 0), .65)
    window = P.V.window((-.80, 1.55, SUPPORT + .60))
    P.role(window, 'background')
    state['light_position'] = (-.80, 1.55, SUPPORT + .60)

    glass = A.tag(G.glass('Water glass', 0, 0, SUPPORT), 'hero', 'The glass on the table is the target; it leaves and returns to the same spot')
    # Back light from the window: one restrained edge on the window-facing side of the clear wall.
    side = math.radians(150)
    cue = P.light_edge('Glass window-side light', [(.0404*math.cos(side), .0404*math.sin(side), z) for z in (.02, .07, .115)], .00035)
    P.attach(cue, glass)

    hand = grasp(glass)
    P.attach(hand, glass)
    state['hand_count'] = 1
    start = glass.location.copy()

    def action(u):
        out = P.smooth((u - LIFT[0]) / (LIFT[1] - LIFT[0])) * (1 - P.smooth((u - SET_BACK[0]) / (SET_BACK[1] - SET_BACK[0])))
        glass.location = start + PATH * out
        glass.rotation_euler.x = math.radians(TILT_DEG) * P.smooth((out - .5) / .5)
        glass.keyframe_insert('location')
        glass.keyframe_insert('rotation_euler')
    state['actions'].append(action)

    target = Vector((0, 0, SUPPORT + .062))
    a = math.radians(AZIMUTH)
    lens = Vector((LENS_DISTANCE * math.sin(a), -LENS_DISTANCE * math.cos(a), SUPPORT + LENS_HEIGHT))
    state['contacts'].append(dict(kind='glass_lift_out_and_back', glass=glass.name, hand=hand.name, same_spot=True,
                                  support_surface_z=SUPPORT, lens_above_table=LENS_HEIGHT))
    state['adaptations'].append('Phone static in portrait at table height (lens 5.5 in above the top), 14 in from the glass, 1x; '
                                'the left hand in the approved slide grasp lifts the glass up and toward the drinker out of the '
                                'top of the frame, holds for the sip and sets it back on the same spot.')
    return finish(state, [glass], lens, target)
