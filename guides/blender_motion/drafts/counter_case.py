"""Counter display-case draft (catalog v3, 2026-11-16): a rail truck along the approved Tripo display case."""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector
from drafts.common import new_state, finish

IDS = ('counter_display_truck',)

ROOT = Path(__file__).resolve().parents[3]
# Visitor side is -Y. The case (1.25 x 0.80 x 1.06 m) is centred at the origin; its front glass is at y = -0.40.
CASE_FRONT_Y = -.40
# Request: phone at chest height about 3 ft (0.91 m) from the glass; truck right about 4 in/s for 5 s (0.51 m).
LENS_Z, GLASS_GAP, PITCH_DEG = 1.30, .9144, 23.
TRUCK = 5 * 4 * .0254
# The case top is a rounded front rail (y -0.35 to -0.17, top z 1.035): the cup stands on its middle.
CUP_XY = (.22, -.26)
# Window light from the front left: a short warm edge on the rail's front-upper edge, left half.
RAIL_EDGE_X = (-.46, -.06)


def library_model(P, name, position, role, turn=0.):
    """The approved library model read into memory with the owner's dot cleanup (render_objects SCAN_PREP); the file
    is only read. Rests on its lowest vertex at `position`, turned `turn` degrees about Z."""
    from render_objects import SCAN_PREP, clean_scan_mesh
    source = ROOT / 'model_refferences/objects' / name / 'tripo-generated/review/asset.blend'
    A = P.A
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(source), link=False) as (src, dst):
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
    bottom = min(v.co.z for o in meshes for v in o.data.vertices)
    for obj in meshes:
        for vertex in obj.data.vertices:
            vertex.co.z -= bottom
        A.tag(obj, role, f'Approved library {name}, dot cleanup in memory, shape unchanged')
    root = A.group('Library ' + name, before, position, role, f'Approved {name} resting on its support')
    root.rotation_euler.z = math.radians(turn)
    root['library_source'] = str(source.relative_to(ROOT)); root['scan_cleanup'] = cleanup
    return root, meshes


def split_loose(obj, keep):
    """Moves the loose parts for which keep(part bounds min, max) is false into a second object; geometry unchanged."""
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table()
    seen, moved = set(), []
    for start in bm.verts:
        if start.index in seen:
            continue
        part, stack = [], [start]; seen.add(start.index)
        while stack:
            v = stack.pop(); part.append(v)
            for edge in v.link_edges:
                other = edge.other_vert(v)
                if other.index not in seen:
                    seen.add(other.index); stack.append(other)
        lo = Vector(tuple(min(v.co[i] for v in part) for i in range(3)))
        hi = Vector(tuple(max(v.co[i] for v in part) for i in range(3)))
        if not keep(lo, hi):
            moved += [v.index for v in part]
    bm.free()
    other = obj.copy(); other.data = obj.data.copy(); other.name = obj.name + ' part'
    for col in obj.users_collection:
        col.objects.link(other)
    moved_set = set(moved)
    for target, drop in ((obj, moved_set), (other, None)):
        bm = bmesh.new(); bm.from_mesh(target.data); bm.verts.ensure_lookup_table()
        doomed = [v for v in bm.verts if (v.index in moved_set) == (drop is not None)]
        bmesh.ops.delete(bm, geom=doomed, context='VERTS'); bm.to_mesh(target.data); bm.free()
    return other


def top_z(meshes, x, y, radius):
    """Highest case vertex within `radius` of (x, y): the surface a prop placed there rests on."""
    bpy.context.view_layer.update()
    return max(p.z for o in meshes for p in (o.matrix_world @ v.co for v in o.data.vertices)
               if math.hypot(p.x - x, p.y - y) <= radius)


def build(gid, record, P):
    state = new_state(); A = P.A
    case, case_meshes = library_model(P, 'display_case', (0, 0, 0), 'important_background')
    # The upper tray with its pastries is one loose part of the scan: drawn as the hero, the rest of the case frames it.
    body = case_meshes[0]
    shelf = split_loose(body, lambda lo, hi: lo.z < .60)
    A.tag(shelf, 'hero', 'Upper tray of pastries inside the approved case, the read of the truck')
    A.tag(body, 'important_background', 'Case frame, posts and lower tray: strong edges because the glass reads weak')
    surface = top_z(case_meshes + [shelf], CUP_XY[0], CUP_XY[1], .07)
    cup, _ = library_model(P, 'takeaway_cup', (CUP_XY[0], CUP_XY[1], surface), 'support')
    # The edge follows the rail's drawn top contour as seen from the phone (the vertex highest in the picture per
    # slice), straightened by a line fit, since the scan surface is wavy.
    bpy.context.view_layer.update()
    end = Vector((TRUCK / 2, CASE_FRONT_Y - GLASS_GAP, LENS_Z)); pitch = math.radians(PITCH_DEG)
    forward = Vector((0, math.cos(pitch), -math.sin(pitch))); up = Vector((0, math.sin(pitch), math.cos(pitch)))
    world = [body.matrix_world @ v.co for v in body.data.vertices]
    found = []
    for k in range(17):
        x = RAIL_EDGE_X[0] + (RAIL_EDGE_X[1] - RAIL_EDGE_X[0]) * k / 16
        near = [p for p in world if abs(p.x - x) < .006 and p.z > .95 and p.y < -.10]
        found.append(max(near, key=lambda p: (p - end).dot(up) / (p - end).dot(forward)))
    mx = sum(p.x for p in found) / len(found)
    def fit(axis):
        mean = sum(p[axis] for p in found) / len(found)
        slope = sum((p.x - mx) * (p[axis] - mean) for p in found) / sum((p.x - mx) ** 2 for p in found)
        return lambda x: mean + slope * (x - mx)
    fy, fz = fit(1), fit(2)
    points = [Vector((x, fy(x) - .001, fz(x) + .001)) for x in (RAIL_EDGE_X[0], mx, RAIL_EDGE_X[1])]
    P.light_edge('Case top rail light edge', points, .0006)
    state['light_position'] = (-1.2, -1.4, 1.6)
    state['adaptations'].append(
        f'Approved display case with its own pastries (upper tray is the hero); takeaway cup on the case top at z {surface:.3f} m; '
        f'warm edge on the left half of the top rail (window front left). Lens {LENS_Z} m, {GLASS_GAP:.2f} m (3 ft) from the glass, {PITCH_DEG} deg down, '
        f'1x; truck right {TRUCK:.3f} m (20 in) in 5 s at an even 10 cm/s, no pan.')
    # Aim distance = the hero tray's distance, so the constant-pixel line width is set at the subject.
    aim = end + 1.35 * Vector((0, math.cos(math.radians(PITCH_DEG)), -math.sin(math.radians(PITCH_DEG))))
    shift = Vector((TRUCK, 0, 0))
    return finish(state, [shelf], end, aim, lambda u, p, t: (p - shift * (1 - u), t - shift * (1 - u)))
