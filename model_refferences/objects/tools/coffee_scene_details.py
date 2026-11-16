"""Local set dressing, stylized materials and anatomical grip preparation."""
import math
from collections import deque

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

import build_assets as P
import build_shared_venue as C
import prepare_creator_tripo as B
from prepare_rigged_characters import named
from prepare_coffee_functional import samples


def clean_shelf_material(root):
    """Replace baked markings with clay materials; preserve source downloads."""
    wood = material('shelf / unmarked clay wood', 'wood', (.46, .25, .115))
    for obj in C.meshes(root):
        if obj.get('baked_markings_removed'):
            obj.data.materials[0] = wood
            continue
        obj.data = obj.data.copy()
        centres, rgb = samples(obj)
        chroma = rgb.max(axis=1)-rgb.min(axis=1)
        known = (chroma > .05) & (rgb.max(axis=1) > .08)
        green = (rgb[:, 1] > rgb[:, 0]*1.03) & (rgb[:, 1] > rgb[:, 2]*1.05)
        labels = np.where(known, green.astype(np.int8), -1)
        neighbors = [[] for _ in obj.data.polygons]
        edges = {}
        for face in obj.data.polygons:
            for edge in face.edge_keys:
                key = tuple(sorted(edge))
                if key in edges:
                    previous = edges[key]
                    neighbors[previous].append(face.index)
                    neighbors[face.index].append(previous)
                else:
                    edges[key] = face.index
        queue = deque(np.flatnonzero(known).tolist())
        while queue:
            index = queue.popleft()
            for other in neighbors[index]:
                if labels[other] < 0:
                    labels[other] = labels[index]
                    queue.append(other)
        low, high = centres[:, 2].min(), centres[:, 2].max()
        missing = labels < 0
        labels[missing] = (centres[missing, 2] < low+(high-low)*.55).astype(np.int8)
        obj.data.materials.clear()
        obj.data.materials.append(wood)
        obj.data.materials.append(P.material('sage'))
        for face in obj.data.polygons:
            face.material_index = int(labels[face.index])
        obj['baked_markings_removed'] = True


