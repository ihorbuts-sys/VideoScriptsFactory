"""Amenity family drafts of the v3 catalog (2026-11-16): a blank amenity sign held in frame."""
import math
from mathutils import Vector
from drafts.common import new_state, finish

IDS = ('amenity_point_hold',)

INCH = .0254
TABLE_TOP = .785
# The p0_scenes.counter card holder, unchanged in size: 0.19 x 0.015 x 0.22 m.
CARD_SIZE = (.19, .015, .22)


def ramp(u, r=.2):
    """Trapezoid velocity: an even pace with short ease-in and ease-out; the peak is 1/(1-r) of the mean."""
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def build(gid, record, P):
    A, G = P.A, P.G
    state = new_state()
    if gid == 'amenity_point_hold':
        # Round table with its near edge at y -0.15; the card stands 8 cm in from that edge, turned 15 deg so it
        # reads as a standing card rather than a frame-parallel rectangle.
        A.table((0, .45, 0), .60)
        centre = Vector((0, -.07, TABLE_TOP + CARD_SIZE[2] / 2))
        card = A.tag(G.block('Amenity card holder', tuple(centre), CARD_SIZE, .008), 'hero',
                     'Blank amenity sign (the approved counter card holder) standing on the table')
        card.rotation_euler.z = math.radians(15)
        # Seated chest height (judgement), 18 in from the card centre at the end (the closest the 0.22 m card fits the
        # hero band at 1x; the request asked about 16 in); the aim sits 2 cm under the centre
        # so the card lands slightly above the frame centre.
        lens_z, distance, push, hold_from = 1.0, 18 * INCH, 2 * INCH, .7
        aim = centre - Vector((0, 0, .02))
        rise = lens_z - aim.z
        position = aim + Vector((0, -math.sqrt(distance ** 2 - rise ** 2), rise))
        state['adaptations'].append('Seated chest height (lens 1.0 m), 1x, 20 in to 18 in from the card in 2.8 s at an even pace, then a still hold; no hands.')

        def sample(u, p, t):
            back = (p - t).normalized() * push * (1 - ramp(min(1., u / hold_from)))
            return p + back, t + back
        return finish(state, [card], position, aim, sample)
    return None
