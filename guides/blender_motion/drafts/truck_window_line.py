"""Truck window from the line (catalog v3, 2026-11-16): the approved food truck, turned as in truck_across_street,
from about 12 ft at standing eye level; a slow even pan right along the side from the cab to the service window and
its awning. Move of room_bar_pan (fixed lens, even pan right); no queue (one creator rig at most). Owner review
2026-11-17: the cook (approved barista rig, working pose) inside behind the window, three approved Tripo burgers on the
inner counter, stray dots removed by the short-stroke filter for this guide only (drafts.truck_cook). Owner review
2026-11-16 r3 ("the window shape is unclear"): the cache draws no contour on the opening's top and right edges (wall and
soffit both face the lens), so a window-frame outline at hero strength traces the opening on the wall, and the truck's
own lines inside the opening are drawn at a lower share (this guide only)."""
import math

import bpy
import bmesh
from mathutils import Vector

from drafts.common import new_state, finish
from drafts.room_v2 import look, even
from drafts.truck_across_street import food_truck, SIDE_Y, FT, EYE

IDS = ('truck_window_line',)

DISTANCE_FT = 12
# Service window opening and awning in the turned cache (probe of the side profile): x -0.8..2.15 m, z 1.1..2.4 m,
# the awning edge out to y -1.71 m; the lens stands opposite the window centre.
WINDOW_X = .65
WINDOW_BOX = ((-.85, 2.2), (1.05, 2.45))
# Pan: 30 deg right in 5 s (6.7 deg/s between a 0.5 s ease at each end; RB29 RB30 give 8-10 deg/s for 1x, the request asks slow);
# level phone (judgement): the window centre sits about 45% from the top.
PAN, PAN_END, PITCH, RAMP = 30., 0., 0., .1
CURB_Y = SIDE_Y - .45
# r3: the service window opening in the turned cache (1 cm ray probe 2026-11-16, scratch/r3/probe_edges.py):
# x -0.675..1.86 m, z 1.19..2.135 m, wall plane y -0.985. The frame outline sits 5 mm in front of the wall.
OPENING_X, OPENING_Z, WALL_Y = (-.675, 1.86), (1.19, 2.135), -.985
FRAME_RADIUS = .0012        # the curb line's tube: one 3 px contour at this distance
# Truck strokes whose points project inside the opening (inset by INTERIOR_INSET_PX) are drawn at this share of the hero
# opacity, so the counter, shelf and pots read behind the frame (judgement).
INTERIOR_SHARE = .4
INTERIOR_INSET_PX = 4.


def window_mask(meshes):
    """Framing mask: the truck's own triangles around the service window and awning, never drawn."""
    masks = []
    (x0, x1), (z0, z1) = WINDOW_BOX
    for obj in meshes:
        copy = obj.copy(); copy.data = obj.data.copy(); bpy.context.collection.objects.link(copy)
        mesh = bmesh.new(); mesh.from_mesh(copy.data)
        discard = [v for v in mesh.verts
                   if not (x0 < (obj.matrix_world @ v.co).x < x1 and z0 < (obj.matrix_world @ v.co).z < z1
                           and (obj.matrix_world @ v.co).y < SIDE_Y + .25)]
        bmesh.ops.delete(mesh, geom=discard, context='VERTS'); mesh.to_mesh(copy.data); mesh.free()
        if not len(copy.data.polygons):
            bpy.data.objects.remove(copy, do_unlink=True); continue
        copy.name = 'Window safety mask / ' + obj.name
        copy['p0_framing_mask'] = True; copy['composition_role'] = 'framing_mask'
        copy.lineart.usage = 'EXCLUDE'; copy.hide_render = True
        masks.append(copy)
    assert masks, 'Food truck has no geometry around the service window'
    return masks


def window_frame(P):
    """Closed rectangle tube tracing the service window opening on the truck's wall (hero role, square corners)."""
    (x0, x1), (z0, z1), y = OPENING_X, OPENING_Z, WALL_Y - .005
    corners = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), (x0, y, z0)]
    frame = P.G.tube('Service window frame outline', corners, FRAME_RADIUS, handle_type='VECTOR')
    P.A.tag(frame, 'hero', 'Outline of the truck service window opening (the cache draws no contour on its top and right edges)')
    return frame


