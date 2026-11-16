"""A local command file keeps this Blender review window current without closing edits."""
import json
import time
import traceback
from pathlib import Path

import bpy

OUT = Path(bpy.data.filepath).resolve().parent
COMMAND = OUT / 'ui-command.json'
STATUS = OUT / 'blender-ui.json'
seen = COMMAND.stat().st_mtime_ns if COMMAND.exists() else 0
initialized = False


def context():
    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return window, area, region


def pause():
    window, area, region = context()
    with bpy.context.temp_override(window=window, area=area, region=region):
        if window.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)


def configure():
    window, area, region = context()
    pause()
    window.scene.sync_mode = 'FRAME_DROP'
    window.scene.frame_set(31)
    view = area.spaces.active
    view.region_3d.view_perspective = 'CAMERA'
    view.overlay.show_overlays = False
    view.shading.type = 'MATERIAL'
    view.shading.use_scene_lights = True
    view.shading.use_scene_world = True


def status(extra=None):
    window, area, region = context()
    report = dict(status='ready', file=bpy.data.filepath, frame=window.scene.frame_current,
        playback_started=window.screen.is_animation_playing, camera_view=True,
        live_reload_available=True, instruction='Spacebar plays or pauses. User edits are backed up before a requested scene reload.')
    report.update(extra or {})
    STATUS.write_text(json.dumps(report, indent=2)+'\n')


def poll():
    global initialized, seen
    try:
        if not initialized:
            configure()
            initialized = True
            status()
        modified = COMMAND.stat().st_mtime_ns if COMMAND.exists() else 0
        if modified > seen:
            data = json.loads(COMMAND.read_text())
            seen = modified
            action = data.get('action')
            if action == 'load':
                target = Path(data['file']).resolve()
                assert target.is_relative_to(OUT) and target.suffix == '.blend' and target.is_file()
                pause()
                if bpy.data.is_dirty:
                    backups = OUT / 'editor-backups'
                    backups.mkdir(exist_ok=True)
                    bpy.ops.wm.save_as_mainfile(filepath=str(backups / (str(time.time_ns())+'.blend')), copy=True)
                bpy.ops.wm.open_mainfile(filepath=str(target), load_ui=False)
                configure()
            elif action == 'pause':
                pause()
            elif action == 'play':
                window, area, region = context()
                with bpy.context.temp_override(window=window, area=area, region=region):
                    if not window.screen.is_animation_playing:
                        bpy.ops.screen.animation_play()
            elif action != 'status':
                raise ValueError('Unknown review action')
            status(dict(last_action=action))
    except Exception:
        STATUS.write_text(json.dumps(dict(status='review_error', error=traceback.format_exc()), indent=2)+'\n')
    return .5


bpy.app.timers.register(poll, first_interval=1, persistent=True)
