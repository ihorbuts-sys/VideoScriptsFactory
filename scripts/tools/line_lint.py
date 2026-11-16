"""Line linter L1-L14 and the opinion-set rules (HANDOFF_scripts_agent_opinions_faceless_linter.md sections 2, 3, 7).

A script is written before the visit: it supplies the frame and the facts, the creator supplies the judgement through
an {opinion} slot. `lint(templates, sets)` returns (rule, where, message) tuples; check_scripts.py turns P0 ones into
errors and counts the rest per rule.
"""
import re

import step_fields

SLOTS = {"venue.name", "menuItem.name", "menuItem.price", "opinion"}
MENU_SLOTS = {"menuItem.name", "menuItem.price"}
SLOT = re.compile(r"\{([A-Za-z.]+)\}")
TONES = {"positive", "neutral", "negative"}
KINDS = {"verdict", "reaction", "taste", "place", "value", "result"}
NO_PRESELECT = {"verdict", "taste"}
CARD_WORDS = 6
CAPTION_CHARS = 32
# L9: long but real-looking values; venues and menu items have no short names to fall back to.
SAMPLE = {"venue.name": "The Corner Bakery and Cafe", "menuItem.name": "Iced Brown Sugar Oat Latte", "menuItem.price": "6.50 USD"}
# A typed dish name (dishSource "typed") is timed at its longest: this phrase cut to the script's maxLength.
TYPED_SAMPLE = "Spicy chicken curry with rice and garlic naan bread"
DISH_SOURCES = {"menu", "typed"}
HINT_CHARS = 60


def typed_rules(t):
    """The typed-name rules when the creator may type the dish: a typed source, or a menu source's typedFallback."""
    source = t.get("dishSource") or {}
    return source if source.get("kind") == "typed" else source.get("typedFallback")


def sample(t):
    """L9 values for this script: a dish name the creator may type runs to its maxLength."""
    rules = typed_rules(t)
    if not rules:
        return SAMPLE
    cap = rules.get("maxLength") or 40
    name = TYPED_SAMPLE[:cap]
    if len(TYPED_SAMPLE) > cap and TYPED_SAMPLE[cap] != " ":
        name = name.rsplit(" ", 1)[0]
    return {**SAMPLE, "menuItem.name": name}


def phrases(*words):
    return re.compile(r"(?<![a-z'])(?:" + "|".join(words) + r")(?![a-z])", re.I)


HEARSAY = phrases(r"says", r"said", r"told me", r"tell me about", r"keeps? telling", r"everyone", r"everybody",
                  r"they all", r"people (?:say|talk)", r"locals", r"known for", r"talks? about",
                  r"barista's pick", r"server's pick", r"staff pick", r"recommended by")
TEASER = phrases(r"here'?s how it tastes", r"here is how it tastes", r"here'?s why", r"here is why",
                 r"here'?s my (?:honest|real)", r"here is my (?:honest|real)", r"honest (?:answer|reaction)",
                 r"let'?s see (?:if|why)", r"let'?s find out", r"moment of truth", r"before i tell you",
                 r"what i really think", r"going to be honest", r"worth the hype")
JUDGEMENT = phrases(r"love[ds]?", r"amazing", r"delicious", r"silky", r"smooth", r"bitter", r"perfect(?:ly)?",
                    r"best", r"wow", r"incredible", r"worth", r"great", r"tasty", r"better", r"favou?rite",
                    r"cozy", r"cosy", r"vibes?", r"beautiful", r"gorgeous", r"looks right", r"finishing all",
                    r"expected", r"so good", r"really good", r"certainly", r"absolutely", r"definitely", r"legit",
                    r"solid", r"fantastic", r"spectacular", r"awesome", r"highly recommend", r"hype")
CALL_TO_ACTION = phrases(r"go try", r"try it", r"come (?:try|see|by|visit)", r"go visit", r"visit (?:us|them|today|soon)", r"book (?:a|your|now)", r"follow", r"don'?t miss",
                         r"must", r"you have to", r"run,? don'?t walk", r"tell me what")
