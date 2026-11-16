# scriptwriter

The script writing backend for the demo: writes the shooting direction, on-screen text and
prompter lines of script steps with Claude Code on this Mac (your Claude login), following the
`script-writer` skill in `.claude/skills/`. Venue facts come from the Loca GraphQL API by venue id.
Development only: VideoEditorKit's `DevelopmentScriptWritingGateway`, `DevelopmentVenueGateway`,
`DevelopmentScriptCatalogGateway` and `DevelopmentShotGuideGateway` call it; a production backend implements
the same API (with the Claude API) behind the kit's `ScriptWritingGateway`, `VenueGateway`,
`ScriptCatalogGateway` and `ShotGuideGateway`.

Run (Claude Code installed and logged in):

    python3 server.py [--port 8765] [--model sonnet]

The first run writes a token to `.token` (ignored by git). Build the demo with the server's address
and token so the app finds it:

    xcodebuild ... SCRIPT_WRITER_URL=http://$(scutil --get LocalHostName).local:8765 SCRIPT_WRITER_TOKEN=$(cat .token)

Try one request without serving: `python3 server.py --write request.json`.

## API

Every call sends `Authorization: Bearer <token>`. Errors answer with `{"error": "..."}`.

`POST /v1/scripts/write`

```json
{ "venueID": "uuid or null", "venueKind": "coffee", "language": "en", "mood": null, "daypart": "morning", "targetSeconds": 60,
  "script": { "title": "First visit", "summary": "..." },
  "steps": [ { "id": "entrance", "title": "Arrive", "shot": "wide", "seconds": 3,
               "direction": "...", "prompter": "...", "pip": false, "isOwn": false } ],
  "only": ["entrance"] }
```

`only` (optional) lists the steps to write; the others are context. The answer has one entry per
written step:

```json
{ "steps": [ { "id": "entrance",
               "seconds": 6,
               "direction": "Low angle from the curb, slow push toward the door.",
               "onScreenText": "{venue.name}",
               "card": "First time at {venue.name}",
               "prompter": [ { "type": "say", "text": "First time at {venue.name}." },
                             { "type": "pause", "seconds": 1.0 },
                             { "type": "cue", "text": "look at the sign" } ] } ] }
```

`seconds` is the suggested step length; all steps together come close to `targetSeconds`, and the
lines fill 40-80% of each step. `onScreenText` null means no text on the video. A `cue` is
shown on the prompter but not read; a `pause` holds the prompter's scrolling.

`menuItem` (optional) is the menu item the script reviews, as `GET /v1/venues/{id}/menu` returns it.

A step may carry `opinion` (`{"set": "verdict_answer", "options": [{"text": "Certainly."}, ...]}`, or only `set`,
looked up in `catalog.json` `opinionSets`): its written line then ends on exactly one `{opinion}` slot the creator
fills on the device, and the line is timed with the longest option in. Without it no line carries the slot. Each
written step may also return `card` (at most 6 words, null allowed), the on-screen text for a silent take. The server
refuses a step that judges for the creator, quotes staff or crowds, teases without saying, puts an opinion, question
or call to action in `onScreenText`, names a time of day without a daypart, or uses an unknown slot; the rules are
VideoGuides `scripts/tools/line_lint.py` (`LINE_LINT_DIR`, default `../VideoGuides/scripts/tools`), and without that
checkout only the slots are checked.

`daypart` (optional) is when the video is filmed, in the venue's time zone: `morning` (opening to 11:00), `midday`
(11:00-16:00) or `evening` (16:00 to close); the app derives it from the capture time. Without it (or with another
value) the server takes it from `menuItem.section` (breakfast, brunch -> morning; lunch -> midday; dinner, happy hour,
cocktails, bar -> evening; English and Ukrainian words, `SECTION_DAYPARTS` in `server.py`), else none. With a daypart
the lines are written for that time of day; without one they never name a time of day.

`GET /v1/venues?page=1` lists Loca venues to pick from (demo only):
`{ "venues": [ { "id", "title", "kind", "city", "hasMenu", "reward" } ], "nextPage": 2 }`, where
`reward` is the active visit reward (`{ "perVisitCents": [300, 100, 200, 300], "currency": "USD" }`)
or null; in Loca the app already has it from the business profile.

`GET /v1/venues/{id}/menu` lists every item of the venue's Loca menus:
`{ "items": [ { "id", "name", "description", "section", "price": "12.50 USD", "dietary": ["Vegan"], "menuURL" } ] }`.

`GET /v1/venue-kinds` lists the script catalog's venue kinds: `{ "venueKinds": [ { "id", "title", "symbol" } ] }`.

