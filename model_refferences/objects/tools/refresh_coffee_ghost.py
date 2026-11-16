"""Rebuild only coffee ghosts from native passes; preserve all colored videos."""
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

import export_reconstructed_scene as E
from export_shared_venue import apng, check_apng

OUT = Path(__file__).resolve().parents[3] / 'catalog/coffee-ordering-v2'
STYLE = 'smooth-contours-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    spec = json.loads((OUT / 'scene-spec.json').read_text())
    checks = json.loads((OUT / 'export-checks.json').read_text())
    backup = OUT / 'before-smooth-contours'
    assert not backup.exists(), 'The prior revision is already archived; do not overwrite it'
    backup.mkdir()
    for folder in [OUT, *(OUT / 'phases').iterdir()]:
        target = backup / folder.relative_to(OUT)
        target.mkdir(parents=True, exist_ok=True)
        for name in ['ghost.png', 'ghost-poster.png', 'ghost-strip.jpg',
                     'scene-spec.json', 'export-checks.json', 'browser-check.json']:
            if (folder / name).exists():
                shutil.copy2(folder / name, target / name)
    video_hashes = {str(p.relative_to(OUT)): digest(p) for p in [
        OUT / 'color.mp4', *(OUT / 'phases').glob('*/color.mp4')]}
    E.OUT, E.FPS, E.GHOST_STYLE = OUT, spec['fps'], STYLE
    folder = OUT / 'ghost-frames'
    for number in range(1, spec['frame_count'] + 1):
        _, ghost = E.frame(number)
        assert ghost.getchannel('A').getextrema()[1] <= 166
        ghost.save(folder / f'frame_{number:04d}.png')
        if number % 60 == 0:
            print('SMOOTH_GHOST_FRAME', number, flush=True)

    def package(target, first, count):
        apng(folder, target / 'ghost.png', first, count, spec['fps'])
        verified = check_apng(target / 'ghost.png', count, count / spec['fps'])
        Image.open(folder / f'frame_{first:04d}.png').save(target / 'ghost-poster.png')
        numbers = sorted(set(round(first + (count - 1) * u) for u in [0, .2, .4, .6, .8, 1]))
        E.OUT = target
        E.strip([Image.open(folder / f'frame_{n:04d}.png').convert('RGBA')
                 for n in numbers], numbers, 'ghost-strip.jpg')
        E.OUT = OUT
        return verified

    checks.update(package(OUT, 1, spec['frame_count']))
    for phase in spec['exported_phases']:
        phase['export_checks'] = package(OUT / 'phases' / phase['id'],
            phase['source_first_frame'], phase['frames'])
    assert all(digest(OUT / name) == sha for name, sha in video_hashes.items())
    spec.update(ghost_style=STYLE, revision='coffee-left-milk-smooth-v3',
                ghost_resolution=[540, 960],
                ghost_simplification='Smoothed role silhouettes; large denoised features only; '
                                     'no fine grain, material marks or small contour fragments')
    (OUT / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    checks.update(ghost_style=STYLE, color_video_hashes_preserved=video_hashes,
                  whole_overlay_alpha=.65, phases=spec['exported_phases'])
    checks['files'] = {name: digest(OUT / name) for name in checks['files']}
    (OUT / 'export-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps(dict(status='passed', style=STYLE, color_videos_unchanged=True)), flush=True)


if __name__ == '__main__':
    run()
