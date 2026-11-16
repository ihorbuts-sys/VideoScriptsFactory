#!/usr/bin/env python3
"""Script writer backend for the demo: writes script step texts with Claude Code on this Mac.

POST /v1/scripts/write    a script writing request -> {"steps": [...]} (see README.md)
GET  /v1/venues?page=1    venues to pick from -> {"venues": [...], "nextPage": 2}
GET  /v1/venues/{id}/menu the venue's menu -> {"items": [...]}
GET  /v1/music?query=&page=0&pageSize=20  the demo music catalog -> {"tracks": [...], "nextPage": 1}
GET  /v1/music/files/{name}?token=  a track's audio (the token rides in the link the catalog gives)
GET  /v1/venue-kinds      the script catalog's venue kinds -> {"venueKinds": [...]}
GET  /v1/venues/{id}/scripts?page=0&pageSize=20  the venue's scripts, its kind decided here from its Loca categories
GET  /v1/scripts?venueKind=coffee&page=0&pageSize=20  a kind's scripts (every kind's without venueKind)
GET  /v1/steps?page=0&pageSize=40&venueKind=  every step for custom scripts, grouped by venue kind (and "general")
GET  /v1/guides?page=0&pageSize=20  all unique guides with animation, poster and strip links
GET  /v1/guides/{id}?duration=  a guide by id
GET  /v1/steps/{templateID.stepID}/guides?venueID=&duration=  the step's live guides; duration stretches the holds
GET  /v1/files/{previews|overlays|scenarios|3d}/{name}?token=  a step picture, a guide's APNG, scenario or 3D spec

Every request needs `Authorization: Bearer <token>`; the token is kept in `.token` next to this file.
"""
import argparse
import json
import os
import secrets
import shutil
import select
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
# The Loca test environment, as the Loca dev app uses; every query here is a public read.
GRAPHQL = os.environ.get("LOCA_GRAPHQL", "https://creator.graphql.test.loca.us/graphql")
SCHEMA = json.load(open(os.path.join(HERE, "response_schema.json")))
# The kit demo's tracks and the catalog its tools/beatmarker wrote for them (the MP3s stay out of git).
MUSIC_DIR = os.environ.get("MUSIC_DIR", os.path.join(HERE, "..", "VideoEditorKit", "Demo", "VideoEditorDemo", "Music"))
VENUE_PAGE_SIZE = 30
# The script catalog built by Loca's ScriptsAndGuides/guides/tools/build_bundle.py: catalog.json + assets.
CATALOG_DIR = os.environ.get("SCRIPT_CATALOG_DIR", os.path.join(HERE, "catalog"))
_catalog = None
_catalog_revision = None
_venue_kind_cache = {}

VENUE_QUERY = """
query($id: UUID!, $ids: [UUID!]) {
  businessById(id: $id) {
    title description menuUrl
    categories { title }
    amenityList { title }
    averagePriceRange { startUnits endUnits currencyCode }
  }
  businessLocationCollection(filters: {businessIds: $ids}, offsetBasedPagination: {page: 1, limit: 1}) {
    items { city street streetNumber website generativeSummary reviewSummary { text } }
  }
}
"""

MENU_QUERY = """
query($id: UUID!) {
  businessById(id: $id) { menuDestination { url } }
  menusByBusinessId(businessId: $id, offsetBasedPagination: {page: 1, limit: 10}) {
    items {
      currency currencyMinorUnitFactor
      sections { title items { id name description dietaryTags { title } variants { amountMinorUnits currency currencyMinorUnitFactor } } }
    }
  }
}
"""

VENUE_KIND_QUERY = """
query($id: UUID!) {
  businessById(id: $id) { categories { slug } }
}
"""

VENUES_QUERY = """
query($page: Int!, $limit: Int!) {
  businessCollection(offsetBasedPagination: {page: $page, limit: $limit}) {
    items { id title hasPublishedMenu categories { title } loyaltyReward { status steps { stepNumber amountInCents } } }
  }
}
"""
_all_venues = None


