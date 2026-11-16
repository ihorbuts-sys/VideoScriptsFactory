"""Venue review draft (catalog v3, 2026-11-16): the order is placed; the counter edge with the card holder and the
working barista behind it, a slow chest-height push-in. The counter_edge_to_pass_v2 scene without the pass cup."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish

IDS = ('venue_order_placed',)

INCH = .0254
TOP = 1.05
TEMPLATE = 'counter_edge_to_pass_v2'
# The approved card holder (p0_scenes.counter, 0.19 x 0.015 x 0.22 m) moved from x -0.70 to the stretch in front of the
# barista's left, 6 in in from the customer edge (y -0.15), so the push can hold both (judgement).
CARD_XY = (-.30, .0)
CARD_TURN_DEG = -12.        # faces the customer standing slightly left of it (judgement)
# Standing chest height (framing.md walk height about 130 cm), about 20 in back from the counter edge (judgement).
LENS_Z = 1.30
PUSH = 3 * INCH             # request: slow 3 in push-in
YAW_DEG, PITCH_DEG = 17., 10.
FRAME_RIGHT_DEG = 9.       # the view turns right of the card: card in the left third, barista in the right (judgement)


def ramp(u, r=.2):
    """Trapezoid velocity: an even pace with short ease-in and ease-out; the peak is 1/(1-r) of the mean."""
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def view(yaw, pitch):
    """Unit view direction: yaw from +Y toward +X, pitch below horizontal (degrees)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p)))


def build(gid, record, P):
    if gid != 'venue_order_placed':
        return None
    import barista
    state = new_state()
    top, machine = P.counter()
    menu, _ = P.board()
    P.role(menu, 'background')
    for x in [-.6, -.4, -.2]:
        P.cup(x, .60, TOP, False)
    for obj in bpy.context.scene.objects:
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    # The template's barista pose, hold included (no pass cup here, so the approved hold stays valid).
    barista.add(P, machine, state, TEMPLATE)
    card = next(o for o in bpy.context.scene.objects if o.name.startswith('Counter card holder'))
    card.location = Vector((CARD_XY[0], CARD_XY[1], card.location.z))
    card.rotation_euler.z = math.radians(CARD_TURN_DEG)
    P.A.tag(card, 'hero', 'The order card holder at the counter edge: the order is placed')
    P.light_edge('Counter surface reflected light', [(CARD_XY[0] - .55, -.07, TOP + .001), (CARD_XY[0] - .12, -.07, TOP + .001)], .00055)
    bpy.context.view_layer.update()
    aim_point = card.location + Vector((0, 0, .01))
    d = view(YAW_DEG, PITCH_DEG)
    # Lens at LENS_Z on the line through the card along the view direction.
    s = (LENS_Z - aim_point.z) / -d.z
    end = aim_point - d * s
    aim = end + view(YAW_DEG + FRAME_RIGHT_DEG, PITCH_DEG)
    state['adaptations'].append(f'Portrait, standing chest height (lens {LENS_Z:.2f} m, {(LENS_Z - TOP) / INCH:.0f} in above the counter), 1x, {PITCH_DEG:.0f} deg down, '
                                f'a 3 in straight push toward the card holder in {record["durationSec"]} s at an even pace; the barista keeps working behind the counter.')

    def sample(u, p, t):
        back = (p - t).normalized() * PUSH * (1 - ramp(u))
        return p + back, t + back
    return finish(state, [card], end, aim, sample)
