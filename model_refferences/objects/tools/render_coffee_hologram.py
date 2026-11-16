"""Render view-dependent surface fields for a translucent hologram study."""
import argparse
import json
import sys
from pathlib import Path

import bpy

BASE = Path(__file__).resolve().parents[3]
SOURCE = BASE / 'catalog/coffee-ordering-v2'
OUT = BASE / 'catalog/coffee-hologram-study'


def material():
    mat = bpy.data.materials.new('Hologram / native Fresnel, broad light, height')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    geometry = nodes.new('ShaderNodeNewGeometry')
    facing = nodes.new('ShaderNodeLayerWeight')
    facing.inputs['Blend'].default_value = .35
    light = nodes.new('ShaderNodeVectorMath')
    light.operation = 'DOT_PRODUCT'
    light.inputs[1].default_value = (-.45, -.55, .70)
    links.new(geometry.outputs['Normal'], light.inputs[0])
    mapped = nodes.new('ShaderNodeMath')
    mapped.operation = 'MULTIPLY_ADD'
    mapped.inputs[1].default_value = .5
    mapped.inputs[2].default_value = .5
    links.new(light.outputs['Value'], mapped.inputs[0])
    separate = nodes.new('ShaderNodeSeparateXYZ')
    links.new(geometry.outputs['Position'], separate.inputs[0])
    height = nodes.new('ShaderNodeMath')
    height.operation = 'MULTIPLY'
    height.inputs[1].default_value = 1 / 3
    links.new(separate.outputs['Z'], height.inputs[0])
    combine = nodes.new('ShaderNodeCombineXYZ')
    links.new(facing.outputs['Fresnel'], combine.inputs['X'])
    links.new(mapped.outputs[0], combine.inputs['Y'])
    links.new(height.outputs[0], combine.inputs['Z'])
    emission = nodes.new('ShaderNodeEmission')
    links.new(combine.outputs[0], emission.inputs['Color'])
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs[0], output.inputs[0])
    return mat


def run(probes):
    OUT.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / 'scene.blend'))
    scene = bpy.context.scene
    excluded = []
    mounted = []
    for obj in scene.objects:
        if obj.type == 'MESH' and not obj.hide_render:
            obj.data.polygons.foreach_set('use_smooth', [True] * len(obj.data.polygons))
        if obj.get('glazing'):
            obj.hide_render = True
        if obj.type == 'LIGHT':
            obj.hide_render = True
        if obj.get('ghost_role') == 'absent' or obj.name.startswith('Room shell /'):
            obj.hide_render = True
            excluded.append(obj.name)
        if obj.get('asset_family') in ['wall_shelf', 'menu_board', 'wall_sconce_local']:
            mounted.append(obj.name)
    (OUT / 'architecture-exclusion.json').write_text(json.dumps(dict(
        walls_and_floor_hidden=True, excluded_objects=excluded,
        mounted_objects_retained=mounted), indent=2) + '\n')
    scene.view_layers[0].material_override = material()
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 16
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.render.resolution_percentage = 100
    # Opaque emission fields retain correct occlusion, then the compositor
    # creates transparency. No textures, mesh-edge drawing or scene bloom.
    numbers = [1, 121, 240] if probes else range(1, 241)
    folder = OUT / ('probe-fields' if probes else 'fields')
    folder.mkdir(exist_ok=True)
    for frame in numbers:
        scene.frame_set(frame)
        scene.render.filepath = str(folder / f'frame_{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    (OUT / ('probes-ready.json' if probes else 'fields-ready.json')).write_text(
        json.dumps(dict(status='ready', frames=len(numbers), source=str(SOURCE / 'scene.blend'))) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probes', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    run(args.probes)
