"""Catalog v3 (research/p0_v3_design.md): checks the four kind scripts in scripts/_parts/v3 and builds
scripts/catalog_v3.json.

    python3 -I scripts/tools/check_scripts.py --v3            # check only
    python3 -I scripts/tools/check_scripts.py --v3 --merge    # check, then write scripts/catalog_v3.json

Every step is checked as its base and as each variant applied over the base (the app's view for that context), and
every text version of each. Line rules L1-L14 come from line_lint (the phrase lists); the v3 rules are V1-V12 below.
"""
import copy
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
PARTS = os.path.join(SCRIPTS, "_parts", "v3")
sys.path.insert(0, HERE)
import line_lint as L  # noqa: E402

CATALOG_VERSION = 3
KINDS = ["dish-review", "drink-review", "menu-item-review", "venue-review"]
ROLES = ["arrive", "place", "before", "main", "after", "amenities", "verdict"]
REQUIRED_ROLES = {"arrive", "place", "main", "verdict"}
WHEN_KEYS = {"kind", "subject", "dishKind", "drinkKind", "serviceKind", "price"}
VARIANT_FIELDS = {"when", "title", "where", "direction", "guides", "gap", "versions", "choice", "required", "question"}
PICTURE_FIELDS = {"imageURL", "image", "picture", "preview", "previewURL", "pictureURL"}
STEP_FIELDS = {"key", "role", "required", "title", "camera", "where", "direction", "guides", "gap", "versions",
               "variants", "choice", "silent", "question"}
TAG_KEYS = {"daypart", "menuSection", "dishKind", "drinkKind"}
DAYPARTS = {"morning", "midday", "evening"}
SLOTS = {"venue.name", "menuItem.name", "menuItem.price", "opinion", "amenity"}
# D-3-levels (owner 2026-11-16): neutral, good, very good; a negative experience goes only to Not for me.
TONES = ["neutral", "positive", "positive"]
MIN_VERSIONS, MAX_VERSIONS = 3, 5
MAX_STEP_SECONDS, MIN_STEP_SECONDS = 8, 3
CARD_WORDS = 6
CAPTION_CHARS = 32
LINE_CHARS = 140
# V9 (Visit, owner 2026-11-16): no health or legal outcome claims; regulated testimonials.
OUTCOME = L.phrases(r"cured?", r"healed", r"heals?", r"fixed my", r"no more pain", r"pain[- ]free", r"diagnos\w*",
                    r"won my case", r"won the case", r"got me (?:the|a|my)", r"guarantee[ds]?", r"lost \d+",
                    r"results? guaranteed", r"treatment worked", r"saved my")
QUESTION = re.compile(r"\?")


def load(name):
    with open(os.path.join(PARTS, name)) as f:
        return json.load(f)


def load_all():
    tables = load("tables.json")
    sets = {s["id"]: s for s in load("choice_sets.json")["choiceSets"]}
    scripts = [load(k + ".json") for k in KINDS]
    return tables, sets, scripts


def slots(text):
    return L.slots(text)


def applied(step, variant):
    out = copy.deepcopy(step)
    out.pop("variants", None)
    for k, val in variant.items():
        if k != "when":
            out[k] = copy.deepcopy(val)
    if "guides" in variant and variant["guides"] and "gap" not in variant:
        out.pop("gap", None)
    return out


def contexts(step):
    """(label, effective step) for the base and every variant."""
    yield "base", {k: val for k, val in step.items() if k != "variants"}
    for i, var in enumerate(step.get("variants") or []):
        when = ",".join(f"{k}={v}" for k, v in var.get("when", {}).items())
        yield f"variant[{i}]({when})", applied(step, var)


def option_texts(choice, sets):
    record = sets.get((choice or {}).get("set"))
    if not record:
        return []
    if record["kind"] == "amenity":
        return [o["text"] for o in record["options"]]
    return [lv["text"] for lv in record["levels"]]


