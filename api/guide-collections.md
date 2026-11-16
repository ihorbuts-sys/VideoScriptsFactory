# Additive guide collections

The Scriptwriter service now supports complete scene collections and scene
proofs alongside the existing guide and script endpoints. It reads
`catalog/guide-collections.json` on each request, so publishing a collection
does not require another restart.

- `GET /v1/guide-collections`: paginated list; supports `venueKind`, `page` and
  `pageSize`.
- `GET /v1/guide-collections/{id}`: full sequence, metadata and phases.
- `GET /v1/guide-collections/{id}/phases/{phase}`: one shot and its handover.

Use the existing bearer token. Asset URLs carry the existing file token and
point to immutable content-hash paths. The `colorVideoURL` is MP4, `overlayURL`
is transparent APNG, and `blenderURL` is the packed native scene.
Do not apply another alpha multiplier to the returned ghost: its 65% factor is
already encoded in every pixel, including the contour lines.

`coffee-ordering` is explicitly a `scene-proof` of counter-to-extraction camera
motion, with `fullScriptSequenceComplete: false`. Its three phases are `order`,
`extraction` and `cup-detail`. Intermediate clips include the beginning of the
next phase. The same camera and scene generate both color and ghost variants.

The full collection uses this endpoint. Its extraction clip is also published through the existing app routes: `GET /v1/steps/cafe-before-opening.shot/guides` and `GET /v1/guides/cup_shot_eye_in_cd_through`. Pick Cafe → Before opening → First shot in the app. The clip lasts 9.53 seconds and includes a camera settle within the same scene; the capture instruction remains five seconds. The next script step is still a cut, with no handoff performance claimed. Other guide bindings, step preview art and script sequences are preserved.

The route smoke check verifies authentication, file access, phase lookup,
unknown IDs, pagination, venue filtering and preservation of all 178 guides.
See `shared-collections-route-check.json` and the installation report. Publishing
also checks that the original `catalog.json` is byte-for-byte unchanged.

The separate `coffee-hologram` collection contains the 16-second glass/hologram material study and the same three phases. It uses native surface orientation, translucent volumes and a broad travelling highlight, with no detected ink contours. Its publication preserves the current template bindings. No Tripo generation or retexturing job was required.

For `coffee-hologram`, the current overlay is an intrinsically transparent object-only image. It has `alphaFactor: 1`; apply `imageViewOpacity: 0.65` on the image view. Play `colorVideoURL` below it with `backgroundDelaySeconds: 2`. Draw the viewfinder separately, as indicated by `viewfinderLayer: separate_ui`. Walls, floor and ceiling are excluded from this overlay. The older collection defaults above still apply to collections with a baked opacity factor.
