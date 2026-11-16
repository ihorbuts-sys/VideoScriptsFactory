#!/usr/bin/env python3
"""Step -> guide catalog for agent 03.

For every step of scripts/script_templates.json this decides the drawn subject (a family and an item), the
camera (front for selfies), the shot signature from scripts/shot_plan.json, and the guide id: an existing kit
scene when angle, framing, move and hand-over match (REUSE), else a generated scene whose id encodes the
subject and the shot. Steps with the same subject and signature share one guide.

    python3 catalog.py            # prints the assignment table
"""
import json, os, re, sys
import p0_catalog

# P0 is a separate registry: legacy 178-guide assignments remain independent.
_P0_FAMILY={'entrance':('door','door'),'menu-board':('menu','board'),'menu-card':('card','menu'),
    'counter-order':('over_shoulder','counter'),'plate-reveal':('plate','plate'),'hand-off':('hands','handoff'),
    'pour':('latte','latte'),'steam':('cup','cup'),'first-bite':('selfie','bite'),
    'sip':('selfie','sip'),'room-from-table':('room','room'),'verdict':('selfie','one')}
P0={g['id']:dict(family=_P0_FAMILY[g['shotType']][0],item=_P0_FAMILY[g['shotType']][1],
    signature=dict(technique=g['technique'],durationSec=g['durationSec'],transitionOut='cut'),
    composition=g['composition'],sourceSetup=g['sourceSetup']) for g in p0_catalog.registry()['guides']}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATES = json.load(open(os.path.join(ROOT, "scripts", "script_templates.json")))
SHOT_PLAN = json.load(open(os.path.join(ROOT, "scripts", "shot_plan.json")))

