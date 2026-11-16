#!/usr/bin/env python3
"""Writes guides/coverage.md: per script step the guide, its style assets, reused or new, angle, move, hand-over,
the jump check, the simulation and what the ghost cannot verify. Run after build_guides.py and render_3d.py."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDES = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import catalog  # noqa: E402

rows = catalog.catalog()
groups = catalog.guides(rows)
notes = json.load(open(os.path.join(GUIDES, "build_notes.json")))
jumps = json.load(open(os.path.join(GUIDES, "jump_check.json")))
sim = {}
for line in open(os.path.join(GUIDES, "simulation.txt")):
    p = line.split()
    if len(p) < 9 or p[0] == "scenario":
        continue
    sim.setdefault(p[0], []).append(p)
scen = {g: json.load(open(os.path.join(GUIDES, "scenarios", g + ".json"))) for g in groups}
three = {g: json.load(open(os.path.join(GUIDES, "overlays", "3d", g + ".json"))) for g in groups}

NOT_VERIFIED = {"still": "the subject's own action is timed, not verified"}


def sim_health(gid):
    """on-pace time against the scene length and the lagging user's lead; the id is cut to 24 chars in the output."""
    rs = sim.get(gid[:24], [])
    worst = []
    for p in rs:
        name, step, user, done, time, tmpl, wait, catch, lead = p[:9]
        if user == "on_pace":
            ratio = float(time) / max(float(tmpl), 0.01)
            limit = 1.8 if float(tmpl) < 2 else 1.3
            if ratio > limit + 0.01:
                worst.append(f"{step} on-pace {ratio:.2f}x")
        if user == "lagging" and float(lead) > 25:
            worst.append(f"{step} lead {lead}%")
    if not rs:
        return "no follow step (hold or still only)"
    return "healthy" if not worst else "; ".join(worst)


def cannot_verify(gid, r):
    out = []
    kinds = [s["kind"] for s in scen[gid]["steps"]]
    if "still" in kinds:
        out.append("subject action (timed still)")
    if r["angle"] in ("high", "low", "top-down", "pov", "over-shoulder", "eye-level"):
        out.append("absolute height: only the tilt band is checked")
    if r["move"] == "static" and "still" not in kinds:
        out.append("framing and stillness only")
    if r["move"] == "reveal-from-behind":
        out.append("the blocker is not tracked, the slide is measured as a truck")
    if r["transition"] in ("match-cut", "pull-back-reveal"):
        out.append("the next step's start pose is not compared with this end pose")
    return "; ".join(out)


lines = ["# Guide coverage", "",
         f"{len(rows)} steps, {len(groups)} guides ({sum(1 for g in groups.values() if g[0]['reused'])} reused kit scenes, "
         f"{sum(1 for g in groups.values() if not g[0]['reused'])} new). Every guide has a schematic APNG and strip in "
         "`overlays/schematic/`, a 3D camera-path spec and preview strip in `overlays/3d/`, and a compiled scenario in "
         "`scenarios/`. Jump check: the largest share of a frame's ink that lies more than 4% of the width away from the "
         "previous frame's ink, outside whips, the first second of draw-on and the final fade (a teleport is over 35%). "
         "Simulation: `simulate.py` on the compiled scenario; on-pace completion within 1.3x the move (1.8x under 2 s), "
         "a lagging user never more than 25% behind.", "",
         "## Per step", "",
         "| script | step | guide | reused | angle | move | hand-over | schematic | 3D model | 3D strip | jump check | simulation | the ghost cannot verify |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    gid = r["guide"]
    j = jumps.get(gid, {})
    jump = f"ok (max {j.get('worst_uncovered_share', 0):.0%})" if not j.get("jumps") else f"FLAGGED at {j['jumps'][0][0]}s"
    t = three[gid]
    model = t["kit_model"] or f"usdz {t['model']}"
    lines.append(f"| {r['template']} | {r['step']} | `{gid}` | {'yes' if r['reused'] else 'no'} | {r['angle']} | {r['move']} | "
                 f"{r['transition']} | `{gid}.png` | {model} | `{gid}_strip.png` | {jump} | {sim_health(gid)} | {cannot_verify(gid, r)} |")

lines += ["", "## Per guide", "", "| guide | steps | camera | anchor | compiled steps | notes |", "|---|---|---|---|---|---|"]
for gid, steps in sorted(groups.items()):
    sc = scen[gid]
    chain = " > ".join(s["kind"] if s["kind"] != "follow" else s["action"] + ("" if "direction" not in s else " " + s["direction"]) for s in sc["steps"])
    anchor = sc["anchor"]["kind"] + (":" + sc["anchor"]["type"] if sc["anchor"].get("type") else "")
    lines.append(f"| `{gid}` | {len(steps)} | {sc['camera']} | {anchor} | {chain} | {'; '.join(notes.get(gid, []))} |")

open(os.path.join(GUIDES, "coverage.md"), "w").write("\n".join(lines) + "\n")
empty = [l for l in lines if "| |" in l or "||" in l.replace("|---", "")]
print("coverage.md written;", len(rows), "step rows;", "rows with an empty cell:", len(empty))
