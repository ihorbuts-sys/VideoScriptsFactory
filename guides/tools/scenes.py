#!/usr/bin/env python3
"""Scene builders for the generated live guides.

A scene is the shot-overlay JSON the kit renders and compiles: line-art elements in world units, 25% white
fills, a 9:16 camera timeline (focus null, mask 0: the app owns the viewfinder), no annotations, and a `live`
block that spells out the steps so the compiler guesses nothing. One builder per subject family draws the
world; `make_scene` frames it for the step's shot-plan entry and animates the one move plus the hand-over.

Conventions: world y down; the subject sits around (500, 500); the drawing clip hides the top 29.5% and the
bottom 30.5% of the screen, so the camera centres the subject on the screen and framings are measured against
that middle band (40% of the height, 0.711 of the width).
"""
import math, os, sys

# primitives.py is a copy of the retired shot-overlay skill's module (archive/retired-skills/shot-overlay).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primitives as P  # noqa: E402

ASPECT = 16 / 9
BAND = 0.711                     # visible band height in frame widths
STYLE = {"main": "#FFFFFF", "accent": "#FFD24A", "stroke": 2.8, "dim_alpha": 100, "halo_opacity": 0.48,
         "label_bg": "#141719", "label_bg_opacity": 0.76}
DRAWING_CLIP = [0.035, 0.295, 0.965, 0.695]
MOTION_BOUNDS = [0.2, 0.34, 0.8, 0.66]
TILT = {"top-down": (85, 10), "high": (45, 12), "eye-level": (0, 12), "low": (-12, 10), "pov": (10, 15),
        "over-shoulder": (20, 15)}
SELFIE_TILT = {"high": (30, 15), "eye-level": (0, 12)}
FRAC = {"wide": (0.55, 0.75), "medium": (0.7, 1.0), "close": (0.95, 1.6)}
SCENE_FRAC = {"wide": 1.0, "medium": 1.9, "close": 3.2}