# ---------------------------------------------------------------- subject per step: family:item
# A family is one drawing builder in scenes.py; the item picks its variant and the 3D model.
SUBJECT = {}
_RULES = """
bakery-fresh-batch oven oven:tray | shelf case:case | pick hand_pov:pastry | break pastry:break | outro selfie:bag
bakery-morning-shift lights room:lights | dough hands:dough | oven oven:tray | case case:case | first selfie:bag
bakery-sell-out hook selfie:one | line facade:line | tray tray:tray | break pastry:break | verdict selfie:one
bakery-box hook selfie:one | case case:case | pick hand_pov:pastry | box topdown:box | total selfie:one
bakery-ask-the-baker hands hands:dough | ask person:one | answer hand_pov:pastry | inside pastry:break | verdict selfie:one
salon-transformation before selfie:one | space room:room | work hair:work | reveal selfie:reveal | book menu:desk
salon-quick-tour door door:door | room room:salon | details details:salon | host person:host | outro selfie:one
salon-fade before selfie:one | station tools:station | line person:barber | blend hair:blend | reveal selfie:one
salon-nail-set accent nails:accent | colors rail:bottle | tech nails:tech | turns nails:turns | verdict selfie:one
salon-brows before selfie:close | tools tools:tray | process person:process | reveal selfie:reveal | book menu:desk
salon-meet-stylist intro person:one | hands over_shoulder:hands | signature hair:signature | tip selfie:two | book menu:desk
cafe-first-visit pour latte:latte | entrance facade:facade | counter over_shoulder:counter | taste selfie:sip | outro selfie:one
cafe-morning-ritual light room:room | cup cup:cup | pastry pastry:plate | corner table:corner
cafe-before-opening lights room:lights | dial over_shoulder:machine | shot cup:shot | door cup:cup | verdict selfie:one
cafe-seasonal-drink finish latte:latte | build glass:build | sip selfie:sip | board menu:board | verdict selfie:one
cafe-work-spot hook selfie:one | room room:room | desk table:desk | outlets table:outlets | score selfie:one
restaurant-date-night entrance door:door | room room:dining | dish plate:plate | bite selfie:bite | outro selfie:close
restaurant-chef-pick hands hands:hands | cook over_shoulder:hands | plate plate:plate | bite selfie:bite | outro selfie:one
restaurant-family-table kids-plate plate:kids | table room:room | setup topdown:kidstuff | bite selfie:bite | total selfie:one
restaurant-weekend-brunch pour cup:pour | spread plate:spread | hook selfie:one | yolk plate:yolk | room room:cupreveal | verdict selfie:one
restaurant-room-tour hook selfie:one | door door:door | room room:dining | bar bar:bar | seat table:seat | verdict selfie:one
restaurant-lunch-deal plate plate:plate | hook selfie:one | menu card:menu | spread plate:spread | bite selfie:bite | offer selfie:one
bar-night-out pour glass:tap | hook selfie:one | crowd room:crowd | cheers glass:cheers | outro selfie:one
bar-tasting flight glass:flight | taps tap:taps | first selfie:sip | favorite glass:favorite | outro glass:outro
night-live-music walkin door:walkin | hook selfie:one | stage room:stage | drink glass:drink | board menu:event | verdict selfie:one
bar-happy-hour pour glass:pour | board menu:hours | hook selfie:one | bite plate:bite | room room:room | verdict selfie:one
fun-first-try ride room:ride | hook selfie:one | park room:park | ticket card:ticket | verdict selfie:one
fun-group-challenge hook selfie:one | action room:game | reaction person:group | score menu:score | verdict selfie:one
quick-order-rate hold burger:burger | hook selfie:one | inside burger:cut | menu menu:board | score selfie:one
quick-truck-find truck facade:truck | window facade:window | handoff bag:handoff | unwrap topdown:unwrap | bite selfie:bite | where selfie:one
quick-budget-run hook selfie:one | board menu:board | first topdown:first | second burger:burger | receipt card:receipt | best selfie:one
quick-late-night hook selfie:one | sign sign:sign | griddle hands:griddle | order burger:burger | bite selfie:bite | outside facade:facade
quick-the-build grill hands:griddle | build over_shoulder:hands | wrap hands:wrap | inside burger:cut | bite selfie:bite | outro selfie:one
food-review dish plate:plate | arrive facade:facade | order over_shoulder:menu | bite selfie:bite | verdict selfie:one
food-review-drink pour latte:latte | order over_shoulder:counter | cup cup:cup | sip selfie:sip | verdict selfie:one
food-review-pour build glass:pour | glass glass:glass | sip selfie:sip | verdict selfie:one
food-review-sweet case case:case | break pastry:plate | taste selfie:bite | verdict selfie:one
food-review-handheld window facade:window | cut burger:cut | bite selfie:bite | verdict selfie:one
food-review-table spread plate:spread | action plate:sizzle | how plate:spread | bite selfie:bite | verdict selfie:one
pro-before-after problem hands:work | quote person:one | tool hands:tool | detail over_shoulder:hands | result hands:work | verdict selfie:one
pro-meet-the-owner hands hands:hands | bench table:bench | hello selfie:two | craft over_shoulder:hands | tip person:one | prices card:pricelist
pro-first-lesson room room:lesson | teacher selfie:two | hands hands:hands | correction over_shoulder:hands | win hands:hands | schedule menu:schedule
pro-quick-tip hook person:one | wrong hands:tool | right hands:tool | try selfie:one | sign sign:sign
pro-what-it-costs ask selfie:one | one hands:work | two hands:work | three over_shoulder:hands | quote person:one | book selfie:one
shop-find-of-the-day find hand_pov:garment | rail rail:garment | label card:label | tag card:tag | why selfie:one | shopfront sign:sign
shop-try-on pick hand_pov:garment | tag card:tag | curtain door:curtain | reveal person:curtain | second person:mirror | verdict selfie:one | sign sign:sign
shop-budget-challenge budget selfie:one | pick-one hand_pov:item | pick-two rail:shelf | pick-three hands:garment | till over_shoulder:till | haul topdown:haul | verdict selfie:one
shop-owner-pick ask person:one | pull over_shoulder:rail | why person:one | tag card:tag | try person:mirror | verdict selfie:one
shop-music-demo chord hands:guitar | player person:player | wall rail:guitar | try hands:guitar | tip person:one | price card:tag
shop-tour door door:door | inside room:shop | rail rail:garment | corner room:shop | find hands:garment | till selfie:one
fit-first-class door door:door | desk menu:pricelist | coach selfie:two | reps person:full | grip hands:hands | after selfie:one | book menu:schedule
fit-gym-tour kit machine:machine | floor room:gym | racks rail:dumbbell | changing room:changing | owner person:one | outside selfie:one
fit-sauna-session door door:sauna | room room:sauna | bag topdown:bag | step-in person:full | after selfie:one | price menu:pricelist
fit-coach-move demo person:full | coach person:one | stance hands:stance | copy person:full | verdict selfie:one | class menu:schedule
fit-treatment room room:treatment | menu card:menu | walkthrough person:one | during hands:during | after selfie:one | sign sign:plate
fit-first-appointment door door:door | waiting room:waiting | meet selfie:two | tools table:treatment | price card:pricelist | verdict selfie:one
"""
for line in _RULES.strip().splitlines():
    parts = line.split()
    tid, rest = parts[0], " ".join(parts[1:])
    for cell in rest.split("|"):
        sid, subj = cell.split()
        SUBJECT[(tid, sid)] = subj

