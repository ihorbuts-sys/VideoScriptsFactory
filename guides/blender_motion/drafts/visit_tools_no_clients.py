"""Standing orbit at the foot of the empty treatment bed (catalog v3, 2026-11-16).

Built like plate_high_orbit_v2 (constant radius, even arc) at room scale: the approved one-hole treatment bed copy,
the approved round table at side-table size and the approved Tripo laptop on it. No people (no clients by rule)."""
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from drafts.common import new_state, finish
from drafts.counter_case import library_model
from drafts.plates_v2 import ramp
from drafts.room_v2 import look

IDS = ('visit_tools_no_clients',)

ROOT = Path(__file__).resolve().parents[3]
BED = 'model_refferences/objects/treatment_bed/one-face-hole-v1/asset.blend'
# The bed (1.02 x 1.95 x 0.76 m) stands centred at the origin, head opening at +Y; the visitor stands past its foot (-Y).
FOOT = Vector((0, -.975, 0))
# Small side table: the approved round table at the people-guide side-table radius, past the head end on the right
# (beside the bed it would leave the frame at the end of the arc).
TABLE, TABLE_RADIUS, TABLE_TOP = (.62, 1.40), .34, .785
# Laptop screen turned toward the foot of the bed so its open lid and keyboard read from the visitor side.
LAPTOP_TURN = 160.
# Standing lens at chest height (walk height RB23 RB25 RB31) about 7 ft from the foot: the nearest distance at which the
# whole bed fits the 28% / 35% band with the 1x lens (geometry); pitch puts the bed's middle at the band centre.
LENS = Vector((0, FOOT.y - 2.10, 1.30))
PITCH = 22.
AIM = look(LENS, 0, PITCH, 3.)
# 15 deg of arc about the vertical through the bed foot in 5 s, an even pace with short eases; ends right of the axis.
ARC, END_AZIMUTH = 15., 7.5


def bed(P):
    """The approved one-hole bed copy read into memory with the default dot cleanup; the file is only read."""
    from render_objects import SCAN_PREP, clean_scan_mesh
    A = P.A
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(ROOT / BED), link=False) as (src, dst):
        dst.objects = src.objects
    meshes = [o for o in dst.objects if o and o.type == 'MESH']
    for obj in meshes:
        bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    for obj in meshes:
        world = obj.matrix_world.copy(); obj.data.transform(world); obj.parent = None; obj.matrix_world = Matrix.Identity(4)
        obj.data.materials.clear(); obj.data.materials.append(P.G.MAT)
    for obj in dst.objects:
        if obj and obj.type != 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
    cleanup = clean_scan_mesh(meshes, **SCAN_PREP)
    for obj in meshes:
        A.tag(obj, 'hero', 'Approved treatment bed (one-hole copy), dot cleanup in memory, shape unchanged')
    root = A.group('Library treatment_bed one-hole', before, (0, 0, 0), 'hero', 'Empty treatment bed, the visit equipment')
    root['library_source'] = BED; root['scan_cleanup'] = cleanup
    return root, meshes


def turn(v, degrees):
    return FOOT + Matrix.Rotation(math.radians(degrees), 3, 'Z') @ (v - FOOT)


def build(gid, record, P):
    A = P.A
    state = new_state()
    root, hero = bed(P)
    table = A.table((TABLE[0], TABLE[1], 0), TABLE_RADIUS)
    P.role(table, 'background')
    laptop, _ = library_model(P, 'laptop', (TABLE[0], TABLE[1] + .02, TABLE_TOP), 'support', LAPTOP_TURN)
    state['light_position'] = (-1.4, 1.2, 2.2)
    state['adaptations'].append(
        f'Empty treatment bed (approved one-hole copy) centred, head opening away from the lens; a small side table '
        f'(approved round table, radius {TABLE_RADIUS} m) past the head end on the right with the approved laptop, screen toward the '
        f'bed foot; no walls drawn. Standing lens {LENS.z * 100:.0f} cm, about {(FOOT.y - LENS.y) / .3048:.1f} ft from the '
        f'bed foot, pitch {PITCH:g} deg down; orbit {ARC:g} deg about the vertical through the bed foot at one even pace, ending {END_AZIMUTH:g} deg '
        f'right of the bed axis. No people.')
    state['contacts'].append(dict(kind='floor_and_table', bed=root.name, table=table.name, laptop=laptop.name,
                                  laptop_on_table_z=TABLE_TOP, people=0))
    def sample(u, p, t):
        back = -ARC * (1 - ramp(u))
        return turn(p, back), turn(t, back)
    return finish(state, hero, turn(LENS, END_AZIMUTH), turn(AIM, END_AZIMUTH), sample)
