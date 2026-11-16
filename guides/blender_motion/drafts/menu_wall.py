"""Menu draft of the 2026-11-11 revision: walk up to the wall board straight on; one row is highlighted throughout (template menu_board_static)."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.menu_v2 import BOARD_FRONT_Y
from drafts.room_window import even

IDS = ('menu_wall_board_item',)

START_DISTANCE, END_DISTANCE = 3.4, 2.0
LENS_HEIGHT = 1.45
START_PITCH_DEG, END_PITCH_DEG = 5., 10.
# Walk window inside the 5 s move: still 0.8 s, walk 3.2 s (0.4 s ease at each end), still 1.0 s.
WALK_START, WALK_END, WALK_RAMP = .16, .80, .125


def row_outline(row, margin=.02):
    """Closed rounded rectangle just outside the bar's front face, in the board plane."""
    bpy.context.view_layer.update()
    hx, hz = row.dimensions.x / 2 + margin, row.dimensions.z / 2 + margin
    y = row.matrix_world.translation.y - row.dimensions.y / 2 - .001
    cx, cz = row.matrix_world.translation.x, row.matrix_world.translation.z
    r, points = .008, []
    for sx, sz, start in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
        for j in range(7):
            a = math.radians(start + j * 15)
            points.append((cx + sx * (hx - r) + r * math.cos(a), y, cz + sz * (hz - r) + r * math.sin(a)))
    return points + [points[0]]


def build(gid, record, P):
    state = new_state()
    A = P.A
    _, columns = P.board()
    chosen = columns[1][2]
    for rows in columns:
        for row in rows:
            if row is not chosen:
                A.tag(row, 'support', 'Other board items, quieter than the chosen one')
    highlight = P.light_edge('Selected board item outline', row_outline(chosen), .001, polyline=True)
    state['lens_mm'] = 48
    item_z = chosen.matrix_world.translation.z
    start = Vector((0, BOARD_FRONT_Y - START_DISTANCE, LENS_HEIGHT))
    start_aim = Vector((0, BOARD_FRONT_Y, LENS_HEIGHT + START_DISTANCE * math.tan(math.radians(START_PITCH_DEG))))
    end = Vector((chosen.matrix_world.translation.x, BOARD_FRONT_Y - END_DISTANCE, LENS_HEIGHT))
    end_aim = Vector((end.x, BOARD_FRONT_Y, LENS_HEIGHT + END_DISTANCE * math.tan(math.radians(END_PITCH_DEG))))
    state['adaptations'].append(
        f'Walk straight at the wall board at 2x, lens {LENS_HEIGHT} m: {START_DISTANCE} m -> {END_DISTANCE} m from the board face '
        f'in 3.2 s (peak 0.50 m/s), pitch {START_PITCH_DEG:g} -> {END_PITCH_DEG:g} deg up with the walk; rows are ragged left-aligned bars; '
        f'the centre column third row (z {item_z:.2f} m) carries a closed yellow light-edge outline on every frame.')

    def sample(u, p, t):
        k = even((u - WALK_START) / (WALK_END - WALK_START), WALK_RAMP)
        return start.lerp(p, k), start_aim.lerp(t, k)
    return finish(state, [chosen, highlight], end, end_aim, sample)
