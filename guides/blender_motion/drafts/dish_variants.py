"""Dish variants of the plate guides (batch, owner go-ahead 2026-11-14): `<template>__<dish>` builds the template's scene
unchanged, then replaces the pasta on its plate with a pilot dish (plate_dishes.PLACEMENT), carried by whatever carries the
pasta (the plate root, a turntable pivot, a held or slid plate) and scaled with that plate. The template camera is kept:
its own safe-band fit with the pasta is applied first, so render_p0 moves the camera only if the dish needs more room."""
import json
import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view
from drafts import plate_dishes as D

TEMPLATES = ('plate_low_push_in_v2', 'plate_high_orbit_v2', 'plate_rise_overhead_v2', 'plate_top_orbit',
             'plate_tissue_slide', 'handoff_plate_lands', 'handoff_plate_lands_v2', 'room_tilt_up_from_plate',
             'verdict_high_plate_v2', 'plate_turntable')
DISHES = D.DISHES
IDS = tuple(f'{t}__{d}' for t in TEMPLATES for d in DISHES)
# The pilot dishes are placed on the reference plate: centred at the origin, base at the table top.
REFERENCE = Matrix.Translation((0, 0, .785))
PASTA = ('Pasta coil', 'Basil leaf')
# Owner-approved variants (review 2026-11-15) keep the 2026-11-14 build (template place setting) so they render the same.
APPROVED = ('plate_rise_overhead_v2__salad', 'plate_tissue_slide__salad', 'plate_top_orbit__salad', 'plate_turntable__salad')
# Overhead guides get the overhead pancake arrangement (plate_dishes.OVERHEAD_PANCAKES).
OVERHEAD = ('plate_rise_overhead_v2', 'plate_top_orbit')
# verdict_high_plate_v2 dish variants (owner review 2026-11-15): the plate rests on the table in frame, the creator keeps
# the template pose and nod with the free hand resting on the table; no held plate, no waiter grip.
VERDICT = 'verdict_high_plate_v2'
# Her plate's centre on the table: its rim 2 cm in from her table edge (people_v2.TABLE_EDGE_Y -.22), 9.5 cm toward
# her right: her left forearm rests on the table from x 0.112 m, and the fork on her left (2 cm clear of the dinner
# plate) then stays over 1 cm clear of it.
VERDICT_PLATE = (-.095, -.39, .785)
PLATE_RIM_R = .151
# Owner review 2026-11-16: the pancakes' fork and knife swap sides of the plate (as seen from the camera).
SWAPPED_CUTLERY = ('verdict_high_plate_v2__pancakes',)
# Owner review 2026-11-16: the pizza refit shows the server's whole forearm, so it fades out before its cut end, about
# where the template's frame edge crops it (0.25-0.31 m from the grip); radii in metres from the grip (render_p0).
HAND_FADE = {'handoff_plate_lands_v2__pizza': (.18, .32)}


def corners(objects):
    deps = bpy.context.evaluated_depsgraph_get()
    return [o.matrix_world @ Vector(c) for o in objects for c in o.evaluated_get(deps).bound_box]


# render_p0's safe band (hero rows at the target frame, from the bottom).
BAND = (.356, .714)
# Pizza may take a camera refit (owner 2026-11-14); another dish that overflows the band at the template camera slides
# toward or away from the lens on the plate, in steps, at most this far.
SHIFT_STEP, SHIFT_MAX = .0025, .03


def rows(state, camera):
    import render_p0
    render_p0.aim(camera, state['target_position'], state['target_aim'], state.get('camera_up'))
    ys = [world_to_camera_view(bpy.context.scene, camera, v).y for v in corners(state['hero'])]
    return min(ys), max(ys)


def fit_camera(state):
    scene = bpy.context.scene
    camera = bpy.data.objects.new('Dish variant fit camera', bpy.data.cameras.new('Dish variant fit lens'))
    scene.collection.objects.link(camera)
    camera.data.lens = state.get('lens_mm', 24); camera.data.sensor_fit = 'VERTICAL'
    camera.data.sensor_width = camera.data.sensor_height = 36
    return camera


