"""Approaching the front desk (catalog v3, 2026-11-16): the approved reception desk composition of visit_reception_pan
with one staff member behind it, a slow chest-height push-in of 4 in. The staff stand-in is the approved barista rig
in its approved rest pose (standing, arms at the sides), turned to face the visitor; no posing, no motion. No clients."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import look, even
from drafts.counter_case import library_model
from drafts.visit_reception_pan import LAPTOP, REMOVED

IDS = ('visit_front_desk_hello',)

INCH = .0254
TOP = 1.05
# Desk in the counter builder frame (customer edge at local y -.15, top back edge at .75), moved 5 ft 4 in ahead.
DESK = (0., 1.62, 0.)
# Staff feet behind the top's back edge, left of the laptop so its lid does not cover him (judgement).
STAFF_FEET = (-.25, 1.02)
# Standing chest height (framing.md walk height 130 cm, judgement); about 4 ft 9 in from the desk edge at the end.
LENS = Vector((.05, 0., 1.30))
YAW, PITCH = -1.5, 6.
PUSH = 4 * INCH            # request: slow 4 in push-in
RAMP = .2


def build(gid, record, P):
    if gid not in IDS:
        return None
    import barista
    A = P.A
    state = new_state()
    before = set(bpy.data.objects)
    P.counter(body=True)
    for obj in [o for o in bpy.data.objects if o not in before and o.name.startswith(REMOVED)]:
        bpy.data.objects.remove(obj, do_unlink=True)
    laptop, laptop_meshes = library_model(P, 'laptop', (LAPTOP[0], LAPTOP[1], TOP), 'hero')
    desk = A.group('Reception desk (approved composition)', before, DESK)
    hero = []
    for obj in P.members(desk):
        if obj.type == 'MESH' and obj.name.startswith('Customer counter top'):
            A.tag(obj, 'hero', 'Reception desk top, where the visitor is greeted')
            hero.append(obj)
    hero += laptop_meshes
    bpy.context.view_layer.update()
    # Rest pose as approved on the objects page: no lean, no head turn; only turned to face the visitor (-Y).
    feet = Vector((DESK[0] + STAFF_FEET[0], DESK[1] + STAFF_FEET[1], 0.))
    root, arm, _, _ = barista.stand(feet, -math.pi / 2, lean=0., side_lean=0., head_away=0., head_down=0.)
    barista.finish(P, root, arm, state, dict(where='behind the reception desk, facing the visitor',
                                             pose='approved rest pose (standing, arms at the sides), static',
                                             face='toward the visitor (request)', held='nothing'))
    state['light_position'] = (-1.6, 1.0, 2.4)
    state['adaptations'].append(
        f'Reception desk (approved composition) with its customer edge {(DESK[1] - .15) / INCH / 12:.1f} ft ahead at the end, '
        f'laptop screen to the staff side; the staff stand-in (approved barista rig, rest pose) stands behind it facing '
        f'the visitor, static; portrait, standing lens {LENS.z / INCH:.0f} in above the floor, 1x, {PITCH:g} deg down, '
        f'a 4 in straight push toward the desk in {record["durationSec"]} s at an even pace. No clients.')
    state['contacts'].append(dict(kind='front_desk_push', desk=desk.name, laptop=laptop.name, staff=1, clients=0))
    aim = look(LENS, YAW, PITCH)

    def sample(u, p, t):
        back = (p - t).normalized() * PUSH * (1 - even(u, RAMP))
        return p + back, t + back
    return finish(state, hero, LENS, aim, sample)
