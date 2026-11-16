"""plate_low_push_in with another approved dish on the same 0.30 m plate (pilot 2026-11-14): one variant id per dish,
the place setting, camera path, light and timing of plate_low_push_in unchanged."""
import math
import bpy
from mathutils import Matrix, Vector
from drafts.common import new_state, finish

TEMPLATE = 'plate_low_push_in'
# The template's target after render_p0's safe-band fit of the pasta (scratch re-render 2026-11-14); fixed here so
# every dish is filmed from the same phone path instead of a dish-specific refit.
TARGET = (0., -.29983729124069214, .9013303518295288)
AIM = (0., 0., .84)
WELL = .794
# 1 cm behind the plate centre keeps the dish's near edge on the template's bottom hero row at the fixed camera.
BACK = .01
DISHES = ('pastry', 'pancakes', 'pizza', 'salad')
IDS = tuple(f'{TEMPLATE}__{dish}' for dish in DISHES)


def meshes(root):
    return [root] if root.type == 'MESH' else [o for o in root.children_recursive if o.type == 'MESH']


def plate_top(r, scale=1.):
    """Top surface height of A.plate (uniformly scaled by `scale`) above its base at radius r (its lathe profile)."""
    r /= scale
    for (r0, z0), (r1, z1) in [((0, .009), (.09, .009)), ((.09, .009), (.115, .015)), ((.115, .015), (.139, .030))]:
        if r <= r1:
            return scale * (z0 + (z1 - z0) * max(0., r - r0) / (r1 - r0))
    return scale * .030


def rest_on_plate(root, base=.785, scale=1.):
    """Raises the dish until no vertex is below the plate's top surface; returns the lift."""
    bpy.context.view_layer.update()
    lift = max(base + plate_top(math.hypot(p.x, p.y), scale) - p.z
               for o in meshes(root) for p in (o.matrix_world @ v.co for v in o.data.vertices))
    if lift > 0:
        root.location.z += lift
    return max(lift, 0.)


# Per-dish placement on the 0.30 m plate, centred at the origin with its base at z 0.785 (the reference plate); a guide
# whose plate sits elsewhere or is scaled moves the built dish with its plate (dish_variants.py).
# pastry: a 17 cm bakery croissant turned -18 deg (its arc sits `arc` m on +Y of its origin, before scaling).
# pizza, round 5 (owner review 2026-11-14): a 10 in round (0.847 of the source) almost the plate's size, flattened in its
# mesh from the centre share to the rim share of the source height (centre about 1.2 cm, crust rim about 1.5 cm); the
# slice is pulled 4.7 cm (0.055 of the source) toward the front right.
PLACEMENT = dict(
    pastry=dict(scale=.80, turn=-18., back=BACK, arc=.064),
    pancakes=dict(scale=.75, back=BACK),
    pizza=dict(scale=.847, centre=.21, rim=.26, pull=.055, angle=-60., turn=30., back=0.),
    salad=dict(scale=.90, back=BACK),
)
PIZZA = PLACEMENT['pizza']

# Place setting per dish (owner rule 2026-11-15, STYLE.md "Objects"): `plate` scales the 0.302 m (11.9 in) dinner
# plate, DESSERT makes the about 8 in dessert plate; `cutlery` lists what stays beside the plate (none: every fork,
# knife and the side plate go); `clear` is the horizontal room between the plate edge and the nearest point of kept
# cutlery (owner: fork and knife 2 cm clear). `dessert` is for future dessert dishes: dessert spoon and knife are
# an open object request (OBJECTS.md), so it has no cutlery until they are approved.
DESSERT = .2032 / .302
PLACE_SETTING = dict(
    pastry=dict(plate=DESSERT, cutlery=(), side_plate=False),
    pizza=dict(plate=1., cutlery=(), side_plate=True),
    pancakes=dict(plate=DESSERT, cutlery=('fork', 'knife'), clear=.02, side_plate=True),
    salad=dict(plate=1., cutlery=('fork', 'knife'), clear=.02, side_plate=True),
    dessert=dict(plate=DESSERT, cutlery=(), side_plate=True),
)

# Pancakes seen from overhead (owner review 2026-11-15): the approved stack's own parts rearranged so it reads from the
# top: layers offset in turn so each rim shows as a crescent, the syrup drips run over the visible edge, the cream and
# berry off-centre beside the butter, and two more of the approved berries on the top layer.
OVERHEAD_PANCAKES = dict(
    layers=((0., 0.), (.016, -.010), (-.008, .016), (.018, .008)),
    butter=(.020, -.026), cream=(-.030, .010), berries=((-.028, .009), (.030, .028), (-.006, -.040)),
    drips=(-20., 100., 220.),
)


