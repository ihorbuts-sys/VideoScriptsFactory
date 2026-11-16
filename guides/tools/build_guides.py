#!/usr/bin/env python3
"""Builds everything in guides/ from the catalog (catalog.py) and the scene builders (scenes.py).

    python3 build_guides.py templates            # guides/templates/*.json (new + reused, labels stripped) and guides/script_templates.json
    python3 build_guides.py render [id ...]      # schematic APNG + strip per scene into guides/overlays/schematic/
    python3 build_guides.py compile              # guides/scenarios/*.json + guides/compile_report.md, checks live steps vs heuristics
    python3 build_guides.py simulate             # simulate.py over all scenarios -> guides/simulation.md
    python3 build_guides.py jumpcheck            # frame-to-frame jump check over all APNGs -> guides/jump_check.json
    python3 build_guides.py check                # the kit's check.py over every template
    python3 build_guides.py all

Python with Pillow and NumPy is needed for render/jumpcheck/check: set GUIDES_PY to that interpreter.
"""
import glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDES = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(GUIDES, ".."))
LOCA = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
KIT = os.path.abspath(os.path.join(LOCA, "..", "VideoEditorKit"))
SHOT_OVERLAY = os.path.join(LOCA, ".claude", "skills", "shot-overlay")
LIVE_GUIDE = os.path.join(LOCA, ".claude", "skills", "live-shot-guide")
KIT_SCENES = os.path.join(KIT, "tools", "shot-overlays", "scenes")
KIT_SCENARIOS = os.path.join(KIT, "Sources", "VideoScripts", "ShotScenarios")
PY = os.environ.get("GUIDES_PY", sys.executable)

TEMPLATES_DIR = os.path.join(GUIDES, "templates")
SCHEMATIC_DIR = os.path.join(GUIDES, "overlays", "schematic")
SCENARIOS_DIR = os.path.join(GUIDES, "scenarios")

sys.path.insert(0, HERE)
import catalog  # noqa: E402
import scenes  # noqa: E402


def load(path):
    return json.load(open(path, encoding="utf-8"))


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- templates
def reused_template(gid):
    """The kit scene without labels, motion hints and glyph elements, with the kit scenario's steps pinned in `live`
    so the compiled guide stays what the kit ships today."""
    d = load(os.path.join(KIT_SCENES, gid + ".json"))
    sc = load(os.path.join(KIT_SCENARIOS, gid + ".json"))
    d["annotations"] = []
    # instruction glyphs and timed accent hint lines (eye line, light rays) go; subject actions (a cup rising,
    # glasses meeting, foam and stream of a pour, the torn pastry) stay
    def is_hint(e):
        if e.get("type") in ("arrow", "phone", "text"):
            return True
        accent = e.get("tone") == "accent" or e.get("tone_override") == "accent"
        timed = e.get("in", 0) > 0 and e.get("out") is not None
        keep = str(e.get("id", "")).startswith(("foam", "stream"))
        return e.get("type") == "path" and accent and timed and not keep
    d["elements"] = [e for e in d["elements"] if not is_hint(e)]
    for k in d["timeline"]:
        k["focus"] = None
        k["mask"] = 0
    d["end"] = {**d.get("end", {}), "return": 0}
    steps = []
    for st in sc["steps"]:
        s = {k: v for k, v in st.items() if k not in ("icon", "_t")}
        steps.append(s)
    live = dict(d.get("live", {}))
    live["camera"] = sc["camera"]
    live["anchor"] = sc["anchor"]
    live["contour"] = sc.get("contour", "box")
    live["steps"] = steps
    d["live"] = live
    return d


def write_templates():
    rows = catalog.catalog()
    groups = catalog.guides(rows)
    if os.path.isdir(TEMPLATES_DIR):
        shutil.rmtree(TEMPLATES_DIR)
    os.makedirs(TEMPLATES_DIR)
    notes = {}
    for gid, steps in sorted(groups.items()):
        r = steps[0]
        if r["reused"]:
            d = reused_template(gid)
            notes[gid] = ["reused kit scene; labels, hints and focus frame removed; steps pinned from the kit scenario"]
        else:
            d, n = scenes.make_scene(gid, r)
            notes[gid] = n
        dump(d, os.path.join(TEMPLATES_DIR, gid + ".json"))
    # overlays into a copy of the catalog
    t = load(os.path.join(ROOT, "scripts", "script_templates.json"))
    by_step = {(r["template"], r["step"]): r["guide"] for r in rows}
    for tpl in t["templates"]:
        for st in tpl["steps"]:
            st["overlays"] = [by_step[(tpl["id"], st["id"])]]
    dump(t, os.path.join(GUIDES, "script_templates.json"))
    dump(notes, os.path.join(GUIDES, "build_notes.json"))
    new = sum(1 for g in groups.values() if not g[0]["reused"])
    print(f"templates: {len(groups)} guides ({len(groups) - new} reused, {new} new) for {len(rows)} steps")
    return groups


