# Canonical creator guides

10 November 2026. Five formerly deferred guides are restored under the same IDs, with three additional friend-filmed options. All 37 local P0 guides are ready; all 87 assets belonging to the earlier 29 guides remain byte-identical.

[Play locally](http://127.0.0.1:8766/p0/index.html#sip_selfie_eye). The owner chose to keep the eight new character guides local/API-only. The public gallery remains at 29. No character assets were uploaded. The default public packaging excludes all eight character guides.

|Guide|Capture|Lens height|Downward tilt|Playback|
|---|---|---|---|---|
|bite_selfie_eye|Front camera, mirrored|1.55 m|8.7 degrees|6 s|
|sip_selfie_eye|Front camera, mirrored|1.55 m|8.7 degrees|6 s|
|sip_high_lean|Front camera, mirrored|1.76 m|28.2 degrees|6 s|
|verdict_eye_level|Front camera, mirrored|1.55 m|8.7 degrees|7 s|
|verdict_high_plate|Front camera, mirrored|1.76 m|30.5 degrees|7 s|
|bite_friend_three_quarter|Friend, rear camera|1.54 m|4.8 degrees|6 s|
|sip_friend_side|Friend, rear camera|1.53 m|4.4 degrees|6 s|
|verdict_friend_eye|Friend, rear camera|1.54 m|4.8 degrees|7 s|

The normal selfie lens stays at eye height, aimed slightly below the eyes for framing. Higher selfie examples look down gently. Friend examples start about a metre away at a three-quarter angle and make a small smooth diagonal approach. The camera holds still during the selfie subject action.

## Model suitability

The existing creator shape is usable for framing, head turns, small gestures and restrained cup/fork actions. The original skinned body and both anatomical hands are retained. No detached replacement hands or regenerated characters are used. The lower torso fades out so the ghost emphasizes the face and the action. The recording hand and phone are not demonstrated.

The source has no jaw, lip, eyelid or facial expression controls. These guides do not demonstrate chewing, blinking or speech. The fork stops beside the lips before a bite; the cup rises to the lower mouth area and returns. A facial rig is required for convincing eating or talking. A complete new head is not needed for the current framing guides.

The line-art copy joins and welds the original segmented mesh before reducing it to approximately 90,000 faces. Existing eye texture marks become small surface contour patches; textures are not rendered. Source models remain unchanged. A selection bug in `geometry.tube` was fixed: prop conversion previously converted selected character meshes and baked away their skinning modifiers. No new Tripo or image-generation credits were used.

## Assets and API

- Current scenes, frames and playback copies: `catalog/p0/animations-light/<id>/`.
- API masters: `guides/p0/renders/<id>.png`, `<id>_selector.png`, `<id>_poster.png`.
- Earlier studies in `guides/p0/deferred/` and `catalog/p0/deferred/` are archived and excluded from bundles.
- Creator contour source: `model_refferences/creator/lineart/asset.blend`.
- API: `/v1/shot-types/first-bite/guides`, `/v1/shot-types/sip/guides`, `/v1/shot-types/verdict/guides`.
- Each character record supplies `camera`, `filmingMode`, `previewMirrored`, `facialAnimation: false`. Use the selected guide camera; the shot-type default remains front. Do not mirror an already mirrored guide a second time.
- First Visit and Food Review steps receive their choices through the existing shot-type mappings. Static step artwork is unchanged.

## Verification

- 37 exports, 111 API assets, 3,405 native frames; all image frames open, alpha is preserved, no shaded mesh surface appears, and start/end targets match.
- All 37 saved native scenes passed camera, source-visibility, fixed-light and relevant support/physics checks.
- All eight character scenes passed checks of actual skinned hand motion, original rig binding, wrist bend, prop attachment, camera height and distance. The verdict plate has real support, at least 6 cm rim margin, and its complete rim clears recording controls.
- All eight animations played in headless Chrome. Screenshot pixels changed during the action and returned exactly to the poster at the end. All 37 posters loaded at a 390 px layout width without overflow.
- See `completion-checks.json`, `saved-scene-checks.json`, `people-scene-checks.json`, `people-browser-checks.json`, `staged-api-checks.json` and `live-api-checks.json` for results.

Numeric checks do not certify perfect anatomy. The actual phone capture UI, on-device camera field of view and automatic camera switching were not tested. Installed Blender is 5.2.3 LTS; Blender 4.x playback was not tested. Public expansion was declined; keep these character assets local/API-only unless the owner gives a new explicit instruction.

## Hand orientation correction

All eight active character hand poses were turned 180 degrees around the finger axis, including the three open-palm verdict gestures. Rotation is shared across shoulder and forearm to avoid an isolated wrist twist. The cup/fork contacts are retained, and the open-palm turn is slower. All eight full motion paths and rendered scenes were checked, including an anatomical palm-normal check toward the camera during the active pose. Browser playback and the local API were refreshed with new asset hashes. The original 29 object guides remain unchanged; these character guides remain local/API-only. See `palm-correction-checks.json`.
