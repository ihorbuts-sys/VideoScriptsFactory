"""Export the companion lighting video; it is not the transparent overlay."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bar_low_truckr_mm"
sources = sorted((OUT / "lit_frames").glob("frame_*.png"))
assert len(sources) == 84
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i",
                str(OUT / "lit_frames" / "frame_%04d.png"), "-an", "-c:v", "libx264",
                "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(OUT / "lighting.mp4")], check=True)
sheet = Image.new("RGB", (1620, 510), "#f7f5ef")
d = ImageDraw.Draw(sheet)
for column, frame in enumerate([1, 24, 35, 46, 61, 84]):
    image = Image.open(sources[frame - 1]).convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
    sheet.paste(image, (column * 270, 30))
    d.text((column * 270 + 12, 8), "%.2f s" % ((frame - 1) / 15), fill="#526c7e")
sheet.save(OUT / "lighting_strip.jpg", quality=94)
checks = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                   "stream=width,height,nb_frames,duration", "-of", "json", str(OUT / "lighting.mp4")]))
stream = checks["streams"][0]
assert int(stream["nb_frames"]) == 84
assert abs(float(stream["duration"]) - 5.6) < .001
(OUT / "lighting-export-checks.json").write_text(json.dumps(checks, indent=2) + "\n")
progress = dict(message="Blender proof ready: composition, ghost hierarchy and selective light cues.",
                progress="5.6 seconds at 15 fps. Two opposing place settings. Native Blender playback available.",
                ready=True, preview=True, lightingReady=True, revision=time.time_ns())
(ROOT / "status.js").write_text("blenderProgress(" + json.dumps(progress) + ");\n")
print(json.dumps(stream))