def longest(texts):
    return max(texts, key=L.step_fields.slotted_words, default="")


def filled(text, step, sets, values):
    choice = longest(option_texts(step.get("choice"), sets))
    text = text.replace("{opinion}", choice).replace("{amenity}", choice)
    return L.fill(text, values)


def values_for(script, tables):
    s = tables["samples"]
    typed = (script.get("dishSource") or {}).get("from") == "typed"
    name = s["typed"][:40].rsplit(" ", 1)[0] if typed else s["menuItem.name"]
    return {"venue.name": s["venue.name"], "menuItem.name": name, "menuItem.price": s["menuItem.price"]}


def seconds(text):
    return math.ceil(round(L.step_fields.slotted_words(text) / L.step_fields.WORDS_PER_SECOND + L.step_fields.FINISH_SECONDS, 6))


def bare(text):
    """Authored words only: slots removed (the creator's pick and the data are not ours)."""
    return L.SLOT.sub(" ", text or "")


def check_version(where, script, step, ver, sets, values, errors, warnings):
    kind = script["kind"]
    tags = ver.get("tags") or {}
    for key in tags:
        if key not in TAG_KEYS:
            errors.append(f"{where}: V5 unknown tag {key}")
    if "daypart" in tags and tags["daypart"] not in DAYPARTS:
        errors.append(f"{where}: V5 daypart {tags['daypart']}")
    timed = bool(tags.get("daypart") or tags.get("menuSection"))
    if not ver.get("card"):
        errors.append(f"{where}: L14 version has no card")
    if step.get("silent"):
        if ver.get("line"):
            errors.append(f"{where}: L7 silent step has a spoken line")
    elif not ver.get("line"):
        errors.append(f"{where}: version has no line")
    for field in ("line", "card", "caption"):
        text = ver.get(field)
        if not text:
            continue
        found = slots(text)
        for s in found:
            if s not in SLOTS:
                errors.append(f"{where}.{field}: L6 unknown slot {{{s}}}")
        for s in set(found):
            if found.count(s) > 1:
                errors.append(f"{where}.{field}: L11 slot {{{s}}} more than once")
        if "opinion" in found and (not step.get("choice") or sets.get(step["choice"]["set"], {}).get("kind") == "amenity"):
            errors.append(f"{where}.{field}: L11 {{opinion}} without an opinion choice")
        if "amenity" in found and step.get("role") != "amenities":
            errors.append(f"{where}.{field}: L6 {{amenity}} outside the amenities step")
        if "amenity" in found and (not step.get("choice") or sets.get(step["choice"]["set"], {}).get("kind") != "amenity"):
            errors.append(f"{where}.{field}: L11 {{amenity}} without the amenity choice")
        if kind == "venue-review" and ({"menuItem.name", "menuItem.price"} & set(found)):
            errors.append(f"{where}.{field}: L6 venue review has no menu item")
        if "menuItem.price" in found and ver.get("_price") is not True:
            errors.append(f"{where}.{field}: L6/L10 price only inside a price:true variant")
        words = bare(text)
        if L.HEARSAY.search(words):
            errors.append(f"{where}.{field}: L1 hearsay '{L.HEARSAY.search(words).group(0)}'")
        if L.TEASER.search(words):
            errors.append(f"{where}.{field}: L2 teaser '{L.TEASER.search(words).group(0)}'")
        if L.JUDGEMENT.search(words):
            errors.append(f"{where}.{field}: L3 judgement outside the slot '{L.JUDGEMENT.search(words).group(0)}'")
        if L.CALL_TO_ACTION.search(words):
            errors.append(f"{where}.{field}: L4 call to action '{L.CALL_TO_ACTION.search(words).group(0)}'")
        if L.TIME_OF_DAY.search(words) and not timed:
            errors.append(f"{where}.{field}: L5 time of day in an untagged version '{L.TIME_OF_DAY.search(words).group(0)}'")
        if L.BANNED.search(words):
            errors.append(f"{where}.{field}: L12 banned claim '{L.BANNED.search(words).group(0)}'")
        if OUTCOME.search(words):
            errors.append(f"{where}.{field}: V9 outcome claim '{OUTCOME.search(words).group(0)}'")
    cap = ver.get("caption") or ""
    if cap and (QUESTION.search(cap) or "opinion" in slots(cap)):
        errors.append(f"{where}.caption: L4 captions are facts only")
    card = ver.get("card") or ""
    if card and L.words(card) > CARD_WORDS:
        errors.append(f"{where}.card: L14 card over {CARD_WORDS} words")
    line = ver.get("line")
    if line:
        spoken = filled(line, step, sets, values)
        if seconds(spoken) > MAX_STEP_SECONDS or len(spoken) > LINE_CHARS:
            errors.append(f"{where}.line: L8/L9 {seconds(spoken)} s, {len(spoken)} chars with real values: {spoken}")
    if cap:
        shown = filled(cap, step, sets, values)
        if len(shown) > CAPTION_CHARS:
            warnings.append(f"{where}.caption: L9 {len(shown)} chars with real values (wraps)")


