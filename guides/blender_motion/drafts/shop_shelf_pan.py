"""Standing pan right in a shop: two approved wall shelves on an undrawn back wall and the approved display case
(catalog v3, 2026-11-16). Probe stage: shelves empty, to check whether they read as a shop."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish
from drafts.room_v2 import look, even
from drafts.counter_case import library_model

IDS = ('shop_shelf_pan',)

# Standing lens at chest height (framing.md walk height 130 cm); visitor side is -Y, back wall at y WALL (not drawn).
LENS = Vector((0, 0, 1.30))
WALL = 2.6
# Two shelves stacked on the wall ahead-right: (x centre, z of the bracket bottom).
SHELVES = ((.9, .90), (.9, 1.55))
# The display case free-standing on the left, its front 1.6 m from the lens.
CASE = (-1.25, 2.0)
PAN, PAN_END, PITCH, RAMP = 40., 18., 6., .1


def build(gid, record, P):
    state = new_state()
    hero = []
    for i, (x, z) in enumerate(SHELVES):
        root, meshes = library_model(P, 'wall_shelf', (0, 0, 0), 'hero')
        bpy.context.view_layer.update()
        pts = [v.co for o in meshes for v in o.data.vertices]
        ys = [p.y for p in pts]; top = max(p.z for p in pts)
        lip_y = sum(p.y for p in pts if p.z > top - .02) / max(1, sum(1 for p in pts if p.z > top - .02))
        mid_y = (min(ys) + max(ys)) / 2
        turn = 0. if lip_y > mid_y else 180.
        depth = max(ys) - min(ys)
        root.rotation_euler.z = math.radians(turn)
        root.location = (x, WALL - depth / 2 - (mid_y if turn == 0 else -mid_y), z)
        print('SHELF', i, 'lip_y', round(lip_y, 3), 'mid_y', round(mid_y, 3), 'turn', turn, 'size',
              round(max(p.x for p in pts) - min(p.x for p in pts), 3), round(depth, 3), round(top, 3))
        hero += meshes
    case, case_meshes = library_model(P, 'display_case', (CASE[0], CASE[1] + .40, 0), 'important_background')
    state['light_position'] = (-1.6, 1.0, 2.4)
    state['adaptations'].append('Probe: two empty wall shelves stacked on an undrawn wall, display case on the left.')
    def sample(u, p, t):
        return p, look(p, PAN_END - PAN * (1 - even(u, RAMP)), PITCH)
    return finish(state, hero, LENS, look(LENS, PAN_END, PITCH), sample)
