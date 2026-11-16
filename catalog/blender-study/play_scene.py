"""Open with Blender scene.blend --python play_scene.py for automatic playback."""
import bpy
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
command_path = ROOT / "viewport-command.json"
try:
    LAST_COMMAND = json.loads(command_path.read_text()).get("serial")
except (OSError, ValueError):
    LAST_COMMAND = None


def fit_preview():
    for area in bpy.context.window.screen.areas:
        if area.type != "SEQUENCE_EDITOR":
            continue
        area.spaces.active.use_zoom_to_fit = True
    return None


def start_playback():
    if bpy.context.window is None:
        return .3
    lit = bpy.data.scenes.get("03 Ghost overlay playback") or bpy.data.scenes.get("02 Morning window light")
    if lit is not None:
        bpy.context.window.scene = lit
    scene = bpy.context.scene
    scene.sync_mode = "FRAME_DROP"
    scene.frame_set(1)
    screen = bpy.context.window.screen
    if scene.name == "03 Ghost overlay playback" and not any(a.type == "SEQUENCE_EDITOR" for a in screen.areas):
        areas = [a for a in screen.areas if a.type == "VIEW_3D"]
        if areas:
            area = max(areas, key=lambda a: a.width * a.height)
            with bpy.context.temp_override(window=bpy.context.window, area=area):
                bpy.ops.screen.area_split(direction="VERTICAL", factor=.5)
            views = sorted([a for a in screen.areas if a.type == "VIEW_3D"], key=lambda a: a.x)
            left = views[0]
            left.type = "SEQUENCE_EDITOR"
            left.spaces.active.view_type = "PREVIEW"
            left.header_text_set("GHOST OVERLAY | Final transparency and framing guides")
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.header_text_set("EDITABLE 3D SETUP | Same camera and timing")
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.region_3d.view_camera_zoom = 6
                area.spaces.active.shading.type = "MATERIAL"
                area.spaces.active.shading.use_scene_lights = True
                area.spaces.active.shading.use_scene_world = True
    fit_preview()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "bar_low_truckr_mm" / "scene.blend"))
    bpy.app.timers.register(fit_preview, first_interval=.5)
    if not bpy.context.screen.is_animation_playing:
        bpy.ops.screen.animation_play()
    print("BLENDER_PLAYBACK_STARTED", flush=True)
    return None


def report_state():
    global LAST_COMMAND
    windows = list(bpy.context.window_manager.windows)
    if not windows:
        return 1.0
    window = windows[0]
    command_file = ROOT / "viewport-command.json"
    if command_file.exists():
        try:
            command = json.loads(command_file.read_text())
            if command.get("serial") != LAST_COMMAND:
                LAST_COMMAND = command.get("serial")
                if command.get("action") == "reload":
                    if any(w.screen.is_animation_playing for w in bpy.context.window_manager.windows):
                        bpy.ops.screen.animation_play()
                    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "bar_low_truckr_mm" / "scene.blend"))
                    bpy.app.timers.register(start_playback, first_interval=.5)
                    return .8
        except (ValueError, OSError):
            pass
    state = dict(pid=os.getpid(), frame=window.scene.frame_current,
                 scene_name=window.scene.name,
                 editors=[a.type for a in window.screen.areas],
                 playing=any(w.screen.is_animation_playing for w in bpy.context.window_manager.windows),
                 scene=str(bpy.data.filepath), windows=len(bpy.context.window_manager.windows))
    (ROOT / "viewport-state.json").write_text(json.dumps(state) + "\n")
    return 1.0


bpy.app.timers.register(start_playback, first_interval=.8)
bpy.app.timers.register(report_state, first_interval=1.2, persistent=True)
