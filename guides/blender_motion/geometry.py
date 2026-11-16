"""Shared native Blender geometry from the approved bar/table study.

These functions model real meshes. They do not import or execute the prototype.
"""
import bpy
import math
from mathutils import Vector
MAT = None


def finish(obj, name):
    obj.name = name
    obj.data.materials.append(MAT)
    return obj


def block(name, location, size, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = finish(bpy.context.object, name)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    return obj


def lathe(name, profile, location, segments=48, ellipse=1):
    vertices = []
    rings = []
    for radius, height in profile:
        if abs(radius) < 1e-8:
            rings.append([len(vertices)])
            vertices.append((0, 0, height))
            continue
        rings.append(list(range(len(vertices), len(vertices) + segments)))
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle) * ellipse, height))
    faces = []
    for lower, upper in zip(rings, rings[1:]):
        for i in range(segments):
            nxt = (i + 1) % segments
            if len(lower) == 1 and len(upper) == 1:
                break
            if len(lower) == 1:
                faces.append((lower[0], upper[nxt], upper[i]))
            elif len(upper) == 1:
                faces.append((lower[i], lower[nxt], upper[0]))
            else:
                faces.append((lower[i], lower[nxt], upper[nxt], upper[i]))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    finish(obj, name)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def tube(name, points, radius=0.015, handle_type='AUTO'):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, location in zip(spline.bezier_points, points):
        point.co = location
        point.handle_left_type = handle_type
        point.handle_right_type = handle_type
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    # Conversion acts on every selected object. Appended assets may retain
    # selection; converting them here would silently bake their armature away.
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.select_set(False)
    finish(obj, name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def plate_outline(name, outline, thickness, lift=None):
    """A flat stamped part: a closed (possibly concave) XY outline, optionally bent by lift(x, y) -> z, given thickness."""
    import bmesh
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, lift(x, y) if lift else 0)) for x, y in outline]
    edges = [bm.edges.new((verts[i], verts[(i + 1) % len(verts)])) for i in range(len(verts))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj, name)
    solid = obj.modifiers.new("Stamped thickness", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0
    return obj


def bottle(name, x, y, z, height=0.32, radius=0.045):
    profile = [(0, 0), (radius * .85, 0), (radius, .015),
               (radius, height * .63), (radius * .88, height * .7),
               (radius * .4, height * .81), (radius * .36, height * .95),
               (radius * .45, height * .96), (radius * .45, height),
               (0, height)]
    return lathe(name, profile, (x, y, z), 32)


def glass(name, x, y, z, scale=1, water=True):
    """Tall straight tumbler (rocks-glass build, 0.08 x 0.125 m): closed exterior, 3 mm wall, heavy 20 mm base.
    With water, a surface contour 2/3 up is drawn through the clear wall."""
    obj = lathe(name, [(0, 0), (.0385, 0), (.040, .003), (.040, .122), (.0395, .125),
                      (.0375, .125), (.037, .122), (.037, .022), (.035, .020), (0, .020)], (x, y, z))
    obj.scale = (scale, scale, scale)
    obj["resting_surface_z"] = z
    if water:
        obj["clear_vessel_shell"] = True
        level = [(.0368 * math.cos(k * math.tau / 48), .0368 * math.sin(k * math.tau / 48), .0833) for k in range(49)]
        surface = tube(name + " water surface", level, .0005)
        surface["composition_role"] = "drink_contents"
        surface["placement_reason"] = "Water level two thirds up, drawn through the clear wall"
        surface.parent = obj
    return obj


def stool(name, x, y, rotation=0):
    components = []
    seat = lathe(name + " sculpted seat", [(0, .72), (.17, .72), (.185, .735),
                    (.19, .762), (.17, .78), (0, .78)], (x, y, 0), ellipse=.9)
    components.append(seat)
    for side in [-1, 1]:
        for front in [-1, 1]:
            components.append(tube(name + " splayed bentwood leg", [
                (x + side * .12, y + front * .105, .73),
                (x + side * .14, y + front * .13, .45),
                (x + side * .22, y + front * .19, .025)], .023))
    points = [(x + .19 * math.cos(a), y + .16 * math.sin(a), .32)
              for a in [i * 2 * math.pi / 32 for i in range(33)]]
    components.append(tube(name + " circular footrest", points, .012))
    components.append(tube(name + " curved back", [
        (x - .145, y - .105, .74), (x - .17, y - .14, 1.04),
        (x, y - .19, 1.12), (x + .17, y - .14, 1.04),
        (x + .145, y - .105, .74)], .021))
    return components


def camera(name, position, direction, lens=32):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 32
    data.sensor_fit = "HORIZONTAL"
    data.clip_start = .05
    data.clip_end = 50
    data.passepartout_alpha = 1
    data.show_composition_thirds = True
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    return obj
