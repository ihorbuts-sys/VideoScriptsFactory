import bpy, sys, json, math, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

out_path = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
gid = sc.name.split("/")[-1].strip()
meta = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "meta.json")))
N = meta["frame_count"]; fps = meta.get("fps", 15)
hold = meta.get("target_hold_frames", 8); final_hold = meta.get("final_hold_frames", 7)
setup = meta.get("setup_frames", 0)
cam = sc.objects["Visitor phone"]
dg = bpy.context.evaluated_depsgraph_get()


def role(o):
    return o.get("composition_role") or o.get("role")


def world_verts(o):
    if o.type != "MESH":
        return []
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    vs = [ev.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return vs


def bbox(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs),
            min(c.z for c in cs), max(c.z for c in cs))


sc.frame_set(1)
heroes = [o for o in sc.objects if o.type == "MESH" and role(o) == "hero"]
hero_source = "composition_role hero"
if not heroes:
    heroes = [o for o in sc.objects if o.type == "MESH" and o.get("p0_framing_mask")
              and "contour skin" in o.name]
    hero_source = "face safety mask (creator skin contour inside the mask)"
if not heroes:
    heroes = [o for o in sc.objects if o.type == "MESH" and o.get("p0_framing_mask")]
    hero_source = "framing mask"
hverts = []
for o in heroes:
    hverts += world_verts(o)
hx = [v.x for v in hverts]; hy = [v.y for v in hverts]; hz = [v.z for v in hverts]
hero_centre = Vector(((min(hx) + max(hx)) / 2, (min(hy) + max(hy)) / 2, (min(hz) + max(hz)) / 2))

SURF_WORDS = ("tabletop", "counter top", "bar top", "table top", "worktop", "shelf", "counter surface")


def surfaces():
    res = []
    for o in sc.objects:
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if any(w in n for w in SURF_WORDS) and "reflect" not in n and "edge" not in n:
            b = bbox(o)
            if (b[1] - b[0]) > 0.25 and (b[3] - b[2]) > 0.2 and (b[5] - b[4]) < 0.12:
                res.append((o.name, b))
    return res


SURFS = surfaces()


def surface_under(p, below_z=None):
    best = ("floor (z=0)", 0.0)
    for name, b in SURFS:
        if b[0] - 0.02 <= p.x <= b[1] + 0.02 and b[2] - 0.02 <= p.y <= b[3] + 0.02:
            top = b[5]
            if below_z is not None and top > below_z + 0.02:
                continue
            if top > best[1]:
                best = (name, top)
    return best


hero_surface = surface_under(hero_centre, below_z=min(hz))


def nearest_surface_to_cam(p):
    # surface directly under the lens, else the closest table/counter edge within 0.6 m (phone held past the edge)
    s = surface_under(p, below_z=p.z)
    if s[0] != "floor (z=0)":
        return s + (0.0,)
    best = None
    for name, b in SURFS:
        if b[5] > p.z + 0.02:
            continue
        dx = max(b[0] - p.x, 0, p.x - b[1]); dy = max(b[2] - p.y, 0, p.y - b[3])
        d = math.hypot(dx, dy)
        if d < 0.6 and (best is None or d < best[2]):
            best = (name, b[5], d)
    return best or ("floor (z=0)", 0.0, 0.0)


def pose(f):
    sc.frame_set(f)
    mw = cam.matrix_world.copy()
    loc = mw.translation.copy()
    rot = mw.to_3x3().normalized()
    fwd = rot @ Vector((0, 0, -1)); up = rot @ Vector((0, 1, 0)); right = rot @ Vector((1, 0, 0))
    pitch = math.degrees(-math.asin(max(-1, min(1, fwd.z))))
    roll = math.degrees(math.atan2(right.z, up.z))
    yaw = math.degrees(math.atan2(fwd.y, fwd.x))
    return dict(f=f, loc=loc, fwd=fwd, pitch=pitch, roll=roll, yaw=yaw, lens=cam.data.lens,
                shift=(cam.data.shift_x, cam.data.shift_y))


poses = {f: pose(f) for f in range(1, N + 1)}
first_demo = hold + 1
seq = list(range(first_demo, N + 1))
steps = []
for a, b in zip(seq[:-1], seq[1:]):
    pa, pb = poses[a], poses[b]
    d = (pb["loc"] - pa["loc"]).length
    ang = math.degrees(pa["fwd"].angle(pb["fwd"])) if (pa["fwd"] - pb["fwd"]).length > 1e-9 else 0.0
    steps.append((a, b, d, ang))
