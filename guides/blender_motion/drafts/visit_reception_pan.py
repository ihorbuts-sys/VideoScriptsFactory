"""Standing pan from the waiting chairs to the reception desk (catalog v3, 2026-11-16).

Built like room_bar_pan (fixed lens, even pan right) on the approved reception desk composition: p0_scenes.counter
(body=True) minus the espresso machine, drying cups and glasses and card holder, with the approved Tripo laptop on
top, its screen toward the staff side. Rework (owner review 2026-11-17 "put stuff there"): three waiting chairs, the
floor plant, the approved wall shelf with two small potted plants behind the desk, a window frame behind the chairs and
two pendants over the desk; all approved objects. Rework (owner review 2026-11-16 "add a worker at the desk"): one
staff member behind the desk, placed as in visit_front_desk_hello (the approved barista rig in its approved rest pose,
left of the laptop, facing the room). No clients."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import look, even
from drafts.counter_case import library_model

IDS = ('visit_reception_pan',)

# Standing lens at chest height (framing.md walk height 130 cm, judgement); visitor side is -Y.
LENS = Vector((0, 0, 1.30))
# Desk footprint origin (counter builder frame: customer edge at local y -.15, top at z 1.05); staff side is +Y.
DESK = (.2, 3.15, 0)
# The laptop where the approved composition render placed it, in the counter frame; turn 0 keeps its screen facing +Y.
LAPTOP = (.35, .42)
# Three waiting chairs along the left, seats facing into the room (+X); the plant between them and the desk.
CHAIRS = ((-2.1, 1.35), (-2.1, 1.95), (-2.1, 2.55))
PLANT = ((-1.8, 3.25), 1.2)
# Undrawn back wall (judgement): the approved wall shelf on it behind the desk, right of the laptop, with two small
# potted plants (the approved plant builder at 0.3 scale); the window frame behind the chairs; pendants over the desk.
WALL_Y = 4.45
SHELF = (.85, 1.55)                     # x centre, z of its lowest point
SHELF_PLANTS = ((.62, .26), (1.08, .22))  # x, plant height
WINDOW = (-2.0, 1.55)                   # x, centre height
PENDANTS = ((-.35, 3.45), (.75, 3.45))
# Staff feet behind the top's back edge, left of the laptop, in the desk frame (visit_front_desk_hello's placement).
STAFF_FEET = (-.25, 1.02)
CEILING = 2.75
# Pan: 42 deg right in 5 s (8.4 deg/s between the ramps, RB29 RB30), ending with the desk centred; pitch from probe.
PAN, PAN_END, PITCH, RAMP = 42., 3., 14.5, .1
REMOVED = ('Espresso', 'Drying', 'Counter card holder', 'Machine side panel highlight', 'Side-on espresso machine')


def wall_shelf(P):
    """The approved wall shelf on the undrawn back wall, lip toward the room (shop_shelf_pan's orientation rule);
    returns its root and the world height of its top board."""
    root, meshes = library_model(P, 'wall_shelf', (0, 0, 0), 'support')
    bpy.context.view_layer.update()
    pts = [v.co for o in meshes for v in o.data.vertices]
    ys = [q.y for q in pts]; top = max(q.z for q in pts)
    rim = [q.y for q in pts if q.z > top - .02]
    turn = 0. if sum(rim) / len(rim) > (min(ys) + max(ys)) / 2 else 180.
    mid = (min(ys) + max(ys)) / 2
    root.rotation_euler.z = math.radians(turn)
    root.location = (SHELF[0], WALL_Y - (max(ys) - min(ys)) / 2 - (mid if turn == 0 else -mid), SHELF[1])
    return root, SHELF[1] + top


def build(gid, record, P):
    import barista
    A = P.A
    state = new_state()
    before = set(bpy.data.objects)
    P.counter(body=True)
    for obj in [o for o in bpy.data.objects if o not in before and o.name.startswith(REMOVED)]:
        bpy.data.objects.remove(obj, do_unlink=True)
    top_z = 1.05
    laptop, laptop_meshes = library_model(P, 'laptop', (LAPTOP[0], LAPTOP[1], top_z), 'hero')
    desk = A.group('Reception desk (approved composition)', before, DESK)
    hero = []
    for obj in P.members(desk):
        if obj.type == 'MESH' and obj.name.startswith(('Customer counter top', 'Customer counter cabinet')):
            A.tag(obj, 'hero', 'Reception desk, the end of the pan')
            hero.append(obj)
    hero += laptop_meshes
    for x, y in CHAIRS:
        P.role(P.V.chair((x, y, 0), math.pi / 2), 'support')
    P.role(P.V.plant((PLANT[0][0], PLANT[0][1], 0), height=PLANT[1]), 'support')
    shelf, shelf_top = wall_shelf(P)
    for x, h in SHELF_PLANTS:
        P.role(P.V.plant((x, WALL_Y - .12, shelf_top), height=h), 'support')
    P.role(P.V.window((WINDOW[0], WALL_Y, WINDOW[1])), 'background')
    for x, y in PENDANTS:
        P.V.pendant((x, y, CEILING))
    bpy.context.view_layer.update()
    # Rest pose as approved on the objects page: no lean, no head turn; only turned to face the room (-Y).
    feet = Vector((DESK[0] + STAFF_FEET[0], DESK[1] + STAFF_FEET[1], 0.))
    root, arm, _, _ = barista.stand(feet, -math.pi / 2, lean=0., side_lean=0., head_away=0., head_down=0.)
    barista.finish(P, root, arm, state, dict(where='behind the reception desk, left of the laptop, facing the room',
                                             pose='approved rest pose (standing, arms at the sides), static',
                                             face='toward the room (owner review 2026-11-16)', held='nothing'))
    state['light_position'] = (WINDOW[0], WALL_Y, WINDOW[1])   # the window is the daylight source
    state['adaptations'].append(
        f'Reception desk (approved composition) with its customer edge {DESK[1] - .15:.2f} m ahead, laptop screen to the '
        f'staff side; three waiting chairs on the left and a floor plant between them and the desk; behind the desk the '
        f'approved wall shelf with two small potted plants, a window frame behind the chairs, two pendants over the desk; one staff member (approved barista rig, rest pose, static) behind the desk facing the room; no clients; no walls drawn; '
        f'standing lens {LENS.z * 100:.0f} cm, pitch {PITCH:g} deg, pan {PAN:g} deg right from the chairs to the desk, no tilt.')
    state['contacts'].append(dict(kind='standing_pan_to_reception_desk', desk=desk.name, laptop=laptop.name, staff=1, clients=0))
    def sample(u, p, t):
        return p, look(p, PAN_END - PAN * (1 - even(u, RAMP)), PITCH)
    return finish(state, hero, LENS, look(LENS, PAN_END, PITCH), sample)