def check_step(script, step, sets, tables, guides, errors, warnings, active):
    sid = f"{script['kind']}/{step.get('key')}"
    for scope in [step] + list(step.get("variants") or []):
        for k in PICTURE_FIELDS & set(scope):
            errors.append(f"{sid}: V1 {k}: v3 steps have no pictures (owner 2026-11-17, design 291:3905)")
    for k in step:
        if k in PICTURE_FIELDS:
            continue
        if k not in STEP_FIELDS:
            errors.append(f"{sid}: V1 unknown field {k}")
    if step.get("role") not in ROLES:
        errors.append(f"{sid}: V1 role {step.get('role')}")
    if step.get("role") in REQUIRED_ROLES and step.get("required") is not True and script["kind"] != "venue-review":
        errors.append(f"{sid}: V2 role {step['role']} must be required")
    for var in step.get("variants") or []:
        for k in var:
            if k not in VARIANT_FIELDS:
                errors.append(f"{sid}: V4 variant field {k}")
        for k in var.get("when") or {}:
            if k not in WHEN_KEYS:
                errors.append(f"{sid}: V4 when key {k} (forms are for guides only)")
        if not var.get("when"):
            errors.append(f"{sid}: V4 variant without when")
    values = values_for(script, tables)
    longest_line = 0
    for label, eff in contexts(step):
        where = f"{sid}.{label}"
        versions = eff.get("versions") or []
        if not MIN_VERSIONS <= len(versions) <= MAX_VERSIONS:
            errors.append(f"{where}: V3 {len(versions)} versions (3-5)")
        when = {}
        if label != "base":
            idx = int(label.split("[")[1].split("]")[0])
            when = step["variants"][idx].get("when") or {}
        choice = eff.get("choice")
        if choice:
            record = sets.get(choice.get("set"))
            if not record:
                errors.append(f"{where}: V6 unknown choice set {choice.get('set')}")
            elif record["kind"] == "verdict" and choice.get("preselect") is not None:
                errors.append(f"{where}: V7 a verdict is never preselected")
            elif record["kind"] == "amenity" and eff.get("role") != "amenities":
                errors.append(f"{where}: V6 amenity set outside the amenities step")
        if eff.get("role") == "verdict" and not choice:
            errors.append(f"{where}: V7 verdict without a choice")
        uses = any("opinion" in slots(v.get("line") or "") + slots(v.get("card") or "") or
                   "amenity" in slots(v.get("line") or "") + slots(v.get("card") or "") for v in versions)
        if choice and not uses:
            errors.append(f"{where}: L11 choice set but no version uses its slot")
        for i, ver in enumerate(versions):
            ver = dict(ver, _price=when.get("price"))
            check_version(f"{where}.versions[{i}]", script, eff, ver, sets, values, errors, warnings)
            if ver.get("line"):
                longest_line = max(longest_line, seconds(filled(ver["line"], eff, sets, values)))
        g = eff.get("guides") or []
        for gid in g:
            if gid not in guides:
                errors.append(f"{where}: V8 unknown guide {gid}")
            elif gid not in active:
                warnings.append(f"{where}: V8 guide {gid} is not in the active set")
        if not g and not eff.get("gap"):
            errors.append(f"{where}: V8 no guides and no gap named")
        faces = [gid for gid in g if (guides.get(gid) or {}).get("showsFace")]
        if faces and len(faces) == len(g):
            warnings.append(f"{where}: L13 every guide shows the face; face-free guide pending")
        direction = eff.get("direction") or ""
        if L.METRIC.search(direction):
            errors.append(f"{where}: US units only in directions")
        if script["kind"] == "venue-review" and when.get("subject") == "visit" and "out of frame" not in direction and eff.get("role") in ("place", "before", "main"):
            errors.append(f"{where}: V9 Visit directions must keep other visitors out of frame")
    return longest_line