TIME_OF_DAY = phrases(r"morning", r"tonight'?s?", r"evening", r"lunch", r"breakfast", r"brunch", r"dinner",
                      r"happy hour", r"noon", r"night", r"walk to work", r"after work", r"before work")
BANNED = phrases(r"best in town", r"best", r"#1", r"number one", r"famous", r"award[- ]winning", r"legendary",
                 r"must[- ]try", r"only place", r"free", r"discount", r"\d+ ?% off", r"deal", r"buy one", r"life changing",
                 r"100%", r"hidden gem")
METRIC = re.compile(r"\b\d+(?:\.\d+)?\s?(?:cm|mm|m|km|meters?|metres?|centimet(?:er|re)s?)\b", re.I)
ZOOM = re.compile(r"\b\d(?:\.\d)?x\b(?! \()", re.I)
ASKS_PRICE = phrases(r"the price", r"what it costs", r"how much")
ASKS_MISSING = phrases(r"the street", r"the address", r"opening hours", r"the hours")
ASKS_DISH = phrases(r"dish'?s name", r"say the dish", r"name the dish")


def slots(text):
    return SLOT.findall(text or "")


def words(text):
    """Card words: a slot counts as one word, the opinion slot as none (it is the creator's)."""
    return len(re.findall(r"[A-Za-z0-9']+", SLOT.sub(lambda m: "" if m.group(1) == "opinion" else "slot", text)))


def fill(text, values):
    return SLOT.sub(lambda m: values.get(m.group(1), m.group(0)), text)


def opinion_texts(step, sets):
    """The texts the creator can pick for the step's slot, longest first (spoken length is checked with the longest)."""
    record = sets.get((step.get("opinion") or {}).get("set"))
    if not record:
        return []
    texts = [o["text"] for o in record["options"] if o.get("text")]
    if record.get("multiSelect"):
        picks = sorted(texts, key=step_fields.slotted_words, reverse=True)[:record.get("maxPicks", 1)]
        texts.append(", ".join(picks))
    return sorted(texts, key=step_fields.slotted_words, reverse=True)


def with_longest(text, step, sets):
    options = opinion_texts(step, sets)
    return text.replace("{opinion}", options[0] if options else "") if "{opinion}" in text else text


def texts(step):
    """(kind, label, text) for every text the step shows or has said: line-like, card, caption-like, direction."""
    out = []
    add = lambda kind, label, text: text and out.append((kind, label, text))
    add("line", "line", step.get("line"))
    add("line", "prompter", step.get("prompter"))
    add("card", "card", step.get("card"))
    add("caption", "caption", step.get("caption"))
    add("direction", "direction", step.get("direction"))
    for i, c in enumerate(step.get("captions") or []):
        add("caption", f"captions[{i}].text", c.get("text"))
        add("line", f"captions[{i}].script", c.get("script"))
    variants = dict(step.get("lineVariants") or {})
    if step.get("noPrice"):
        variants["noPrice"] = step["noPrice"]
    for name, variant in variants.items():
        for key, kind in (("line", "line"), ("card", "card"), ("caption", "caption")):
            add(kind, f"{name}.{key}", (variant or {}).get(key))
    for name, variant in (step.get("servingVariants") or {}).items():
        add("direction", f"{name}.direction", (variant or {}).get("direction"))
    return out


