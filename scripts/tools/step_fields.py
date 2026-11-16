"""The P0 step fields (shotType, access, orders, voice, ambient, camera, composition, guides, examplePreview) for
every catalog step, from the explicit values in the parts, the shot-type registry (guides/tools/p0_catalog.py) and
the keyword table (scripts/step_shot_types.json).

A step may list `venueKinds`: the template then has one step set per kind (`resolve`), numbered per kind.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SCRIPTS, "..", "guides", "tools"))
import p0_catalog  # noqa: E402

P0_SCRIPTS = {"food-review", "food-review-typed", "first-visit"}
TABLE = json.load(open(os.path.join(SCRIPTS, "step_shot_types.json")))
REGISTRY = p0_catalog.registry()
SHOT_TYPES = {t["id"]: t for t in REGISTRY["shotTypes"]}
GUIDES = {g["id"]: g for g in REGISTRY["guides"]}
P0_KEYS = ["shotType", "access", "captureOrder", "editOrder", "required", "voice", "ambient", "camera",
           "composition", "guides", "examplePreview"]
# Guided v0 (p0/tasks/09): a step with `complexity` keeps its own guides and camera; the levels are in guide_levels.json.
V0_KEYS = ["complexity", "line", "caption", "idea", "titleFacts", "lineVariants", "key", "card", "opinion", "noPrice", "servingVariants"]
# Time-of-day text variants (owner 2026-11-12): {"morning"|"midday"|"evening": {"line", "caption"}}; `line` and `caption`
# stay the time-neutral default. Dayparts in the venue's time zone: morning to 11:00, midday 11:00-16:00, evening 16:00 on.
DAYPARTS = ("morning", "midday", "evening")
LEVELS = json.load(open(os.path.join(SCRIPTS, "..", "guides", "p0", "guide_levels.json")))
# Opinion slots (handoff 2026-11-13): `{opinion}` is the creator's pick from a shared set; a step is timed with its
# longest option in, and a `noPrice` variant ({"line", "card", "caption"}) replaces the texts when the price is missing.
OPINION_SETS = json.load(open(os.path.join(SCRIPTS, "opinion_sets.json")))["opinionSets"]
SETS = {s["id"]: s for s in OPINION_SETS}


INHERITED_GUIDES = 5
MAX_STEP_SECONDS = 8
WORDS_PER_SECOND = 2.5
FINISH_SECONDS = 1.0


def words(text):
    return len(re.findall(r"[A-Za-z0-9']+", text))


def slotted_words(text):
    """Words read aloud, a slot counting as a two-word name (a price as one)."""
    text = text.replace("{menuItem.price}", "price")
    return words(re.sub(r"\{[A-Za-z.]+\}", "a name", text))


def variant_lines(step):
    variants = list((step.get("lineVariants") or {}).values()) + [step.get("noPrice")]
    return [v.get("line") for v in variants if isinstance(v, dict) and v.get("line")]


def longest_option(step):
    """The longest text the step's opinion slot can take (taste sets: the longest allowed picks joined)."""
    record = SETS.get((step.get("opinion") or {}).get("set"))
    if not record:
        return ""
    texts = [o["text"] for o in record["options"] if o.get("text")]
    if record.get("multiSelect"):
        texts.append(", ".join(sorted(texts, key=slotted_words, reverse=True)[:record.get("maxPicks", 1)]))
    return max(texts, key=slotted_words, default="")


def spoken(step, line):
    return line.replace("{opinion}", longest_option(step)) if "{opinion}" in line else line


def step_line(step):
    """The text a step is timed by: the longest of its line and its variant and noPrice lines with the longest opinion
    option in, else its prompter, else its longest caption script; so a step's length never depends on the daypart,
    the price or the creator's pick."""
    lines = [spoken(step, line) for line in [step.get("line")] + variant_lines(step) if line]
    if lines:
        return max(lines, key=slotted_words)
    if step.get("prompter"):
        return step["prompter"]
    scripts = [c.get("script") or "" for c in step.get("captions") or []]
    return max(scripts, key=slotted_words, default="")