def graphql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(GRAPHQL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        result = json.load(error)
    if result.get("errors"):
        raise RuntimeError(result["errors"][0].get("message", "GraphQL error"))
    return result["data"]


def shorten(text, limit):
    text = (text or "").strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "..."


def venue_brief(venue_id):
    """The venue's facts as plain lines, from the business and its first location."""
    data = graphql(VENUE_QUERY, {"id": venue_id, "ids": [venue_id]})
    business = data["businessById"]
    if not business:
        return None
    locations = data["businessLocationCollection"]["items"]
    location = locations[0] if locations else {}
    price = business.get("averagePriceRange")
    lines = [
        f"Name: {business['title']}",
        "Kind: " + ", ".join(c["title"] for c in business.get("categories") or []),
        "Description: " + shorten(business.get("description"), 600),
        "Address: " + " ".join(filter(None, [location.get("street"), location.get("streetNumber"), location.get("city")])),
        "Price: " + (f"{price['startUnits']}-{price['endUnits']} {price['currencyCode']}" if price else ""),
        "Amenities: " + ", ".join(a["title"] for a in business.get("amenityList") or []),
        "About: " + shorten(location.get("generativeSummary"), 300),
        "What guests say: " + shorten((location.get("reviewSummary") or {}).get("text"), 600),
        "Menu: " + (business.get("menuUrl") or ""),
        "Website: " + (location.get("website") or ""),
    ]
    return "\n".join(line for line in lines if not line.endswith(": "))


def venues(page):
    """Every venue, the ones with a Loca menu first; loaded once per server run."""
    global _all_venues
    if _all_venues is None:
        loaded, next_page = [], 1
        while next_page:
            items = graphql(VENUES_QUERY, {"page": next_page, "limit": 100})["businessCollection"]["items"]
            loaded += [{
                "id": business["id"],
                "title": business["title"],
                "kind": ", ".join(c["title"] for c in business.get("categories") or []),
                "city": "",
                "hasMenu": bool(business.get("hasPublishedMenu")),
                "reward": active_reward(business.get("loyaltyReward")),
            } for business in items]
            next_page = next_page + 1 if len(items) == 100 else None
        _all_venues = sorted(loaded, key=lambda venue: (not venue["hasMenu"], venue["title"].lower()))
    start = (page - 1) * VENUE_PAGE_SIZE
    return {"venues": _all_venues[start:start + VENUE_PAGE_SIZE], "nextPage": page + 1 if start + VENUE_PAGE_SIZE < len(_all_venues) else None}


def active_reward(loyalty):
    """Cash back per visit, only while the reward is active. Loca rewards carry no currency; they are US dollars."""
    steps = sorted((loyalty or {}).get("steps") or [], key=lambda step: step["stepNumber"])
    if (loyalty or {}).get("status") != "Active" or not steps:
        return None
    return {"perVisitCents": [step["amountInCents"] for step in steps], "currency": "USD"}


def menu(venue_id):
    """Every item of the venue's menus with a formatted price (the first variant's)."""
    data = graphql(MENU_QUERY, {"id": venue_id})
    menu_url = ((data.get("businessById") or {}).get("menuDestination") or {}).get("url")
    items = []
    for menu in data["menusByBusinessId"]["items"]:
        for section in menu["sections"]:
            for item in section["items"]:
                variant = (item.get("variants") or [None])[0]
                price = None
                if variant and variant.get("amountMinorUnits") is not None:
                    factor = variant.get("currencyMinorUnitFactor") or menu.get("currencyMinorUnitFactor") or 100
                    price = f"{variant['amountMinorUnits'] / factor:.2f} {variant.get('currency') or menu.get('currency') or ''}".strip()
                items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "description": item.get("description"),
                    "section": section["title"],
                    "price": price,
                    "dietary": [tag["title"] for tag in item.get("dietaryTags") or [] if tag.get("title")],
                    "menuURL": menu_url,
                })
    return {"items": items}


class Cancelled(Exception):
    pass


