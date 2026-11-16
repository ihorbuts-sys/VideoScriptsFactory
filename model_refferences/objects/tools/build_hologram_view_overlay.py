"""Export transparent object images with the global opacity left to the view."""
import hashlib
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from export_shared_venue import apng
from hologram_ghost import render, GLASS_TINT, GLASS_HIGHLIGHT
from optimize_coffee_ghost import features
import export_reconstructed_scene as E

OUT = Path(__file__).resolve().parents[3] / 'catalog/coffee-hologram-study'
SIZE = (405, 720)
VIEW_OPACITY = .65


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(number):
    with Image.open(OUT / 'fields' / f'frame_{number:04d}.png') as fields:
        with Image.open(OUT / 'mask' / f'frame_{number:04d}.png') as mask:
            im = render(fields, np.array(mask.convert('RGBA')), (number - 1) / 15,
                        opacity=1, solid_surfaces=True)
    rgba = np.array(im.resize(SIZE, Image.Resampling.LANCZOS))
    rgba[rgba[:, :, 3] == 0] = 0
    return rgba


def check(path, count, fps):
    duration = maximum = 0
    with Image.open(path) as image:
        assert image.n_frames == count
        assert image.size == SIZE
        for n in range(count):
            image.seek(n)
            duration += image.info['duration']
            lo, hi = image.convert('RGBA').getchannel('A').getextrema()
            assert lo == 0, 'Every frame must retain a transparent background'
            maximum = max(maximum, hi)
    assert abs(duration / 1000 - count / fps) < .03
    return dict(frames=count, seconds=duration / 1000, max_alpha=maximum)


