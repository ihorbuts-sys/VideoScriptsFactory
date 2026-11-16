"""One public visit route, reused by cafe, bakery and bar dressing packs."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as B
import build_reconstructed_scene as EXPORT

BASE = P.BASE
FPS = 15
DURATION = 34
COUNT = FPS * DURATION
CACHE = {}
CONTACTS = []


def meshes(root):
    return [o for o in root.children_recursive if o.type == 'MESH']


def role(root, name):
    values = {'hero': (.25, 1), 'support': (.13, .65), 'context': (.035, .22), 'absent': (0, 0)}
    fill, line = values[name]
    linear = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    for obj in meshes(root):
        actual_fill, actual_line = (0, 0) if obj.get('ghost_role') == 'absent' else (fill, line)
        obj.color = (linear(actual_fill), linear(actual_line), 0, 1)
        obj['guide_role'] = name


def load(aid, position=(0, 0, 0), turn=0, scale=1, quality=None):
    if quality is None:
        quality = 'scene-ready' if (P.ROOT / aid / 'tripo-generated/scene-ready/asset.blend').exists() else 'review'
    relative = ('asset.blend' if quality == 'authored' else 'reconstructed/asset.blend' if quality == 'local'
                else f'{quality}/asset.blend' if quality in ['functional', 'full-height', 'approved-v2']
                else f'tripo-generated/{quality}/asset.blend')
    path = P.ROOT / aid / relative
    assert path.exists(), path
    key = str(path)
    if key not in CACHE:
        with bpy.data.libraries.load(str(path), link=False) as (source, destination):
            destination.collections = [source.collections[0]]
        collection = destination.collections[0]
        CACHE[key] = collection
    else:
        original = CACHE[key]
        collection = bpy.data.collections.new(original.name + ' instance')
        clones = {o: o.copy() for o in original.objects}
        for old, clone in clones.items():
            collection.objects.link(clone)
            if old.parent in clones:
                clone.parent = clones[old.parent]
    bpy.context.scene.collection.children.link(collection)
    members = set(collection.objects)
    roots = [o for o in collection.objects if o.parent not in members]
    assert len(roots) == 1, (aid, [o.name for o in roots])
    placement = P.empty('Placement / ' + aid, position)
    placement.rotation_euler.z = turn
    placement.scale = (scale,) * 3
    placement['asset_family'] = aid
    placement['source_file'] = str(path.relative_to(BASE))
    # The source root includes calibration. Never overwrite its location/rotation.
    roots[0].parent = placement
    bpy.context.view_layer.update()
    role(placement, 'context')
    return placement


def surface(root, x, y, from_z=4):
    hits = []
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in meshes(root):
        evaluated = obj.evaluated_get(deps)
        inverse = evaluated.matrix_world.inverted()
        hit, point, normal, index = evaluated.ray_cast(inverse @ Vector((x, y, from_z)),
                                                     inverse.to_3x3() @ Vector((0, 0, -1)))
        if hit:
            world_normal = evaluated.matrix_world.to_3x3().inverted().transposed() @ normal
            if world_normal.z > .35:
                hits.append((evaluated.matrix_world @ point).z)
    assert hits, ('No actual support below', root.name, x, y)
    return max(hits)


def supported(aid, support, x, y, turn=0, scale=1, quality=None):
    root = load(aid, (x, y, 0), turn, scale, quality)
    z = surface(support, x, y)
    lo, hi = B.bounds(meshes(root))
    root.location.z += z - lo.z + .0005
    bpy.context.view_layer.update()
    low = min((o.matrix_world @ v.co).z for o in meshes(root) for v in o.data.vertices)
    CONTACTS.append(dict(asset=aid, support=support.name, xy=[x, y], surface_z=z, lowest_vertex_z=low,
                         centre_contact_error_m=abs(low - z)))
    return root


def wall(name, pos, size):
    obj = P.block('Room shell / ' + name, pos, size, 'cream', .018)
    obj.color = (0, 0, 0, 1)
    obj['ghost_role'] = 'absent'
    return obj


def cubic(points, t):
    if t <= points[0][0]:
        return Vector(points[0][1])
    if t >= points[-1][0]:
        return Vector(points[-1][1])
    i = next(i for i in range(len(points) - 1) if points[i][0] <= t < points[i + 1][0])
    t0, p0 = points[max(0, i - 1)]
    t1, p1 = points[i]
    t2, p2 = points[i + 1]
    t3, p3 = points[min(len(points) - 1, i + 2)]
    p0, p1, p2, p3 = map(Vector, [p0, p1, p2, p3])
    u = (t - t1) / (t2 - t1)
    m1 = (p2 - p0) / max(.001, t2 - t0) * (t2 - t1)
    m2 = (p3 - p1) / max(.001, t3 - t1) * (t2 - t1)
    return (2 * u**3 - 3 * u**2 + 1) * p1 + (u**3 - 2 * u**2 + u) * m1 + (-2 * u**3 + 3 * u**2) * p2 + (u**3 - u**2) * m2


def smooth(t, a, b):
    u = max(0, min(1, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


def setup(venue, out, full_height=False):
    CACHE.clear()
    CONTACTS.clear()
    P.clear()
    P.MATS.clear()
    scene = bpy.context.scene
    P.studio(scene)
    scene.name = 'Loca shared venue / ' + venue
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 48
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = COUNT
    scene.view_layers[0].material_override = None
    # Real holes in the wall; no wall mesh across the door or window.
    floor = wall('floor', (0, 2.65, -.045), (5.4, 5.3, .09))
    wall('public pavement', (0, -2, -.055), (8, 4, .11))
    wall('back wall', (0, 5.3, 1.5), (5.2, .16, 3))
    wall('left wall', (-2.6, 2.65, 1.5), (.16, 5.3, 3))
    wall('right wall front return', (2.6, .4, 1.5), (.16, .8, 3))
    wall('right wall back return', (2.6, 3.8, 1.5), (.16, 3, 3))
    wall('right wall under window', (2.6, 1.55, .01 if full_height else .525), (.16, 1.5, .02 if full_height else 1.05))
    wall('right wall above window', (2.6, 1.55, 2.91 if full_height else 2.7475), (.16, 1.5, .18 if full_height else .505))
    for name, x, width in [('left return', -2.27, .66), ('between openings', -.22, .86), ('right return', 2.18, .86)]:
        wall(name, (x, 0, 1.5), (width, .18, 3))
    wall('above entrance', (-1.3, 0, 2.61), (1.3, .18, .78))
    wall('under window', (1, 0, .01 if full_height else .445), (1.5, .18, .02 if full_height else .89))
    wall('above window', (1, 0, 2.91 if full_height else 2.6775), (1.5, .18, .18 if full_height else .645))
    door = load('glazed_door', (-1.3, 0, -.10))
    window = load('window', (1, 0, .02 if full_height else .91), quality='full-height' if full_height else None)
    side_window = load('window', (2.6, 1.55, .02 if full_height else 1.05), math.pi / 2, quality='full-height' if full_height else None)
    hinge = next(o for o in door.children_recursive if o.get('max_open_angle_deg'))
    awning = P.block('Exterior / yellow awning', (0, -.45, 2.92 if full_height else 2.64), (3.9, .9, .10), 'yellow', .04)
    awning.rotation_euler.x = -.10
    awning.color = (.015, .06, 0, 1)
    sign = load('signboard', (-2.1, -.17, 1.8), quality='authored')
    table = load('dining_table', (1.15, 1.55, 0))
    # Canonical chair front is -Y. Near chair looks +Y, far chair looks -Y.
    chairs = [load('dining_chair', (1.15, .80, 0), math.pi), load('dining_chair', (1.15, 2.30, 0))]
    plate = supported('saucer', table, 1.02, 1.35, scale=1.18, quality='local')
    far_plate = supported('saucer', table, 1.30, 1.75, scale=1.18, quality='local')
    saucer = supported('saucer', table, 1.39, 1.36, quality='local')
    if venue == 'bar':
        hero = supported('drinking_glass', saucer, 1.39, 1.36)
    else:
        hero = supported('latte_cup', saucer, 1.39, 1.36, turn=-.3)
    pastry = supported('croissant', plate, 1.02, 1.35, turn=.35,
                       quality='approved-v2' if (P.ROOT / 'croissant/approved-v2/asset.blend').exists() else 'local')
    second = supported('saucer', table, .97, 1.75, quality='local')
    second_cup = supported('latte_cup', second, .97, 1.75, turn=math.pi)
    menu = load('menu_board', (0, 5.12, 1.9))
    # Flat hanging resources face the visitor; their back is against the wall.
    counter = load('display_case' if venue == 'bakery' else 'bar_counter', (0, 4.55, 0))
    service = [counter, menu]
    if venue == 'bar':
        menu.location.x = .72
        for x in [-.8, .1, 1.0]:
            service.append(load('bar_stool', (x, 3.6, 0), math.pi))
        for z in [1.35, 1.95]:
            shelf = load('wall_shelf', (-.55, 5.05, z), quality='local')
            service.append(shelf)
            for x in [-.98, -.70, -.40, -.12]:
                service.append(supported('bottle', shelf, x, 4.96))
        service.append(supported('drinking_glass', counter, -.35, 4.35))
    elif venue == 'cafe':
        service.append(supported('kettle', counter, -.5, 4.4))
        service.append(supported('latte_cup', counter, .35, 4.35))
    else:
        shelf = load('wall_shelf', (0, 4.15, .60), quality='local')
        tongs = supported('kitchen_tongs', shelf, .25, 4.1, turn=math.pi / 2, scale=.8)
        service += [shelf, tongs]
    # An existing clay plant adds venue context without another paid model.
    load('plant', (2.05, 2.05, 0), scale=2.2, quality='authored')
    P.lighting(Vector((0, 1.4, 1.1)), 1.7)
    sun_data = bpy.data.lights.new('Fixed morning sun through the same window', 'SUN')
    sun_data.energy = 1.5
    sun_data.angle = .10
    sun = bpy.data.objects.new(sun_data.name, sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = Vector((-.35, 1, -.60)).to_track_quat('-Z', 'Y').to_euler()
    area_data = bpy.data.lights.new('Fixed soft window key', 'AREA')
    area_data.energy = 130
    area_data.shape = 'DISK'
    area_data.size = 1.4
    area = bpy.data.objects.new(area_data.name, area_data)
    scene.collection.objects.link(area)
    area.location = (1.5, -.8, 2.4)
    area.rotation_euler = (Vector((1.15, 1.55, .8)) - area.location).to_track_quat('-Z', 'Y').to_euler()
    data = bpy.data.cameras.new('Phone / one continuous public visit')
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    data.sensor_fit = 'VERTICAL'
    data.sensor_height = 36
    data.lens = 27
    data.clip_start = .04
    positions = [
        (0, (-2.5, -2.6, 1.55)), (2, (-1.8, -1.7, 1.53)),
        (4.5, (-1.3, -.65, 1.51)), (6, (-1.3, -.25, 1.50)),
        (7, (-1.3, .35, 1.50)), (8, (-1.2, .95, 1.49)),
        (10.5, (-.65, 1.7, 1.48)), (12.5, (-.15, 1.55, 1.46)),
        (16, (.5, 1.1, 1.35)), (18, (1.05, 1.0, 1.02)),
        (20, (1.21, 1.18, .88)), (22.3, (1.22, 1.40, .96)),
        (24, (.85, 1.03, 1.11)), (26.5, (-.1, .90, 1.46)),
        (28.4, (-1.3, .65, 1.49)), (29.4, (-1.3, .25, 1.50)),
        (30.4, (-1.3, -.35, 1.50)), (32, (-1.6, -1.35, 1.53)),
        (33.3, (-2.2, -2.1, 1.55)), (34, (-2.25, -2.13, 1.55)),
    ]
    if venue == 'bakery':
        positions = [(t, (p[0] - .37, p[1], p[2])) if 18 <= t <= 22.3 else (t, p)
                     for t, p in positions]
    lo, hi = B.bounds(meshes(hero))
    cup_target = tuple((lo + hi) / 2)
    lo, hi = B.bounds(meshes(pastry))
    pastry_target = tuple((lo + hi) / 2)
    focus = pastry_target if venue == 'bakery' else cup_target
    targets = [(0, (-.5, 0, 1.25)), (2, (-1.25, 0, 1.3)),
               (6, (-1.3, 1.5, 1.3)), (8, (-.1, 4.55, 1.55)),
               (10.5, (0, 4.55, 1.6)), (12.5, (1.10, 1.6, 1.0)),
               (16, (1.20, 1.45, .85)), (18, focus), (22.0, focus),
               (24, pastry_target), (26.5, (0, 2.5, 1.2)),
               (29.4, (-.5, 2.5, 1.3)), (31, (-.5, 0, 1.3)),
               (33.3, (-.2, 0, 1.3)), (34, (-.15, 0, 1.3))]
    samples = []
    previous_pos = previous_rot = None
    maximum_speed = maximum_turn = 0
    for frame in range(1, COUNT + 1):
        t = (frame - 1) / FPS
        position = cubic(positions, t)
        target = cubic(targets, t)
        position.z += .0025 * math.sin(t * 2.2)
        rotation = (target - position).to_track_quat('-Z', 'Y')
        if previous_rot is not None and previous_rot.dot(rotation) < 0:
            rotation.negate()
        camera.location = position
        camera.rotation_mode = 'QUATERNION'
        camera.rotation_quaternion = rotation
        camera.keyframe_insert('location', frame=frame)
        camera.keyframe_insert('rotation_quaternion', frame=frame)
        angle = 88 * smooth(t, 2.1, 4.3) * (1 - smooth(t, 32, 33.7))
        hinge.rotation_euler.z = math.radians(angle)
        hinge.keyframe_insert('rotation_euler', frame=frame)
        if abs(position.y) < .22:
            assert abs(position.x + 1.3) < .24, ('Doorway route leaves the opening', t, list(position))
            assert angle > 80, ('Door is not open before crossing', t)
        assert position.y < 3.0, 'The phone must never enter the staff service area'
        if previous_pos is not None:
            maximum_speed = max(maximum_speed, (position - previous_pos).length * FPS)
            maximum_turn = max(maximum_turn, math.degrees(previous_rot.rotation_difference(rotation).angle) * FPS)
        previous_pos, previous_rot = position.copy(), rotation.copy()
        samples.append(dict(frame=frame, time_s=t, position=list(position), target=list(target), door_angle_deg=angle))
    assert maximum_speed < 1.4, maximum_speed
    assert maximum_turn < 120, maximum_turn
    role(door, 'support')
    role(window, 'context')
    role(side_window, 'context')
    role(table, 'support')
    for chair in chairs:
        role(chair, 'context')
    for obj in [hero, pastry]:
        role(obj, 'hero')
    for obj in [plate, saucer, far_plate, second, second_cup]:
        role(obj, 'support')
    for obj in service:
        role(obj, 'support')
    # Store the route and diagnostics before any costly full render.
    phases = [dict(id='arriving', start_s=0, end_s=8, action='Approach the same entrance, open the door and continue inside'),
              dict(id='visiting', start_s=8, end_s=16, action='Reveal the venue service zone, turn and lower toward the window table'),
              dict(id='tasting', start_s=16, end_s=24, action='Approach the actual place setting, arc and change height around its food or drink'),
              dict(id='leaving', start_s=24, end_s=34, action='Return through the same open doorway and settle on the same exterior')]
    assert all(c['centre_contact_error_m'] < .002 for c in CONTACTS)
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'), compress=True)
    spec = dict(id='shared-' + venue + '-visit', venue=venue, status='probes_pending', frame_count=COUNT, fps=FPS,
                duration_s=DURATION, scope='complete_non_character_visit', handover_status='continuous_same_scene',
                title=venue.title() + ' / arrive, visit, taste, leave',
                phases=phases, assets=sorted({o.get('asset_family') for o in scene.objects if o.get('asset_family')}),
                shared_layout=True, human_performance_included=False, source_downloads_preserved=True,
                camera=dict(lens_mm=data.lens, max_speed_m_s=maximum_speed, max_angular_speed_deg_s=maximum_turn, samples=samples),
                mobile='Walk in the public aisle, lean toward the table, make a short phone arc with a small height change, then walk out.',
                lighting='Fixed morning window key and sun; geometric window shadows, no bloom and no animated fixtures.',
                contacts=list(CONTACTS), composition=['Same room and same props throughout all four phases',
                    'Two usable opposite place settings and inward-facing chairs',
                    'Food and drink are off centre; the shared table middle remains clear',
                    'Architecture frames arrival; window light and layered depth guide the interior turn'],
                ghost=dict(whole_overlay_alpha=.65, walls_absent=True, viewfinder_embedded=False),
                render_variants=['full_color', 'transparent_ghost'],
                probe_frames=[1, 53, 106, 151, 196, 241, 286, 331, 361, 406, 451, 496], published=False)
    (out / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    return scene, spec


def render(scene, out, spec, probes=False, frames=None):
    numbers = frames or (spec['probe_frames'] if probes else range(1, COUNT + 1))
    mask = EXPORT.mask_material()
    for mode in ['color', 'mask']:
        path = out / (('probes-' if probes else '') + mode)
        path.mkdir(exist_ok=True)
        scene.view_layers[0].material_override = mask if mode == 'mask' else None
        scene.view_settings.view_transform = 'Standard' if mode == 'mask' else 'AgX'
        scene.view_settings.exposure = 0 if mode == 'mask' else -.1
        scene.eevee.taa_render_samples = 8 if mode == 'mask' else 32
        for obj in scene.objects:
            if obj.get('glazing'):
                obj.hide_render = mode == 'mask'
        for frame in numbers:
            scene.frame_set(frame)
            scene.render.filepath = str(path / ('frame_%04d.png' % frame))
            bpy.ops.render.render(write_still=True)
    print('SHARED_VENUE_RENDERED', spec['venue'], 'probes' if probes else 'full', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--venue', choices=['cafe', 'bakery', 'bar'], default='cafe')
    parser.add_argument('--probes', action='store_true')
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--resume-render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = BASE / 'catalog/shared-venue-visits' / args.venue
    if args.resume_render:
        bpy.ops.wm.open_mainfile(filepath=str(out / 'scene.blend'))
        scene = bpy.context.scene
        spec = json.loads((out / 'scene-spec.json').read_text())
    else:
        scene, spec = setup(args.venue, out)
    if not args.build_only:
        render(scene, out, spec, args.probes)