def check_sets(sets, errors):
    for sid, s in sets.items():
        if s["kind"] == "amenity":
            if any(o.get("tone") != "neutral" for o in s["options"]):
                errors.append(f"set {sid}: V6 amenity options are neutral facts")
            if not s.get("allowCustom"):
                errors.append(f"set {sid}: V6 custom text allowed")
            if "non_smoking" in {o["slug"] for o in s["options"]}:
                errors.append(f"set {sid}: V6 non_smoking is a fact only, not a chip")
            continue
        levels = s.get("levels") or []
        if [lv.get("level") for lv in levels] != [1, 2, 3]:
            errors.append(f"set {sid}: V6 three ordered levels 1-3")
        if [lv.get("tone") for lv in levels] != TONES:
            errors.append(f"set {sid}: V6 tones neutral, positive, positive (no negative level)")
        if s["kind"] != "verdict" and s.get("privateFeedback"):
            errors.append(f"set {sid}: V7 Not for me is on verdicts only")
        if not s.get("allowCustom"):
            errors.append(f"set {sid}: V6 own words must be allowed")
        if s["kind"] == "verdict":
            if s.get("preselect") is not None:
                errors.append(f"set {sid}: V7 verdict never preselected")
            if (s.get("privateFeedback") or {}).get("label") != "Not for me":
                errors.append(f"set {sid}: V7 verdict needs the Not for me private feedback")
        texts = [lv.get("text") or "" for lv in levels]
        if len(set(texts)) != len(texts):
            errors.append(f"set {sid}: V6 duplicate level text")
        for t in texts:
            if L.words(t) > s.get("maxWords", 4):
                errors.append(f"set {sid}: '{t}' over maxWords")
            if L.TIME_OF_DAY.search(t) or L.HEARSAY.search(t) or L.CALL_TO_ACTION.search(t):
                errors.append(f"set {sid}: '{t}' breaks a line rule")
            if t.strip().lower().rstrip(".") == "not for me":
                errors.append(f"set {sid}: '{t}' clashes with the Not for me chip")


FROZEN = os.path.join(SCRIPTS, "kinds_frozen.json")


def check_frozen_kinds(tables, errors, frozen=None):
    """V13 (D-kinds-frozen, 2026-11-16): dish and drink kind ids are never renamed or removed; a new id must be added
    to kinds_frozen.json; a deprecated id needs replacedBy pointing to a live id of the same group."""
    if frozen is None:
        with open(FROZEN, encoding="utf-8") as f:
            frozen = json.load(f)
    if tables.get("kindsVersion") != frozen["kindsVersion"]:
        errors.append(f"V13 tables kindsVersion {tables.get('kindsVersion')} != kinds_frozen.json {frozen['kindsVersion']}")
    for group in ("dishKinds", "drinkKinds"):
        live = {k["id"]: k for k in tables[group]}
        known = {k["id"] for k in frozen[group]}
        for fid in known - set(live):
            errors.append(f"kind {fid}: V13 frozen id removed or renamed; keep it with deprecated: true and replacedBy")
        for kid in set(live) - known:
            errors.append(f"kind {kid}: V13 new id not in kinds_frozen.json (add it there and bump kindsVersion)")
        for k in live.values():
            if not (k.get("labels") or {}).get("en") or not (k.get("labels") or {}).get("uk"):
                errors.append(f"kind {k['id']}: V13 labels.en and labels.uk required")
            if k.get("deprecated"):
                target = live.get(k.get("replacedBy"))
                if not target or target.get("deprecated"):
                    errors.append(f"kind {k['id']}: V13 deprecated needs replacedBy pointing to a live {group[:-1]} id")