def drop(camera):
    data = camera.data; bpy.data.objects.remove(camera, do_unlink=True); bpy.data.cameras.remove(data)


def template_fit(template, state, camera):
    """render_p0's safe-band fit of the template's own hero (the pasta), so a dish variant starts from the published
    camera; render_p0 then refits only for the dish."""
    import render_p0
    for action in state['actions']:
        action(1.)
    bpy.context.view_layer.update()
    points = corners(state['hero']); p, t = state['target_position'].copy(), state['target_aim'].copy()
    for _ in range(200):
        render_p0.aim(camera, p, t, state.get('camera_up'))
        ys = [world_to_camera_view(bpy.context.scene, camera, v).y for v in points]
        if min(ys) >= BAND[0] and max(ys) <= BAND[1]:
            break
        if template == 'plate_tissue_slide':
            p += Vector((0, -.015, 0)); t += Vector((0, -.015, 0))
        else:
            p = t + (p - t) * 1.035
    else:
        raise ValueError('Template does not fit the safe band: ' + template)
    state['target_position'], state['target_aim'] = p, t


def keep_in_band(state, camera, root, plate):
    """Slides the dish along the plate toward the lens (top overflow) or away (bottom overflow) until its hero rows fit
    the band at the template camera; returns the slide in metres (0 when it fits or the dish is not the hero)."""
    if not any(o in state['hero'] for o in D.meshes(root)):
        return 0.
    centre = plate.matrix_world.translation; lens = state['target_position'] - centre
    toward = (lens - plate.matrix_world.to_3x3().col[2].normalized() * lens.dot(plate.matrix_world.to_3x3().col[2].normalized())).normalized()
    moved = 0.
    while True:
        low, high = rows(state, camera)
        if low >= BAND[0] and high <= BAND[1]:
            return moved
        step = SHIFT_STEP if high > BAND[1] else -SHIFT_STEP
        if abs(moved + step) > SHIFT_MAX + 1e-9 or (high > BAND[1] and low < BAND[0]):
            return moved
        root.matrix_world = Matrix.Translation(toward * step) @ root.matrix_world
        bpy.context.view_layer.update(); moved += step


def cutlery_roots(centre):
    """The place-setting fork and knife roots beside the plate at `centre` (other tables' settings excluded)."""
    kinds = dict(fork='Fork', knife='Dinner knife')
    out = {k: [] for k in kinds}
    bpy.context.view_layer.update()
    for o in bpy.context.scene.objects:
        w = o.matrix_world.translation
        if o.type != 'EMPTY' or (w - centre).xy.length > .40 or abs(w.z - centre.z) > .06:
            continue
        for kind, name in kinds.items():
            if o.name.split('.')[0] == name:
                out[kind].append(o)
    return out


def remove_tree(root):
    for o in list(root.children_recursive) + [root]:
        bpy.data.objects.remove(o, do_unlink=True)


def flat_gap(points, boxes):
    """Smallest horizontal distance from the points to the XY boxes."""
    best = 9.
    for (x0, y0, x1, y1) in boxes:
        for p in points:
            dx = max(x0 - p.x, 0., p.x - x1); dy = max(y0 - p.y, 0., p.y - y1)
            best = min(best, (dx * dx + dy * dy) ** .5)
    return best