def step_rules(t, s, sets, p0):
    tid, sw = t["id"], f"{t['id']}/{s['id']}"
    found = []
    hit = lambda rule, message: found.append((rule, sw, message))
    complex_step = s.get("complexity") == "complex"
    all_texts = texts(s)
    script_slots = {x for step in t["steps"] for _, _, text in texts(step) for x in slots(text)}
    for kind, label, text in all_texts:
        if kind == "direction":
            if METRIC.search(text):
                hit("L-units", f"{label}: metric distance '{METRIC.search(text).group(0)}' (US units)")
            if ZOOM.search(text):
                hit("L-units", f"{label}: unexplained zoom '{ZOOM.search(text).group(0)}' (say '2x (closer)')")
            if ASKS_MISSING.search(text):
                hit("L6", f"{label}: asks for '{ASKS_MISSING.search(text).group(0)}', which no script has")
            if ASKS_PRICE.search(text) and "menuItem.price" not in script_slots:
                hit("L6", f"{label}: asks for the price, the script has no price slot")
            if ASKS_DISH.search(text) and not t.get("featuresMenuItem"):
                hit("L6", f"{label}: asks for '{ASKS_DISH.search(text).group(0)}', the script has no menu item")
            continue
        bare = SLOT.sub(" ", text)
        if HEARSAY.search(bare):
            hit("L1", f"{label}: hearsay or crowd claim '{HEARSAY.search(bare).group(0)}': '{text}'")
        if kind != "caption" and TEASER.search(bare):
            hit("L2", f"{label}: teaser '{TEASER.search(bare).group(0)}': '{text}'")
        if kind in ("line", "card") and JUDGEMENT.search(bare):
            hit("L3", f"{label}: judgement '{JUDGEMENT.search(bare).group(0)}' outside an opinion slot: '{text}'")
        if kind == "caption":
            m = JUDGEMENT.search(bare) or CALL_TO_ACTION.search(bare) or TEASER.search(bare)
            if m or "?" in text or "{opinion}" in text:
                hit("L4", f"{label}: caption is not a fact ('{m.group(0) if m else 'opinion or question'}'): '{text}'")
        if p0 and not label.split(".")[0] in step_fields.DAYPARTS and TIME_OF_DAY.search(bare):
            hit("L5", f"{label}: time of day '{TIME_OF_DAY.search(bare).group(0)}' in a P0 text: '{text}'")
        for name in slots(text):
            if name not in SLOTS:
                hit("L6", f"{label}: unknown slot {{{name}}}")
            elif name in MENU_SLOTS and not t.get("featuresMenuItem"):
                hit("L6", f"{label}: {{{name}}} in a script without a menu item")
            elif name == "menuItem.price" and typed_rules(t):
                hit("L6", f"{label}: {{menuItem.price}} in a script whose dish may be typed, which never has a price")
        if BANNED.search(bare):
            hit("L12", f"{label}: banned claim '{BANNED.search(bare).group(0)}': '{text}'")
        n = slots(text).count("opinion")
        if n > 1:
            hit("L11", f"{label}: the opinion slot appears {n} times")
        if n and not s.get("opinion"):
            hit("L11", f"{label}: {{opinion}} without an opinion block")
    # L7: complex steps are silent.
    if complex_step and (s.get("line") or s.get("prompter")):
        hit("L7", "complex step with a spoken line or prompter")
    # L8: spoken length fits the step with the longest option in.
    if not complex_step:
        for kind, label, text in all_texts:
            if kind != "line":
                continue
            spoken = with_longest(text, s, sets)
            need = step_fields.line_seconds(spoken)
            if need > s.get("seconds", 0) or need > step_fields.MAX_STEP_SECONDS:
                hit("L8", f"{label}: needs {need} s with the longest option in, the step is {s.get('seconds')} s: '{spoken}'")
    # L9: real-length values fit (line 8 s, caption 32 characters).
    values = sample(t)
    for kind, label, text in all_texts:
        if kind == "line" and not complex_step:
            if step_fields.MAX_STEP_SECONDS < step_fields.line_seconds(fill(with_longest(text, s, sets), values)):
                hit("L9", f"{label}: over 8 s with real-length values")
        # No short names exist to fall back to, so a long caption wraps in the app: a warning, not an error.
        if kind == "caption" and len(fill(text, values)) > CAPTION_CHARS:
            hit("L9-caption", f"{label}: over {CAPTION_CHARS} characters with real-length values, wraps: '{fill(text, values)}'")
    # L10: a missing price never leaves a hole; the step carries a noPrice variant without the price.
    uses_price = any("menuItem.price" in slots(s.get(k)) for k in ("line", "card", "caption"))
    if uses_price:
        variant = s.get("noPrice")
        if not variant:
            hit("L10", "uses {menuItem.price} without a noPrice variant")
        elif any("menuItem.price" in slots(variant.get(k)) for k in ("line", "card", "caption")):
            hit("L10", "the noPrice variant still uses {menuItem.price}")
        elif any(bool(s.get(k)) != bool(variant.get(k)) for k in ("line", "card", "caption")):
            hit("L10", "the noPrice variant must replace each of line, card and caption the step has")
    # L11: the block and the slot go together; the opinion fills the line and card, never the caption.
    block = s.get("opinion")
    if block:
        record = sets.get(block.get("set"))
        if record is None:
            hit("L11", f"opinion set {block.get('set')} does not exist")
        else:
            ids = [o["id"] for o in record["options"]]
            if block.get("preselect") is not None and (not record.get("preselectAllowed") or block["preselect"] not in ids):
                hit("L11", f"preselect {block['preselect']} is not allowed in {record['id']}")
            if record["kind"] in NO_PRESELECT and block.get("preselect") is not None:
                hit("L11", f"a {record['kind']} slot is never preselected")
            bad = [o for o in block.get("order") or [] if o not in ids]
            if bad or len(set(block.get("order") or [])) != len(block.get("order") or []):
                hit("L11", f"order names unknown or repeated options {bad}")
            if record["kind"] == "verdict":
                first = [o for o in record["options"] if o["id"] == (block.get("order") or [None])[0]]
                if not first or first[0]["tone"] != "positive":
                    hit("L11", "a verdict order starts with the script's own positive word")
        if "{opinion}" not in (s.get("line") or "") + (s.get("card") or ""):
            hit("L11", "opinion block without an {opinion} slot in the line or card")
    # L13: a step with a face guide also offers a face-free guide (a pending one counts, as a warning).
    levels = step_fields.LEVELS["guides"]
    guides = s.get("guides") or []
    if any(levels.get(g, {}).get("showsFace") for g in guides):
        free = [g for g in guides if levels.get(g, {}).get("showsFace") is False]
        pending = [g for g in step_fields.LEVELS["pending"] if f"{tid}.{s['id']}" in g.get("steps", []) and g.get("showsFace") is False]
        if not free and not pending:
            hit("L13", f"face guides {guides} and no face-free guide")
        elif not free:
            hit("L13-pending", f"face-free guide pending: {[g['id'] for g in pending]}")
    unknown = [g for g in guides if "showsFace" not in levels.get(g, {})]
    if unknown:
        hit("L13", f"guides without showsFace: {unknown}")
    # L14: every step has a card (or titleFacts); a card is at most 6 words.
    card = s.get("card")
    if not card and not s.get("titleFacts"):
        hit("L14", "no card and no titleFacts")
    elif card is None:
        hit("L14", "no card")
    for kind, label, text in all_texts:
        if kind == "card" and words(text) > CARD_WORDS:
            hit("L14", f"{label}: {words(text)} words (at most {CARD_WORDS})")
    return found


