"""Menu family drafts of the 2026-11-10 regeneration (board at the counter, card on the table)."""
import math
import bpy
from mathutils import Vector, Matrix
from drafts.common import new_state, finish

IDS = ('menu_board_truck_v2', 'menu_board_tilt_up_v2', 'menu_board_static', 'menu_board_tilt_down', 'menu_card_top_v2')

# Front face of the p0_scenes board panel (centre y 1.25, depth .035).
BOARD_FRONT_Y = 1.2325
TILT_DEG = 22.
# Per-guide machine shift along the counter (m; the shared position stays): owner review r2.
MACHINE_SHIFT = {'menu_board_truck_v2': -.2, 'menu_board_tilt_up_v2': -.55, 'menu_board_static': -.50}
# Per-guide machine shift towards the back of the counter (m): owner review r4, so the machine enters menu_board_static
# at the right edge with its drying cups at the top of its body.
MACHINE_BACK = {'menu_board_static': .12}


def ramp(u, r=.25):
    """Trapezoid velocity: peak speed is 1/(1-r) of the mean, so 22 deg in 3 s peaks under 10 deg/s."""
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def tilt_sample(degrees):
    """Pure tilt about the phone's horizontal axis; the lens position and the yaw stay fixed."""
    def sample(u, p, t):
        end = t - p
        axis = end.cross(Vector((0, 0, 1))).normalized()
        return p, p + Matrix.Rotation(math.radians(degrees) * (1 - ramp(u)), 3, axis) @ end
    return sample


def counter_scene(P, shift=0., back=0.):
    A = P.A
    top, machine = P.counter(machine_offset=(shift, back)); menu, columns = P.board()
    # A shifted machine keeps the served cup on its client-side right, 8 cm clear of the body.
    drink, saucer = P.cup(.6 if not shift else 1.24 + shift + .158, .02, 1.05, False)
    cups = [drink]
    for x in [-.6, -.4, -.2]:
        cups.append(P.cup(x, .60, 1.05, False)[0])
    for obj in bpy.context.scene.objects:
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    return A, menu, columns, cups, machine