def place_setting(state, plate, food, dish, scale, world_scale):
    """Applies plate_dishes.PLACE_SETTING around the swapped plate (already at its final, u = 1 place): removes the
    cutlery and side plate the dish does not get; for kept cutlery adds the missing knife (mirroring the fork across the
    plate) and moves fork and knife sideways until their nearest point is `clear` from the plate edge, then slides any piece toward the diner until it
    is 1 cm clear of the other tabletop pieces. Returns a short report."""
    setting = D.PLACE_SETTING[dish]
    report = dict(plate_scale=round(scale, 4), plate_diameter_in=round(2 * PLATE_RIM_R * world_scale * scale / .0254, 2))
    bpy.context.view_layer.update()
    centre = plate.matrix_world.translation.copy()
    roots = cutlery_roots(centre)
    placed = {o.name: (o.matrix_world.translation.copy(), [m.matrix_world @ v.co for m in D.meshes(o) for v in m.data.vertices])
              for k in roots for o in roots[k]}
    rim = PLATE_RIM_R * world_scale
    if not setting['side_plate']:
        side = [o for o in bpy.context.scene.objects if o.name.startswith('Plate with formed rim') and o != plate
                and (o.matrix_world.translation - centre).xy.length < .50 and abs(o.matrix_world.translation.z - centre.z) < .06]
        for o in side:
            bpy.data.objects.remove(o, do_unlink=True)
        report['side_plates_removed'] = len(side)
    if not setting['cutlery']:
        report['cutlery_removed'] = [o.name for k in roots for o in roots[k]]
        for k in roots:
            for o in roots[k]:
                remove_tree(o)
        follow_points(state, centre, scale, rim, placed, {})
        return report
    if not roots['knife'] and roots['fork']:
        fork = roots['fork'][0]; f = fork.matrix_world.translation
        knife = state['P'].A.knife((2 * centre.x - f.x, f.y, f.z - .01))
        roots['knife'].append(knife); report['knife_added'] = True
    radius = PLATE_RIM_R * world_scale * scale
    moved = {}
    for kind in ('fork', 'knife'):
        for o in roots[kind]:
            side = 1. if o.matrix_world.translation.x > centre.x else -1.
            total = 0.
            for _ in range(4):
                bpy.context.view_layer.update()
                gap = min((m.matrix_world @ v.co - centre).xy.length for m in D.meshes(o) for v in m.data.vertices) - radius
                step = setting['clear'] - gap
                if abs(step) < 1e-4:
                    break
                o.matrix_world = Matrix.Translation((side * step, 0, 0)) @ o.matrix_world; total += step
            moved[o.name] = dict(clear_in=round(setting['clear'] / .0254, 2), moved_out_in=round(total / .0254, 2))
    report['cutlery_moved_in'] = moved
    bpy.context.view_layer.update()
    cutlery = [o for k in roots for o in roots[k]]
    mine = set(D.meshes(plate)) | set(food) | {m for c in cutlery for m in D.meshes(c)}
    boxes = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or o in mine or o.get('p0_hand') or o.get('composition_role') in ('structure', 'background', 'hand', 'character'):
            continue
        cs = corners([o])
        if min(c.z for c in cs) > centre.z + .03 or max(c.z for c in cs) < centre.z - .01:
            continue
        boxes.append((min(c.x for c in cs), min(c.y for c in cs), max(c.x for c in cs), max(c.y for c in cs)))
    slid = {}
    for o in cutlery:
        step = 0
        while step < 20:
            pts = [m.matrix_world @ v.co for m in D.meshes(o) for v in list(m.data.vertices)[::3]]
            if flat_gap(pts, boxes) >= .01:
                break
            o.matrix_world = Matrix.Translation((0, -.005, 0)) @ o.matrix_world
            bpy.context.view_layer.update(); step += 1
        if step:
            slid[o.name] = round(step * .005 / .0254, 2)
    if slid:
        report['cutlery_slid_toward_diner_in'] = slid
    follow_points(state, centre, scale, rim, placed, {o.name: o.matrix_world.translation.copy() for o in cutlery})
    return report


def follow_points(state, centre, scale, rim, before, after):
    """Triangle points follow the place setting: a point on the dinner plate rim moves to the scaled rim; a point on a
    fork or knife moves with it, or to the plate rim on that side when the piece is removed."""
    points = state.get('triangle_points')
    if not points:
        return
    for k, point in enumerate(points):
        flat = (point - centre).xy.length
        piece = next((name for name, (_, pts) in before.items() if min((point - q).xy.length for q in pts) < .035), None)
        if piece is not None:
            if piece in after:
                points[k] = point + (after[piece] - before[piece][0])
            else:
                side = (point - centre).xy.normalized()
                points[k] = Vector((centre.x + side.x * rim * scale, centre.y + side.y * rim * scale, centre.z + .030 * scale))
        elif .10 < flat < rim + .01 and point.z < centre.z + .04:
            offset = point - centre
            points[k] = Vector((centre.x + offset.x * scale, centre.y + offset.y * scale, centre.z + offset.z * scale))