# 3D model per family:item (kit GhostModel types, or a usdz name for subjects the kit lacks)
KIT_TYPE = {
    "selfie": "person", "person": "person", "hair": "person",
    "over_shoulder": "hands_board", "facade": "facade", "door": "door", "sign": "sign", "menu": "menu_board",
    "card": "card", "room": "room", "table": "table", "bar": "table", "case": "display_case", "rail": "rail",
    "oven": "oven", "tray": "tray", "pastry": "pastry", "cup": "cup", "latte": "latte", "glass": "glass",
    "tap": "tap", "plate": "pasta", "burger": "burger", "topdown": "box", "hands": "hands_board",
    "hand_pov": "pastry", "nails": "hand", "tools": "tray", "bag": "box", "details": "plant", "machine": "machine",
}
ITEM_TYPE = {("plate", "spread"): "pasta", ("plate", "bite"): "pasta", ("hand_pov", "garment"): "garment",
             ("hand_pov", "item"): "box", ("rail", "guitar"): "guitar", ("rail", "dumbbell"): "rack",
             ("rail", "bottle"): "rail", ("rail", "shelf"): "rail", ("hands", "guitar"): "guitar",
             ("hands", "garment"): "garment", ("hands", "griddle"): "griddle", ("glass", "tap"): "tap",
             ("room", "cupreveal"): "room", ("pastry", "plate"): "dessert", ("over_shoulder", "counter"): "cup",
             ("over_shoulder", "menu"): "menu_board", ("over_shoulder", "machine"): "cup",
             ("over_shoulder", "till"): "menu_board", ("over_shoulder", "rail"): "garment",
             ("sign", "plate"): "sign", ("menu", "taps"): "tap", ("facade", "window"): "window"}
KIT_LACKS = {"hands_board", "card", "table", "rail", "tray", "burger", "box", "garment", "guitar", "rack",
             "griddle", "machine", "hand"}


def kit_type(family, item):
    return ITEM_TYPE.get((family, item), KIT_TYPE[family])


# ---------------------------------------------------------------- existing guides reused as they are
# key: (family, item, angle, start, end, move, transitionOut) -> kit scene id. Only exact fits.
REUSE = {
    ("selfie", "one", "eye-level", "medium", "medium", "static", "cut"): "talking_head_eye_level",
    ("selfie", "sip", "eye-level", "medium", "medium", "static", "cut"): "selfie_sip_reaction",
    ("selfie", "bite", "eye-level", "medium", "medium", "static", "cut"): "selfie_bite_reaction",
    ("case", "case", "eye-level", "medium", "medium", "truck-left", "cut"): "shelf_slide_left",
    ("room", "room", "eye-level", "wide", "wide", "pan-right", "cut"): "interior_pan",
    ("sign", "sign", "low", "medium", "medium", "tilt-down", "cut"): "sign_tilt_down_reveal",
    ("person", "one", "eye-level", "medium", "close", "push-in", "cut"): "counter_barista_side",
    ("glass", "tap", "eye-level", "close", "close", "static", "match-cut"): "tap_pour_glass",
    ("glass", "cheers", "low", "medium", "medium", "static", "cut"): "glasses_clink_center",
    ("tools", "station", "high", "close", "detail", "push-in", "cut"): "tools_closeup_hands",
    ("pastry", "plate", "high", "close", "detail", "push-in", "cut"): "pastry_tear_open",
    ("room", "salon", "eye-level", "close", "medium", "reveal-from-behind", "cut"): "chair_reveal_frame",
    ("door", "walkin", "pov", "wide", "medium", "push-in", "cut"): "pov_door_entry",
}
# salon "before" selfies (static, in the chair facing the mirror light) turn front-then-back for the reveal later
REUSE_BY_STEP = {
    ("salon-transformation", "before"): "before_front_back",
    ("salon-fade", "before"): "before_front_back",
}

