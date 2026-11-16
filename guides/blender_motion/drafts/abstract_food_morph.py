"""abstract_food_morph (owner review 2026-11-17, round 2): plate_low_push_in_v2 with the approved dishes cycling on one
dinner plate, all drawn in the P0 light-edge yellow (per-object `p0_line_color`, hero role): pasta, cut pizza with the
pulled slice, cake slice, croissant, pancakes, salad, back to pasta. Each swap is a scale transition about the plate
centre: the outgoing dish shrinks away, the next one grows in. No cutlery and no side plate for the whole cycle (the
cycle includes pizza and pastry). Round 1 (abstract shapes) is archived next to the draft.

`<template>__generic` (owner 2026-11-17: "generate all food guides in such way"): the same cycle on the plate of each
dish_variants template, carried by whatever carries the pasta there (plate root, turntable pivot, slide carrier, held
or table plate); the template camera is kept."""
import bpy
from mathutils import Vector
from drafts import dish_variants as DV
from drafts import plate_dishes as D

GID = 'abstract_food_morph'
TEMPLATE = 'plate_low_push_in_v2'
# The P0 light-edge yellow (STYLE.md "Drawing"), as a per-object line colour.
YELLOW = (1., .73, .17)
CYCLE = ('pasta', 'pizza', 'cake', 'pastry', 'pancakes', 'salad')
# `abstract_food_morph__still_<dish>` shows one dish on the plate at the target
# camera (render_p0 refits the camera only if that dish leaves the safe band), for the owner's stills.
IDS = (GID,) + tuple(f'{GID}__still_{d}' for d in CYCLE)
# plate_low_push_in_v2 reuses the pilot as its generic version.
GENERIC = tuple(f'{t}__generic' for t in DV.TEMPLATES if t != TEMPLATE)
IDS += GENERIC
# A dish whose dish version was skipped for a template (dish_batch.SKIP) leaves that template's cycle.
LEFT_OUT = {'plate_tissue_slide': ('pizza',)}
# Cake slice: no approved dish version yet; 0.6 of the source (14 x 16 x 14.5 cm) makes an about 3.3 x 3.8 in slice,
# 3.4 in tall, beside the pasta mound's 3 in (judgement); turned 180 deg so its layered long side faces the lens (fewest scan dots of four turns probed).
CAKE = dict(scale=.6, turn=180., back=D.BACK)
# Demonstration frames (15 fps): a swap is OUT frames of shrink then IN frames of growth (0.2 s each), and each middle
# dish stays full for an even share of the frames left, at most FULL_MAX, so a dish comes round about every 0.8 s
# (pilot, 60 frames: 5, 5, 4, 4, 4); pasta is full at both ends and through the holds, so the first frame equals the
# last; frames beyond FULL_MAX per dish (5 s and 6 s clips) lengthen the pasta at the start and end of the move.
OUT = IN = 3
FULL_MAX = 5
# Hidden dishes wait far above the table, outside the camera's view.
AWAY = Vector((0, 0, 50.))


def smooth(t):
    return t * t * (3 - 2 * t)


