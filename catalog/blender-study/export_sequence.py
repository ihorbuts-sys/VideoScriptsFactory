"""Compose Blender renders into review and transparent animation artifacts.

No illustrated objects are drawn here. Framing guides belong to the review UI.
Blender renders are preserved in frames/. Alpha is multiplied by 0.5 once.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import subprocess
import shutil
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
SIZE = (540, 960)


def guides():
    image = Image.new("RGBA", SIZE)
    d = ImageDraw.Draw(image)
    w, h = SIZE
    for x in [w / 3, 2 * w / 3]:
        d.line((x, 0, x, h), fill=(113, 139, 154, 45), width=1)
    for y in [h / 3, 2 * h / 3]:
        d.line((0, y, w, y), fill=(113, 139, 154, 45), width=1)
    for x in range(22, w - 22, 15):
        d.line((x, h / 2, x + 7, h / 2), fill=(216, 178, 76, 155), width=1)
    for x, y, dx, dy in [(20, 20, 1, 1), (w - 20, 20, -1, 1),
                          (20, h - 20, 1, -1), (w - 20, h - 20, -1, -1)]:
        d.line((x, y + dy * 25, x, y, x + dx * 25, y), fill=(226, 192, 91, 210), width=2)
    cx, cy = w / 2, h / 2
    d.line((cx - 7, cy, cx + 7, cy), fill=(226, 192, 91, 210), width=2)
    d.line((cx, cy - 7, cx, cy + 7), fill=(226, 192, 91, 210), width=2)
    return image


def main():
    sources = sorted((OUT / "frames").glob("frame_*.png"))
    assert len(sources) == 84, "Render all 84 frames before exporting"
    fill_paths = sorted((OUT / "fill_frames").glob("frame_*.png"))
    has_fill = len(fill_paths) == len(sources)
    fill_settings = json.loads((OUT / "color-fill-settings.json").read_text()) if has_fill else {}
    nominal_fill_max = max(fill_settings.get("final_fill_alpha", {}).values(), default=0)
    if has_fill:
        backup = OUT / "outline-only"
        if not backup.exists():
            backup.mkdir()
            for name in ["guide.png", "guide_with_guides.png", "poster.png", "strip.jpg", "preview.mp4", "export-checks.json"]:
                if (OUT / name).exists():
                    shutil.copy2(OUT / name, backup / name)
    frames = []
    ghost_folder = OUT / "ghost_frames"
    ghost_folder.mkdir(exist_ok=True)
    for path in sources:
        original = Image.open(path).convert("RGBA")
        assert original.size == SIZE
        if has_fill:
            import numpy as np
            mask = np.asarray(Image.open(OUT / "fill_frames" / path.name).convert("RGBA"), dtype=np.uint16)
            fill_alpha = np.rint(mask[:, :, 0] * mask[:, :, 3] / 255).astype(np.uint8)
            assert int(fill_alpha.max()) <= round(nominal_fill_max * 2 * 255) + 1, "Fill exceeds its configured opacity"
            fill = Image.new("RGBA", SIZE, (118, 155, 178, 0))
            fill.putalpha(Image.fromarray(fill_alpha))
            original = Image.alpha_composite(fill, original)
        result = original.copy()
        result.putalpha(original.getchannel("A").point(lambda v: round(v * .5)))
        assert result.convert("RGB").tobytes() == original.convert("RGB").tobytes()
        assert result.getchannel("A").getextrema()[1] <= 128
        frames.append(result)
        result.save(ghost_folder / path.name)
    ui = guides()
    ui.save(OUT / "viewfinder.png")
    review = [Image.alpha_composite(frame, ui) for frame in frames]
    durations = [round((i + 1) * 1000 / 15) - round(i * 1000 / 15) for i in range(84)]
    for name, sequence in [("guide.png", frames), ("guide_with_guides.png", review)]:
        sequence[0].save(OUT / name, save_all=True, append_images=sequence[1:],
                         duration=durations, loop=0, disposal=0, blend=0, optimize=False)
    frames[0].save(OUT / "poster.png")
    review[0].save(OUT / "poster_with_guides.png")
    # A fixed neutral backing belongs only to the review MP4 and contact sheet.
    neutral = Image.new("RGBA", SIZE, "#f7f5ef")
    process = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "540x960", "-r", "15", "-i", "-", "-an", "-c:v", "libx264",
        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT / "preview.mp4")
    ], stdin=subprocess.PIPE)
    for frame in review:
        process.stdin.write(Image.alpha_composite(neutral, frame).convert("RGB").tobytes())
    process.stdin.close()
    assert process.wait() == 0
    selected = [0, 23, 34, 45, 60, 83]
    sheet = Image.new("RGB", (6 * 270, 510), "#f7f5ef")
    d = ImageDraw.Draw(sheet)
    for col, index in enumerate(selected):
        small = Image.alpha_composite(neutral, review[index]).convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        sheet.paste(small, (col * 270, 30))
        d.text((col * 270 + 12, 8), "%.2f s%s" % (index / 15, " | next shot" if index >= 60 else ""), fill="#526c7e")
    sheet.save(OUT / "strip.jpg", quality=94)
    checks = dict(frames=84, fps=15, duration_ms=sum(durations),
                  color_fill=has_fill, final_fill_alpha_max=nominal_fill_max,
                  size=list(SIZE), final_alpha_max=max(f.getchannel("A").getextrema()[1] for f in frames),
                  rgb_unchanged_in_alpha_pass=True, final_alpha_multiplier=.5,
                  raw_frame_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    for name in ["guide.png", "guide_with_guides.png"]:
        image = Image.open(OUT / name)
        duration = 0
        for index in range(image.n_frames):
            image.seek(index)
            duration += image.info.get("duration", 0)
        assert abs(duration - 5600) < 1, (name, duration)
        checks[name] = dict(encoded_frames=image.n_frames, duration_ms=duration)
    assert frames[0].tobytes() == frames[18].tobytes(), "Starting hold must be stable"
    assert frames[45].tobytes() == frames[59].tobytes(), "Ending hold must be stable"
    assert frames[19].tobytes() != frames[44].tobytes(), "Truck must visibly move"
    assert frames[59].tobytes() != frames[60].tobytes(), "Next-shot cut must be visible"
    checks["holds_stable"] = True
    checks["truck_visibly_moves"] = True
    checks["next_shot_cut_visible"] = True
    (OUT / "export-checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    progress = dict(message="Faint colour-fill ghost preview ready." if has_fill else "Blender proof complete: low truck, hold, then the next shot.",
                    progress="84 rendered frames, 15 fps, 5.6 seconds. Editable in scene.blend.",
                    ready=True, preview=True, lightingReady=True, revision=time.time_ns())
    (ROOT / "status.js").write_text("blenderProgress(" + json.dumps(progress) + ");\n")
    print(json.dumps({k: v for k, v in checks.items() if k != "raw_frame_sha256"}, indent=2))


if __name__ == "__main__":
    main()
