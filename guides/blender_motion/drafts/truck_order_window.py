"""Order at the truck window (catalog v3, 2026-11-16): the approved food truck, turned as in truck_across_street, from
the sidewalk right at the service window; standing eye level, the phone tilted slightly up into the window, a slow
straight push-in of about 3 in. Move of entrance_walk_in_v2 (constant push, the phone does not re-aim); no staff
(no approved rig inside a truck): the interior shelf, pots and tap read as service."""
import math

import bpy
import bmesh
from mathutils import Vector

from drafts.common import new_state, finish
from drafts.truck_across_street import food_truck, ramp, SIDE_Y, FT, EYE

IDS = ('truck_order_window',)

# Service area inside the turned cache (probe of the interior): shelf with pots x 0.6-1.5 m, z 1.75-2.0 m; counter
# items z 1.5-1.6 m; tap x 1.5-1.65 m; back wall y +0.17 m. The window opening is x -0.75..1.95 m, z 1.27..2.05 m
# (sill about 4 ft 2 in), the awning edge out to y -1.71 m.
SERVICE_BOX = ((.55, 1.7), (-.6, .3), (1.45, 2.05))
SERVICE_X = sum(SERVICE_BOX[0]) / 2
# Lens about 2 ft 9 in from the window side (just outside the awning edge), tilted 3 deg up: the service area sits
# about 36-58% from the top (framing.md RA2 gives 40-45% for the centre; judgement on the tilt).
DISTANCE_FT = 2.75
PITCH_UP_DEG = 3.
PUSH_IN = 3 * .0254     # 3 in over the move (about 0.75 in/s; slower than RA21's table push, the request asks slow)


def service_mask(meshes):
    """Framing mask: the truck's own triangles of the service area behind the window, never drawn."""
    masks = []
    (x0, x1), (y0, y1), (z0, z1) = SERVICE_BOX
    for obj in meshes:
        copy = obj.copy(); copy.data = obj.data.copy(); bpy.context.collection.objects.link(copy)
        mesh = bmesh.new(); mesh.from_mesh(copy.data)
        inside = lambda w: x0 < w.x < x1 and y0 < w.y < y1 and z0 < w.z < z1
        bmesh.ops.delete(mesh, geom=[v for v in mesh.verts if not inside(obj.matrix_world @ v.co)], context='VERTS')
        mesh.to_mesh(copy.data); mesh.free()
        if not len(copy.data.polygons):
            bpy.data.objects.remove(copy, do_unlink=True); continue
        copy.name = 'Service area safety mask / ' + obj.name
        copy['p0_framing_mask'] = True; copy['composition_role'] = 'framing_mask'
        copy.lineart.usage = 'EXCLUDE'; copy.hide_render = True
        masks.append(copy)
    assert masks, 'Food truck has no geometry in the service area'
    return masks


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    state = new_state()
    meshes = food_truck(P)
    masks = service_mask(meshes)
    lens = Vector((SERVICE_X, SIDE_Y - DISTANCE_FT * FT, EYE))
    pitch = math.radians(PITCH_UP_DEG)
    aim = lens + Vector((0, math.cos(pitch), math.sin(pitch))) * 1.5
    state['framing_masks'] = masks
    state['contacts'].append(dict(kind='standing_push_in_at_truck_window', lens_height_m=EYE, pitch_up_deg=PITCH_UP_DEG,
                                  from_window_side_ft=DISTANCE_FT, push_in_in=3, lens='1x', people=0))
    state['adaptations'].append(
        f'Standing at the window at eye level (lens {EYE} m), {DISTANCE_FT} ft from the truck\'s window side, opposite '
        f'the service area; phone tilted {PITCH_UP_DEG:.0f} deg up into the window; a slow straight push-in of 3 in with a '
        'short ease at each end, the phone does not re-aim; hero band measured on the service area behind the window '
        '(shelf, pots, counter items, tap); the window frame is larger than the band at this distance.')

    def sample(u, p, t):
        offset = Vector((0, -PUSH_IN * (1 - ramp(u)), 0))
        return p + offset, t + offset
    return finish(state, masks, lens, aim, sample)
