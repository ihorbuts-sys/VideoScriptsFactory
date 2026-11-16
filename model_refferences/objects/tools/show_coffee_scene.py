"""Open the requested scene in camera view and start timeline playback."""
import json
import traceback
from pathlib import Path

import bpy

OUT = Path(bpy.data.filepath).parent if bpy.data.filepath else Path(__file__).resolve().parents[3] / 'catalog/coffee-ordering'
(OUT / 'blender-ui.json').write_text(json.dumps(dict(status='startup_script_loaded')) + '\n')


def configure():
    manager = bpy.context.window_manager
    if not manager.windows:
        return 1.0
    window = manager.windows[0]
    scene = window.scene
    scene.sync_mode = 'FRAME_DROP'
    scene.frame_set(1)
    area = next((area for area in window.screen.areas if area.type == 'VIEW_3D'), None)
    if area is None:
        return 1.0
    space = area.spaces.active
    space.region_3d.view_perspective = 'CAMERA'
    space.region_3d.view_camera_zoom = 0
    space.overlay.show_overlays = False
    space.shading.type = 'MATERIAL'
    space.shading.use_scene_lights = True
    space.shading.use_scene_world = True
    region = next(region for region in area.regions if region.type == 'WINDOW')
    with bpy.context.temp_override(window=window, area=area, region=region):
        if not window.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
    (OUT / 'blender-ui.json').write_text(json.dumps(dict(scene=str(OUT / 'scene.blend'),
        camera_view=True, playback_started=window.screen.is_animation_playing,
        start_frame=scene.frame_start, end_frame=scene.frame_end,
        instruction='Spacebar pauses or resumes playback; numpad 0 toggles the camera view.'), indent=2) + '\n')
    return None


def ready():
    try:
        return configure()
    except Exception:
        (OUT / 'blender-ui.json').write_text(json.dumps(dict(status='playback_start_error',
            error=traceback.format_exc()), indent=2) + '\n')
        return None


bpy.app.timers.register(ready, first_interval=2)