def overhead_pancakes(root):
    """Rearranges a T.pancakes stack (unscaled, before placement) by OVERHEAD_PANCAKES; parts keep their shapes."""
    import assets as A
    import geometry as G
    d = OVERHEAD_PANCAKES
    layers = sorted([o for o in root.children if o.name.startswith('Rounded pancake layer')],
                    key=lambda o: min(v.co.z for v in o.data.vertices))
    for o, (x, y) in zip(layers, d['layers']):
        o.location.x += x; o.location.y += y
    top = d['layers'][-1]
    for o in list(root.children):
        if o.name.startswith('Butter'):
            o.location.x, o.location.y = d['butter'][0] + top[0], d['butter'][1] + top[1]
        elif o.name.startswith('Soft cream'):
            o.location.x, o.location.y = d['cream'][0] + top[0], d['cream'][1] + top[1]
        elif o.name.startswith('Berry on cream'):
            berry = o
        elif o.name.startswith('Syrup drip'):
            bpy.data.objects.remove(o, do_unlink=True)
    role = berry.get('composition_role', 'hero')
    bx, by = d['berries'][0]
    berry.location.x, berry.location.y = bx + top[0], by + top[1]
    for x, y in d['berries'][1:]:
        extra = A.ellipsoid('Berry on cream', (x + top[0], y + top[1], .074), (.009, .009, .010), role,
                            'One simple topping; no photographic microdetail')
        extra.parent = root; extra.matrix_parent_inverse.identity()
    # The approved drip contour (top edge, over the rim, down the top layer's side), turned to each drip angle.
    for angle in d['drips']:
        a = math.radians(angle)
        points = [(top[0] + r * math.cos(a), top[1] + r * math.sin(a), z)
                  for r, z in [(.060, .0645), (.075, .064), (.085, .054), (.0865, .045)]]
        drip = A.tag(G.tube('Syrup drip', points, .0018), role, 'A small connected syrup contour over the visible edge')
        drip.parent = root; drip.matrix_parent_inverse.identity()
    return root


def pastry(P):
    d = PLACEMENT['pastry']; scale = d['scale']
    root, _ = P.A.pastry((0, 0, 0))
    root.scale = (scale,) * 3; root.rotation_euler.z = math.radians(d['turn'])
    root.location = Vector((0, d['back'], WELL)) - root.rotation_euler.to_matrix() @ Vector((0, d['arc'] * scale, 0))
    return root


def pancakes(P):
    import p0_table_compositions as T
    d = PLACEMENT['pancakes']
    root = T.pancakes((0, d['back'], WELL)); root.scale = (d['scale'],) * 3
    return root


def pizza(P):
    import p0_table_compositions as T
    s = PIZZA['scale']
    root = T.imported_food('pizza', (0, PIZZA['back'], WELL), 'hero'); root.scale = (s,) * 3
    # Turned and flattened in the mesh, not on the root: render_p0 frames per-slice local bounding boxes, and a turned
    # root widens them; a flattening root scale would also squash the cut-face line tubes into ribbons.
    source = next(o for o in root.children if o.type == 'MESH')
    local = source.matrix_local; turn = Matrix.Rotation(math.radians(PIZZA['turn']), 4, 'Z')
    for v in source.data.vertices:
        q = turn @ (local @ v.co); u = min(1., max(0., (math.hypot(q.x, q.y) - .095) / .03))
        q.z *= PIZZA['centre'] + (PIZZA['rim'] - PIZZA['centre']) * u * u * (3 - 2 * u)
        v.co = local.inverted() @ q
    source.data.update()
    # Pulled front-right so the near cut gap faces the lens; solid cut faces with layer lines (round 4).
    T.slice_round(root, pulled=PIZZA['angle'], pull=PIZZA['pull'], lift=0., solid_cut=True)
    # The pulled slice overhangs the rim: tilt its crust up just enough to rest on the rim instead of lifting the round.
    pulled = next(o for o in root.children if o.name.startswith('Pizza slice 0'))
    def need(objs):
        bpy.context.view_layer.update()
        return max(.785 + plate_top(math.hypot(p.x, p.y)) - p.z for o in objs for p in (o.matrix_world @ v.co for v in o.data.vertices))
    mine = [pulled] + [o for o in pulled.children_recursive if o.type == 'MESH']
    rest = need([m for m in meshes(root) if m not in mine])
    for k in range(60):
        pulled.rotation_axis_angle[0] = -math.atan2(.001 * k / s, .15)
        if need(mine) <= rest + 1e-4:
            break
    return root


def salad(P):
    import p0_table_compositions as T
    d = PLACEMENT['salad']
    root = T.imported_food('salad_portion', (0, d['back'], WELL), 'hero'); root.scale = (d['scale'],) * 3
    return root


def build(gid, record, P):
    dish = gid.split('__', 1)[1]
    assert record.get('dish', dish) == dish, (gid, record.get('dish'))
    state = new_state()
    setting = P.place_setting(); plate = setting['plate']
    for obj in list(meshes(plate)):
        if not obj.name.startswith('Plate with formed rim'):
            bpy.data.objects.remove(obj, do_unlink=True)
    root = globals()[dish](P)
    lift = rest_on_plate(root)
    food = meshes(root)
    for obj in food:
        P.A.tag(obj, 'hero', f'The {dish} on the shared dinner plate is the shot subject')
    bpy.context.view_layer.update()
    points = [o.matrix_world @ v.co for o in food for v in o.data.vertices]
    top = max(points, key=lambda p: p.z)
    cx = sum(p.x for p in points) / len(points); cy = sum(p.y for p in points) / len(points)
    state['triangle_points'] = [Vector((cx, cy, top.z)), Vector((-.04, -.144, .815)), Vector((.18, .225, .795))]
    state['dish'] = dict(kind=dish, lift_m=round(lift, 4), top_m=round(top.z - .785, 4))
    state['adaptations'].append(f'Dish variant of {TEMPLATE}: the {dish} replaces the pasta on the same plate; '
                                'camera path, place setting, light and timing are the template\'s.')
    return finish(state, food, TARGET, AIM, lambda u, p, t: (t + (p - t) * (1 + 1.2 * (1 - P.smooth(u))), t))
