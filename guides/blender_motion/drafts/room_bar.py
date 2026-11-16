"""Seated pan from the room to the bar counter along the right side of the room (revision 2026-11-11 r2).

Built from room_v2 (room_seated_pan_v2 layout) plus the approved p0_scenes.counter, as is."""
import math
import bpy
from drafts.common import new_state, finish
from drafts.room_v2 import SEAT, PITCH, look, even

IDS = ('room_bar_pan',)

# Counter footprint centre; turned so its customer edge faces the room (-x) and its length runs along the room (+y).
COUNTER, COUNTER_TURN = (2.55, 4.0, 0), -90.
# Pan: 40 deg right over 5 s, 8.9 deg/s between a 0.5 s ease at each end; ends with the bar in the right part.
PAN, PAN_END, RAMP = 40., 29., .1
# Menu board on the right wall behind the counter (0.70 m behind its back edge at x 3.30), facing the room (-x),
# its panel centre at y BOARD_CENTRE[1] and BOARD_RAISE above the builder's 1.85 m so it clears the machine top.
BOARD_CENTRE, BOARD_RAISE = (4.0, 4.9), .45


def build(gid, record, P):
    A = P.A
    state = new_state()
    heroes = P.room()
    A.table((.1, 0, 0), .55)
    drink, _ = P.cup(-.25, .22, .785, False)
    P.role(drink, 'foreground')
    before = set(bpy.data.objects)
    P.counter(body=True)
    bar = A.group('Bar counter along the right of the room', before, COUNTER)
    bar.rotation_euler.z = math.radians(COUNTER_TURN)
    P.role(bar, 'important_background')
    before = set(bpy.data.objects)
    P.board()
    # The builder draws the panel face at y 1.25 facing -y; turning -90 deg makes it face -x at x +1.25.
    board = A.group('Menu board on the right wall behind the bar', before, (BOARD_CENTRE[0] - 1.25, BOARD_CENTRE[1], BOARD_RAISE))
    board.rotation_euler.z = math.radians(-90)
    P.role(board, 'important_background')
    state['adaptations'].append(
        f'Bar counter along the right side of the room, its customer edge {COUNTER[0] - .15:.2f} m to the right of the seat; '
        f'menu board on the right wall behind the counter, facing the room, centred at x {BOARD_CENTRE[0]:.2f} m, '
        f'y {BOARD_CENTRE[1]:.2f} m, {1.85 + BOARD_RAISE:.2f} m high (no wall drawn); '
        f'seated lens 115 cm, pitch {PITCH:g} deg, pan {PAN:g} deg right from the room to the bar, no tilt.')
    state['contacts'].append(dict(kind='seated_pan_to_bar', counter=bar.name, side='right'))
    def sample(u, p, t):
        return p, look(p, PAN_END - PAN * (1 - even(u, RAMP)), PITCH)
    return finish(state, heroes, SEAT, look(SEAT, PAN_END, PITCH), sample)