def schedule(n=60, cycle=CYCLE):
    """Per-dish scale for each demonstration frame index 0..n-1."""
    scales = {d: [] for d in cycle}

    def frame(shown):
        for d in cycle:
            scales[d].append(shown.get(d, 0.))
    middle = len(cycle) - 1
    spare = n - 2 - len(cycle) * (OUT + IN)
    share, extra = divmod(spare, middle)
    full = [min(share + (k < extra), FULL_MAX) for k in range(middle)]
    ends = spare - sum(full)
    for _ in range(1 + (ends + 1) // 2):
        frame({'pasta': 1.})
    order = cycle[1:] + ('pasta',)
    current = 'pasta'
    for k, nxt in enumerate(order):
        for i in range(1, OUT + 1):
            frame({current: 1 - smooth(i / (OUT + 1))})
        for i in range(1, IN + 1):
            frame({nxt: smooth(i / (IN + 1))})
        for _ in range(full[k] if k < middle else 1 + ends // 2):
            frame({nxt: 1.})
        current = nxt
    assert all(len(v) == n for v in scales.values()), {d: len(v) for d, v in scales.items()}
    return scales


def cake(P):
    """The approved cake slice as its line-art approval prepared it (dot cleanup in memory, shape unchanged)."""
    from drafts.counter_case import library_model
    root, _ = library_model(P, 'cake_slice', (0, CAKE['back'], D.WELL), 'hero', CAKE['turn'])
    root.scale = (CAKE['scale'],) * 3
    return root


def build(gid, record, P):
    generic = gid in GENERIC
    template = gid.split('__')[0] if generic else TEMPLATE
    dishes_in = tuple(d for d in CYCLE if d not in LEFT_OUT.get(template, ())) if generic else CYCLE
    state = DV.build_template(template, dict(record, id=template), P)
    camera = DV.fit_camera(state)
    DV.template_fit(template, state, camera)
    pasta = [o for o in bpy.context.scene.objects if o.name.startswith(DV.PASTA)]
    holder = next(o for o in pasta if o.name.startswith('Pasta coil')).parent
    plate = next((o for o in holder.children if o.name.startswith('Plate with formed rim')), None)
    if plate is None:
        plate_root = next(o for o in bpy.context.scene.objects if o.name.startswith('Pasta plate'))
        plate = next(o for o in plate_root.children if o.name.startswith('Plate with formed rim'))
    # A template whose pasta is not its hero (verdict: the face) keeps the pasta's role and does not slide dishes.
    role = next(o for o in pasta if o.name.startswith('Pasta coil')).get('composition_role', 'hero') if generic else 'hero'
    slides = not generic or any(o in state['hero'] for o in pasta)
    bpy.context.view_layer.update()
    world_scale = plate.matrix_world.to_3x3().col[0].length
    centre = plate.matrix_world.translation.copy()
    base = centre.z + D.plate_top(0.) * world_scale
    move = plate.matrix_world @ DV.REFERENCE.inverted()
    dishes = {'pasta': pasta}
    report = {}
    for dish in dishes_in[1:]:
        root = cake(P) if dish == 'cake' else getattr(D, dish)(P)
        if generic and dish == 'pancakes' and template in DV.OVERHEAD:
            D.overhead_pancakes(root)
        lift = D.rest_on_plate(root)
        root.matrix_world = move @ root.matrix_world
        P.attach(root, holder)
        dishes[dish] = root
        report[dish] = dict(lift_m=round(lift, 4))
    for dish, items in dishes.items():
        for obj in (items if dish == 'pasta' else D.meshes(items)):
            P.A.tag(obj, role, f'The {dish} on the dinner plate, one dish of the yellow cycle')
            obj['p0_line_color'] = list(YELLOW)
    # Same placement as the approved dish versions: every dish but pizza slides on the plate until it fits the safe
    # band at the template camera (dish_variants.keep_in_band).
    kept_hero = list(state['hero'])
    for dish in dishes_in[1:]:
        state['hero'] = D.meshes(dishes[dish])
        if dish != 'pizza' and slides:
            report[dish]['slide_m'] = round(DV.keep_in_band(state, camera, dishes[dish], plate), 4)
        if generic:
            low, high = DV.rows(state, camera)
            report[dish].update(slide_m=report[dish].get('slide_m', 0.), target_rows=[round(low, 3), round(high, 3)])
    state['hero'] = kept_hero
    DV.drop(camera)
    state['P'] = P
    # The pastry row (no cutlery, no side plate) is the strictest setting in the cycle.
    setting = DV.place_setting(state, plate, [m for d in dishes_in[1:] for m in D.meshes(dishes[d])] + pasta, 'pastry', 1., world_scale)
    del state['P']
    pivots = {}
    for dish, items in dishes.items():
        pivot = bpy.data.objects.new(f'Food cycle pivot / {dish}', None)
        bpy.context.scene.collection.objects.link(pivot)
        pivot.location = (centre.x, centre.y, base)
        P.attach(pivot, holder)
        for obj in (items if dish == 'pasta' else [items]):
            P.attach(obj, pivot)
        pivots[dish] = (pivot, pivot.location.copy())
    still = gid.split('__still_')[1] if '__still_' in gid else None
    frames = record['durationSec'] * 15
    scales = {d: [float(d == still)] * frames for d in dishes_in} if still else schedule(frames, dishes_in)

    def cycle(u):
        i = round(u * (frames - 1))
        frame = bpy.context.scene.frame_current
        for dish, (pivot, home) in pivots.items():
            s = scales[dish][i]
            pivot.scale = (max(s, .001),) * 3
            pivot.location = home if s > 0 else home + AWAY
            pivot.keyframe_insert('scale', frame=frame); pivot.keyframe_insert('location', frame=frame)
    state['actions'].append(cycle)
    if still:
        state['hero'] = dishes['pasta'] if still == 'pasta' else D.meshes(dishes[still])
    cycle(1.)
    bpy.context.view_layer.update()
    if not generic:
        state['dish'] = dict(kind='cycle', template=TEMPLATE, cycle=list(CYCLE), dishes=report, place_setting=setting)
        state['adaptations'].append('The approved dishes cycle on the plate_low_push_in_v2 dinner plate in yellow lines (pasta, pizza, '
                                    'cake slice, croissant, pancakes, salad, pasta), each swap a 0.2 s shrink then a 0.2 s growth about '
                                    'the plate centre; no cutlery, no side plate: ' + str(setting) + '; dishes: ' + str(report))
        return state
    names = dict(pasta='pasta', pizza='pizza', cake='cake slice', pastry='croissant', pancakes='pancakes', salad='salad')
    order = ', '.join(names[d] for d in dishes_in + ('pasta',))
    state['dish'] = dict(kind='generic', template=template, cycle=list(dishes_in), dishes=report, place_setting=setting, role=role)
    state['adaptations'].append(f'Generic version of {template}: the approved dishes cycle on its dinner plate in yellow lines '
                                f'({order}), each swap a 0.2 s shrink then a 0.2 s growth about the plate centre, carried by '
                                f'the template\'s plate carrier; {role} role; no cutlery, no side plate: ' + str(setting)
                                + '; dishes: ' + str(report))
    return state
