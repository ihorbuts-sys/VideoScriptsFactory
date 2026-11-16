"""Checks script parts or the merged catalog against the kit format, the README limits and the shot-plan rules.

Usage:
  python3 -I check_scripts.py <part.json> [...]     check one or more parts ({"templates": [...], "shotPlan": {...}})
  python3 -I check_scripts.py --merge               merge scripts/_parts/*.json into script_templates.json and
                                                    shot_plan.json with the P0 step fields (step_fields.py), then
                                                    check the result
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import step_fields  # noqa: E402
import line_lint  # noqa: E402
from step_fields import words  # noqa: E402
PREVIEWS = os.path.join(SCRIPTS, "..", json.load(open(os.path.join(SCRIPTS, "..", "previews", "active-art-revision.json")))["assetDirectory"])

KINDS = [
    {"id": "coffee", "title": "Cafe", "symbol": "cup.and.saucer.fill"},
    {"id": "bakery", "title": "Bakery", "symbol": "birthday.cake.fill"},
    {"id": "dining", "title": "Restaurant", "symbol": "fork.knife"},
    {"id": "fast-food", "title": "Quick bites", "symbol": "takeoutbag.and.cup.and.straw.fill"},
    {"id": "entertainment", "title": "Going out", "symbol": "music.note.house.fill"},
    {"id": "beauty-salon", "title": "Salon", "symbol": "comb.fill"},
    {"id": "sport_health", "title": "Fitness and wellness", "symbol": "figure.yoga"},
    {"id": "shopping", "title": "Shop", "symbol": "bag.fill"},
    {"id": "services", "title": "Local pro", "symbol": "wrench.and.screwdriver.fill"},
]
KIND_IDS = {k["id"] for k in KINDS}
SHOTS = {"wide", "medium", "close", "detail", "pov", "selfie"}
ANGLES = {"eye-level", "low", "high", "top-down", "over-shoulder", "dutch", "pov"}
FRAMES = ["detail", "close", "medium", "wide"]
MOVES = {"static", "push-in", "pull-out", "pan-left", "pan-right", "tilt-up", "tilt-down", "truck-left",
         "truck-right", "orbit-left", "orbit-right", "whip", "reveal-from-behind"}
TRANSITIONS = {"cut", "match-cut", "whip", "push-through", "pull-back-reveal"}
STEP_KEYS = {"id", "title", "shot", "position", "direction", "seconds", "prompter", "captions", "pip", "imageURL",
             "overlays"}
OPTIONAL_KEYS = set(step_fields.P0_KEYS) | set(step_fields.V0_KEYS) | {"venueKinds"}
PLAN_KEYS = {"angle", "start", "end", "move", "seconds", "transitionOut", "reads"}
ROWS = {"top-down": 0, "high": 1, "eye-level": 2, "low": 3}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FILLER = re.compile(r"\b(elevate|elevated|experience|unlock|unforgettable|indulge|curated|vibes? check)\b", re.I)
# Catalog version 2 (2026-11-13): steps carry key, card, opinion and noPrice and the catalog its opinionSets; drafts
# started on version 1 stay on it.
CATALOG_VERSION = 2
# Bundled lines must hold at any venue of a kind: no staff pronouns, no slots, no clock times, no fixed scores.
INVENTED = re.compile(r"\$__|\b(she|he|her|his|him|herself|himself)\b|\b\d{1,2}(:\d\d)?\s?(am|pm)\b|\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+) out of ten\b", re.I)
CYRILLIC = re.compile(r"[\u0400-\u04FF]")


def v0_errors(s, sw, guides, errors):
    """Guided v0: one complexity per step, its guides at the same level, the easy texts or none."""
    level = s["complexity"]
    if level not in ("easy", "complex"):
        errors.append(f"{sw}: complexity {level}")
    levels = step_fields.LEVELS["guides"]
    for g in guides:
        record = levels.get(g)
        if record is None:
            errors.append(f"{sw}: guide {g} has no level in guide_levels.json")
            continue
        if record["complexity"] != level:
            errors.append(f"{sw}: guide {g} is {record['complexity']}, the step is {level}")
        if record.get("camera") not in ("back", "front"):
            errors.append(f"{sw}: guide {g} without a camera")
        beats = record.get("beats", [])
        if level == "complex" and not 2 <= len(beats) <= 4:
            errors.append(f"{sw}: complex guide {g} has {len(beats)} beats (2 to 4)")
        if level == "easy" and beats:
            errors.append(f"{sw}: easy guide {g} has beats")
        times = [b["atSec"] for b in beats]
        duration = step_fields.GUIDES.get(g, {}).get("durationSec", 0)
        if times != sorted(times) or any(t >= duration for t in times) or any(len(b["text"]) > 70 for b in beats):
            errors.append(f"{sw}: guide {g} beats out of order, past {duration} s or over 70 chars")
    if level == "easy":
        line, caption = s.get("line"), s.get("caption")
        if not line or not caption:
            errors.append(f"{sw}: easy step without a line or caption")
        elif step_fields.line_too_long(line):
            errors.append(f"{sw}: line '{line}' needs {step_fields.line_seconds(line)} s or is over 140 chars (8 s at most)")
    elif s.get("line") is not None or s.get("caption") is not None:
        errors.append(f"{sw}: complex step with a line or caption")
    variant_errors(s, sw, level, errors)
    if not s.get("idea") or len(s["idea"]) > 90:
        errors.append(f"{sw}: idea missing or over 90 chars")
    if s.get("pip") or s.get("camera") == "both":
        errors.append(f"{sw}: picture in picture is out of v0")


SERVING_KEYS = {"venueKinds", "position", "direction", "idea", "guides"}


def serving_variant_errors(t, s, sw, errors, warnings):
    """`servingVariants`: a named variant the app picks by the venue's kind (handheld for bakery and quick bites).
    It replaces only where and how to film, never the texts; its guides are at the step's level and shot type, its
    pending guides list the step as `<script>.<step>#<variant>`."""
    variants = s.get("servingVariants")
    if variants is None:
        return
    if not isinstance(variants, dict) or "complexity" not in s:
        errors.append(f"{sw}: servingVariants must be an object on a guided step")
        return
    for name, v in variants.items():
        vw = f"{sw}#{name}"
        if not isinstance(v, dict) or set(v) - SERVING_KEYS:
            errors.append(f"{vw}: a serving variant has only {', '.join(sorted(SERVING_KEYS))}")
            continue
        kinds = v.get("venueKinds") or []
        if not kinds or set(kinds) - set(t.get("venueKinds", [])):
            errors.append(f"{vw}: venueKinds {kinds} must be a non-empty subset of the script's {t.get('venueKinds')}")
        if not v.get("position") or not v.get("direction"):
            errors.append(f"{vw}: position and direction are required")
        if "idea" in v and (not v["idea"] or len(v["idea"]) > 90):
            errors.append(f"{vw}: idea missing or over 90 chars")
        guides = v.get("guides", s.get("guides", []))
        levels = step_fields.LEVELS["guides"]
        for g in guides:
            record = levels.get(g)
            if record is None or record["complexity"] != s["complexity"] or step_fields.GUIDES.get(g, {}).get("shotType") != s.get("shotType"):
                errors.append(f"{vw}: guide {g} is not a {s['complexity']} {s.get('shotType')} guide")
        pending = [g["id"] for g in step_fields.LEVELS["pending"] if f"{t['id']}.{s['id']}#{name}" in g.get("steps", [])]
        if pending:
            warnings.append(f"{vw}: pending guides {pending}")
        if not 2 <= len(guides) + len(pending) <= 5:
            errors.append(f"{vw}: {len(guides)} guides and {len(pending)} pending (2 to 5)")


def variant_errors(s, sw, level, errors):
    """`lineVariants`: known dayparts only; an easy step's variant texts pass the line caps and its variant lines say
    8 to 14 words (slots as two); a complex step's variants are null."""
    variants = s.get("lineVariants")
    if variants is None:
        return
    if not isinstance(variants, dict):
        errors.append(f"{sw}: lineVariants is not an object")
        return
    for part, variant in variants.items():
        vw = f"{sw}[{part}]"
        if part not in step_fields.DAYPARTS:
            errors.append(f"{vw}: unknown daypart ({', '.join(step_fields.DAYPARTS)})")
        if variant is None:
            continue
        if not isinstance(variant, dict) or set(variant) - {"line", "caption"}:
            errors.append(f"{vw}: a variant has only line and caption")
            continue
        texts = {key: variant.get(key) for key in ("line", "caption")}
        if level != "easy":
            if any(texts.values()):
                errors.append(f"{vw}: complex step with a variant line or caption")
            continue
        if not any(texts.values()):
            errors.append(f"{vw}: empty variant")
        for key, text in texts.items():
            if text is None:
                continue
            if not isinstance(text, str) or not text:
                errors.append(f"{vw}: {key} is not text")
            elif step_fields.line_too_long(text):
                errors.append(f"{vw}: {key} '{text}' needs {step_fields.line_seconds(text)} s or is over 140 chars (8 s at most)")
            elif key == "line" and not 8 <= step_fields.slotted_words(text) <= 14:
                errors.append(f"{vw}: line '{text}' has {step_fields.slotted_words(text)} words (8 to 14)")
            m = INVENTED.search(text) if isinstance(text, str) else None
            if m:
                errors.append(f"{vw}: '{m.group(0)}' is a venue-specific fact, pronoun or slot: '{text}'")