MOVE_SHORT = {"static": "hold", "push-in": "in", "pull-out": "out", "pan-right": "panr", "pan-left": "panl",
              "tilt-down": "tiltd", "tilt-up": "tiltu", "truck-right": "truckr", "truck-left": "truckl",
              "orbit-right": "orbitr", "orbit-left": "orbitl", "whip": "whip", "reveal-from-behind": "reveal"}
ANGLE_SHORT = {"eye-level": "eye", "high": "high", "low": "low", "top-down": "top", "pov": "pov",
               "over-shoulder": "os"}
FRAME_SHORT = {"wide": "w", "medium": "m", "close": "c", "detail": "d"}
# match-cut and pull-back-reveal need no extra animation (the subject ends centred, the next step starts on
# the detail), so they share the plain scene; only a whip-out and a push-through change the last second.
TRANS_SHORT = {"cut": "", "match-cut": "", "whip": "whipout", "push-through": "through", "pull-back-reveal": ""}


def new_id(family, item, sig):
    angle, start, end, move, trans = sig
    parts = [family if family == item else f"{family}_{item}", ANGLE_SHORT[angle], MOVE_SHORT[move]]
    if move != "static" or start != end:
        parts.append(FRAME_SHORT[start] + FRAME_SHORT[end])
    if TRANS_SHORT[trans]:
        parts.append(TRANS_SHORT[trans])
    return "_".join(parts)


def catalog():
    """Returns rows: dict per step with template, step, family, item, camera, sig, guide, reused."""
    rows = []
    for tpl in TEMPLATES["templates"]:
        for st in tpl["steps"]:
            key = (tpl["id"], st["id"])
            e = SHOT_PLAN[tpl["id"]][st["id"]]
            family, item = SUBJECT[key].split(":")
            sig = (e["angle"], e["start"], e["end"], e["move"], e["transitionOut"])
            camera = "front" if family == "selfie" else "back"
            guide = REUSE_BY_STEP.get(key) or REUSE.get((family, item) + sig)
            reused = guide is not None
            if not guide:
                guide = new_id(family, item, sig)
            rows.append(dict(template=tpl["id"], step=st["id"], family=family, item=item, camera=camera,
                             angle=e["angle"], start=e["start"], end=e["end"], move=e["move"],
                             transition=e["transitionOut"], seconds=st["seconds"], shot=st["shot"], pip=st["pip"],
                             reads=e.get("reads", ""), direction=st["direction"], guide=guide, reused=reused,
                             kit_type=kit_type(family, item)))
    return rows


def guides(rows=None):
    """Guide id -> the steps that use it (first one defines the scene)."""
    out = {}
    for r in rows or catalog():
        out.setdefault(r["guide"], []).append(r)
    return out


if __name__ == "__main__":
    rows = catalog()
    missing = [(t["id"], s["id"]) for t in TEMPLATES["templates"] for s in t["steps"] if (t["id"], s["id"]) not in SUBJECT]
    extra = [k for k in SUBJECT if k not in {(t["id"], s["id"]) for t in TEMPLATES["templates"] for s in t["steps"]}]
    if missing or extra:
        print("MISSING", missing, "EXTRA", extra)
        sys.exit(1)
    g = guides(rows)
    new = [k for k, v in g.items() if not v[0]["reused"]]
    print(f"steps {len(rows)}  guides {len(g)}  reused {len(g) - len(new)}  new {len(new)}")
    for gid, steps in sorted(g.items(), key=lambda kv: (kv[1][0]['reused'], kv[0])):
        r = steps[0]
        tag = "REUSE" if r["reused"] else "new  "
        print(f"{tag} {gid:<42} {r['family']}:{r['item']:<10} {r['angle']:<13} {r['start']}>{r['end']:<7} {r['move']:<19} {r['transition']:<16} x{len(steps)}  " + ", ".join(f"{s['template']}/{s['step']}" for s in steps))