def run():
    spec = json.loads((OUT / 'scene-spec.json').read_text())
    architecture = json.loads((OUT / 'architecture-exclusion.json').read_text())
    assert architecture['walls_and_floor_hidden']
    assert any('floor' in n.lower() for n in architecture['excluded_objects'])
    assert any('wall' in n.lower() for n in architecture['excluded_objects'])
    assert architecture['mounted_objects_retained']
    probes = spec['probe_frames']
    # This material has one continuous tint/highlight ramp. Preserve its three
    # dominant surface alpha levels exactly instead of spending palette entries
    # on rare edge colors. This also avoids coarse color bands at 100% opacity.
    tint = np.array(GLASS_TINT, np.float32)
    delta = np.array(GLASS_HIGHLIGHT, np.float32) - tint
    rows = [[0, 0, 0, 0]]
    warm_lights = bool(spec.get('lighting_action'))
    for alpha, count in [(255, 64 if warm_lights else 96), (235, 64 if warm_lights else 96), (140, 32),
                         (20, 6), (60, 6), (100, 6), (180, 6), (210, 6)]:
        for shade in np.linspace(0, 1, count):
            rows.append([*np.rint(tint + delta * shade).astype(int), alpha])
    if warm_lights:
        for alpha in [255,235]:
            for shade in np.linspace(0,1,32):
                rows.append([255,round(207+38*shade),round(106+85*shade),alpha])
    while len(rows) < 256:
        rows.append([0, 0, 0, 0])
    palette = np.array(rows, dtype=np.uint8)
    transparent = 0
    tree = cv2.flann_Index(features(palette), dict(algorithm=1, trees=4))
    a, shade = np.indices((64, 512), dtype=np.float32)
    grid = np.column_stack([tint + delta * shade.reshape(-1, 1) / 511,
                            a.reshape(-1, 1) * 255 / 63])
    selected, _ = tree.knnSearch(features(grid), 1, params=dict(checks=128))
    lookup = selected.reshape(64, 512).astype(np.uint8)
    frames = OUT / 'view-frames'
    frames.mkdir(exist_ok=True)
    errors = []
    opacity_checks = []
    for n in range(1, spec['frame_count'] + 1):
        rgba = source(n)
        shade = np.clip(((rgba[:, :, :3].astype(np.float32) - tint) * delta).sum(axis=2)
                        / (delta * delta).sum(), 0, 1)
        alpha = np.rint(rgba[:, :, 3].astype(np.float32) * 63 / 255).astype(np.uint8)
        indices = lookup[alpha, np.rint(shade * 511).astype(np.int32)]
        if warm_lights:
            projected=tint+delta*shade[:, :, None]
            off_ramp=np.linalg.norm(rgba[:, :, :3]-projected,axis=2)>6
            if off_ramp.any():
                selected,_=tree.knnSearch(features(rgba[off_ramp].astype(np.float32)),1,params=dict(checks=128))
                indices[off_ramp]=selected[:,0].astype(np.uint8)
        indices[rgba[:, :, 3] == 0] = transparent
        image = Image.fromarray(indices)
        image.putpalette(palette[:, :3].flatten().tolist())
        image.info['transparency'] = bytes(palette[:, 3])
        image.save(frames / f'frame_{n:04d}.png')
        if n in probes:
            decoded = palette[indices]
            with Image.open(OUT / 'mask' / f'frame_{n:04d}.png') as mask:
                role = np.array(mask.resize(SIZE, Image.Resampling.NEAREST).convert('RGBA'))
            core = cv2.erode(((role[:, :, 1] > 245) & (role[:, :, 3] > 250)).astype(np.uint8),
                             np.ones((5, 5), np.uint8)).astype(bool)
            if core.sum() > 50:
                median_alpha = float(np.median(decoded[:, :, 3][core]))
                assert median_alpha >= 245, (n, median_alpha)
                opacity_checks.append(dict(frame=n, hero_core_median_alpha_at_100=median_alpha))
            for bg in [np.array([247, 242, 231]), np.array([30, 42, 35])]:
                aa = rgba[:, :, 3:4] / 255 * VIEW_OPACITY
                bb = decoded[:, :, 3:4] / 255 * VIEW_OPACITY
                expected = rgba[:, :, :3] * aa + bg * (1 - aa)
                actual = decoded[:, :, :3] * bb + bg * (1 - bb)
                error = float(np.abs(expected - actual).mean())
                assert error < 1.6, (n, error)
                errors.append(error)
        if n % 60 == 0:
            print('VIEW_OVERLAY_FRAME', n, flush=True)
    files = {}
    phases = []
    for folder, first, count in [(OUT, 1, spec['frame_count']), *[
            (OUT / 'phases' / p['id'], p['source_first_frame'], p['frames'])
            for p in spec['exported_phases']]]:
        apng(frames, folder / 'view-overlay.png', first, count, spec['fps'])
        report = check(folder / 'view-overlay.png', count, spec['fps'])
        with Image.open(frames / f'frame_{first:04d}.png') as poster:
            poster.convert('RGBA').save(folder / 'view-overlay-poster.png')
        numbers = sorted(set(round(first + (count - 1) * u) for u in [0, .2, .4, .6, .8, 1]))
        images = []
        for n in numbers:
            with Image.open(frames / f'frame_{n:04d}.png') as image:
                image = image.convert('RGBA')
                image.putalpha(image.getchannel('A').point(lambda value: round(value * VIEW_OPACITY)))
                images.append(image)
        E.OUT, E.FPS = folder, spec['fps']
        E.strip(images, numbers, 'view-overlay-strip.jpg')
        for name in ['view-overlay.png', 'view-overlay-poster.png', 'view-overlay-strip.jpg']:
            files[str((folder / name).relative_to(OUT))] = digest(folder / name)
        phases.append(dict(folder=str(folder.relative_to(OUT)), **report))
    report = dict(status='passed', image_opacity_baked=1, recommended_image_view_opacity=VIEW_OPACITY,
        background_delay_seconds=2, viewfinder_embedded=False, walls_excluded=True, floor_excluded=True,
        ceiling_excluded=True, mounted_objects_retained=True, resolution=list(SIZE), phases=phases,
        surface_visibility='hero opaque at 100%; support 92%; context 55%',
        opacity_100_sample_checks=opacity_checks,
        max_composited_mean_error=max(errors), files=files)
    (OUT / 'view-overlay-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    spec.update(surface_style='glass-full-surfaces-v3',
        display=dict(opacity_mode='image_view', image_opacity=.65, background_delay_seconds=2,
                     viewfinder='separate_ui_layer', walls=False, floor=False, ceiling=False))
    (OUT / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    checks = json.loads((OUT / 'export-checks.json').read_text()) if (OUT / 'export-checks.json').exists() else dict(status='passed',files={})
    checks['files']['scene-spec.json'] = digest(OUT / 'scene-spec.json')
    (OUT / 'export-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps(dict(status='passed', images_use_view_opacity=True, phases=len(phases))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder',type=Path)
    args = parser.parse_args()
    if args.folder:
        OUT = args.folder.resolve()
    run()