def set_rules(sets):
    found = []
    for sid, record in sets.items():
        hit = lambda message: found.append(("set", f"opinionSets/{sid}", message))
        if record.get("kind") not in KINDS:
            hit(f"kind {record.get('kind')}")
        options = record.get("options") or []
        ids = [o.get("id") for o in options]
        if len(set(ids)) != len(ids):
            hit("repeated option ids")
        if not any(o.get("tone") == "neutral" for o in options):
            hit("no neutral option")
        if record.get("allowCustom") is not True:
            hit("allowCustom must be true")
        if record.get("kind") in NO_PRESELECT and record.get("preselectAllowed"):
            hit(f"a {record['kind']} set never allows a preselection")
        if record.get("kind") == "verdict" and not any(o.get("action") == "private_feedback" for o in options):
            hit("a verdict set needs the private_feedback (Not for me) action")
        if record.get("multiSelect") and not record.get("maxPicks"):
            hit("multiSelect without maxPicks")
        for o in options:
            if o.get("tone") not in TONES:
                hit(f"{o.get('id')}: tone {o.get('tone')}")
            if o.get("action"):
                if o.get("text") is not None or not o.get("label"):
                    hit(f"{o.get('id')}: an action has text null and a label")
                continue
            text = o.get("text") or ""
            if not text:
                hit(f"{o.get('id')}: empty text")
            if words(text) > record.get("maxWords", 0):
                hit(f"{o.get('id')}: '{text}' is over {record.get('maxWords')} words")
            for rule, pattern in (("L1", HEARSAY), ("L2", TEASER), ("L5", TIME_OF_DAY), ("L12", BANNED), ("L6", SLOT)):
                if pattern.search(text):
                    hit(f"{o.get('id')}: '{text}' breaks {rule}")
    return found


