"""Seated pan from the window beside your table into the room (revision 2026-11-11); one scene, mirrored by side.

room_window_pan_left: window on the left wall, pan right. room_window_pan_right: the same scene mirrored in x, pan left.
Built from room_v2 (room_seated_pan_v2 / room_static_wide layout) plus the approved venue_assets.window."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import SEAT, PITCH, look

IDS = ('room_window_pan_left', 'room_window_pan_right')

# Window frame in a side wall beside the table, facing into the room; x is for the left side and mirrors for the right.
# Moved 0.18 m toward the lens along its line of sight (2026-11-11 r2): 1.69 -> 1.51 m from the seat to the frame centre.
WINDOW = (-.85, 1.00, 1.40)
TABLE = (-.10, 0, 0)  # shifted toward the window: about 0.20 m from its rim to the wall
CUP = (-.30, .22, .785)
# Pan: 29 deg from the window to 2 deg past the room axis over 4 s, 8.1 deg/s between a 0.4 s ease at each end.
PAN, PAN_END, RAMP = 29., 2., .1
# Left id (owner 2026-11-11 r2): same start, 1 s longer at the same speed, 37 deg to 10 deg past the room axis over 5 s (8.3 deg/s),
# ending on a glazed door in the wall parallel to the window wall with a floor plant beside it.
LEFT_PAN, LEFT_PAN_END = 37., 10.
DOOR, DOOR_PLANT = (2.40, 5.00), (2.20, 4.05)  # x for the left id (window at x -0.85); door faces the room (-x)
# Left id (owner 2026-11-11 r5): the window sits 0.50 m toward the lens (-y) from its r3 place, 1.00 m left of r4 in the start frame.
LEFT_WINDOW_SHIFT = -.50
# Left id: the window's wall plane is x WINDOW[0]; room objects beyond it would show through the glass (owner r5).
WALL_MARGIN = .05


def plan_bounds(root):
    xs, ys = [], []
    for o in [root] + list(root.children_recursive):
        if o.type == 'MESH':
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                xs.append(w.x)
                ys.append(w.y)
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None


def keep_inside_wall(roots, wall, state):
    """Moves mirrored room roots (children of the x-mirror) to the room side (+x) of the window wall plane."""
    bpy.context.view_layer.update()
    bounds = {r: b for r in roots if (b := plan_bounds(r))}
    centre = {r: ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2) for r, b in bounds.items()}
    tables = [r for r in bounds if r.name.startswith('Two-person dining table')]
    # A table's pendant, glass and menu card move with it.
    cluster = {r: min(tables, key=lambda t: math.dist(centre[t], centre[r])) for r in bounds}
    groups = {}
    for r in bounds:
        t = cluster[r] if math.dist(centre[cluster[r]], centre[r]) < .6 else r
        groups.setdefault(t, []).append(r)
    for head, members in groups.items():
        lo = min(bounds[r][0] for r in members)
        if lo >= wall + WALL_MARGIN:
            continue
        if head.name.startswith('Faint partition plane') and max(bounds[r][1] for r in members) < wall:
            for r in members:
                bpy.data.objects.remove(r, do_unlink=True)
            state['adaptations'].append(f'Room partition at x {lo:+.2f} m removed: it stood outside the window wall.')
            continue
        shift = wall + WALL_MARGIN - lo
        for r in members:
            r.location.x -= shift  # parent mirror has scale x -1
        state['adaptations'].append(f'{head.name.split(".")[0]} moved {shift:.2f} m to the room side of the window wall.')


def even(u, r=RAMP):
    u = max(0., min(1., u))
    if u < r:
        return u * u / (2 * r * (1 - r))
    if u > 1 - r:
        return 1 - (1 - u) ** 2 / (2 * r * (1 - r))
    return (u - r / 2) / (1 - r)


def build(gid, record, P):
    A = P.A
    state = new_state()
    s = -1 if gid.endswith('_left') else 1  # sign of the window's side in x
    before = set(bpy.data.objects)
    heroes = P.room()
    if s < 0:
        # Left variant: mirror the whole room in x (builders bake positions into children) so the ids are mirror images.
        roots = [o for o in set(bpy.data.objects) - before if o.parent is None]
        mirror = A.empty('Room mirrored for the left window')
        mirror.scale.x = -1
        for obj in roots:
            obj.parent = mirror
        keep_inside_wall(roots, WINDOW[0], state)
    wx, wy, wz = WINDOW
    if s < 0:
        wy += LEFT_WINDOW_SHIFT
    window = P.V.window((-s * wx, wy, wz))
    # -90 deg on both sides keeps the lit post (lighting_cues: local x < 0) on the room-side edge of the frame.
    window.rotation_euler.z = math.radians(-90)
    P.role(window, 'important_background')
    window['p0_side_window'] = True
    P.A.table((-s * TABLE[0], TABLE[1], TABLE[2]), .55)
    drink, _ = P.cup(-s * CUP[0], CUP[1], CUP[2], False)
    P.role(drink, 'foreground')
    pan, pan_end = (LEFT_PAN, LEFT_PAN_END) if s < 0 else (PAN, PAN_END)
    if s < 0:
        door, _ = P.V.door((DOOR[0], DOOR[1], 0))
        door.rotation_euler.z = math.radians(90)
        P.role(door, 'background')
        P.role(P.V.plant((DOOR_PLANT[0], DOOR_PLANT[1], 0), height=1.1), 'background')
        state['adaptations'].append(
            f'Glazed door in the wall parallel to the window wall at x {DOOR[0]:+.2f} m, y {DOOR[1]:.2f} m, with a floor plant '
            f'beside it at y {DOOR_PLANT[1]:.2f} m (no wall drawn).')
    state['light_position'] = (-s * wx, wy, wz)
    state['adaptations'].append(
        f'Window frame in the wall beside your table at x {-s * wx:+.2f} m (no wall drawn); seated lens 115 cm, pitch {PITCH:g} deg, '
        f'pan {pan:g} deg {"left" if s > 0 else "right"} away from the window, no tilt; room layout mirrored for the left id.')
    state['contacts'].append(dict(kind='seated_pan_from_window', window=window.name, side='right' if s > 0 else 'left'))
    seat = Vector((-s * SEAT.x, SEAT.y, SEAT.z))
    end = -s * pan_end
    def sample(u, p, t):
        return p, look(p, end + s * pan * (1 - even(u)), PITCH)
    return finish(state, heroes, seat, look(seat, end, PITCH), sample)
