#!/usr/bin/env python3
"""Collects the script catalog, the step previews and both guide styles into one data bundle the development
server (Scriptwriter/server.py) serves: catalog.json plus the asset folders.

    python3 build_bundle.py [--out DIR] [--profile p0]     # default: Scriptwriter/catalog, full profile

catalog.json: venueKinds, categoryKinds (Loca category slugs per kind, in priority order), templates (every step
with imageURL and overlays as bundle-relative paths and the P0 step fields of scripts/script_templates.json),
guides (per overlay id: schematic, scenario, 3D spec, seconds, moves) and stepGroups (every step grouped by venue
kind; steps of scripts that fit several kinds form the general group).

--profile p0 also writes shot_types.json: the shot-type registry, the P0 guides with their animation, selector
and poster files from guides/p0/renders/<id>.png, <id>_selector.png, <id>_poster.png (missing renders are listed in
pendingRenders) and the step keyword table for written steps. The full profile removes it. It also leaves the
templates scripts/p0_scope.json hides out of catalog.json, with their steps and every record keyed by them.
"""
import argparse, hashlib, json, os, shutil, sys, datetime, math
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDES = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(GUIDES, ".."))
SERVER = os.path.abspath(os.path.join(ROOT, "..", "..", "..", "..", "..", "Scriptwriter"))
sys.path.insert(0, HERE)
import catalog as guide_catalog  # noqa: E402
sys.path.insert(0,os.path.join(ROOT,'api'))
import opacity_assets
import clay_scene_assets
sys.path.insert(0, os.path.join(ROOT, "scripts", "tools"))
import step_fields  # noqa: E402
import p0_preview_assets

# research/venue_kinds.md: Loca category slugs per kind, first match wins
CATEGORY_KINDS = [
    {"kind": "coffee", "slugs": ["coffee"]},
    {"kind": "bakery", "slugs": ["bakery"]},
    {"kind": "entertainment", "slugs": ["entertainment", "craft-beer", "events-music-n-film", "events-social"]},
    {"kind": "fast-food", "slugs": ["fast-food", "food-truck"]},
    {"kind": "dining", "slugs": ["dining", "food-and-drinks", "food-and-drinks-family"]},
    {"kind": "beauty-salon", "slugs": ["beauty-salon", "beauty", "beauty-barbershop", "beauty-nails", "beauty-products"]},
    {"kind": "sport_health", "slugs": ["sport_health", "services-health"]},
    {"kind": "shopping", "slugs": ["shopping", "clothing-shops", "shopping-music", "thrift-shops", "vintage-shop", "book-stores", "shopping-other", "knick-knacks"]},
    {"kind": "services", "slugs": ["services", "services-education", "business-services", "services-cleaning", "services-photography", "services-pet"]},
]
GHOST_SECONDS = {"frame": 1.2, "whip": 1.0, "reframe": 1.5}
# The live-guide overlays of renamed steps stay published under /v1/guides.
LEGACY_STEPS = {"first-visit.entrance": "cafe-first-visit.entrance", "first-visit.counter": "cafe-first-visit.counter",
                "first-visit.drink": "cafe-first-visit.pour", "first-visit.sip": "cafe-first-visit.taste",
                "first-visit.verdict": "cafe-first-visit.outro"}
P0_FILES = {"animation": "{}.png", "selector": "{}_selector.png", "poster": "{}_poster.png"}


def ghost_seconds(step):
    k = step["kind"]
    if k == "frame":
        return GHOST_SECONDS["frame"]
    if k == "follow":
        return GHOST_SECONDS["whip"] if step.get("action") == "whip" else step.get("duration", 2.0)
    if k == "reframe":
        return GHOST_SECONDS["reframe"]
    return step.get("duration", 1.0)


def camera_down_tilt(sample):
    """Match MotionSample: positive down, from the camera's world-space -Z forward."""
    x, y, _ = sample["rotation"]
    return round(math.degrees(math.asin(max(-1, min(1, math.cos(x) * math.cos(y))))))


def copy_tree(src, dst, suffixes, skip=()):
    os.makedirs(dst, exist_ok=True)
    n = 0
    for name in sorted(os.listdir(src)):
        if name.endswith(suffixes) and not name.endswith(skip):
            shutil.copy2(os.path.join(src, name), os.path.join(dst, name))
            n += 1
    return n