def spoken(step):
    return step.get("pip") or step.get("shot") in ("selfie", "close")


def size(frame):
    return FRAMES.index(frame)


def check(templates, plan):
    errors, warnings, staff = [], [], []
    seen = set()
    for t in templates:
        tid = t.get("id", "?")
        where = tid
        if tid in seen:
            errors.append(f"{where}: duplicate template id")
        seen.add(tid)
        if not KEBAB.match(tid):
            errors.append(f"{where}: id is not kebab-case")
        for key in ("venueKinds", "title", "summary", "steps"):
            if key not in t:
                errors.append(f"{where}: missing {key}")
        bad = set(t.get("venueKinds", [])) - KIND_IDS
        if bad:
            errors.append(f"{where}: unknown venue kinds {sorted(bad)}")
        steps = t.get("steps", [])
        for s in steps:
            if set(s.get("venueKinds", [])) - set(t.get("venueKinds", [])):
                errors.append(f"{tid}/{s.get('id')}: step venue kinds outside the template's")
        variants = {k: step_fields.resolve(t, k) for k in t.get("venueKinds", [])} if any("venueKinds" in s for s in steps) else {None: steps}
        for kind, vsteps in variants.items():
            label = where if kind is None else f"{where}[{kind}]"
            if not 3 <= len(vsteps) <= 7:
                errors.append(f"{label}: {len(vsteps)} steps (3 to 7)")
            total = sum(s.get("seconds", 0) for s in vsteps)
            if not 20 <= total <= 45:
                errors.append(f"{label}: total {total} s (20 to 45)")
        ids = [s.get("id") for s in steps]
        if len(set(ids)) != len(ids):
            errors.append(f"{where}: repeated step id")
        tplan = plan.get(tid)
        if tplan is None:
            errors.append(f"{where}: no shot plan")
            tplan = {}
        if set(tplan) - set(ids):
            errors.append(f"{where}: shot plan names unknown steps {sorted(set(tplan) - set(ids))}")
        for s in steps:
            sw = f"{tid}/{s.get('id')}"
            missing = STEP_KEYS - set(s)
            if missing:
                errors.append(f"{sw}: missing {sorted(missing)}")
            extra = set(s) - STEP_KEYS - OPTIONAL_KEYS
            if extra:
                errors.append(f"{sw}: unknown keys {sorted(extra)}")
            if not KEBAB.match(s.get("id", "")):
                errors.append(f"{sw}: step id not kebab-case")
            if s.get("shot") not in SHOTS:
                errors.append(f"{sw}: shot {s.get('shot')}")
            if not 2 <= s.get("seconds", 0) <= 8:
                errors.append(f"{sw}: {s.get('seconds')} s (2 to 8)")
            if s.get("imageURL") != f"{tid}_{s.get('id')}.jpg":
                if os.path.isfile(os.path.join(PREVIEWS, s.get("imageURL") or "-")):
                    warnings.append(f"{sw}: borrows the preview {s.get('imageURL')}")
                else:
                    errors.append(f"{sw}: imageURL should be {tid}_{s.get('id')}.jpg")
            kind_record = step_fields.SHOT_TYPES.get(s.get("shotType"))
            guides = s.get("guides", [])
            if s.get("access") not in ("public", "counter", "staff"):
                errors.append(f"{sw}: access {s.get('access')}")
            if s.get("shotType") != "none" and kind_record is None:
                errors.append(f"{sw}: shot type {s.get('shotType')}")
            if tid in step_fields.P0_SCRIPTS and s.get("access") == "staff":
                errors.append(f"{sw}: staff step in a P0 script")
            elif s.get("access") == "staff":
                staff.append(sw)
            if tid in step_fields.P0_SCRIPTS and s.get("shotType") == "none":
                errors.append(f"{sw}: P0 step without a shot type")
            pending = [g["id"] for g in step_fields.LEVELS["pending"] if f"{tid}.{s.get('id')}" in g.get("steps", [])]
            if "complexity" in s and pending:
                warnings.append(f"{sw}: pending guides {pending}")
            serving_variant_errors(t, s, sw, errors, warnings)
            if "complexity" in s and not 2 <= len(guides) + len(pending) <= 5:
                errors.append(f"{sw}: {len(guides)} guides and {len(pending)} pending (2 to 5)")
            if kind_record:
                if "complexity" not in s and (not 2 <= len(guides) <= step_fields.INHERITED_GUIDES or guides[:1] != kind_record["guides"][:1]):
                    errors.append(f"{sw}: guides {guides} (2 to {step_fields.INHERITED_GUIDES}, the recommended one first)")
                if any(step_fields.GUIDES.get(g, {}).get("shotType") != s["shotType"] for g in guides):
                    errors.append(f"{sw}: a guide of another shot type in {guides}")
                if guides and s.get("seconds") != step_fields.step_seconds(s):
                    errors.append(f"{sw}: {s.get('seconds')} s, the step length rule gives {step_fields.step_seconds(s)} s")
                if step_fields.line_too_long(step_fields.step_line(s)):
                    errors.append(f"{sw}: its line needs over 8 s or 140 chars")
                if not 3 <= s.get("seconds", 0) <= 8:
                    errors.append(f"{sw}: guided step {s.get('seconds')} s (3 to 8)")
            elif guides:
                errors.append(f"{sw}: guides without a shot type")
            line = step_fields.step_line(s) if "complexity" in s else ""
            if not guides and line and s.get("seconds", 0) < min(step_fields.MAX_STEP_SECONDS, step_fields.line_seconds(line)):
                errors.append(f"{sw}: {s.get('seconds')} s is too short for its line ({step_fields.line_seconds(line)} s)")
            if s.get("overlays") != []:
                errors.append(f"{sw}: overlays must be empty")
            caps = s.get("captions", [])
            if not caps or any(not c.get("text") or not c.get("script") for c in caps):
                errors.append(f"{sw}: captions need text and script")
            if "complexity" in s:
                v0_errors(s, sw, guides, errors)
            elif "lineVariants" in s:
                errors.append(f"{sw}: lineVariants outside a guided step")
            elif spoken(s):
                n = words(s.get("prompter", ""))
                if not 8 <= n <= 14:
                    errors.append(f"{sw}: spoken prompter has {n} words (8 to 14)")
                if s.get("seconds", 0) < n / 3.0:
                    warnings.append(f"{sw}: {n} words in {s.get('seconds')} s is fast")
                if not 1 <= len(caps) <= 3:
                    errors.append(f"{sw}: spoken step has {len(caps)} captions (1 to 3)")
            else:
                if s.get("prompter"):
                    errors.append(f"{sw}: a just-film step has a prompter")
                if not 2 <= len(caps) <= 3:
                    errors.append(f"{sw}: just-film step has {len(caps)} captions (2 to 3)")
            for c in caps:
                n = words(c.get("script", ""))
                if not 6 <= n <= 18:
                    warnings.append(f"{sw}: caption script '{c.get('text')}' has {n} words")
                if len(c.get("text", "")) > 28:
                    warnings.append(f"{sw}: caption text '{c.get('text')}' is long")
            blob = json.dumps(s, ensure_ascii=False)
            if FILLER.search(blob):
                errors.append(f"{sw}: filler word '{FILLER.search(blob).group(0)}'")
            lines = [s.get("prompter", ""), s.get("direction", ""), s.get("title", "")] + [c.get("text", "") + " " + c.get("script", "") for c in caps]
            for line in lines:
                m = INVENTED.search(line)
                if m:
                    errors.append(f"{sw}: '{m.group(0)}' is a venue-specific fact, pronoun or slot: '{line}'")
            if CYRILLIC.search(blob):
                errors.append(f"{sw}: Cyrillic text")
            p = tplan.get(s.get("id"))
            if p is None:
                errors.append(f"{sw}: no shot-plan entry")
                continue
            if set(p) != PLAN_KEYS:
                errors.append(f"{sw}: plan keys {sorted(set(p) ^ PLAN_KEYS)}")
            if p.get("angle") not in ANGLES:
                errors.append(f"{sw}: angle {p.get('angle')}")
            if p.get("start") not in FRAMES or p.get("end") not in FRAMES:
                errors.append(f"{sw}: framing {p.get('start')}/{p.get('end')}")
            if p.get("move") not in MOVES:
                errors.append(f"{sw}: move {p.get('move')}")
            if p.get("transitionOut") not in TRANSITIONS:
                errors.append(f"{sw}: transition {p.get('transitionOut')}")
            if p.get("seconds") != s.get("seconds"):
                errors.append(f"{sw}: plan seconds {p.get('seconds')} differ from step {s.get('seconds')}")
            if not p.get("reads"):
                errors.append(f"{sw}: no reads line")
            if p.get("start") in FRAMES and p.get("end") in FRAMES:
                d = size(p["end"]) - size(p["start"])
                mv = p.get("move")
                if mv == "push-in" and d >= 0:
                    errors.append(f"{sw}: push-in must end tighter than it starts")
                if mv == "pull-out" and d <= 0:
                    errors.append(f"{sw}: pull-out must end wider than it starts")
                if mv == "static" and d != 0:
                    errors.append(f"{sw}: static shot changes size")
            if s.get("shot") == "selfie" and p.get("angle") not in ("eye-level", "high", "low"):
                warnings.append(f"{sw}: selfie at angle {p.get('angle')}")
        # chaining, in edit order
        for kind, vsteps in variants.items():
            chained = sorted(vsteps, key=lambda s: s.get("editOrder", 0))
            chain(tid, chained, tplan, errors, warnings)
    # No metric in any guide text the app shows (owner 2026-11-13).
    for gid, g in step_fields.GUIDES.items():
        shown = [g.get("title"), g.get("invariant")] + [b["text"] for b in step_fields.LEVELS["guides"].get(gid, {}).get("beats", [])]
        if any(line_lint.METRIC.search(t or "") for t in shown):
            errors.append(f"guide {gid}: metric units in its title, instruction or beats (US units)")
    p1 = {}
    for rule, where, message, p0 in line_lint.lint(templates, step_fields.OPINION_SETS):
        if rule in ("L13-pending", "dishSource-missing") or (rule == "L9-caption" and p0):
            warnings.append(f"{where}: {message}")
        elif p0 or rule == "set":
            errors.append(f"{where}: {rule} {message}")
        else:
            p1[rule] = p1.get(rule, 0) + 1
    if p1:
        warnings.append("P1 line-lint findings (not rewritten yet): " + ", ".join(f"{r} {n}" for r, n in sorted(p1.items())))
    return errors, warnings, staff