# ---------------------------------------------------------------- world
def hull(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return [list(p) for p in lo[:-1] + up[:-1]]


class World:
    def __init__(self):
        self.elements, self.fills, self.shapes = [], [], {}
        self.n = 0

    def el(self, type_, id=None, fill=False, tone=None, **kw):
        self.n += 1
        spec = {"type": type_, "id": id or f"{type_}_{self.n}", **kw}
        if tone:
            spec["tone_override"] = tone
        spec.setdefault("in", 0)
        spec.setdefault("draw", 0.8)
        shape = P.build(spec)
        self.shapes[spec["id"]] = shape
        self.elements.append(spec)
        if fill:
            self.fill_of(spec, shape)
        return spec["id"]

    def fill_of(self, spec, shape=None, polygon=None):
        if polygon is None:
            shape = shape or self.shapes[spec["id"]]
        pts = polygon or hull([p for path in shape.paths for p in path.pts])
        if len(pts) < 3:
            return
        f = {"id": "surface_" + spec["id"], "opacity": 0.25, "in": spec.get("in", 0), "fade_in": 0.8,
             "polygons": [pts]}
        if "out" in spec:
            f["out"] = spec["out"]
        self.fills.append(f)

    def bbox(self, id):
        return P.bbox_of(self.shapes[id].paths)

    def anchor(self, id, name):
        return self.shapes[id].anchors[name]


def rect_center(b):
    return (b[0] + b[2] / 2, b[1] + b[3] / 2)


def union(*bs):
    x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
    x1 = max(b[0] + b[2] for b in bs); y1 = max(b[1] + b[3] for b in bs)
    return (x0, y0, x1 - x0, y1 - y0)


def cam(center, width):
    h = width * ASPECT
    return [round(center[0] - width / 2, 2), round(center[1] - h / 2, 2), round(width, 2), round(h, 2)]


def width_for(b, frac):
    fw, fh = frac if isinstance(frac, tuple) else (frac, frac)
    return max(b[2] / fw, b[3] / (fh * BAND))


class Subject:
    """What a builder returns: the framed thing and what the step needs around it."""
    def __init__(self, bbox, detail=None, scene_level=False, anchor=None, action=None, focus=None,
                 tilt_target=None, orbit=None, fill_center=None, whip_from=None, whip_to=None):
        self.bbox, self.detail, self.scene_level = bbox, detail or bbox, scene_level
        self.whip_from, self.whip_to = whip_from, whip_to  # a whip-in starts on whip_from; a whip between details ends on whip_to
        self.anchor = anchor or {"kind": "salient"}
        self.action = action            # subject motion word for static steps (None = plain hold)
        self.focus = focus or bbox      # what medium/close centre on for scene-level subjects
        self.tilt_target = tilt_target  # what a tilt-down ends on
        self.orbit = orbit              # f(world, t_in, t_out, azimuth_deg) adds one turned variant
        self.fill_center = fill_center  # push-through: the plain surface that fills the last frame

    def frame(self, framing):
        if framing == "detail":
            # a detail is always tighter than close, even when the part is tall (a glass's liquid)
            close_w = self.frame("close")[2]
            return cam(rect_center(self.detail), min(width_for(self.detail, 0.9), 0.65 * close_w))
        if self.scene_level:
            b = self.bbox if framing == "wide" else self.focus
            return cam(rect_center(b), width_for(self.bbox, SCENE_FRAC[framing]) if framing == "wide"
                       else width_for(b, {"medium": (0.8, 1.0), "close": (1.1, 1.6)}[framing]))
        return cam(rect_center(self.bbox), width_for(self.bbox, FRAC[framing]))


# ---------------------------------------------------------------- builders (one per family)
def b_selfie(w, item, r):
    hi = r["angle"] == "high"
    if item == "close":
        pid = w.el("person", "me", fill=True, x=380, y=330, w=240, h=300, pose="head_shoulders")
        face = w.anchor(pid, "face")
        return Subject(w.anchor(pid, "head"), detail=face, anchor={"kind": "face"})
    if item == "two":
        a = w.el("person", "me", fill=True, x=300, y=360, w=210, h=260)
        b = w.el("person", "them", fill=True, x=500, y=370, w=200, h=250)
        if hi:
            w.el("ellipse", "floor", cx=500, cy=640, rx=330, ry=40, tone="dim")
        return Subject(union(w.bbox(a), w.bbox(b)), anchor={"kind": "face"})
    pid = w.el("person", "me", fill=True, x=380, y=360, w=240, h=290)
    if hi:
        w.el("ellipse", "table", cx=500, cy=660, rx=300, ry=34, tone="dim")
    if item == "bag":
        w.el("paper_bag", "bag", fill=True, x=600, y=470, w=130, h=150, text="", **{"in": 1.0, "draw": 0.7})
        return Subject(w.bbox(pid), anchor={"kind": "face"}, action="raise the bag")
    if item in ("bite", "sip"):
        hid = w.el("hand", "hand", x=560, y=560, w=90, h=130, pose="hold", **{"in": 0.9, "draw": 0.6})
        if item == "bite":
            w.el("fork", "fork", x=585, y=440, w=30, h=150, **{"in": 0.9, "draw": 0.6})
        else:
            w.el("cup", "cup", fill=True, x=548, y=470, w=110, h=90, saucer=False, steam=False, **{"in": 0.9, "draw": 0.6})
        return Subject(w.bbox(pid), detail=w.anchor(pid, "face"), anchor={"kind": "face"},
                       action="bite" if item == "bite" else "sip")
    if item == "reveal":
        return Subject(w.bbox(pid), detail=w.anchor(pid, "face"), anchor={"kind": "face"}, action="reveal")
    return Subject(w.bbox(pid), detail=w.anchor(pid, "face"), anchor={"kind": "face"})


def b_person(w, item, r):
    if item == "full":
        pid = w.el("person", "them", fill=True, x=420, y=250, w=160, h=480, pose="full")
        w.el("path", "floor", points=[[100, 730], [900, 730]], tone="dim")
        return Subject(w.bbox(pid), anchor={"kind": "face"}, action="the move")
    if item == "group":
        ids = [w.el("person", f"p{i}", fill=(i == 1), x=240 + i * 190, y=360 + (0 if i == 1 else 30), w=200, h=300,
                    pose="waist_up") for i in range(3)]
        return Subject(union(*[w.bbox(i) for i in ids]), anchor={"kind": "face"}, action="react")
    if item == "barber":
        w.el("mirror", "mirror", x=330, y=200, w=340, h=420, tone="dim")
        pid = w.el("person", "me", fill=True, x=400, y=330, w=200, h=300, pose="head_shoulders")
        w.el("person", "barber", x=560, y=250, w=160, h=300, pose="waist_up", facing="side", tone="dim")
        return Subject(w.bbox(pid), anchor={"kind": "face"}, action="the barber lines you up")
    if item == "host":
        w.el("shelf", "shelf", x=-900, y=330, w=520, h=300, rows=2, bottles=4, tone="dim")
        pid = w.el("person", "host", fill=True, x=390, y=330, w=220, h=320, pose="waist_up")
        w.el("bar_counter", "desk", x=250, y=600, w=500, h=120, stools=0, tone="dim")
        return Subject(w.bbox(pid), anchor={"kind": "face"}, whip_from=(-900, 330, 520, 300))
    if item in ("mirror",):
        mid = w.el("mirror", "mirror", x=300, y=180, w=400, h=560)
        pid = w.el("person", "me", fill=True, x=400, y=280, w=200, h=400, pose="waist_up")
        return Subject(w.bbox(mid), detail=w.anchor(pid, "chest"), anchor={"kind": "face"}, action="turn")
    if item == "curtain":
        pid = w.el("person", "me", fill=True, x=430, y=230, w=150, h=470, pose="full")
        w.el("path", "floor", points=[[200, 700], [800, 700]], tone="dim")
        return Subject(w.bbox(pid), detail=w.anchor(pid, "chest"), anchor={"kind": "face"})
    if item == "player":
        pid = w.el("person", "player", fill=True, x=380, y=280, w=240, h=400, pose="waist_up")
        w.el("ellipse", "body", cx=520, cy=560, rx=90, ry=60)
        w.el("path", "neck", points=[[560, 530], [720, 450]])
        w.el("hand", "hand", x=470, y=480, w=60, h=90, pose="open", rotate=-30)
        return Subject(w.bbox(pid), detail=(440, 480, 160, 140), anchor={"kind": "face"}, action="play")
    if item == "process":
        pid = w.el("person", "tech", fill=True, x=350, y=300, w=300, h=360, pose="head_shoulders")
        w.el("hand", "h1", x=330, y=560, w=80, h=120, pose="open", rotate=25, **{"in": 1.2, "draw": 0.6})
        w.el("hand", "h2", x=590, y=560, w=80, h=120, pose="open", rotate=-25, **{"in": 1.2, "draw": 0.6})
        face = w.anchor(pid, "face")
        return Subject(w.bbox(pid), detail=face, anchor={"kind": "face"}, fill_center=face)
    pid = w.el("person", "them", fill=True, x=390, y=330, w=220, h=320, pose="waist_up")
    w.el("bar_counter", "counter", x=200, y=610, w=600, h=110, stools=0, tone="dim")
    return Subject(w.bbox(pid), detail=w.anchor(pid, "face"), anchor={"kind": "face"}, action="talk")


def b_over_shoulder(w, item, r):
    w.el("person", "shoulder", x=40, y=200, w=420, h=620, pose="head_shoulders", facing="side", tone="dim")
    if item == "hands":
        bid = w.el("board", "board", fill=True, x=430, y=470, w=330, h=180)
        w.el("hand", "h1", x=470, y=400, w=80, h=130, pose="open", rotate=-20)
        w.el("hand", "h2", x=640, y=400, w=80, h=130, pose="hold", rotate=20)
        w.el("knife", "knife", x=660, y=300, w=24, h=160, rotate=15, tone="dim")
        return Subject(w.bbox(bid), detail=(540, 470, 150, 110), anchor={"element": "board", "type": "board"},
                       action="hands at work")
    if item in ("counter", "machine"):
        w.el("box", "machine", x=560, y=330, w=260, h=190, radius=10, tone="dim")
        cid = w.el("cup", "cup", fill=True, x=600, y=540, w=90, h=80, saucer=False, steam=True)
        w.el("path", "stream", points=[[645, 520], [645, 548]], tone="accent", **{"in": 1.4, "draw": 0.5})
        return Subject(union(w.bbox(cid), (560, 330, 260, 190)), detail=w.anchor(cid, "cup"),
                       anchor={"element": "cup", "type": "cup"}, action="the drink is made")
    if item == "menu":
        mid = w.el("menu_board", "menu", fill=True, x=520, y=300, w=320, h=300, title="", lines=5)
        return Subject(w.bbox(mid), detail=w.anchor(mid, "item3"), anchor={"element": "menu", "type": "menu_board"},
                       action="order")
    if item == "till":
        bid = w.el("box", "till", fill=True, x=540, y=430, w=220, h=150, radius=8)
        w.el("box", "display", x=575, y=455, w=150, h=60, radius=4, tone="accent")
        w.el("hand", "h1", x=760, y=470, w=70, h=120, pose="point", rotate=-60, tone="dim")
        return Subject(w.bbox(bid), detail=(575, 455, 150, 60), anchor={"element": "till", "type": "box"},
                       action="the total comes up")
    rid = w.el("shelf", "rail", fill=True, x=480, y=300, w=420, h=320, rows=2, bottles=4)
    w.el("hand", "h1", x=560, y=380, w=70, h=120, pose="hold", rotate=-30)
    return Subject(w.bbox(rid), detail=(560, 380, 120, 120), anchor={"kind": "none", "type": "shelf"},
                   action="the pull")


def b_facade(w, item, r):
    if item == "truck":
        w.el("box", "body", fill=True, x=150, y=330, w=700, h=300, radius=12)
        w.el("box", "window", x=420, y=390, w=230, h=150, radius=6)
        w.el("awning", "awning", x=400, y=350, w=270, h=50)
        w.el("ellipse", "wheel1", cx=300, cy=650, rx=50, ry=50)
        w.el("ellipse", "wheel2", cx=720, cy=650, rx=50, ry=50)
        return Subject((150, 330, 700, 370), detail=(420, 390, 230, 150), scene_level=True,
                       focus=(400, 350, 270, 200), anchor={"kind": "none", "type": "facade"})
    fid = w.el("facade", "f", x=100, y=200, w=800, h=600, sign_text="", door_pos="center", windows=2)
    w.fill_of(w.elements[-1], polygon=[[p[0], p[1]] for p in [(100, 200), (900, 200), (900, 800), (100, 800)]])
    if item == "window":
        win = w.anchor(fid, "window2.window")
        w.el("person", "server", x=win[0] + win[2] * .2, y=win[1] + win[3] * .15, w=win[2] * .6, h=win[3] * .9,
             pose="head_shoulders", tone="dim")
        w.el("box", "ledge", x=win[0] - 20, y=win[1] + win[3], w=win[2] + 40, h=18)
        return Subject(w.bbox(fid), detail=win, scene_level=True, focus=union(win, (win[0] - 20, win[1] + win[3], win[2] + 40, 18)),
                       anchor={"kind": "none", "type": "window"}, action="order")
    if item == "line":
        for i in range(4):
            w.el("person", f"q{i}", x=720 + i * 140, y=560, w=90, h=240, pose="full", tone="dim" if i else None)
        return Subject(w.bbox(fid), scene_level=True, focus=w.anchor(fid, "door"), anchor={"kind": "none", "type": "facade"})
    door = w.anchor(fid, "door")
    return Subject(w.bbox(fid), detail=door, scene_level=True, focus=(door[0] - door[2] * .6, door[1] - door[3] * .25, door[2] * 2.2, door[3] * 1.25),
                   anchor={"kind": "none", "type": "facade"})


def b_door(w, item, r):
    if item == "curtain":
        w.el("box", "frame", x=330, y=180, w=340, h=600)
        for i in range(6):
            x = 350 + i * 52
            w.el("path", f"fold{i}", points=[[x, 200], [x + 8, 420], [x - 4, 770]], tone="dim" if i % 2 else "main")
        w.fill_of({"id": "curtain", "in": 0}, polygon=[[335, 185], [665, 185], [665, 775], [335, 775]])
        return Subject((330, 180, 340, 600), detail=(420, 380, 160, 200), scene_level=True,
                       focus=(330, 180, 340, 600), anchor={"kind": "none", "type": "door"}, fill_center=(420, 380, 160, 200))
    if item == "sauna":
        w.el("box", "wall", x=150, y=150, w=700, h=650, tone="dim")
        did = w.el("door", "door", fill=True, x=360, y=230, w=280, h=570, handle="left", glass=True)
        g = w.anchor(did, "glass")
        return Subject(w.bbox(did), detail=g, scene_level=True, focus=w.bbox(did),
                       anchor={"kind": "none", "type": "door"}, fill_center=g)
    fid = w.el("facade", "f", x=100, y=200, w=800, h=600, sign_text="", door_pos="center", windows=2)
    w.fill_of(w.elements[-1], polygon=[[100, 200], [900, 200], [900, 800], [100, 800]])
    g = w.anchor(fid, "glass")
    return Subject(w.bbox(fid), detail=g, scene_level=True, focus=w.anchor(fid, "door"),
                   anchor={"kind": "none", "type": "door"}, fill_center=g)


def b_sign(w, item, r):
    fid = w.el("facade", "f", x=100, y=200, w=800, h=600, sign_text="", door_pos="center", windows=2, tone="dim")
    sid = w.el("sign", "plate", fill=True, x=610, y=430, w=200, h=90, text="")
    return Subject(w.bbox(fid), detail=w.bbox(sid), scene_level=True, focus=w.bbox(sid), anchor={"kind": "none", "type": "sign"})


def b_menu(w, item, r):
    if item == "desk":
        w.el("bar_counter", "desk", x=150, y=480, w=700, h=160, stools=0, tone="dim")
        bid = w.el("book", "book", fill=True, x=380, y=440, w=240, h=120, open=True)
        w.el("price_tag", "card", x=640, y=470, w=90, h=60, text="")
        w.el("person", "receptionist", x=400, y=170, w=200, h=300, pose="waist_up", tone="dim")
        return Subject((150, 170, 700, 470), detail=w.bbox(bid), scene_level=True, focus=(380, 440, 350, 120),
                       anchor={"kind": "none", "type": "menu_board"})
    if item == "taps":
        mid = w.el("menu_board", "board", fill=True, x=300, y=120, w=400, h=260, title="", lines=4)
        tid = w.el("tap", "taps", fill=True, x=360, y=470, w=280, h=230, count=4)
        return Subject(w.bbox(mid), scene_level=True, focus=w.bbox(mid), tilt_target=w.bbox(tid),
                       anchor={"kind": "none", "type": "menu_board"})
    if item in ("board", "schedule") and r["move"] == "tilt-down":
        mid = w.el("menu_board", "board", fill=True, x=300, y=120, w=400, h=280, title="", lines=5)
        w.el("bar_counter", "counter", x=180, y=520, w=640, h=160, stools=0)
        w.el("cup", "cup", x=470, y=470, w=60, h=50, saucer=False, steam=False, tone="dim")
        return Subject(w.bbox(mid), scene_level=True, focus=w.bbox(mid), tilt_target=(180, 450, 640, 230),
                       anchor={"kind": "none", "type": "menu_board"})
    if r["move"] in ("truck-right", "truck-left"):
        ids = [w.el("menu_board", f"board{i}", fill=(i == 1), x=-120 + i * 430, y=300, w=400, h=280, title="", lines=5)
               for i in range(3)]
        return Subject(union(*[w.bbox(i) for i in ids]), scene_level=True, focus=w.bbox(ids[1]),
                       anchor={"kind": "none", "type": "menu_board"})
    lines = 4 if item == "score" else 5
    mid = w.el("menu_board", "board", fill=True, x=320, y=280, w=360, h=320, title="", lines=lines)
    if item == "score":
        w.el("box", "big", x=380, y=330, w=240, h=90, radius=6, tone="accent")
    item_anchor = w.anchor(mid, "item2" if item != "score" else "item1")
    if item == "score":
        item_anchor = (380, 330, 240, 90)
    return Subject(w.bbox(mid), detail=item_anchor, scene_level=False, anchor={"element": "board", "type": "menu_board"})


def b_card(w, item, r):
    top = r["angle"] == "top-down"
    if item == "receipt":
        cid = w.el("box", "receipt", fill=True, x=430, y=300, w=140, h=400, radius=4)
        for i in range(8):
            w.el("path", f"l{i}", points=[[450, 340 + i * 40], [550 if i % 3 else 510, 340 + i * 40]], tone="dim")
        w.el("path", "total", points=[[450, 660], [550, 660]], tone="accent")
        return Subject(w.bbox(cid), detail=(440, 630, 120, 60), anchor={"element": "receipt", "type": "card"})
    if item in ("tag", "label"):
        hid = w.el("hand", "hand", x=470, y=520, w=110, h=170, pose="hold", rotate=-15)
        tid = w.el("price_tag", "tag", fill=True, x=430, y=380, w=150, h=100, text="")
        w.el("path", "price", points=[[465, 430], [545, 430]], tone="accent")
        if item == "label":
            w.el("path", "l2", points=[[465, 410], [530, 410]], tone="dim")
            w.el("path", "l3", points=[[465, 450], [520, 450]], tone="dim")
        return Subject(w.bbox(tid), detail=(455, 410, 100, 40), anchor={"element": "tag", "type": "card"},
                       fill_center=(455, 410, 100, 40))
    if item == "ticket":
        hid = w.el("hand", "hand", x=440, y=540, w=120, h=180, pose="hold")
        tid = w.el("box", "ticket", fill=True, x=400, y=400, w=200, h=120, radius=6)
        w.el("path", "perf", points=[[540, 400], [540, 520]], tone="dim")
        w.el("path", "price", points=[[430, 460], [520, 460]], tone="accent")
        return Subject(w.bbox(tid), detail=(420, 440, 110, 40), anchor={"element": "ticket", "type": "card"})
    cid = w.el("book", "card", fill=True, x=330, y=330, w=340, h=260, open=True) if item == "menu" else \
        w.el("box", "card", fill=True, x=360, y=300, w=280, h=360, radius=6)
    n = 6 if item != "menu" else 0
    for i in range(n):
        w.el("path", f"l{i}", points=[[390, 350 + i * 50], [600, 350 + i * 50]], tone="dim")
        w.el("path", f"p{i}", points=[[560, 350 + i * 50], [610, 350 + i * 50]], tone="accent")
    detail = (380, 420, 240, 80) if item != "menu" else (360, 380, 140, 120)
    return Subject(w.bbox(cid), detail=detail, anchor={"element": "card", "type": "card"})


def b_room(w, item, r):
    w.el("box", "wall", x=-700, y=150, w=2400, h=560, tone="dim")
    w.el("path", "floor", points=[[-700, 710], [1700, 710]])
    w.el("path", "skirting", points=[[-700, 860], [1700, 860]], tone="dim")
    for i, x in enumerate((-520, 1180)):
        w.el("window", f"win{i}", x=x, y=230, w=300, h=300, panes=2)
    tid = w.el("table", "table", fill=True, x=400, y=600, w=200, h=90)
    w.el("chair", "c1", x=350, y=600, w=44, h=100, facing="right")
    w.el("chair", "c2", x=606, y=600, w=44, h=100, facing="left")
    for i, x in enumerate((-250, 1050)):
        w.el("table", f"t{i}", x=x, y=620, w=170, h=80, tone="dim")
        w.el("chair", f"ca{i}", x=x - 44, y=620, w=40, h=90, facing="right", tone="dim")
        w.el("chair", f"cb{i}", x=x + 174, y=620, w=40, h=90, facing="left", tone="dim")
    w.el("pendant", "lamp", x=420, y=150, w=160, h=140, count=2)
    w.el("pendant", "lamp2", x=-200, y=150, w=120, h=120, count=1, tone="dim")
    w.el("pendant", "lamp3", x=1080, y=150, w=120, h=120, count=1, tone="dim")
    focus = w.bbox(tid)
    if item in ("crowd", "stage", "park", "game"):
        for i in range(7):
            w.el("person", f"p{i}", x=-400 + i * 290, y=430 + (i % 2) * 40, w=120, h=260, pose="full", tone="dim" if i % 2 else None)
    if item == "stage":
        w.el("box", "stage", fill=True, x=200, y=560, w=600, h=50)
        for i in range(3):
            w.el("person", f"m{i}", x=300 + i * 160, y=330, w=100, h=240, pose="full")
        focus = (200, 330, 600, 280)
    if item in ("gym", "shop"):
        for i in range(5):
            w.el("shelf", f"s{i}", x=-600 + i * 480, y=330, w=300, h=280, rows=2, bottles=4, tone="dim" if i != 2 else None)
    if item == "sauna":
        for i in range(2):
            w.el("box", f"bench{i}", x=-300, y=520 + i * 120, w=1600, h=40)
        w.el("pendant", "bulb", x=470, y=150, w=60, h=100, count=1)
    if item == "lights":
        w.el("box", "counter", x=-100, y=560, w=360, h=150, tone="dim")
        w.el("pendant", "lamp4", x=760, y=150, w=160, h=140, count=2)
    if item == "ride":
        w.el("path", "rail1", points=[[-100, 900], [430, 560]], tone="accent")
        w.el("path", "rail2", points=[[1100, 900], [570, 560]], tone="accent")
    if item == "changing":
        w.el("door", "door", x=700, y=330, w=220, h=440, handle="left", glass=False)
        focus = (700, 330, 220, 440)
    if item in ("lesson", "waiting", "treatment"):
        w.el("plant", "plant", x=120, y=460, w=130, h=250)
        if item == "treatment":
            w.el("box", "bed", fill=True, x=380, y=560, w=280, h=60, radius=8)
    anchor = {"kind": "none", "type": "room"}
    action = {"crowd": "the room", "lights": "lights on", "stage": "the band plays", "game": "the game"}.get(item)
    return Subject((-200, 150, 1400, 710), scene_level=True, focus=focus, anchor=anchor, action=action)


def b_table(w, item, r):
    tid = w.el("table", "table", fill=True, x=250, y=540, w=500, h=160)
    if item == "desk":
        w.el("book", "laptop", x=380, y=470, w=200, h=90, open=True)
        cid = w.el("cup", "cup", fill=True, x=620, y=490, w=70, h=60, saucer=True, steam=True)
        return Subject((250, 400, 500, 300), detail=union(w.bbox(cid), (380, 470, 200, 90)), scene_level=True,
                       focus=(370, 460, 330, 110), anchor={"kind": "none", "type": "table"})
    if item == "corner":
        w.el("window", "window", x=560, y=180, w=260, h=330)
        w.el("chair", "chair", x=220, y=500, w=70, h=200, facing="right")
        cid = w.el("cup", "cup", fill=True, x=470, y=490, w=70, h=60, saucer=True, steam=True)
        w.el("plant", "plant", x=120, y=330, w=90, h=180, tone="dim")
        return Subject((100, 180, 760, 540), detail=w.bbox(cid), scene_level=True, focus=(440, 470, 130, 100),
                       anchor={"kind": "none", "type": "table"})
    if item == "outlets":
        w.el("box", "outlet", fill=True, x=470, y=760, w=70, h=70, radius=8)
        w.el("ellipse", "hole1", cx=490, cy=795, rx=6, ry=10, tone="accent")
        w.el("ellipse", "hole2", cx=520, cy=795, rx=6, ry=10, tone="accent")
        cid = w.el("cup", "cup", x=600, y=490, w=70, h=60, saucer=True, steam=False, tone="dim")
        return Subject((250, 460, 500, 240), detail=(470, 760, 70, 70), scene_level=True, focus=(300, 470, 400, 220),
                       tilt_target=(400, 700, 220, 180), anchor={"kind": "none", "type": "table"})
    if item == "seat":
        w.el("chair", "c1", x=190, y=520, w=60, h=180, facing="right")
        w.el("chair", "c2", x=750, y=520, w=60, h=180, facing="left")
        w.el("window", "window", x=330, y=200, w=340, h=280, tone="dim")
        w.el("glass", "glass", x=460, y=460, w=40, h=90, kind="wine", garnish=False)
        return Subject((190, 200, 620, 500), detail=(400, 440, 200, 120), scene_level=True, focus=(300, 440, 400, 200),
                       anchor={"kind": "none", "type": "table"})
    if item == "bench":
        w.el("box", "vice", x=330, y=470, w=90, h=80, radius=6)
        w.el("brush", "tool", x=470, y=500, w=140, h=40, kind="comb")
        w.el("hand", "hand", x=640, y=430, w=70, h=120, pose="hold")
        w.el("shelf", "shelf", x=200, y=200, w=600, h=240, rows=2, bottles=6, tone="dim")
        return Subject((200, 200, 600, 500), detail=(440, 440, 220, 110), scene_level=True, focus=(300, 430, 400, 200),
                       anchor={"kind": "none", "type": "table"})
    bid = w.el("box", "bed", fill=True, x=300, y=470, w=400, h=70, radius=10)
    w.el("ellipse", "pillow", cx=360, cy=478, rx=50, ry=14)
    w.el("path", "towel", points=[[430, 500], [660, 500]], tone="accent")
    w.el("path", "legs", points=[[320, 540], [320, 600], [680, 600], [680, 540]], tone="dim")
    w.el("box", "cabinet", x=740, y=380, w=120, h=200, tone="dim")
    w.el("plant", "plant", x=130, y=380, w=90, h=180, tone="dim")
    return Subject((130, 380, 730, 320), detail=(400, 470, 220, 110), scene_level=True, focus=(300, 440, 400, 200),
                   anchor={"kind": "none", "type": "table"})


def b_bar(w, item, r):
    bid = w.el("bar_counter", "bar", fill=True, x=-200, y=560, w=1400, h=180, stools=0)
    w.el("tap", "taps", x=560, y=330, w=200, h=230, count=3)
    for i in range(5):
        w.el("glass", f"g{i}", x=-100 + i * 260, y=470, w=50, h=100, kind="tumbler", garnish=False, tone="dim" if i % 2 else None)
    w.el("shelf", "shelf", x=-200, y=120, w=1400, h=200, rows=2, bottles=14, tone="dim")
    return Subject((-200, 120, 1400, 620), scene_level=True, focus=(200, 330, 600, 400), anchor={"kind": "none", "type": "bar_counter"})


def b_case(w, item, r):
    cid = w.el("display_case", "case", fill=True, x=50, y=380, w=1100, h=420, rows=2, items=6)
    for i in range(1, 13):
        b = w.anchor(cid, f"item{i}")
        w.el("bread", f"p{i}", x=b[0] + b[2] * .1, y=b[1] + b[3] * .15, w=b[2] * .8, h=b[3] * .85, kind="croissant",
             tone=None if i == 3 else "dim")
    it = w.anchor(cid, "item3")
    return Subject(w.bbox(cid), detail=it, scene_level=True, focus=union(w.anchor(cid, "item2"), w.anchor(cid, "item4")),
                   anchor={"kind": "none", "type": "display_case"}, fill_center=it)


def b_rail(w, item, r):
    if item == "garment":
        w.el("path", "rail", points=[[-300, 330], [1300, 330]])
        for i in range(9):
            x = -220 + i * 180
            w.el("path", f"hook{i}", points=[[x + 40, 330], [x + 40, 355]], tone="dim")
            w.el("path", f"g{i}", points=[[x + 40, 355], [x - 10, 400], [x - 10, 620], [x + 90, 620], [x + 90, 400], [x + 40, 355]],
                 tone="main" if i == 4 else "dim")
        w.fill_of({"id": "g4", "in": 0}, polygon=[[510, 355], [460, 400], [460, 620], [560, 620], [560, 400]])
        return Subject((-230, 330, 1540, 290), scene_level=True, focus=(420, 340, 220, 280), anchor={"kind": "none", "type": "shelf"})
    if item == "dumbbell":
        w.el("shelf", "rack", fill=True, x=-300, y=380, w=1600, h=280, rows=2, bottles=0)
        for row in range(2):
            for i in range(8):
                x = -220 + i * 200
                y = 470 + row * 120
                w.el("path", f"bar{row}{i}", points=[[x, y], [x + 80, y]])
                w.el("ellipse", f"wa{row}{i}", cx=x, cy=y, rx=14, ry=26, tone="dim")
                w.el("ellipse", f"wb{row}{i}", cx=x + 80, cy=y, rx=14, ry=26, tone="dim")
        return Subject((-300, 380, 1600, 280), scene_level=True, focus=(380, 420, 240, 180), anchor={"kind": "none", "type": "shelf"})
    if item == "guitar":
        for i in range(7):
            x = -220 + i * 200
            w.el("ellipse", f"body{i}", cx=x + 60, cy=560, rx=70, ry=55, tone="main" if i == 3 else "dim")
            w.el("ellipse", f"waist{i}", cx=x + 60, cy=470, rx=50, ry=40, tone="main" if i == 3 else "dim")
            w.el("path", f"neck{i}", points=[[x + 60, 440], [x + 60, 240]], tone="main" if i == 3 else "dim")
        w.fill_of({"id": "body3", "in": 0}, polygon=hull(P.arc(440, 560, 70, 55).pts))
        return Subject((-230, 240, 1560, 380), scene_level=True, focus=(360, 240, 200, 380), anchor={"kind": "none", "type": "shelf"})
    sid = w.el("shelf", "shelf", fill=True, x=-300, y=330, w=1600, h=320, rows=3, bottles=16)
    return Subject(w.bbox(sid), scene_level=True, focus=(380, 340, 260, 300), anchor={"kind": "none", "type": "shelf"})


def b_oven(w, item, r):
    oid = w.el("oven", "oven", x=250, y=250, w=500, h=480, open=True)
    tid = w.el("tray", "tray", fill=True, x=300, y=560, w=400, h=70, items="buns", count=4)
    w.el("hand", "glove", x=250, y=600, w=80, h=120, pose="hold", rotate=90, tone="dim", **{"in": 1.0, "draw": 0.6})
    items = w.anchor(tid, "items")
    return Subject(w.bbox(oid), detail=items, scene_level=True, focus=w.bbox(tid),
                   anchor={"element": "tray", "type": "oven"}, action="the tray comes out", fill_center=items)


def b_tray(w, item, r):
    tid = w.el("tray", "tray", fill=True, x=250, y=470, w=500, h=90, items="croissants", count=5)
    w.el("ellipse", "shelf", cx=500, cy=560, rx=400, ry=60, tone="dim")
    w.el("hand", "tongs", x=620, y=330, w=70, h=130, pose="hold", rotate=160, tone="dim", **{"in": 1.2, "draw": 0.6})
    return Subject(w.bbox(tid), detail=w.anchor(tid, "items"), anchor={"element": "tray", "type": "pastry"})


def b_pastry(w, item, r):
    bid = w.el("bread", "pastry", fill=True, x=300, y=430, w=400, h=180, kind="croissant", torn=False)
    w.el("ellipse", "counter", cx=500, cy=620, rx=380, ry=36, tone="dim")
    for i, (x, y) in enumerate(((470, 480), (500, 500), (530, 475))):
        w.el("path", f"crumb{i}", points=[[x, y], [x + 8, y - 24], [x - 4, y - 40]], tone="accent", **{"in": 1.6 + i * 0.2, "draw": 0.5})
    return Subject(w.bbox(bid), detail=w.anchor(bid, "crumb"), anchor={"element": "pastry", "type": "pastry"}, action="tear it open")


def cup_variant(w, t_in, t_out, az, cx=500, cy=520, cw=240, ch=200):
    """A cup seen from azimuth `az` (0 = handle on the right, 90 = handle facing the lens)."""
    a = math.radians(az)
    tag = f"{int(az)}"
    ex = {"in": t_in, "draw": 0.25}
    if t_out is not None:
        ex["out"] = t_out
    body = [[cx - cw * .5, cy - ch * .5], [cx + cw * .5, cy - ch * .5], [cx + cw * .38, cy + ch * .5], [cx - cw * .38, cy + ch * .5]]
    w.el("path", f"body{tag}", points=body + [body[0]], **ex)
    w.el("ellipse", f"rim{tag}", cx=cx, cy=cy - ch * .5, rx=cw * .5, ry=ch * .12, **ex)
    hx = cx + cw * .62 * math.cos(a)
    rx = cw * .2 * max(abs(math.cos(a)), 0.18)
    w.el("ellipse", f"handle{tag}", cx=hx, cy=cy, rx=rx, ry=ch * .26, tone="main" if math.cos(a) > -0.2 else "dim", **ex)
    w.el("ellipse", f"saucer{tag}", cx=cx, cy=cy + ch * .5, rx=cw * .78, ry=ch * .13, tone="dim", **ex)
    if t_in == 0:
        w.fill_of({"id": f"body{tag}", "in": 0}, polygon=body)


def b_cup(w, item, r):
    if r["move"].startswith("orbit"):
        def orbit(world, t_in, t_out, az):
            cup_variant(world, t_in, t_out, az)
        cup_variant(w, 0, None, 0)  # placeholder removed by make_scene (variants replace it)
        w.elements, w.fills = [], []
        return Subject((380, 400, 240, 260), anchor={"kind": "salient", "type": "cup"}, orbit=orbit)
    if item == "pour":
        cid = w.el("cup", "cup", fill=True, x=420, y=500, w=160, h=130, saucer=True, steam=False)
        w.el("box", "pot", x=560, y=300, w=170, h=150, radius=12, rotate=-25)
        w.el("path", "stream", points=[[560, 420], [520, 500]], tone="accent", **{"in": 1.3, "draw": 0.6})
        return Subject(union(w.bbox(cid), (520, 280, 230, 180)), detail=w.anchor(cid, "rim"), anchor={"element": "cup", "type": "cup"}, action="pour")
    if item == "shot":
        w.el("box", "machine", x=330, y=240, w=340, h=200, radius=10, tone="dim")
        w.el("box", "spout", x=480, y=430, w=40, h=40)
        cid = w.el("cup", "cup", fill=True, x=440, y=520, w=120, h=100, saucer=True, steam=False)
        w.el("path", "stream", points=[[500, 470], [500, 525]], tone="accent", **{"in": 1.2, "draw": 0.5})
        rim = w.anchor(cid, "rim")
        return Subject(union(w.bbox(cid), (330, 240, 340, 220)), detail=rim, anchor={"element": "cup", "type": "cup"}, action="the shot pulls", fill_center=rim)
    if r["angle"] == "high":
        w.el("ellipse", "rim", cx=500, cy=470, rx=130, ry=60)
        w.el("ellipse", "crema", cx=500, cy=470, rx=108, ry=48, tone="accent")
        w.el("path", "body", points=[[370, 470], [390, 600], [610, 600], [630, 470]])
        w.fill_of({"id": "rim", "in": 0}, polygon=hull(P.arc(500, 470, 130, 60).pts + [(390, 600), (610, 600)]))
        w.el("ellipse", "saucer", cx=500, cy=600, rx=220, ry=70, tone="dim")
        w.el("bar_counter", "counter", x=-100, y=640, w=1200, h=140, stools=0, tone="dim")
        return Subject((280, 410, 440, 260), detail=(392, 422, 216, 96), anchor={"element": "rim", "type": "cup"})
    cid = w.el("cup", "cup", fill=True, x=400, y=470, w=200, h=160, saucer=True, steam=True)
    return Subject(w.anchor(cid, "cup"), detail=w.anchor(cid, "rim"), anchor={"element": "cup", "type": "cup"}, action="steam rises")


def b_latte(w, item, r):
    lid = w.el("latte", "latte", fill=True, cx=500, cy=500, r=150, art="heart")
    w.el("path", "stream", points=[[560, 300], [515, 470]], tone="accent", **{"in": 1.2, "draw": 0.6})
    return Subject(w.anchor(lid, "latte"), detail=w.anchor(lid, "art"), anchor={"element": "latte", "type": "latte"}, action="pour")


def b_glass(w, item, r):
    if item == "flight":
        w.el("board", "paddle", x=-200, y=560, w=1400, h=60)
        ids = [w.el("glass", f"g{i}", fill=(i == 2), x=-120 + i * 260, y=430, w=90, h=150, kind="tumbler", garnish=False) for i in range(6)]
        return Subject((-200, 430, 1400, 190), scene_level=True, focus=w.bbox(ids[2]), anchor={"kind": "none", "type": "glass"})
    if item == "outro":
        gid = w.el("glass", "glass", fill=True, x=430, y=400, w=140, h=260, kind="tumbler", garnish=False)
        w.el("bar_counter", "bar", x=-100, y=640, w=1200, h=150, stools=0, tone="dim")
        w.el("tap", "taps", x=640, y=300, w=180, h=250, count=3, tone="dim")
        return Subject(union(w.bbox(gid), (-100, 300, 1200, 490)), detail=w.anchor(gid, "liquid"), scene_level=True, focus=(300, 300, 520, 400),
                       anchor={"element": "glass", "type": "glass"})
    kind = {"drink": "tumbler", "glass": "highball", "favorite": "cocktail", "build": "highball", "pour": "highball"}.get(item, "highball")
    gid = w.el("glass", "glass", fill=True, x=410, y=330, w=180, h=360, kind=kind, garnish=item in ("favorite", "build"))
    if item in ("pour", "build"):
        w.el("path", "stream", points=[[500, 260], [500, 400]], tone="accent", **{"in": 1.2, "draw": 0.6})
        if r["angle"] == "low":
            w.el("ellipse", "foam", cx=500, cy=372, rx=84, ry=18, tone="accent", **{"in": 1.8, "draw": 0.5})
    if item == "glass":
        w.el("ellipse", "coaster", cx=500, cy=700, rx=130, ry=30, tone="dim")
    if r["angle"] == "high":
        w.el("ellipse", "counter", cx=500, cy=690, rx=380, ry=50, tone="dim")
    detail = w.anchor(gid, "garnish") if item == "favorite" else w.anchor(gid, "liquid")
    sub = Subject(w.anchor(gid, "glass"), detail=detail, anchor={"element": "glass", "type": "glass"},
                  action={"pour": "pour", "build": "build the drink", "drink": None, "glass": None}.get(item), fill_center=w.anchor(gid, "liquid"))
    if item == "glass":
        sub.tilt_target = (370, 600, 260, 130)
    return sub


def b_tap(w, item, r):
    return b_menu(w, "taps", r)


def plate_variant(w, t_in, t_out, az, cx=500, cy=520, R=230, high=True):
    ry = 0.45 if high else 1.0
    tag = f"{int(az)}"
    ex = {"in": t_in, "draw": 0.25}
    if t_out is not None:
        ex["out"] = t_out
    a = math.radians(az)
    def pt(rr, th):
        return [cx + rr * math.cos(th + a), cy + ry * rr * math.sin(th + a)]
    w.el("path", "food" + tag, points=[pt(R * .55 * (1 + .12 * math.sin(3 * k)), 2 * math.pi * k / 24) for k in range(25)], **ex)
    w.el("path", "fork" + tag, points=[pt(R * 1.25, -0.9), pt(R * .6, -0.9)], tone="dim", **ex)
    for j, th in enumerate((0.4, 1.6, 2.9)):
        q = pt(R * .35, th)
        w.el("ellipse", f"garnish{tag}_{j}", cx=q[0], cy=q[1], rx=10, ry=10 * ry, tone="accent", **ex)


def b_plate(w, item, r):
    top = r["angle"] == "top-down"
    low = r["angle"] == "low"
    if r["move"].startswith("orbit"):
        w.el("ellipse", "plate", cx=500, cy=520, rx=230, ry=104)
        w.fill_of({"id": "plate", "in": 0}, polygon=hull(P.arc(500, 520, 230, 104).pts))
        w.el("ellipse", "table", cx=500, cy=560, rx=420, ry=150, tone="dim")
        def orbit(world, t_in, t_out, az):
            plate_variant(world, t_in, t_out, az)
        return Subject((270, 416, 460, 208), anchor={"element": "plate", "type": "pasta"}, orbit=orbit)
    if item == "spread":
        if r["angle"] == "eye-level":
            ids = []
            for i, (x, wdt) in enumerate(((120, 200), (380, 260), (700, 200))):
                ids.append(w.el("ellipse", f"p{i}", cx=x + wdt / 2, cy=560, rx=wdt / 2, ry=18, tone="main" if i == 1 else "dim"))
                w.el("path", f"food{i}", points=[[x + 20, 556], [x + wdt * .3, 500], [x + wdt * .7, 495], [x + wdt - 20, 556]], tone="main" if i == 1 else "dim")
            w.fill_of({"id": "p1", "in": 0}, polygon=hull(P.arc(510, 560, 130, 18).pts + [(458, 500), (562, 495)]))
            w.el("path", "table", points=[[-100, 580], [1100, 580]], tone="dim")
            return Subject((100, 480, 820, 110), detail=(430, 495, 170, 70), scene_level=True, focus=(380, 495, 260, 80),
                           anchor={"kind": "none", "type": "pasta"}, action="how it works")
        pid = w.el("plate", "plate", fill=True, cx=500, cy=500, r=150, dish="pasta", cutlery=True)
        for (x, y, rr, d) in ((200, 360, 95, "salad"), (820, 400, 100, "steak"), (260, 700, 80, "dessert"), (790, 690, 90, "none")):
            w.el("plate", f"p{x}", cx=x, cy=y, r=rr, dish=d, cutlery=False, tone="dim")
        w.el("glass", "glass", x=620, y=240, w=50, h=60, kind="tumbler", garnish=False, tone="dim")
        return Subject((80, 220, 860, 580), detail=w.anchor(pid, "food"), scene_level=True, focus=w.anchor(pid, "plate"),
                       anchor={"element": "plate", "type": "pasta"})
    if top:
        dish = {"kids": "salad", "bite": "none"}.get(item, "pasta")
        pid = w.el("plate", "plate", fill=True, cx=500, cy=500, r=170, dish=dish, cutlery=True)
        if item == "bite":
            w.el("ellipse", "glass", cx=760, cy=430, rx=55, ry=55)
            w.el("ellipse", "beer", cx=760, cy=430, rx=42, ry=42, tone="accent")
            w.el("ellipse", "snack", cx=500, cy=500, rx=90, ry=60, tone="main")
        return Subject(w.anchor(pid, "plate"), detail=w.anchor(pid, "food"), anchor={"element": "plate", "type": "pasta"},
                       action="hands in" if item == "kids" else None)
    if low or r["angle"] == "eye-level":
        w.el("ellipse", "rim", cx=500, cy=600, rx=260, ry=44)
        w.el("path", "food", points=[[330, 592], [380, 520], [470, 480], [560, 490], [640, 540], [670, 592]])
        w.fill_of({"id": "rim", "in": 0}, polygon=hull(P.arc(500, 600, 260, 44).pts + [(380, 520), (470, 480), (560, 490), (640, 540)]))
        if item == "sizzle":
            for i in range(3):
                w.el("path", f"steam{i}", points=[[440 + i * 50, 480], [430 + i * 50, 420], [445 + i * 50, 360]], tone="dim", **{"in": 1.2 + i * .2, "draw": 0.7})
        w.el("path", "table", points=[[-100, 650], [1100, 650]], tone="dim")
        w.el("glass", "glass", x=790, y=430, w=70, h=170, kind="wine", garnish=False, tone="dim")
        return Subject((240, 480, 520, 164), detail=(430, 480, 160, 80), anchor={"element": "rim", "type": "pasta"},
                       fill_center=(430, 490, 160, 70), action="sizzle" if item == "sizzle" else None)
    w.el("ellipse", "rim", cx=500, cy=520, rx=240, ry=120)
    w.fill_of({"id": "rim", "in": 0}, polygon=hull(P.arc(500, 520, 240, 120).pts))
    if item == "yolk":
        w.el("ellipse", "egg", cx=470, cy=500, rx=110, ry=60)
        w.el("ellipse", "yolk", cx=480, cy=500, rx=40, ry=24, tone="accent")
        w.el("knife", "knife", x=560, y=380, w=20, h=150, rotate=30, tone="dim", **{"in": 1.4, "draw": 0.6})
        return Subject((260, 400, 480, 240), detail=(430, 470, 100, 60), anchor={"element": "rim", "type": "pasta"})
    plate_variant(w, 0, None, 0)
    return Subject((260, 400, 480, 240), detail=(400, 470, 200, 100), anchor={"element": "rim", "type": "pasta"})


def b_burger(w, item, r):
    if item == "cut":
        w.el("path", "bun_top", points=P.arc(500, 470, 170, 70, 180, 360).pts)
        layers = [(400, 20, "accent"), (430, 26, "main"), (470, 22, "accent"), (500, 20, "dim")]
        for i, (y, h, tone) in enumerate(layers):
            w.el("box", f"layer{i}", x=330, y=y + 70, w=340, h=h, tone=tone)
        w.el("box", "bun_bot", x=330, y=590, w=340, h=40, radius=16)
        w.fill_of({"id": "bun_top", "in": 0}, polygon=[[330, 630], [330, 470], [500, 400], [670, 470], [670, 630]])
        w.el("hand", "hand", x=640, y=560, w=90, h=150, pose="hold", rotate=-20, tone="dim")
        return Subject((330, 400, 340, 230), detail=(360, 465, 280, 100), anchor={"element": "bun_top", "type": "burger"},
                       fill_center=(380, 470, 240, 90))
    w.el("path", "bun_top", points=P.arc(500, 480, 190, 90, 180, 360).pts + [(690, 480), (310, 480)])
    w.el("box", "lettuce", x=300, y=485, w=400, h=22, tone="accent")
    w.el("box", "patty", x=320, y=512, w=360, h=34)
    w.el("box", "cheese", x=310, y=550, w=380, h=16, tone="accent")
    w.el("box", "bun_bot", x=320, y=570, w=360, h=50, radius=20)
    w.fill_of({"id": "bun_top", "in": 0}, polygon=[[310, 620], [310, 480], [500, 390], [690, 480], [690, 620]])
    w.el("path", "table", points=[[-100, 640], [1100, 640]], tone="dim")
    if item == "burger" and r["start"] == "medium":
        w.el("hand", "hand", x=560, y=620, w=120, h=170, pose="hold", rotate=-15, tone="dim")
    return Subject((310, 390, 380, 230), detail=(360, 480, 280, 100), anchor={"element": "bun_top", "type": "burger"})


def b_topdown(w, item, r):
    if item == "box":
        bid = w.el("box", "box", fill=True, x=300, y=330, w=400, h=340, radius=10)
        for i, (x, y) in enumerate(((380, 400), (560, 410), (380, 560), (560, 570))):
            w.el("bread", f"p{i}", x=x, y=y, w=110, h=70, kind="croissant")
        w.el("hand", "hand", x=640, y=600, w=90, h=150, pose="hold", rotate=-40, **{"in": 1.2, "draw": 0.6})
        return Subject(w.bbox(bid), detail=(370, 390, 240, 180), anchor={"element": "box", "type": "box"}, action="fill the box")
    if item == "bag":
        w.el("box", "towel", fill=True, x=300, y=360, w=260, h=300, radius=6)
        w.el("bottle", "bottle", x=600, y=360, w=70, h=200)
        w.el("ellipse", "flip1", cx=630, cy=630, rx=28, ry=55, tone="dim")
        w.el("ellipse", "flip2", cx=700, cy=630, rx=28, ry=55, tone="dim")
        return Subject((300, 360, 430, 330), anchor={"element": "towel", "type": "box"})
    if item == "haul":
        w.el("paper_bag", "bag", fill=True, x=380, y=330, w=240, h=300, text="")
        for i, (x, y, rot) in enumerate(((160, 420, -15), (680, 440, 12), (300, 700, 5), (620, 690, -8))):
            w.el("box", f"g{i}", x=x, y=y, w=180, h=120, radius=8, rotate=rot, tone="dim")
        return Subject((160, 330, 700, 490), detail=(400, 350, 200, 160), scene_level=True, focus=(380, 330, 240, 300),
                       anchor={"element": "bag", "type": "box"})
    if item == "kidstuff":
        w.el("ellipse", "cup", cx=400, cy=480, rx=50, ry=30)
        w.el("ellipse", "lid", cx=400, cy=470, rx=36, ry=20, tone="accent")
        for i in range(4):
            w.el("box", f"crayon{i}", x=520 + i * 34, y=430, w=16, h=140, rotate=10 * (i - 1.5), tone="accent" if i % 2 else "main")
        w.el("box", "paper", fill=True, x=330, y=560, w=340, h=160, radius=4)
        w.el("ellipse", "table", cx=500, cy=580, rx=380, ry=200, tone="dim")
        return Subject((330, 420, 340, 300), detail=(500, 420, 180, 160), anchor={"element": "paper", "type": "box"})
    if item == "first":
        pid = w.el("plate", "plate", fill=True, cx=480, cy=500, r=160, dish="salad", cutlery=False)
        w.el("price_tag", "tag", x=660, y=380, w=110, h=70, text="")
        w.el("path", "price", points=[[685, 415], [745, 415]], tone="accent")
        return Subject(w.anchor(pid, "plate"), detail=w.anchor(pid, "food"), anchor={"element": "plate", "type": "pasta"})
    w.el("box", "wrap", fill=True, x=310, y=380, w=380, h=260, radius=30)
    w.el("path", "fold1", points=[[310, 510], [500, 400], [690, 510]], tone="dim")
    w.el("path", "bun", points=P.arc(500, 520, 120, 50, 180, 360).pts, tone="accent", **{"in": 1.2, "draw": 0.6})
    w.el("hand", "h1", x=240, y=560, w=90, h=160, pose="open", rotate=60, tone="dim")
    w.el("hand", "h2", x=680, y=560, w=90, h=160, pose="open", rotate=-60, tone="dim")
    return Subject((310, 380, 380, 260), detail=(390, 470, 220, 90), anchor={"element": "wrap", "type": "box"}, action="unwrap")


def b_hands(w, item, r):
    high = r["angle"] == "high"
    if item == "griddle":
        w.el("box", "griddle", fill=True, x=200, y=380, w=600, h=300, radius=8)
        for i, (x, y) in enumerate(((330, 460), (490, 450), (640, 470), (420, 590), (590, 600))):
            w.el("ellipse", f"patty{i}", cx=x, cy=y, rx=60, ry=38 if high else 50)
        w.el("box", "spatula", x=700, y=300, w=60, h=140, radius=4, rotate=20, tone="dim", **{"in": 1.3, "draw": 0.6})
        for i in range(3):
            w.el("path", f"steam{i}", points=[[380 + i * 110, 420], [370 + i * 110, 380], [385 + i * 110, 340]], tone="dim", **{"in": 1.0 + i * .2, "draw": 0.7})
        return Subject((200, 380, 600, 300), detail=(420, 420, 220, 110), anchor={"element": "griddle", "type": "griddle"}, action="sizzle")
    if item == "guitar":
        w.el("ellipse", "body", fill=True, cx=520, cy=560, rx=200, ry=140 if high else 170)
        w.el("ellipse", "hole", cx=560, cy=540, rx=40, ry=30, tone="dim")
        w.el("path", "neck", points=[[330, 500], [40, 400]])
        for i in range(4):
            w.el("path", f"str{i}", points=[[60, 395 + i * 8], [560, 520 + i * 10]], tone="dim")
        w.el("hand", "hand", x=420, y=440, w=90, h=140, pose="open", rotate=-40)
        return Subject((40, 400, 680, 300), detail=(380, 430, 200, 140), anchor={"element": "body", "type": "guitar"}, action="play")
    if item == "garment":
        w.el("box", "g1", fill=True, x=320, y=430, w=360, h=200, radius=10)
        w.el("box", "g2", x=350, y=380, w=300, h=70, radius=10, tone="dim")
        w.el("hand", "h1", x=260, y=560, w=80, h=150, pose="open", rotate=40, tone="dim")
        w.el("hand", "h2", x=660, y=560, w=80, h=150, pose="open", rotate=-40, tone="dim")
        w.el("path", "counter", points=[[-100, 650], [1100, 650]], tone="dim")
        return Subject((320, 380, 360, 250), detail=(400, 470, 200, 100), anchor={"element": "g1", "type": "garment"})
    if item == "stance":
        w.el("box", "mat", fill=True, x=250, y=300, w=500, h=420, radius=14)
        w.el("ellipse", "foot1", cx=420, cy=520, rx=45, ry=100, rotate=-12)
        w.el("ellipse", "foot2", cx=590, cy=500, rx=45, ry=100, rotate=12)
        return Subject((250, 300, 500, 420), detail=(360, 400, 290, 240), anchor={"element": "mat", "type": "hands_board"}, action="set the stance")
    if item == "during":
        w.el("box", "table", fill=True, x=200, y=330, w=600, h=360, radius=12)
        w.el("ellipse", "back", cx=500, cy=520, rx=160, ry=120, tone="dim")
        w.el("hand", "h1", x=400, y=380, w=90, h=150, pose="open", rotate=15)
        w.el("hand", "h2", x=520, y=380, w=90, h=150, pose="open", rotate=-15)
        return Subject((200, 330, 600, 360), detail=(380, 380, 240, 180), anchor={"element": "table", "type": "hands_board"}, action="the treatment")
    bid = w.el("board", "board", fill=True, x=250, y=360, w=500, h=300)
    if item == "dough":
        w.el("ellipse", "dough", cx=500, cy=510, rx=120, ry=90 if high else 100)
        w.el("hand", "h1", x=340, y=420, w=90, h=150, pose="open", rotate=20)
        w.el("hand", "h2", x=570, y=420, w=90, h=150, pose="open", rotate=-20)
        return Subject(w.bbox(bid), detail=(380, 420, 240, 180), anchor={"element": "board", "type": "hands_board"}, action="hands fold the dough")
    if item == "wrap":
        w.el("box", "paper", x=330, y=400, w=340, h=220, radius=6)
        w.el("path", "bun", points=P.arc(500, 530, 110, 45, 180, 360).pts, tone="accent")
        w.el("hand", "h1", x=280, y=560, w=80, h=140, pose="open", rotate=50, tone="dim")
        w.el("hand", "h2", x=640, y=560, w=80, h=140, pose="open", rotate=-50, tone="dim")
        return Subject(w.bbox(bid), detail=(380, 440, 240, 150), anchor={"element": "board", "type": "hands_board"}, action="wrap it")
    if item in ("tool", "work"):
        w.el("box", "piece", x=380, y=440, w=240, h=140, radius=8)
        w.el("brush", "tool", x=470, y=380, w=160, h=36, kind="comb", rotate=-30, tone="dim")
        w.el("hand", "h1", x=600, y=330, w=80, h=130, pose="hold", rotate=-35)
        return Subject(w.bbox(bid), detail=(400, 440, 200, 110), anchor={"element": "board", "type": "hands_board"}, action="the work")
    w.el("hand", "h1", x=360, y=420, w=90, h=150, pose="open", rotate=20)
    w.el("hand", "h2", x=550, y=420, w=90, h=150, pose="hold", rotate=-20)
    w.el("knife", "knife", x=580, y=340, w=22, h=150, rotate=-15, tone="dim")
    w.el("veg", "veg", cx=470, cy=560, r=40, kind="tomato", halves=True)
    return Subject(w.bbox(bid), detail=(380, 430, 240, 170), anchor={"element": "board", "type": "hands_board"}, action="hands at work")


def b_hand_pov(w, item, r):
    if item == "pastry":
        cid = w.el("display_case", "case", x=50, y=330, w=900, h=420, rows=2, items=5, tone="dim")
        it = w.anchor(cid, "item3")
        bid = w.el("bread", "pick", fill=True, x=it[0], y=it[1], w=it[2], h=it[3], kind="croissant")
        w.el("hand", "hand", x=it[0] + 20, y=it[1] + it[3] - 30, w=110, h=240, pose="point", rotate=-15, **{"in": 1.0, "draw": 0.7})
        return Subject((50, 330, 900, 420), detail=w.bbox(bid), scene_level=True, focus=w.bbox(bid),
                       anchor={"element": "pick", "type": "pastry"})
    if item == "garment":
        w.el("path", "rail", points=[[-200, 300], [1200, 300]])
        for i in range(7):
            x = -120 + i * 180
            w.el("path", f"g{i}", points=[[x + 40, 300], [x + 40, 325], [x - 10, 370], [x - 10, 600], [x + 90, 600], [x + 90, 370], [x + 40, 325]],
                 tone="main" if i == 3 else "dim")
        w.fill_of({"id": "g3", "in": 0}, polygon=[[420, 325], [370, 370], [370, 600], [470, 600], [470, 370]])
        w.el("hand", "hand", x=380, y=520, w=110, h=240, pose="point", rotate=10, **{"in": 1.0, "draw": 0.7})
        return Subject((-130, 300, 1340, 300), detail=(370, 325, 100, 275), scene_level=True, focus=(340, 300, 160, 300),
                       anchor={"kind": "salient", "type": "garment"})
    sid = w.el("shelf", "shelf", x=0, y=300, w=1000, h=320, rows=2, bottles=6, tone="dim")
    bid = w.el("bottle", "pick", fill=True, x=460, y=330, w=80, h=200)
    w.el("hand", "hand", x=430, y=460, w=110, h=240, pose="point", rotate=0, **{"in": 1.0, "draw": 0.7})
    return Subject((0, 300, 1000, 320), detail=w.bbox(bid), scene_level=True, focus=w.bbox(bid),
                   anchor={"element": "pick", "type": "bottle"})


def b_nails(w, item, r):
    if item == "tech":
        w.el("hand", "mine", fill=True, x=380, y=420, w=200, h=320, pose="open")
        w.el("hand", "tech", x=560, y=330, w=130, h=220, pose="hold", rotate=-120, tone="dim")
        w.el("brush", "brush", x=560, y=480, w=120, h=24, kind="round", rotate=-50, tone="accent")
        return Subject((380, 330, 310, 410), detail=(400, 420, 160, 130), anchor={"element": "mine", "type": "hand"}, action="at work")
    hid = w.el("hand", "hand", fill=True, x=360, y=380, w=280, h=400, pose="open")
    for i, fx in enumerate((0.185, 0.41, 0.63, 0.855)):
        w.el("ellipse", f"nail{i}", cx=360 + 280 * fx, cy=395 + (0 if i in (1, 2) else 25), rx=14, ry=18, tone="accent")
    detail = (380, 370, 240, 70) if item != "accent" else (400, 370, 80, 60)
    return Subject(w.bbox(hid), detail=detail, anchor={"element": "hand", "type": "hand"},
                   action="turn the hand" if item == "turns" else None)


def b_tools(w, item, r):
    tid = w.el("tray", "tray", fill=True, x=250, y=560, w=500, h=60, items="none")
    w.el("box", "trayface", x=250, y=380, w=500, h=200, radius=10)
    w.el("scissors", "scissors", x=330, y=400, w=60, h=160, rotate=20)
    w.el("brush", "brush", x=440, y=460, w=160, h=30, kind="comb")
    w.el("path", "tweezers", points=[[660, 410], [650, 550], [680, 410]], tone="dim")
    return Subject((250, 380, 500, 240), detail=(320, 400, 300, 170), anchor={"element": "trayface", "type": "tray"})


def b_bag(w, item, r):
    w.el("box", "ledge", x=100, y=250, w=800, h=40)
    w.el("hand", "hand", x=440, y=280, w=120, h=200, pose="hold", rotate=180, tone="dim")
    bid = w.el("paper_bag", "bag", fill=True, x=400, y=440, w=200, h=240, text="")
    return Subject((400, 290, 200, 390), detail=w.bbox(bid), anchor={"element": "bag", "type": "box"}, action="the bag comes down")


def b_details(w, item, r):
    pid = w.el("plant", "plant", fill=True, x=400, y=360, w=200, h=320)
    lid = w.el("pendant", "lamp", x=1420, y=300, w=160, h=200, count=1)
    w.fill_of({"id": "lamp", "in": 0}, polygon=[[1440, 420], [1560, 420], [1580, 480], [1420, 480]])
    return Subject(w.bbox(pid), detail=w.bbox(pid), anchor={"element": "plant", "type": "plant"}, whip_to=w.bbox(lid))


def b_machine(w, item, r):
    w.el("box", "frame", fill=True, x=330, y=250, w=340, h=480, radius=14)
    w.el("box", "stack", x=360, y=420, w=120, h=280, tone="dim")
    for i in range(6):
        w.el("path", f"plate{i}", points=[[360, 450 + i * 40], [480, 450 + i * 40]], tone="dim")
    w.el("box", "seat", x=520, y=560, w=120, h=40, radius=10)
    w.el("path", "cable", points=[[420, 420], [420, 290], [600, 290], [600, 420]], tone="accent")
    w.el("path", "floor", points=[[-100, 740], [1100, 740]], tone="dim")
    return Subject((330, 250, 340, 490), detail=(340, 400, 160, 200), anchor={"element": "frame", "type": "machine"})


def hair_variant(w, t_in, t_out, az, cx=500, cy=480, rx=170, ry=210):
    tag = f"{int(az)}"
    ex = {"in": t_in, "draw": 0.25}
    if t_out is not None:
        ex["out"] = t_out
    a = math.radians(az)
    def px(theta_deg):
        th = math.radians(theta_deg) - a
        return cx + rx * math.sin(th), math.cos(th)
    w.el("ellipse", "head" + tag, cx=cx, cy=cy, rx=rx, ry=ry, **ex)
    w.el("path", "neck" + tag, points=[[cx - 50, cy + ry], [cx - 60, cy + ry + 90], [cx + 60, cy + ry + 90], [cx + 50, cy + ry]], **ex)
    for theta, name in ((90, "ear_r"), (-90, "ear_l")):
        x, vis = px(theta)
        if vis > -0.15:
            w.el("ellipse", f"{name}{tag}", cx=x, cy=cy + 10, rx=max(6, 22 * abs(math.cos(math.radians(theta) - a))), ry=34, tone="dim", **ex)
    x0, _ = px(0)
    w.el("ellipse", "whorl" + tag, cx=x0, cy=cy - ry * .45, rx=max(5, 18 * abs(math.cos(a))), ry=14, tone="dim", **ex)
    for k in range(-3, 4):
        x, vis = px(k * 22)
        if vis > 0:
            w.el("path", f"strand{k + 3}{tag}", points=[[x, cy - ry * .95], [x + 6 * k, cy - ry * .2]], tone="dim", **ex)
    if t_in == 0:
        w.fill_of({"id": "head" + tag, "in": 0}, polygon=hull(P.arc(cx, cy, rx, ry).pts))


def b_hair(w, item, r):
    if r["move"].startswith("orbit"):
        w.el("salon_chair", "chair", x=360, y=700, w=280, h=140, facing="front", tone="dim")
        if item == "blend":
            w.el("box", "clipper", x=700, y=420, w=50, h=120, radius=10, tone="accent", **{"in": 1.0, "draw": 0.5})
            w.el("hand", "hand", x=690, y=540, w=90, h=160, pose="hold", rotate=0, tone="dim", **{"in": 1.0, "draw": 0.5})
        def orbit(world, t_in, t_out, az):
            hair_variant(world, t_in, t_out, az)
        return Subject((330, 270, 340, 420), anchor={"kind": "salient", "type": "person"}, orbit=orbit)
    hair_variant(w, 0, None, 0)
    w.el("scissors", "scissors", x=640, y=300, w=60, h=170, rotate=-30, tone="accent", **{"in": 1.0, "draw": 0.6})
    w.el("brush", "comb", x=600, y=420, w=120, h=28, kind="comb", rotate=20, tone="dim", **{"in": 1.0, "draw": 0.6})
    w.el("hand", "hand", x=650, y=470, w=90, h=160, pose="hold", rotate=-10, tone="dim", **{"in": 1.0, "draw": 0.6})
    return Subject((330, 270, 340, 420), detail=(560, 300, 180, 200), anchor={"kind": "salient", "type": "person"},
                   fill_center=(420, 320, 160, 160))


BUILDERS = {"selfie": b_selfie, "person": b_person, "over_shoulder": b_over_shoulder, "facade": b_facade, "door": b_door,
            "sign": b_sign, "menu": b_menu, "card": b_card, "room": b_room, "table": b_table, "bar": b_bar, "case": b_case,
            "rail": b_rail, "oven": b_oven, "tray": b_tray, "pastry": b_pastry, "cup": b_cup, "latte": b_latte,
            "glass": b_glass, "tap": b_tap, "plate": b_plate, "burger": b_burger, "topdown": b_topdown, "hands": b_hands,
            "hand_pov": b_hand_pov, "nails": b_nails, "tools": b_tools, "bag": b_bag, "details": b_details,
            "machine": b_machine, "hair": b_hair}


# ---------------------------------------------------------------- assembling the scene
def shift(rect, dx=0, dy=0):
    return [round(rect[0] + dx, 2), round(rect[1] + dy, 2), rect[2], rect[3]]


def kf(t, rect, ease=None):
    k = {"t": round(t, 2), "camera": {"target": rect, "pad": 0}, "focus": None, "mask": 0}
    if ease:
        k["ease"] = ease
    return k


def make_scene(gid, r, title=None):
    """Scene JSON + the compiled-step list for one step row of the catalog (see catalog.py)."""
    w = World()
    sub = BUILDERS[r["family"]](w, r["item"], r)
    angle, move, trans = r["angle"], r["move"], r["transition"]
    front = r["camera"] == "front"
    tilt = SELFIE_TILT[angle] if front else TILT[angle]
    tilt = {"target": tilt[0], "tolerance": tilt[1]}
    T = max(4.0, min(float(r["seconds"]), 6.3))
    whip_out = trans == "whip"
    if whip_out:
        T = max(T, 4.6)
    T_hold_end = T - (0.9 if whip_out else 0.0)

    start = sub.frame(r["start"])
    end = sub.frame(r["end"])
    if trans == "push-through" and sub.fill_center:
        end = cam(rect_center(sub.fill_center), width_for(sub.fill_center, 1.15))
    tl, steps, notes = [], [{"kind": "frame", "lock_after": 0.6, "tilt": tilt}], []
    direction = move.split("-")[1] if "-" in move else "right"

    if move == "static":
        tl += [kf(0, start), kf(T_hold_end, start)]
        if sub.action:
            still = round(max(1.5, T_hold_end - 1.2 - 1.2), 2)
            steps.append({"kind": "still", "duration": still, "subject_motion": sub.action, "tilt": tilt})
            steps.append({"kind": "hold", "duration": 1.2, "tilt": tilt})
        else:
            steps.append({"kind": "hold", "duration": round(min(3.0, T_hold_end - 1.2), 2), "tilt": tilt})
        last = start
    elif move == "whip":
        # the step starts mid-whip: a short hold off the subject, the flick onto it, then the hold
        if sub.whip_from:
            start = cam(rect_center(sub.whip_from), end[2])
        elif sub.whip_to:
            end = cam(rect_center(sub.whip_to), start[2])
        for i in range(4):
            y = start[1] + start[3] * (0.42 + 0.05 * i)
            w.el("path", f"whipin{i}", points=[[start[0] + start[2] * 0.4, y], [end[0] + end[2] * 0.6, y]], tone="dim",
                 **{"in": 1.15, "draw": 0.12, "out": 1.7})
        tl += [kf(0, start), kf(1.2, start), kf(1.65, end, "inOutExpo"), kf(T_hold_end, end)]
        steps.append({"kind": "follow", "action": "whip", "direction": "right", "channel": "gyro_yaw", "min_peak_rate": 3.0})
        steps.append({"kind": "hold", "duration": round(T_hold_end - 2.65, 2), "tilt": tilt})
        notes.append("starts on the previous detail and whips onto the subject")
        last = end
    else:
        M = round(max(1.8, min(3.2, T_hold_end - 1.2 - 1.4)), 2)
        E = round(T_hold_end - 1.2 - M, 2)
        if move in ("push-in", "pull-out"):
            tl += [kf(0, start), kf(1.2, start), kf(1.2 + M, end, "inOutSine"), kf(T_hold_end, end)]
            amount = round(start[2] / end[2], 3)
            steps.append({"kind": "follow", "action": "dolly_in" if move == "push-in" else "dolly_out", "amount": amount,
                          "duration": M, "channel": "image_scale" if sub.anchor.get("kind") in ("none", "face") else "subject_scale",
                          "tilt": tilt})
            last = end
        elif move.startswith("pan") or move.startswith("truck"):
            amt = 0.8 if r["start"] == "wide" else 0.6
            sgn = 1 if direction == "right" else -1
            end = shift(start, dx=sgn * amt * start[2])
            tl += [kf(0, start), kf(1.2, start), kf(1.2 + M, end, "inOutSine"), kf(T_hold_end, end)]
            steps.append({"kind": "follow", "action": "pan" if move.startswith("pan") else "truck", "direction": direction,
                          "amount": amt, "duration": M, "channel": "gyro_yaw" if move.startswith("pan") else "image_motion",
                          "tilt": tilt})
            last = end
        elif move == "tilt-down":
            target = sub.tilt_target or sub.detail
            end = cam((rect_center(start)[0], rect_center(target)[1]), start[2])
            amt = round((end[1] - start[1]) / start[3], 3)
            tl += [kf(0, start), kf(1.2, start), kf(1.2 + M, end, "inOutSine"), kf(T_hold_end, end)]
            steps.append({"kind": "follow", "action": "tilt", "direction": "down", "amount": amt, "duration": M, "channel": "gravity_tilt"})
            last = end
        elif move == "reveal-from-behind":
            # the camera slides out from behind a blocker that fills the start frame; a truck is the one named move
            end = sub.frame(r["end"])
            start = shift(end, dx=-0.7 * end[2])
            kind = "wall" if r["family"] in ("selfie", "person") or r["item"] in ("changing", "treatment", "waiting") else "plant"
            bx = start[0] - 0.1 * start[2]
            if r["item"] == "cupreveal":
                w.el("cup", "blocker", fill=True, x=bx, y=start[1] + 0.3 * start[3], w=0.6 * start[2], h=0.4 * start[3], saucer=False, steam=True)
            else:
                w.el("frame_edge", "blocker", x=bx, y=start[1] - 0.1 * start[3], w=0.68 * start[2], h=1.2 * start[3], kind=kind, side="left")
                w.fill_of({"id": "blocker", "in": 0}, polygon=[[bx, start[1] - 0.1 * start[3]], [bx + 0.68 * start[2], start[1] - 0.1 * start[3]],
                                                             [bx + 0.68 * start[2], start[1] + 1.1 * start[3]], [bx, start[1] + 1.1 * start[3]]])
            tl += [kf(0, start), kf(1.2, start), kf(1.2 + M, end, "inOutSine"), kf(T_hold_end, end)]
            steps.append({"kind": "follow", "action": "truck", "direction": "right", "amount": 0.7, "duration": M,
                          "channel": "image_motion", "tilt": tilt})
            notes.append("reveal drawn as a truck out from behind a foreground blocker")
            last = end
        elif move.startswith("orbit"):
            arc = 60
            n = 7
            sgn = 1 if direction == "right" else -1
            for i in range(n):
                t_in = 0 if i == 0 else round(1.2 + M * i / (n - 1) - 0.15, 2)
                t_out = None if i == n - 1 else round(1.2 + M * (i + 1) / (n - 1) - 0.15, 2)
                sub.orbit(w, t_in, t_out, sgn * arc * i / (n - 1))
            drift = shift(start, dx=0.06 * start[2] * sgn)
            tl += [kf(0, start), kf(1.2, start), kf(1.2 + M, drift, "inOutSine"), kf(T_hold_end, drift)]
            steps.append({"kind": "follow", "action": "orbit", "direction": direction, "arc": arc, "duration": M,
                          "channel": "orbit", "tilt": tilt, "level": None})
            notes.append(f"orbit shown as {n} turned poses cross-faded ({arc // (n - 1)} degrees apart)")
            last = drift
        else:
            raise ValueError(move)
        steps.append({"kind": "hold", "duration": max(E, 1.0), "tilt": tilt})

    if whip_out:
        off = shift(last, dx=1.35 * last[2])
        for i in range(4):
            y = last[1] + last[3] * (0.42 + 0.05 * i)
            w.el("path", f"streak{i}", points=[[last[0] + last[2] * 0.3, y], [off[0] + off[2] * 0.6, y]], tone="dim",
                 **{"in": T_hold_end - 0.05, "draw": 0.12, "out": T_hold_end + 0.45})
        tl += [kf(T_hold_end + 0.42, off, "inOutExpo"), kf(T, off)]
        steps.append({"kind": "follow", "action": "whip", "direction": "right", "channel": "gyro_yaw", "min_peak_rate": 3.0})
        steps.append({"kind": "hold", "duration": 0.4})
        notes.append("ends with a whip out to the right")
    if trans == "push-through":
        notes.append("ends filled by the subject for the push-through")

    anchor = dict(sub.anchor)
    for st in steps:
        if st.get("action") in ("tilt", "whip"):
            st.pop("tilt", None)
    scene = {
        "name": gid,
        "title": title or gid.replace("_", " "),
        "description": f"{r['family']} {r['item']}: {angle}, {r['start']} to {r['end']}, {move}, then {trans}. {r['reads']}",
        "canvas": {"w": 540, "h": 960}, "fps": 15, "style": dict(STYLE),
        "drawing_clip": DRAWING_CLIP, "motion_bounds": MOTION_BOUNDS,
        "elements": w.elements, "fills": w.fills, "timeline": tl, "annotations": [],
        "end": {"hold": 0.4, "fade": 0.3, "return": 0},
        "live": {"camera": r["camera"], "anchor": anchor, "contour": "box" if anchor.get("kind") in ("none", "face") or
                 anchor.get("type") in ("display_case", "facade", "sign", "window", "door", "room", "bar_counter", "shelf", "menu_board") else "instance_mask",
                 "steps": steps},
    }
    return scene, notes
