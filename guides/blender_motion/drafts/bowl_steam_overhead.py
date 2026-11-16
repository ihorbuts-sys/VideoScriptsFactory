"""Overhead rise over a soup bowl (catalog v3, 2026-11-16): the approved serving_bowl at a place setting, phone flat
above it, rising straight up. Layout and move of plate_rise_overhead_v2; only the dish, the cutlery and the heights
change."""
import json
import math

import bpy
from mathutils import Vector

from drafts.common import new_state, finish

IDS = ('bowl_steam_overhead',)

SUPPORT = .785
IN = .0254
# Lens heights above the bowl rim (request: about 14 in, then up to about 22 in).
START_ABOVE_RIM = 14 * IN
END_ABOVE_RIM = 22 * IN
# Rise from 1.0 s to 4.0 s of the 5 s move; the 3.5 s beat says stop as it eases out.
RISE = (.2, .8)
# Camera 3 cm toward screen-down puts the bowl centre about 46% from the top (framing.md hero centre, RA2).
SCREEN_DOWN_OFFSET = .03
# Owner rule 2026-11-15 spacing (fork and knife 3/4 in clear) used for the soup spoon too.
CLEAR = .02
BOWL = 'model_refferences/objects/serving_bowl/tripo-generated/review/asset.blend'


def ramp(u, r=.15):
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def serving_bowl(P, position, prep=None):
    """The serving_bowl as its approved line-art render prepared it: default dot cleanup (SCAN_PREP) and the line-art
    study's weld, bevel and weighted normals, in memory; the source file is not changed."""
    from pathlib import Path
    from render_objects import SCAN_PREP, clean_scan_mesh
    import lineart_render as L
    A, G = P.A, P.G
    root_dir = Path(__file__).resolve().parents[3]
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(root_dir / BOWL), link=False) as (src, dst):
        dst.objects = src.objects
    loaded = [o for o in dst.objects if o]
    for obj in loaded:
        bpy.context.collection.objects.link(obj)
    # The source carries its 0.21 scale on a parent empty: bake world transforms before dropping the empties.
    bpy.context.view_layer.update()
    meshes = [o for o in loaded if o.type == 'MESH' and not o.hide_render]
    for obj in meshes:
        world = obj.matrix_world.copy(); obj.data.transform(world)
    for obj in meshes:
        obj.parent = None; obj.matrix_world.identity()
    for obj in loaded:
        if obj not in meshes:
            bpy.data.objects.remove(obj, do_unlink=True)
    clean_scan_mesh(meshes, **dict(SCAN_PREP, **(prep or {})))
    L.prepare_meshes(meshes)
    for obj in meshes:
        obj.data.materials.clear(); obj.data.materials.append(G.MAT)
        A.tag(obj, 'hero', 'The approved serving_bowl is the shot subject')
    return A.group('Serving bowl', before, position, 'hero', 'Bowl at the place setting')


def rim(meshes):
    """Rim height and radius of the placed bowl (world), from its top vertices."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        ev = obj.evaluated_get(deps)
        points += [ev.matrix_world @ v.co for v in ev.data.vertices]
    top = max(p.z for p in points)
    near = [p for p in points if p.z > top - .002]
    cx = sum(p.x for p in points) / len(points); cy = sum(p.y for p in points) / len(points)
    radius = max(math.hypot(p.x - cx, p.y - cy) for p in points)
    rim_r = sum(math.hypot(p.x - cx, p.y - cy) for p in near) / len(near)
    return Vector((cx, cy, top)), rim_r, radius


def steam(P, state, centre, top):
    """The published steam strands (steam_v2.steam), rising from inside the bowl; light contours come from
    p0_steam_points in P.lighting_cues."""
    curls = []
    for side in [-1, 1]:
        points = [(centre.x + side * .016 + .007 * math.sin(k * .8), centre.y, top - .02 + k * .016) for k in range(9)]
        strand = P.A.tag(P.G.tube('Steam strand', points, .00075), 'drink_contents',
                         'Steam rises from the soup bowl')
        strand['p0_steam_points'] = json.dumps(points)
        curls.append(strand)

    def action(u):
        for k, obj in enumerate(curls):
            obj.location.x = .003 * math.sin(u * math.tau + k)
            obj.keyframe_insert('location')
    state['actions'].append(action)
    return curls


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    A = P.A
    state = new_state()
    variant = record.get('dishVariant', 'soup')
    with_steam = bool(record.get('steam', False))
    # Table and chair as plate_rise_overhead_v2 places them (place_setting, then moved).
    A.table((.22, .18, 0), .70).location = (0, .40, 0)
    P.role(P.V.chair((0, 1.22, 0)), 'background')
    bowl = serving_bowl(P, (0, 0, SUPPORT), record.get('scanPrep'))
    meshes = P.members(bowl)
    centre, rim_r, radius = rim(meshes)
    if variant == 'soup':
        # Dessert spoon to the right, bowl of the spoon away from the diner, 3/4 in clear of the bowl's widest point.
        # The spoon is 0.0195 m half-wide; its length runs about -0.12..+0.061 along +Y, centred on the bowl.
        A.spoon((centre.x + radius + CLEAR + .0195, centre.y + .03, SUPPORT), role='support')
    if with_steam:
        steam(P, state, centre, centre.z)
    # Light rim cue on the side facing the default fixed side light (as the plate rim cue).
    source = Vector(state.get('light_position', (-.65, -.18, 1.5)))
    angle = math.atan2(source.y - centre.y, source.x - centre.x)
    P.light_edge('Bowl light-facing rim', [Vector((centre.x + rim_r * math.cos(a), centre.y + rim_r * math.sin(a), centre.z))
                                           for a in [angle + math.radians(-25 + j * 50 / 24) for j in range(25)]],
                 .0003, parent=meshes[0])
    state['camera_up'] = (0, 1, 0)
    aim = Vector((centre.x, centre.y - SCREEN_DOWN_OFFSET, SUPPORT))
    end = Vector((aim.x, aim.y, centre.z + END_ABOVE_RIM))
    start_z = centre.z + START_ABOVE_RIM

    def sample(u, p, t):
        z = start_z + (p.z - start_z) * ramp((u - RISE[0]) / (RISE[1] - RISE[0]))
        pos = Vector((p.x, p.y, z))
        return pos, pos + Vector((0, 0, -1))

    state['dish'] = dict(variant=variant, rim_z=round(centre.z, 4), rim_radius=round(rim_r, 4), radius=round(radius, 4),
                         steam=with_steam)
    state['contacts'].append(dict(kind='overhead_pedestal_rise', lens_above_rim_start_in=14, lens_above_rim_end_in=22,
                                  pitch_deg=90, support_surface_z=SUPPORT, rise_window_u=list(RISE)))
    state['adaptations'].append('Pedestal rise with the phone flat (90 degrees) the whole way, standing: lens about 14 in '
                                'above the bowl rim, held 1 s, rising straight up to about 22 in by 4 s, held to the end.')
    state['adaptations'].append(('Soup variant: dessert spoon to the right, 3/4 in clear of the bowl.' if variant == 'soup'
                                 else 'Bowls and sushi variant: the bowl alone, no spoon.')
                                + (' Steam strands kept.' if with_steam else ' Steam strands left out.'))
    return finish(state, meshes, end, aim, sample)
