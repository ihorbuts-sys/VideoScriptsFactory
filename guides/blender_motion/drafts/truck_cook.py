"""Shared setup of the truck drafts' rework (owner review 2026-11-17): the cook inside the food truck (the approved
barista rig in an approved pose), burgers on the truck's inner counter, and a per-guide stroke treatment of the truck
(short-stroke dot filter, optional outline emphasis). Nothing here changes a shared builder or default: the stroke
treatment wraps lineart_render.strokes_setup in the running Blender process of the guide that installs it only.

Truck frame (the cache turned 180 deg, truck_across_street.food_truck): window side -Y, cab -X. Interior from the
2026-11-17 ray probe: window opening x -0.55..1.70 m, z about 1.25..2.05 m; behind the window wall a recess with a
flat top at z 1.07 between y -0.90 and -0.40 (where the cook stands; his legs are under it); the inner counter top at
z 1.43-1.45 from y -0.35 to 0.15 against the back wall (y 0.17); pots and a shelf over x 0.45-1.0 and a tap at x 1.7.
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

# The cook's feet stand this far above the street so the approved pose keeps its own proportions to the window: the
# template counter top (1.05 m) maps onto the truck's sill (about 1.25 m). Hidden under the recess top (judgement).
COOK_FLOOR = .20
# Working cook (counter_edge_to_pass_v2 pose): left part of the window, in the recess, facing the pots to his right
# (+X), body 10 deg past profile away from the street as in the template.
WORK_FEET = (-.15, -.62)
WORK_FACING_DEG = 0.
# Inner counter top and the burger spots on its clear stretch right of the pots (x 1.05-1.45, judgement).
INNER_TOP = 1.45
BURGER_SPOTS = ((1.06, -.24, 15.), (1.24, -.15, -20.), (1.42, -.24, 40.))
# Short-stroke filter (render_objects SCAN_PREP min_stroke_px, the objects page default); outline emphasis keeps the
# truck's outer contour at the role opacity and draws the interior contours at this share of it (judgement).
MIN_STROKE_PX = 12
INTERIOR_SHARE = .5
OUTLINE_PX = 3.


def cook_working(P, state, gid, feet=WORK_FEET, facing_deg=WORK_FACING_DEG):
    """The approved working barista (barista.add, counter_edge_to_pass_v2 hold) inside the truck behind the window."""
    import barista
    ahead, aside, height = barista.HOLDS['counter_edge_to_pass_v2']
    # In-memory only: the template hold, raised with the cook's floor so the pose relative to his body is unchanged.
    barista.HOLDS[gid] = (ahead, aside, height + COOK_FLOOR)
    facing = math.radians(facing_deg + barista.BODY_AWAY_DEG)
    machine_rot = facing - math.pi / 2 - math.radians(barista.BODY_AWAY_DEG)
    place = Matrix.Translation(Vector((feet[0], feet[1], COOK_FLOOR))) @ Matrix.Rotation(machine_rot, 4, 'Z') \
        @ Matrix.Translation(-barista.FEET_LOCAL)
    anchor = P.A.empty('Cook working spot inside the truck', place.translation)
    anchor.rotation_euler.z = machine_rot
    bpy.context.view_layer.update()
    root = barista.add(P, anchor, state, gid)
    state['character_fade_floor'] = barista.FADE_FLOOR + COOK_FLOOR
    state['contacts'][-1].update(where='inside the food truck, behind the service window, in the recess',
                                 template_pose='counter_edge_to_pass_v2 (working, milk pitcher swirl)',
                                 feet_world=[feet[0], feet[1], COOK_FLOOR], fade_floor_m=state['character_fade_floor'])
    state['adaptations'].append('The cook (the approved barista rig in the counter_edge_to_pass_v2 working pose) stands '
                                'inside the truck behind the window, in profile, swirling the milk pitcher.')
    return root


def burgers(P, spots=BURGER_SPOTS, role='support'):
    """The approved Tripo burger (library model, default dot cleanup in memory) on the truck's inner counter."""
    from drafts.counter_case import library_model
    roots = []
    for x, y, turn in spots:
        root, meshes = library_model(P, 'burger', (x, y, INNER_TOP), role, turn)
        roots.append(root)
    return roots


def _points(drawing):
    attr = drawing.attributes.get('position')
    if attr is None:
        return None
    points = np.empty((len(attr.data), 3), dtype=np.float32); attr.data.foreach_get('vector', points.ravel())
    return points


def _pixels(scene, obj, points):
    camera = scene.camera
    fov_y = camera.data.angle_y if camera.data.sensor_fit == 'VERTICAL' else camera.data.angle
    w, h = scene.render.resolution_x, scene.render.resolution_y
    tan_y = math.tan(fov_y / 2); tan_x = tan_y * w / h
    m = np.asarray(camera.matrix_world.inverted() @ obj.matrix_world, dtype=np.float64)
    xyz = points @ m[:3, :3].T + m[:3, 3]; depth = np.maximum(-xyz[:, 2], 1e-7)
    return np.column_stack((xyz[:, 0] / depth * w / (2 * tan_x), xyz[:, 1] / depth * h / (2 * tan_y)))


