# Animation API

The current server repository is `/Users/ihor.buts/Documents/Development/Scriptwriter`.
New scene collections and proofs have additive [guide-collection endpoints](guide-collections.md).
The revised coffee scene is available as a collection; its espresso clip also replaces the existing Cafe → Before opening → First shot guide binding.

The current step-picture collection is the reviewed plasticine edition: 304 step JPEGs from 276 unique illustrations. All 304 returned image URLs were downloaded and checked against the exports; see `../previews/clay-3d/publication/live-api-check.json`. Pictures are available through `GET /v1/scripts` and its existing `imageURL` fields, with content revisions in the paths.

The step-picture cache now includes the image URL path. Rebuild the app once to include this correction; existing cached pictures otherwise remain keyed only by script and step identity. `step-preview-swift-cache-check.json` records both passing cache regression tests. The active artwork source is selected by `../previews/active-art-revision.json`; future bundle builds use that reviewed collection. Earlier source artwork remains preserved.

The development API is running at `http://Ihors-MacBook-Pro.local:8765`.
All JSON requests use the existing `Authorization: Bearer <token>` header.
Returned file URLs include their existing token query parameter; follow those URLs directly.

| Request | Result |
|---|---|
| `GET /v1/guides?page=0&pageSize=20` | All unique guides, paginated; `guides`, `total`, `nextPage` |
| `GET /v1/guides/bar_low_truckr_mm` | One guide with animation and supporting file URLs |
| `GET /v1/steps/{templateID.stepID}/guides?duration=20` | Existing per-step API; still supported |
| `GET /v1/guides/{id}?duration=20` | Same animation, with live scenario holds stretched to the requested duration |

There are 178 guides: 139 Blender object/hand animations, 19 watercolor animations and 20 original schematics. The 39 people-dependent guides retain their previous artwork while people generation is deferred. The originals remain
available where matching watercolor artwork/action layers are incomplete. The API returns the raw
transparent APNG as `overlayURL`, plus `scenarioURL`, `model3DURL`, `posterURL`, `stripURL`, stable `id`,
`style`, `sha256`, `seconds`, `camera`, `moves` and `subject`.

All guide records include `alphaFactor: 0.65`, `animationSeconds` and the rendering method. Alpha is
already applied to the image; do not apply another opacity multiplier. The raw animation has no baked viewfinder UI.
`seconds` is the live scenario duration; `animationSeconds` is the demonstration APNG duration. Stretching
the live scenario does not retime the demonstration APNG.

The Loca development build already uses `DevelopmentShotGuideGateway` when its script-writer server URL
and token are configured. Its existing per-step endpoint now returns the updated animation URLs. Rebuild
the app once to include the cache correction: asset paths, including content revisions, are part of the
guide cache keys. Without that correction, an installed build can retain older downloaded animations.
Production configurations without a development server continue to use bundled guides.

The server streams large APNG files in 64 KB chunks. Animation/scenario/poster/strip URLs include content
hashes, while old flat file URLs remain available. A newly built catalog index is published last and
reloaded automatically by the server; future data-only bundle updates need no server restart.

Rebuild the served bundle from ScriptsAndGuides:

```sh
<python> guides/tools/build_bundle.py
```

The historical default destination is `VideoEditorKit/tools/scriptwriter/catalog`.
For the running service, explicitly pass `--out /Users/ihor.buts/Documents/Development/Scriptwriter/catalog`.
Reviewed Blender base shots take priority, followed by reviewed watercolor animations; `--overlays schematic` selects originals.
Source preview JPEGs, canonical schematic files and live scenario definitions are not changed.

Implementation is in the sibling VideoEditorKit project:

- `tools/scriptwriter/server.py`: guide library endpoints, file streaming, catalog reload.
- `Sources/VideoScripts/ScriptCatalogGateway.swift`: asset-aware guide cache keys.
- `Tests/VideoScriptsTests/GuideAssetRevisionTests.swift`: cache refresh and reuse regression test.

`publication.json` records the running server PID, installed paths and backups of the prior source files
and catalog index. `patches/*.diff` shows the targeted source changes, preserving earlier uncommitted work.
The preparation/publication scripts are guarded one-time migration helpers; ordinary data refreshes use
the bundle builder above.

