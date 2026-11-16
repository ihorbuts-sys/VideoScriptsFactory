#!/usr/bin/env python3
"""3D style of every guide: the subject model, its size in metres, the camera path of the move, a preview strip.

    GUIDES_PY=<python with numpy+Pillow> python3 render_3d.py            # all guides
    python3 render_3d.py cup_eye_orbitr_cc ...                          # some

Per guide it writes guides/overlays/3d/<id>.json (model, size, look-at, camera keyframes at the step boundaries)
and guides/overlays/3d/<id>_strip.png (the model seen from the camera at the start, the middle and the end of
every move, drawn as a wireframe by the same pinhole camera the kit's GhostPath implies). Subjects the kit
lacks are exported once as guides/overlays/3d/models/<name>.usdz (USD primitives, metres, origin at the base
centre, y up) with their footprint and look-at point in models/index.json.
"""
import glob, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDES = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(GUIDES, "overlays", "3d")
MODELS = os.path.join(OUT, "models")
sys.path.insert(0, HERE)
import catalog  # noqa: E402

HFOV = 2 * math.atan(math.tan(math.radians(60) / 2) * 9 / 16)   # portrait: 60 degrees vertical
ELEV = {"top-down": 85, "high": 45, "eye-level": 0, "low": -12, "pov": 10, "over-shoulder": 20}
SELFIE_ELEV = {"high": 30, "eye-level": 0}
FRAME_FRAC = {"wide": 0.25, "medium": 0.5, "close": 0.95, "detail": 1.0}
SCENE_FRAC = {"wide": 0.9, "medium": 1.0, "close": 1.0, "detail": 1.0}


# ---------------------------------------------------------------- models: primitives in metres (y up, origin at the base)
def box(cx, cy, cz, w, h, d):
    return {"kind": "box", "c": [cx, cy, cz], "s": [w, h, d]}


def cyl(cx, cy, cz, r, h, axis="y"):
    return {"kind": "cylinder", "c": [cx, cy, cz], "r": r, "h": h, "axis": axis}


def sph(cx, cy, cz, r):
    return {"kind": "sphere", "c": [cx, cy, cz], "r": r}


def cone(cx, cy, cz, r, h):
    return {"kind": "cone", "c": [cx, cy, cz], "r": r, "h": h}


def line(*pts):
    return {"kind": "line", "pts": [list(p) for p in pts]}


def person(full=False):
    parts = [sph(0, 1.55, 0, 0.1), cyl(0, 1.42, 0, 0.035, 0.08), box(0, 1.22, 0, 0.44, 0.3, 0.2)]
    if full:
        parts += [box(0, 0.9, 0, 0.36, 0.4, 0.18), box(-0.09, 0.4, 0, 0.12, 0.8, 0.14), box(0.09, 0.4, 0, 0.12, 0.8, 0.14)]
    return parts


def storefront():
    p = [box(0, 1.5, 0, 4.0, 3.0, 0.3), box(0, 1.05, 0.16, 0.9, 2.1, 0.02), box(-1.3, 1.6, 0.16, 1.1, 1.2, 0.02),
         box(1.3, 1.6, 0.16, 1.1, 1.2, 0.02), box(0, 2.6, 0.17, 2.0, 0.5, 0.02), box(0, 2.2, 0.35, 1.4, 0.05, 0.5),
         sph(0.33, 1.0, 0.18, 0.03)]
    return p


def room():
    p = [box(0, 1.4, -2.5, 5.0, 2.8, 0.02), box(-2.5, 1.4, 0, 0.02, 2.8, 5.0), box(2.5, 1.4, 0, 0.02, 2.8, 5.0),
         box(0, 0.0, 0, 5.0, 0.02, 5.0), box(0, 0.72, -1.0, 1.0, 0.05, 0.8), box(-0.8, 0.45, -1.0, 0.45, 0.9, 0.45),
         box(0.8, 0.45, -1.0, 0.45, 0.9, 0.45), box(0, 1.9, -2.49, 1.2, 1.0, 0.02), cone(0, 2.3, -1.0, 0.15, 0.2),
         line((0, 2.8, -1.0), (0, 2.4, -1.0))]
    return p


