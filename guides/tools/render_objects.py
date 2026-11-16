"""Single-object line-art stills of the guide object library (OBJECTS.md section 1), in the P0 guide look.

Driver (any python3):
    python3 guides/tools/render_objects.py [scope] [--jobs 4] [--id NAME]
    scope: all (default) | approved | study | library | <object id> [<object id> ...] | <model path>
    A model path (a .blend/.glb file, or a folder holding asset.blend, model.blend or a .glb) renders a request
    candidate (section "candidate"); --id names it (default: candidate_<model name>).
    --prep '<json>' --out <folder>: a test run with other dot-cleanup values (SCAN_PREP); PNGs go to the folder only.
    Output: guides/review/objects_renders/<id>.png (three-quarter, 30 deg down), <id>_top.png for objects flat on a
    table, <id>_front.png for flat upright objects, and index.json (merged: a partial run replaces only its ids).
Blender (one object per process; the driver calls it):
    Blender -b --factory-startup --python-exit-code 1 -P guides/tools/render_objects.py -- --object <id> --result <json>

Each object is built by the guides' own builders (or loaded from its .blend into memory) and drawn with the guides'
line-art setup (`lineart_render.strokes_setup`, contour only, 3 px white over a 5 px black underlay at 55%, role
opacity and yellow light-edge cues as in `render_p0.py`) on the P0 player's dark stage colour. No model file is
written, saved or changed; library and study renders are test renders, not approvals.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "guides" / "review" / "objects_renders"
MODELS = ROOT / "model_refferences" / "objects"
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
SIZE = 1080
STAGE = (0x24, 0x35, 0x2d)  # the P0 player stage colour (p0_gallery.py .stage)
LENS_MM = 50.
ELEVATION, AZIMUTH = 30., 45.
TEST_NOTE = "Test render, not an approval: the owner approves a model only after reviewing it."
NOTE = ("Single-object line-art stills of OBJECTS.md section 1. Study, library and candidate renders are test renders, "
        "not approvals: the owner approves a model only after reviewing its render. Approved items are shown alone in "
        "the approved style; their status is the OBJECTS.md one.")
VARIANTS = ("tripo-generated/review", "tripo-generated/scene-ready", "functional")

# ---------------------------------------------------------------------------------------------------------------
# Registry: id -> section, OBJECTS.md row key, status, source. Pure data so the driver runs without Blender.


def _a(id, row, builder, status="approved", label=None, **kw):
    return dict(id=id, section="approved", row=row, builder=builder, status=status, label=label or id, **kw)


APPROVED = [
    _a("cup_heart", "cup()", "cup_heart", label="Ceramic cup, foam heart", source="assets.cup + p0_scenes.cup(art='heart')"),
    _a("cup_rosetta", "cup()", "cup_rosetta", label="Ceramic cup, rosetta", source="assets.cup + p0_scenes.cup(art='rosetta')"),
    _a("saucer", "`saucer`", "saucer", source="assets.saucer"),
    _a("plate", "`plate` (", "plate", label="Plate with formed rim (0.30 m)", source="assets.plate"),
    _a("platter", "`platter`", "platter", source="p0_table_compositions.platter"),
    _a("fork", "`fork`", "fork", source="assets.fork"),
    _a("knife", "knife", "knife", status="approved, background only", label="Dinner knife",
       source="p0_scenes.py handoff_plate_lands G.plate_outline('Dinner knife')"),
    _a("water_glass", "water glass", "water_glass", status="approved, support", source="geometry.glass"),
    _a("cocktail_glass", "cocktail glass", "cocktail_glass", source="p0_table_compositions.cocktail(primary=True)"),
    _a("pasta", "`pasta`", "pasta", status="approved; owner's example dish for all kinds", source="assets.pasta"),
    _a("pastry", "`pastry`", "pastry", status="approved, support", label="Two-half croissant", source="assets.pastry"),
    _a("bread", "bread loaf", "bread", source="p0_table_compositions.bread"),
    _a("pancakes", "pancake stack", "pancakes", source="p0_table_compositions.pancakes"),
    _a("pizza", "pizza", "pizza", status="approved in P0",
       source="model_refferences/objects/pizza/lineart/asset.blend (Z scale 0.55 as in table_spread_orbit)"),
    _a("salad_portion", "salad portion", "salad", status="approved in P0",
       source="model_refferences/objects/salad_portion/lineart/asset.blend"),
    _a("milk_pitcher", "milk pitcher", "milk_pitcher", status="approved in P0",
       source="model_refferences/objects/milk_pitcher/functional/asset.blend via p0_scenes.reused_pourer"),
    _a("kettle", "gooseneck kettle", "kettle", status="approved in P0",
       source="model_refferences/objects/kettle/tripo-generated/review/asset.blend via p0_scenes.reused_pourer"),
    _a("menu_card", "menu card", "menu_card", source="p0_scenes.plain_card"),
    _a("p0_menu_board", "menu board, three", "menu_board", label="Menu board, three columns", source="p0_scenes.board"),
    _a("counter", "counter (", "counter", label="Counter with cabinet and espresso block",
       source="p0_scenes.counter(body=True)"),
    _a("round_table", "round table", "round_table", source="assets.table"),
    _a("p0_dining_table", "two-person dining", "dining_table", label="Two-person dining table with settings",
       source="venue_assets.dining_table(settings=True)"),
    _a("long_tabletop", "long tabletop", "long_tabletop", source="p0_table_compositions.py pancake_clear_path block"),
    _a("p0_chair", "dining chair", "chair", status="approved, background", label="Dining chair", source="venue_assets.chair"),
    _a("p0_window", "window (frame", "window", label="Window frame", source="venue_assets.window"),
    _a("door", "glazed door", "door", label="Glazed door with hinge", source="venue_assets.door"),
    _a("entry_sign", "venue sign", "entry_sign", label="Venue sign, hanging bracket, downlight",
       source="p0_scenes.entry_sign(hanging=True)"),
    _a("welcome_stand", "A-frame", "welcome_stand", label="A-frame welcome stand, facade ground line",
       source="p0_scenes.facade_ground_and_welcome"),
    _a("p0_pendant", "pendant lamp", "pendant", label="Pendant lamp", source="venue_assets.pendant"),
    _a("p0_plant", "floor plant", "plant", label="Floor plant", source="venue_assets.plant"),
    _a("partition", "partition planes", "partition", label="Partition plane", source="p0_scenes.room partition block"),
    _a("bust", "schematic mouthless", "bust", status="approved only as a faint static barista",
       label="Schematic mouthless bust", source="assets.portrait(prop=None)"),
    _a("creator", "canonical creator", "creator", status="approved, local/API only, not public",
       label="Canonical creator, neutral seated pose", source="model_refferences/creator/lineart/asset.blend via p0_people.load_creator"),
    _a("hand_fork_pinch", "cropped anatomical hands", "hand_fork", status="approved only in the three owner-requested grips",
       label="CC0 pinch hand holding the fork (bite_pip_dish)", source="real_hands.place('pinch','L') as in bite_pip_dish"),
    _a("hand_glass_grip", "cropped anatomical hands", "hand_glass", status="approved only in the three owner-requested grips",
       label="CC0 hand, vertical side grip on the cocktail glass (glass_slide_close)",
       source="p0_table_compositions.glass_grip"),
    _a("hand_plate_rim", "cropped anatomical hands", "hand_plate", status="approved only in the three owner-requested grips",
       label="CC0 relaxed hand on the plate rim (pancake_clear_path)", source="real_hands.place('relaxed','L') as in pancake_clear_path"),
]
SKIPPED = [dict(id="effects", section="approved", row="milk stream", status="approved", label="Milk stream, steam strands, light-edge cues",
                source="p0_scenes.py (tubes, shape keys)",
                skipped="Guide effects shaped per scene, not standalone objects; see the guide posters.")]

STUDY = [
    dict(id="latte_cup_functional", row="latte_cup (functional, hollow)", path="latte_cup/functional/asset.blend",
         status="study only; status file functional_asset_pending_contact_validation", label="Latte cup (functional, hollow)"),
    dict(id="saucer_reconstructed", row="saucer", path="saucer/reconstructed/asset.blend",
         status="study only (reviewed_for_scene_proof)", label="Saucer (TripoSR)"),
    dict(id="croissant_approved_v2", row="croissant approved-v2", path="croissant/approved-v2/asset.blend",
         status="owner-approved shape; study only in line art", label="Croissant approved-v2"),
    dict(id="serving_tray", row="serving tray", path="serving_tray/tripo-generated/review/asset.blend",
         status="study only", label="Serving tray"),
    dict(id="cake_slice", row="cake slice", path="cake_slice/tripo-generated/review/asset.blend",
         status="study only", label="Cake slice"),
    dict(id="dinner_plate", row="dinner plate (0.26 m)", path="dinner_plate/tripo-generated/review/asset.blend",
         status="study only", label="Dinner plate (Tripo)"),
]
for e in STUDY:
    e["section"] = "study"

# Code-built candidates awaiting the owner's approval (2026-11-16): new builders used only by new guides. Each gets a
# third, low side view (`side_view`) besides the three-quarter and the top or front view.
SIDE = dict(side_view=True)
CODE_CANDIDATES = [
    dict(id="dessert_spoon", builder="dessert_spoon", label="Dessert spoon (0.175 m)", source="assets.spoon(length=.175)", **SIDE),
    dict(id="teaspoon", builder="teaspoon", label="Teaspoon (0.135 m)", source="assets.spoon(length=.135)", **SIDE),
    dict(id="dessert_knife", builder="dessert_knife", label="Dessert knife (0.20 m)", source="assets.knife(length=.20)", **SIDE),
    dict(id="paper_wrap_closed", builder="paper_wrap_closed", label="Paper wrap, closed", source="assets.paper_wrap()", **SIDE),
    dict(id="paper_wrap_open", builder="paper_wrap_open", label="Paper wrap, opened", source="assets.paper_wrap(opened=True)", **SIDE),
    dict(id="paper_tray", builder="paper_tray", label="Paper-lined tray (0.36 x 0.27 m)", source="assets.paper_tray()", **SIDE),
    dict(id="product_boxes", builder="product_boxes", label="Generic product boxes (6x4x2, 8x5x3, 4x4x4 in)", source="assets.product_box(w, d, h, flap=True)", **SIDE),
    dict(id="shopping_bag", builder="shopping_bag", label="Paper shopping bag (10x6x13 in)", source="assets.shopping_bag()", **SIDE),
]
for e in CODE_CANDIDATES:
    e.update(section="candidate", row="candidate", status="code-built candidate, awaiting owner approval")

LIB_MODELS = {
    "Drinkware": ["takeaway_cup", "drinking_glass", "stemmed_glass", "bottle", "latte_cup"],
    "Coffee equipment": ["espresso_machine", "coffee_grinder", "portafilter", "coffee_tamper", "knock_box"],
    "Food": ["burger", "brunch_toast", "croissant_oozing"],
    "Tableware": ["serving_bowl", "kitchen_tongs"],
    "Furniture": ["dining_table", "dining_chair", "bar_counter", "bar_stool"],
    "Bakery": ["display_case", "pastry_rack", "pastry_box", "bakery_oven"],
    "Venue": ["glazed_door", "window", "wall_shelf", "menu_board", "pendant", "beer_tap"],
    "Work": ["laptop"],
    "Other venue kinds": ["acoustic_guitar", "dumbbell", "hair_clipper", "salon_chair", "treatment_bed", "tshirt"],
}
LIB_STATUS = {"drinking_glass": "scene-ready variant: locally_corrected_scene_candidate",
              "espresso_machine": "functional variant pending contact validation",
              "dining_chair": "rendered_pending_visual_review", "bar_stool": "scene-ready variant exists",
              "glazed_door": "scene-ready: derived_asset_pending_scene_validation",
              "window": "scene-ready and full-height (native_full_height_window_ready) variants exist",
              "display_case": "glass-pane occlusion pass not solved", "kitchen_tongs": "the tong grip was rejected (1d)"}
# Per-model dot-cleanup overrides of SCAN_PREP (11 Nov review): the guitar's frets, string posts and tuner pins are
# short strokes and small separate parts that the defaults removed.
LIB_PREP = {"acoustic_guitar": dict(min_part=0, min_stroke_px=5)}
LEGACY = [
    ("legacy_burger", "food_assets.burger", "Procedural burger"),
    ("legacy_card", "food_assets.card", "Lettered paper card"),
    ("legacy_open_box", "food_assets.open_box", "Open food box with pastries"),
    ("legacy_held_tongs", "food_assets.held_tongs", "Held tongs with a hand"),
    ("legacy_tool_brush", "food_assets.tool('brush')", "Tool: brush"),
    ("legacy_tool_tamper", "food_assets.tool('tamper')", "Tool: tamper"),
    ("legacy_tool_clippers", "food_assets.tool('clippers')", "Tool: clippers"),
    ("legacy_tool_scissors", "food_assets.tool('scissors')", "Tool: scissors"),
    ("legacy_pastry_case", "venue_assets.pastry_case", "Pastry case (2.3 m, no glass)"),
    ("legacy_salon_chair", "venue_assets.chair(salon=True)", "Salon chair"),
    ("legacy_salon_station", "venue_assets.salon_station", "Salon station with mirror"),
    ("legacy_salon_tools", "venue_assets.salon_tools", "Salon tools"),
    ("legacy_garment", "venue_assets.garment", "Garment on a hanger"),
    ("legacy_rack_garment", "venue_assets.rack('garment')", "Garment rack"),
    ("legacy_rack_bottle", "venue_assets.rack('bottle')", "Bottle shelf"),
    ("legacy_bench", "venue_assets.bench", "Bench"),
    ("legacy_sauna_bench", "venue_assets.bench(sauna=True)", "Sauna bench"),
    ("legacy_treatment_bed", "venue_assets.treatment_bed", "Treatment bed"),
    ("legacy_facade", "venue_assets.facade", "Shopfront facade"),
    ("legacy_food_truck", "venue_assets.facade(truck=True)", "Food truck front"),
    ("legacy_dumbbell", "venue_assets.dumbbell", "Dumbbell"),
    ("legacy_grill", "food_scenes.py grill variant (lines 147-150)", "Tabletop grill block with meat"),
    ("legacy_guitar", "venue_assets.guitar (vendor/innerscene-guitar/guitar.glb)", "Acoustic guitar CC0"),
]
LEGACY_ROW = "Legacy procedural, older glass/colour pipelines"


# Owner-approved derived copies (2026-11-11) replace the picked variant; the sources stay untouched.
DERIVED = {"pastry_box": "pastry_box/filled-v1/asset.blend", "brunch_toast": "brunch_toast/yolk-highlight-v1/asset.blend",
           "treatment_bed": "treatment_bed/one-face-hole-v1/asset.blend"}


def pick_variant(name):
    if name in DERIVED and (MODELS / DERIVED[name]).exists():
        return DERIVED[name]
    for variant in VARIANTS:
        if (MODELS / name / variant / "asset.blend").exists():
            return f"{name}/{variant}/asset.blend"
    return None


def library():
    out = []
    for row, names in LIB_MODELS.items():
        for name in names:
            out.append(dict(id=name, section="library", row=row, path=pick_variant(name), label=name,
                            status=LIB_STATUS.get(name, "review_candidate"), prep=LIB_PREP.get(name)))
    out.append(dict(id="rack_shelf_tray", section="library", row="Supplemental local", label="rack_shelf_tray",
                    path="rack_shelf_tray/reconstructed/asset.blend", status="reviewed_for_scene_proof (TripoSR)"))
    out.append(dict(id="plant", section="library", row="Supplemental local", label="plant (model_built)",
                    path="plant/asset.blend", status="model_built"))
    for name in ["barista", "friend_locs"]:
        out.append(dict(id=name, section="library", row="Characters", label=name + " (65-bone rig, rest pose)",
                        path=f"../{name}/tripo-rigged/review/asset.blend", status="review_candidate; not used in P0"))
    for id, source, label in LEGACY:
        out.append(dict(id=id, section="library", row=LEGACY_ROW, builder=id, source=source, label=label,
                        status="unverified (older native colour pipeline)"))
    return out


def registry():
    return {e["id"]: e for e in APPROVED + STUDY + library() + CODE_CANDIDATES}


# ---------------------------------------------------------------------------------------------------------------
# Scan-surface cleanup for Tripo/TripoSR models (owner review 2026-11-11: "cleanup dots from surface"). Importable
# by a guide scene: `from render_objects import SCAN_PREP, clean_scan_mesh, drop_short_strokes`. The dots are
# contour fragments of 1-11 px from surface noise; the 12 px stroke filter removes them and keeps every real contour.
# Remesh, smooth and decimate stay off by default: on the 11 Nov test set they melted panel and rim lines (espresso
# machine, dinner plate) and broke rings into dashes (bar stool). A registry row may set them with `prep=dict(...)`.

SCAN_PREP = dict(voxel_fraction=0, smooth=0, iterations=0, decimate=1, min_part=.02, min_stroke_px=12)


def clean_scan_mesh(meshes, voxel=None, voxel_fraction=0, smooth=0, iterations=0, decimate=1, min_part=.02, **_):
    """Cleans a generated scan in memory: weld, normals, loose parts smaller than `min_part` of the model's diagonal
    removed; optionally voxel remesh (`voxel` in metres, else `voxel_fraction` of the largest side), Laplacian
    smooth and decimate. Changes only the given in-memory meshes; returns a dict of what it did.
    """
    import bmesh
    import bpy
    import numpy as np
    points = []
    for obj in meshes:
        co = np.empty(len(obj.data.vertices) * 3); obj.data.vertices.foreach_get("co", co)
        m = np.array(obj.matrix_world); points.append(co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3])
    points = np.concatenate(points)
    lo, hi = points.min(0), points.max(0); diag = float(np.linalg.norm(hi - lo))
    size = voxel or float(max(hi - lo)) * voxel_fraction
    report = dict(voxel_m=round(size, 5), faces_before=sum(len(o.data.polygons) for o in meshes), loose_parts_removed=0)
    deps = bpy.context.evaluated_depsgraph_get
    for obj in meshes:
        bm = bmesh.new(); bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=diag * 1e-6)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(obj.data); bm.free()
        if size > 0:
            mod = obj.modifiers.new("Scan cleanup / voxel remesh", "REMESH"); mod.mode = "VOXEL"; mod.voxel_size = size
            mod.use_smooth_shade = True
        bake = obj.evaluated_get(deps()); data = bpy.data.meshes.new_from_object(bake, depsgraph=deps())
        obj.modifiers.clear(); old = obj.data; obj.data = data; bpy.data.meshes.remove(old)
        if min_part:
            bm = bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table()
            seen, drop = set(), []
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
                co = np.array([v.co[:] for v in part])
                if np.linalg.norm(co.max(0) - co.min(0)) < min_part * diag:
                    drop += part
            if drop:
                report["loose_parts_removed"] += 1
                bmesh.ops.delete(bm, geom=drop, context="VERTS"); bm.to_mesh(obj.data)
            bm.free()
        if smooth and iterations:
            mod = obj.modifiers.new("Scan cleanup / smooth", "SMOOTH"); mod.factor = smooth; mod.iterations = iterations
        if decimate and decimate < 1:
            mod = obj.modifiers.new("Scan cleanup / decimate", "DECIMATE"); mod.ratio = decimate
        if obj.modifiers:
            bake = obj.evaluated_get(deps()); data = bpy.data.meshes.new_from_object(bake, depsgraph=deps())
            obj.modifiers.clear(); old = obj.data; obj.data = data; bpy.data.meshes.remove(old)
        obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    report["faces_after"] = sum(len(o.data.polygons) for o in meshes)
    return report


def drop_short_strokes(gp_obj, camera, fov_y, width, height, min_px=12):
    """Removes baked line-art strokes shorter than `min_px` screen pixels (the 4 Nov study's speckle filter);
    returns the number removed."""
    import numpy as np
    tan_y = math.tan(fov_y / 2); tan_x = tan_y * width / height
    transform = np.asarray(camera.matrix_world.inverted() @ gp_obj.matrix_world, dtype=np.float64)
    removed = 0
    for layer in gp_obj.data.layers:
        for frame in layer.frames:
            drawing = frame.drawing; attr = drawing.attributes.get("position")
            if attr is None:
                continue
            points = np.empty((len(attr.data), 3), dtype=np.float32); attr.data.foreach_get("vector", points.ravel())
            xyz = points @ transform[:3, :3].T + transform[:3, 3]; depth = np.maximum(-xyz[:, 2], 1e-7)
            px = np.column_stack((xyz[:, 0] / depth * width / (2 * tan_x), xyz[:, 1] / depth * height / (2 * tan_y)))
            drop, start = [], 0
            for index, stroke in enumerate(drawing.strokes):
                end = start + len(stroke.points)
                if float(np.linalg.norm(np.diff(px[start:end], axis=0), axis=1).sum()) < min_px:
                    drop.append(index)
                start = end
            if drop:
                drawing.remove_strokes(indices=drop); removed += len(drop)
    gp_obj.data.update_tag()
    return removed


# ---------------------------------------------------------------------------------------------------------------
# Blender side


def blender_side(argv):
    import bpy
    import bmesh
    import numpy as np
    from mathutils import Matrix, Vector
    for path in [ROOT / "guides/blender_motion", HERE, ROOT / "model_refferences/objects/tools"]:
        sys.path.insert(0, str(path))
    import assets as A
    import geometry as G
    import venue_assets as V
    import p0_scenes as P
    import p0_table_compositions as TC
    import real_hands as H
    import lineart_render as L
    L.WIDTH = L.HEIGHT = SIZE

    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--path", help="candidate model path (section candidate)")
    parser.add_argument("--label")
    parser.add_argument("--prep", help="JSON overrides of the scan cleanup for this run (test renders)")
    parser.add_argument("--out", type=Path, help="write the PNGs here instead of guides/review/objects_renders")
    args = parser.parse_args(argv)
    out_dir = args.out or OUT
    if args.path:
        spec = dict(id=args.object, section="candidate", path=str(Path(args.path).resolve()), label=args.label or args.object,
                    status="candidate for an OBJECTS.md request")
    else:
        spec = registry()[args.object]
    notes, result = [], dict(spec)
    prep = None if spec.get("prep") is False else dict(SCAN_PREP, **(spec.get("prep") or {}), **json.loads(args.prep or "{}"))
    started = time.time()

    def context(root_or_objs):
        objs = root_or_objs if isinstance(root_or_objs, (list, tuple, set)) else P.members(root_or_objs)
        for obj in objs:
            if obj.type == "MESH":
                obj["render_objects_context"] = True

    def remove(root):
        for obj in list(root.children_recursive) + [root]:
            bpy.data.objects.remove(obj, do_unlink=True)

    def load_meshes(path, name):
        """In-memory copies of every mesh in a .blend, world transforms applied; the file is only read."""
        before = set(bpy.data.objects)
        with bpy.data.libraries.load(str(path), link=False) as (src, dst):
            dst.objects = src.objects
        meshes = [o for o in dst.objects if o and o.type == "MESH"]
        for obj in meshes:
            bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.update()
        for obj in meshes:
            world = obj.matrix_world.copy(); obj.data.transform(world); obj.parent = None; obj.matrix_world = Matrix.Identity(4)
            obj.data.materials.clear()
            for face in obj.data.polygons:
                face.use_smooth = True
            A.tag(obj, "hero", name)
        for obj in dst.objects:
            if obj and obj.type != "MESH":
                bpy.data.objects.remove(obj, do_unlink=True)
        bottom = min(v.co.z for o in meshes for v in o.data.vertices)
        for obj in meshes:
            for vertex in obj.data.vertices:
                vertex.co.z -= bottom
        return A.group(name, before, (0, 0, 0), "hero", name)

    def seat(arm):
        """Neutral seated pose: thighs forward, shins down, from the rig's rest pose."""
        def turn(bone, degrees):
            pb = arm.pose.bones[bone]
            head = arm.matrix_world @ pb.head
            world = Matrix.Translation(head) @ Matrix.Rotation(math.radians(degrees), 4, "X") @ Matrix.Translation(-head)
            pb.matrix = arm.matrix_world.inverted() @ world @ arm.matrix_world @ pb.matrix
            bpy.context.view_layer.update()
        for side in ["Left", "Right"]:
            turn(f"mixamorig:{side}UpLeg", -88)
        for side in ["Left", "Right"]:
            turn(f"mixamorig:{side}Leg", 88)

    def build(builder):
        b = builder
        if b == "cup_heart" or b == "cup_rosetta":
            root, saucer = P.cup(0, 0, 0, True, "heart" if b == "cup_heart" else "rosetta")
            bpy.data.objects.remove(saucer, do_unlink=True)
        elif b == "saucer": A.saucer((0, 0, 0))
        elif b == "plate": A.plate((0, 0, 0))
        elif b == "platter": TC.platter((0, 0, 0), .175)
        elif b == "fork": A.fork((0, 0, 0))
        elif b == "knife":
            A.knife((0, 0, 0))
        elif b == "dessert_spoon": A.spoon((0, 0, 0), role="hero")
        elif b == "teaspoon": A.spoon((0, 0, 0), "Teaspoon", "hero", length=.135)
        elif b == "dessert_knife": A.knife((0, 0, 0), "Dessert knife", "hero", length=.20)
        elif b == "paper_wrap_closed": A.paper_wrap((0, 0, 0))
        elif b == "paper_wrap_open": A.paper_wrap((0, 0, 0), opened=True)
        elif b == "paper_tray": A.paper_tray((0, 0, 0), role="hero")
        elif b == "product_boxes":
            A.product_box((-.17, 0, 0), .152, .102, .051, name="Product box small")
            A.product_box((0, 0, 0), .203, .127, .076, name="Product box medium")
            A.product_box((.17, 0, 0), .102, .102, .102, name="Product box cube")
        elif b == "shopping_bag": A.shopping_bag((0, 0, 0))
        elif b == "water_glass": A.tag(G.glass("Water glass", 0, 0, 0), "support", "Water glass")
        elif b == "cocktail_glass": TC.cocktail((0, 0, 0), 0, "support", primary=True)
        elif b == "pasta": A.pasta((0, 0, 0))
        elif b == "pastry": A.pastry((0, 0, 0))
        elif b == "bread": TC.bread((0, 0, 0))
        elif b == "pancakes": TC.pancakes((0, 0, 0))
        elif b in ("pizza", "salad"):
            name = "pizza" if b == "pizza" else "salad_portion"
            cache = MODELS / name / "lineart"
            import hashlib
            source = MODELS / name / "tripo-generated/review/asset.blend"
            meta = json.loads((cache / "metadata.json").read_text())
            if meta.get("source_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
                raise RuntimeError("line-art cache is stale for " + name + "; the guide would rebuild it, this renderer never writes it")
            root = load_meshes(cache / "asset.blend", "Reusable " + name)
            if b == "pizza":
                root.scale.z = .55
            notes.append("Loaded the guides' cleaned line-art cache (" + str((cache / "asset.blend").relative_to(ROOT)) + ").")
        elif b in ("milk_pitcher", "kettle"):
            P.reused_pourer(b == "milk_pitcher", (0, 0, .3))
            notes.append("Remesh, smooth and decimate applied in memory exactly as the pour guides do.")
        elif b == "menu_card": P.plain_card((0, 0, 0))
        elif b == "menu_board": P.board()
        elif b == "counter": P.counter(body=True)
        elif b == "round_table": A.table((0, 0, 0), .60)
        elif b == "dining_table": V.dining_table((0, 0, 0), settings=True)
        elif b == "long_tabletop":
            A.tag(G.block("Long commercial dining tabletop", (0, .55, .752), (1.4, 2.65, .066), .025), "structure", "Long table")
        elif b == "chair": V.chair((0, 0, 0))
        elif b == "window": V.window((0, 0, 0))
        elif b == "door": V.door((0, 0, 0))
        elif b == "entry_sign": P.entry_sign(hanging=True)
        elif b == "welcome_stand":
            P.facade_ground_and_welcome()
            for obj in [o for o in bpy.data.objects if o.name.startswith("Facade ground junction")]:
                bpy.data.objects.remove(obj, do_unlink=True)
            notes.append("The helper's two facade ground-junction lines are left out so the stand fills the frame.")
        elif b == "pendant": V.pendant((0, 0, 2.65))
        elif b == "plant": V.plant((0, 0, 0), height=1.12)
        elif b == "partition":
            A.tag(G.block("Faint partition plane", (0, 0, .48), (.045, 1.25, .96), .015), "background", "Partition")
        elif b == "bust": A.portrait((0, 0, 0), prop=None)
        elif b == "creator":
            import p0_people
            root, arm, masks = p0_people.load_creator(P)
            for mask in masks:
                bpy.data.objects.remove(mask, do_unlink=True)
            seat(arm)
            notes.append("Rest pose with the thighs turned forward and the shins down (no chair, no prop); "
                         "the guides' below-chest character fade is not applied so the whole rig shows.")
        elif b == "hand_fork":
            fork = A.fork((.055, -.015, .846), role="hero"); fork.rotation_euler = (math.radians(10), 0, math.pi / 2)
            bpy.context.view_layer.update(); grip = fork.matrix_world @ Vector((0, -.09, .005))
            wrist = H.place("pinch", "L", target=grip, forward=(-1, 0, 0), normal=(0, 0, -1), anchor="grip")
            P.role(wrist, "hand"); wrist["p0_hand"] = True; wrist["p0_cropped_grip"] = True
            context(fork)
            notes.append("The fork is drawn at support opacity as the grip's context; the forearm fades from the grip as in the guide.")
        elif b == "hand_glass":
            drink = TC.cocktail((-.08, -.05, .785), 0, "support", primary=True); hand = TC.glass_grip(drink)
            context(drink["root"])
            notes.append("The cocktail glass is drawn at support opacity as the grip's context.")
        elif b == "hand_plate":
            plate = A.plate((.14, .10, .785))
            left = H.place("relaxed", "L", target=(-.006, .10, .817), forward=(1, 0, 0), normal=(0, 0, 1), anchor="f_middle.03")
            left["p0_hand"] = True; left["p0_cropped_grip"] = True
            bpy.context.view_layer.update()
            mesh = next(o for o in left.children_recursive if o.type == "MESH")
            inverse = mesh.matrix_world.inverted()
            for vertex in mesh.data.vertices:
                p = mesh.matrix_world @ vertex.co
                if p.z < .789:
                    p.z = .789; vertex.co = inverse @ p
            for obj in left.children_recursive:
                if obj.type == "MESH":
                    A.tag(obj, "hand", "Left-side grip holds the left plate rim")
            context([plate])
            notes.append("The plate is drawn at support opacity as the grip's context (the guide's salad is left out).")
        elif b.startswith("legacy_"):
            import food_assets as F
            k = b[len("legacy_"):]
            if k == "burger": F.burger((0, 0, 0))
            elif k == "card": F.card((0, 0, 0))
            elif k == "open_box": F.open_box((0, 0, 0))
            elif k == "held_tongs":
                food = A.ellipsoid("Meat portion", (0, 0, .02), (.10, .065, .02), "hero", "Food")
                F.held_tongs(food)
                notes.append("held_tongs needs a food object; a 0.20 m ellipsoid portion (as in the grill variant) stands in.")
            elif k.startswith("tool_"): F.tool(k[5:], (0, 0, 0))
            elif k == "pastry_case": V.pastry_case((0, 0, 0))
            elif k == "salon_chair": V.chair((0, 0, 0), salon=True)
            elif k == "salon_station": V.salon_station((0, 0, 0), 0)
            elif k == "salon_tools": V.salon_tools((0, 0, 0))
            elif k == "garment": V.garment((0, 0, 0))
            elif k == "rack_garment": V.rack("garment", (0, 0, 0))
            elif k == "rack_bottle": V.rack("bottle", (0, 0, 0))
            elif k == "bench": V.bench((0, 0, 0))
            elif k == "sauna_bench": V.bench((0, 0, 0), sauna=True)
            elif k == "treatment_bed": V.treatment_bed((0, 0, 0))
            elif k == "facade": V.facade()
            elif k == "food_truck": V.facade(truck=True)
            elif k == "dumbbell": V.dumbbell((0, 0, 0))
            elif k == "grill":
                V.tag(G.block("Tabletop grill", (0, 0, .82), (.38, .29, .07), .025), "support", "Grill")
                for x in [i * .035 for i in range(-4, 5)]:
                    V.tag(G.tube("Grill bar", [(x, -.13, .86), (x, .13, .86)], .003), "background", "Grill bar")
                A.ellipsoid("Meat portion", (0, 0, .883), (.10, .065, .02), "hero", "Meat")
                notes.append("Grill block, bars and meat copied from food_scenes.py lines 147-150 (inline scene code); steam left out.")
            elif k == "guitar":
                V.guitar((0, 0, 0))
                if not (ROOT / "guides/blender_motion/vendor/innerscene-guitar/guitar.glb").exists():
                    notes.append("vendor guitar.glb missing; the procedural fallback guitar was drawn.")
            else:
                raise KeyError(b)
        else:
            raise KeyError(b)

    def import_model(path):
        scene = bpy.context.scene
        if path.suffix.lower() == ".blend":
            with bpy.data.libraries.load(str(path), link=False) as (src, dst):
                dst.objects = src.objects
            for obj in dst.objects:
                if obj is not None:
                    scene.collection.objects.link(obj)
        elif path.suffix.lower() in (".glb", ".gltf"):
            bpy.ops.import_scene.gltf(filepath=str(path))
        else:
            raise ValueError("unsupported model format " + path.suffix)
        bpy.context.view_layer.update()
        originals = list(bpy.data.objects)
        helpers = sorted(o.name for o in originals if o.type == "MESH" and o.hide_render)
        if helpers:
            notes.append("Left out meshes hidden from render in the source file: " + ", ".join(helpers))
        deps = bpy.context.evaluated_depsgraph_get(); meshes = []
        for obj in originals:
            if obj.type != "MESH" or obj.hide_render or not len(obj.data.vertices):
                continue
            ev = obj.evaluated_get(deps); data = bpy.data.meshes.new_from_object(ev, depsgraph=deps)
            data.transform(ev.matrix_world); data.materials.clear()
            copy = bpy.data.objects.new("Source / " + obj.name, data); meshes.append(copy)
            if obj.get("composition_role"):
                copy["composition_role"] = obj["composition_role"]
        for obj in originals:
            bpy.data.objects.remove(obj, do_unlink=True)
        if not meshes:
            raise ValueError("no renderable mesh in " + str(path))
        for obj in meshes:
            scene.collection.objects.link(obj)
        bpy.context.view_layer.update()
        names = sorted(o.name.replace("Source / ", "") for o in meshes)
        source_faces = sum(len(o.data.polygons) for o in meshes)
        if prep:
            cleanup = clean_scan_mesh(meshes, **prep); result["scan_cleanup"] = dict(prep, **cleanup)
            steps = [f"voxel remesh {cleanup['voxel_m'] * 1000:.2f} mm" if cleanup["voxel_m"] else "",
                     f"smooth {prep['smooth']} x {prep['iterations']}" if prep["smooth"] and prep["iterations"] else "",
                     f"decimate {prep['decimate']}" if prep["decimate"] < 1 else ""]
            notes.append(f"Dot cleanup in memory (clean_scan_mesh, drop_short_strokes): weld, "
                         f"{cleanup['loose_parts_removed']} meshes lost loose parts under {prep['min_part']:.0%} of the diagonal, "
                         + "".join(x + ", " for x in steps if x) + f"line-art strokes under {prep['min_stroke_px']} px dropped; "
                         f"{cleanup['faces_before']} -> {cleanup['faces_after']} faces.")
        for obj in meshes:
            if not obj.get("composition_role"):
                A.tag(obj, "hero", "Library model")
        notes.append(f"Imported {len(meshes)} mesh objects ({source_faces} source faces): " + ", ".join(names[:12])
                     + (" ..." if len(names) > 12 else ""))
        notes.append("Prepared in memory as the 4 Nov line-art study does (lineart_render.prepare_meshes: weld, "
                     "recalculated normals, small bevel, weighted normals); the file is not changed.")
        result["source_faces"] = source_faces

    # Scene, as render_p0 sets it up, at 1080 x 1080 on the dark stage colour.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = SIZE; scene.render.resolution_percentage = 100
    scene.render.film_transparent = False; scene.render.use_compositing = False; scene.render.use_sequencer = False
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.eevee.taa_render_samples = 16
    scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "None"
    world = bpy.data.worlds.new("Dark stage"); world.use_nodes = True
    srgb = [c / 255 for c in STAGE]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
    world.node_tree.nodes["Background"].inputs[0].default_value = (*linear, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1
    scene.world = world

    try:
        if spec.get("builder"):
            build(spec["builder"])
        else:
            if not spec.get("path"):
                raise FileNotFoundError("no asset.blend in " + ", ".join(VARIANTS))
            path = (MODELS / spec["path"]).resolve() if not Path(spec["path"]).is_absolute() else Path(spec["path"])
            if not path.exists():
                raise FileNotFoundError(str(path))
            import_model(path)
        P.lighting_cues(scene, dict(hero=[]))
        bpy.context.view_layer.update()

        meshes = [o for o in scene.objects if o.type == "MESH" and not o.get("p0_framing_mask")]
        groups = {}
        for obj in meshes:
            role = obj.get("composition_role", "support")
            name = ("lighting_cue" if role == "lighting_cue" else "drink_contents" if role == "drink_contents"
                    else "context" if obj.get("render_objects_context") else "hand" if role == "hand"
                    else "character" if role == "character" else "subject")
            groups.setdefault(name, []).append(obj)
        alpha = dict(subject=1., hand=1., character=1., context=P.ROLE_ALPHA["support"],
                     drink_contents=P.ROLE_ALPHA["drink_contents"], lighting_cue=P.ROLE_ALPHA["lighting_cue"])
        collections = {}
        for name, objs in groups.items():
            col = bpy.data.collections.new("Objects / " + name); scene.collection.children.link(col); collections[name] = col
            for obj in objs:
                for previous in list(obj.users_collection):
                    previous.objects.unlink(obj)
                col.objects.link(obj); obj.data.materials.clear()
        bpy.context.view_layer.update()
        subject = [o for n in ("subject", "hand", "character") for o in groups.get(n, [])]
        if not subject:
            raise RuntimeError("no subject meshes")

        deps = bpy.context.evaluated_depsgraph_get()
        clouds, sized, faces = [], [], 0
        framed = subject + [o for n in ("context", "drink_contents", "lighting_cue") for o in groups.get(n, [])]
        for obj in framed:
            ev = obj.evaluated_get(deps); mesh = ev.to_mesh()
            co = np.empty(len(mesh.vertices) * 3, dtype=np.float64); mesh.vertices.foreach_get("co", co)
            co = co.reshape(-1, 3); m = np.array(ev.matrix_world)
            world_co = co @ m[:3, :3].T + m[:3, 3]
            if obj in subject:
                faces += len(mesh.polygons)
                sized.append(world_co)
                clouds.append(("s", world_co))
                if obj.get("composition_role") == "hand":
                    # Frame the drawn grip, not the forearm that fades out beyond 0.16 m.
                    hand = obj.parent
                    while not hand.get("p0_hand"):
                        hand = hand.parent
                    marks = json.loads(obj["landmarks"])
                    grip = np.array(hand.matrix_world @ ((Vector(marks["f_index.03"]) + Vector(marks["thumb.03"])) / 2
                                    if hand.get("contact_landmark", "grip") == "grip" else Vector(marks[hand["contact_landmark"]])))
                    world_co = world_co[np.linalg.norm(world_co - grip, axis=1) < .14]
                    clouds[-1] = ("f", world_co)
            else:
                clouds.append(("c", world_co))
            ev.to_mesh_clear()
        sub = np.concatenate(sized)
        allp = np.concatenate([c for _, c in clouds])
        lo, hi = sub.min(0), sub.max(0); dims = hi - lo
        result["dimensions_m"] = [round(float(v), 4) for v in dims]
        result["faces"] = int(faces)
        if len(allp) > 200000:
            allp = allp[np.random.default_rng(1).choice(len(allp), 200000, replace=False)]

        camera = bpy.data.objects.new("Object camera", bpy.data.cameras.new("Object lens"))
        scene.collection.objects.link(camera); scene.camera = camera
        camera.data.lens = spec.get("lens", LENS_MM); camera.data.sensor_fit = "VERTICAL"
        camera.data.sensor_width = camera.data.sensor_height = 36
        fov = 2 * math.atan(18 / camera.data.lens); tangent = math.tan(fov / 2)

        def aim(position, target, up):
            direction = (target - position).normalized()
            right = direction.cross(Vector(up)).normalized()
            screen_up = right.cross(direction).normalized()
            camera.location = position; camera.rotation_mode = "QUATERNION"
            camera.rotation_quaternion = Matrix((right, screen_up, -direction)).transposed().to_quaternion()
            bpy.context.view_layer.update()

        def project(points):
            inv = np.array(camera.matrix_world.inverted())
            c = points @ inv[:3, :3].T + inv[:3, 3]
            depth = -c[:, 2]
            x = c[:, 0] / depth / tangent * .5 + .5 - camera.data.shift_x
            y = c[:, 1] / depth / tangent * .5 + .5 - camera.data.shift_y
            return x, y, depth

        def frame(direction, up, fill):
            centre = Vector(((allp.min(0) + allp.max(0)) / 2).tolist())
            camera.data.shift_x = camera.data.shift_y = 0
            size = float(np.linalg.norm(allp.max(0) - allp.min(0)))
            near, far = size * .2, size * 40
            for _ in range(60):
                d = (near + far) / 2; aim(centre + direction * d, centre, up)
                x, y, depth = project(allp)
                span = max(x.max() - x.min(), y.max() - y.min()) if depth.min() > 0 else 9
                if span > fill: near = d
                else: far = d
            d = far; aim(centre + direction * d, centre, up)
            for _ in range(4):
                x, y, _ = project(allp)
                camera.data.shift_x += (x.min() + x.max()) / 2 - .5
                camera.data.shift_y += (y.min() + y.max()) / 2 - .5
            x, y, depth = project(allp)
            camera.data.clip_start = max(.0005, float(depth.min()) * .2); camera.data.clip_end = float(depth.max()) * 5 + 10
            return d, dict(x_min=float(x.min()), x_max=float(x.max()), y_min=float(y.min()), y_max=float(y.max()))

        views = []
        az, el = math.radians(spec.get("azimuth", AZIMUTH)), math.radians(spec.get("elevation", ELEVATION))
        views.append(("", Vector((-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))), (0, 0, 1)))
        order = sorted(range(3), key=lambda i: dims[i])
        thin, middle = order[0], order[1]
        flat = spec.get("flat", bool(dims[thin] < .2 * dims[middle]))
        if flat and thin == 2:
            views.append(("_top", Vector((0, 0, 1)), (0, 1, 0)))
        elif flat:
            views.append(("_front", Vector((0, -1, 0)) if thin == 1 else Vector((-1, 0, 0)), (0, 0, 1)))
        result["flat"] = flat
        if spec.get("side_view"):
            if not flat:
                views.append(("_top", Vector((0, 0, 1)), (0, 1, 0)))
            side_az, side_el = az + math.radians(90), math.radians(8)
            views.append(("_side", Vector((-math.sin(side_az) * math.cos(side_el), -math.cos(side_az) * math.cos(side_el),
                                           math.sin(side_el))), (0, 0, 1)))

        def fade_hands(obj):
            hands = [o for o in scene.objects if o.get("p0_hand")]
            if not hands:
                return
            for layer in obj.data.layers:
                for drawing_frame in layer.frames:
                    drawing = drawing_frame.drawing; position = drawing.attributes.get("position")
                    if position is None:
                        continue
                    points = np.empty((len(position.data), 3), dtype=np.float32); position.data.foreach_get("vector", points.ravel())
                    fades = []
                    for hand in hands:
                        mesh = next(o for o in hand.children_recursive if o.type == "MESH")
                        marks = json.loads(mesh["landmarks"]); anchor = hand.get("contact_landmark", "grip")
                        local = Vector(marks[anchor]) if anchor in marks else (Vector(marks["f_index.03"]) + Vector(marks["thumb.03"])) / 2
                        g = np.array(hand.matrix_world @ local); inner, outer = (.08, .16) if hand.get("p0_cropped_grip") else (.18, .48)
                        u = np.clip((np.linalg.norm(points - g, axis=1) - inner) / (outer - inner), 0, 1); fades.append(1 - u * u * (3 - 2 * u))
                    opacity = drawing.attributes.get("opacity")
                    values = np.ones(len(points), dtype=np.float32)
                    if opacity: opacity.data.foreach_get("value", values)
                    else: opacity = drawing.attributes.new("opacity", "FLOAT", "POINT")
                    opacity.data.foreach_set("value", (values * np.max(np.stack(fades), axis=0)).astype(np.float32))

        files, strokes, frames_info = [], {}, {}
        out_dir.mkdir(parents=True, exist_ok=True)
        for suffix, direction, up in views:
            distance, bounds = frame(direction.normalized(), up, spec.get("fill", .80))
            for obj in meshes:
                obj.hide_render = False
            gp = []
            counts_view = {}
            for name, col in collections.items():
                rargs = argparse.Namespace(hidden=False, contour_only=True, skip_intersections=name == "character")
                shells = [(o, o.lineart.usage) for o in meshes if o.get("clear_vessel_shell")] if name in ("drink_contents", "hand", "lighting_cue") else []
                for shell, _ in shells:
                    shell.lineart.usage = "EXCLUDE"
                before = set(bpy.data.objects)
                try:
                    obj, counts = L.strokes_setup(scene, col, rargs, max(.15, distance), fov, 1)
                except RuntimeError as error:
                    if name in ("subject", "hand", "character") or "no visible contours" not in str(error):
                        raise
                    for extra in set(bpy.data.objects) - before:
                        bpy.data.objects.remove(extra, do_unlink=True)
                    counts_view[name] = "occluded"; continue
                finally:
                    for shell, usage in shells:
                        shell.lineart.usage = usage
                if prep and prep.get("min_stroke_px") and result.get("scan_cleanup"):
                    dropped = drop_short_strokes(obj, camera, fov, SIZE, SIZE, prep["min_stroke_px"])
                    result["scan_cleanup"].setdefault("short_strokes_removed", {})[suffix or "three_quarter"] = dropped
                for layer in obj.data.layers:
                    layer.opacity = alpha[name]
                if name == "hand":
                    fade_hands(obj)
                if name == "lighting_cue":
                    obj.data.materials[1].grease_pencil.color = (1., .73, .17, 1.)
                gp.append(obj); counts_view[name] = counts
            for obj in meshes:
                obj.hide_render = True
            target = out_dir / f"{spec['id']}{suffix}.png"
            scene.frame_set(1); scene.render.filepath = str(target); bpy.ops.render.render(write_still=True)
            image = bpy.data.images.load(str(target), check_existing=False)
            px = np.empty(len(image.pixels), dtype=np.float32); image.pixels.foreach_get(px)
            rgb = px.reshape(-1, 4)[:, :3]; bpy.data.images.remove(image)
            ink = float((np.abs(rgb - np.array(srgb)).max(1) > .06).mean())
            files.append(target.name); strokes[suffix or "three_quarter"] = counts_view
            frames_info[suffix or "three_quarter"] = dict(bounds=bounds, ink_fraction=round(ink, 5),
                                                         camera_distance_m=round(distance, 4))
            if ink < .002:
                notes.append(f"{target.name}: almost no line pixels ({ink:.4f}).")
            for obj in gp:
                bpy.data.objects.remove(obj, do_unlink=True)
        result.update(status_render="rendered", files=files, strokes=strokes, views=frames_info, error=None)
    except Exception as error:
        import traceback
        traceback.print_exc()
        result.update(status_render="failed", files=[], error=f"{type(error).__name__}: {error}")
    result["notes"] = notes
    result["seconds"] = round(time.time() - started, 1)
    result["blender_version"] = bpy.app.version_string
    args.result.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("RENDER_OBJECTS", spec["id"], result["status_render"], result.get("error") or "", flush=True)


# ---------------------------------------------------------------------------------------------------------------
# Driver


def run_one(spec, scratch, extra=()):
    result = scratch / f"{spec['id']}.json"
    if result.exists():
        result.unlink()
    command = [BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(Path(__file__).resolve()), "--",
               "--object", spec["id"], "--result", str(result), *extra]
    log = scratch / f"{spec['id']}.log"
    try:
        with log.open("w") as handle:
            subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, timeout=spec.get("timeout", 1200), cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        pass
    if result.exists():
        return json.loads(result.read_text())
    tail = log.read_text().strip().splitlines()[-5:] if log.exists() else []
    return dict(spec, status_render="failed", files=[], error="Blender exited without a result: " + " | ".join(tail))


def entry(raw):
    keep = ["id", "label", "section", "row", "status", "dimensions_m", "faces", "source_faces", "flat", "files", "notes", "error",
            "views", "seconds", "scan_cleanup", "before_files"]
    out = {k: raw.get(k) for k in keep if k in raw}
    path = raw.get("path")
    if path and not path.startswith("/"):
        path = os.path.relpath((MODELS / path).resolve(), ROOT)
    out["source"] = raw.get("source") or path
    if raw.get("builder") and not raw.get("source"):
        out["source"] = raw["builder"]
    out["render_status"] = raw.get("status_render", "skipped" if raw.get("skipped") else "failed")
    if raw.get("skipped"):
        out["notes"] = [raw["skipped"]]
    out["approval"] = ("Approved in P0 (render shows the approved object alone)" if raw["section"] == "approved"
                       else TEST_NOTE)
    out["rendered_at"] = time.strftime("%Y-%m-%d %H:%M")
    return out


def driver(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scope", nargs="*", default=["all"])
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--id", help="id for a candidate model path")
    parser.add_argument("--prep", help="JSON overrides of the scan cleanup (test runs; use with --out)")
    parser.add_argument("--out", type=Path, help="test output folder: PNGs and results only, index.json untouched")
    args = parser.parse_args(argv)
    reg = registry()
    specs, extra = [], {}
    for item in args.scope:
        if item == "all":
            specs += list(reg.values())
        elif item in ("approved", "study", "library"):
            specs += [e for e in reg.values() if e["section"] == item]
        elif item in reg:
            specs.append(reg[item])
        elif Path(item).expanduser().exists():
            path = Path(item).expanduser().resolve()
            if path.is_dir():
                found = [path / n for n in ("asset.blend", "model.blend") if (path / n).exists()] or sorted(path.rglob("*.glb"))
                if not found:
                    parser.error("no asset.blend, model.blend or .glb in " + str(path))
                path = found[0]
            parts = path.relative_to(MODELS).parts if path.is_relative_to(MODELS) else ()
            name = args.id or "candidate_" + (parts[0] if parts else path.parent.name if path.stem in ("asset", "model") else path.stem)
            specs.append(dict(id=name, section="candidate", path=str(path), label=name, row="candidate",
                              status="candidate for an OBJECTS.md request"))
            extra[name] = ["--path", str(path), "--label", name]
        else:
            parser.error("unknown scope: " + item)
    seen = set(); specs = [s for s in specs if not (s["id"] in seen or seen.add(s["id"]))]
    scratch = Path(os.environ.get("RENDER_OBJECTS_SCRATCH", "/private/tmp/render_objects")); scratch.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        test = [*(["--prep", args.prep] if args.prep else []), *(["--out", str(args.out.resolve())] if args.out else [])]
        futures = {s["id"]: pool.submit(run_one, s, scratch, [*extra.get(s["id"], ()), *test]) for s in specs}
        results = {}
        for id, future in futures.items():
            results[id] = future.result()
            r = results[id]
            print(f"{id:28s} {r.get('status_render')} {r.get('seconds', '')}s {r.get('error') or ''}", flush=True)
    if args.out:
        print(json.dumps(dict(seconds=round(time.time() - started), out=str(args.out))))
        return
    index_path = OUT / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    objects = {o["id"]: o for o in index.get("objects", [])}
    full = args.scope == ["all"]
    if full:
        for s in SKIPPED:
            objects[s["id"]] = entry(s)
    for id, raw in results.items():
        objects[id] = entry(raw)
    order = {id: n for n, id in enumerate([s["id"] for s in APPROVED[:0]] + [e["id"] for e in SKIPPED] + list(reg))}
    index = dict(
        note=NOTE,
        renderer="guides/tools/render_objects.py", style=dict(size=[SIZE, SIZE], lens_mm=LENS_MM, elevation_deg=ELEVATION,
             azimuth_deg=AZIMUTH, background=("#%02x%02x%02x" % STAGE), lines="lineart_render.strokes_setup contour only: white 3 px over black 5 px at 55%",
             roles="subject 1.0, grip context 0.60, drink contents 0.72, yellow light-edge cues 0.55 (p0_scenes.ROLE_ALPHA)"),
        updated=time.strftime("%Y-%m-%d %H:%M"),
        objects=sorted(objects.values(), key=lambda o: (["approved", "study", "library", "candidate"].index(o["section"]), order.get(o["id"], 9999), o["id"])))
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    counts = {}
    for r in results.values():
        key = (r["section"], r.get("status_render"))
        counts[key] = counts.get(key, 0) + 1
    print(json.dumps(dict(seconds=round(time.time() - started), counts={f"{a}/{b}": n for (a, b), n in counts.items()}, index=str(index_path))))


if __name__ == "__main__":
    try:
        import bpy  # noqa: F401
    except ImportError:
        driver(sys.argv[1:])
    else:
        blender_side(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
