"""Run after scene.blend in Blender's argument list."""
import bpy
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
lighting = "--lighting" in args
scene = bpy.data.scenes.get("02 Morning window light") if lighting else bpy.data.scenes.get("01 Contour guide", bpy.context.scene)
bpy.context.window.scene = scene
frames = [1, 46, 70] if "--probes" in args else range(61, 85) if "--table" in args else range(1, 85)

for i, frame in enumerate(frames):
    scene.frame_set(frame)
    folder = OUT if "--probes" in args else OUT / ("lit_frames" if lighting else "frames")
    folder.mkdir(exist_ok=True)
    name = ("lit_probe_%04d.png" if lighting else "probe_%04d.png") if "--probes" in args else "frame_%04d.png"
    scene.render.filepath = str(folder / (name % frame))
    # These are actual specified holds, so reuse the identical render exactly.
    held_source = 1 if 2 <= frame <= 19 else 46 if 47 <= frame <= 60 else None
    if "--probes" not in args and held_source:
        shutil.copy2(folder / (name % held_source), folder / (name % frame))
    else:
        bpy.ops.render.render(write_still=True, scene=scene.name)
    if "--probes" in args and frame == 1 and not lighting:
        shutil.copy2(folder / (name % frame), OUT / "poster.png")
    data = dict(message="Rendering the morning-window lighting example." if lighting else "Rendering Blender contour previews." if "--probes" in args else "Rendering the camera animation in Blender.",
                progress="%d / %d frames rendered." % (i + 1, len(frames)), ready=False, preview=True)
    tmp = ROOT / "status.tmp"
    tmp.write_text("blenderProgress(" + json.dumps(data) + ");\n")
    tmp.replace(ROOT / "status.js")

if lighting and "--probes" in args:
    scene.timeline_markers.clear()
    scene.camera = bpy.data.objects["LIGHTING SETUP - window and opposing diners"]
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = str(OUT / "lighting_setup.png")
    bpy.ops.render.render(write_still=True, scene=scene.name)