def line_seconds(line):
    """Seconds to say the line and finish before the guide loops again (uncapped)."""
    return math.ceil(round(slotted_words(line) / WORDS_PER_SECOND + FINISH_SECONDS, 6))


def line_too_long(line):
    return line_seconds(line) > MAX_STEP_SECONDS or len(line) > 140


def step_seconds(step):
    """A guided step lasts its first guide's loop, or longer to finish its line, at most 8 s."""
    guide = GUIDES[step["guides"][0]]["durationSec"]
    return min(MAX_STEP_SECONDS, max(guide, line_seconds(step_line(step))))


def inherited_guides(kind, skip=()):
    """The guides a step without its own list offers: the shot type's first five, in registry order; a guide whose
    level says `"inherited": false` is offered only by the steps that name it."""
    return [g for g in kind["guides"] if g not in skip and LEVELS["guides"].get(g, {}).get("inherited", True)][:INHERITED_GUIDES] if kind else []


def has(text, phrases):
    return any(re.search(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])", text) for p in phrases)


def is_staff(key, step):
    return key in TABLE["staff"]["steps"] or has(step.get("position", "").lower(), TABLE["staff"]["positionWords"])


def shot_type(step, kinds, last):
    """The first keyword rule the step matches, or none."""
    text = " ".join(step.get(k) or "" for k in ("title", "position", "direction")).lower()
    food = bool(set(kinds) & set(TABLE["foodKinds"]))
    for rule in TABLE["rules"]:
        if rule.get("foodOnly") and not food or rule.get("last") and not last:
            continue
        if "shots" in rule and step.get("shot") not in rule["shots"]:
            continue
        if "words" in rule and not has(text, rule["words"]) or "moves" in rule and not has(text, rule["moves"]):
            continue
        return rule["shotType"]
    return "none"


def resolve(template, kind):
    """The template's steps for one venue kind, capture order and edit order renumbered from 1."""
    steps = [dict(s) for s in template["steps"] if kind in s.get("venueKinds", template["venueKinds"])]
    for index, step in enumerate(steps):
        step["captureOrder"] = index + 1
    for rank, step in enumerate(sorted(steps, key=lambda s: s["editOrder"])):
        step["editOrder"] = rank + 1
    return steps


def derive(templates, plan):
    """Fills the P0 fields of every step in place; inherited guided steps get their seconds (step_seconds); the plan
    takes each step's seconds."""
    for template in templates:
        steps = template["steps"]
        for index, step in enumerate(steps):
            key = template["id"] + "." + step["id"]
            kinds = step.get("venueKinds", template["venueKinds"])
            last = all(kind not in s.get("venueKinds", template["venueKinds"]) for s in steps[index + 1:] for kind in kinds)
            staff = is_staff(key, step)
            if staff:
                step["access"] = "staff"
            step.setdefault("access", "counter" if has(step.get("position", "").lower(), TABLE["counterWords"]) else "public")
            if "shotType" not in step:
                step["shotType"] = "none" if staff else shot_type(step, kinds, last)
            kind = SHOT_TYPES.get(step["shotType"])
            v0 = "complexity" in step
            if not v0:
                step["guides"] = inherited_guides(kind)
                if step["guides"]:
                    step["seconds"] = step_seconds(step)
            if kind:
                if step["id"] in plan.get(template["id"], {}):
                    plan[template["id"]][step["id"]]["seconds"] = step["seconds"]
            step.setdefault("captureOrder", index + 1)
            step.setdefault("editOrder", index + 1)
            step.setdefault("required", False)
            if v0:
                step["required"] = True
                step["voice"] = "prompter" if step["complexity"] == "easy" else "none"
            else:
                step["voice"] = "prompter" if step.get("prompter") else "none"
            step["ambient"] = kind["ambientDefault"] if kind else "noise"
            if not v0:
                step["camera"] = "both" if step.get("pip") else kind["camera"] if kind else "front" if step.get("shot") == "selfie" else "back"
            step["composition"] = kind["composition"] if kind else "none"
            step["examplePreview"] = step["imageURL"]
    return templates
