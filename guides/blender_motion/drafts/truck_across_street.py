"""Food truck from across the street (catalog v3, 2026-11-16): the approved food truck, service window to the lens,
seen from about 30 ft at eye level; a slow walk forward of about 3 ft. Move of entrance_walk_in_v2 (constant walk, the
phone does not re-aim); the facade is replaced by the truck and a faint curb line. Owner review 2026-11-17: the cook
(approved barista rig, working pose) inside behind the window; a more distinct silhouette (outer contour at full
opacity, interior contours fainter) and no stray dots (short-stroke filter), both per guide (drafts.truck_cook)."""
import math

import bpy
from mathutils import Matrix, Vector

from drafts.common import new_state, finish

IDS = ('truck_across_street',)

FT = .3048
TRUCK = 'model_refferences/objects/food_truck/lineart/asset.blend'
# Window-side body panel of the cache at y = +1.12 m (counter ledge 1.30 m, awning 1.71 m); turned 180 deg it faces -Y.
SIDE_Y = -1.12
START_FT = 30
WALK_FT = 3
EYE = 1.55              # standing eye level, lens height in m (judgement, about 5 ft 1 in)
PITCH_DEG = 3.          # slightly down, as entrance_walk_in_v2: puts the truck centre about 46% from the top (framing.md RA2)
CURB_Y = SIDE_Y - .45   # the sidewalk edge the truck parks along, between the lens and the window (judgement)


def ramp(u, r=.15):
    u = max(0., min(1., u)); v = 1 / (1 - r)
    if u < r:
        return v * u * u / (2 * r)
    if u > 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def food_truck(P):
    """The approved line-art cache, turned 180 deg about Z so the service window faces the visitor (-Y)."""
    from pathlib import Path
    import lineart_render as L
    A, G = P.A, P.G
    root_dir = Path(__file__).resolve().parents[3]
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(root_dir / TRUCK), link=False) as (src, dst):
        dst.objects = src.objects
    meshes = [o for o in dst.objects if o and o.type == 'MESH']
    for obj in meshes:
        bpy.context.collection.objects.link(obj)
    L.prepare_meshes(meshes)
    for obj in meshes:
        obj.data.transform(Matrix.Rotation(math.pi, 4, 'Z'))
        obj.data.materials.clear(); obj.data.materials.append(G.MAT)
        A.tag(obj, 'hero', 'The approved food truck, service window to the lens, is the shot subject')
    A.group('Food truck', before, (0, 0, 0), 'hero', 'Parked at the far curb, window side to the street')
    return meshes


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    A, G = P.A, P.G
    state = new_state()
    meshes = food_truck(P)
    A.tag(G.tube('Curb line', [(-4.2, CURB_Y, .012), (4.2, CURB_Y, .012)], .0012), 'structure',
          'Sidewalk edge under the truck; no filled street or ground plane')
    from drafts.truck_cook import cook_working, install_stroke_treatment
    install_stroke_treatment(meshes, outline=True)
    cook_working(P, state, gid)
    state['contacts'].append(dict(kind='truck_strokes', short_stroke_filter_px=12, outline_emphasis=True,
                                  interior_share=.5, scope='this guide only (strokes_setup wrapped in process)'))
    start_y = SIDE_Y - START_FT * FT
    end = Vector((0, start_y + WALK_FT * FT, EYE))
    aim = end + Vector((0, math.cos(math.radians(PITCH_DEG)), -math.sin(math.radians(PITCH_DEG)))) * (SIDE_Y - end.y)
    walk = WALK_FT * FT

    def sample(u, p, t):
        offset = Vector((0, -walk * (1 - ramp(u)), 0))
        return p + offset, t + offset

    state['contacts'].append(dict(kind='standing_walk', lens_height_m=EYE, pitch_deg=PITCH_DEG,
                                  start_from_window_side_ft=START_FT, walk_ft=WALK_FT, lens='1x'))
    state['adaptations'].append(f'Standing at eye level (lens {EYE} m), {PITCH_DEG:.0f} deg down, {START_FT} ft from the truck\'s '
                                f'window side; a slow straight walk of {WALK_FT} ft over the move with a short ease at '
                                'each end; the phone does not re-aim.')
    return finish(state, meshes, end, aim, sample)
