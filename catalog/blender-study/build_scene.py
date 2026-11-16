"""Blender proof: real low truck, then a scripted cut to the next shot.

Run with Blender --background --python build_scene.py -- --probes
or Blender --python build_scene.py -- --watch to inspect the build live.
The owner explicitly requested this 3D experiment after stopping sprite work.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
OUT.mkdir(exist_ok=True)
(OUT / "frames").mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
WATCH = "--watch" in ARGS
SCENE = bpy.context.scene
INK = (0.12, 0.24, 0.34)
MAT = None


def progress(message, detail="", preview=False):
    data = dict(message=message, progress=detail, ready=False, preview=preview)
    target = ROOT / "status.js"
    tmp = target.with_suffix(".tmp")
    tmp.write_text("blenderProgress(" + json.dumps(data) + ");\n")
    tmp.replace(target)
    print(message, detail, flush=True)


def initialize():
    global MAT
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    SCENE.unit_settings.system = "METRIC"
    SCENE.render.engine = "CYCLES"
    SCENE.cycles.device = "CPU"
    SCENE.cycles.samples = 1
    SCENE.cycles.use_denoising = False
    SCENE.render.threads_mode = "FIXED"
    SCENE.render.threads = 6
    SCENE.render.resolution_x = 540
    SCENE.render.resolution_y = 960
    SCENE.render.resolution_percentage = 100
    SCENE.render.fps = 15
    SCENE.frame_start = 1
    SCENE.frame_end = 84
    SCENE.render.film_transparent = True
    SCENE.render.image_settings.file_format = "PNG"
    SCENE.render.image_settings.color_mode = "RGBA"
    SCENE.render.image_settings.color_depth = "8"
    SCENE.render.filepath = str(OUT / "frames" / "frame_")
    SCENE.view_settings.view_transform = "Standard"
    MAT = bpy.data.materials.new("Neutral occluding geometry; surfaces omitted from overlay")
    MAT.diffuse_color = (0.55, 0.68, 0.76, 1)
    MAT.use_nodes = True
    nodes = MAT.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
    MAT.node_tree.links.new(emission.outputs[0], output.inputs[0])
    SCENE.render.use_freestyle = True
    settings = SCENE.view_layers[0].freestyle_settings
    settings.as_render_pass = True
    settings.crease_angle = math.radians(100)
    settings.use_smoothness = True
    lines = settings.linesets[0]
    lines.name = "Visible contours, rims and construction seams"
    lines.select_silhouette = True
    lines.select_border = True
    lines.select_crease = True
    lines.select_edge_mark = True
    lines.select_by_visibility = True
    lines.visibility = "VISIBLE"
    style = lines.linestyle
    style.color = INK
    style.alpha = 1
    style.thickness = 1.65
    style.caps = "ROUND"
    # Freestyle provides camera-dependent lines and hidden-surface removal.
    # Output ONLY that pass: occluding mesh faces never become colored fills.
    tree = bpy.data.node_groups.new("Transparent contour output", "CompositorNodeTree")
    SCENE.compositing_node_group = tree
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    layers = tree.nodes.new("CompositorNodeRLayers")
    layers.scene = SCENE
    output = tree.nodes.new("NodeGroupOutput")
    tree.links.new(layers.outputs["Freestyle"], output.inputs["Image"])
    SCENE["guide_id"] = "bar_low_truckr_mm"
    SCENE["script_context"] = "restaurant-room-tour: bar -> seat"
    SCENE["source_timing"] = "1.2 s frame, 1.8 s truck, 1.0 s hold, cut to next shot"
    SCENE["artwork_export"] = "Freestyle pass only; final alpha x 0.5 in export_sequence.py"


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


def tube(name, points, radius=0.015):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, location in zip(spline.bezier_points, points):
        point.co = location
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.select_set(False)
    finish(obj, name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def bottle(name, x, y, z, height=0.32, radius=0.045):
    profile = [(0, 0), (radius * .85, 0), (radius, .015),
               (radius, height * .63), (radius * .88, height * .7),
               (radius * .4, height * .81), (radius * .36, height * .95),
               (radius * .45, height * .96), (radius * .45, height),
               (0, height)]
    return lathe(name, profile, (x, y, z), 32)


def glass(name, x, y, z, scale=1):
    # Closed exterior plus inner well: actual rim thickness, wall and heavy base.
    obj = lathe(name, [(0, 0), (.043, 0), (.049, .009), (.055, .115),
                      (.055, .122), (.050, .122), (.048, .114),
                      (.044, .023), (0, .023)], (x, y, z))
    obj.scale = (scale, scale, scale)
    obj["resting_surface_z"] = z
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


def build_bar():
    progress("Building the bar counter and glass contacts.")
    block("Bar counter solid carcass", (0, .29, .55), (5.8, .92, 1.1), .018)
    block("Continuous rounded counter top", (0, .25, 1.105), (6.05, 1.16, .07), .025)
    block("Counter lower plinth", (0, -.185, .12), (5.78, .035, .12), .009)
    for x in [-2.85, -1.4, 0, 1.4, 2.85]:
        block("Inset panel stile", (x, -.18, .61), (.035, .018, .77), .004)
    for z in [.23, .98]:
        block("Inset panel rail", (0, -.18, z), (5.7, .018, .025), .003)
    tube("Customer brass foot rail", [(-2.8, -.50, .24), (2.8, -.50, .24)], .018)
    for x in [-2.5, -.9, .9, 2.5]:
        tube("Foot rail bracket", [(x, -.18, .18), (x, -.36, .18), (x, -.50, .24)], .011)
    for i, x in enumerate([-.04, 1.15, -1.35]):
        glass("Tumbler " + str(i + 1), x, -.06, 1.14, 1.35)
    for x in [.72, .92, 1.12]:
        tube("Beer tap swan neck", [(x, .52, 1.14), (x, .52, 1.57),
             (x, .43, 1.66), (x, .30, 1.62), (x, .27, 1.52)], .018)
        tube("Tap handle stem", [(x, .42, 1.62), (x, .42, 1.77)], .013)
        lathe("Ceramic tap handle", [(0, 0), (.027, .015), (.031, .09),
            (.022, .13), (0, .14)], (x, .42, 1.73), 24)


def build_stools():
    progress("Adding foreground stools for genuine depth and occlusion.")
    for i, x in enumerate([-.75, .8, 2.3]):
        stool("Bar stool " + str(i + 1), x, -.95)


def build_backbar():
    progress("Adding distant shelves and bottle silhouettes.")
    for z in [1.38, 1.95]:
        block("Floating backbar shelf", (0, 1.38, z), (5.6, .32, .045), .009)
        # Grouped repetition, with breathing spaces instead of a uniform grid.
        xs = [-2.48, -2.28, -2.08, -1.48, -1.28, -1.08, -.88,
              -.31, -.10, .11, .66, .86, 1.06, 1.27, 1.97, 2.18, 2.39]
        for i, x in enumerate(xs):
            if z > 1.5:
                x += .055
            name = "Background focal bottle" if i == 10 else "Shelf bottle"
            bottle(name, x, 1.36, z + .023,
                   .24 + .055 * (i % 3), .034 + .007 * (i % 2))
    for x in [-2.35, -.8, .8, 2.35]:
        tube("Shelf upright", [(x, 1.50, 1.10), (x, 1.50, 2.47)], .011)


def build_table():
    progress("Building the next shot: a high view of the best table.")
    x, y = 9, 0
    lathe("Round dining tabletop", [(0, .72), (.61, .72), (.65, .735),
          (.65, .77), (.63, .785), (0, .785)], (x, y, 0), 64)
    lathe("Table pedestal", [(0, 0), (.33, .01), (.35, .035), (.08, .08),
          (.065, .69), (.22, .72), (0, .72)], (x, y, 0), 48)
    for i, side in enumerate([-1, 1]):
        # Local +Y points away from each diner, towards the table centre.
        # Opposing guests therefore have opposing, rather than parallel, settings.
        group = bpy.data.objects.new("Place setting " + str(i + 1), None)
        bpy.context.collection.objects.link(group)
        group.location = (x + side * .30, y, .785)
        group.rotation_euler.z = -math.pi / 2 if side == -1 else math.pi / 2
        group["diner_side"] = "west" if side == -1 else "east"
        group["local_forward"] = "+Y towards table centre"
        parts = []
        parts.append(lathe("Dinner plate " + str(i + 1), [(0, 0), (.10, 0), (.145, .015),
              (.16, .024), (.16, .032), (.14, .027), (.10, .008), (0, .008)],
              (0, 0, 0), 48))
        # Knife and four-tined fork are shaped mesh objects, not drawn symbols.
        parts.append(tube("Knife handle " + str(i + 1), [(.20, -.13, .012),
             (.20, .035, .012)], .008))
        parts.append(block("Knife blade " + str(i + 1), (.196, .10, .012), (.014, .14, .004), .003))
        parts.append(tube("Fork handle " + str(i + 1), [(-.20, -.13, .012),
             (-.20, .05, .012)], .006))
        for offset in [-.009, -.003, .003, .009]:
            parts.append(tube("Fork tine", [(-.20, .05, .012),
                 (-.20 + offset, .075, .012),
                 (-.20 + offset, .115, .012)], .0018))
        parts.append(glass("Water glass at table " + str(i + 1), .19, .21, 0))
        for part in parts:
            part.parent = group
        # Each dining chair faces its own plate. Seat height is 48 cm.
        chair = bpy.data.objects.new("Dining chair " + str(i + 1), None)
        bpy.context.collection.objects.link(chair)
        chair.location = (x + side * .84, y, 0)
        chair.rotation_euler.z = group.rotation_euler.z
        chair_parts = [lathe("Dining chair sculpted seat", [(0, .435), (.19, .435),
                      (.21, .45), (.21, .47), (.19, .48), (0, .48)], (0, 0, 0), ellipse=.91)]
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                chair_parts.append(tube("Dining chair tapered leg", [
                    (sx * .14, sy * .12, .445), (sx * .17, sy * .15, .03)], .018))
        chair_parts.append(tube("Dining chair curved back", [(-.15, -.12, .45),
            (-.185, -.17, .82), (0, -.21, .95), (.185, -.17, .82), (.15, -.12, .45)], .019))
        chair_parts.append(tube("Dining chair back rail", [(-.17, -.16, .76),
            (0, -.205, .80), (.17, -.16, .76)], .014))
        for part in chair_parts:
            part.parent = chair
    lathe("Bud vase", [(0, 0), (.035, 0), (.047, .065), (.022, .12),
          (.018, .17), (.013, .17), (.013, .12)], (x, y + .43, .785), 32)
    tube("Single botanical stem", [(x, y + .43, .88), (x + .015, y + .43, 1.02),
         (x + .045, y + .43, 1.08)], .003)
    tube("Botanical sprig", [(x + .01, y + .43, 1.00),
         (x - .045, y + .43, 1.04), (x - .065, y + .43, 1.065)], .002)


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


def setup_cameras():
    progress("Animating the visitor-side camera path and the scripted cut.")
    pitch = math.radians(12)
    yaw = math.radians(10)
    bar = camera("01 LOW BAR - truck right 0.8m", (-.8, -2.2, 1.05),
                 (math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    for frame, x in [(1, -.8), (19, -.8), (46, 0), (60, 0)]:
        bar.location.x = x
        bar.keyframe_insert(data_path="location", frame=frame)
    table = camera("02 HIGH TABLE - gentle approach", (9.38, -1.35, 2.02),
                   (-.38, 1.35, -1.21), lens=30)
    for frame, position in [(61, (9.38, -1.35, 2.02)), (84, (9.3462, -1.23, 1.9124))]:
        table.location = position
        table.keyframe_insert(data_path="location", frame=frame)
    marker = SCENE.timeline_markers.new("01 FRAME 1.2s -> TRUCK 1.8s -> HOLD 1s", frame=1)
    marker.camera = bar
    marker = SCENE.timeline_markers.new("02 CUT TO HIGH TABLE", frame=61)
    marker.camera = table
    SCENE.camera = bar
    SCENE.frame_set(1)
    # A visible viewport path; it is a guide object, excluded from rendering.
    path = tube("CAMERA PATH - visitor side, never behind bar",
                [(-.8, -2.2, 1.05), (0, -2.2, 1.05)], .009)
    path.hide_render = True
    path.display_type = "WIRE"


def validate():
    bar = bpy.data.objects["01 LOW BAR - truck right 0.8m"]
    tumbler = bpy.data.objects["Tumbler 1"]
    tracks = []
    rotations = []
    for frame in range(1, 61):
        SCENE.frame_set(frame)
        rotations.append(tuple(bar.rotation_euler))
        tracks.append(dict(frame=frame, x=bar.location.x, y=bar.location.y, z=bar.location.z))
    assert all(a["x"] <= b["x"] + 1e-7 for a, b in zip(tracks, tracks[1:])), "Truck must move right"
    assert all(abs(t["y"] + 2.2) < 1e-6 for t in tracks), "Camera must stay customer side"
    assert max(abs(v - rotations[0][i]) for r in rotations for i, v in enumerate(r)) < 1e-7
    assert abs(tumbler.location.z - 1.14) < 1e-6, "Glass must rest on countertop"
    # Compare projected near/far landmarks under an actual 0.8 m translation.
    shifts = {}
    for name, point in [("near_stool", Vector((-.75, -.95, .78))),
                        ("glass", Vector((-.04, -.06, 1.22))),
                        ("far_shelf", Vector((0, 1.36, 1.95)))]:
        positions = []
        for f in [19, 46]:
            SCENE.frame_set(f)
            bpy.context.view_layer.update()
            positions.append(world_to_camera_view(SCENE, bar, point).x)
        shifts[name] = positions[1] - positions[0]
    assert shifts["near_stool"] < shifts["glass"] < shifts["far_shelf"] < 0
    table_settings = []
    bpy.context.view_layer.update()
    for index in [1, 2]:
        group = bpy.data.objects["Place setting " + str(index)]
        plate = bpy.data.objects["Dinner plate " + str(index)]
        water = bpy.data.objects["Water glass at table " + str(index)]
        local_glass = water.location
        assert local_glass.x > 0 and local_glass.y > 0, "Glass must be above the knife, from diner's view"
        assert math.hypot(local_glass.x, local_glass.y) > .16 + .055 + .02
        forward = group.rotation_euler.to_matrix() @ Vector((0, 1, 0))
        toward_centre = Vector((9, 0, .785)) - group.location
        assert forward.dot(toward_centre) > .29, "Each setting must face its diner"
        assert abs(min((plate.matrix_world @ v.co).z for v in plate.data.vertices) - .785) < 1e-5
        assert abs(min((water.matrix_world @ v.co).z for v in water.data.vertices) - .785) < 1e-5
        table_settings.append(dict(diner=group["diner_side"], plate_centre=list(group.location),
                                   rotation_deg=round(math.degrees(group.rotation_euler.z)),
                                   fork="left of plate", knife="right of plate; blade inward",
                                   water_glass="upper right from diner's viewpoint"))
    data = dict(guide="bar_low_truckr_mm", script="restaurant-room-tour", step="bar",
                next_step="seat", next_guide="table_seat_high_in_mc", fps=15,
                total_frames=84, take_seconds=4, next_shot_seconds=1.6,
                camera_height_m=1.05, pitch_up_deg=12, truck_right_m=.8,
                composition_adaptation="Fixed 10-degree oblique bar view; truck direction and distance preserved",
                camera_positions=tracks, projected_horizontal_shifts=shifts,
                glass_base_z_m=1.14, countertop_z_m=1.14,
                viewpoint="Public customer aisle, y=-2.2; counter front y=-0.33",
                checks=dict(monotonic_rightward_truck=True, no_pan_or_zoom_during_truck=True,
                            genuine_depth_parallax=True, glass_contact=True,
                            visitor_accessible=True, visible_hands=0),
                render="Real meshes + visible Freestyle contours; no surface fills",
                table_layout=dict(guests=2, opposing_settings=table_settings,
                                  chair_seat_height_m=.48, tabletop_height_m=.785,
                                  centerpiece="Small vase moved to rear edge; centre clear"),
                proof_status="First Blender experiment; not published to catalog or API")
    (OUT / "scene-report.json").write_text(json.dumps(data, indent=2) + "\n")
    SCENE.frame_set(1)


def save():
    validate()
    bpy.ops.object.select_all(action="DESELECT")
    SCENE.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.region_3d.view_perspective = "CAMERA"
                space.region_3d.view_camera_zoom = 0
                space.shading.type = "SOLID"
                space.shading.color_type = "MATERIAL"
                space.shading.show_cavity = True
                space.shading.cavity_type = "BOTH"
                space.overlay.show_floor = False
                space.overlay.show_extras = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))
    progress("3D scene saved. Rendering the first contour previews.",
             "The editable scene and its real camera animation are available in Blender.")


def render_probes():
    for frame in [1, 46, 70]:
        SCENE.frame_set(frame)
        SCENE.render.filepath = str(OUT / ("probe_%04d.png" % frame))
        bpy.ops.render.render(write_still=True)
        if frame == 1:
            # Raw first preview; export applies final opacity to all sequence frames.
            import shutil
            shutil.copy2(OUT / "probe_0001.png", OUT / "poster.png")
        progress("Reviewing the first contour renders.", "Rendered camera frame %d." % frame, preview=True)
    SCENE.render.filepath = str(OUT / "frames" / "frame_")
    SCENE.frame_set(1)


STAGES = [initialize, build_bar, build_stools, build_backbar, build_table, setup_cameras, save]

if WATCH:
    # Timers allow Blender to redraw between model-building phases.
    queue = iter(STAGES)

    def tick():
        try:
            next(queue)()
            return 1.0
        except StopIteration:
            bpy.ops.screen.animation_play()
            return None
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    bpy.app.timers.register(tick, first_interval=1.0)
else:
    for stage in STAGES:
        stage()
    if "--probes" in ARGS:
        render_probes()
    if "--render" in ARGS:
        bpy.ops.render.render(animation=True)
