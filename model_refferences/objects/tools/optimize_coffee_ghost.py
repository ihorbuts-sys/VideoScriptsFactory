"""Encode a smaller ghost with one shared RGBA palette and unchanged timing."""
import hashlib
import argparse
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_reconstructed_scene as E
from export_shared_venue import apng, check_apng

OUT = Path(__file__).resolve().parents[3] / 'catalog/coffee-ordering'
SIZE = (405, 720)


def small(number):
    im = Image.open(OUT / 'ghost-frames' / f'frame_{number:04d}.png').convert('RGBA')
    array = np.array(im.resize(SIZE, Image.Resampling.LANCZOS))
    array[:, :, 3] = np.minimum(array[:, :, 3], 166)
    array[array[:, :, 3] == 0] = 0
    return array


def features(rgba):
    values = rgba.astype(np.float32)
    values[:, :3] *= values[:, 3:4] / 255
    values[:, 3] *= 2
    return values


def run():
    spec = json.loads((OUT / 'scene-spec.json').read_text())
    old = json.loads((OUT / 'export-checks.json').read_text())
    assert old['status'] == 'passed'
    probes = spec['probe_frames']
    sample = Image.new('RGBA', (SIZE[0] * 3, SIZE[1] * 3))
    for index, number in enumerate(probes):
        sample.paste(Image.fromarray(small(number)), ((index % 3) * SIZE[0], (index // 3) * SIZE[1]))
    quantized = sample.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    palette = np.array(quantized.getpalette('RGBA'), dtype=np.uint8).reshape(-1, 4)
    used = np.unique(np.array(quantized))
    palette[np.setdiff1d(np.arange(256), used)] = 0
    assert palette[:, 3].max() <= 166
    tree = cv2.flann_Index(features(palette), dict(algorithm=1, trees=4))
    # Cache nearest RGBA palette entries once; frame conversion becomes indexing.
    a, r, g, b = np.indices((43, 32, 32, 32), dtype=np.float32)
    grid = np.stack([r * 255 / 31, g * 255 / 31, b * 255 / 31, a * 166 / 42], axis=-1).reshape(-1, 4)
    indices, distances = tree.knnSearch(features(grid), 1, params=dict(checks=64))
    lookup = indices.reshape(43, 32, 32, 32).astype(np.uint8)
    folder = OUT / 'ghost-mobile-frames'
    folder.mkdir(exist_ok=True)
    errors = []
    for number in range(1, spec['frame_count'] + 1):
        rgba = small(number)
        rgb = np.rint(rgba[:, :, :3].astype(np.float32) * 31 / 255).astype(np.uint8)
        alpha = np.rint(rgba[:, :, 3].astype(np.float32) * 42 / 166).astype(np.uint8)
        selected = lookup[alpha, rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]]
        image = Image.fromarray(selected, mode='P')
        image.putpalette(palette[:, :3].flatten().tolist())
        image.info['transparency'] = bytes(palette[:, 3])
        image.save(folder / f'frame_{number:04d}.png', compress_level=6)
        if number in probes:
            decoded = palette[selected]
            for bg in [(247, 242, 231), (30, 42, 35)]:
                original = rgba[:, :, :3] * (rgba[:, :, 3:4] / 255) + np.array(bg) * (1 - rgba[:, :, 3:4] / 255)
                result = decoded[:, :, :3] * (decoded[:, :, 3:4] / 255) + np.array(bg) * (1 - decoded[:, :, 3:4] / 255)
                error = float(np.abs(original - result).mean())
                errors.append(error)
                assert error < 1.6, (number, bg, error)
        if number % 60 == 0:
            print('MOBILE_GHOST_FRAME', number, flush=True)
    temporary = OUT / 'ghost-mobile.png'
    apng(folder, temporary, 1, spec['frame_count'], spec['fps'])
    verified = check_apng(temporary, spec['frame_count'], spec['duration_s'])
    previous_size = (OUT / 'ghost.png').stat().st_size
    new_size = temporary.stat().st_size
    assert new_size < previous_size * .30, (new_size, previous_size)
    backup = OUT / 'full-resolution-exports'
    backup.mkdir(exist_ok=True)
    for name in ['ghost.png', 'ghost-poster.png', 'ghost-strip.jpg', 'export-checks.json']:
        shutil.copy2(OUT / name, backup / name)
    temporary.replace(OUT / 'ghost.png')
    Image.open(folder / 'frame_0001.png').convert('RGBA').save(OUT / 'ghost-poster.png')
    E.OUT = OUT
    E.FPS = spec['fps']
    chosen = sorted(set([1, *probes, spec['frame_count']]))
    E.strip([Image.open(folder / f'frame_{n:04d}.png').convert('RGBA') for n in chosen], chosen, 'ghost-strip.jpg')
    for phase in spec['exported_phases']:
        target = OUT / 'phases' / phase['id']
        original = backup / 'phases' / phase['id']
        original.mkdir(parents=True, exist_ok=True)
        for name in ['ghost.png', 'ghost-poster.png', 'ghost-strip.jpg']:
            shutil.copy2(target / name, original / name)
        first = phase['source_first_frame']
        length = phase['frames']
        apng(folder, target / 'ghost.png', first, length, spec['fps'])
        phase['export_checks'] = check_apng(target / 'ghost.png', length, length / spec['fps'])
        Image.open(folder / f'frame_{first:04d}.png').convert('RGBA').save(target / 'ghost-poster.png')
        numbers = sorted(set(round(first + (length - 1) * u) for u in [0, .2, .4, .6, .8, 1]))
        E.OUT = target
        E.strip([Image.open(folder / f'frame_{n:04d}.png').convert('RGBA') for n in numbers], numbers, 'ghost-strip.jpg')
    spec['ghost_resolution'] = list(SIZE)
    spec['ghost_encoding'] = 'Shared 256-entry RGBA palette; source color/mask renders retained'
    (OUT / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    old.update(verified, ghost_resolution=list(SIZE), mobile_optimized=True,
        alpha_applied_again=False, original_apng_bytes=previous_size, optimized_apng_bytes=new_size,
        mean_composited_pixel_error=max(errors), phases=spec['exported_phases'])
    old['files'] = {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in old['files']}
    (OUT / 'export-checks.json').write_text(json.dumps(old, indent=2) + '\n')
    print(json.dumps(dict(status='passed', original_bytes=previous_size, optimized_bytes=new_size,
        reduction_percent=round(100 * (1-new_size/previous_size), 1), max_composited_mean_error=max(errors))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=Path)
    args = parser.parse_args()
    if args.folder:
        OUT = args.folder.resolve()
    run()