def _silhouette(scene, collection):
    """Baked outer contour of the collection as a group (native Line Art, silhouette filtering), frame -> pixels."""
    gp = bpy.data.grease_pencils.new('Truck outline probe') if hasattr(bpy.data, 'grease_pencils') else bpy.data.grease_pencils_v3.new('Truck outline probe')
    obj = bpy.data.objects.new('Truck outline probe', gp); scene.collection.objects.link(obj)
    material = bpy.data.materials.new('Truck outline probe'); bpy.data.materials.create_gpencil_data(material)
    gp.materials.append(material)
    gp.layers.new('Outline', set_active=True)
    mod = obj.modifiers.new('Outline', 'LINEART')
    mod.source_type = 'COLLECTION'; mod.source_collection = collection
    mod.target_layer = 'Outline'; mod.target_material = material
    mod.use_contour = True; mod.use_crease = False; mod.use_intersection = False; mod.use_material = False
    mod.use_edge_mark = False; mod.use_loose = False; mod.use_light_contour = False; mod.use_shadow = False
    mod.silhouette_filtering = 'GROUP'
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.lineart_bake_strokes(bake_all=False)
    result = {}
    for layer in obj.data.layers:
        for frame in layer.frames:
            scene.frame_set(frame.frame_number); bpy.context.view_layer.update()
            points = _points(frame.drawing)
            if points is not None and len(points):
                result[frame.frame_number] = _pixels(scene, obj, points)
    bpy.data.objects.remove(obj, do_unlink=True)
    return result


def install_stroke_treatment(meshes, outline=False, min_px=MIN_STROKE_PX, interior=INTERIOR_SHARE, report=None):
    """Wraps lineart_render.strokes_setup in this process: the role collection holding `meshes` loses strokes shorter
    than `min_px` screen pixels per frame (the objects-page dot filter) and, with `outline`, keeps its outer contour
    at full layer opacity while interior contours get `interior` of it. Other collections are untouched."""
    import lineart_render as L
    original = getattr(L.strokes_setup, 'p0_original', L.strokes_setup)
    names = {m.name for m in meshes}
    log = report if report is not None else {}

    def wrapped(scene, collection, args, distance, fov_y, motion_end):
        obj, counts = original(scene, collection, args, distance, fov_y, motion_end)
        if not names & {o.name for o in collection.all_objects}:
            return obj, counts
        current = scene.frame_current
        sil = _silhouette(scene, collection) if outline else {}
        dropped = 0; outline_share = []
        for layer in obj.data.layers:
            for frame in layer.frames:
                scene.frame_set(frame.frame_number); bpy.context.view_layer.update()
                drawing = frame.drawing; points = _points(drawing)
                if points is None:
                    continue
                px = _pixels(scene, obj, points)
                drop, start = [], 0
                for index, stroke in enumerate(drawing.strokes):
                    end = start + len(stroke.points)
                    if float(np.linalg.norm(np.diff(px[start:end], axis=0), axis=1).sum()) < min_px:
                        drop.append(index)
                    start = end
                if drop:
                    keep = np.ones(len(points), bool); start = 0
                    for index, stroke in enumerate(drawing.strokes):
                        end = start + len(stroke.points)
                        if index in drop:
                            keep[start:end] = False
                        start = end
                    drawing.remove_strokes(indices=drop); dropped += len(drop)
                    px = px[keep]
                if outline:
                    ref = sil.get(frame.frame_number)
                    if ref is None:
                        ref = sil[min(sil, key=lambda k: abs(k - frame.frame_number))]
                    near = np.full(len(px), np.inf)
                    for a in range(0, len(px), 2048):
                        chunk = px[a:a + 2048]
                        near[a:a + 2048] = np.sqrt(((chunk[:, None, :] - ref[None, :, :]) ** 2).sum(-1)).min(1)
                    on = near <= OUTLINE_PX
                    value = np.where(on, 1., interior).astype(np.float32)
                    opacity = drawing.attributes.get('opacity') or drawing.attributes.new('opacity', 'FLOAT', 'POINT')
                    opacity.data.foreach_set('value', value)
                    outline_share.append(float(on.mean()) if len(on) else 0.)
        scene.frame_set(current); bpy.context.view_layer.update()
        obj.data.update_tag()
        log[collection.name] = dict(short_strokes_removed=dropped, min_stroke_px=min_px, outline_emphasis=outline,
                                    interior_share=interior if outline else None,
                                    outline_point_share=round(float(np.mean(outline_share)), 3) if outline_share else None)
        print('TRUCK_STROKES', collection.name, log[collection.name], flush=True)
        return obj, counts

    wrapped.p0_original = original
    L.strokes_setup = wrapped
    return log