def material(name, kind, base):
    mat = bpy.data.materials.new('Loca / ' + name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .73
    shader.inputs['Specular IOR Level'].default_value = .22
    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 8 if kind == 'plaster' else 3
    noise.inputs['Detail'].default_value = 1.4
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .15
    ramp.color_ramp.elements[1].position = .85
    ramp.color_ramp.elements[0].color = (*(v * .90 for v in base), 1)
    ramp.color_ramp.elements[1].color = (*base, 1)
    links.new(noise.outputs['Fac'], ramp.inputs[0])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .13
    bump.inputs['Distance'].default_value = .0006
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    if kind == 'floor':
        brick = nodes.new('ShaderNodeTexBrick')
        brick.offset = 0
        brick.offset_frequency = 1
        brick.inputs['Scale'].default_value = 1
        brick.inputs['Brick Width'].default_value = .45
        brick.inputs['Row Height'].default_value = .45
        brick.inputs['Mortar Size'].default_value = .002
        brick.inputs['Mortar Smooth'].default_value = .005
        brick.inputs['Color1'].default_value = (*base, 1)
        brick.inputs['Color2'].default_value = (*(v * .92 for v in base), 1)
        brick.inputs['Mortar'].default_value = (*(v * .82 for v in base), 1)
        links.new(coord.outputs['Object'], brick.inputs['Vector'])
        links.new(brick.outputs['Color'], shader.inputs['Base Color'])
    elif kind == 'wood':
        mapping = nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (1.0, 15.0, 3)
        links.new(coord.outputs['Object'], mapping.inputs[0])
        links.new(mapping.outputs[0], noise.inputs['Vector'])
        grain = nodes.new('ShaderNodeTexWave')
        grain.wave_type = 'BANDS'
        grain.bands_direction = 'Y'
        grain.inputs['Scale'].default_value = 4
        grain.inputs['Distortion'].default_value = 12
        grain.inputs['Detail'].default_value = 2
        grain.inputs['Detail Scale'].default_value = 1.5
        links.new(coord.outputs['Object'], grain.inputs['Vector'])
        links.new(grain.outputs['Fac'], ramp.inputs[0])
        ramp.color_ramp.elements[0].position = 0
        ramp.color_ramp.elements[0].color = (*(min(1, v*1.06) for v in base), 1)
        ramp.color_ramp.elements[1].position = 1
        ramp.color_ramp.elements[1].color = (*(min(1, v*1.08) for v in base), 1)
        for position, amount in [(.46, 1.04), (.54, .78), (.62, 1.04)]:
            ramp.color_ramp.elements.new(position).color = (*(min(1, v*amount) for v in base), 1)
        ramp.color_ramp.interpolation = 'EASE'
        links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
        links.new(grain.outputs['Fac'], bump.inputs['Height'])
        bump.inputs['Distance'].default_value = .00025
    else:
        links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
    return mat


def apply_material(root, mat):
    for obj in C.meshes(root) if root.type != 'MESH' else [root]:
        obj.data = obj.data.copy()
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for face in obj.data.polygons:
            face.material_index = 0


def apply_counter_wood(root, mat):
    lo, hi = B.bounds(C.meshes(root))
    for obj in C.meshes(root):
        centres, rgb = samples(obj)
        wood = (centres[:, 2] > hi.z-.11) & (rgb[:, 0] > rgb[:, 1]*1.12) & (rgb[:, 0] > rgb[:, 2]*1.25)
        obj.data = obj.data.copy()
        index = len(obj.data.materials)
        obj.data.materials.append(mat)
        for face, selected in zip(obj.data.polygons, wood):
            if selected:
                face.material_index = index


def yellow_wall(name, position, dimensions, mat):
    obj = C.wall(name, position, dimensions)
    apply_material(obj, mat)
    return obj


def environment(scene):
    yellow = material('soft yellow plaster', 'plaster', (.79, .50, .10))
    cream = material('warm cream plaster', 'plaster', (.83, .73, .57))
    floor = material('soft warm clay tiles', 'floor', (.76, .63, .45))
    wood = material('gentle clay wood grain', 'wood', (.44, .24, .12))
    for obj in list(scene.objects):
        if obj.name.startswith('Room shell /') and obj.type == 'MESH':
            if obj.name.endswith('/ floor'):
                apply_material(obj, floor)
            elif 'wall' in obj.name:
                apply_material(obj, cream)
    for root in scene.objects:
        if root.get('asset_family') == 'dining_table':
            apply_material(root, wood)
        elif root.get('asset_family') == 'bar_counter':
            apply_counter_wood(root, wood)
    windows = [o for o in scene.objects if o.get('asset_family') == 'window']
    for window in windows:
        window.scale.x *= 1.06
        window.scale.z *= 1.01
    side_window = next(w for w in windows if w.location.x > 2)
    side_window.location.y = 3.80
    bpy.context.view_layer.update()
    front_window = next(w for w in windows if abs(w.location.y) < .1)
    side_window = next(w for w in windows if w.location.x > 2)
    door = next(o for o in scene.objects if o.get('asset_family') == 'glazed_door')
    frosted = bpy.data.materials.new('Loca / slightly frosted door glass')
    frosted.use_nodes = True
    nodes, links = frosted.node_tree.nodes, frosted.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.86, .93, .88, 1)
    shader.inputs['Roughness'].default_value = .18
    shader.inputs['Transmission Weight'].default_value = 1
    shader.inputs['IOR'].default_value = 1.20
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .15
    clear = nodes.new('ShaderNodeBsdfTransparent')
    links.new(clear.outputs[0], mix.inputs[1])
    links.new(shader.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes.get('Material Output').inputs['Surface'])
    frosted.surface_render_method = 'BLENDED'
    for obj in C.meshes(door):
        if obj.get('glazing'):
            apply_material(obj, frosted)
            obj.scale.x *= 1.04
            obj.scale.z *= 1.03
    scene.eevee.use_raytracing = True
    scene.eevee.ray_tracing_options.resolution_scale = '4'
    # Stable clear glazing for the fixed windows; the door alone is frosted.
    clear_mat = bpy.data.materials.new('Loca / quiet clear window glass')
    clear_mat.use_nodes = True
    clear_mat.surface_render_method = 'BLENDED'
    shader = clear_mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.84, .94, .88, 1)
    shader.inputs['Alpha'].default_value = .07
    shader.inputs['Roughness'].default_value = .18
    for root in windows:
        for obj in C.meshes(root):
            if obj.get('glazing'):
                apply_material(obj, clear_mat)
    cleanup_faces = 0
    for obj in C.meshes(door):
        if 'movable leaf' not in obj.name:
            continue
        # Cut a straight aperture through the inferred glass remnants. Retain
        # the yellow handle even where its supports overlap the opening.
        mesh = obj.data.copy()
        obj.data = mesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        keep_gold = bm.faces.layers.int.new('retain_original_handle')
        shader = mesh.materials[0].node_tree.nodes.get('Principled BSDF')
        texture = shader.inputs['Base Color'].links[0].from_node.image
        pixels = np.asarray(texture.pixels[:], dtype=np.float32).reshape(texture.size[1], texture.size[0], 4)
        uv_layer = bm.loops.layers.uv.active
        for face in bm.faces:
            uv = sum((loop[uv_layer].uv for loop in face.loops), Vector((0, 0))) / len(face.loops)
            rgb = pixels[min(texture.size[1]-1, max(0, int(uv.y*texture.size[1]))),
                         min(texture.size[0]-1, max(0, int(uv.x*texture.size[0]))), :3]
            face[keep_gold] = int(rgb[0] > .6 and rgb[1] > .4 and rgb[2] < .55)
        transform = obj.matrix_world.inverted() @ door.matrix_world
        for co, normal in [((-.335, 0, 0), (1, 0, 0)), ((.335, 0, 0), (1, 0, 0)),
                           ((0, 0, .64), (0, 0, 1)), ((0, 0, 2.015), (0, 0, 1))]:
            bmesh.ops.bisect_plane(bm, geom=[*bm.verts, *bm.edges, *bm.faces],
                plane_co=transform @ Vector(co),
                plane_no=transform.inverted().transposed().to_3x3() @ Vector(normal), dist=.000001)
        selected = []
        for face in bm.faces:
            p = obj.matrix_world @ face.calc_center_median()
            local = door.matrix_world.inverted() @ p
            if abs(local.x) < .335 and .64 < local.z < 2.015 and abs(local.y) < .065 and not face[keep_gold]:
                selected.append(face)
        cleanup_faces += len(selected)
        bmesh.ops.delete(bm, geom=selected, context='FACES')
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000003)
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()
    hinge = next(o for o in door.children_recursive if o.get('max_open_angle_deg'))
    for label, position, dimensions in [
        ('upper', (0, -.045, 2.015), (.71, .022, .028)),
        ('lower', (0, -.045, .640), (.71, .022, .028)),
        ('left', (-.340, -.045, 1.328), (.025, .022, 1.40)),
        ('right', (.340, -.045, 1.328), (.025, .022, 1.40)),
    ]:
        trim = P.block('Door / clean '+label+' glazing bead', door.matrix_world @ Vector(position),
                       dimensions, 'sage', .004)
        trim.parent = hinge
        trim.matrix_parent_inverse = hinge.matrix_world.inverted()
        trim.color = (.015, .18, 0, 1)
    names = ['left return', 'between openings', 'right return', 'above entrance',
        'under window', 'above window', 'right wall front return', 'right wall back return',
        'right wall under window', 'right wall above window', 'back wall']
    for obj in list(scene.objects):
        if obj.name in ['Room shell / ' + name for name in names]:
            bpy.data.objects.remove(obj, do_unlink=True)

    def opening(root, axis):
        lo, hi = B.bounds(C.meshes(root))
        if root.get('asset_family') == 'window':
            # Sills overhang the jambs: fit to the narrowest mid-height frame,
            # not the overall bounding box which includes those overhangs.
            points = np.array([o.matrix_world @ v.co for o in C.meshes(root)
                               if not o.get('glazing') for v in o.data.vertices])
            spans = []
            for ratio in [.30, .50, .70]:
                z = lo.z + (hi.z-lo.z)*ratio
                band = points[np.abs(points[:, 2]-z) < (hi.z-lo.z)*.035]
                if len(band):
                    spans.append((band[:, axis].min(), band[:, axis].max()))
            return (max(a for a, b in spans)+.012, min(b for a, b in spans)-.012,
                    max(0, lo.z+.05), hi.z-.06)
        return (lo[axis] + .012, hi[axis] - .012, max(0, lo.z + .012), hi.z - .03)

    def wall_with_openings(label, position, start, end, holes, side=False, colored=False):
        holes = sorted(holes)
        segments = []
        cursor = start
        for left, right, low, high in holes:
            segments += [(cursor, left, 0, 3), (left, right, 0, low), (left, right, high, 3)]
            cursor = right
        segments.append((cursor, end, 0, 3))
        for i, (a, b, lo, hi) in enumerate(segments):
            if b - a < .001 or hi - lo < .001:
                continue
            p = (position, (a + b) / 2, (lo + hi) / 2) if side else ((a + b) / 2, position, (lo + hi) / 2)
            size = (.16, b - a, hi - lo) if side else (b - a, .16, hi - lo)
            yellow_wall(label + ' fitted panel ' + str(i), p, size, yellow if colored else cream)

    wall_with_openings('front wall', 0, -2.6, 2.6, [opening(door, 0), opening(front_window, 0)])
    wall_with_openings('right wall', 2.6, 0, 5.3, [opening(side_window, 1)], side=True)
    wall_with_openings('yellow rear wall', 5.3, -2.6, 2.6, [], colored=True)
    ceiling = C.wall('ceiling', (0, 2.65, 3.07), (5.4, 5.3, .14))
    apply_material(ceiling, cream)
    # A soft exterior card keeps refraction from looking into an empty void.
    backdrop = C.wall('right window daylight', (3.15, 3.80, 1.50), (.02, 2.1, 3.0))
    apply_material(backdrop, cream)
    shelves = []
    upgraded_shelf = (P.ROOT / 'wall_shelf/tripo-generated/review/asset.blend').exists()
    for z in [1.65, 2.30]:
        unmarked = (P.ROOT / 'wall_shelf/tripo-generated/scene-ready/asset.blend').exists()
        shelf = C.load('wall_shelf', (1.43, 0, 0), quality='scene-ready' if unmarked else 'review' if upgraded_shelf else 'local')
        if upgraded_shelf:
            clean_shelf_material(shelf)
        if upgraded_shelf:
            shelf.scale.y = .70
        bpy.context.view_layer.update()
        shelf_lo, shelf_hi = B.bounds(C.meshes(shelf))
        shelf.location.y += 5.225-shelf_hi.y
        bpy.context.view_layer.update()
        shelf.location.z += z-C.surface(shelf, 1.43, 5.07)
        bpy.context.view_layer.update()
        C.role(shelf, 'context')
        shelves.append(shelf)
        for x in [1.12, 1.45, 1.78]:
            cup = C.supported('latte_cup', shelf, x, 5.07, scale=.90, quality='functional')
            C.role(cup, 'context')
        shelf_lo, shelf_hi = B.bounds(C.meshes(shelf))
        diffuser = P.block('Shelf / fixed warm diffuser', (1.43, 5.08, shelf_hi.z-.035),
            (.95, .015, .012), 'cream', .004)
        diffuser.color = (0, 0, 0, 1)
        diffuser['ghost_role'] = 'absent'
        data = bpy.data.lights.new('Shelf / fixed warm wash ' + str(z), 'AREA')
        data.energy = 8
        data.color = (1, .77, .48)
        data.shape = 'RECTANGLE'
        data.size = .95
        data.size_y = .06
        lamp = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(lamp)
        lamp.location = (1.43, 5.04, shelf_hi.z-.035)
        lamp.rotation_euler = (Vector((1.43, 5.20, shelf_hi.z-.3))-lamp.location).to_track_quat('-Z', 'Y').to_euler()
    upgraded_pendant = (P.ROOT / 'pendant/tripo-generated/review/asset.blend').exists()
    pendant = C.load('pendant', (1.15, 1.55, 0)) if upgraded_pendant else P.build('pendant')
    pendant.name = 'Ceiling / pendant above the table'
    pendant.location.x = 1.15
    pendant.location.y = 1.55
    bpy.context.view_layer.update()
    pendant_lo, pendant_hi = B.bounds(C.meshes(pendant))
    pendant.location.z += 3.0-pendant_hi.z
    bpy.context.view_layer.update()
    pendant_lo, pendant_hi = B.bounds(C.meshes(pendant))
    pendant['asset_family'] = 'pendant'
    C.role(pendant, 'context')
    data = bpy.data.lights.new('Table / fixed pendant light', 'AREA')
    data.energy = 30
    data.color = (1, .83, .59)
    data.shape = 'DISK'
    data.size = .28
    lamp = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(lamp)
    lamp.location = (1.15, 1.55, pendant_lo.z-.012)
    # Default local -Z points toward the table.
    for x in [-.66, .59]:
        before = set(bpy.data.objects)
        P.block('Wall / small sage light mount', (x, 5.17, 2.68), (.10, .07, .12), 'sage', .025)
        P.ball('Wall / warm frosted globe', (x, 5.10, 2.68), (.065, .065, .065), 'cream')
        fixture = P.group('Wall / quiet practical fixture', before)
        fixture['asset_family'] = 'wall_sconce_local'
        C.role(fixture, 'context')
        data = bpy.data.lights.new('Wall / fixed soft practical ' + str(x), 'POINT')
        data.energy = 6
        data.color = (1, .80, .55)
        data.shadow_soft_size = .09
        lamp = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(lamp)
        lamp.location = (x, 5.06, 2.68)
    data = bpy.data.lights.new('Full-height right window / fixed soft key', 'AREA')
    data.energy = 150
    data.shape = 'RECTANGLE'
    data.size = 1.20
    data.size_y = 1.4
    lamp = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(lamp)
    lamp.location = (2.95, 3.80, 2.15)
    lamp.rotation_euler = (Vector((.15, 4.1, 1.1)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
    return dict(window_width_scale=1.06, fitted_openings_overlap_m=.012,
        rear_window_removed=True, right_full_height_window=list(side_window.location), shelves=len(shelves),
        door_upper_glass_residual_faces_removed=cleanup_faces,
        fixed_practicals=['Two shelf washes', 'Two wall globes', 'Pendant above the table'],
        materials=['yellow clay plaster', 'warm clay floor tiles', 'gentle matte table wood grain'])


def polish_practicals(scene):
    """Keep light emitters below diffusers and outside opaque fixture meshes."""
    menu = next((o for o in scene.objects if o.get('asset_family') == 'menu_board'), None)
    if menu:
        lo, hi = B.bounds(C.meshes(menu))
        middle = (lo+hi)/2
        for fixture in [o for o in scene.objects if o.get('asset_family') == 'wall_sconce_local']:
            a, b = B.bounds(C.meshes(fixture))
            centre = (a+b)/2
            target_x = lo.x-.18 if centre.x < middle.x else hi.x+.18
            fixture.location.x += target_x-centre.x
            fixture.location.z += middle.z-centre.z
        for lamp in [o for o in scene.objects if o.type == 'LIGHT' and o.name.startswith('Wall / fixed soft practical')]:
            lamp.location.x = lo.x-.18 if lamp.location.x < middle.x else hi.x+.18
            lamp.location.z = middle.z
    pendant = next((o for o in scene.objects if o.get('asset_family') == 'pendant'), None)
    if pendant and not any(o.name.startswith('Pendant / warm opal diffuser') for o in pendant.children_recursive):
        lo, hi = B.bounds(C.meshes(pendant))
        diffuser = P.lathe('Pendant / warm opal diffuser', [(0, 0), (.18, 0), (.185, .004),
            (.18, .008), (0, .008)], (pendant.location.x, pendant.location.y, lo.z+.022), 'cream')
        diffuser.parent = pendant
        diffuser.matrix_parent_inverse = pendant.matrix_world.inverted()
        mat = P.material('cream').copy()
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Emission Color'].default_value = (1, .76, .44, 1)
        shader.inputs['Emission Strength'].default_value = .65
        diffuser.data.materials.clear()
        diffuser.data.materials.append(mat)
        C.role(pendant, 'context')
    for obj in scene.objects:
        if obj.get('max_open_angle_deg'):
            obj.animation_data_clear()
            obj.rotation_euler.z = 0
        if obj.name.startswith('Wall / small sage light mount'):
            obj.location.y = 5.195
        elif obj.type == 'LIGHT' and obj.name.startswith('Wall / fixed soft practical'):
            obj.location.y = 5.00
        elif obj.type == 'LIGHT' and obj.name.startswith('Table / fixed pendant light'):
            pendant = next(o for o in scene.objects if o.get('asset_family') == 'pendant')
            lo, hi = B.bounds(C.meshes(pendant))
            obj.location.z = lo.z-.012
    for shelf in [o for o in scene.objects if o.get('asset_family') == 'wall_shelf']:
        lo, hi = B.bounds(C.meshes(shelf))
        underside = []
        for obj in C.meshes(shelf):
            inverse = obj.matrix_world.inverted()
            hit, p, n, face = obj.ray_cast(inverse @ Vector((1.43, 5.07, lo.z-.03)),
                inverse.to_3x3() @ Vector((0, 0, 1)))
            if hit:
                underside.append((obj.matrix_world @ p).z)
        if not underside:
            continue
        z = min(underside)
        lights = [o for o in scene.objects if o.type == 'LIGHT' and o.name.startswith('Shelf / fixed warm wash')]
        lamp = min(lights, key=lambda o:abs(o.location.z-hi.z))
        lamp.location.z = z-.013
        strips = [o for o in scene.objects if o.name.startswith('Shelf / fixed warm diffuser')]
        strip = min(strips, key=lambda o:abs(o.location.z-hi.z))
        strip.location.z = z-.004
        strip.dimensions.z = .006


def orient_bone(arm, bone, direction, position=None):
    world = arm.matrix_world @ bone.matrix
    old = world.to_3x3().col[1].normalized()
    rotation = old.rotation_difference(direction.normalized())
    result = rotation.to_matrix().to_4x4() @ world
    result.translation = world.translation if position is None else position
    bone.matrix = arm.matrix_world.inverted() @ result
    bpy.context.view_layer.update()


class Grip:
    def __init__(self, arm, side='Right'):
        self.arm = arm
        self.side = side
        self.upper = named(arm, side+'Arm')
        self.fore = named(arm, side+'ForeArm')
        self.hand = named(arm, side+'Hand')
        self.length_a = (arm.matrix_world.to_3x3() @ (self.upper.tail-self.upper.head)).length
        self.length_b = (arm.matrix_world.to_3x3() @ (self.fore.tail-self.fore.head)).length
        wrist = arm.matrix_world @ self.hand.head
        index = arm.matrix_world @ named(arm, side+'HandIndex1').head
        pinky = arm.matrix_world @ named(arm, side+'HandPinky1').head
        forward = ((index+pinky)/2-wrist).normalized()
        across = (index-pinky).normalized()
        across = (across-forward*across.dot(forward)).normalized()
        normal = forward.cross(across).normalized()
        self.rest_frame = Matrix((forward, across, normal)).transposed()
        self.rest_hand_world = (arm.matrix_world @ self.hand.matrix).copy()

    def pose(self, grip, frame, forward=None, across=None, wrist_offset=.060):
        arm = self.arm
        # Hand approaches the handle from the operator's right, palm down.
        forward = Vector((-1, 0, -.10)).normalized() if forward is None else forward.normalized()
        across = Vector((0, -1, 0)) if across is None else across.normalized()
        normal = forward.cross(across).normalized()
        dorsal = normal if self.side == 'Right' else -normal
        frame_matrix = Matrix((forward, across, normal)).transposed()
        delta = frame_matrix @ self.rest_frame.inverted()
        wrist = grip - forward*wrist_offset + dorsal*.021
        shoulder = arm.matrix_world @ self.upper.head
        target = wrist-shoulder
        distance = target.length
        assert distance < (self.length_a+self.length_b)*.99, ('Arm cannot reach', distance)
        direction = target.normalized()
        along = (self.length_a**2-self.length_b**2+distance**2)/(2*distance)
        height = math.sqrt(max(0, self.length_a**2-along**2))
        pole = Vector((-.9 if self.side == 'Right' else .9, .15, -.7))
        pole = (pole-direction*pole.dot(direction)).normalized()
        elbow = shoulder+direction*along+pole*height
        orient_bone(arm, self.upper, elbow-shoulder)
        orient_bone(arm, self.fore, wrist-elbow)
        world = delta.to_4x4() @ self.rest_hand_world
        world.translation = wrist
        self.hand.matrix = arm.matrix_world.inverted() @ world
        bpy.context.view_layer.update()
        # Curl the actual finger chains around the cylinder; do not rotate the arm as a rigid prop.
        for finger in ['Index', 'Middle', 'Ring', 'Pinky']:
            directions = [forward*.05-dorsal, -forward*.85-dorsal*.52, -forward*.85+dorsal*.52]
            for i, direction in enumerate(directions, 1):
                orient_bone(arm, named(arm, self.side+'Hand'+finger+str(i)), direction)
        directions = [forward*.12+across*.4-dorsal*.9,
                      forward*.70-across*.12-dorsal*.68,
                      forward*.65-across*.20+dorsal*.73]
        for i, direction in enumerate(directions, 1):
            orient_bone(arm, named(arm, self.side+'HandThumb'+str(i)), direction)
        affected = [self.upper, self.fore, self.hand] + [b for b in arm.pose.bones if self.side+'Hand' in b.name and b != self.hand]
        for bone in affected:
            bone.rotation_mode = 'QUATERNION'
            bone.keyframe_insert('rotation_quaternion', frame=frame)
            bone.keyframe_insert('location', frame=frame)
        error = ((arm.matrix_world @ self.hand.head)-wrist).length
        assert error < .002, error
        return dict(wrist_error_m=error, reach_m=distance, wrist=list(wrist))


def outlets(root):
    inverse = root.matrix_world.inverted()
    vertices = np.array([inverse @ (o.matrix_world @ v.co) for o in C.meshes(root) for v in o.data.vertices])
    bottom = vertices[vertices[:, 2] < vertices[:, 2].min()+.018]
    # In calibrated asset coordinates the actual transverse tube follows Y.
    dark = []
    for obj in C.meshes(root):
        centres, rgb = samples(obj)
        local = np.array([inverse @ Vector(p) for p in centres])
        selected = (local[:, 2] < .035) & (local[:, 0] < -.025) & (rgb.max(axis=1) < .48)
        dark.extend(local[selected].tolist())
    dark = np.asarray(dark)
    result = []
    for sign in [-1, 1]:
        candidates = dark[dark[:, 1]*sign > .010] if len(dark) else np.empty((0, 3))
        if len(candidates) > 8:
            extent = candidates[:, 1]*sign
            band = candidates[extent > np.quantile(extent, .55)]
        else:
            edge = np.quantile(bottom[:, 1], .03 if sign < 0 else .97)
            band = bottom[np.abs(bottom[:, 1]-edge)<.0015]
        point = np.mean(band, axis=0)
        outward = (root.matrix_world.to_3x3() @ Vector((0, sign, 0))).normalized()
        result.append((root.matrix_world @ Vector(point.tolist()), outward))
    return result