# ---------------------------------------------------------------- script catalog
def catalog():
    """Reload a completely published catalog when its atomic index changes."""
    global _catalog, _catalog_revision
    path = os.path.join(CATALOG_DIR, "catalog.json")
    if not os.path.isfile(path):
        raise RuntimeError(f"no script catalog at {path}: run ScriptsAndGuides/guides/tools/build_bundle.py")
    stat = os.stat(path)
    revision = (stat.st_mtime_ns, stat.st_size)
    if _catalog is None or revision != _catalog_revision:
        with open(path, encoding="utf-8") as file:
            updated = json.load(file)
        _catalog = updated
        _catalog_revision = revision
        _venue_kind_cache.clear()
    return _catalog


def file_url(base_url, token, relative):
    return f"{base_url}/v1/files/{relative}?token={token}"


def with_links(step, base_url, token, template_id=None):
    """A step with its picture and guides as links to this server."""
    guides = catalog()["guides"]
    out = dict(step)
    if step.get("imageURL"):
        out["imageURL"] = file_url(base_url, token, step["imageURL"])
    owner = template_id or step.get("templateID")
    key = owner + "." + step["id"] if owner else ""
    overrides = catalog().get("stepGuideOverrides", {}).get(key, {})
    out["overlays"] = [file_url(base_url, token, overrides.get(g, {}).get("overlay", guides[g]["overlay"])) for g in step.get("overlays", []) if g in guides]
    return out


def template_with_links(template, base_url, token):
    out = dict(template)
    out["steps"] = [with_links(step, base_url, token, template["id"]) for step in template["steps"]]
    return out


def paged(items, page, page_size):
    size = max(page_size, 1)
    start = max(page, 0) * size
    chosen = items[start:start + size]
    return chosen, (page + 1 if start + size < len(items) else None)


def kind_for_slugs(slugs):
    """The first kind in priority order that one of the venue's category slugs belongs to."""
    slugs = set(slugs)
    for entry in catalog()["categoryKinds"]:
        if slugs & set(entry["slugs"]):
            return entry["kind"]
    return None


def venue_kind(venue_id):
    """The venue's script kind from its Loca categories; None when nothing fits. Cached per run."""
    if venue_id not in _venue_kind_cache:
        business = graphql(VENUE_KIND_QUERY, {"id": venue_id})["businessById"]
        if not business:
            raise RuntimeError(f"unknown venue {venue_id}")
        _venue_kind_cache[venue_id] = kind_for_slugs(c["slug"] for c in business.get("categories") or [])
    return _venue_kind_cache[venue_id]


def scripts(kind, page, page_size, base_url, token):
    templates = [t for t in catalog()["templates"] if kind is None or kind in t["venueKinds"]]
    chosen, next_page = paged(templates, page, page_size)
    return {"venueKind": kind, "templates": [template_with_links(t, base_url, token) for t in chosen], "nextPage": next_page}


def venue_scripts(venue_id, page, page_size, base_url, token):
    kind = venue_kind(venue_id)
    if kind is None:
        return {"venueKind": None, "templates": [], "nextPage": None}
    return scripts(kind, page, page_size, base_url, token)


def steps(kind, page, page_size, base_url, token):
    """A page of the step library, grouped by venue kind; a kind filter keeps that kind's steps and the general ones."""
    flat = []
    for group in catalog()["stepGroups"]:
        if kind and group["venueKind"] not in (kind, None):
            continue
        for step in group["steps"]:
            flat.append((group, step))
    chosen, next_page = paged(flat, page, page_size)
    groups = []
    for group, step in chosen:
        if not groups or groups[-1]["venueKind"] != group["venueKind"]:
            groups.append({"venueKind": group["venueKind"], "title": group["title"], "steps": []})
        groups[-1]["steps"].append(with_links(step, base_url, token))
    return {"groups": groups, "nextPage": next_page}


GHOST_SECONDS = {"frame": 1.2, "whip": 1.0, "reframe": 1.5}


def ghost_seconds(step):
    kind = step["kind"]
    if kind == "frame":
        return GHOST_SECONDS["frame"]
    if kind == "follow":
        return GHOST_SECONDS["whip"] if step.get("action") == "whip" else step.get("duration", 2.0)
    if kind == "reframe":
        return GHOST_SECONDS["reframe"]
    return step.get("duration", 1.0)


