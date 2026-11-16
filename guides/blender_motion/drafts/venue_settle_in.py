"""Venue review draft (catalog v3, 2026-11-16): settle in at your table. The room_seated_pan_v2 scene and pan with the
approved Tripo takeaway cup instead of the ceramic cup, and the room's window moved so the left pan ends on it.
Reuses room_v2 (seat, pitch, pan easing) and counter_case (library model)."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import SEAT, PITCH, PAN, look, even
from drafts.counter_case import library_model

IDS = ('venue_settle_in',)

# The template pan (30 deg left in 4 s) ends 7 deg further right than its -15 deg, so the counter's espresso machine
# leaves the end frame and the window at 1/3 width stands clear of it (probe 2026-11-16: at -15 the machine covered it).
PAN_END = -8.
# Your cup keeps its template place in the end frame (13 deg left of the heading, 0.47 m ahead of the seat).
CUP = (SEAT.x + .47 * math.tan(math.radians(PAN_END - 13)), .22, .785)
# Window on the same far line and height as room() builds it (y 6, z 1.5), moved from the right (x +1.5, start
# frame) to the left so it sits at about 1/3 width in the end frame (venue D3 end composition, RB31).
WINDOW_END_X = 1. / 3


def window_x(heading, third=WINDOW_END_X, lens=24., y=6.):
    """World x on the far line y for a point at `third` of the frame width at the end heading (deg)."""
    half = math.atan(18 / lens * 9 / 16)
    offset = math.atan((2 * third - 1) * math.tan(half))
    return SEAT.x + (y - SEAT.y) * math.tan(math.radians(heading) + offset)


def build(gid, record, P):
    if gid != 'venue_settle_in':
        return None
    A = P.A
    state = new_state()
    heroes = P.room()
    window = next(o for o in bpy.data.objects if o.name.startswith('Window frame only'))
    window.location.x = window_x(PAN_END)
    A.table((.1, 0, 0), .55)
    cup, _ = library_model(P, 'takeaway_cup', CUP, 'foreground')
    before = set(bpy.data.objects)
    P.counter()
    P.role(A.group('Counter at left of room', before, (-2.5, 2, 0)), 'background')
    state['contacts'].append(dict(kind='seated_pan_to_window', window=window.name, cup=cup.name, cup_supported=True,
                                  support_surface_z=CUP[2]))
    state['adaptations'].append(
        f'room_seated_pan_v2 room and pan (seated lens 115 cm, pitch {PITCH:g} deg, {PAN:g} deg left in 4 s); the takeaway '
        f'cup stands where the ceramic cup stood; the window frame moved on its far line to x {window.location.x:+.2f} m '
        f'so the pan ends on it (no wall drawn).')
    def sample(u, p, t):
        return p, look(p, PAN_END + PAN * (1 - even(u)), PITCH)
    return finish(state, heroes, SEAT, look(SEAT, PAN_END, PITCH), sample)