Verification:

- `staged-api-check.json`: isolated real HTTP handlers, including automatic index reload.
- `live-api-check.json`: running server, all 178 APNG hashes, 890 asset downloads, 304 per-step endpoints,
  authorization, unknown-id handling, duration stretching and compatibility file links.
- `swift-cache-check.json`: changed asset URLs refresh the cache while stable revisions are reused.
- `preservation-check.json`: all 789 snapshotted source files remain unchanged.

The Blender rollout currently publishes reusable base shots immediately. Their `rendering` field states
`native-3d-base-shot; contextual-handover-pending`; it does not claim that the next-shot handover is
complete. The raw APNG is 540×960, uses 65% whole-overlay opacity, and has no baked viewfinder. All 139
were verified through the live API: 178 overlay hashes, 890 assets and 304 per-step endpoints passed.
See `blender-publication.json` and `blender-live-api-check.json`.

For a staged refresh, run the bundle builder with `--out api/bundle`, then
`api/publish_reviewed_assets.py`. It accepts asset/scenario changes for reviewed Blender records and opacity-only updates to deferred artwork,
keeps prior versioned URLs intact, checks all indexed paths, then atomically replaces the catalog.
The menu-to-drink scenario uses an API-only adaptation of its tilt targets: 25 degrees up at the
start and 23 degrees down at the end. Canonical source scenarios remain unchanged.

## Contextual object animations

The live API now returns the actual script-specific animation from
`GET /v1/steps/{templateID.stepID}/guides`. There are 173 object-step versions, including 32 explicit transitions
into the next object shot. The demonstration includes the next object action and can be longer than
one capture step. No new people appear in these sequences.

Guide records expose `scope`, `handoverStatus`, `contextTemplateID`, `contextStepID` and
`nextGuideID`. `handoverStatus: deferred_people` means the export stops before the people shot.
The 39 deferred guide IDs continue to return their previous artwork, rather than the rejected native
people renders. Per-step asset URLs remain immutable and include a content revision.

`GET /v1/scripts/{templateID}/guide-sequence` returns the complete 21.267-second
`cafe-morning-ritual` sequence, including transparent APNG and MP4 URLs. The other 55 scripts report
`scope: deferred_people` and their pending step IDs, with playback deferred. Eight script-specific variants cover worksheet/exercise resources, consistent seasonal-drink
glassware and connected dining, shop and fitness entrances.

`context-live-api-check.json` verifies all 304 step endpoints, 173 contextual animation hashes,
posters/strips, timing, alpha, one complete sequence and 55 explicit sequence-deferral records. `context-server.diff` and
`context-server-publication.json` record the tested handler changes and the backed-up server source.
The existing token is unchanged. Saved Blender projects were preserved; filtering affects exported
animations and publication.

## Cinematic revision (27 October 2026)

33 native guides were regenerated, including the two guitar guides using an imported CC0 model.
68 native scenes have depth-tested warm reflection cues. All 178 published animations use 65%
whole-overlay opacity. Viewfinder and live X/XY levels are separate camera UI. Rebuild the app for
that UI change; immutable asset URLs refresh the animation cache. The bundle now uses the phone
sensor convention for tilt: positive down. See [the complete revision report](../catalog/cinematic-revision/report.md).

The resting-hand guide now uses a locked overhead hold, and 21 dining-table layouts keep dishes at
off-centre personal settings. The 19 affected script sequences were rebuilt and verified through the
live API. See [the correction report](../catalog/table-placement-review/report.md).

The current 65% opacity publication is checked in [the opacity report](../catalog/opacity-65/report.md),
including all 138 video previews and the live API.

`hands_during_top_hold` now serves a 6.8-second close-up massage stroke, with a fixed camera, one
anatomical hand and a cropped curved contact surface. The API-only treatment instructions, capture
duration and scenario match this action. See [the massage preview](../catalog/massage-review/index.html).

The cafe correction and step-boundary audit are documented in
[the cafe report](../catalog/cafe-review/report.md). The current opacity report is
[65% publication](../catalog/opacity-65/report.md). Ordinary cuts stop at the step boundary;
only explicit short whip landings and native connected camera moves cross into the next resource.
