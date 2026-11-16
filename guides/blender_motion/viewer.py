"""Live Blender viewer for the active generated scene, with automatic updates."""
import bpy
import json
import os
from pathlib import Path

CATALOG=Path(__file__).resolve().parents[2]/"catalog/blender-animations"
LAST_COMMAND=None
READY_FOLDER=None


def start():
    if bpy.context.window is None:return .3
    window=bpy.context.window
    source=bpy.data.scenes.get("01 Ghost contours") or window.scene
    out=Path(bpy.data.filepath).parent
    files=sorted((out/"ghost_frames").glob("frame_*.png"))
    preview=bpy.data.scenes.get("03 Ghost playback")
    if files and len(files)==source.frame_end and preview is None:
        preview=source.copy();preview.name="03 Ghost playback";preview.use_fake_user=True
        cues=preview.view_layers[0].layer_collection.children.get("Role - lighting_cue")
        if cues is not None:cues.exclude=True
        preview.render.use_freestyle=False;preview.render.use_compositing=False;preview.render.use_sequencer=True
        preview.view_settings.view_transform="Standard"
        editor=preview.sequence_editor_create()
        bg=editor.strips.new_effect(name="Neutral preview backing",type="COLOR",channel=1,frame_start=1,length=len(files))
        bg.color=(.95,.945,.93)
        strip=editor.strips.new_image(name="Actual transparent ghost",filepath=str(files[0]),channel=2,frame_start=1)
        for path in files[1:]:strip.elements.append(path.name)
        strip.frame_final_duration=len(files);strip.blend_type="ALPHA_OVER";strip.blend_alpha=1
        strip.directory="//ghost_frames/"
        if (out/"viewfinder.png").exists():
            sight=editor.strips.new_image(name="Fixed review guides",filepath=str(out/"viewfinder.png"),channel=3,frame_start=1)
            sight.frame_final_duration=len(files);sight.blend_type="ALPHA_OVER";sight.directory="//"
    window.scene=preview or source
    window.scene.sync_mode="FRAME_DROP";window.scene.frame_set(1)
    screen=window.screen
    if preview and not any(a.type=="SEQUENCE_EDITOR" for a in screen.areas):
        area=max((a for a in screen.areas if a.type=="VIEW_3D"),key=lambda a:a.width*a.height)
        with bpy.context.temp_override(window=window,area=area):
            bpy.ops.screen.area_split(direction="VERTICAL",factor=.5)
        left=min((a for a in screen.areas if a.type=="VIEW_3D"),key=lambda a:a.x)
        left.type="SEQUENCE_EDITOR";left.spaces.active.view_type="PREVIEW"
    for area in screen.areas:
        if area.type=="VIEW_3D":
            space=area.spaces.active;space.region_3d.view_perspective="CAMERA"
            space.region_3d.view_camera_zoom=6;space.shading.type="MATERIAL";space.shading.color_type="MATERIAL"
            space.shading.use_scene_lights=True;space.shading.use_scene_world=True
            space.overlay.show_floor=False
            area.header_text_set("LIVE 3D CAMERA | "+out.name)
        elif area.type=="SEQUENCE_EDITOR":
            area.spaces.active.use_zoom_to_fit=True
            area.header_text_set("GHOST OVERLAY | "+out.name+" | 25% main fill")
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"scene.blend"))
    if not screen.is_animation_playing:
        with bpy.context.temp_override(window=window):bpy.ops.screen.animation_play()
    print("LIVE_VIEWER_PLAYING",out.name,flush=True)
    return None


def watch():
    global LAST_COMMAND,READY_FOLDER
    windows=list(bpy.context.window_manager.windows)
    if not windows:return 1
    window=windows[0];out=Path(bpy.data.filepath).parent
    command=CATALOG/"viewer-command.json"
    if command.exists():
        try:
            data=json.loads(command.read_text())
            if data.get("serial")!=LAST_COMMAND:
                LAST_COMMAND=data.get("serial")
                gid=data.get("guide","")
                if gid and all(c.isalnum() or c=="_" for c in gid):
                    target=CATALOG/gid/"scene.blend"
                    if target.exists() and target.resolve()!=Path(bpy.data.filepath).resolve():
                        with bpy.context.temp_override(window=window):
                            if window.screen.is_animation_playing:bpy.ops.screen.animation_play()
                            bpy.ops.wm.open_mainfile(filepath=str(target))
                        READY_FOLDER=None;bpy.app.timers.register(start,first_interval=.5);return .8
        except (OSError,ValueError):pass
    if (out/"ghost_frames/frame_0001.png").exists() and READY_FOLDER!=str(out):
        source=bpy.data.scenes.get("01 Ghost contours")
        if source and len(list((out/"ghost_frames").glob("frame_*.png")))==source.frame_end:
            READY_FOLDER=str(out)
            if bpy.data.scenes.get("03 Ghost playback") is None:
                if window.screen.is_animation_playing:
                    with bpy.context.temp_override(window=window):bpy.ops.screen.animation_play()
                bpy.app.timers.register(start,first_interval=.3)
    state=dict(pid=os.getpid(),guide=out.name,frame=window.scene.frame_current,playing=window.screen.is_animation_playing,
               scene=window.scene.name,editors=[a.type for a in window.screen.areas])
    (CATALOG/"viewer-state.json").write_text(json.dumps(state)+"\n")
    return 1


bpy.app.timers.register(start,first_interval=.7)
bpy.app.timers.register(watch,first_interval=1.2,persistent=True)