`GET /v1/venues/{id}/scripts?page=0&pageSize=20` lists the scripts for a venue: its kind is decided here from
the venue's Loca category slugs (`catalog.json` `categoryKinds`, first match wins), so the app needs no
mapping of its own: `{ "venueKind": "coffee", "templates": [...], "nextPage": 1 }`. `venueKind` null and no
templates means none of the venue's categories has scripts (the app offers a custom script).
`GET /v1/scripts?venueKind=coffee&page=0&pageSize=20` lists a kind's scripts the same way. Every step's
`imageURL`, `examplePreview` and `overlays` (its guides' animations) are links to `GET /v1/files/...` on this
server. Steps carry the P0 fields `shotType` (one of the 12 or `none`), `access` (`public`, `counter`, `staff`),
`captureOrder`, `editOrder`, `required`, `voice`, `ambient`, `camera`, `composition` and `guides` (ids, the
recommended one first); a guided step's `seconds` is its first guide's `durationSec`. A template whose steps list
`venueKinds` (`first-visit`) comes resolved for the kind, with `venueKind` set and the orders counted from 1;
without `venueKind` it comes once per kind.

`GET /v1/steps?page=0&pageSize=40&venueKind=` pages the step library for custom scripts, grouped by venue kind
with the steps of scripts that fit several kinds in a general group (`venueKind` null) at the end; `venueKind`
keeps that kind's and the general steps. Staff steps are left out. A group continues on the next page when its
kind repeats there:
`{ "groups": [ { "venueKind": "coffee", "title": "Cafe", "steps": [ { "templateID", "templateTitle", ...step } ] } ], "nextPage": 1 }`.

`GET /v1/shot-types` lists the P0 shot types: `{ "shotTypes": [ { "id", "title", "startTrigger", "capturePreset",
"composition", "camera", "ambientDefault", "guides" (ids in order), "durationSec": { "min", "max" } } ] }`.
`GET /v1/shot-types/{id}/guides` returns `{ "shotType", "guides": [...] }` with the type's guides in order.

`GET /v1/steps/{templateID.stepID}/guides?venueID=` lists the step's guides in order (2 to 3, the recommended one
first), `[]` for a step with `shotType: none`: `{ "stepID", "templateID", "venueKind", "shotType", "seconds",
"guides": [ { "id", "shotType", "title", "invariant", "durationSec", "startTrigger", "capturePreset",
"setupBeatSeconds", "alphaFactor", "animation" (APNG 405 x 720), "selector" (APNG 120 x 213), "poster" (frame 0,
the target frame), "sha256" } ] }`. `seconds` is the first guide's `durationSec`; `duration` is ignored. `sha256`
null means the guide is not rendered yet and its files answer 404.

`POST /v1/scripts/write` gives every returned step `shotType` (the request step's, else from the keyword table
`stepKeywords` in `shot_types.json`), that type's `guides`, and the first guide's length as `seconds`.

`GET /v1/files/{previews|overlays|scenarios|3d}/{name}?token=` serves a step picture, a guide's APNG, scenario
(`&duration=` stretches it) or 3D spec from the catalog folder.

The catalog folder (`SCRIPT_CATALOG_DIR`, default `catalog/` next to this file, not in git) is built by Loca's
`.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/ScriptsAndGuides/guides/tools/build_bundle.py --profile p0`: `catalog.json`,
`shot_types.json` plus `previews/`, `overlays/`, `scenarios/` and `3d/`.

`GET /v1/music?query=&page=0&pageSize=20` serves the kit demo's music catalog (`VideoEditorKit/Demo/VideoEditorDemo/Music`,
`MUSIC_DIR` overrides it; written by the kit's tools/beatmarker; the MP3s stay out of git) as `{ "tracks": [...], "nextPage": 1 }`, each
`audioURL` pointing at `GET /v1/music/files/{name}?token=` on this server.

Venue data comes from the Loca test environment, as the Loca dev app uses (`LOCA_GRAPHQL` overrides
it); every query is a public read.

## Complete animation library

`GET /v1/guides?page=0&pageSize=20` pages all 178 unique guides: `{ "guides": [...], "total": 178,
"nextPage": 1 }`. `GET /v1/guides/{id}?duration=` returns one guide. Both use the existing bearer token.
The existing per-step endpoint continues to return the same guide objects.

Each guide includes `id`, `overlayURL` (transparent APNG, without baked viewfinder UI), `scenarioURL`,
`model3DURL`, `posterURL`, `stripURL`, `seconds`, `camera`, `moves`, `subject`, `style` and `sha256`.
Reviewed watercolor guides also include `alphaFactor: 0.5`, `animationSeconds` and the rendering method.
`seconds` describes the live scenario; `animationSeconds` describes the demonstration APNG loop.

The bundle builder defaults to reviewed watercolor artwork where available (currently 96 guides),
falling back to original schematics for the other 82. `--overlays schematic` builds the original set.
It preserves the source previews and sensor scenarios. The global 50% alpha is already in watercolor
APNGs; clients must not apply it again.

Changed overlays and scenarios have content-versioned URLs; flat legacy file links remain valid.
The iOS repository includes asset paths in cache keys, so a rebuilt app refreshes changed guide assets.
The server reloads a catalog when its atomic catalog.json index changes; future bundle rebuilds need
no server restart. Asset files are installed before the index is replaced.

## Catalog version 3 (2026-11-16)

`POST /v1/scripts/write` with `kind` set to one of `dish-review`, `drink-review`, `menu-item-review`, `venue-review`
uses the v3 path: the request carries `subject` (venue review), `dishKind` or `drinkKind`, an optional `menuItem`
(`name`, `price`, `section`, `source`), `daypart` and `only` (step keys). The response is
`{"kind", "context", "steps": [{"key", "versions": [{"line", "card", "caption"}]}]}`; every version passes the catalog
rules from `VideoGuides/scripts/tools/v3_catalog.py` or the request fails with the problems. Alcohol drink kinds are P1
and refused. Requests without `kind` keep the v2 behaviour. The bundle's `catalog_v3.json` is built by
`build_bundle.py --catalog-version 3` (not published by this change).