MODEL = {
    "cup": dict(parts=[cyl(0, 0.04, 0, 0.04, 0.08), cyl(0, 0.003, 0, 0.07, 0.006), box(0.055, 0.045, 0, 0.02, 0.045, 0.012)],
                size=[0.13, 0.08, 0.14], look=[0, 0.04, 0], kit=True),
    "pasta": dict(parts=[cyl(0, 0.008, 0, 0.135, 0.015), sph(0.02, 0.03, 0, 0.065), line((0.1, 0.02, 0.06), (0.16, 0.02, 0.1))],
                  size=[0.27, 0.1, 0.27], look=[0, 0.03, 0], kit=True),
    "dessert": dict(parts=[cyl(0, 0.008, 0, 0.1, 0.015), box(0, 0.045, 0, 0.09, 0.06, 0.06), sph(0.03, 0.09, 0, 0.015)],
                    size=[0.2, 0.1, 0.2], look=[0, 0.04, 0], kit=True),
    "glass": dict(parts=[cyl(0, 0.075, 0, 0.035, 0.15), cyl(0, 0.14, 0, 0.036, 0.01)], size=[0.07, 0.15, 0.07], look=[0, 0.08, 0], kit=True),
    "pastry": dict(parts=[sph(0, 0.03, 0, 0.06), sph(-0.05, 0.025, 0.01, 0.04), sph(0.05, 0.025, 0.01, 0.04)],
                   size=[0.18, 0.06, 0.08], look=[0, 0.03, 0], kit=True),
    "person": dict(parts=person(), size=[0.44, 1.65, 0.2], look=[0, 1.5, 0], kit=True, frame=0.26),
    "person_full": dict(parts=person(True), size=[0.44, 1.65, 0.2], look=[0, 0.95, 0], kit=True),
    "facade": dict(parts=storefront(), size=[4.0, 3.0, 0.8], look=[0, 1.6, 0], kit=True, scene=True,
                   parts_focus={"door": ([0, 1.05, 0.16], 0.9), "sign": ([0, 2.6, 0.17], 2.0), "window": ([1.3, 1.6, 0.16], 1.1)}),
    "room": dict(parts=room(), size=[5.0, 2.8, 5.0], look=[0, 1.2, -1.0], kit=True, scene=True,
                 parts_focus={"table": ([0, 0.75, -1.0], 1.2), "window": ([0, 1.9, -2.49], 1.2)}),
    "tap": dict(parts=[box(0, 0.1, 0, 0.9, 0.04, 0.4), box(0, 0.32, 0, 0.3, 0.4, 0.15)] +
                [cyl(x, 0.45, 0.1, 0.012, 0.1, "z") for x in (-0.09, 0, 0.09)], size=[0.35, 0.55, 0.4], look=[0, 0.35, 0], kit=True),
    "oven": dict(parts=[box(0, 0.45, 0, 0.8, 0.9, 0.7), box(0, 0.5, 0.36, 0.65, 0.4, 0.02), box(0, 0.33, 0.55, 0.6, 0.02, 0.4)] +
                 [sph(x, 0.37, 0.55, 0.05) for x in (-0.18, 0, 0.18)], size=[0.8, 0.9, 1.0], look=[0, 0.45, 0.2], kit=True,
                 parts_focus={"tray": ([0, 0.36, 0.55], 0.6)}),
    "display_case": dict(parts=[box(0, 0.5, 0, 1.5, 1.0, 0.6), box(0, 0.4, 0, 1.4, 0.02, 0.55), box(0, 0.7, 0, 1.4, 0.02, 0.55)] +
                         [sph(x, y + 0.06, 0.1, 0.06) for y in (0.4, 0.7) for x in (-0.5, -0.25, 0, 0.25, 0.5)],
                         size=[1.5, 1.0, 0.6], look=[0, 0.55, 0.3], kit=True, scene=True, parts_focus={"item": ([0, 0.76, 0.1], 0.2)}),
    "menu_board": dict(parts=[box(0, 1.5, 0, 0.8, 0.6, 0.03)] + [line((-0.3, 1.7 - i * 0.1, 0.02), (0.1 + 0.05 * (i % 2), 1.7 - i * 0.1, 0.02)) for i in range(5)],
                       size=[0.8, 0.6, 0.03], look=[0, 1.5, 0], kit=True, parts_focus={"item": ([-0.1, 1.6, 0.02], 0.4)}),
    "window": dict(parts=[box(0, 1.5, 0, 3.0, 3.0, 0.2), box(0, 1.5, 0.11, 1.1, 1.2, 0.02), box(0, 0.88, 0.2, 1.3, 0.04, 0.2)],
                   size=[1.3, 1.3, 0.3], look=[0, 1.4, 0.1], kit=True),
    "plant": dict(parts=[cyl(0, 0.12, 0, 0.12, 0.24)] + [sph(0.14 * math.cos(a), 0.45, 0.14 * math.sin(a), 0.09) for a in np.linspace(0, 6.0, 6)],
                  size=[0.5, 0.6, 0.5], look=[0, 0.4, 0], kit=True),
    "lamp": dict(parts=[line((0, 0.9, 0), (0, 0.45, 0)), cone(0, 0.35, 0, 0.15, 0.2), sph(0, 0.2, 0, 0.04)], size=[0.3, 0.9, 0.3], look=[0, 0.3, 0], kit=True),
    # subjects the kit lacks: exported as usdz
    "hands_board": dict(parts=[box(0, 0.015, 0, 0.4, 0.03, 0.3), sph(-0.1, 0.07, 0.02, 0.055), sph(0.1, 0.07, 0.02, 0.055)],
                        size=[0.4, 0.12, 0.3], look=[0, 0.05, 0], kit=False),
    "card": dict(parts=[box(0, 0.002, 0, 0.1, 0.004, 0.15)] + [line((-0.035, 0.005, -0.05 + i * 0.025), (0.03, 0.005, -0.05 + i * 0.025)) for i in range(4)],
                 size=[0.1, 0.01, 0.15], look=[0, 0.0, 0], kit=False),
    "table": dict(parts=[box(0, 0.73, 0, 1.2, 0.04, 0.75)] + [box(x, 0.36, z, 0.05, 0.72, 0.05) for x in (-0.55, 0.55) for z in (-0.33, 0.33)] +
                  [cyl(0.2, 0.79, 0, 0.04, 0.08)], size=[1.2, 0.8, 0.75], look=[0, 0.75, 0], kit=False, scene=True),
    "rail": dict(parts=[cyl(0, 1.6, 0, 0.015, 2.0, "x")] + [box(-0.9 + i * 0.3, 1.2, 0, 0.22, 0.7, 0.04) for i in range(7)],
                 size=[2.0, 1.7, 0.1], look=[0, 1.25, 0], kit=False, scene=True),
    "tray": dict(parts=[box(0, 0.01, 0, 0.5, 0.02, 0.35)] + [sph(-0.17 + i * 0.115, 0.05, 0, 0.045) for i in range(4)],
                 size=[0.5, 0.1, 0.35], look=[0, 0.04, 0], kit=False),
    "burger": dict(parts=[cyl(0, 0.015, 0, 0.06, 0.03), cyl(0, 0.04, 0, 0.062, 0.02), cyl(0, 0.07, 0, 0.065, 0.04)],
                   size=[0.13, 0.09, 0.13], look=[0, 0.045, 0], kit=False),
    "box": dict(parts=[box(0, 0.05, 0, 0.3, 0.1, 0.2), box(0, 0.1, -0.12, 0.3, 0.1, 0.01)], size=[0.3, 0.2, 0.2], look=[0, 0.06, 0], kit=False),
    "garment": dict(parts=[box(0, 1.1, 0, 0.5, 0.7, 0.05), line((0, 1.45, 0), (0, 1.55, 0))], size=[0.5, 0.8, 0.05], look=[0, 1.15, 0], kit=False),
    "guitar": dict(parts=[cyl(0, 0.03, 0, 0.2, 0.06, "y"), cyl(0, 0.03, 0.22, 0.15, 0.06, "y"), box(0, 0.035, 0.55, 0.05, 0.02, 0.6)],
                   size=[0.4, 0.07, 0.9], look=[0, 0.03, 0.1], kit=False),
    "rack": dict(parts=[box(0, 0.5, 0, 2.0, 0.04, 0.4), box(0, 0.9, 0, 2.0, 0.04, 0.4)] +
                 [cyl(-0.8 + i * 0.32, y + 0.06, 0, 0.012, 0.25, "x") for y in (0.5, 0.9) for i in range(6)],
                 size=[2.0, 1.0, 0.4], look=[0, 0.7, 0], kit=False, scene=True),
    "griddle": dict(parts=[box(0, 0.02, 0, 0.8, 0.04, 0.5)] + [cyl(x, 0.055, z, 0.06, 0.02) for x, z in ((-0.25, -0.1), (0, 0.05), (0.25, -0.08), (-0.12, 0.15), (0.14, 0.17))],
                    size=[0.8, 0.08, 0.5], look=[0, 0.04, 0], kit=False),
    "machine": dict(parts=[box(0, 0.9, 0, 0.8, 1.8, 1.2), box(-0.25, 0.5, 0, 0.25, 0.8, 0.25), box(0.2, 0.5, 0.3, 0.35, 0.05, 0.35)],
                    size=[0.8, 1.8, 1.2], look=[0, 0.8, 0], kit=False),
    "hand": dict(parts=[box(0, 0.01, 0, 0.09, 0.02, 0.1)] + [cyl(-0.033 + i * 0.022, 0.01, 0.085, 0.009, 0.07, "z") for i in range(4)],
                 size=[0.1, 0.03, 0.19], look=[0, 0.01, 0.02], kit=False),
    "sign": dict(parts=storefront(), size=[4.0, 3.0, 0.8], look=[0, 2.6, 0.17], kit=True, scene=True, parts_focus={"sign": ([0, 2.6, 0.17], 2.0)}),
    "door": dict(parts=storefront(), size=[4.0, 3.0, 0.8], look=[0, 1.05, 0.16], kit=True, scene=True, parts_focus={"door": ([0, 1.05, 0.16], 0.9)}),
    "latte": dict(parts=[cyl(0, 0.04, 0, 0.04, 0.08), cyl(0, 0.003, 0, 0.07, 0.006), line((-0.015, 0.081, 0), (0, 0.081, 0.015), (0.015, 0.081, 0), (0, 0.081, -0.015))],
                  size=[0.13, 0.08, 0.14], look=[0, 0.08, 0], kit=True),
}
KIT_MODEL_FOR = {"facade": "storefront(facade)", "door": "storefront(door)", "sign": "storefront(sign)", "window": "storefront(window)",
                 "room": "room(table)", "table": "room(table)", "latte": "cup", "pasta": "pasta", "display_case": "displayCase",
                 "menu_board": "menu", "person_full": "person"}