def install_interior_quieting(meshes, report):
    """Wraps lineart_render.strokes_setup (after the dot filter) in this process: in the collection holding the truck,
    points projecting inside the window opening get INTERIOR_SHARE opacity; everything else keeps full opacity."""
    import numpy as np
    import lineart_render as L
    from drafts.truck_cook import _points, _pixels
    inner = L.strokes_setup
    names = {m.name for m in meshes}
    (x0, x1), (z0, z1) = OPENING_X, OPENING_Z
    corners = np.array([[x0, WALL_Y, z0], [x1, WALL_Y, z0], [x1, WALL_Y, z1], [x0, WALL_Y, z1]], dtype=np.float64)

    def wrapped(scene, collection, args, distance, fov_y, motion_end):
        obj, counts = inner(scene, collection, args, distance, fov_y, motion_end)
        if not names & {o.name for o in collection.all_objects}:
            return obj, counts
        current = scene.frame_current
        shares = []
        for layer in obj.data.layers:
            for frame in layer.frames:
                scene.frame_set(frame.frame_number); bpy.context.view_layer.update()
                drawing = frame.drawing; points = _points(drawing)
                if points is None or not len(points):
                    continue
                px = _pixels(scene, obj, points)
                # Opening corners in the same pixel space (world points: identity object matrix stand-in).
                box = _pixels(scene, _World(), corners)
                lo = box.min(0) + INTERIOR_INSET_PX; hi = box.max(0) - INTERIOR_INSET_PX
                inside = np.all((px > lo) & (px < hi), axis=1)
                existing = drawing.attributes.get('opacity')
                value = np.ones(len(points), np.float32)
                if existing is not None:
                    existing.data.foreach_get('value', value)
                value = np.where(inside, value * INTERIOR_SHARE, value).astype(np.float32)
                opacity = existing or drawing.attributes.new('opacity', 'FLOAT', 'POINT')
                opacity.data.foreach_set('value', value)
                shares.append(float(inside.mean()))
        scene.frame_set(current); bpy.context.view_layer.update()
        obj.data.update_tag()
        report[collection.name] = dict(interior_share=INTERIOR_SHARE, inset_px=INTERIOR_INSET_PX,
                                       interior_point_share=round(float(np.mean(shares)), 3) if shares else None)
        print('TRUCK_INTERIOR', collection.name, report[collection.name], flush=True)
        return obj, counts

    wrapped.p0_original = getattr(inner, 'p0_original', inner)
    L.strokes_setup = wrapped
    return report


class _World:
    """Object stand-in with an identity world matrix, for projecting world points with truck_cook._pixels."""
    from mathutils import Matrix as _M
    matrix_world = _M.Identity(4)


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    A, G = P.A, P.G
    state = new_state()
    meshes = food_truck(P)
    A.tag(G.tube('Curb line', [(-4.2, CURB_Y, .012), (4.2, CURB_Y, .012)], .0012), 'structure',
          'Sidewalk edge under the truck; no filled street or ground plane')
    masks = window_mask(meshes)
    window_frame(P)
    from drafts.truck_cook import cook_working, burgers, install_stroke_treatment
    install_stroke_treatment(meshes)
    install_interior_quieting(meshes, {})
    cook_working(P, state, gid)
    burgers(P)
    state['contacts'].append(dict(kind='truck_strokes', short_stroke_filter_px=12, outline_emphasis=False,
                                  window_frame_outline=dict(x=list(OPENING_X), z=list(OPENING_Z), y=WALL_Y - .005, role='hero'),
                                  interior_share=INTERIOR_SHARE,
                                  scope='this guide only (strokes_setup wrapped in process)'))
    lens = Vector((WINDOW_X, SIDE_Y - DISTANCE_FT * FT, EYE))
    state['framing_masks'] = masks
    state['contacts'].append(dict(kind='standing_pan_to_truck_window', lens_height_m=EYE, pitch_deg=PITCH,
                                  from_window_side_ft=DISTANCE_FT, pan_deg=PAN, lens='1x', people='cook inside the truck (barista rig)'))
    state['adaptations'].append(
        f'Standing at eye level (lens {EYE} m), level phone, {DISTANCE_FT} ft from the truck\'s window side, opposite '
        f'the window centre; pan {PAN:g} deg right from the cab to the service window and awning, no tilt, no walk; '
        'hero band measured on the window and awning (the truck body is taller than the band at this distance).')

    def sample(u, p, t):
        return p, look(p, PAN_END - PAN * (1 - even(u, RAMP)), PITCH)
    return finish(state, masks, lens, look(lens, PAN_END, PITCH), sample)