# ---------------------------------------------------------------- render
def render(ids=None, formats="apng,strip"):
    files = [os.path.join(TEMPLATES_DIR, f"{i}.json") for i in ids] if ids else [TEMPLATES_DIR]
    os.makedirs(SCHEMATIC_DIR, exist_ok=True)
    cmd = [PY, os.path.join(SHOT_OVERLAY, "scripts", "render.py"), *files, "--out", SCHEMATIC_DIR, "--formats", formats,
           "--fps", "15", "--scale", "0.75", "--palette", "--jobs", str(max(2, (os.cpu_count() or 4) - 2))]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- compile
def compile_all():
    if os.path.isdir(SCENARIOS_DIR):
        shutil.rmtree(SCENARIOS_DIR)
    report = os.path.join(GUIDES, "compile_report.md")
    subprocess.run([PY, os.path.join(LIVE_GUIDE, "scripts", "compile_template.py"), os.path.join(TEMPLATES_DIR, "*.json"),
                    "--out", SCENARIOS_DIR, "--primitives", os.path.join(SHOT_OVERLAY, "scripts"), "--report", report],
                   check=True, stdout=subprocess.DEVNULL)
    # new scenes: compare the pinned steps with what the heuristics would have produced (actions only)
    sys.path.insert(0, os.path.join(LIVE_GUIDE, "scripts"))
    import compile_template as ct  # noqa
    sys.path.insert(0, os.path.join(SHOT_OVERLAY, "scripts"))
    import primitives as prim  # noqa
    mism = []
    for p in sorted(glob.glob(os.path.join(TEMPLATES_DIR, "*.json"))):
        d = load(p)
        live = d.pop("live")
        sc, _ = ct.build_steps(d, prim)
        auto = [(s["kind"], s.get("action"), s.get("direction")) for s in sc["steps"] if s["kind"] != "hold"]
        want = [(s["kind"], s.get("action"), s.get("direction")) for s in live["steps"] if s["kind"] != "hold"]
        auto_f = [a for a in auto if a[0] == "follow"]
        want_f = [a for a in want if a[0] == "follow"]
        if auto_f != want_f:
            mism.append((os.path.basename(p)[:-5], want_f, auto_f))
    # reused scenes: pinned steps must equal the kit scenario's steps
    kit_diff = []
    for gid, steps in catalog.guides().items():
        if steps[0]["reused"]:
            a = load(os.path.join(SCENARIOS_DIR, gid + ".json"))["steps"]
            b = load(os.path.join(KIT_SCENARIOS, gid + ".json"))["steps"]
            strip = lambda ss: [{k: v for k, v in s.items() if k not in ("icon", "_t")} for s in ss]
            if strip(a) != strip(b):
                kit_diff.append(gid)
    with open(os.path.join(GUIDES, "compile_check.md"), "w") as f:
        f.write("# Compile check\n\nPinned `live` steps against the compiler's own reading of the camera timeline "
                "(follow actions only; holds and stills are authored). A difference is not an error: the pinned list "
                "is what ships, the heuristic reading is listed so a wrong camera path shows up.\n\n")
        f.write(f"Scenes: {len(glob.glob(os.path.join(TEMPLATES_DIR, '*.json')))}, heuristic reads differently: {len(mism)}, "
                f"reused scenes whose steps differ from the kit: {len(kit_diff)}\n\n")
        for gid, want, auto in mism:
            f.write(f"- `{gid}`: pinned {want} / heuristic {auto}\n")
        for gid in kit_diff:
            f.write(f"- reused `{gid}` differs from the kit scenario\n")
    print(f"compiled {len(glob.glob(os.path.join(SCENARIOS_DIR, '*.json')))} scenarios; heuristic differs on {len(mism)}; kit diff {len(kit_diff)}")


# ---------------------------------------------------------------- simulate
def simulate():
    out = subprocess.run([PY, os.path.join(LIVE_GUIDE, "scripts", "simulate.py"), *sorted(glob.glob(os.path.join(SCENARIOS_DIR, "*.json")))],
                         capture_output=True, text=True)
    with open(os.path.join(GUIDES, "simulation.txt"), "w") as f:
        f.write(out.stdout + out.stderr)
    return out.stdout