def check_tables(tables, errors):
    dish = {k["id"] for k in tables["dishKinds"]}
    drink = {k["id"] for k in tables["drinkKinds"]}
    for k in tables["dishKinds"] + tables["drinkKinds"]:
        if k["form"] not in tables["forms"]:
            errors.append(f"kind {k['id']}: V10 unknown form {k['form']}")
        if k.get("phase") not in ("P0", "P1"):
            errors.append(f"kind {k['id']}: V10 phase P0 or P1")
        if not k.get("menuKeywords"):
            errors.append(f"kind {k['id']}: V10 no menu keywords")
    check_frozen_kinds(tables, errors)
    for k in ("beer-wine", "cocktails"):
        if next((d for d in tables["drinkKinds"] if d["id"] == k), {}).get("phase") != "P1":
            errors.append(f"kind {k}: V10 alcohol is P1 (owner 2026-11-16)")
    seen = {}
    for s in tables["venueSubjects"]:
        for c in s["categories"]:
            if c in seen:
                errors.append(f"category {c}: V11 in {seen[c]} and {s['id']}")
            seen[c] = s["id"]
            if c in tables["venueSubjectRules"]["excluded"]["categories"]:
                errors.append(f"category {c}: V11 excluded from P0")
    if {"dineIn", "counter", "truck"} - {s["id"] for s in tables["venueSubjects"]}:
        errors.append("V11 the three food service kinds must be subjects")
    return dish, drink


def check_whens(script, tables, errors):
    subjects = {s["id"] for s in tables["venueSubjects"]}
    dish = {k["id"] for k in tables["dishKinds"]}
    drink = {k["id"] for k in tables["drinkKinds"]}
    allowed = {"subject": subjects, "serviceKind": set(tables["serviceKinds"]), "dishKind": dish, "drinkKind": drink,
               "kind": set(KINDS), "price": {True, False}}
    for step in script.get("steps") or []:
        for var in step.get("variants") or []:
            for k, val in (var.get("when") or {}).items():
                if k in allowed and val not in allowed[k]:
                    errors.append(f"{script['kind']}/{step['key']}: V4 when {k}={val} not in the tables")
                if script["kind"] == "dish-review" and k == "drinkKind" or script["kind"] == "drink-review" and k == "dishKind":
                    errors.append(f"{script['kind']}/{step['key']}: V4 {k} does not apply to this kind")
                if script["kind"] == "venue-review" and k in ("dishKind", "drinkKind", "price"):
                    errors.append(f"{script['kind']}/{step['key']}: V4 {k} does not apply to a venue review")