def stretched(scenario, seconds):
    """The scenario with its holds and stills scaled so the ghost's loop lasts `seconds` (2 to 60); the moves keep
    their pace. Returned as is when nothing can stretch or the length already fits."""
    seconds = max(2.0, min(float(seconds), 60.0))
    steps = scenario["steps"]
    fixed = sum(ghost_seconds(s) for s in steps if s["kind"] not in ("hold", "still"))
    holds = [s for s in steps if s["kind"] in ("hold", "still")]
    current = sum(s.get("duration", 1.0) for s in holds)
    if not holds or abs(fixed + current - seconds) < 0.05:
        return scenario, round(fixed + current, 2)
    factor = max(0.3, (seconds - fixed) / max(current, 0.01))
    out = json.loads(json.dumps(scenario))
    for s in out["steps"]:
        if s["kind"] in ("hold", "still"):
            s["duration"] = round(s.get("duration", 1.0) * factor, 2)
    return out, round(fixed + sum(s["duration"] for s in out["steps"] if s["kind"] in ("hold", "still")), 2)


def find_step(step_id):
    """A catalog step by `templateID.stepID` (a dot inside either part is resolved from the right)."""
    for template in catalog()["templates"]:
        if step_id.startswith(template["id"] + "."):
            rest = step_id[len(template["id"]) + 1:]
            for step in template["steps"]:
                if step["id"] == rest:
                    return template, step
    return None, None


def guide_with_links(gid, base_url, token, duration=None, override=None):
    guide = dict(catalog()["guides"][gid])
    if override:
        guide.update(override)
    seconds = guide["seconds"]
    if duration is None and guide.get("opacityAppliedIn") == "image_view":
        duration = seconds
    scenario_url = file_url(base_url, token, guide["scenario"])
    if duration:
        with open(os.path.join(CATALOG_DIR, guide["scenario"]), encoding="utf-8") as file:
            _, seconds = stretched(json.load(file), duration)
        scenario_url += f"&duration={duration}"
    result = {
        "id": gid,
        "overlayURL": file_url(base_url, token, guide["overlay"]),
        "scenarioURL": scenario_url,
        "model3DURL": file_url(base_url, token, guide["model3D"]),
        "seconds": seconds,
        "camera": guide["camera"],
        "moves": guide["moves"],
        "subject": guide["subject"],
        "style": guide.get("style", "schematic"),
    }
    for key in ("sha256", "animationSeconds", "alphaFactor", "rendering", "scope", "handoverStatus", "contextTemplateID", "contextStepID", "nextGuideID", "imageViewOpacity", "opacityAppliedIn"):
        if guide.get(key) is not None:
            result[key] = guide[key]
    for key in ("poster", "strip", "colorVideo"):
        if guide.get(key):
            result[key + "URL"] = file_url(base_url, token, guide[key])
    return result


def all_guides(page, page_size, base_url, token):
    ids = sorted(catalog()["guides"])
    chosen, next_page = paged(ids, page, page_size)
    return {"guides": [guide_with_links(gid, base_url, token) for gid in chosen],
            "total": len(ids), "nextPage": next_page}


def step_guides(step_id, venue_id, duration, base_url, token):
    template, step = find_step(step_id)
    if step is None:
        raise RuntimeError(f"unknown step {step_id}")
    guides = catalog()["guides"]
    overrides = catalog().get("stepGuideOverrides", {}).get(step_id, {})
    out = [guide_with_links(gid, base_url, token, duration, overrides.get(gid))
           for gid in step.get("overlays", []) if gid in guides]
    kind = venue_kind(venue_id) if venue_id else None
    return {"stepID": step_id, "templateID": template["id"], "venueKind": kind, "seconds": duration or step["seconds"], "guides": out}


