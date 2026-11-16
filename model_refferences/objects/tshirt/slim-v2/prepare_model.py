import bpy
import json
import math
import sys
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector

asset = Path(sys.argv[sys.argv.index('--') + 1])
source = asset / 'tripo/tripo-out/tshirt-slim-v2-2d3fe51d/model.glb'
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
values, vectors = np.linalg.eigh(np.cov(points[:, :2].T))
width = vectors[:, np.argmax(values)]
if width[0] < 0:
    width *= -1
angle = math.atan2(width[1], width[0])
rotation = np.array(Matrix.Rotation(-angle, 4, 'Z'))[:3, :3]
rotated = points @ rotation.T
minimum, maximum = rotated.min(axis=0), rotated.max(axis=0)
canonical_raw_dimensions = maximum - minimum
target = np.array([0.5, 0.025, 0.65])
scale = target / canonical_raw_dimensions
shift = np.array([-0.25, -0.0125, 0.0]) - minimum * scale
transform = np.eye(4)
transform[:3, :3] = np.diag(scale) @ rotation
transform[:3, 3] = shift
root = bpy.data.objects.new('TshirtSlim', None)
bpy.context.scene.collection.objects.link(root)
root['dimensions_m'] = target.tolist()
root['usage'] = 'upright for hanging; separate flat-laid GLB for shelf placement'
material = bpy.data.materials.new('Sunny yellow clay')
material.use_nodes = True
shader = material.node_tree.nodes.get('Principled BSDF')
def linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
yellow = tuple(linear(c / 255) for c in (246, 188, 39)) + (1.0,)
shader.inputs['Base Color'].default_value = yellow
shader.inputs['Roughness'].default_value = 0.8
shader.inputs['Metallic'].default_value = 0.0
material.diffuse_color = yellow
for obj in meshes:
    matrix = Matrix(transform.tolist()) @ obj.matrix_world
    obj.parent = None
    obj.data.transform(matrix)
    obj.matrix_world = Matrix.Identity(4)
    obj.parent = root
    obj.data.materials.clear()
    obj.data.materials.append(material)
    obj.data.calc_loop_triangles()
for obj in list(bpy.context.scene.objects):
    if obj != root and obj not in meshes:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.context.view_layer.update()
final_points = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in meshes])
measured = np.ptp(final_points, axis=0)
if not np.allclose(measured, target, atol=0.00001):
    raise RuntimeError('Prepared dimensions do not match target')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(asset / 'tshirt-slim.blend'))
bpy.ops.export_scene.gltf(filepath=str(asset / 'tshirt-slim.glb'), export_format='GLB', export_extras=True)
root.rotation_euler.x = -math.pi / 2
root.location.z = 0.0125
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(asset / 'tshirt-shelf-flat.glb'), export_format='GLB', export_extras=True)
root.rotation_euler.x = 0
root.location.z = 0
bpy.context.view_layer.update()
report = {
    'task_id': '2d3fe51d-0f90-465b-a5e3-2b9730d8f679',
    'model_version': 'v3.1-20260211',
    'status': 'success',
    'credits_consumed': 30,
    'balance_after': 415,
    'frozen_after': 0,
    'source_image': 'reference.png',
    'original_model': str(source.relative_to(asset)),
    'prepared_model': 'tshirt-slim.glb',
    'flat_model': 'tshirt-shelf-flat.glb',
    'blender_file': 'tshirt-slim.blend',
    'verification': {
        'blender_import': 'passed',
        'blender_version': bpy.app.version_string,
        'mesh_objects': len(meshes),
        'triangles': sum(len(o.data.loop_triangles) for o in meshes),
        'raw_bounds': raw_bounds,
        'canonical_raw_dimensions_m': canonical_raw_dimensions.tolist(),
        'prepared_dimensions_m': measured.tolist(),
        'depth_enforced_locally': True,
        'material': 'plain matte sunny yellow #F6BC27 restored locally; raw download preserved',
        'flat_variant': 'same garment laid flat, unfolded, front upward, lowest surface at Z=0',
        'hanger_fit': 'not tested with a specific hanger',
        'cloth_simulation': False
    }
}
(asset / 'generation-result.json').write_text(json.dumps(report, indent=2) + '\n')
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.world = bpy.data.worlds.new('Studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
for name, location, power, size in [('Key', (1, -2, 2), 120, 2), ('Fill', (-1, -1, 1), 50, 1.5)]:
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 0.325)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
camera_data = bpy.data.cameras.new('PreviewCamera')
camera = bpy.data.objects.new('PreviewCamera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 0.85
camera.location = (0.8, -2.0, 0.75)
camera.rotation_euler = (Vector((0, 0, 0.325)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(asset / 'preview.png')
bpy.ops.render.render(write_still=True)
camera.location = (2.0, 0, 0.325)
camera.rotation_euler = (Vector((0, 0, 0.325)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x = 384
scene.render.resolution_y = 768
camera_data.ortho_scale = 0.75
scene.render.filepath = str(asset / 'side.png')
bpy.ops.render.render(write_still=True)
print('TSHIRT_SLIM_VERIFIED ' + json.dumps(report['verification']))