def follow_rim(state, plate, scale, world_scale):
    """Rim grips (plate_turntable, handoff_plate_lands_v2) follow the smaller rim: each hand moves rigidly in its own
    frame, inward by the rim shrink and down by the rim drop (kept 1 mm over the table), for every frame."""
    hands = [o for o in bpy.context.scene.objects if o.get('p0_hand')]
    if not hands or scale == 1.:
        return []
    for action in state['actions']:
        action(.3)
    bpy.context.view_layer.update()
    centre = plate.matrix_world.translation
    table = centre.z
    report = []
    for hand in hands:
        mesh = next(o for o in hand.children_recursive if o.type == 'MESH')
        radial = hand.matrix_world.translation - centre; radial.z = 0; radial.normalize()
        low = min((mesh.matrix_world @ v.co).z for v in mesh.data.vertices)
        drop = min(.030 * world_scale * (1 - scale), max(0., low - table - .001))
        delta = -radial * (.146 * world_scale * (1 - scale)) + Vector((0, 0, -drop))
        local = hand.matrix_world.to_3x3().inverted() @ delta
        def follow(u, hand=hand, local=local):
            bpy.context.view_layer.update()
            # Location only: re-decomposing the rotation every frame drifts and breaks first frame = last frame.
            space = (hand.parent.matrix_world @ hand.matrix_parent_inverse).to_3x3() if hand.parent else Matrix.Identity(3)
            hand.location += space.inverted() @ (hand.matrix_world.to_3x3() @ local)
            hand.keyframe_insert('location'); hand.keyframe_insert('rotation_euler')
            bpy.context.view_layer.update()
        state['actions'].append(follow)
        report.append(dict(hand=hand.name, inward_in=round(delta.xy.length / .0254, 2), down_in=round(drop / .0254, 2)))
    for action in state['actions']:
        action(1.)
    bpy.context.view_layer.update()
    return report


def build_template(template, record, P, side=1.):
    if template != VERDICT:
        return P.build(template, dict(record, id=template))
    from drafts import people_v2 as people
    gid = VERDICT + '__table'
    people.GUIDES[gid] = dict(people.GUIDES[VERDICT], act=None, nod=True)
    state = people.build(gid, dict(record, id=VERDICT), P)
    root = next(o for o in bpy.context.scene.objects if o.name.startswith('Pasta plate'))
    fork = next(o for o in bpy.context.scene.objects if o.type == 'EMPTY' and o.name.split('.')[0] == 'Fork')
    root.location = VERDICT_PLATE
    # The template's own place-setting fork, on her left of the plate as in place_setting (17 cm from the centre).
    fork.location = (VERDICT_PLATE[0] + side * .17, VERDICT_PLATE[1], fork.location.z)
    for o in P.members(root):
        if o.name.startswith('Plate with formed rim'):
            P.A.tag(o, 'support', 'Her plate resting on the table in front of her')
    bpy.context.view_layer.update()
    state['adaptations'].append('The plate rests on the table in front of her, in frame; no held plate and no waiter grip; '
                                'her free hand rests on the table and she keeps the verdict nod (owner review 2026-11-15).')
    return state