def script_guide_sequence(template_id, base_url, token):
    sequence = catalog().get("scriptGuideSequences", {}).get(template_id)
    if sequence is None:
        status = catalog().get("scriptGuideSequenceStatus", {}).get(template_id)
        if status:
            return {"id": template_id, "scope": "deferred_people", **status}
        return None
    result = {key: sequence[key] for key in ("id", "title", "seconds", "sha256", "steps")}
    for key in ("overlay", "video", "poster", "strip"):
        if sequence.get(key):
            result[key + "URL"] = file_url(base_url, token, sequence[key])
    result["scope"] = "full_script_instruction_sequence"
    for key in ("alphaFactor", "imageViewOpacity", "opacityAppliedIn", "fullScriptSequenceComplete",
                "sceneRevision", "viewfinderEmbedded", "wallsEmbedded", "floorEmbedded"):
        if key in sequence:
            result[key] = sequence[key]
    return result


CONTENT_TYPES = {".glb": "model/gltf-binary", ".jpg": "image/jpeg", ".png": "image/png", ".json": "application/json", ".usdz": "model/vnd.usdz+zip", ".mp4": "video/mp4"}


def run_claude(command, is_cancelled):
    """Runs Claude and returns its output; stops it when `is_cancelled()` turns true."""
    process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    started = time.time()
    while process.poll() is None:
        if is_cancelled():
            process.kill()
            raise Cancelled()
        if time.time() - started > 240:
            process.kill()
            raise RuntimeError("Claude took too long")
        time.sleep(0.25)
    return process.communicate()


def music(query, page, page_size, base_url, token):
    """The catalog page, each track's audio pointing back at this server."""
    tracks = json.load(open(os.path.join(MUSIC_DIR, "music_catalog.json")))["tracks"]
    term = (query or "").strip().lower()
    if term:
        tracks = [t for t in tracks if term in t["title"].lower() or term in t.get("author", "").lower()]
    start = max(page, 0) * max(page_size, 1)
    chosen = tracks[start:start + page_size]
    for track in chosen:
        track["audioURL"] = f"{base_url}/v1/music/files/{track['audioURL'].split('/')[-1]}?token={token}"
    return {"tracks": chosen, "nextPage": page + 1 if start + page_size < len(tracks) else None}


def write(request, model, is_cancelled=lambda: False):
    venue_id = request.get("venueID")
    try:
        brief = venue_brief(venue_id) if venue_id else None
    except Exception as error:
        # An unknown or unreachable venue only costs the facts; the script is still written.
        print(f"venue {venue_id} skipped: {error}", flush=True)
        brief = None
    prompt = "\n\n".join([
        "/script-writer",
        "## Venue\n" + (brief or "unknown"),
        "## Request\n```json\n" + json.dumps(request, ensure_ascii=False, indent=2) + "\n```",
    ])
    command = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--json-schema", json.dumps(SCHEMA),
        "--allowedTools", "WebFetch",
    ]
    stdout, stderr = run_claude(command, is_cancelled)
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Claude returned no result: " + (stderr or stdout)[-400:])
    if result.get("is_error") or "structured_output" not in result:
        raise RuntimeError("Claude failed: " + str(result.get("result"))[-400:])
    steps = result["structured_output"]["steps"]
    only = request.get("only")
    if only:
        steps = [step for step in steps if step["id"] in only]
    return {"steps": steps}


def venue_collections():
    path = os.path.join(CATALOG_DIR, "guide-collections.json")
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file).get("collections", {})
    except FileNotFoundError:
        return {}


def venue_collection_with_links(record, base_url, token):
    result = dict(record)
    for field in ("overlay", "video", "poster", "colorPoster", "strip", "colorStrip", "blender", "sceneSpec"):
        if field in result:
            relative = result.pop(field)
            key = "colorVideoURL" if field == "video" else field + "URL"
            result[key] = file_url(base_url, token, relative)
    if "phases" in result:
        result["phases"] = [venue_collection_with_links(phase, base_url, token) for phase in result["phases"]]
    return result


def guide_objects():
    path = os.path.join(CATALOG_DIR, "guide-objects.json")
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file).get("objects", {})
    except FileNotFoundError:
        return {}


def guide_object_with_links(record, base_url, token):
    result = dict(record)
    result["assets"] = {}
    for name, info in record.get("assets", {}).items():
        asset = {key: value for key, value in info.items() if key != "path"}
        asset["url"] = file_url(base_url, token, info["path"])
        result["assets"][name] = asset
        result[name + "URL"] = asset["url"]
    result["views"] = [{"name": view["name"], "sha256": view["sha256"],
                        "url": file_url(base_url, token, view["path"])} for view in record.get("views", [])]
    return result