def check_script(script, sets, tables, guides, active, errors, warnings):
    kind = script.get("kind")
    if kind not in KINDS:
        errors.append(f"V1 kind {kind}")
        return {}
    if "id" in script or "type" in script:
        errors.append(f"{kind}: V1 kind is the identity (no id, no type)")
    source = script.get("dishSource")
    if kind in ("dish-review", "drink-review"):
        if (source or {}).get("from") != "typed" or not 10 <= source.get("maxLength", 0) <= 60:
            errors.append(f"{kind}: V12 typed dish source with maxLength 10-60")
        if (source or {}).get("kindChip") != ("dishKinds" if kind == "dish-review" else "drinkKinds"):
            errors.append(f"{kind}: V12 kind chip")
    if kind == "menu-item-review":
        if (source or {}).get("from") != "menu" or script.get("stepsFrom") != "derived":
            errors.append(f"{kind}: V12 menu source, steps from the derived kind")
        return {}
    if kind == "venue-review":
        if source:
            errors.append(f"{kind}: V12 a venue review has no dish source")
        if not any((c.get("when") or {}).get("subject") == "visit" for c in script.get("consent") or []):
            errors.append(f"{kind}: V9 Visit consent screen missing")
    roles = [s.get("role") for s in script.get("steps") or []]
    if roles != ROLES:
        errors.append(f"{kind}: V1 roles in order {ROLES}, got {roles}")
    keys = [s.get("key") for s in script["steps"]]
    if len(set(keys)) != len(keys):
        errors.append(f"{kind}: V1 duplicate step keys")
    check_whens(script, tables, errors)
    out = {}
    for step in script["steps"]:
        out[step["key"]] = check_step(script, step, sets, tables, guides, errors, warnings, active)
    if kind == "venue-review":
        for subject in [s["id"] for s in tables["venueSubjects"]]:
            req = {}
            for step in script["steps"]:
                r = step.get("required")
                for var in step.get("variants") or []:
                    if (var.get("when") or {}).get("subject") == subject and "required" in var:
                        r = var["required"]
                req[step["role"]] = r
            payoff = [r for r in ("before", "main", "after") if req.get(r)]
            if not payoff:
                errors.append(f"{kind}/{subject}: V2 one of before, main, after must be required")
            for r in ("arrive", "place", "verdict"):
                if not req.get(r):
                    errors.append(f"{kind}/{subject}: V2 {r} must be required")
    return out


def approved_drafts():
    """Draft guides the owner approved on a drafts page (decisions/drafts-*.json, choice approve) that are not
    promoted yet: {guide id: record}. Archived records are ignored; the newest revision folder wins."""
    root = os.path.join(SCRIPTS, "..", "guides")
    found = {}
    for path in sorted(glob.glob(os.path.join(root, "review", "decisions", "drafts-*.json"))):
        day = os.path.basename(path)[len("drafts-"):-len(".json")]
        with open(path) as f:
            decided = json.load(f)
        for gid, d in decided.items():
            if d.get("choice") != "approve":
                continue
            for rec in sorted(glob.glob(os.path.join(root, "revisions", day, "**", gid, "record.json"), recursive=True)):
                if "archive" not in os.path.relpath(rec, root).split(os.sep):
                    with open(rec) as f:
                        found[gid] = json.load(f)
    return found


def check(tables, sets, scripts):
    errors, warnings = [], []
    import step_fields
    p0 = os.path.join(SCRIPTS, "..", "guides", "p0")
    with open(os.path.join(p0, "guide_levels.json")) as f:
        levels = json.load(f)["guides"]
    with open(os.path.join(p0, "promoted.json")) as f:
        promoted = json.load(f)["guides"]
    guides = {gid: dict(levels.get(gid, {}), durationSec=(step_fields.GUIDES.get(gid) or {}).get("durationSec"))
              for gid in set(levels) | set(step_fields.GUIDES)}
    active = set(promoted)
    drafts = approved_drafts()
    for gid, rec in drafts.items():
        guides.setdefault(gid, {})
        guides[gid].update({k: rec[k] for k in ("durationSec", "showsFace") if k in rec})
        active.add(gid)
    check_sets(sets, errors)
    check_tables(tables, errors)
    timing = {}
    for script in scripts:
        timing[script["kind"]] = check_script(script, sets, tables, guides, active, errors, warnings)
    return errors, warnings, timing, guides