def chain(tid, steps, tplan, errors, warnings):
    for a, b in zip(steps, steps[1:]):
        pa, pb = tplan.get(a.get("id")), tplan.get(b.get("id"))
        if not pa or not pb:
            continue
        j = f"{tid}/{a['id']}->{b['id']}"
        tr = pa.get("transitionOut")
        same_pose = pa.get("angle") == pb.get("angle") and pa.get("end") == pb.get("start")
        if same_pose and tr not in ("match-cut", "whip"):
            errors.append(f"{j}: same angle and size across a {tr}; change one or join with match-cut or whip")
        if tr == "cut" and {pa.get("end"), pb.get("start")} == {"wide", "detail"}:
            errors.append(f"{j}: wide and detail on a plain cut; bridge with a middle size or a named join")
        if tr == "cut" and not same_pose:
            size_jump = abs(size(pa["end"]) - size(pb["start"])) if pa.get("end") in FRAMES and pb.get("start") in FRAMES else 0
            ra, rb = ROWS.get(pa.get("angle")), ROWS.get(pb.get("angle"))
            if ra is None or rb is None:
                angle_jump = pa.get("angle") != pb.get("angle")
            else:
                angle_jump = abs(ra - rb) >= 2
            camera_flip = (a.get("shot") == "selfie") != (b.get("shot") == "selfie")
            if size_jump < 2 and not angle_jump and not camera_flip and not (spoken(a) and spoken(b)):
                warnings.append(f"{j}: weak cut (size step {size_jump}, angle {pa.get('angle')}->{pb.get('angle')})")
        if tr == "pull-back-reveal" and (pa.get("end") != "detail" or pb.get("start") != "detail"):
            errors.append(f"{j}: pull-back-reveal joins detail to detail")
        if tr == "push-through" and (pa.get("end") not in ("close", "detail") or pb.get("start") not in ("close", "detail")):
            errors.append(f"{j}: push-through needs a tight end and a tight start")
        if tr == "pull-back-reveal" and pb.get("move") not in ("pull-out", "reveal-from-behind"):
            errors.append(f"{j}: pull-back-reveal needs the next step to pull out or reveal")
        if tr == "match-cut" and pa.get("angle") == pb.get("angle") and pa.get("end") == pb.get("start"):
            warnings.append(f"{j}: match-cut keeps angle and size; that is a plain continuation")
    joins = [tplan.get(s["id"], {}).get("transitionOut") for s in steps[:-1]]
    deliberate = sum(1 for x in joins if x and x != "cut")
    if deliberate == 0:
        warnings.append(f"{tid}: no deliberate transition")
    if deliberate > 3:
        warnings.append(f"{tid}: {deliberate} deliberate transitions")