class Handler(BaseHTTPRequestHandler):
    token = ""
    model = "sonnet"

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/v1/health":
            return self.reply(200, {"ok": True})
        if url.path.startswith("/v1/music/files/"):
            return self.send_music_file(url)
        if url.path.startswith("/v1/files/"):
            return self.send_catalog_file(url)
        if not self.authorized():
            return
        query = parse_qs(url.query)
        base_url = f"http://{self.headers.get('Host')}"
        page = int(query.get("page", ["0"])[0])
        page_size = int(query.get("pageSize", ["20"])[0])
        collection_parts = url.path.strip("/").split("/")
        if url.path == "/v1/guide-objects":
            records = list(guide_objects().values())
            category = query.get("category", [None])[0]
            if category:
                records = [record for record in records if record.get("category") == category]
            selected, next_page = paged(sorted(records, key=lambda record: record["id"]), page, page_size)
            return self.reply(200, {"objects": [guide_object_with_links(record, base_url, self.token) for record in selected],
                                    "total": len(records), "nextPage": next_page})
        if len(collection_parts) == 3 and collection_parts[:2] == ["v1", "guide-objects"]:
            record = guide_objects().get(collection_parts[2])
            if record is None:
                return self.reply(404, {"error": "unknown guide object"})
            return self.reply(200, guide_object_with_links(record, base_url, self.token))
        if url.path == "/v1/guide-collections":
            records = list(venue_collections().values())
            kind = query.get("venueKind", [None])[0]
            if kind:
                records = [record for record in records if kind in record.get("venueKinds", [])]
            selected, next_page = paged(sorted(records, key=lambda record: record["id"]), page, page_size)
            return self.reply(200, {"collections": [venue_collection_with_links(record, base_url, self.token) for record in selected],
                                    "total": len(records), "nextPage": next_page})
        if len(collection_parts) in (3, 5) and collection_parts[:2] == ["v1", "guide-collections"]:
            record = venue_collections().get(collection_parts[2])
            if record is None:
                return self.reply(404, {"error": "unknown guide collection"})
            if len(collection_parts) == 5:
                if collection_parts[3] != "phases":
                    return self.reply(404, {"error": "not found"})
                record = next((phase for phase in record.get("phases", []) if phase["id"] == collection_parts[4]), None)
                if record is None:
                    return self.reply(404, {"error": "unknown collection phase"})
            return self.reply(200, venue_collection_with_links(record, base_url, self.token))
        if url.path == "/v1/guides":
            return self.run(lambda: all_guides(page, page_size, base_url, self.token))
        guide_parts = url.path.strip("/").split("/")
        if len(guide_parts) == 3 and guide_parts[:2] == ["v1", "guides"]:
            if guide_parts[2] not in catalog()["guides"]:
                return self.reply(404, {"error": "unknown guide"})
            duration = query.get("duration", [None])[0]
            return self.run(lambda: guide_with_links(guide_parts[2], base_url, self.token,
                                                     float(duration) if duration else None))
        if len(guide_parts) == 4 and guide_parts[:2] == ["v1", "scripts"] and guide_parts[3] == "guide-sequence":
            sequence = script_guide_sequence(guide_parts[2], base_url, self.token)
            if sequence is None:
                return self.reply(404, {"error": "unknown script sequence"})
            return self.reply(200, sequence)
        if url.path == "/v1/venue-kinds":
            return self.run(lambda: {"venueKinds": catalog()["venueKinds"]})
        if url.path == "/v1/scripts":
            return self.run(lambda: scripts(query.get("venueKind", [None])[0] or None, page, page_size, base_url, self.token))
        if url.path == "/v1/steps":
            return self.run(lambda: steps(query.get("venueKind", [None])[0] or None, page, page_size, base_url, self.token))
        parts = url.path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["v1", "venues"] and parts[3] == "scripts":
            return self.run(lambda: venue_scripts(parts[2], page, page_size, base_url, self.token))
        if len(parts) == 4 and parts[:2] == ["v1", "steps"] and parts[3] == "guides":
            duration = query.get("duration", [None])[0]
            return self.run(lambda: step_guides(parts[2], query.get("venueID", [None])[0] or None,
                                                float(duration) if duration else None, base_url, self.token))
        if url.path == "/v1/music":
            query = parse_qs(url.query)
            base_url = f"http://{self.headers.get('Host')}"
            return self.run(lambda: music(
                query.get("query", [""])[0],
                int(query.get("page", ["0"])[0]),
                int(query.get("pageSize", ["20"])[0]),
                base_url,
                self.token,
            ))
        if url.path == "/v1/venues":
            page = int(parse_qs(url.query).get("page", ["1"])[0])
            return self.run(lambda: venues(page))
        parts = url.path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["v1", "venues"] and parts[3] == "menu":
            return self.run(lambda: menu(parts[2]))
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        if not self.authorized():
            return
        if urlparse(self.path).path != "/v1/scripts/write":
            return self.reply(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            request = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self.reply(400, {"error": "body is not JSON"})
        self.run(lambda: write(request, self.model, self.client_left))

    def send_catalog_file(self, url):
        query = parse_qs(url.query)
        if query.get("token", [""])[0] != self.token:
            return self.reply(401, {"error": "missing or wrong token"})
        relative = os.path.normpath(url.path[len("/v1/files/"):])
        path = os.path.join(CATALOG_DIR, relative)
        kind = relative.split(os.sep)[0]
        if relative.startswith("..") or kind not in ("previews", "overlays", "scenarios", "3d", "sequences") or not os.path.isfile(path):
            return self.reply(404, {"error": "not found"})
        duration = query.get("duration", [None])[0]
        if kind == "scenarios" and duration:
            scenario, _ = stretched(json.load(open(path, encoding="utf-8")), float(duration))
            body = json.dumps(scenario).encode()
        else:
            body = None
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(os.path.splitext(path)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(body) if body is not None else os.path.getsize(path)))
        self.end_headers()
        try:
            if body is not None:
                self.wfile.write(body)
            else:
                with open(path, "rb") as file:
                    shutil.copyfileobj(file, self.wfile, length=64 * 1024)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_music_file(self, url):
        if parse_qs(url.query).get("token", [""])[0] != self.token:
            return self.reply(401, {"error": "missing or wrong token"})
        name = os.path.basename(url.path)
        path = os.path.join(MUSIC_DIR, name)
        if not name.endswith(".mp3") or not os.path.isfile(path):
            return self.reply(404, {"error": "not found"})
        body = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        if self.headers.get("Authorization") == f"Bearer {self.token}":
            return True
        self.reply(401, {"error": "missing or wrong token"})
        return False

    def client_left(self):
        """The app closed the connection: it cancelled the request."""
        readable, _, _ = select.select([self.connection], [], [], 0)
        if not readable:
            return False
        try:
            return self.connection.recv(1, socket.MSG_PEEK) == b""
        except OSError:
            return True

    def run(self, work):
        started = time.time()
        try:
            self.reply(200, work())
            outcome = "ok"
        except Cancelled:
            outcome = "cancelled by the app"
        except Exception as error:
            outcome = f"failed: {error}"
            self.reply(502, {"error": str(error)})
        print(f"{self.command} {self.path} {time.time() - started:.1f}s {outcome}", flush=True)

    def reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def load_token():
    path = os.path.join(HERE, ".token")
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(secrets.token_urlsafe(24))
    return open(path).read().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--write", metavar="REQUEST_JSON", help="write one request from a file and print the result, without serving")
    args = parser.parse_args()
    if args.write:
        print(json.dumps(write(json.load(open(args.write)), args.model), ensure_ascii=False, indent=2))
        return
    Handler.token = load_token()
    Handler.model = args.model
    host = subprocess.run(["scutil", "--get", "LocalHostName"], capture_output=True, text=True).stdout.strip() or socket.gethostname()
    print(f"Serving on http://{host}.local:{args.port} with model {args.model}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()


if __name__ == "__main__":
    sys.exit(main())