# ---------------------------------------------------------------- jump check
def jumpcheck():
    """Frame-to-frame continuity of the drawn alpha, tolerant to motion: the share of a frame's ink that lies farther
    than about 4% of the width from any ink of the previous frame. Smooth camera moves, draw-ons and cross-fades
    stay under that; a subject that teleports or flips moves most of its ink at once. Whips (camera moves of more
    than half a frame width in under 0.6 s, read from the template), the draw-on of the first second and the final
    fade are exempt."""
    code = r'''
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageSequence
tdir, sdir, outp = sys.argv[1:4]
DS, K, LIMIT = 3, 5, 0.35          # downsample, dilation radius in downsampled px (15 px at 405 wide, 56% of the width per second), flag share
def dilate(m, k):
    out = m.copy()
    for s in range(1, k + 1):
        out[:, s:] |= m[:, :-s]; out[:, :-s] |= m[:, s:]
    m2 = out.copy()
    for s in range(1, k + 1):
        out[s:, :] |= m2[:-s, :]; out[:-s, :] |= m2[s:, :]
    return out
out = {}
for p in sorted(glob.glob(sdir + "/*.png")):
    if p.endswith("_strip.png"):
        continue
    gid = os.path.basename(p)[:-4]
    d = json.load(open(os.path.join(tdir, gid + ".json")))
    tl = sorted(d["timeline"], key=lambda k: k["t"])
    whips = []
    for a, b in zip(tl, tl[1:]):
        ra, rb = a["camera"]["target"], b["camera"]["target"]
        if b["t"] - a["t"] < 0.6 and abs(rb[0] - ra[0]) > 0.5 * ra[2]:
            whips.append((a["t"] - 0.1, b["t"] + 0.2))
    fade = d.get("end", {}).get("fade", 0.3)
    im = Image.open(p)
    fps = 15
    frames, times, clock = [], [], 0.0
    for fr in ImageSequence.Iterator(im):   # the APNG merges identical frames, so read each frame's own duration
        a = np.asarray(fr.convert("RGBA"))[..., 3].astype(np.float32)
        h, w = a.shape[0] // DS * DS, a.shape[1] // DS * DS
        frames.append(a[:h, :w].reshape(h // DS, DS, w // DS, DS).mean(axis=(1, 3)))
        times.append(clock)
        clock += fr.info.get("duration", 1000 / fps) / 1000.0
    n = len(frames)
    dur = clock
    shares = []
    for i in range(1, n):
        t = times[i]
        if t < 1.0 or t > dur - fade - 0.1 or any(w0 <= t <= w1 for w0, w1 in whips):
            continue
        prev, cur = frames[i - 1], frames[i]
        ink = cur.sum()
        if ink < 0.02 * max(f.sum() for f in frames):   # nothing in frame (after a whip out)
            continue
        covered = dilate(prev > 40, K)
        shares.append((round(t, 2), float((cur * (~covered)).sum() / ink)))
    worst = max(shares, key=lambda c: c[1]) if shares else (0, 0)
    jumps = [c for c in shares if c[1] > LIMIT]
    out[gid] = {"frames": n, "whip_windows": [[round(a, 2), round(b, 2)] for a, b in whips], "worst_uncovered_share": round(worst[1], 3),
                "worst_at": worst[0], "jumps": jumps}
json.dump(out, open(outp, "w"), indent=1)
bad = {k: v for k, v in out.items() if v["jumps"]}
print(len(out), "animations;", len(bad), "with ink moving more than 4% of the width in one frame:",
      ", ".join(f"{k}@{v['jumps'][0][0]}({v['jumps'][0][1]:.0%})" for k, v in sorted(bad.items())))
'''
    subprocess.run([PY, "-c", code, TEMPLATES_DIR, SCHEMATIC_DIR, os.path.join(GUIDES, "jump_check.json")], check=True)


def check():
    env = dict(os.environ, SHOT_OVERLAY_SCRIPTS=os.path.join(SHOT_OVERLAY, "scripts"))
    out = subprocess.run([PY, os.path.join(KIT, "tools", "shot-overlays", "check.py"), TEMPLATES_DIR], capture_output=True, text=True, env=env)
    with open(os.path.join(GUIDES, "kit_check.txt"), "w") as f:
        f.write(out.stdout + out.stderr)
    bad = [l for l in out.stdout.splitlines() if l.startswith("BAD")]
    print(f"kit check.py: {len(bad)} scenes flagged (guides/kit_check.txt)")


if __name__ == "__main__":
    if '--profile' in sys.argv and sys.argv[sys.argv.index('--profile')+1]=='p0':
        if len(sys.argv)<2 or sys.argv[1]!='check':
            raise SystemExit('P0 supports: build_guides.py check --profile p0; render native scenes with render_p0.py')
        from check_p0 import check as check_p0
        check_p0()
        raise SystemExit(0)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("templates", "all"):
        write_templates()
    if cmd == "render":
        render(sys.argv[2:] or None)
    if cmd == "all":
        render()
    if cmd in ("compile", "all"):
        compile_all()
    if cmd in ("simulate", "all"):
        print(simulate()[-2000:])
    if cmd in ("jumpcheck", "all"):
        jumpcheck()
    if cmd in ("check", "all"):
        check()