moving = [s for s in steps if s[2] > 1e-5 or s[3] > 1e-3]
start_f = moving[0][0] if moving else first_demo
end_f = moving[-1][1] if moving else first_demo
dur = (end_f - start_f) / fps
path = sum(s[2] for s in steps)
ang_total = sum(s[3] for s in steps)
peak_v = max((s[2] * fps for s in steps), default=0)
peak_w = max((s[3] * fps for s in steps), default=0)
ps, pe = poses[start_f], poses[1]

# orbit arc around hero (azimuth of camera position about the hero centre)
def az(p):
    v = p["loc"] - hero_centre
    return math.degrees(math.atan2(v.y, v.x))
az_total = 0.0
for a, b, *_ in steps:
    dz = az(poses[b]) - az(poses[a])
    dz = (dz + 180) % 360 - 180
    az_total += dz

# lens clearance along the move
clear = []
for f in [1] + seq:
    p = poses[f]
    s = nearest_surface_to_cam(p["loc"])
    clear.append((p["loc"].z - s[1], f, s[0], s[2]))
min_clear = min(clear)


def project(f):
    sc.frame_set(f)
    xs, ys, zs = [], [], []
    for v in hverts:
        co = world_to_camera_view(sc, cam, v)
        xs.append(co.x); ys.append(co.y); zs.append(co.z)
    if not xs or min(zs) <= 0:
        return None
    return dict(x_min=min(xs), x_max=max(xs), y_min_from_top=1 - max(ys), y_max_from_top=1 - min(ys),
                fill_width=max(xs) - min(xs), fill_height=max(ys) - min(ys),
                centre_x=(min(xs) + max(xs)) / 2, centre_from_top=1 - (min(ys) + max(ys)) / 2)


def root(o):
    while o.parent is not None:
        o = o.parent
    return o
group_roots = {root(o) for o in heroes if o.parent is not None}
group_roots = {g for g in group_roots if "cast" not in g.name.lower() and "rig" not in g.name.lower()}
gverts = []
group_names = []
for g in group_roots:
    group_names.append(g.name)
    for o in [g] + list(g.children_recursive):
        gverts += world_verts(o)


def project_vs(f, vs):
    global hverts
    keep = hverts; hverts = vs
    try:
        return project(f)
    finally:
        hverts = keep


# hero verts are static from frame 1 (objects present from frame 1); hands etc. may move but heroes are props
sc.frame_set(1)
tgt = project(1)
st = project(start_f)

res_x, res_y = sc.render.resolution_x, sc.render.resolution_y
sw = cam.data.sensor_width
# vertical sensor fit: sensor_width maps to the image height
if cam.data.sensor_fit == "VERTICAL":
    vfov = 2 * math.degrees(math.atan(sw / 2 / cam.data.lens))
    hfov = 2 * math.degrees(math.atan(sw / 2 * res_x / res_y / cam.data.lens))
else:
    hfov = 2 * math.degrees(math.atan(sw / 2 / cam.data.lens))
    vfov = 2 * math.degrees(math.atan(sw / 2 * res_y / res_x / cam.data.lens))

cam_surf_end = nearest_surface_to_cam(pe["loc"]); cam_surf_start = nearest_surface_to_cam(ps["loc"])
PHONE_BELOW_LENS = 0.132  # iPhone ~14.7 cm long, rear lens ~1.5 cm from the top edge (judgement)


def portrait_check(f):
    sc.frame_set(f)
    mw = cam.matrix_world
    lens = mw.translation.copy()
    up = (mw.to_3x3().normalized() @ Vector((0, 1, 0)))
    worst = (-9.0, None)
    for i in range(1, 11):
        q = lens - up * (PHONE_BELOW_LENS * i / 10)
        tops = [b[5] for n, b in SURFS if b[0] <= q.x <= b[1] and b[2] <= q.y <= b[3] and q.z < b[5] and lens.z >= b[5] - 0.005]
        depth = max([t - q.z for t in tops] + [-q.z if q.z < 0 else -9.0])
        if depth > worst[0]:
            worst = (depth, i)
    inside = None
    for n, b in SURFS:
        if b[0] <= lens.x <= b[1] and b[2] <= lens.y <= b[3] and lens.z >= b[5] - 0.005:
            inset = min(lens.x - b[0], b[1] - lens.x, lens.y - b[2], b[3] - lens.y)
            inside = (n, inset)
    return worst[0], inside


