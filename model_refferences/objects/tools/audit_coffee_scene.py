"""Independently check the posed arm, surface materials and menu alignment."""
import json
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
import prepare_creator_tripo as B

OUT = P.BASE / 'catalog/coffee-ordering-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'scene.blend'))
scene = bpy.context.scene
machine = next(o for o in scene.objects if o.get('asset_family') == 'espresso_machine')
barista = next(o for o in scene.objects if o.get('asset_family') == 'barista')


def geometry(objects, selected_arm=False):
    points, triangles = [], []
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        if selected_arm:
            groups = {g.index for g in obj.vertex_groups if
                      g.name.split(':')[-1] in ['LeftArm', 'LeftForeArm'] or 'LeftHand' in g.name}
            selected = [sum(g.weight for g in v.groups if g.group in groups) > .5 for v in obj.data.vertices]
        else:
            selected = [True]*len(mesh.vertices)
        faces = [tuple(f.vertices) for f in mesh.polygons if all(selected[i] for i in f.vertices)]
        used = sorted({i for face in faces for i in face})
        mapping = {i:len(points)+n for n, i in enumerate(used)}
        points.extend(evaluated.matrix_world @ mesh.vertices[i].co for i in used)
        triangles.extend(tuple(mapping[i] for i in face) for face in faces)
        evaluated.to_mesh_clear()
    return points, triangles


checks = []
for frame in [1, 121, 240]:
    scene.frame_set(frame)
    vertices, faces = geometry(C.meshes(machine))
    machine_tree = BVHTree.FromPolygons(vertices, faces)
    arm_vertices, arm_faces = geometry(C.meshes(barista), selected_arm=True)
    arm_tree = BVHTree.FromPolygons(arm_vertices, arm_faces)
    intersections = len(arm_tree.overlap(machine_tree))
    clearance = min(machine_tree.find_nearest(p)[3] for p in arm_vertices)
    assert intersections == 0, (frame, intersections)
    assert clearance > .01, (frame, clearance)
    checks.append(dict(frame=frame, intersecting_triangle_pairs=intersections,
                       minimum_sampled_arm_clearance_m=clearance))

menu = next(o for o in scene.objects if o.get('asset_family') == 'menu_board')
lo, hi = B.bounds(C.meshes(menu))
mid = (lo+hi)/2
fixtures = [o for o in scene.objects if o.get('asset_family') == 'wall_sconce_local']
centres = sorted(((B.bounds(C.meshes(o))[0]+B.bounds(C.meshes(o))[1])/2 for o in fixtures), key=lambda p:p.x)
left_gap = lo.x-centres[0].x
right_gap = centres[1].x-hi.x
assert abs(left_gap-right_gap) < .001
assert all(abs(p.z-mid.z) < .001 for p in centres)
shelves = [o for o in scene.objects if o.get('asset_family') == 'wall_shelf']
assert all(o.get('baked_markings_removed') for shelf in shelves for o in C.meshes(shelf))
wood = []
for root in [o for o in scene.objects if o.get('asset_family') in ['wall_shelf','bar_counter','dining_table']]:
    used = {m for o in C.meshes(root) for m in o.data.materials if m and m.use_nodes}
    found = [m.name for m in used if any(n.type == 'TEX_WAVE' for n in m.node_tree.nodes)]
    assert found, root.name
    wood.append(dict(asset=root['asset_family'], wood_materials=found))
report = dict(status='passed', left_arm_machine_collision_checks=checks,
    menu_equal_horizontal_gaps_m=[left_gap,right_gap], menu_lights_same_height=True,
    shelf_markings_removed=True, wood_surfaces=wood)
(OUT / 'scene-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report), flush=True)