def build(gid, record, P):
    template, dish = gid.split('__', 1)
    assert record.get('dish', dish) == dish, (gid, record.get('dish'))
    approved = gid in APPROVED
    state = build_template(template, record, P, side=-1. if gid in SWAPPED_CUTLERY else 1.)
    if gid in HAND_FADE:
        for hand in [o for o in bpy.context.scene.objects if o.get('p0_hand')]:
            hand['p0_grip_fade'] = HAND_FADE[gid]
        state['adaptations'].append(f'The server\'s forearm fades out {HAND_FADE[gid][1] / .0254:.1f} in from the grip, '
                                    'before its cut end, as the template\'s frame edge crops it (owner review 2026-11-16).')
    if gid in SWAPPED_CUTLERY:
        state['adaptations'].append('Fork and knife swap sides of the plate as seen from the camera: fork on her right, '
                                    'knife on her left (owner review 2026-11-16).')
    camera = fit_camera(state)
    template_fit(template, state, camera)
    pasta = [o for o in bpy.context.scene.objects if o.name.startswith(PASTA)]
    roots = {o.parent.name for o in pasta if o.parent}
    holder = next(o for o in pasta if o.name.startswith('Pasta coil')).parent
    plate_root = next(o for o in bpy.context.scene.objects if o.name.startswith('Pasta plate'))
    plate = next(o for o in plate_root.children if o.name.startswith('Plate with formed rim'))
    assert len(roots) == 1 and len([o for o in bpy.context.scene.objects if o.name.startswith('Pasta plate')]) == 1, gid
    role = next(o for o in pasta if o.name.startswith('Pasta coil')).get('composition_role', 'hero')
    gone = {o.name for o in pasta}
    swap_hero = any(o.name in gone for o in state['hero'])
    kept_hero = [o for o in state['hero'] if o.name not in gone]
    for obj in pasta:
        bpy.data.objects.remove(obj, do_unlink=True)

    setting = dict(plate=1.) if approved else D.PLACE_SETTING[dish]
    scale = setting['plate']
    world_scale = plate.matrix_world.to_3x3().col[0].length
    root = getattr(D, dish)(P)
    if dish == 'pancakes' and template in OVERHEAD and not approved:
        D.overhead_pancakes(root)
    lift = D.rest_on_plate(root, scale=scale)
    food = D.meshes(root)
    bpy.context.view_layer.update()
    reference = [o.matrix_world @ v.co for o in food for v in o.data.vertices]
    top = max(p.z for p in reference)
    move = plate.matrix_world @ REFERENCE.inverted()
    root.matrix_world = move @ root.matrix_world
    P.attach(root, holder)
    if scale != 1.:
        plate.scale = plate.scale * scale
        bpy.context.view_layer.update()
    why = f'The {dish} on the {template} plate (replaces the pasta)'
    for obj in food:
        P.A.tag(obj, role, why if role == 'hero' else why + '; the template\'s ' + role + ' role')
    if swap_hero:
        state['hero'] = kept_hero + food
    setting_report = hands = None
    if not approved:
        state['P'] = P
        setting_report = place_setting(state, plate, food, dish, scale, world_scale)
        del state['P']
        hands = follow_rim(state, plate, scale, world_scale)
    slide = 0. if dish == 'pizza' else keep_in_band(state, camera, root, plate)
    drop(camera)
    # The food point of a triangle follows the dish top (the pasta mound was about 8 cm high).
    points = state.get('triangle_points')
    if points:
        bpy.context.view_layer.update()
        world = [o.matrix_world @ v.co for o in food for v in o.data.vertices]
        here = Vector((sum(q.x for q in world) / len(world), sum(q.y for q in world) / len(world), max(q.z for q in world)))
        flat = plate.matrix_world.translation
        for k, point in enumerate(points):
            if (point.xy - flat.xy).length < .06 and point.z > flat.z + .04:
                points[k] = here
    state['dish'] = dict(kind=dish, template=template, lift_m=round(lift, 4), top_m=round(top - .785, 4), slide_m=round(slide, 4))
    if setting_report is not None:
        state['dish'].update(place_setting=setting_report, rim_hands=hands)
        state['adaptations'].append(f'Place setting for {dish} (plate_dishes.PLACE_SETTING, owner rule 2026-11-15): '
                                    + json.dumps(setting_report) + (f'; rim grips follow the smaller rim: {json.dumps(hands)}' if hands else ''))
    if slide:
        state['adaptations'].append(f'The {dish} sits {abs(slide) * 100:.1f} cm ({abs(slide) / .0254:.2f} in) '
                                    f'{"toward" if slide > 0 else "away from"} the lens from its pilot place on the plate, so it fits the '
                                    'safe band at the template camera.')
    if approved:
        state['adaptations'].append(f'Dish variant of {template}: the {dish} replaces the pasta on the same plate and moves with it; '
                                    'camera path, setting, light, hands and timing are the template\'s.')
    else:
        state['adaptations'].append(f'Dish variant of {template}: the {dish} replaces the pasta on the template plate and moves with it; '
                                    'camera path, light, hands and timing are the template\'s; the place setting is the dish\'s.')
    return state
