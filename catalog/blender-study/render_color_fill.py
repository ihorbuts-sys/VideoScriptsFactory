"""Render faint flat fills from the same 3D geometry and cameras as the ghost.

Solid depth-tested masks avoid accumulating fill where objects overlap. Only
guide subjects contribute; room walls, floors, lighting cues and ceilings do not.
"""
import bpy
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
FOLDER = OUT / "fill_frames"
FOLDER.mkdir(exist_ok=True)
ALPHA_BEFORE_FINAL_PASS = dict(hero=.50, support=.35, important_background=.40,
                              foreground_frame=.25, structure=.20, background=.125)


def linear(srgb):
    return srgb / 12.92 if srgb <= .04045 else ((srgb + .055) / 1.055) ** 2.4


scene = bpy.data.scenes.get("04 Ghost color fill")
if scene is None:
    scene = bpy.data.scenes["01 Contour guide"].copy()
    scene.name = "04 Ghost color fill"
scene.use_fake_user = True
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 16
scene.render.use_sequencer = False
scene.render.use_compositing = False
scene.render.use_freestyle = False
scene.render.film_transparent = True
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.timeline_markers.clear()
bpy.context.window.scene = scene
for child in scene.view_layers[0].layer_collection.children:
    if child.name.startswith("Lighting set") or child.name.startswith("Ghost light"):
        child.exclude = True

mat = bpy.data.materials.get("Ghost fill opacity mask") or bpy.data.materials.new("Ghost fill opacity mask")
mat.use_nodes = True
mat.node_tree.nodes.clear()
info = mat.node_tree.nodes.new("ShaderNodeObjectInfo")
emission = mat.node_tree.nodes.new("ShaderNodeEmission")
output = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
mat.node_tree.links.new(info.outputs["Color"], emission.inputs["Color"])
mat.node_tree.links.new(emission.outputs[0], output.inputs[0])
scene.view_layers[0].material_override = mat
for obj in bpy.data.collections["Guide subjects - reusable geometry"].all_objects:
    if obj.type == "MESH" and not obj.hide_render:
        role = obj.get("composition_role", "support")
        value = linear(ALPHA_BEFORE_FINAL_PASS[role])
        obj.color = (value, value, value, 1)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
frames = [1, 70] if "--probes" in args else range(1, 85)
for i, frame in enumerate(frames):
    scene.frame_set(frame)
    scene.camera = bpy.data.objects["02 HIGH TABLE - gentle approach" if frame >= 61 else "01 LOW BAR - truck right 0.8m"]
    target = FOLDER / ("frame_%04d.png" % frame)
    held_source = 1 if 2 <= frame <= 19 else 46 if 47 <= frame <= 60 else None
    if held_source is not None:
        shutil.copy2(FOLDER / ("frame_%04d.png" % held_source), target)
    else:
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True, scene=scene.name)
    data = dict(message="Rendering faint colour fills beneath the ghost outlines.",
                progress="%d / %d frames." % (i + 1, len(frames)), ready=False, preview=True)
    temp = ROOT / "status.tmp"
    temp.write_text("blenderProgress(" + json.dumps(data) + ");\n")
    temp.replace(ROOT / "status.js")

(OUT / "color-fill-settings.json").write_text(json.dumps(dict(
    pigment_rgb=[118, 155, 178], final_fill_alpha={k: v * .5 for k, v in ALPHA_BEFORE_FINAL_PASS.items()},
    method="Depth-tested Blender masks under existing contours; final frame alpha x 0.5 once",
    walls_filled=False, outlines_preserved=True, samples=16,
    role_masks="Grayscale RGB encodes fill opacity; render alpha encodes edge coverage"
), indent=2) + "\n")