def build(tables, sets, scripts, timing, guides):
    out = []
    for script in scripts:
        s = copy.deepcopy(script)
        for step in s.get("steps") or []:
            first = [g for g in (step.get("guides") or []) if (guides.get(g) or {}).get("durationSec")]
            loop = guides[first[0]]["durationSec"] if first else MIN_STEP_SECONDS
            step["seconds"] = min(MAX_STEP_SECONDS, max(MIN_STEP_SECONDS, math.ceil(loop), timing[s["kind"]].get(step["key"], 0)))
            # `gap` is authoring information (research/v3_guide_work.md); it never ships. An empty `guides` list is
            # valid: the carousel always starts with "No guide" (owner 2026-11-16), so it then shows only that.
            step.pop("gap", None)
            for var in step.get("variants") or []:
                var.pop("gap", None)
        out.append(s)
    return {"version": CATALOG_VERSION, "kinds": out, "choiceSets": list(sets.values()), "tables": tables}


def gaps(scripts):
    """Every guide gap named in the scripts: (gap, kind/step, context)."""
    found = []
    for script in scripts:
        for step in script.get("steps") or []:
            for label, eff in contexts(step):
                if eff.get("gap"):
                    found.append((eff["gap"], f"{script['kind']}/{step['key']}", label))
    return found


def main(argv):
    tables, sets, scripts = load_all()
    errors, warnings, timing, guides = check(tables, sets, scripts)
    for w in warnings:
        print("warn:", w)
    for e in errors:
        print("ERROR:", e)
    n_versions = sum(len(eff.get("versions") or []) for sc in scripts for st in sc.get("steps") or [] for _, eff in contexts(st))
    print(f"v3: {len(scripts)} kinds, {sum(len(s.get('steps') or []) for s in scripts)} steps, {n_versions} versions, "
          f"{len(sets)} choice sets, {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        return 1
    if "--merge" in argv:
        catalog = build(tables, sets, scripts, timing, guides)
        text = json.dumps(catalog)
        assert '"gap"' not in text, "gap must not reach the client catalog"
        assert '"noGuideAllowed"' not in text, "No guide is always the first carousel item; the flag must not ship"
        with open(os.path.join(SCRIPTS, "catalog_v3.json"), "w") as f:
            json.dump(catalog, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print("wrote scripts/catalog_v3.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


def menu_kind(section, tables):
    """(review kind, dish or drink kind id) for a menu section name; unknown -> (dish-review, None) and the kind chip.
    Keywords match case-insensitively at a word start (Ukrainian entries are stems); the longest matching keyword wins."""
    text = (section or "").lower()
    best = None
    for review, group in (("dish-review", "dishKinds"), ("drink-review", "drinkKinds")):
        for k in tables[group]:
            for word in k["menuKeywords"]:
                if re.search(r"(?<!\w)" + re.escape(word.lower()), text) and (best is None or len(word) > best[0]):
                    best = (len(word), review, k["id"])
    return (best[1], best[2]) if best else ("dish-review", None)


def matches(when, context):
    return all(context.get(k) == val for k, val in (when or {}).items())


def effective_step(step, context):
    """The step as the app shows it in `context`: the first variant whose `when` matches overrides the base."""
    for var in step.get("variants") or []:
        if matches(var.get("when"), context):
            return applied(step, var)
    return {k: val for k, val in step.items() if k != "variants"}


def written_errors(script, step_key, versions, context, sets, tables):
    """Rule problems in versions the AI writer returned for one step of `script` in `context` (empty when they pass)."""
    step = next((s for s in script.get("steps") or [] if s["key"] == step_key), None)
    if step is None:
        return [f"unknown step {step_key}"]
    eff = effective_step(step, context)
    errors, warnings = [], []
    values = values_for(script, tables)
    for i, ver in enumerate(versions):
        tags = dict(ver.get("tags") or {})
        if context.get("daypart") and not tags:
            tags["daypart"] = context["daypart"]
        check_version(f"{script['kind']}/{step_key}.written[{i}]", script, eff,
                      dict(ver, tags=tags, _price=context.get("price")), sets, values, errors, warnings)
    return errors
