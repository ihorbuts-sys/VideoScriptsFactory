"""Reference resolver for catalog version 3: turns one request into the script the app shows.

The backend runs this logic (decision D-backend-resolves, 2026-11-16); the app keeps the full catalog only as an offline
fallback and runs the same logic there. Standard library only.

    resolve(catalog, request) -> {"kind", "context", "steps", ...}

Request A (the app knows the kind):
    {"kind": "dish-review" | "drink-review" | "venue-review",
     "dishKind" | "drinkKind": "<frozen id>",          # dish and drink reviews
     "serviceKind": "dineIn" | "counter" | "truck",     # from the venue category
     "subject": "<venue subject>",                     # venue review only
     "price": true | false,
     "businessAmenities": ["free_wifi", ...]}          # optional, preselects amenity chips
Request B (from a menu item):
    {"kind": "menu-item-review", "serviceKind": "...",
     "menuItem": {"name": "...", "price": "9.50 USD" | null, "section": "Breakfast", "videoKind": "<frozen id>"?},
     "kindChip": "<frozen id>"?,                       # the creator's override for this video
     "businessAmenities": [...]}

Override order for request B: kindChip, then menuItem.videoKind, then the menu section keyword match
(tables.menuSectionMapping), then the fallback (dish-review, no dish kind, the app shows the kind chip).
`daypart` and `typedName` do not change the steps: every version is returned with its tags and the app preselects
one version (tags first, random among equals) and shows the others as "Other options".
"""
import copy
import json
import re

SLOT = re.compile(r"\{(opinion|amenity)\}")
CHOICE_KEYS = ("kind", "levels", "options", "allowCustom", "maxWords", "multiSelect", "privateFeedback", "answers")


def menu_kind(section, tables):
    """(review kind, dish or drink kind id) for a menu section; unknown -> (dish-review, None).
    Case-insensitive match at a word start (Ukrainian entries are stems); the longest matching keyword wins."""
    text = (section or "").lower()
    best = None
    for review, group in (("dish-review", "dishKinds"), ("drink-review", "drinkKinds")):
        for k in tables[group]:
            for word in k["menuKeywords"]:
                if re.search(r"(?<!\w)" + re.escape(word.lower()), text) and (best is None or len(word) > best[0]):
                    best = (len(word), review, k["id"])
    return (best[1], best[2]) if best else ("dish-review", None)


def kind_of(kind_id, tables):
    """(review kind, kind id) for a frozen dish or drink kind id, following `replacedBy` for deprecated ids."""
    for review, group in (("dish-review", "dishKinds"), ("drink-review", "drinkKinds")):
        for k in tables[group]:
            if k["id"] == kind_id:
                if k.get("deprecated") and k.get("replacedBy"):
                    return kind_of(k["replacedBy"], tables)
                return review, k["id"]
    raise ValueError("unknown kind id: %s" % kind_id)


def context_for(request, tables):
    """The variant context a request resolves in: kind, dish or drink kind, serviceKind or subject, price."""
    if request["kind"] != "menu-item-review":
        ctx = {k: request[k] for k in ("kind", "dishKind", "drinkKind", "serviceKind", "subject", "price") if k in request}
        return ctx, None
    item = request["menuItem"]
    chosen = request.get("kindChip") or item.get("videoKind")
    review, kind_id = kind_of(chosen, tables) if chosen else menu_kind(item.get("section"), tables)
    ctx = {"kind": review}
    if kind_id:
        ctx["dishKind" if review == "dish-review" else "drinkKind"] = kind_id
    ctx["price"] = bool(item.get("price"))
    if "serviceKind" in request:
        ctx["serviceKind"] = request["serviceKind"]
    return ctx, item


def matches(when, context):
    return all(context.get(k) == val for k, val in (when or {}).items())


def effective_step(step, context):
    """Base step plus the first variant whose `when` matches the context; variants and authoring keys removed."""
    out = copy.deepcopy(step)
    out.pop("variants", None)
    for var in step.get("variants") or []:
        if matches(var.get("when"), context):
            for k, val in var.items():
                if k != "when":
                    out[k] = copy.deepcopy(val)
            break
    out.pop("gap", None)
    return out


def inline_choice(step, sets, business_amenities):
    """Writes the referenced choice set into the step and marks which versions use it (chips show only then)."""
    choice = step.get("choice")
    if not choice or choice.get("set") not in sets:
        return
    src = sets[choice["set"]]
    inline = {k: copy.deepcopy(src[k]) for k in CHOICE_KEYS if k in src}
    if src.get("kind") == "amenity":
        inline["businessPreselectExample"] = list(business_amenities or [])
        inline["source"] = src.get("source")
    choice["inline"] = inline
    choice["showChipsWhen"] = "the selected version contains " + ("{amenity}" if src.get("kind") == "amenity" else "{opinion}")
    for v in step.get("versions", []):
        v["usesChoice"] = bool(SLOT.search(" ".join(str(v.get(k) or "") for k in ("line", "card", "caption"))))


def resolve(catalog, request):
    tables = catalog["tables"]
    sets = {s["id"]: s for s in catalog["choiceSets"]}
    scripts = {k["kind"]: k for k in catalog["kinds"]}
    ctx, item = context_for(request, tables)
    script = scripts[ctx["kind"]]
    steps = []
    for s in script["steps"]:
        if "sameAs" in s:
            s = next(x for x in scripts[s["sameAs"]]["steps"] if x["key"] == s["key"])
        step = effective_step(s, ctx)
        inline_choice(step, sets, request.get("businessAmenities"))
        steps.append(step)
    out = {"kind": ctx["kind"], "context": ctx}
    if item is not None:
        out["menuItem"] = {k: item[k] for k in ("name", "price", "section") if k in item}
        out["derivedFrom"] = "menu-item-review"
    consent = [c for c in script.get("consent") or [] if matches(c.get("when"), ctx)]
    if consent:
        out["consent"] = copy.deepcopy(consent)
    out["steps"] = steps
    return out


if __name__ == "__main__":
    import sys
    cat = json.load(open(sys.argv[1], encoding="utf-8"))
    req = json.load(open(sys.argv[2], encoding="utf-8"))
    print(json.dumps(resolve(cat, req), indent=1, ensure_ascii=False))
