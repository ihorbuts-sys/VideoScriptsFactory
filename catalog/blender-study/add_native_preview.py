"""Add a native Blender playback scene for the actual transparent ghost frames."""
import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
lit = bpy.data.scenes["02 Morning window light"]
preview = lit.copy()
preview.name = "03 Ghost overlay playback"
preview.use_fake_user = True
preview.render.use_sequencer = True
preview.render.use_compositing = False
preview.render.use_freestyle = False
preview.view_settings.view_transform = "Standard"
preview.sync_mode = "FRAME_DROP"
editor = preview.sequence_editor_create()
background = editor.strips.new_effect(name="Neutral backing for transparency review", type="COLOR",
                                     channel=1, frame_start=1, length=84)
background.color = (39 / 255, 58 / 255, 71 / 255)
paths = sorted((OUT / "ghost_frames").glob("frame_*.png"))
assert len(paths) == 84
ghost = editor.strips.new_image(name="Actual ghost overlay - final alpha already applied",
                               filepath=str(paths[0]), channel=2, frame_start=1)
for path in paths[1:]:
    ghost.elements.append(path.name)
ghost.frame_final_duration = 84
ghost.blend_type = "ALPHA_OVER"
ghost.blend_alpha = 1
ghost.directory = "//ghost_frames/"
viewfinder = editor.strips.new_image(name="Fixed framing guides - review only",
                                    filepath=str(OUT / "viewfinder.png"), channel=3, frame_start=1)
viewfinder.frame_final_duration = 84
viewfinder.blend_type = "ALPHA_OVER"
viewfinder.blend_alpha = 1
viewfinder.directory = "//"
preview["purpose"] = "Actual ghost overlay on the left, editable live 3D camera setup on the right"
preview.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "SEQUENCE_EDITOR":
            area.spaces.active.use_zoom_to_fit = True
bpy.context.window.scene = preview
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))
print("NATIVE_GHOST_PLAYBACK_READY", flush=True)
