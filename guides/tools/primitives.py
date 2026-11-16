"""Schematic line-art primitives for shot-guide overlays.

Every primitive returns a Shape: polylines in WORLD coordinates (y down),
named anchors (bboxes) that the camera / focus frame can target, and optional
world-space texts. Everything is a polyline so the renderer can "draw on"
any element by truncating total stroke length.

Tones: "main" (white), "accent" (highlight colour), "dim" (faded).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field


@dataclass
class Path:
    pts: list            # [(x, y), ...]
    closed: bool = False
    tone: str = "main"


@dataclass
class Text:
    x: float
    y: float
    text: str
    size: float          # world units (scales with camera zoom)
    tone: str = "main"


@dataclass
class Shape:
    paths: list = field(default_factory=list)
    anchors: dict = field(default_factory=dict)   # name -> (x, y, w, h)
    texts: list = field(default_factory=list)

    def add(self, other: "Shape", prefix: str | None = None):
        self.paths += other.paths
        self.texts += other.texts
        for k, v in other.anchors.items():
            self.anchors[f"{prefix}.{k}" if prefix else k] = v
        return self


# ---------------------------------------------------------------- geometry

def rect(x, y, w, h, tone="main"):
    return Path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True, tone)


def line(x1, y1, x2, y2, tone="main"):
    return Path([(x1, y1), (x2, y2)], False, tone)


def arc(cx, cy, rx, ry, a0=0, a1=360, n=None, tone="main"):
    n = n or max(12, int(abs(a1 - a0) / 6))
    pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    closed = abs(a1 - a0) >= 360
    if closed:
        pts = pts[:-1]
    return Path(pts, closed, tone)


def rrect(x, y, w, h, r, tone="main"):
    r = min(r, w / 2, h / 2)
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
                       (x + r, y + h - r, 90), (x + r, y + r, 180)):
        pts += arc(cx, cy, r, r, a0, a0 + 90, 6).pts
    return Path(pts, True, tone)


def wave(x1, x2, y, amp, periods, tone="main", vertical=False):
    n = int(periods * 16)
    pts = []
    for i in range(n + 1):
        t = i / n
        a = x1 + (x2 - x1) * t
        b = y + amp * math.sin(t * periods * 2 * math.pi)
        pts.append((b, a) if vertical else (a, b))
    return Path(pts, False, tone)


def bbox_of(paths):
    xs = [p[0] for pa in paths for p in pa.pts]
    ys = [p[1] for pa in paths for p in pa.pts]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def bezier(start, *segments):
    """Chained cubic contours, sampled into the same draw-on polylines."""
    pts = [start]
    for c1, c2, end in segments:
        p = pts[-1]
        for i in range(1, 21):
            t, u = i / 20, 1 - i / 20
            pts.append(tuple(u**3*p[k] + 3*u*u*t*c1[k] +
                             3*u*t*t*c2[k] + t**3*end[k] for k in (0, 1)))
    return pts


# ---------------------------------------------------------------- exterior

def door(x, y, w, h, handle="right", glass=True, **_):
    s = Shape()
    s.paths.append(rect(x, y, w, h))
    m = w * 0.12
    if glass:
        g = (x + m, y + m, w - 2 * m, h * 0.62)
        s.paths.append(rect(*g, tone="dim"))
        # reflection strokes
        s.paths.append(line(g[0] + g[2] * .55, g[1] + g[3] * .1, g[0] + g[2] * .2, g[1] + g[3] * .45, "dim"))
        s.paths.append(line(g[0] + g[2] * .8, g[1] + g[3] * .2, g[0] + g[2] * .45, g[1] + g[3] * .6, "dim"))
        s.anchors["glass"] = g
        s.paths.append(rect(x + m, y + m + h * .62 + m * .6, w - 2 * m, h - h * .62 - 2.6 * m, "dim"))
    hx = x + w - m * 1.1 if handle == "right" else x + m * 0.5
    hw, hh = m * .6, h * .22
    hy = y + h * .45
    s.paths.append(rrect(hx, hy, hw, hh, hw / 2, "accent"))
    s.anchors["handle"] = (hx, hy, hw, hh)
    s.anchors["door"] = (x, y, w, h)
    return s


def window(x, y, w, h, panes=2, sill=True, **_):
    s = Shape()
    s.paths.append(rect(x, y, w, h))
    for i in range(1, panes):
        s.paths.append(line(x + w * i / panes, y, x + w * i / panes, y + h, "dim"))
    s.paths.append(line(x + w * .15, y + h * .2, x + w * .05, y + h * .4, "dim"))
    if sill:
        s.paths.append(line(x - w * .04, y + h, x + w * 1.04, y + h))
    s.anchors["window"] = (x, y, w, h)
    return s


def awning(x, y, w, h, scallops=8, **_):
    s = Shape()
    s.paths.append(Path([(x, y + h * .6), (x + w * .04, y), (x + w * .96, y), (x + w, y + h * .6)]))
    sw = w / scallops
    pts = []
    for i in range(scallops):
        pts += arc(x + sw * (i + .5), y + h * .6, sw / 2, h * .4, 180, 0, 8).pts
    s.paths.append(Path(pts))
    for i in range(1, scallops):
        s.paths.append(line(x + w * .04 + (w * .92) * i / scallops, y, x + sw * i, y + h * .6, "dim"))
    s.anchors["awning"] = (x, y, w, h)
    return s


def sign(x, y, w, h, text="CAFE", **_):
    s = Shape()
    s.paths.append(rrect(x, y, w, h, h * .2))
    if text:
        s.texts.append(Text(x + w / 2, y + h / 2, text, h * .5))
    s.anchors["sign"] = (x, y, w, h)
    return s


def facade(x, y, w, h, sign_text="CAFE", door_pos="center", windows=2, has_awning=True, **_):
    s = Shape()
    s.paths.append(Path([(x, y + h), (x, y), (x + w, y), (x + w, y + h)]))
    s.paths.append(line(x - w * .03, y + h * .06, x + w * 1.03, y + h * .06))           # cornice
    s.paths.append(line(x - w * .15, y + h, x + w * 1.15, y + h))                         # sidewalk
    s.paths.append(line(x - w * .15, y + h * 1.04, x + w * 1.15, y + h * 1.04, "dim"))
    s.add(sign(x + w * .3, y + h * .1, w * .4, h * .1, sign_text))
    dw, dh = w * .2, h * .55
    dx = {"center": x + (w - dw) / 2, "left": x + w * .1, "right": x + w * .7}[door_pos]
    s.add(door(dx, y + h - dh, dw, dh))
    if has_awning:
        s.add(awning(dx - dw * .3, y + h - dh - h * .12, dw * 1.6, h * .1))
    if windows:
        ww, wh = w * .25, h * .32
        slots = [x + w * .07, x + w * .68] if door_pos == "center" else [x + w * .4, x + w * .7]
        for i, wx in enumerate(slots[:windows]):
            s.add(window(wx, y + h * .4, ww, wh), f"window{i + 1}")
    s.anchors["facade"] = (x, y, w, h)
    return s


# ---------------------------------------------------------------- interior

def room(x, y, w, h, depth=0.32, **_):
    """One-point perspective box: back wall + floor/ceiling/wall lines."""
    s = Shape()
    bx, by, bw, bh = x + w * depth, y + h * depth * .9, w * (1 - 2 * depth), h * (1 - 1.8 * depth) * .9
    s.paths.append(rect(bx, by, bw, bh))
    for (ox, oy), (ix, iy) in (((x, y), (bx, by)), ((x + w, y), (bx + bw, by)),
                               ((x, y + h), (bx, by + bh)), ((x + w, y + h), (bx + bw, by + bh))):
        s.paths.append(line(ox, oy, ix, iy, "dim"))
    # floor boards converging
    for i in range(1, 5):
        fx = x + w * i / 5
        s.paths.append(line(fx, y + h, bx + bw * i / 5, by + bh, "dim"))
    s.anchors.update(room=(x, y, w, h), back_wall=(bx, by, bw, bh),
                     left_wall=(x, by, bx - x, bh), right_wall=(bx + bw, by, x + w - bx - bw, bh),
                     floor=(x, by + bh, w, y + h - by - bh))
    return s


def table(x, y, w, h, **_):
    s = Shape()
    s.paths.append(rect(x, y, w, h * .08))
    s.paths.append(line(x + w * .1, y + h * .08, x + w * .1, y + h))
    s.paths.append(line(x + w * .9, y + h * .08, x + w * .9, y + h))
    s.anchors["table"] = (x, y, w, h)
    s.anchors["top"] = (x, y - h * .4, w, h * .48)
    return s


def chair(x, y, w, h, facing="right", **_):
    s = Shape()
    back = x if facing == "right" else x + w
    s.paths.append(Path([(back, y), (back, y + h)]))
    s.paths.append(Path([(x, y + h * .55), (x + w, y + h * .55), (x + w if facing == "right" else x, y + h)]))
    s.anchors["chair"] = (x, y, w, h)
    return s


def bar_counter(x, y, w, h, stools=3, **_):
    s = Shape()
    s.paths.append(rect(x, y, w, h * .12))
    s.paths.append(rect(x + w * .02, y + h * .12, w * .96, h * .5, "dim"))
    for i in range(stools):
        sx = x + w * (i + .5) / stools
        s.paths.append(arc(sx, y + h * .66, w * .05, h * .025))
        s.paths.append(line(sx, y + h * .69, sx, y + h))
        s.paths.append(line(sx - w * .04, y + h, sx + w * .04, y + h, "dim"))
    s.anchors["bar"] = (x, y, w, h)
    return s


def pendant(x, y, w, h, count=3, **_):
    s = Shape()
    for i in range(count):
        cx = x + w * (i + .5) / count
        r = min(w / count * .3, h * .3)
        s.paths.append(line(cx, y, cx, y + h - r, "dim"))
        s.paths.append(arc(cx, y + h - r, r, r, 180, 360))
        s.paths.append(line(cx - r, y + h - r, cx + r, y + h - r))
    s.anchors["pendant"] = (x, y, w, h)
    return s


def shelf(x, y, w, h, rows=3, bottles=5, **_):
    s = Shape()
    for r in range(rows + 1):
        s.paths.append(line(x, y + h * r / rows, x + w, y + h * r / rows))
    for r in range(rows):
        base = y + h * (r + 1) / rows
        for b in range(bottles):
            bx = x + w * (b + .5) / bottles
            bw = w / bottles * .35
            bh = h / rows * (.55 + .25 * ((b * 7 + r * 3) % 3) / 2)
            s.paths.append(Path([(bx - bw / 2, base), (bx - bw / 2, base - bh * .6),
                                 (bx - bw / 5, base - bh * .8), (bx - bw / 5, base - bh),
                                 (bx + bw / 5, base - bh), (bx + bw / 5, base - bh * .8),
                                 (bx + bw / 2, base - bh * .6), (bx + bw / 2, base)], False, "dim"))
    s.anchors["shelf"] = (x, y, w, h)
    return s


def plant(x, y, w, h, **_):
    s = Shape()
    s.paths.append(Path([(x + w * .25, y + h * .7), (x + w * .3, y + h), (x + w * .7, y + h), (x + w * .75, y + h * .7)], True))
    for a in (-60, -25, 0, 25, 60):
        tx = x + w / 2 + math.sin(math.radians(a)) * w * .45
        ty = y + h * .7 - math.cos(math.radians(a)) * h * .65
        s.paths.append(Path([(x + w / 2, y + h * .7), ((x + w / 2 + tx) / 2 + w * .05, (y + h * .7 + ty) / 2), (tx, ty)], False, "dim"))
    s.anchors["plant"] = (x, y, w, h)
    return s


def menu_board(x, y, w, h, title="MENU", lines=5, **_):
    s = Shape()
    s.paths.append(rect(x, y, w, h))
    s.paths.append(rect(x + w * .04, y + h * .04, w * .92, h * .92, "dim"))
    s.texts.append(Text(x + w / 2, y + h * .14, title, h * .09))
    for i in range(lines):
        ly = y + h * (.3 + .6 * i / max(lines, 1))
        s.paths.append(line(x + w * .12, ly, x + w * .62, ly))
        s.paths.append(line(x + w * .66, ly, x + w * .78, ly, "dim"))   # dots
        s.paths.append(line(x + w * .8, ly, x + w * .88, ly, "accent"))  # price
        s.anchors[f"item{i + 1}"] = (x + w * .1, ly - h * .05, w * .8, h * .1)
    s.anchors["menu"] = (x, y, w, h)
    s.anchors["title"] = (x + w * .2, y + h * .06, w * .6, h * .16)
    return s


# ---------------------------------------------------------------- food & drink

def cup(x, y, w, h, saucer=True, steam=True, **_):
    """Side view. (x,y,w,h) is the cup body; saucer & steam extend outside."""
    s = Shape()
    s.paths.append(Path(bezier((x, y),
        ((x+w*.03, y+h*.3), (x+w*.03, y+h*.78), (x+w*.17, y+h*.9)),
        ((x+w*.3, y+h*1.03), (x+w*.7, y+h*1.03), (x+w*.83, y+h*.9)),
        ((x+w*.97, y+h*.78), (x+w*.97, y+h*.3), (x+w, y)))))
    s.paths.append(arc(x + w / 2, y, w / 2, h * .08))
    s.paths.append(arc(x + w / 2, y + h * .03, w * .42, h * .05, 0, 180, tone="accent"))  # crema
    s.paths.append(arc(x + w * 1.0, y + h * .38, w * .2, h * .2, -80, 90))
    if saucer:
        s.paths.append(arc(x + w / 2, y + h * 1.02, w * .85, h * .1, 0, 180))
        s.paths.append(arc(x + w / 2, y + h * 1.02, w * .85, h * .1, 180, 360, tone="dim"))
    if steam:
        for i, dx in enumerate((.3, .5, .7)):
            s.paths.append(wave(y - h * .1, y - h * (.6 + .1 * i), x + w * dx, w * .05, 1.2, "dim", vertical=True))
        s.anchors["steam"] = (x + w * .2, y - h * .7, w * .6, h * .6)
    s.anchors["cup"] = (x, y - h * .08, w * 1.2, h * 1.08)
    s.anchors["rim"] = (x, y - h * .1, w, h * .2)
    s.anchors["handle"] = (x + w * .9, y + h * .15, w * .32, h * .45)
    return s


def latte(cx, cy, r, art="heart", **_):
    """Top view: saucer, cup, latte art."""
    s = Shape()
    s.paths.append(arc(cx, cy, r * 1.5, r * 1.5, tone="dim"))
    s.paths.append(arc(cx, cy, r, r))
    s.paths.append(arc(cx, cy, r * .85, r * .85))
    s.paths.append(Path([(cx + r, cy - r * .15), (cx + r * 1.45, cy - r * .12),
                         (cx + r * 1.45, cy + r * .12), (cx + r, cy + r * .15)]))
    if art == "heart":
        a = r * .45
        pts = []
        for i in range(41):
            t = i / 40 * 2 * math.pi
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((cx + hx / 17 * a, cy + hy / 17 * a))
        s.paths.append(Path(pts, True, "accent"))
    else:  # rosetta
        for i in range(6):
            yy = cy - r * .5 + i * r * .17
            ww = r * (.55 - i * .07)
            s.paths.append(arc(cx, yy, ww, r * .08, 0, 180, tone="accent"))
        s.paths.append(line(cx, cy - r * .6, cx, cy + r * .5, "accent"))
    s.anchors["latte"] = (cx - r * 1.5, cy - r * 1.5, r * 3, r * 3)
    s.anchors["cup"] = (cx - r, cy - r, 2 * r, 2 * r)
    s.anchors["art"] = (cx - r * .55, cy - r * .55, r * 1.1, r * 1.1)
    return s


def plate(cx, cy, r, dish="pasta", cutlery=True, **_):
    """Top view plate with dish."""
    s = Shape()
    s.paths.append(arc(cx, cy, r, r))
    s.paths.append(arc(cx, cy, r * .72, r * .72, tone="dim"))
    fr = r * .5
    if dish == "pasta":
        pts = []
        for i in range(160):
            t = i / 160 * 5 * 2 * math.pi
            rr = fr * (1 - i / 175)
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * .9))
        s.paths.append(Path(pts, False, "main"))
        for a in (30, 150, 260):
            s.paths.append(arc(cx + fr * .5 * math.cos(math.radians(a)), cy + fr * .5 * math.sin(math.radians(a)),
                               r * .06, r * .04, tone="accent"))  # basil / tomato
    elif dish == "salad":
        for a in range(0, 360, 45):
            lx, ly = cx + fr * .5 * math.cos(math.radians(a)), cy + fr * .5 * math.sin(math.radians(a))
            s.paths.append(arc(lx, ly, fr * .35, fr * .2, a, a + 360, 16, "main"))
        s.paths.append(arc(cx, cy, fr * .15, fr * .15, tone="accent"))
    elif dish == "steak":
        s.paths.append(Path([(cx - fr, cy - fr * .3), (cx - fr * .4, cy - fr * .7), (cx + fr * .7, cy - fr * .5),
                             (cx + fr * .9, cy + fr * .3), (cx, cy + fr * .6), (cx - fr * .9, cy + fr * .3)], True))
        for i in range(4):
            s.paths.append(line(cx - fr * .6 + i * fr * .4, cy - fr * .4, cx - fr * .9 + i * fr * .4, cy + fr * .3, "accent"))
    elif dish == "dessert":
        s.paths.append(Path([(cx - fr * .7, cy + fr * .4), (cx, cy - fr * .8), (cx + fr * .7, cy + fr * .4)], True))
        s.paths.append(arc(cx, cy - fr * .2, fr * .12, fr * .12, tone="accent"))
        s.paths.append(wave(cx - fr * .9, cx + fr * .9, cy + fr * .7, fr * .08, 3, "accent"))
    if cutlery:
        fx = cx - r * 1.25
        s.paths.append(line(fx, cy - r * .7, fx, cy + r * .8))
        for d in (-.06, 0, .06):
            s.paths.append(line(fx + r * d, cy - r * .9, fx + r * d, cy - r * .65))
        kx = cx + r * 1.25
        s.paths.append(Path([(kx, cy + r * .8), (kx, cy - r * .3), (kx + r * .08, cy - r * .85), (kx + r * .08, cy - r * .1), (kx, cy - r * .1)]))
    s.anchors["plate"] = (cx - r, cy - r, 2 * r, 2 * r)
    s.anchors["food"] = (cx - fr, cy - fr, 2 * fr, 2 * fr)
    s.anchors["setting"] = (cx - r * 1.4, cy - r * 1.05, r * 2.8, r * 2.1)
    return s


def glass(x, y, w, h, kind="cocktail", garnish=True, **_):
    s = Shape()
    cx = x + w / 2
    if kind == "cocktail":   # coupe / martini
        bowl = h * .45
        s.paths.append(Path([(x, y), (cx, y + bowl), (x + w, y)]))
        s.paths.append(arc(cx, y, w / 2, h * .03))
        s.paths.append(line(x + w * .1, y + bowl * .2, x + w * .9, y + bowl * .2, "accent"))
        s.paths.append(line(cx, y + bowl, cx, y + h * .95))
        s.paths.append(arc(cx, y + h * .97, w * .3, h * .03))
        liquid = (x + w * .1, y + bowl * .2, w * .8, bowl * .8)
    elif kind == "wine":
        bowl = h * .5
        s.paths.append(Path([(x + w * .08, y)] + arc(cx, y + bowl * .4, w * .42, bowl * .6, 180, 0, 20).pts + [(x + w * .92, y)]))
        s.paths.append(arc(cx, y + bowl * .55, w * .38, h * .025, tone="accent"))
        s.paths.append(line(cx, y + bowl, cx, y + h * .95))
        s.paths.append(arc(cx, y + h * .97, w * .3, h * .03))
        liquid = (x + w * .1, y + bowl * .55, w * .8, bowl * .45)
    else:  # tumbler / highball
        top = y if kind == "highball" else y + h * .4
        s.paths.append(Path([(x, top), (x + w * .06, y + h), (x + w * .94, y + h), (x + w, top)]))
        s.paths.append(arc(cx, top, w / 2, h * .03))
        lv = top + (y + h - top) * .25
        s.paths.append(line(x + w * .03, lv, x + w * .97, lv, "accent"))
        for i in range(2):
            s.paths.append(rect(x + w * (.25 + .3 * i), lv + (y + h - lv) * .15, w * .22, w * .22, "dim"))
        s.paths.append(line(cx + w * .1, top - h * .25, cx - w * .1, y + h * .8, "dim"))  # straw
        liquid = (x, lv, w, y + h - lv)
    gx, gy = (x + w * .9, y) if kind != "highball" else (x + w, y)
    if garnish:
        s.paths.append(arc(gx, gy, w * .14, w * .14, tone="accent"))
        s.paths.append(line(gx - w * .1, gy, gx + w * .1, gy, "accent"))
        s.anchors["garnish"] = (gx - w * .2, gy - w * .2, w * .4, w * .4)
    s.anchors["glass"] = (x, y - h * .05, w, h * 1.05)
    s.anchors["liquid"] = liquid
    s.anchors["base"] = (x, y + h * .8, w, h * .2)
    return s


def bottle(x, y, w, h, **_):
    s = Shape()
    s.paths.append(Path([(x, y + h), (x, y + h * .4), (x + w * .3, y + h * .25), (x + w * .3, y),
                         (x + w * .7, y), (x + w * .7, y + h * .25), (x + w, y + h * .4), (x + w, y + h)], True))
    s.paths.append(rect(x + w * .1, y + h * .55, w * .8, h * .25, "accent"))
    s.anchors["bottle"] = (x, y, w, h)
    s.anchors["label"] = (x + w * .1, y + h * .55, w * .8, h * .25)
    return s


# ---------------------------------------------------------------- helpers / meta

def phone(x, y, w, h, **_):
    """Smartphone glyph — use with `rotate` to show how to hold it."""
    s = Shape()
    s.paths.append(rrect(x, y, w, h, w * .15))
    s.paths.append(arc(x + w * .5, y + h * .08, w * .07, w * .07, tone="accent"))
    s.anchors["phone"] = (x, y, w, h)
    return s


def arrow(points, head=0.04, tone="accent", **_):
    """World-space arrow along points. head = head size in world units (or fraction<1 of path length)."""
    s = Shape()
    pts = [tuple(p) for p in points]
    s.paths.append(Path(pts, False, tone))
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    hs = head * L if head < 1 else head
    a = math.atan2(y2 - y1, x2 - x1)
    for d in (2.6, -2.6):
        s.paths.append(Path([(x2, y2), (x2 + hs * math.cos(a + d), y2 + hs * math.sin(a + d))], False, tone))
    s.anchors["arrow"] = bbox_of(s.paths)
    return s


def path(points, closed=False, tone="main", **_):
    s = Shape()
    s.paths.append(Path([tuple(p) for p in points], closed, tone))
    s.anchors["path"] = bbox_of(s.paths)
    return s


def box(x, y, w, h, tone="main", radius=0, **_):
    s = Shape()
    s.paths.append(rrect(x, y, w, h, radius, tone) if radius else rect(x, y, w, h, tone))
    s.anchors["box"] = (x, y, w, h)
    return s


def ellipse(cx, cy, rx, ry, tone="main", **_):
    s = Shape()
    s.paths.append(arc(cx, cy, rx, ry, tone=tone))
    s.anchors["ellipse"] = (cx - rx, cy - ry, 2 * rx, 2 * ry)
    return s


def text(x, y, text, size=30, tone="main", **_):
    s = Shape()
    s.texts.append(Text(x, y, text, size, tone))
    s.anchors["text"] = (x - size * len(text) * .3, y - size / 2, size * len(text) * .6, size)
    return s


def trace(x, y, w, h, paths, tone="dim", **_):
    """Polylines produced by trace.py, normalized to 0..1 inside (x,y,w,h)."""
    s = Shape()
    for p in paths:
        s.paths.append(Path([(x + u * w, y + v * h) for u, v in p], False, tone))
    s.anchors["trace"] = (x, y, w, h)
    return s


# ---------------------------------------------------------------- people & hands

def person(x, y, w, h, pose="head_shoulders", facing="front", **_):
    """Schematic person. pose: head_shoulders (bust), waist_up, full (standing).
    Box = the whole figure. Anchors: person, head, face, eyes, chest, hands."""
    s = Shape()
    cx = x + w / 2
    if pose == "full":
        hr = h * .07
        hy = y + hr
    elif pose == "waist_up":
        hr = h * .13
        hy = y + hr
    else:
        hr = h * .24
        hy = y + hr * 1.05
    rx = hr * .82
    if facing == "side":
        s.paths.append(arc(cx, hy, rx, hr))
        s.paths.append(Path([(cx + rx * .95, hy - hr * .1), (cx + rx * 1.18, hy + hr * .15), (cx + rx * .95, hy + hr * .25)]))
        s.paths.append(arc(cx + rx * .45, hy - hr * .15, rx * .07, rx * .07))
    elif pose == "full":
        s.paths.append(arc(cx, hy, rx, hr))
    else:
        s.paths.append(arc(cx, hy, rx, hr))
        for d in (-.38, .38):
            s.paths.append(arc(cx + rx * d, hy - hr * .12, rx * .09, rx * .09))
        s.paths.append(arc(cx, hy + hr * .38, rx * .32, hr * .12, 20, 160, 10))
        # Small hair, brow and nose contours keep the person schematic while
        # matching the approved face's more recognizable expression.
        s.paths.append(Path(bezier((cx-rx*.9, hy-hr*.32),
            ((cx-rx*.55, hy-hr*.42), (cx-rx*.5, hy-hr*.7), (cx-rx*.47, hy-hr*.76)),
            ((cx-rx*.05, hy-hr*.4), (cx+rx*.4, hy-hr*.55), (cx+rx*.65, hy-hr*.77)),
            ((cx+rx*.65, hy-hr*.5), (cx+rx*.8, hy-hr*.4), (cx+rx*.91, hy-hr*.3)))))
        for d in (-.38, .38):
            s.paths.append(arc(cx+rx*d, hy-hr*.18, rx*.19, hr*.08, 205, 330, tone="dim"))
        s.paths.append(Path(bezier((cx, hy-hr*.02),
            ((cx-rx*.04, hy+hr*.09), (cx-rx*.13, hy+hr*.14), (cx-rx*.08, hy+hr*.18)),
            ((cx-rx*.02, hy+hr*.21), (cx+rx*.07, hy+hr*.2), (cx+rx*.11, hy+hr*.17))), tone="dim"))
    neck_y = hy + hr
    sh_y = neck_y + hr * .35
    sw = w * (.5 if pose != "head_shoulders" else .5)
    s.paths.append(line(cx - rx * .35, neck_y - hr * .05, cx - rx * .35, sh_y - hr * .1))
    s.paths.append(line(cx + rx * .35, neck_y - hr * .05, cx + rx * .35, sh_y - hr * .1))
    bottom = y + h
    if pose == "head_shoulders":
        s.paths.append(Path([(x, bottom), (x + w * .04, sh_y + (bottom - sh_y) * .35), (cx - rx * .35, sh_y - hr * .1)]))
        s.paths.append(Path([(x + w, bottom), (x + w * .96, sh_y + (bottom - sh_y) * .35), (cx + rx * .35, sh_y - hr * .1)]))
        hands = (x, bottom - h * .1, w, h * .1)
    elif pose == "waist_up":
        s.paths.append(Path([(cx - sw * .45, bottom), (cx - sw * .5, sh_y + h * .08), (cx - rx * .35, sh_y - hr * .1)]))
        s.paths.append(Path([(cx + sw * .45, bottom), (cx + sw * .5, sh_y + h * .08), (cx + rx * .35, sh_y - hr * .1)]))
        s.paths.append(Path([(cx - sw * .5, sh_y + h * .08), (cx - sw * .62, sh_y + h * .38), (cx - sw * .3, sh_y + h * .52)]))
        s.paths.append(Path([(cx + sw * .5, sh_y + h * .08), (cx + sw * .62, sh_y + h * .38), (cx + sw * .3, sh_y + h * .52)]))
        hands = (cx - sw * .4, sh_y + h * .44, sw * .8, h * .14)
    else:
        hip = y + h * .55
        s.paths.append(Path([(cx - rx * .35, sh_y - hr * .1), (cx - w * .22, sh_y), (cx - w * .2, hip), (cx + w * .2, hip), (cx + w * .22, sh_y), (cx + rx * .35, sh_y - hr * .1)]))
        s.paths.append(Path([(cx - w * .22, sh_y), (cx - w * .32, y + h * .45), (cx - w * .28, y + h * .55)]))
        s.paths.append(Path([(cx + w * .22, sh_y), (cx + w * .32, y + h * .45), (cx + w * .28, y + h * .55)]))
        s.paths.append(Path([(cx - w * .14, hip), (cx - w * .16, bottom)]))
        s.paths.append(Path([(cx + w * .14, hip), (cx + w * .16, bottom)]))
        hands = (cx - w * .35, y + h * .5, w * .7, h * .1)
    s.anchors["person"] = (x, y, w, h)
    s.anchors["head"] = (cx - rx, hy - hr, 2 * rx, 2 * hr)
    s.anchors["face"] = (cx - rx * .8, hy - hr * .6, rx * 1.6, hr * 1.4)
    s.anchors["eyes"] = (cx - rx * .6, hy - hr * .3, rx * 1.2, hr * .35)
    s.anchors["chest"] = (cx - w * .3, sh_y, w * .6, (bottom - sh_y) * .5)
    s.anchors["hands"] = hands
    return s


def hand(x, y, w, h, pose="open", **_):
    """Hand pointing up (wrist at the bottom). pose: open (palm), hold (fist around a stem/handle), point."""
    s = Shape()
    pw, ph = w, h * .45
    py = y + h * .45
    if pose == "open":
        fw = pw / 4.6
        for i, fl in enumerate((.82, .98, .92, .74)):
            fx = x + pw * .12 + i * fw * 1.05
            ft = py - h * .45 * fl
            s.paths.append(Path([(fx, py)] + arc(fx + fw / 2, ft + fw / 2, fw / 2, fw / 2, 180, 360, 8).pts + [(fx + fw, py)]))
        s.paths.append(Path([(x + pw * .12, py + ph * .3), (x - pw * .1, py - ph * .1), (x - pw * .02, py - ph * .3), (x + pw * .14, py + ph * .02)]))
        s.paths.append(Path([(x + pw * .12, py), (x + pw * .12, py + ph * .7), (x + pw * .3, y + h)]))
        s.paths.append(Path([(x + pw * .12 + 4 * fw * 1.05 - fw * .05, py), (x + pw * .95, py + ph * .7), (x + pw * .78, y + h)]))
    elif pose == "point":
        fw = pw / 4.6
        s.paths.append(Path([(x + pw * .3, py)] + arc(x + pw * .3 + fw / 2, y + fw / 2, fw / 2, fw / 2, 180, 360, 8).pts + [(x + pw * .3 + fw, py)]))
        s.paths.append(rrect(x + pw * .2, py - ph * .05, pw * .7, ph * .7, pw * .2))
        s.paths.append(Path([(x + pw * .3, py + ph * .65), (x + pw * .35, y + h)]))
        s.paths.append(Path([(x + pw * .8, py + ph * .65), (x + pw * .75, y + h)]))
        s.anchors["tip"] = (x + pw * .3, y, fw, fw)
    else:  # hold
        s.paths.append(rrect(x + pw * .1, py - ph * .4, pw * .8, ph * .8, pw * .25))
        for i in range(1, 4):
            s.paths.append(line(x + pw * (.1 + .2 * i), py - ph * .4, x + pw * (.1 + .2 * i), py - ph * .1, "dim"))
        s.paths.append(Path([(x + pw * .2, py + ph * .38), (x + pw * .28, y + h)]))
        s.paths.append(Path([(x + pw * .8, py + ph * .38), (x + pw * .72, y + h)]))
    s.anchors["hand"] = (x - pw * .1, y, w * 1.1, h)
    return s


def fork(x, y, w, h, **_):
    """Vertical fork, tines up. Box = whole fork."""
    s = Shape()
    cx = x + w / 2
    th = h * .28
    for d in (0, .33, .66, 1):
        s.paths.append(line(x + w * d, y, x + w * d, y + th))
    s.paths.append(Path([(x, y + th), (x + w * .1, y + th * 1.3), (cx - w * .12, y + th * 1.5), (cx - w * .1, y + h)]))
    s.paths.append(Path([(x + w, y + th), (x + w * .9, y + th * 1.3), (cx + w * .12, y + th * 1.5), (cx + w * .1, y + h)]))
    s.anchors["fork"] = (x, y, w, h)
    s.anchors["tines"] = (x, y, w, th)
    return s


def knife(x, y, w, h, **_):
    """Vertical knife, blade up. Box = whole knife."""
    s = Shape()
    bl = h * .58
    s.paths.append(Path([(x + w * .15, y + bl), (x + w * .15, y + h * .08), (x + w * .5, y), (x + w * .85, y + h * .2), (x + w * .85, y + bl)], True))
    s.paths.append(rrect(x, y + bl, w, h - bl, w * .3))
    s.paths.append(line(x + w * .3, y + h * .1, x + w * .3, y + bl * .9, "accent"))
    s.anchors["knife"] = (x, y, w, h)
    s.anchors["blade"] = (x, y, w, bl)
    return s


def board(x, y, w, h, **_):
    """Cutting board, top view, with a handle hole."""
    s = Shape()
    s.paths.append(rrect(x, y, w, h, min(w, h) * .08))
    s.paths.append(arc(x + w * .92, y + h / 2, min(w, h) * .04, min(w, h) * .04))
    s.paths.append(line(x + w * .05, y + h * .9, x + w * .8, y + h * .9, "dim"))
    s.anchors["board"] = (x, y, w, h)
    return s


def veg(cx, cy, r, kind="tomato", halves=False, **_):
    """Top/side view produce. kind: tomato, lemon, onion. halves: two cut halves side by side."""
    s = Shape()
    if halves:
        for d in (-1, 1):
            hx = cx + d * r * 1.15
            s.paths.append(arc(hx, cy, r, r))
            s.paths.append(arc(hx, cy, r * .78, r * .78, tone="dim"))
            for a in range(0, 360, 60):
                s.paths.append(line(hx, cy, hx + r * .7 * math.cos(math.radians(a)), cy + r * .7 * math.sin(math.radians(a)), "accent"))
        s.anchors["veg"] = (cx - r * 2.2, cy - r, r * 4.4, 2 * r)
        s.anchors["cut"] = (cx - r * 2.2, cy - r, r * 4.4, 2 * r)
        return s
    s.paths.append(arc(cx, cy, r, r * (.85 if kind == "lemon" else 1)))
    if kind == "tomato":
        for a in range(-90, 270, 72):
            s.paths.append(line(cx, cy - r * .1, cx + r * .3 * math.cos(math.radians(a)), cy - r * .1 + r * .3 * math.sin(math.radians(a)), "accent"))
    elif kind == "onion":
        s.paths.append(arc(cx, cy, r * .6, r * .9, -80, 80, 10, "dim"))
        s.paths.append(arc(cx, cy, r * .6, r * .9, 100, 260, 10, "dim"))
    s.anchors["veg"] = (cx - r, cy - r, 2 * r, 2 * r)
    return s


def tray(x, y, w, h, items="buns", count=4, **_):
    """Baking tray, front 3/4 view. items: buns, croissants, cookies, none. Steam above when items."""
    s = Shape()
    s.paths.append(Path([(x, y + h * .3), (x + w, y + h * .3), (x + w * .96, y + h), (x + w * .04, y + h)], True))
    s.paths.append(line(x + w * .02, y + h * .5, x + w * .98, y + h * .5, "dim"))
    iw = w * .8 / max(1, count)
    for i in range(count if items != "none" else 0):
        ix = x + w * .1 + iw * i + iw * .1
        if items == "croissants":
            s.paths.append(Path(arc(ix + iw * .4, y + h * .3, iw * .45, h * .28, 180, 360, 12).pts, False))
            for k in (.25, .5, .75):
                s.paths.append(line(ix + iw * .8 * k, y + h * .05, ix + iw * .8 * k - iw * .05, y + h * .3, "accent"))
        else:
            s.paths.append(arc(ix + iw * .4, y + h * .3, iw * .4, h * .3 if items == "buns" else h * .12, 180, 360, 12))
            s.paths.append(arc(ix + iw * .4, y + h * .18, iw * .15, h * .04, 200, 340, 6, "accent"))
    if items != "none":
        for i in range(3):
            sx = x + w * (.3 + .2 * i)
            s.paths.append(wave(y, y - h * (.9 + .15 * i), sx, w * .02, 1.2, "dim", vertical=True))
        s.anchors["steam"] = (x + w * .25, y - h * 1.1, w * .5, h * 1.1)
    s.anchors["tray"] = (x, y, w, h)
    s.anchors["items"] = (x + w * .08, y, w * .84, h * .35)
    return s


def oven(x, y, w, h, open=True, **_):
    """Deck/convection oven front. open: door down with the tray slid out toward the viewer."""
    s = Shape()
    s.paths.append(rect(x, y, w, h))
    s.paths.append(rect(x + w * .08, y + h * .12, w * .84, h * .55))
    for i in range(4):
        s.paths.append(arc(x + w * (.2 + .2 * i), y + h * .06, w * .03, w * .03, tone="dim"))
    s.paths.append(line(x + w * .1, y + h * .8, x + w * .9, y + h * .8, "dim"))
    if open:
        s.paths.append(Path([(x + w * .08, y + h * .67), (x - w * .05, y + h * .95), (x + w * 1.05, y + h * .95), (x + w * .92, y + h * .67)]))
        s.paths.append(line(x + w * .15, y + h * .32, x + w * .85, y + h * .32, "dim"))
        s.paths.append(line(x + w * .15, y + h * .5, x + w * .85, y + h * .5, "dim"))
    else:
        s.paths.append(rect(x + w * .14, y + h * .18, w * .72, h * .43, "dim"))
        s.paths.append(line(x + w * .25, y + h * .63, x + w * .75, y + h * .63, "accent"))
    s.anchors["oven"] = (x, y, w, h)
    s.anchors["mouth"] = (x + w * .08, y + h * .12, w * .84, h * .55)
    return s


def bread(x, y, w, h, kind="loaf", torn=False, **_):
    """Side view bread. kind: loaf, croissant, bun. torn: split in two with crumb showing (accent)."""
    s = Shape()
    if kind == "croissant":
        s.paths.append(Path(arc(x + w / 2, y + h, w / 2, h, 180, 360, 20).pts))
        s.paths.append(line(x, y + h, x + w, y + h))
        for k in (.25, .42, .58, .75):
            s.paths.append(arc(x + w * k, y + h, w * .08, h * (1 - abs(k - .5) * 1.3), 200, 340, 6, "dim"))
        s.anchors["bread"] = (x, y, w, h)
        s.anchors["crumb"] = (x + w * .3, y + h * .3, w * .4, h * .7)
        return s
    if torn:
        gap = w * .12
        hw = (w - gap) / 2
        s.paths.append(Path(arc(x + hw, y + h, hw, h, 180, 280, 12).pts + [(x + hw * .95, y + h * .3), (x + hw * 1.02, y + h * .55), (x + hw * .94, y + h * .8), (x + hw, y + h)]))
        s.paths.append(line(x, y + h, x + hw, y + h))
        s.paths.append(Path(arc(x + hw + gap, y + h, hw, h, 260, 360, 12).pts[::-1][::-1] ))
        s.paths.append(Path([(x + hw + gap, y + h * .1), (x + hw + gap * 1.08, y + h * .45), (x + hw + gap * .96, y + h * .75), (x + hw + gap, y + h)]))
        s.paths.append(line(x + hw + gap, y + h, x + w, y + h))
        for i in range(5):
            s.paths.append(arc(x + hw * .9 - (i % 2) * hw * .1, y + h * (.3 + .13 * i), w * .012, w * .012, tone="accent"))
            s.paths.append(arc(x + hw + gap * 1.1 + (i % 2) * hw * .1, y + h * (.35 + .12 * i), w * .012, w * .012, tone="accent"))
        s.anchors["crumb"] = (x + hw * .7, y + h * .2, gap + hw * .6, h * .8)
    else:
        s.paths.append(Path(arc(x + w / 2, y + h, w / 2, h, 180, 360, 24).pts))
        s.paths.append(line(x, y + h, x + w, y + h))
        for k in (.3, .5, .7):
            s.paths.append(line(x + w * (k - .06), y + h * .25, x + w * (k + .06), y + h * .1, "accent"))
        s.anchors["crumb"] = (x + w * .3, y + h * .2, w * .4, h * .8)
    s.anchors["bread"] = (x, y, w, h)
    return s


def display_case(x, y, w, h, rows=2, items=4, **_):
    """Glass pastry case, front view, with rows of items on trays."""
    s = Shape()
    s.paths.append(Path([(x, y + h), (x, y + h * .25), (x + w * .06, y), (x + w, y), (x + w, y + h)]))
    s.paths.append(line(x, y + h, x + w, y + h))
    s.paths.append(line(x + w * .1, y + h * .05, x + w * .3, y + h * .2, "dim"))
    rh = h * .75 / rows
    for r in range(rows):
        ry = y + h * .25 + rh * (r + 1) - rh * .15
        s.paths.append(line(x + w * .03, ry, x + w * .97, ry, "dim"))
        iw = w * .9 / items
        for i in range(items):
            ix = x + w * .05 + iw * i
            if (i + r) % 2:
                s.paths.append(arc(ix + iw * .45, ry, iw * .35, rh * .45, 180, 360, 12))
            else:
                s.paths.append(Path([(ix + iw * .1, ry), (ix + iw * .1, ry - rh * .4), (ix + iw * .8, ry - rh * .55), (ix + iw * .8, ry)]))
            s.anchors[f"item{r * items + i + 1}"] = (ix + iw * .05, ry - rh * .6, iw * .85, rh * .6)
    s.anchors["case"] = (x, y, w, h)
    return s


def paper_bag(x, y, w, h, text="", **_):
    s = Shape()
    s.paths.append(Path([(x, y + h * .12), (x, y + h), (x + w, y + h), (x + w, y + h * .12)]))
    s.paths.append(wave(x, x + w, y + h * .12, h * .02, 4))
    s.paths.append(arc(x + w * .5, y + h * .4, w * .18, w * .18, tone="accent"))
    if text:
        s.texts.append(Text(x + w / 2, y + h * .7, text, h * .1))
    s.anchors["bag"] = (x, y, w, h)
    s.anchors["logo"] = (x + w * .3, y + h * .3, w * .4, h * .25)
    return s


def tap(x, y, w, h, count=3, **_):
    """Beer tap tower with handles, front view. Box = tower area down to the drip tray."""
    s = Shape()
    s.paths.append(rect(x, y + h * .25, w, h * .12))
    s.paths.append(line(x, y + h, x + w, y + h))
    s.paths.append(rect(x + w * .05, y + h * .95, w * .9, h * .05, "dim"))
    for i in range(count):
        tx = x + w * (i + .5) / count
        s.paths.append(rrect(tx - w * .04, y, w * .08, h * .25, w * .03))
        s.paths.append(Path([(tx, y + h * .37), (tx, y + h * .45), (tx + w * .03, y + h * .48)]))
        s.anchors[f"tap{i + 1}"] = (tx - w * .08, y, w * .16, h * .5)
    s.paths.append(rrect(x + w * .48, y, w * .06, h * .25, w * .03, "accent"))
    s.anchors["tower"] = (x, y, w, h)
    s.anchors["spout"] = (x + w / 2 - w * .15, y + h * .37, w * .3, h * .6)
    return s


def mirror(x, y, w, h, **_):
    """Salon mirror with bulbs around it."""
    s = Shape()
    s.paths.append(rrect(x, y, w, h, w * .08))
    s.paths.append(rrect(x + w * .06, y + h * .05, w * .88, h * .9, w * .06, "dim"))
    for i in range(4):
        s.paths.append(arc(x + w * (.2 + .2 * i), y - w * .03, w * .025, w * .025, tone="accent"))
    s.paths.append(line(x + w * .15, y + h * .2, x + w * .35, y + h * .08, "dim"))
    s.anchors["mirror"] = (x, y, w, h)
    s.anchors["glass"] = (x + w * .06, y + h * .05, w * .88, h * .9)
    return s


def salon_chair(x, y, w, h, facing="front", **_):
    """Styling chair on a pump base. facing: front, left, right."""
    s = Shape()
    if facing == "front":
        s.paths.append(rrect(x + w * .15, y, w * .7, h * .5, w * .1))
        s.paths.append(rrect(x + w * .05, y + h * .45, w * .9, h * .14, w * .05))
        s.paths.append(line(x, y + h * .35, x + w * .15, y + h * .35))
        s.paths.append(line(x + w, y + h * .35, x + w * .85, y + h * .35))
    else:
        sgn = 1 if facing == "right" else -1
        bx = x + (w * .15 if sgn > 0 else w * .7)
        s.paths.append(rrect(bx, y, w * .15, h * .55, w * .05))
        s.paths.append(rrect(x + w * .1, y + h * .45, w * .8, h * .12, w * .04))
        s.paths.append(line(x + w * .2, y + h * .35, x + w * .8, y + h * .35))
    s.paths.append(line(x + w / 2, y + h * .59, x + w / 2, y + h * .9))
    s.paths.append(arc(x + w / 2, y + h * .95, w * .35, h * .05))
    s.paths.append(line(x + w * .55, y + h * .8, x + w * .75, y + h * .88, "accent"))
    s.anchors["chair"] = (x, y, w, h)
    s.anchors["seat"] = (x, y, w, h * .6)
    return s


def scissors(x, y, w, h, **_):
    """Open scissors, blades up."""
    s = Shape()
    cx = x + w / 2
    py = y + h * .55
    s.paths.append(Path([(cx, py), (x + w * .1, y), (x + w * .28, y + h * .05), (cx, py)], True))
    s.paths.append(Path([(cx, py), (x + w * .9, y), (x + w * .72, y + h * .05), (cx, py)], True, "accent"))
    s.paths.append(arc(cx, py, w * .04, w * .04))
    s.paths.append(line(cx, py, x + w * .3, y + h * .75))
    s.paths.append(line(cx, py, x + w * .7, y + h * .75))
    s.paths.append(arc(x + w * .25, y + h * .85, w * .15, h * .12))
    s.paths.append(arc(x + w * .75, y + h * .85, w * .15, h * .12))
    s.anchors["scissors"] = (x, y, w, h)
    s.anchors["blades"] = (x, y, w, h * .55)
    return s


def brush(x, y, w, h, kind="round", **_):
    """Round hair brush (kind=round) or comb (kind=comb), horizontal."""
    s = Shape()
    if kind == "comb":
        s.paths.append(rect(x, y, w, h * .3))
        for i in range(14):
            bx = x + w * (i + .5) / 14
            s.paths.append(line(bx, y + h * .3, bx, y + h))
    else:
        bw = w * .55
        s.paths.append(rrect(x, y + h * .2, bw, h * .6, h * .3))
        for i in range(8):
            bx = x + bw * (i + .5) / 8
            s.paths.append(line(bx, y, bx, y + h * .2, "dim"))
            s.paths.append(line(bx, y + h * .8, bx, y + h, "dim"))
        s.paths.append(rrect(x + bw, y + h * .35, w - bw, h * .3, h * .15))
    s.anchors["brush"] = (x, y, w, h)
    return s


def book(x, y, w, h, open=True, **_):
    """Top view book (open spread or closed cover)."""
    s = Shape()
    if open:
        s.paths.append(Path([(x, y + h * .05), (x + w / 2, y + h * .1), (x + w, y + h * .05), (x + w, y + h), (x + w / 2, y + h * 1.04), (x, y + h)], True))
        s.paths.append(line(x + w / 2, y + h * .1, x + w / 2, y + h * 1.04))
        for i in range(5):
            ly = y + h * (.25 + .13 * i)
            s.paths.append(line(x + w * .07, ly, x + w * .43, ly, "dim"))
            s.paths.append(line(x + w * .57, ly, x + w * .93, ly, "dim"))
    else:
        s.paths.append(rect(x, y, w, h))
        s.paths.append(line(x + w * .08, y, x + w * .08, y + h))
    s.anchors["book"] = (x, y, w, h)
    return s


def price_tag(x, y, w, h, text="$4.50", **_):
    s = Shape()
    s.paths.append(Path([(x + h * .4, y), (x + w, y), (x + w, y + h), (x + h * .4, y + h), (x, y + h / 2)], True, "accent"))
    s.paths.append(arc(x + h * .45, y + h / 2, h * .1, h * .1, tone="accent"))
    s.texts.append(Text(x + w * .6, y + h / 2, text, h * .5, "accent"))
    s.anchors["tag"] = (x, y, w, h)
    return s


def frame_edge(x, y, w, h, kind="plant", side="left", **_):
    """Foreground blocker you shoot from behind for a reveal: a door frame / wall edge (kind=wall) or a big leafy plant (kind=plant)."""
    s = Shape()
    if kind == "wall":
        s.paths.append(rect(x, y, w, h))
        ex = x + w if side == "left" else x
        s.paths.append(line(ex + (-w * .15 if side == "left" else w * .15), y, ex + (-w * .15 if side == "left" else w * .15), y + h, "dim"))
    else:
        cx = x + w / 2
        s.paths.append(line(cx, y + h, cx, y + h * .1))
        for i in range(7):
            ly = y + h * (.15 + .11 * i)
            d = -1 if i % 2 else 1
            s.paths.append(arc(cx + d * w * .28, ly, w * .3, h * .045, (d < 0) * 180 - 20, (d < 0) * 180 + 200, 14))
    s.anchors["edge"] = (x, y, w, h)
    return s


REGISTRY = {f.__name__: f for f in (
    door, window, awning, sign, facade, room, table, chair, bar_counter, pendant, shelf, plant,
    menu_board, cup, latte, plate, glass, bottle, phone, arrow, path, box, ellipse, text, trace,
    person, hand, fork, knife, board, veg, tray, oven, bread, display_case, paper_bag, tap, mirror,
    salon_chair, scissors, brush, book, price_tag, frame_edge)}


def build(spec: dict) -> Shape:
    kind = spec["type"]
    if kind not in REGISTRY:
        raise ValueError(f"unknown element type '{kind}'. Known: {', '.join(sorted(REGISTRY))}")
    args = {k: v for k, v in spec.items() if k not in ("type", "id", "in", "out", "draw", "rotate", "tone_override", "opacity")}
    shape = REGISTRY[kind](**args)
    if spec.get("tone_override"):
        for p in shape.paths:
            p.tone = spec["tone_override"]
        for t in shape.texts:
            t.tone = spec["tone_override"]
    rot = spec.get("rotate")
    if rot:
        bx, by, bw, bh = bbox_of(shape.paths)
        cx, cy = bx + bw / 2, by + bh / 2
        c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        f = lambda p: (cx + (p[0] - cx) * c - (p[1] - cy) * s_, cy + (p[0] - cx) * s_ + (p[1] - cy) * c)
        for p in shape.paths:
            p.pts = [f(q) for q in p.pts]
        shape.anchors = {k: _rot_box(v, f) for k, v in shape.anchors.items()}
    return shape


def _rot_box(b, f):
    x, y, w, h = b
    pts = [f(p) for p in ((x, y), (x + w, y), (x, y + h), (x + w, y + h))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