def versioned_file(source, out, kind, name, copy_alias=False):
    """Keep old file links working; give changed assets a new immutable URL."""
    with open(source, "rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    relative = f"{kind}/{digest[:16]}/{name}"
    target = os.path.join(out, relative)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    if not os.path.exists(target):
        shutil.copy2(source, target)
    # The compatibility alias is a link to the bundle copy, never to source art.
    alias = os.path.join(out, kind, name)
    temporary = alias + ".tmp"
    if os.path.exists(temporary):
        os.unlink(temporary)
    if copy_alias:
        shutil.copy2(target, temporary)
    else:
        os.link(target, temporary)
    os.replace(temporary, alias)
    return relative, digest


def context_assets(row, out):
    folder = os.path.join(ROOT, row["folder"])
    checks = json.load(open(os.path.join(folder, "assembly-checks.json")))
    assert checks["sha256"] == row["sha256"] and not checks["alpha_applied_again"]
    assert checks["max_alpha"] <= 128
    for stage in checks["stages"]:
        origin = stage["source"]
        source = os.path.join(ROOT, origin["source"], "guide.png")
        assert hashlib.sha256(open(source, "rb").read()).hexdigest() == origin["source_sha256"]
    gid = row["guide_id"]
    opacity=opacity_assets.assets(os.path.join(folder,'guide.png'))
    assert opacity['source_sha256']==row['sha256'] and opacity['max_alpha']==opacity_assets.MAX_ALPHA
    overlay, digest = versioned_file(os.path.join(ROOT,opacity['overlay']), out, "overlays", gid + ".png")
    poster, _ = versioned_file(os.path.join(ROOT,opacity['poster']), out, "overlays", gid + "_poster.png")
    strip, _ = versioned_file(os.path.join(ROOT,opacity['strip']), out, "overlays", gid + "_strip.jpg")
    result = {"overlay": overlay, "poster": poster, "strip": strip, "sha256": digest,
            "animationSeconds": row["duration"], "scope": row["scope"],"alphaFactor":opacity_assets.TARGET,"sourceSha256":row['sha256'],
            "handoverStatus": row["handover_status"], "contextTemplateID": row["template_id"],
            "contextStepID": row["step_id"], "nextGuideID": row.get("next_guide"),
            "rendering": "native-3d-shot-and-handover" if row["scope"] == "shot_and_handover" else
                         "native-3d-final-shot" if row["scope"] == "complete_final_shot" else
                         "native-3d-base-shot; people-handover-deferred" if row["handover_status"] == "deferred_people" else
                         "native-3d-base-shot; cut-at-step-boundary"}
    if row.get('transition_method'):result['transitionMethod']=row['transition_method']
    return result


def shot_types(out):
    renders = os.path.join(GUIDES, "p0", "renders")
    guides, pending = {}, []
    for guide in step_fields.REGISTRY["guides"]:
        if guide.get('availability') in ('deferred','archived'):continue
        gid = guide["id"]
        record = {key: guide[key] for key in ("id", "shotType", "title", "invariant", "durationSec", "startTrigger",
                                              "capturePreset", "setupBeatSeconds", "alphaFactor", "camera")}
        if guide.get('allowedPeople'):
            record.update({key:guide[key] for key in ['camera','filmingMode','previewMirrored','facialAnimation']})
        names = {field: pattern.format(gid) for field, pattern in P0_FILES.items()}
        check_path = os.path.join(renders, gid + '_checks.json')
        checked = json.load(open(check_path)) if os.path.isfile(check_path) else {}
        complete = all(os.path.isfile(os.path.join(renders, name)) for name in names.values())
        object_only=checked.get('maximum_hands',99)<=guide.get('allowedHands',0) and checked.get('silhouettes',99)<=guide.get('allowedSilhouettes',0) and checked.get('detailed_people',99)<=guide.get('allowedPeople',0)
        if complete and object_only and checked.get('status') == 'passed' and checked.get('sha256') == hashlib.sha256(open(os.path.join(renders, names['animation']), 'rb').read()).hexdigest():
            for field, name in names.items():
                record[field], digest = versioned_file(os.path.join(renders, name), out, "overlays/p0", name)
                if field == "animation":
                    record["sha256"] = digest
        else:
            record.update({field: "overlays/p0/" + name for field, name in names.items()}, sha256=None)
            pending.append(gid)
        record['content']='canonical-character' if guide.get('allowedPeople') else 'cropped-grip' if guide.get('allowedHands') else 'object-with-background-silhouette' if guide.get('allowedSilhouettes') else 'object-only'
        guides[gid] = record
    types=[]
    for kind in step_fields.REGISTRY['shotTypes']:
        active=[gid for gid in kind['guides'] if gid in guides]
        types.append({**kind,'guides':active,'availability':'active' if active else 'deferred',
                      'deferredGuideIDs':[gid for gid in kind['guides'] if gid not in guides]})
        if active:
            types[-1].update(startTrigger=guides[active[0]]['startTrigger'],capturePreset=guides[active[0]]['capturePreset'])
    return {"version": 1, "shotTypes": types, "guides": guides, "pendingRenders": pending,
            "deferredGuides":step_fields.REGISTRY.get('deferredGuides',{}),
            "stepKeywords": step_fields.TABLE}


def apply_p0_scope(bundle):
    """Removes the hidden templates, their steps and the step- or script-keyed records of them; returns their ids."""
    with open(os.path.join(ROOT, "scripts", "p0_scope.json")) as file:
        hidden = {tid for ids in json.load(file)["hiddenUntil"].values() for tid in ids}
    unknown = hidden - {t["id"] for t in bundle["templates"]}
    assert not unknown, f"p0_scope.json names unknown templates: {sorted(unknown)}"
    bundle["templates"] = [t for t in bundle["templates"] if t["id"] not in hidden]
    for group in bundle["stepGroups"]:
        group["steps"] = [s for s in group["steps"] if s["templateID"] not in hidden]
    bundle["stepGroups"] = [g for g in bundle["stepGroups"] if g["steps"]]
    for key in ("stepGuideOverrides", "scriptGuideSequenceStatus", "scriptGuideSequences"):
        bundle[key] = {k: v for k, v in bundle[key].items() if k.split(".")[0] not in hidden}
    return sorted(hidden)


def write_v3(out):
    """catalog_v3.json beside catalog.json: the four kind scripts, choice sets and tables, unchanged."""
    source = os.path.join(ROOT, "scripts", "catalog_v3.json")
    with open(source) as f:
        catalog = json.load(f)
    if catalog.get("version") != 3:
        raise RuntimeError("scripts/catalog_v3.json is not catalog version 3")
    with open(os.path.join(out, "catalog_v3.json.tmp"), "w") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    os.replace(os.path.join(out, "catalog_v3.json.tmp"), os.path.join(out, "catalog_v3.json"))
    print(f"catalog_v3.json: {len(catalog['kinds'])} kinds, {len(catalog['choiceSets'])} choice sets")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(SERVER, "catalog"))
    ap.add_argument("--overlays", choices=("reviewed", "schematic"), default="reviewed",
                    help="Prefer reviewed Blender shots, then watercolor APNGs; or only original schematics")
    ap.add_argument("--profile", choices=("full", "p0"), default="full")
    ap.add_argument("--catalog-version", type=int, choices=(2, 3), default=2,
                    help="3: also write catalog_v3.json (scripts/catalog_v3.json, built by check_scripts.py --v3 --merge)")
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    if a.catalog_version == 3:
        write_v3(out)

    templates = json.load(open(os.path.join(ROOT, "scripts", "script_templates.json")))
    legacy = {t["id"] + "." + s["id"]: s["overlays"]
              for t in json.load(open(os.path.join(GUIDES, "script_templates.json")))["templates"] for s in t["steps"]}
    for t in templates["templates"]:
        for s in t["steps"]:
            key = t["id"] + "." + s["id"]
            s["overlays"] = legacy.get(LEGACY_STEPS.get(key, key), [])
    kinds = templates["venueKinds"]
    kind_title = {k["id"]: k["title"] for k in kinds}
    preview_root = os.path.join(ROOT, "previews")
    preview_info = None
    active_previews = os.path.join(preview_root, "active-art-revision.json")
    if os.path.exists(active_previews):
        preview_info = json.load(open(active_previews))
        assert preview_info["approved"]
        preview_root = os.path.abspath(os.path.join(ROOT, preview_info["assetDirectory"]))
        assert os.path.commonpath([ROOT, preview_root]) == ROOT
        preview_manifest = json.load(open(os.path.join(ROOT, preview_info["manifest"])))
        assert all(e["status"] == "approved" for e in preview_manifest["entries"])
    preview_hashes = {}
    for t in templates["templates"]:
        for s in t["steps"]:
            name = s["imageURL"]
            assert os.path.basename(name) == name
            relative, digest = versioned_file(os.path.join(preview_root, name), out,
                                               "previews", name, copy_alias=True)
            s["imageURL"] = relative
            preview_hashes[name] = digest
    if preview_info:
        revision = hashlib.sha256(json.dumps(preview_hashes, sort_keys=True).encode()).hexdigest()
        assert revision == preview_info["revisionSHA256"], "Active preview revision changed without review"

    reviewed = set()
    motion = {}
    blender = {}
    context_index = os.path.join(ROOT, "catalog", "context-animations", "index.json")
    contexts = json.load(open(context_index)) if os.path.exists(context_index) and a.overlays == "reviewed" else {}
    if a.overlays == "reviewed":
        with open(os.path.join(ROOT, "catalog", "animations", "index.json")) as file:
            reviewed = set(json.load(file)["guides"])
        with open(os.path.join(GUIDES, "watercolor_motion", "manifest.json")) as file:
            motion = {g["id"]: g for g in json.load(file)["guides"]}
        index = os.path.join(ROOT, "catalog", "blender-animations", "index.json")
        if os.path.exists(index):
            for row in json.load(open(index))["shots"]:
                if row["exported"] and row["reviewed"]:
                    folder = os.path.join(ROOT, "catalog", "blender-animations", row["id"])
                    spec = json.load(open(os.path.join(folder, "scene-spec.json")))
                    checks = json.load(open(os.path.join(folder, "export-checks.json")))
                    review = json.load(open(os.path.join(folder, "review.json")))
                    digest = hashlib.sha256(open(os.path.join(folder, "guide.png"), "rb").read()).hexdigest()
                    assert checks["build_fingerprint"] == spec["build_fingerprint"], row["id"]
                    assert review["guide_sha256"] == digest, row["id"]
                    assert checks["rgb_preserved_in_final_alpha_pass"], row["id"]
                    assert checks["main_fill_alpha"] == .25, row["id"]
                    blender[row["id"]] = (folder, spec, checks)
        pilot = os.path.join(ROOT, "catalog", "blender-study", "bar_low_truckr_mm")
        if 'bar_low_truckr_mm' not in blender and os.path.exists(os.path.join(pilot, "publication-review.json")):
            review = json.load(open(os.path.join(pilot, "publication-review.json")))
            checks = json.load(open(os.path.join(pilot, "export-checks.json")))
            digest = hashlib.sha256(open(os.path.join(pilot, "guide.png"), "rb").read()).hexdigest()
            assert review["guide_sha256"] == digest
            assert checks["next_shot_cut_visible"] and checks["final_fill_alpha_max"] == .25
            checks["alpha_multiplier_applied_once"] = checks["final_alpha_multiplier"]
            blender["bar_low_truckr_mm"] = (pilot, {"scope": "shot_and_handover"}, checks)
    guides = {}
    for gid in sorted({o for t in templates["templates"] for s in t["steps"] for o in s["overlays"]}):
        scenario = json.load(open(os.path.join(GUIDES, "scenarios", gid + ".json")))
        spec3d = json.load(open(os.path.join(GUIDES, "overlays", "3d", gid + ".json")))
        follows = [s for s in scenario["steps"] if s["kind"] == "follow"]
        native = gid in blender
        watercolor = gid in reviewed and not native
        if native:
            folder, native_spec, checks = blender[gid]
            source = os.path.join(folder, "guide.png")
            poster = os.path.join(folder, "poster.png")
            strip = os.path.join(folder, "strip.jpg")
            animation = {"duration": checks["duration_ms"] / 1000,
                         "alpha_factor": checks["alpha_multiplier_applied_once"]}
        elif watercolor:
            assert motion[gid]["status"] in ("approved", "keyframes_reviewed"), gid
            folder = os.path.join(ROOT, "catalog", "animations", gid)
            source = os.path.join(folder, "guide.png")
            poster = os.path.join(folder, "poster.png")
            strip = os.path.join(folder, "strip.png")
            with open(os.path.join(folder, "guide.json")) as file:
                animation = json.load(file)
        else:
            source = os.path.join(GUIDES, "overlays", "schematic", gid + ".png")
            poster = os.path.join(ROOT, "catalog", "animations", "original-posters", gid + ".png")
            strip = os.path.join(GUIDES, "overlays", "schematic", gid + "_strip.png")
            animation = {}
        opacity=opacity_assets.assets(source)
        source=os.path.join(ROOT,opacity['overlay']);poster=os.path.join(ROOT,opacity['poster']);strip=os.path.join(ROOT,opacity['strip'])
        animation.update(duration=opacity['duration_ms']/1000,alpha_factor=opacity_assets.TARGET)
        overlay, digest = versioned_file(source, out, "overlays", gid + ".png")
        poster_path, _ = versioned_file(poster, out, "overlays", gid + "_poster.png")
        strip_path, _ = versioned_file(strip, out, "overlays", gid + "_strip" + os.path.splitext(strip)[1])
        scenario_source = os.path.join(GUIDES, "scenarios", gid + ".json")
        adapted_scenario = False
        if native and native_spec.get("camera_samples"):
            samples = native_spec["camera_samples"]
            first_name = samples[0]["camera"]
            primary = [sample for sample in samples if sample["camera"] == first_name]
            first_tilt = camera_down_tilt(primary[0])
            last_tilt = camera_down_tilt(primary[-1])
            scenario["steps"][0]["tilt"] = {"target": first_tilt, "tolerance": 12}
            has_tilt = any(step.get("action") == "tilt" for step in scenario["steps"])
            for step in scenario["steps"][1:]:
                if "tilt" in step: step["tilt"] = {"target": last_tilt if has_tilt and step.get("kind") == "hold" else first_tilt, "tolerance": 12}
            adapted_scenario = True
        if native and gid == "glass_favorite_eye_in_cd":
            scenario["camera"] = "front"
            adapted_scenario = True
        if native and gid == "glass_pour_eye_in_cd_through":
            for step in scenario["steps"]:
                if step.get("action") == "dolly_in": step["amount"] = 1.18
            adapted_scenario = True
        if native and gid == "cup_pour_eye_hold":
            scenario["anchor"] = {"kind": "salient", "type": "pasta"}
            adapted_scenario = True
        if native and gid == "menu_board_low_tiltd_mm":
            # Keep canonical source art intact; reconcile this reviewed camera with live sensor targets.
            scenario["steps"][0]["tilt"] = {"target": -25, "tolerance": 12}
            scenario["steps"][-1]["tilt"] = {"target": 23, "tolerance": 12}
            adapted_scenario = True
        if native and gid == 'hands_during_top_hold':
            scenario['title']='Close-up massage stroke'
            scenario['anchor']={'kind':'none','type':'massage_detail'}
            for step in scenario['steps']:
                if step.get('kind')=='still':
                    step['duration']=4.4
                    step['subject_motion']='One practitioner hand performs a slow palm stroke over a cropped curved back area'
            adapted_scenario=True
        if native and gid in ['over_shoulder_counter_os_hold','room_lights_eye_hold']:
            scenario['title']='Order: coffee brewing' if gid=='over_shoulder_counter_os_hold' else 'Cafe lights on'
            for step in scenario['steps']:
                if step.get('kind')=='still':
                    step['duration']=3.0 if gid=='over_shoulder_counter_os_hold' else 2.8
                    step['subject_motion']='Espresso flows from the outlet into the supported cup' if gid=='over_shoulder_counter_os_hold' else 'The pendant lamps switch on once; the room stays still'
            adapted_scenario=True
        if native and gid=='cup_eye_hold_whipout':
            first=scenario['steps'][0]
            last_tilt=camera_down_tilt(native_spec['camera_samples'][round(native_spec['take_end']*15)-1])
            scenario['title']='Cup and neighbouring croissant'
            scenario['steps']=[first,
                {'kind':'still','duration':.8,'subject_motion':'Steam rises from the supported cup','tilt':{'target':first_tilt,'tolerance':12},'level':4},
                {'kind':'follow','action':'tilt','direction':'down','amount':round(abs(last_tilt-first_tilt)/90,3),'duration':2.2,'channel':'gravity_tilt','level':4,'icon':{'symbol':'tilt','mods':[]}},
                {'kind':'hold','duration':.8,'tilt':{'target':last_tilt,'tolerance':12},'level':4}]
            adapted_scenario=True
        if adapted_scenario:
            adapted = os.path.join(ROOT, "api", "scenario-adaptations")
            os.makedirs(adapted, exist_ok=True)
            scenario_source = os.path.join(adapted, gid + ".json")
            with open(scenario_source, "w") as file:
                json.dump(scenario, file, indent=1)
        scenario_path, _ = versioned_file(scenario_source, out, "scenarios", gid + ".json")
        guides[gid] = {
            "overlay": overlay,
            "scenario": scenario_path,
            "poster": poster_path,
            "strip": strip_path,
            "style": "blender" if native else "watercolor" if watercolor else "schematic",
            "sha256": digest,
            "sourceSha256": opacity['source_sha256'],
            "animationSeconds": animation.get("duration"),
            "alphaFactor": animation.get("alpha_factor"),
            "rendering": ("native-3d-shot-and-handover" if native_spec.get("scope") == "shot_and_handover" else "native-3d-final-shot" if native_spec.get("scope") == "complete_final_shot" else "native-3d-base-shot; contextual-handover-pending") if native else motion.get(gid, {}).get("rendering", {}).get("method") if watercolor else None,
            "scope": ("shot_and_handover" if native_spec.get("scope") == "shot_and_handover" else "complete_final_shot" if native_spec.get("scope") == "complete_final_shot" else "base_shot") if native else "existing_guide",
            "handoverStatus": ("included" if native_spec.get("scope") == "shot_and_handover" else "not_applicable" if native_spec.get("scope") == "complete_final_shot" else "pending_contextual_sequence") if native else "existing",
            "model3D": f"3d/{gid}.json",
            "seconds": round(sum(ghost_seconds(s) for s in scenario["steps"]), 2),
            "camera": scenario["camera"],
            "moves": [s["action"] + ("" if "direction" not in s else " " + s["direction"]) for s in follows],
            "subject": spec3d["model"],
        }
        if native and gid in contexts.get("guides", {}):
            guides[gid].update(context_assets(contexts["guides"][gid], out))

    step_overrides = {}
    for key, row in contexts.get("steps", {}).items():
        if row.get("folder") and row["guide_id"] in blender:
            step_overrides[key] = {row["guide_id"]: context_assets(row, out)}
    sequence_status = {
        key: {"status": "deferred_people", "title": row["title"],
              "deferredSteps": row["deferred_steps"], "objectSteps": row["object_steps"]}
        for key, row in contexts.get("scripts", {}).items() if row.get("status") == "deferred_people"
    }
    script_sequences = {}
    for key, row in contexts.get("scripts", {}).items():
        if not row.get("folder"): continue
        folder = os.path.join(ROOT, row["folder"])
        checks = json.load(open(os.path.join(folder, "assembly-checks.json")))
        assert checks["sha256"] == row["sha256"] and not checks["alpha_applied_again"]
        opacity=opacity_assets.assets(os.path.join(folder,'guide.png'),video=True)
        record = {"id": key, "title": row["title"], "seconds": row["duration"],
                  "sha256": opacity['sha256'], "sourceSha256":row['sha256'],"alphaFactor":opacity_assets.TARGET,"steps": row["steps"]}
        for field, filename in (("overlay", "guide.png"), ("video", "preview.mp4"),
                                ("poster", "poster.png"), ("strip", "strip.jpg")):
            extension = os.path.splitext(filename)[1]
            record[field], _ = versioned_file(os.path.join(ROOT,opacity[field]), out, "sequences",
                                              key + "_" + field + extension)
        script_sequences[key] = record
    # Context variants share immutable paths; flat compatibility links retain canonical guide art.
    for guide in guides.values():
        for key in ("overlay", "poster", "strip", "scenario"):
            target = os.path.join(out, guide[key])
            alias = os.path.join(out, guide[key].split("/")[0], os.path.basename(target))
            temporary = alias + ".tmp"
            if os.path.exists(temporary): os.unlink(temporary)
            os.link(target, temporary)
            os.replace(temporary, alias)

    # Keep app instructions consistent with the owner's revised physical demonstrations.
    directions={
        'room_lights_eye_hold':'Ask staff before filming the opening routine. From the public doorway, hold a wide view of the tables and pendant lamps while the lights switch on, then hold the lit room. Keep the camera still; do not stage chair movement.',
        'latte_top_in_cd_whipout':'Film from a reachable overhead angle as milk pours from the pitcher into the supported cup. Keep the milk landing point inside the rim, hold briefly on the finished art, then whip right for the entrance cut.',
        'over_shoulder_counter_os_hold':'Stay on the customer side and hold a medium view with the order board above the cup. Keep the phone steady as the visible machine outlet fills the supported cup; no staff-side access is needed.',
        'cup_eye_hold_whipout':'Start close to the steaming cup with the plated croissant beside it. Rise and lean diagonally to reveal the pairing on the same table; keep both supported.',
        'hands_during_top_hold':'Prop the phone above a tight massage detail or ask a companion to hold it still. Frame one practitioner hand and a small back area; show a slow palm stroke and release, with body edges outside the picture.',
        'card_menu_high_in_cd_whipout':'Ask a companion to film while you hold the menu at about 50 degrees and point to the lunch offer. They move the phone in a slow diagonal rising arc to reveal the dishes on the same table.',
        'card_label_high_hold_whipout':'Show the maker label on the folded garment. Move the phone through a short rising curve, then continue toward its attached price tag.',
        'card_tag_high_hold':'Keep the attached price tag readable on the upright folded garment. Lean in along a small curved high-angle path.',
        'card_tag_top_in_cd_through':'Start above the attached price tag and move closer on a gentle curve, changing the viewing angle while keeping the price readable.',
        'hands_garment_high_hold':'Lay the garment right way up, with the collar and folded sleeves visible. Move from the maker detail toward the attached price tag.',
        'hands_guitar_high_hold':'Keep the instrument supported and film a slow curved detail move along the strings toward the body. Change the phone height and pitch together.',
        'hand_pov_pastry_pov_in_mc':'Place the opened pastry on a plate and show its filling. Move the phone through a gentle rising arc toward the cut faces.',
        'pastry_tear_open':'Show the already opened pastry and its filling on a plate. Use a short rising arc to reveal the cut faces.',
        'pastry_break_eye_hold':'Show the already opened pastry and its filling on a plate. Move smoothly from its crust toward the cut faces.',
        'case_eye_in_mc_through':'Film the selected pastry through the case from the customer side, then move along the public counter toward the plated pastry.',
        'cup_high_out_dm':'Keep the filled cup on its saucer. Move the phone back and slightly upward on a curve to reveal the counter around it.',
        'cup_pour_eye_hold':'Keep the cup and neighbouring plate in view as water pours from the kettle into the cup. Then move the phone diagonally upward to reveal the same table.',
        'glass_drink_high_hold':'Film the ordered glass at the customer edge of the bar, then move the phone back and change its pitch toward the event board in the same space.',
        'glass_eye_tiltd_cc':'Leave the served glass on the counter. Change phone height and pitch smoothly from its rim toward its base, staying on the customer side.',
        'glass_flight_high_truckr_cc':'Stay on the customer side and move diagonally along the tasting flight. Raise and turn the phone toward the tap board, then settle on the handles.',
        'glass_pour_eye_in_cd_through':'Film the pour near the customer edge of the bar, then move back and tilt toward the happy-hour board. Keep the phone outside the staff work area.',
        'glass_pour_low_in_cd':'Hold the phone low on the customer side while the glass fills, then rise on a short curved path to show its rim and the same counter.',
        'door_eye_in_wd_through':'Let the door open, then walk through the same doorway and along the public aisle. Change phone position and pitch smoothly toward the room feature.',
        'door_pov_in_wc_through':'Let the door open, then walk through the same doorway into the public waiting area, keeping the camera movement smooth.',
        'door_pov_in_wd_through':'Let the door open, then walk through the same doorway and along the public aisle toward the room feature or reception.',
        'facade_eye_hold':'Start on the sign and frontage, then approach the entrance on a short curved diagonal path, changing phone height and pitch together.',
        'facade_truck_eye_in_wm':'Stay outside the food truck and approach its open serving window on a gentle curve. Reveal the serving ledge and food rack through the window.',
    }
    revision=json.load(open(os.path.join(ROOT,'guides/blender_motion/cinematic-revision-status.json')))
    for template in templates['templates']:
        for step in template['steps']:
            if template['id'] in step_fields.P0_SCRIPTS or not step['overlays']:continue
            gid=step['overlays'][0]
            if gid in directions:step['direction']=directions[gid]
            if gid=='hands_during_top_hold':step['position']='Phone fixed above a tightly cropped massage area'
            row=contexts.get('steps',{}).get(template['id']+'.'+step['id'],{})
            if row.get('source') and (gid in revision['native_guides'] or gid in ['latte_top_in_cd_whipout','over_shoulder_counter_os_hold','cup_eye_hold_whipout','room_lights_eye_hold'] or row['source'].get('source_guide_id',gid)!=gid):
                step['seconds']=round(row['source']['frames']/15,2)
            if template['id']=='cafe-morning-ritual' and step['id']=='pastry':
                step['direction']='Continue from the paired cup-and-croissant view. Lean toward the already opened pastry to show its layers and filling; keep the cup beside it and the pastry resting on the plate.'

    groups = {}
    for t in templates["templates"]:
        key = t["venueKinds"][0] if len(t["venueKinds"]) == 1 else None
        g = groups.setdefault(key, {"venueKind": key, "title": kind_title.get(key, "General"), "steps": []})
        for s in t["steps"]:
            g["steps"].append({"templateID": t["id"], "templateTitle": t["title"], **s})
    order = [k["id"] for k in kinds] + [None]
    step_groups = [groups[k] for k in order if k in groups]

    bundle = {
        # The catalog version from scripts/script_templates.json (2: key, card, opinion, noPrice per step).
        "version": templates.get("version", 1),
        "generatedAt": datetime.datetime.now(ZoneInfo("Europe/Kyiv")).date().isoformat(),
        "venueKinds": kinds,
        "opinionSets": templates.get("opinionSets", []),
        "categoryKinds": CATEGORY_KINDS,
        "templates": templates["templates"],
        "guides": guides,
        "stepGroups": step_groups,
        "stepGuideOverrides": step_overrides,
        "scriptGuideSequenceStatus": sequence_status,
        "scriptGuideSequences": script_sequences,
    }
    if preview_info:
        bundle["previewArt"] = preview_info
    if a.overlays == 'reviewed':
        clay_scene_assets.apply(bundle, out)
    if a.profile == 'p0':
        p0_preview_assets.apply(bundle, out, versioned_file)
        deferred=step_fields.REGISTRY.get('deferredGuides',{})
        archived={g['id'] for g in step_fields.REGISTRY['guides'] if g.get('availability')=='archived'}
        for step in [s for t in bundle['templates'] for s in t['steps']] + [s for g in step_groups for s in g['steps']]:
            removed=[gid for gid in step['guides'] if gid in deferred]
            # A guided v0 step keeps its own guides: they share its level and carry its choices (no P0 upside-down).
            if 'complexity' not in step:step['guides']=step_fields.inherited_guides(step_fields.SHOT_TYPES.get(step.get('shotType')),deferred)
            else:step['guides']=[gid for gid in step['guides'] if gid not in deferred and gid not in archived]
            if removed:step['deferredGuides']=removed
    for step in [s for t in bundle["templates"] for s in t["steps"]] + [s for g in step_groups for s in g["steps"]]:
        if step["guides"]:
            step["seconds"] = step_fields.step_seconds(step)
    hidden = []
    if a.profile == "p0":
        hidden = apply_p0_scope(bundle)
        templates["templates"], step_groups = bundle["templates"], bundle["stepGroups"]
    counts = {
        "previews": len(preview_hashes),
        "overlays": len(guides),
        "watercolor": sum(g["style"] == "watercolor" for g in guides.values()),
        "blender": sum(g["style"] == "blender" for g in guides.values()),
        "schematic": sum(g["style"] == "schematic" for g in guides.values()),
        "scenarios": len(guides),
        "3d": copy_tree(os.path.join(GUIDES, "overlays", "3d"), os.path.join(out, "3d"), (".json", "_strip.png")),
        "3d/models": copy_tree(os.path.join(GUIDES, "overlays", "3d", "models"), os.path.join(out, "3d", "models"), (".usdz", ".json")),
    }
    steps = sum(len(t["steps"]) for t in templates["templates"])
    missing = [s["imageURL"] for t in templates["templates"] for s in t["steps"] if not os.path.exists(os.path.join(out, s["imageURL"]))]
    if missing:
        raise RuntimeError(f"Missing previews: {missing}")
    registry_path = os.path.join(out, "shot_types.json")
    if a.profile == "p0":
        registry = shot_types(out)
        p0_preview_assets.guide_examples(registry, out, versioned_file)
        with open(registry_path + ".tmp", "w") as file:
            json.dump(registry, file, ensure_ascii=False, indent=1)
        os.replace(registry_path + ".tmp", registry_path)
        print(f"shot_types.json: {len(registry['shotTypes'])} shot types, {len(registry['guides'])} guides, "
              f"{len(registry['pendingRenders'])} pending renders")
    elif os.path.exists(registry_path):
        os.unlink(registry_path)
    # Publish the index after every referenced file exists.
    with open(os.path.join(out, "catalog.json.tmp"), "w") as file:
        json.dump(bundle, file, ensure_ascii=False, indent=1)
    os.replace(os.path.join(out, "catalog.json.tmp"), os.path.join(out, "catalog.json"))
    print(f"catalog.json: {len(kinds)} kinds, {len(templates['templates'])} scripts, {steps} steps, {len(guides)} guides, "
          f"{len(step_groups)} step groups ({', '.join(g['title'] for g in step_groups)}); files {counts}; missing previews {len(missing)}; hidden scripts {hidden}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