pc = {f: portrait_check(f) for f in [1] + seq}
blocked = [f for f, (d, _) in pc.items() if d > 0]
worst_f = max(pc, key=lambda f: pc[f][0])
over = [f for f, (_, ins) in pc.items() if ins]
eyes = [o for o in sc.objects if o.type == "MESH" and o.get("p0_framing_mask") and "eye" in o.name.lower()]
eye_info = None
if eyes:
    ev = []
    for o in eyes:
        ev += world_verts(o)
    ec = Vector((sum(v.x for v in ev) / len(ev), sum(v.y for v in ev) / len(ev), sum(v.z for v in ev) / len(ev)))
    sc.frame_set(1)
    co = world_to_camera_view(sc, cam, ec)
    eye_info = dict(eye_z=round(ec.z, 3), cam_minus_eye_z=round(poses[1]["loc"].z - ec.z, 3),
                    dist_cam_eye=round((poses[1]["loc"] - ec).length, 3), eye_y_from_top=round(1 - co.y, 3),
                    eye_x=round(co.x, 3))
r = lambda v, n=3: round(v, n)
data = dict(
    id=gid, frames=N, fps=fps, hold=hold, setup_frames=setup, final_hold=final_hold,
    hero_source=hero_source, hero_objects=sorted({o.name for o in heroes})[:6], hero_count=len(heroes),
    hero_centre=[r(v) for v in hero_centre], hero_size=[r(max(hx) - min(hx)), r(max(hy) - min(hy)), r(max(hz) - min(hz))],
    hero_surface=dict(name=hero_surface[0], top_z=r(hero_surface[1])),
    start_frame=start_f, end_frame=end_f, move_duration_s=r(dur, 2),
    start_loc=[r(v) for v in ps["loc"]], end_loc=[r(v) for v in pe["loc"]],
    pitch_start=r(ps["pitch"], 1), pitch_end=r(pe["pitch"], 1),
    pitch_range=[r(min(p["pitch"] for p in poses.values()), 1), r(max(p["pitch"] for p in poses.values()), 1)],
    roll_start=r(ps["roll"], 1), roll_end=r(pe["roll"], 1),
    roll_max_abs=r(max(abs(p["roll"]) for p in poses.values()), 1),
    yaw_change=r(((pe["yaw"] - ps["yaw"] + 180) % 360) - 180, 1),
    height_above_hero_surface_start=r(ps["loc"].z - hero_surface[1]), height_above_hero_surface_end=r(pe["loc"].z - hero_surface[1]),
    cam_surface_start=dict(name=cam_surf_start[0], top_z=r(cam_surf_start[1]), xy_gap=r(cam_surf_start[2]), height=r(ps["loc"].z - cam_surf_start[1])),
    cam_surface_end=dict(name=cam_surf_end[0], top_z=r(cam_surf_end[1]), xy_gap=r(cam_surf_end[2]), height=r(pe["loc"].z - cam_surf_end[1])),
    min_lens_clearance=dict(height=r(min_clear[0]), frame=min_clear[1], surface=min_clear[2], xy_gap=r(min_clear[3])),
    dist_hero_start=r((ps["loc"] - hero_centre).length), dist_hero_end=r((pe["loc"] - hero_centre).length),
    dist_hero_min=r(min((p["loc"] - hero_centre).length for p in poses.values())),
    path_length=r(path), straight_line=r((pe["loc"] - ps["loc"]).length),
    peak_speed=r(peak_v), mean_speed=r(path / dur if dur > 0 else 0),
    view_rotation_total_deg=r(ang_total, 1), peak_angular_speed=r(peak_w, 1),
    mean_angular_speed=r(ang_total / dur if dur > 0 else 0, 1),
    orbit_arc_about_hero_deg=r(az_total, 1),
    lens_mm=cam.data.lens, lens_animated=len({p["lens"] for p in poses.values()}) > 1,
    hfov=r(hfov, 1), vfov=r(vfov, 1), shift=[r(v) for v in poses[1]["shift"]],
    target_projection=tgt and {k: r(v) for k, v in tgt.items()},
    start_projection=st and {k: r(v) for k, v in st.items()},
    portrait_feasible=not blocked, portrait_blocked_frames=len(blocked), portrait_worst_intrusion_m=r(pc[worst_f][0]),
    portrait_worst_frame=worst_f, lens_over_surface_frames=len(over), lens_over_surface_inset_max=r(max([pc[f][1][1] for f in over], default=0)),
    eyes=eye_info,
    hero_group=group_names, group_target_projection=(lambda g: g and {k: r(v) for k, v in g.items()})(project_vs(1, gverts) if gverts else None),
    surfaces_found=[n for n, _ in SURFS][:8],
)
with open(out_path, "w") as fh:
    json.dump(data, fh, indent=1)
print("WROTE", out_path)