# ---------------------------------------------------------------- wireframe edges of a primitive
def edges(p, n=18):
    k = p["kind"]
    if k == "line":
        return [p["pts"]]
    cx, cy, cz = p["c"]
    if k == "box":
        w, h, d = p["s"]
        x0, x1, y0, y1, z0, z1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, cz - d / 2, cz + d / 2
        a = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]]
        b = [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
        return [a + [a[0]], b + [b[0]]] + [[a[i], b[i]] for i in range(4)]
    if k in ("cylinder", "cone"):
        r, h, ax = p["r"], p["h"], p.get("axis", "y")
        def ring(t, rr):
            pts = []
            for i in range(n + 1):
                a = 2 * math.pi * i / n
                if ax == "y":
                    pts.append([cx + rr * math.cos(a), cy + t, cz + rr * math.sin(a)])
                elif ax == "x":
                    pts.append([cx + t, cy + rr * math.cos(a), cz + rr * math.sin(a)])
                else:
                    pts.append([cx + rr * math.cos(a), cy + rr * math.sin(a), cz + t])
            return pts
        if k == "cone":
            top = [cx, cy + h / 2, cz]
            base = ring(-h / 2, r)
            return [base] + [[base[i], top] for i in range(0, n, 4)]
        lo, hi = ring(-h / 2, r), ring(h / 2, r)
        return [lo, hi] + [[lo[i], hi[i]] for i in range(0, n, 4)]
    if k == "sphere":
        r = p["r"]
        out = []
        for lat in (-0.5, 0, 0.5):
            rr = r * math.cos(lat * math.pi / 2)
            yy = cy + r * math.sin(lat * math.pi / 2)
            out.append([[cx + rr * math.cos(2 * math.pi * i / n), yy, cz + rr * math.sin(2 * math.pi * i / n)] for i in range(n + 1)])
        for lon in (0, 0.5):
            a = lon * math.pi
            out.append([[cx + r * math.cos(a) * math.cos(t), cy + r * math.sin(t), cz + r * math.sin(a) * math.cos(t)]
                        for t in np.linspace(0, 2 * math.pi, n + 1)])
        return out
    return []


# ---------------------------------------------------------------- camera
def pose_matrix(look, dist, elev, azim, yaw=0.0, pitch=0.0, lateral=0.0):
    """Camera position on a sphere around `look`; yaw/pitch turn the camera on the spot; lateral slides it sideways."""
    e, a = math.radians(elev), math.radians(azim)
    pos = np.array([look[0] + dist * math.cos(e) * math.sin(a), look[1] + dist * math.sin(e), look[2] + dist * math.cos(e) * math.cos(a)])
    fwd = (np.array(look) - pos)
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    pos = pos + right * lateral
    # yaw right = turn the camera to the right; pitch down = negative
    y, p = math.radians(yaw), math.radians(pitch)
    fwd2 = fwd * math.cos(y) + right * math.sin(y)
    right2 = np.cross(fwd2, [0, 1, 0]); right2 /= np.linalg.norm(right2)
    up2 = np.cross(right2, fwd2)
    fwd3 = fwd2 * math.cos(p) + up2 * math.sin(p)
    up3 = np.cross(right2, fwd3)
    return pos, right2, up3, fwd3


def project(pt, cam, W, H):
    pos, right, up, fwd = cam
    v = np.array(pt) - pos
    z = float(v @ fwd)
    if z < 0.02:
        return None
    x = float(v @ right) / z
    y = float(v @ up) / z
    f = (H / 2) / math.tan(math.radians(60) / 2)
    return (W / 2 + x * f, H / 2 - y * f)


def draw_view(model, cam, W=270, H=480, subject_turn=0.0):
    img = Image.new("RGB", (W, H), (26, 26, 30))
    d = ImageDraw.Draw(img)
    # band the app keeps clear (prompter / controls)
    d.rectangle([0, 0, W, int(H * 0.295)], fill=(20, 20, 24))
    d.rectangle([0, int(H * 0.695), W, H], fill=(20, 20, 24))
    look = model["look"]
    # ground reference: a faint circle under the subject
    r = max(model["size"][0], model["size"][2]) * 0.8
    ring = [[r * math.cos(t), 0, r * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 40)]
    for poly, col in [(ring, (70, 70, 80))]:
        pts = [project(p, cam, W, H) for p in poly]
        for a, b in zip(pts, pts[1:]):
            if a and b:
                d.line([a, b], fill=col, width=1)
    ct, st = math.cos(math.radians(subject_turn)), math.sin(math.radians(subject_turn))
    def turn(p):
        x, y, z = p
        return [x * ct + z * st, y, -x * st + z * ct]
    for part in model["parts"]:
        for poly in edges(part):
            pts = [project(turn(p), cam, W, H) for p in poly]
            for a, b in zip(pts, pts[1:]):
                if a and b:
                    d.line([a, b], fill=(255, 255, 255), width=2)
    return img


# ---------------------------------------------------------------- camera path from the compiled steps
def model_for(row):
    t = row["kit_type"]
    # restaurant-weekend-brunch/pour explicitly films sauce on a plate.
    # The legacy guide id says cup, but the description and source step do not.
    if t == "cup" and row["item"] == "pour":
        return "dessert"
    if t == "person" and row["item"] in ("full", "curtain"):
        return "person_full"
    return t if t in MODEL else "box"


PERSON_DISTANCE = {"front": {"wide": 1.6, "medium": 0.65, "close": 0.4, "detail": 0.3},
                   "back": {"wide": 3.0, "medium": 1.3, "close": 0.8, "detail": 0.5}}


def start_distance(model, framing, part=None, camera="back", person=False):
    """Distance that puts the subject (or its focused part) at the framing's share of the frame width."""
    if person:
        return PERSON_DISTANCE[camera][framing]
    width = model["size"][0]
    if framing != "wide" and part and model.get("parts_focus") and part in model["parts_focus"]:
        width = model["parts_focus"][part][1]
    frac = FRAME_FRAC[framing] if not model.get("scene") else {"wide": 0.9, "medium": 0.9, "close": 1.0, "detail": 1.0}[framing]
    if framing == "detail" and not (part and model.get("parts_focus")):
        width *= 0.45
    return width / (frac * 2 * math.tan(HFOV / 2))


def name_is_person(model):
    return model is MODEL["person"] or model is MODEL["person_full"]


def camera_path(row, steps, model):
    front = row["camera"] == "front"
    elev = SELFIE_ELEV[row["angle"]] if front else ELEV[row["angle"]]
    part = None
    if model.get("parts_focus"):
        part = {"door": "door", "sign": "sign", "window": "window", "room": "table", "table": "table", "oven": "tray",
                "display_case": "item", "menu_board": "item"}.get(row["kit_type"])
    look = list(model["look"])
    if part and model.get("parts_focus") and row["start"] != "wide":
        look = list(model["parts_focus"][part][0])
    person = name_is_person(model)
    if person and row["start"] != "wide":
        look = [0, 1.5, 0]
    d0 = start_distance(model, row["start"], part, row["camera"], person)
    pose = dict(t=0.0, distance_m=round(d0, 3), elevation_deg=elev, azimuth_deg=0.0, yaw_deg=0.0, pitch_deg=0.0, lateral_m=0.0, subject_turn_deg=0.0)
    keys = [dict(pose, label="start")]
    t = 0.0
    for st in steps:
        k = st["kind"]
        if k == "frame":
            t += 1.2
            continue
        if k in ("hold", "still"):
            t += st.get("duration", 1.0)
            keys.append(dict(pose, t=round(t, 2), label=k))
            continue
        if k != "follow":
            continue
        a = st["action"]
        sgn = -1 if st.get("direction") in ("left", "up") else 1
        dur = st.get("duration", 1.0 if a == "whip" else 2.0)
        frame_w = 2 * pose["distance_m"] * math.tan(HFOV / 2)
        if a in ("dolly_in", "dolly_out"):
            amt = st.get("amount", 1.25)
            factor = math.exp(abs(math.log(max(amt, 0.01))))
            pose["distance_m"] = round(pose["distance_m"] / factor if a == "dolly_in" else pose["distance_m"] * factor, 3)
        elif a == "pan":
            pose["yaw_deg"] = round(pose["yaw_deg"] + sgn * st.get("amount", 0.5) * math.degrees(HFOV), 1)
        elif a == "truck":
            pose["lateral_m"] = round(pose["lateral_m"] + sgn * st.get("amount", 0.5) * frame_w, 3)
        elif a == "tilt":
            pose["pitch_deg"] = round(pose["pitch_deg"] - sgn * st.get("amount", 0.3) * 60, 1)
        elif a == "orbit":
            pose["azimuth_deg"] = round(pose["azimuth_deg"] + sgn * st.get("arc", 60), 1)
        elif a == "whip":
            pose["yaw_deg"] = round(pose["yaw_deg"] + sgn * 1.2 * math.degrees(HFOV), 1)
        t += dur
        keys.append(dict(pose, t=round(t, 2), label=a))
    return look, keys


def lerp_pose(a, b, u):
    out = dict(a)
    for k in ("distance_m", "elevation_deg", "azimuth_deg", "yaw_deg", "pitch_deg", "lateral_m"):
        if k == "distance_m":
            out[k] = a[k] * (b[k] / a[k]) ** u
        else:
            out[k] = a[k] + (b[k] - a[k]) * u
    return out


def render_guide(gid, row, steps):
    name = model_for(row)
    model = MODEL[name]
    look, keys = camera_path(row, steps, model)
    moves = [i for i in range(1, len(keys)) if keys[i]["label"] not in ("hold", "still")]
    frames, labels = [], []
    def view(p):
        cam = pose_matrix(look, p["distance_m"], p["elevation_deg"], p["azimuth_deg"], p["yaw_deg"], p["pitch_deg"], p["lateral_m"])
        return draw_view(model, cam)
    if not moves:
        frames = [view(keys[0]), view(keys[0]), view(keys[-1])]
        labels = ["start", "hold", "end"]
    else:
        for i in moves:
            a, b = keys[i - 1], keys[i]
            if not frames:
                frames.append(view(a)); labels.append("start")
            frames.append(view(lerp_pose(a, b, 0.5))); labels.append(b["label"] + " mid")
            frames.append(view(b)); labels.append(b["label"] + " end")
    W, H = frames[0].size
    sheet = Image.new("RGB", (len(frames) * (W + 8) + 8, H + 58), (20, 20, 22))
    d = ImageDraw.Draw(sheet)
    for i, (fr, lb) in enumerate(zip(frames, labels)):
        x = 8 + i * (W + 8)
        sheet.paste(fr, (x, 8))
        d.text((x + 4, H + 12), lb, fill=(255, 210, 74))
    p0, p1 = keys[0], keys[-1]
    d.text((8, H + 30), f"{name}  d {p0['distance_m']:.2f}->{p1['distance_m']:.2f} m  elev {p0['elevation_deg']}  az {p0['azimuth_deg']}->{p1['azimuth_deg']}  yaw {p1['yaw_deg']}  pitch {p1['pitch_deg']}  lat {p1['lateral_m']:.2f} m",
           fill=(200, 200, 200))
    sheet.save(os.path.join(OUT, gid + "_strip.png"))
    spec = {"guide": gid, "model": name, "kit_model": KIT_MODEL_FOR.get(name, name) if model.get("kit") else None,
            "usdz": None if model.get("kit") else f"models/{name}.usdz", "size_m": dict(zip(("width", "height", "depth"), model["size"])),
            "look_at_m": [round(v, 3) for v in look], "fov_vertical_deg": 60, "camera": keys,
            "subject_turns": [k["azimuth_deg"] for k in keys if k["label"] == "orbit end"] or None}
    json.dump(spec, open(os.path.join(OUT, gid + ".json"), "w"), indent=1)
    return name


# ---------------------------------------------------------------- usdz export for subjects the kit lacks
def usda(name, model):
    lines = ["#usda 1.0", "(", f'    defaultPrim = "{name}"', "    metersPerUnit = 1", '    upAxis = "Y"', ")",
             f'def Xform "{name}" (', '    kind = "component"', ")", "{"]
    for i, p in enumerate(model["parts"]):
        k = p["kind"]
        if k == "line":
            pts = ", ".join(f"({a}, {b}, {c})" for a, b, c in p["pts"])
            lines += [f'    def BasisCurves "line{i}"', "    {", '        uniform token type = "linear"',
                      f"        int[] curveVertexCounts = [{len(p['pts'])}]", f"        point3f[] points = [{pts}]", "        float[] widths = [0.004]", "    }"]
            continue
        cx, cy, cz = p["c"]
        if k == "box":
            w, h, d = p["s"]
            lines += [f'    def Cube "part{i}"', "    {", "        double size = 1", f"        double3 xformOp:translate = ({cx}, {cy}, {cz})",
                      f"        float3 xformOp:scale = ({w}, {h}, {d})", '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]', "    }"]
        elif k in ("cylinder", "cone"):
            ax = p.get("axis", "y").upper()
            lines += [f'    def {"Cylinder" if k == "cylinder" else "Cone"} "part{i}"', "    {", f"        double radius = {p['r']}", f"        double height = {p['h']}",
                      f'        token axis = "{ax}"', f"        double3 xformOp:translate = ({cx}, {cy}, {cz})", '        uniform token[] xformOpOrder = ["xformOp:translate"]', "    }"]
        elif k == "sphere":
            lines += [f'    def Sphere "part{i}"', "    {", f"        double radius = {p['r']}", f"        double3 xformOp:translate = ({cx}, {cy}, {cz})",
                      '        uniform token[] xformOpOrder = ["xformOp:translate"]', "    }"]
    lines.append("}")
    return "\n".join(lines) + "\n"


def export_models(names):
    os.makedirs(MODELS, exist_ok=True)
    index = {}
    for name in sorted(names):
        m = MODEL[name]
        if m.get("kit"):
            continue
        src = os.path.join(MODELS, name + ".usda")
        open(src, "w").write(usda(name, m))
        subprocess.run(["usdzip", os.path.join(MODELS, name + ".usdz"), src], check=True, cwd=MODELS)
        chk = subprocess.run(["usdchecker", os.path.join(MODELS, name + ".usdz")], capture_output=True, text=True)
        os.remove(src)
        index[name] = {"file": name + ".usdz", "footprint_m": {"width": m["size"][0], "depth": m["size"][2]}, "height_m": m["size"][1],
                       "look_at_m": m["look"], "origin": "base centre, y up", "usdchecker": "ok" if "Success" in chk.stdout else chk.stdout[-300:]}
    json.dump(index, open(os.path.join(MODELS, "index.json"), "w"), indent=1)
    return index


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    want = set(sys.argv[1:])
    used = set()
    n = 0
    for gid, rows in catalog.guides().items():
        if want and gid not in want:
            continue
        sc = json.load(open(os.path.join(GUIDES, "scenarios", gid + ".json")))
        used.add(render_guide(gid, rows[0], sc["steps"]))
        n += 1
    idx = export_models(used)
    print(f"3D: {n} guides, models used {sorted(used)}; usdz exported: {sorted(idx)}")
