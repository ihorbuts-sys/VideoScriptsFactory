"""Add an instructional lighting variant to the same, corrected 3D scene.

Run after scene.blend in Blender's argument list. The contour output remains a
separate scene. The second scene shows actual illumination, highlights and shadows.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
guide = bpy.context.scene
guide.name = "01 Contour guide"
guide.use_fake_user = True
geometry = bpy.data.collections["Collection"]
geometry.name = "Guide subjects - reusable geometry"
environment = bpy.data.collections.new("Lighting set - excluded from guide contours")
guide.collection.children.link(environment)
line_set = guide.view_layers[0].freestyle_settings.linesets[0]
line_set.select_by_collection = True
line_set.collection = geometry
line_set.collection_negation = "INCLUSIVE"


def material(name, color, roughness=.5, metal=0, transmission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value = 1.45
    return mat


clay = material("Lighting study - neutral stone", (.56, .60, .62), .52)
ceramic = material("Lighting study - glazed porcelain", (.79, .81, .80), .20)
glass = material("Lighting study - frosted glass", (.83, .88, .90), .10, transmission=.72)
metal = material("Lighting study - brushed metal", (.45, .49, .51), .23, metal=.7)
wood = material("Lighting study - neutral pale timber", (.48, .47, .44), .48)
floor = material("Lighting study - matte floor", (.30, .32, .33), .85)
wall = material("Lighting study - plaster", (.72, .73, .70), .85)
for obj in geometry.objects:
    if obj.type != "MESH":
        continue
    name = obj.name.lower()
    mat = ceramic if "plate" in name or "vase" in name else glass if "glass" in name or "tumbler" in name or "bottle" in name else metal if any(s in name for s in ["tap", "knife", "fork", "foot rail"]) else wood if any(s in name for s in ["table", "chair", "stool", "counter", "shelf"]) else clay
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def block(name, position, size, mat=wall):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
    modifier.width = .008
    modifier.segments = 2
    obj.data.materials.append(mat)
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    environment.objects.link(obj)
    return obj


block("Lighting floor", (4, 1, -.04), (24, 14, .08), floor)
block("Bar rear plaster wall", (0, 1.72, 1.7), (6.8, .14, 3.4))
block("Bar ceiling blocks direct outdoor sun", (0, -.8, 3.05), (7, 5.2, .14))
block("Bar side wall blocks direct outdoor sun", (-3.45, -.8, 1.55), (.14, 5.2, 3.1))
# The real window is to the left of the diners, outside the medium shot.
# Its mullions cast shadows through an actual opening, not a painted gobo.
window_x = 7.55
block("Window wall below sill", (window_x, .2, .475), (.14, 4.5, .95))
block("Window wall above lintel", (window_x, .2, 2.95), (.14, 4.5, .70))
block("Window wall rear jamb", (window_x, 1.85, 1.775), (.14, 1.20, 1.65))
block("Window wall front jamb", (window_x, -1.45, 1.775), (.14, 1.20, 1.65))
for yy in [-.85, .20, 1.25]:
    block("Window vertical frame", (window_x, yy, 1.775), (.11, .045, 1.65), wood)
for zz in [.95, 1.775, 2.60]:
    block("Window horizontal frame", (window_x, .2, zz), (.11, 2.10, .045), wood)
block("Deep window sill", (window_x + .05, .2, .94), (.32, 2.22, .07), wood)


def light(name, kind, position, target, energy, color, size=None):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == "SUN":
        data.angle = math.radians(1.2)
    elif size is not None:
        data.shape = "DISK"
        data.size = size
    obj = bpy.data.objects.new(name, data)
    environment.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["instruction"] = "Fixed during take; creator chooses camera and subject placement"
    return obj


sun = light("Fixed morning sun through window", "SUN", (6, 1.5, 3.0), (9, 0, .785), 2.3, (1, .87, .70))
light("Soft window sky fill", "AREA", (7.65, .40, 2.15), (9, 0, .8), 55, (.72, .83, 1), 1.45)
light("Bar customer-side softbox", "AREA", (-2, -3, 3.8), (0, .3, 1.0), 120, (.82, .89, 1), 3)
light("Bar fixed broad ceiling fixture", "AREA", (0, -.7, 2.86), (0, .3, 1.0), 190, (1, .95, .86), 3)

# Assign opacity by instructional role, not distance alone. A useful far tap
# remains clearer than decorative shelves, while near framing stays restrained.
roles = {
    "hero": (1.0, 1.9, "Primary subject/contact that the creator must place clearly"),
    "support": (.68, 1.5, "Supports the subject and explains a usable place setting"),
    "important_background": (.78, 1.6, "A deliberate background landmark; retain legibility"),
    "foreground_frame": (.48, 1.6, "Near framing and depth cue; leave the subject readable"),
    "background": (.25, 1.15, "Quiet context and grouped rhythm; no competition with subject"),
    "structure": (.40, 1.3, "Physical support and room context, with low visual weight"),
}
role_collections = {}
for role in roles:
    collection = bpy.data.collections.new("Ghost role - " + role)
    geometry.children.link(collection)
    role_collections[role] = collection

object_plan = []
bpy.context.view_layer.update()
for obj in list(geometry.objects):
    if obj.type != "MESH" or obj.hide_render:
        continue
    name = obj.name.lower()
    if name in ["continuous rounded counter top", "round dining tabletop"] or "sculpted seat" in name:
        role = "hero"
    elif "background focal bottle" in name or "tap" in name:
        role = "important_background"
    elif "shelf" in name or "bottle" in name:
        role = "background"
    elif "bar stool" in name and "curved back" in name:
        role = "support"
    elif "bar stool" in name:
        role = "foreground_frame"
    elif any(term in name for term in ["panel", "plinth", "carcass", "foot rail", "dining chair", "table pedestal"]):
        role = "structure"
    else:
        role = "support"
    geometry.objects.unlink(obj)
    role_collections[role].objects.link(obj)
    alpha, thickness, reason = roles[role]
    if "counter top" in name:
        reason = "Continuous contact plane and converging leading edge; glasses stay physically attached"
    elif "round dining tabletop" in name:
        reason = "Frames the two opposing settings; its clear centre preserves usability and negative space"
    elif "bar stool" in name:
        reason = "The script sells bar seating: seats/backrests explain where to sit; lower legs provide restrained foreground depth"
    elif "tumbler" in name:
        reason = "Supporting evidence of bar use; this room-tour shot is about the bar and seating, not an ordered drink"
    elif "background focal bottle" in name:
        reason = "Selected distant landmark interrupts repetition and remains clearer than decorative bottles"
    elif "shelf bottle" in name:
        reason = "Grouped repetition with deliberate gaps establishes bar character without competing with the hero"
    elif "tap" in name:
        reason = "Recognizable background anchor helps the viewer read the bar and the lateral move"
    elif "dinner plate" in name or "water glass at table" in name:
        reason = "Part of a usable opposing setting; camera depth separates the near and far diner"
    elif "knife" in name or "fork" in name:
        reason = "Diner-relative left/right placement and inward knife blade make the setting functional"
    elif "vase" in name or "botanical" in name:
        reason = "Small rear-edge accent balances the diagonal settings while leaving the centre and sightlines clear"
    elif "dining chair" in name:
        reason = "Identifies the corresponding diner's position and faces the correct plate"
    obj["composition_role"] = role
    obj["placement_reason"] = reason
    obj["overlay_alpha_before_export"] = alpha
    bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    centre = sum(bounds, Vector()) / len(bounds)
    object_plan.append(dict(object=obj.name, role=role, reason=reason, world_bbox_centre_m=list(centre), alpha_before_export=alpha,
                            final_alpha_ceiling=round(alpha * .5, 3)))

settings = guide.view_layers[0].freestyle_settings
for line_set in list(settings.linesets):
    settings.linesets.remove(line_set)


def line_set(name, collection, color, alpha, thickness):
    lines = settings.linesets.new(name)
    lines.select_by_collection = True
    lines.collection = collection
    lines.collection_negation = "INCLUSIVE"
    lines.select_by_visibility = True
    lines.visibility = "VISIBLE"
    lines.select_silhouette = True
    lines.select_border = True
    lines.select_crease = True
    lines.select_edge_mark = True
    style = lines.linestyle
    style.color = color
    style.alpha = alpha
    style.thickness = thickness
    style.caps = "ROUND"


for role, (alpha, thickness, _) in roles.items():
    line_set(role, role_collections[role], (.12, .24, .34), alpha, thickness)

# Yellow accents belong to real surface locations. A light footprint is a
# projection of the actual window frame along the actual sun direction.
highlights = bpy.data.collections.new("Ghost light - selected surface highlights")
footprint = bpy.data.collections.new("Ghost light - projected window boundaries")
guide.collection.children.link(highlights)
guide.collection.children.link(footprint)
yellow = material("Ghost light cue", (.90, .65, .17), .5)


def light_line(name, points, collection):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = .00045
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, value in zip(spline.points, points):
        point.co = (*value, 1)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.data.materials.append(yellow)
    obj["composition_role"] = "lighting_cue"
    obj["placement_reason"] = "Explains fixed window illumination while preserving camera visibility"
    obj["light_fixed_during_take"] = True
    return obj


bpy.context.view_layer.update()
light_angle = math.atan2(1.5, -3)
for index in [1, 2]:
    plate = bpy.data.objects["Dinner plate " + str(index)]
    centre = plate.matrix_world.translation
    points = [(centre.x + .157 * math.cos(a), centre.y + .157 * math.sin(a), .819)
              for a in [light_angle + math.radians(-43 + j * 86 / 24) for j in range(25)]]
    light_line("Window-facing plate rim " + str(index), points, highlights)
    water = bpy.data.objects["Water glass at table " + str(index)]
    centre = water.matrix_world.translation
    points = [(centre.x + .0552 * math.cos(a), centre.y + .0552 * math.sin(a), .908)
              for a in [light_angle + math.radians(-34 + j * 68 / 20) for j in range(21)]]
    light_line("Window-facing glass rim " + str(index), points, highlights)


def project_window(y, z):
    travel = (z - .787) / 2.215
    return Vector((7.55 + 3 * travel, y - 1.5 * travel, .787))


def clip_to_table(a, b):
    direction = b - a
    relative = a - Vector((9, 0, .787))
    aa = direction.x ** 2 + direction.y ** 2
    bb = 2 * (relative.x * direction.x + relative.y * direction.y)
    cc = relative.x ** 2 + relative.y ** 2 - .638 ** 2
    disc = bb * bb - 4 * aa * cc
    if disc <= 0 or aa < 1e-8:
        return None
    lo = max(0, (-bb - math.sqrt(disc)) / (2 * aa))
    hi = min(1, (-bb + math.sqrt(disc)) / (2 * aa))
    return [a + lo * direction, a + hi * direction] if lo < hi else None


window_edges = [((-.85, .95), (1.25, .95)), ((1.25, .95), (1.25, 2.60)),
                ((1.25, 2.60), (-.85, 2.60)), ((-.85, 2.60), (-.85, .95)),
                ((-.85, 1.7525), (1.25, 1.7525)), ((-.85, 1.7975), (1.25, 1.7975)),
                ((.1775, .95), (.1775, 2.60)), ((.2225, .95), (.2225, 2.60))]
for index, (a, b) in enumerate(window_edges):
    clipped = clip_to_table(project_window(*a), project_window(*b))
    if clipped:
        light_line("Window light/shadow boundary " + str(index), [tuple(p) for p in clipped], footprint)
line_set("Warm rim highlights", highlights, (.78, .48, .08), .90, 2.2)
line_set("Faint window-light footprint", footprint, (.78, .48, .08), .38, 1.3)
world = bpy.data.worlds.new("Cool ambient daylight")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.68, .79, 1, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .12
guide.world = world

data = bpy.data.cameras.new("LIGHTING SETUP - window and opposing diners")
data.lens = 35
data.sensor_width = 36
setup = bpy.data.objects.new("LIGHTING SETUP - window and opposing diners", data)
environment.objects.link(setup)
setup.location = (11.4, -3.6, 2.9)
setup.rotation_euler = (Vector((8.65, .12, 1.05)) - setup.location).to_track_quat("-Z", "Y").to_euler()

lit = guide.copy()
lit.name = "02 Morning window light"
lit.use_fake_user = True
lit.render.engine = "BLENDER_EEVEE"
lit.eevee.taa_render_samples = 32
lit.eevee.taa_samples = 16
lit.eevee.use_raytracing = True
lit.render.use_freestyle = False
lit.render.use_compositing = False
lit.render.film_transparent = False
lit.view_settings.view_transform = "AgX"
lit["lighting_lesson"] = "Fixed warm side light; real window shadows, contact shadows and curved-surface highlights"
lit["no_animated_lights"] = True
lit.view_layers[0].layer_collection.children[highlights.name].exclude = True
lit.view_layers[0].layer_collection.children[footprint.name].exclude = True
guide.frame_set(1)
lit.frame_set(1)
bpy.context.window.scene = lit
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.shading.type = "MATERIAL"
            space.shading.use_scene_lights = True
            space.shading.use_scene_world = True
            space.shading.use_scene_lights_render = True
            space.shading.use_scene_world_render = True
            space.region_3d.view_perspective = "CAMERA"
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))

checks = dict(light_source="Fixed warm sun and broad cool window fill",
              bar_lighting="Fixed broad venue fixtures; direct sunlight blocked by ceiling and side wall; shelf-glow light removed",
              walls_in_ghost=False,
              window_plane_x_m=window_x, target_table_centre=[9, 0, .785],
              sun_direction=list(sun.rotation_euler), animated_lights=False,
              real_window_frame_shadows=True, neutral_materials=True,
              contour_scene=guide.name, lighting_scene=lit.name,
              scene_purpose="Lighting example alongside the transparent guide; camera timing is shared",
              techniques=["Side lighting reveals form", "Soft contact shadows anchor objects",
                          "Warm direct light and cool ambient fill", "Rhythm in backbar bottles",
                          "Opposing table settings balance the high shot"],
              lighting_not_a_requirement_for_every_guide=True)
(OUT / "lighting-report.json").write_text(json.dumps(checks, indent=2) + "\n")
(OUT / "object-composition-plan.json").write_text(json.dumps(dict(
    guide="bar_low_truckr_mm", next_guide="table_seat_high_in_mc",
    decisions=["Fixed oblique bar angle gives converging counter/shelf lines",
               "Bar counter and seating are the subject; glassware is supporting context",
               "Near stool reveals the subject through real occlusion",
               "Bottle groups have deliberate gaps and one clearer distant landmark",
               "Two opposing settings remain functional; camera makes a depth diagonal",
               "Window-side placement motivates yellow rim cues and faint projected light boundaries"],
    audience_takeaway="Understand the bar seating and atmosphere, then see the best table to book",
    bar_subject="Bar counter and seats; room-tour context",
    glassware_role="Supporting context; not a menu-item review or product hero",
    roles={name: dict(alpha_before_export=data[0], final_alpha=data[0] * .5, reason=data[2]) for name, data in roles.items()},
    objects=object_plan, lighting_cues=[o.name for c in [highlights, footprint] for o in c.objects]
), indent=2) + "\n")
print("LIGHTING_SCENES_READY", flush=True)