def dish_source_rules(templates):
    """dishSource: "menu" (picked from the venue's menu; with no menu either a whenNoMenu fallback script or a
    typedFallback inside this script) or "typed" (the creator types the name before filming: maxLength, hint; never a
    price)."""
    found, by_id = [], {t["id"]: t for t in templates}
    for t in templates:
        source = t.get("dishSource")
        if source is None:
            continue
        hit = lambda message, rule="dishSource": found.append((rule, t["id"], message, t["id"] in step_fields.P0_SCRIPTS))
        kind = source.get("kind")
        if kind not in DISH_SOURCES:
            hit(f"kind {kind} (menu or typed)")
        if not t.get("featuresMenuItem"):
            hit("a dish source needs featuresMenuItem: true")
        if kind == "menu":
            if set(source) - {"kind", "whenNoMenu", "typedFallback"}:
                hit(f"a menu source has only kind, whenNoMenu and typedFallback, not {sorted(set(source) - {'kind', 'whenNoMenu', 'typedFallback'})}")
            if "whenNoMenu" in source and "typedFallback" in source:
                hit("a menu source has whenNoMenu or typedFallback, not both")
            fallback = source.get("whenNoMenu")
            if fallback is not None:
                other = by_id.get(fallback)
                if other is None:
                    # Checking one part file alone: the fallback may live in another part.
                    hit(f"whenNoMenu {fallback} is not among the checked scripts", "dishSource-missing")
                elif (other.get("dishSource") or {}).get("kind") != "typed":
                    hit(f"whenNoMenu {fallback} is not a typed-dish script")
                elif set(t["venueKinds"]) - set(other["venueKinds"]):
                    hit(f"whenNoMenu {fallback} does not cover venue kinds {sorted(set(t['venueKinds']) - set(other['venueKinds']))}")
        rules = typed_rules(t) if kind in DISH_SOURCES else None
        if kind == "menu" and "typedFallback" in source and not isinstance(rules, dict):
            hit("typedFallback is an object with maxLength and hint")
        elif isinstance(rules, dict):
            allowed = {"kind", "maxLength", "hint"} if kind == "typed" else {"maxLength", "hint"}
            if set(rules) - allowed:
                hit(f"typed rules have only {sorted(allowed)}, not {sorted(set(rules) - allowed)}")
            cap = rules.get("maxLength")
            if not isinstance(cap, int) or not 10 <= cap <= 60:
                hit(f"maxLength {cap} (10 to 60 characters)")
            hint = rules.get("hint")
            if not isinstance(hint, str) or not hint or len(hint) > HINT_CHARS:
                hit(f"hint is required, at most {HINT_CHARS} characters")
            elif SLOT.search(hint):
                hit("the hint has no placeholders")
    return found


def lint(templates, sets_list):
    sets = {s["id"]: s for s in sets_list or []}
    found = set_rules(sets)
    found += dish_source_rules(templates)
    for t in templates:
        p0 = t["id"] in step_fields.P0_SCRIPTS
        for s in t["steps"]:
            found += [(rule, where, message, p0) for rule, where, message in step_rules(t, s, sets, p0)]
    return [f if len(f) == 4 else f + (True,) for f in found]
