# Current collection

[37 active guides](http://127.0.0.1:8766/p0/index.html) ([public snapshot: 29 guides](https://loca-camera-guides.forgivingmacaw.chatgpt.site)). [Canonical creator guides](people-guides-report.md). [Latest scene and grip corrections](owner-corrections-report.md); [table sequences](table-composition-report.md); [previous entrance/menu/pour updates](followup-report.md). Three reference-based table shots are shared by Food review / Dish and Restaurant / First visit / Plate. Five person/selfie guides are restored with the canonical creator rig; three additional friend-filmed options use the rear camera. Facial speech and chewing remain unsupported.

## Result directories

- `catalog/p0/animations-light/<id>/`: active Blender scene, source frames, processed frames, selector frames, camera metadata, pre-render review and checks. Playback copies are `guide.png`, `guide_selector.png`, `guide_poster.png`.
- `guides/p0/renders/`: the 111 active API-ready files and their check sidecars.
- `catalog/p0/deferred/<id>/` and `guides/p0/deferred/<id>/`: the five earlier person/selfie studies, preserved as archives. Active replacements keep their original IDs under `animations-light/` and `renders/`.
- `previews/clay-3d/p0/`: separate step pictures, originals, prompts and manifest from the previous illustration pass. This revision changes animations only.
- `api/p0-bundle/`: checked staging bundle; the matching local API bundle is `/Users/ihor.buts/Documents/Development/Scriptwriter/catalog`.
- `revision-probes/`: static composition-check frames, not additional published animations. `animations/` and `archive/` contain earlier studies.

## Style and playback

Transparent white contours, dark underlay, restrained yellow light-facing edges and local steam glow. No shaded surfaces, broad walls/floor or baked viewfinder. Canonical creator guides use the original skinned body and hands, with a fade below the chest. Five front-camera previews are mirrored; three friend-filmed rear-camera previews are not mirrored. The original 29 object guides are unchanged. Separate player controls provide viewfinder/level, light/dark backgrounds and 65% before-capture / 30% during-capture image-view opacity. Raw alphaFactor remains 1.

405 x 720 RGBA APNG at 15 fps; 120 x 213 looping selectors. Main animations play once: eight target frames, optional fifteen-frame setup, `durationSec * 15` demonstration frames, seven final target frames. Opening and closing targets match; the poster equals frame zero. All active guides demonstrate actual camera or physical subject movement. The target hero stays within the protected middle band; supporting rim/cup/fork markers may extend beyond that band while staying on screen.

## API

Use `GET /v1/scripts?venueKind=coffee` or `venueKind=dining`, then **First visit** (`first-visit`). Coffee resolves to five steps; dining resolves to six. `food-review` is also mapped. First bite, sip and verdict now include character guides.

`GET /v1/shot-types` lists twelve registered types. `GET /v1/shot-types/{id}/guides` gives the current animation, selector and poster links. Sip and verdict each return three choices. First bite includes its two character choices and the existing dish/fork close-up. Character records expose `camera`, `filmingMode`, `previewMirrored` and `facialAnimation`; use the selected guide camera rather than the shot-type default when filming with a friend. `GET /v1/steps/first-visit.drink/guides` returns the three corrected pours. `GET /v1/steps/food-review.dish/guides` and `GET /v1/steps/first-visit.plate/guides` both include the same table spread, cocktail slide and pancake reveal assets. Requests use the existing Bearer token; follow signed file URLs from the response. Content hashes update the URL when an existing guide is re-rendered. The legacy 178-guide endpoint is separate.

## Updating the same guide

Use `render_p0.py --id <existing-id> --out catalog/p0/animations-light/<existing-id> --replace`, then the existing P0 export and bundle tools. `--replace` updates the same scene/frame directory; it does not add an animation variant. The former deferred IDs have been explicitly restored in the registry. Rebuild the small creator cache with `prepare_p0_creator.py` only when its source or simplification changes.

```sh
/private/tmp/loca-p0-people-venv/bin/python .ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/ScriptsAndGuides/guides/tools/build_guides.py check --profile p0
/Applications/Blender.app/Contents/MacOS/Blender -b --python-exit-code 1 -P .ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/ScriptsAndGuides/guides/blender_motion/verify_p0_scene.py
```

See the character report for export, saved-scene, actual skinning/grip, browser and API check results. Earlier table-scene evidence remains in the linked table report. Physical phone capture and mobile UI were not exercised; installed Blender is 5.2.3 LTS.

## Public hosting

The standalone public gallery still contains the earlier 29 P0 guides. The owner chose local/API-only delivery for the eight character guides. Public packaging excludes these eight by default. Do not expand the public scope without a new explicit owner instruction. [Publication record](publication.json) and [update instructions](public-hosting.md).