def build(gid, record, P):
    state = new_state()
    if gid.startswith('menu_board_'):
        A, menu, columns, cups, machine = counter_scene(P, MACHINE_SHIFT.get(gid, 0.), MACHINE_BACK.get(gid, 0.))
        if gid == 'menu_board_truck_v2':
            # B2: 1x, about 1.5 m back, lens 1.6 m (standing reach), 6.5 deg up, 0.54 m in 4 s at an even 13.7 cm/s.
            for obj in P.members(menu):
                A.tag(obj, 'support', 'Other columns remain subordinate to the chosen drinks column')
            for obj in columns[-1]:
                A.tag(obj, 'hero', 'Chosen drinks column')
            # Owner review: cups on the machine, as a cafe keeps them: under the group heads (the top holds the drying cups).
            bpy.context.view_layer.update()
            for x in [-.17, .17]:
                waiting, _ = P.cup(*(machine.matrix_world @ Vector((x, -.30, 1.09))), False)
                # Handle towards the client, clear of the machine's working face.
                waiting.rotation_euler.z = -math.pi / 2
            y = BOARD_FRONT_Y - 1.5
            aim = Vector((.57, BOARD_FRONT_Y, 1.6 + 1.5 * math.tan(math.radians(6.5))))
            state['adaptations'].append('Truck shortened to the middle-to-drinks column step (0.54 m) at about 14 cm/s; lens at 1.6 m, the highest standing reach, 6.5 deg up.')
            return finish(state, columns[-1], (.57, y, 1.6), aim,
                          lambda u, p, t: (p + Vector((-.54 * (1 - u), 0, 0)), t + Vector((-.54 * (1 - u), 0, 0))))
        state['lens_mm'] = 48
        if gid == 'menu_board_static':
            # B1: 2x, 3.0 m back, lens 1.6 m, at most 10 deg up, still phone.
            for obj in P.members(menu):
                A.tag(obj, 'support', 'Side columns are context; the chosen centre column is read')
            for obj in columns[1]:
                A.tag(obj, 'hero', 'Chosen centre column, straight on')
            y = BOARD_FRONT_Y - 3.0
            aim = Vector((0, BOARD_FRONT_Y, 1.6 + 3.0 * math.tan(math.radians(3))))
            state['adaptations'].append('A still 2x hold 3 m back; the 1.8 m board is wider than the 2x view at 3 m, so the centre column is the hero and the side columns run off both edges.')
            return finish(state, columns[1], (0, y, 1.6), aim)
        if gid == 'menu_board_tilt_up_v2':
            # Reverse of B3: 2x, 3.0 m back, lens 1.5 m, tilt up 22 deg in 3 s from the cups on the counter to the board.
            for obj in P.members(menu):
                A.tag(obj, 'support', 'Side columns are context; the chosen centre column is read')
            for obj in columns[1]:
                A.tag(obj, 'hero', 'Chosen centre column at the end of the tilt')
            y = BOARD_FRONT_Y - 3.0
            aim = Vector((0, BOARD_FRONT_Y, 1.5 + 3.0 * math.tan(math.radians(4.8))))
            state['adaptations'].append('Pure tilt, no pan, 22 deg in 3 s (peak under 10 deg/s); ends 4.8 deg up on the centre column at 2x from 3.0 m.')
            return finish(state, columns[1], (0, y, 1.5), aim, tilt_sample(-TILT_DEG))
        if gid == 'menu_board_tilt_down':
            # B3: 2x, 2.5 m back, lens 1.5 m, tilt down 22 deg in 3 s from the board to the cups on the counter.
            for obj in P.members(menu):
                A.tag(obj, 'support', 'Board is where the tilt starts')
            hero = []
            for root in cups[1:]:
                for obj in P.members(root):
                    if obj.get('composition_role') == 'support':
                        A.tag(obj, 'hero', 'Cups on the counter end the tilt')
                        hero.append(obj)
            x = -.37
            y = BOARD_FRONT_Y - 2.5
            start_pitch = 8.
            end_pitch = start_pitch - TILT_DEG
            aim = Vector((x, y + 1.5 * math.cos(math.radians(end_pitch)), 1.5 + 1.5 * math.sin(math.radians(end_pitch))))
            state['adaptations'].append('No pastry case in the approved set: the tilt ends on the counter top with its cups. Pure tilt, no pan, 22 deg in 3 s, from 8 deg up to 14 deg down.')
            return finish(state, hero, (x, y, 1.5), aim, tilt_sample(TILT_DEG))
    if gid == 'menu_card_top_v2':
        A = P.A
        A.table((.22, .18, 0), .65); card, panel = P.plain_card(); drink, saucer = P.cup(.12, .22, .785, False); A.fork((-.2, 0, .79))
        selected = next(o for o in P.members(card) if o.name.startswith('Menu price row 02'))
        bpy.context.view_layer.update()
        P.light_edge('Selected menu position', [selected.matrix_world @ Vector((x, 0, .0013)) for x in [-.087, .087]], .001, parent=selected, polyline=True)
        rows = [o for o in P.members(card) if o.name.startswith('Menu price row')]
        A.tag(panel, 'support', 'Card outline frames the readable rows')
        state['camera_up'] = (0, 1, 0)
        state['adaptations'].append('Owner review: overhead pedestal down at 90 deg, 1x: 45 cm to 30 cm above the card in 3 s, from the whole card with the cup to the readable dish rows; the cup moves from (.22, .18) to (.12, .22) so it is in frame at 45 cm.')
        return finish(state, rows, (0, -.02, .785 + .30), (0, -.02, .79),
                      lambda u, p, t: (p + Vector((0, 0, .15 * (1 - ramp(u)))), t))
    return None