def load_part(path):
    with open(path) as f:
        part = json.load(f)
    return part.get("templates", []), part.get("shotPlan", {})


def main(argv):
    if argv[:1] == ["--v3"]:
        import v3_catalog
        return v3_catalog.main(argv[1:])
    if argv[:1] == ["--merge"]:
        templates, plan = [], {}
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "_parts", "*.json"))):
            t, p = load_part(path)
            templates += t
            plan.update(p)
        step_fields.derive(templates, plan)
        catalog = {"version": CATALOG_VERSION, "venueKinds": KINDS, "opinionSets": step_fields.OPINION_SETS,
                   "templates": templates}
        with open(os.path.join(SCRIPTS, "script_templates.json"), "w") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(os.path.join(SCRIPTS, "shot_plan.json"), "w") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
            f.write("\n")
        for kind in KINDS:
            n = sum(1 for t in templates if kind["id"] in t["venueKinds"])
            print(f"{kind['id']}: {n} scripts")
    else:
        templates, plan = [], {}
        for path in argv:
            t, p = load_part(path)
            templates += t
            plan.update(p)
        step_fields.derive(templates, plan)
    errors, warnings, staff = check(templates, plan)
    for w in warnings:
        print("warn:", w)
    for s in staff:
        print("staff:", s)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(templates)} templates, {sum(len(t['steps']) for t in templates)} steps, "
          f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
