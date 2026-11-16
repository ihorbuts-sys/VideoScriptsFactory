"""Experience floor pan draft (catalog v3, 2026-11-16): standing chest-height pan right across a generic training floor.

Built from room_bar (room_seated_pan_v2 pan helpers) with approved objects only: the Tripo dumbbell (owner 2026-11-16,
dot cleanup in memory), the window frame, and the long tabletop block resized as a generic bench stand-in."""
import math
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import look, even
from drafts.counter_case import library_model

IDS = ('experience_floor_pan',)

# Standing lens at chest height (walk height, RB23 RB25 RB31), fixed position.
LENS = Vector((0, 0, 1.30))
# Pan 40 deg right in 5 s, 8.9 deg/s between a 0.5 s ease at each end (RB29 RB30 8-10 deg/s), as room_bar_pan.
PAN, PAN_END, PITCH, RAMP = 40., 15., 26., .1
# Dumbbells on the floor lightest to heaviest like a gym rack (owner 2026-11-16): four pairs of uniform scaled copies
# of the approved model, 1x to 1.8x; each turned 90 deg so its handle points toward the camera, the two of a pair the
# same scale side by side PAIR_GAP clear, pairs GAP clear, the row centred on the end-of-pan view line.
DUMBBELL_WIDTH, SCALES, PAIR_GAP, GAP, TURN = .124, [1.8 ** (i / 3) for i in range(4)], .04, .15, 90.
ROW_Y = 2.6
# Bench stand-ins: the long tabletop block (same block, 0.025 bevel) at bench size, solid down to the floor, top 0.45 m;
# the right one sits 0.2 m further back than r1 so the larger dumbbells stay clear of it.
BENCHES, BENCH_SIZE, BENCH_TOP = [(-1.35, 2.9), (2.0, 3.4)], (.36, 1.20, .45), .45
WINDOW = (-1.4, 5.6, 1.5)


def row_x():
    """(centre x, scale) of each dumbbell, the row of pairs centred where the end-of-pan view line crosses ROW_Y."""
    widths = [DUMBBELL_WIDTH * scale for scale in SCALES]
    total = sum(2 * w + PAIR_GAP for w in widths) + GAP * (len(widths) - 1)
    edge = ROW_Y * math.tan(math.radians(PAN_END)) - total / 2
    out = []
    for width, scale in zip(widths, SCALES):
        out += [(edge + width / 2, scale), (edge + width * 1.5 + PAIR_GAP, scale)]
        edge += 2 * width + PAIR_GAP + GAP
    return out


def build(gid, record, P):
    A, G, V = P.A, P.G, P.V
    state = new_state()
    heroes = []
    for x, scale in row_x():
        root, meshes = library_model(P, 'dumbbell', (x, ROW_Y, 0), 'hero', TURN)
        root.scale = (scale,) * 3
        heroes += meshes
    for x, y in BENCHES:
        A.tag(G.block('Bench stand-in block (long tabletop block)', (x, y, BENCH_TOP - BENCH_SIZE[2] / 2), BENCH_SIZE, .025),
              'support', 'Generic bench: the approved long tabletop block at bench size, solid to the floor')
    P.role(V.window(WINDOW), 'important_background')
    state['adaptations'].append(
        f'Standing lens {LENS.z * 100:.0f} cm, pitch {PITCH:g} deg down, fixed position; pan {PAN:g} deg right from the window '
        f'and left bench to the dumbbell row and right bench, no tilt. Walls are not drawn (STYLE: no walls); the window frame '
        f'marks the far wall. Benches are the long tabletop block, solid to the floor, at {BENCH_SIZE[0]:.2f} x {BENCH_SIZE[1]:.2f} m, top {BENCH_TOP:.2f} m.')
    state['contacts'].append(dict(kind='floor_row', objects='dumbbell', count=2 * len(SCALES), pairs=len(SCALES), floor_z=0.,
                                  row_y=ROW_Y, turn_deg=TURN, scales=[round(s, 3) for s in SCALES]))
    def sample(u, p, t):
        return p, look(p, PAN_END - PAN * (1 - even(u, RAMP)), PITCH)
    return finish(state, heroes, LENS, look(LENS, PAN_END, PITCH), sample)
