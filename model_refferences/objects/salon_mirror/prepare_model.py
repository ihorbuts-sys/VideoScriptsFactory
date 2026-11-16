import bpy
import json
import math
import sys
from pathlib import Path
import numpy as np
from mathutils import Matrix

asset = Path(sys.argv[sys.argv.index('--') + 1])
source = asset / 'tripo/tripo-out/salon-mirror-7388f97b/model.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not meshes:
    raise RuntimeError('No mesh objects imported')
arrays = []
for obj in meshes:
    coords = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
    obj.data.vertices.foreach_get('co', coords)
    coords = coords.reshape(-1, 3)
    world = np.array(obj.matrix_world)
    arrays.append(coords @ world[:3, :3].T + world[:3, 3])
points = np.concatenate(arrays)
raw_bounds = [points.min(axis=0).tolist(), points.max(axis=0).tolist()]
height = np.ptp(points[:, 2])
upper = points[points[:, 2] > points[:, 2].min() + height * 0.3]
values, vectors = np.linalg.eigh(np.cov(upper[:, :2].T))
width_axis = vectors[:, np.argmax(values)]
if width_axis[0] < 0:
    width_axis *= -1
angle = math.atan2(width_axis[1], width_axis[0])
rotation = np.array(Matrix.Rotation(-angle, 4, 'Z'))[:3, :3]
rotated = points @ rotation.T
lower = rotated[rotated[:, 2] < rotated[:, 2].min() + height * 0.06]
upper_rotated = upper @ rotation.T
if lower[:, 1].mean() > upper_rotated[:, 1].mean():
    rotation = np.diag([-1.0, -1.0, 1.0]) @ rotation
    rotated = points @ rotation.T
minimum, maximum = rotated.min(axis=0), rotated.max(axis=0)
target = np.array([0.6, 0.1016, 0.938])
scale = target / (maximum - minimum)
shift = np.array([-0.3, -0.1016, -0.038]) - minimum * scale
transform = np.eye(4)
transform[:3, :3] = np.diag(scale) @ rotation
transform[:3, 3] = shift
root = bpy.data.objects.new('SalonMirror', None)
bpy.context.scene.collection.objects.link(root)
root['mirror_width_m'] = 0.6
root['mirror_height_target_m'] = 0.9
root['mount_mirror_bottom_above_floor_m'] = 1.016
root['shelf_depth_m'] = 0.1016
for obj in meshes:
    matrix = Matrix(transform.tolist()) @ obj.matrix_world
    obj.parent = None
    obj.data.transform(matrix)
    obj.matrix_world = Matrix.Identity(4)
    obj.parent = root
    obj.data.calc_loop_triangles()
for obj in list(bpy.context.scene.objects):
    if obj != root and obj not in meshes:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(asset / 'salon-mirror.blend'))
bpy.ops.export_scene.gltf(filepath=str(asset / 'salon-mirror.glb'), export_format='GLB', export_extras=True)
report = {
    'task_id': '7388f97b-1d07-4818-a574-c5c1d339fa71',
    'model_version': 'v3.1-20260211',
    'status': 'success',
    'credits_consumed': 30,
    'balance_after': 445,
    'frozen_after': 0,
    'source_image': 'reference.png',
    'original_model': str(source.relative_to(asset)),
    'prepared_model': 'salon-mirror.glb',
    'prepared_blender_file': 'salon-mirror.blend',
    'verification': {
        'blender_import': 'passed',
        'blender_version': bpy.app.version_string,
        'mesh_objects': len(meshes),
        'triangles': sum(len(o.data.loop_triangles) for o in meshes),
        'raw_bounds': raw_bounds,
        'calibrated_assembly_dimensions_m': target.tolist(),
        'origin': 'mirror bottom centre at wall plane; shelf extends below origin',
        'forward': '-Y',
        'scene_mount_root_z_m': 1.016,
        'individual_frame_depth_and_mirror_height': 'approximate; only total assembly envelope calibrated',
        'glass_glints': 'present in source appearance; dedicated line-art strokes not prepared',
        'line_art_rendered': False
    }
}
(asset / 'generation-result.json').write_text(json.dumps(report, indent=2) + '\n')
print('SALON_MIRROR_VERIFIED ' + json.dumps(report['verification']))
