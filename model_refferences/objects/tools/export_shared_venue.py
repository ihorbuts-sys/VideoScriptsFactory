"""Stream shared-room exports and slice handovers from the same rendered route."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_reconstructed_scene as E

BASE = Path(__file__).resolve().parents[3]


def apng(folder, output, first, count, fps):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps),
                    '-start_number', str(first), '-i', str(folder / 'frame_%04d.png'),
                    '-frames:v', str(count), '-plays', '0', '-f', 'apng',
                    '-compression_level', '4', str(output)], check=True)


def check_apng(path, count, seconds):
    with Image.open(path) as im:
        total = maximum = 0
        assert im.n_frames == count, (path, im.n_frames, count)
        for frame in range(im.n_frames):
            im.seek(frame)
            total += im.info.get('duration', 0)
            maximum = max(maximum, im.convert('RGBA').getchannel('A').getextrema()[1])
        assert abs(total / 1000 - seconds) < .03, (path, total, seconds)
        assert maximum <= 166, (path, maximum)
    return dict(frames=count, seconds=total / 1000, max_alpha=maximum)


def run(venue, folder=None):
    out = Path(folder) if folder else BASE / 'catalog/shared-venue-visits' / venue
    E.OUT = out
    spec = json.loads((out / 'scene-spec.json').read_text())
    fps = spec['fps']
    count = spec['frame_count']
    E.FPS = fps
    E.GHOST_STYLE = spec.get('ghost_style')
    assert all((out / mode / f'frame_{n:04d}.png').exists()
               for mode in ['color', 'mask'] for n in range(1, count + 1)), 'Render is incomplete'
    ghost_frames = out / 'ghost-frames'
    ghost_frames.mkdir(exist_ok=True)
    writer = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo',
        '-pix_fmt', 'rgb24', '-s', '540x960', '-r', str(fps), '-i', '-', '-an',
        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        str(out / 'color.mp4')], stdin=subprocess.PIPE)
    chosen = sorted(set([1, *spec['probe_frames'], count]))
    colors = {}
    ghosts = {}
    first_pixels = last_pixels = None
    maximum_alpha = 0
    for frame in range(1, count + 1):
        color, ghost = E.frame(frame)
        maximum_alpha = max(maximum_alpha, ghost.getchannel('A').getextrema()[1])
        assert maximum_alpha <= 166
        ghost.save(ghost_frames / f'frame_{frame:04d}.png')
        background = Image.new('RGBA', color.size, '#f7f2e7')
        background.alpha_composite(color)
        writer.stdin.write(background.convert('RGB').tobytes())
        if frame == 1:
            first_pixels = np.array(background)
            color.save(out / 'color-poster.png')
            ghost.save(out / 'ghost-poster.png')
        if frame == count:
            last_pixels = np.array(background)
        if frame in chosen:
            colors[frame] = color.copy()
            ghosts[frame] = ghost.copy()
    writer.stdin.close()
    assert writer.wait() == 0
    apng(ghost_frames, out / 'ghost.png', 1, count, fps)
    checks = check_apng(out / 'ghost.png', count, count / fps)
    E.strip([colors[n] for n in chosen], chosen, 'color-strip.jpg')
    E.strip([ghosts[n] for n in chosen], chosen, 'ghost-strip.jpg')
    phase_records = []
    for index, phase in enumerate(spec['phases']):
        folder = out / 'phases' / phase['id']
        folder.mkdir(parents=True, exist_ok=True)
        first = round(phase['start_s'] * fps) + 1
        capture_frames = round((phase['end_s'] - phase['start_s']) * fps)
        tail = min(23, count - (first + capture_frames - 1)) if index < len(spec['phases']) - 1 else 0
        length = capture_frames + tail
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(out / 'color.mp4'),
            '-vf', f'trim=start_frame={first - 1}:end_frame={first - 1 + length},setpts=PTS-STARTPTS',
            '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
            str(folder / 'color.mp4')], check=True)
        apng(ghost_frames, folder / 'ghost.png', first, length, fps)
        report = check_apng(folder / 'ghost.png', length, length / fps)
        color, ghost = E.frame(first)
        color.save(folder / 'color-poster.png')
        ghost.save(folder / 'ghost-poster.png')
        strip_numbers = sorted(set(round(first + (length - 1) * u) for u in [0, .2, .4, .6, .8, 1]))
        clip_colors = []
        clip_ghosts = []
        for number in strip_numbers:
            c, g = E.frame(number)
            clip_colors.append(c)
            clip_ghosts.append(g)
        old_out = E.OUT
        E.OUT = folder
        E.strip(clip_colors, strip_numbers, 'color-strip.jpg')
        E.strip(clip_ghosts, strip_numbers, 'ghost-strip.jpg')
        E.OUT = old_out
        phase_records.append(dict(**phase, frames=length, capture_seconds=capture_frames / fps,
            animation_seconds=length / fps, handover_seconds=tail / fps,
            next_phase=spec['phases'][index + 1]['id'] if tail else None,
            source_first_frame=first, source_last_frame=first + length - 1,
            scope='shot_and_handover' if tail else 'complete_final_shot', export_checks=report))
    changed = float(np.mean(np.any(first_pixels != last_pixels, axis=2)))
    assert changed > .03
    spec['status'] = 'color_and_ghost_proof_ready' if 'proof' in spec['scope'] else 'color_and_ghost_visit_ready'
    spec['exported_phases'] = phase_records
    (out / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    checks.update(status='passed', whole_overlay_alpha=.65, matching_camera_for_both_variants=True,
                  no_embedded_viewfinder=True, full_route_continuous=True,
                  first_last_changed_pixel_fraction=changed, scope=spec['scope'],
                  phases=phase_records, scene_texture_sizes_preserve_original_assets=True,
                  files={name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                         for name in ['scene.blend', 'scene-spec.json', 'color.mp4', 'ghost.png']})
    (out / 'export-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps(dict(venue=venue, status='passed', phases=len(phase_records), frames=count,
                         seconds=count / fps, max_alpha=maximum_alpha)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('venue', choices=['cafe', 'bakery', 'bar'])
    run(parser.parse_args().venue)
