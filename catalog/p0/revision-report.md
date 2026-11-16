# Object-only revision, 4 November 2026

[Play the updated collection](http://127.0.0.1:8766/p0/index.html).

20 animations replaced in their existing directories and under their existing guide IDs. Three approved object guides are retained. No animation IDs were added. The active collection has 23 object-only guides, 69 animation/selector/poster assets and 1,950 encoded frames. Five person/selfie guides are deferred and omitted from the active gallery and P0 API records; source scenes and exports are preserved under `catalog/p0/deferred/` and `guides/p0/deferred/`.

## Changes

- All three entrances share glazed windows on both sides of the door, furnished tables beyond the frontage and a lit venue sign. The hip-height walkthrough has opposed place settings, plates, cups and a plant beside its rear window.
- Both menu-board guides and both counter guides have fixed yellow highlights on selected board, fixture, cup and counter edges. Spare cups are seated on the counter rather than floating above and behind it.
- The flat menu has a short sideways slide and gentle pitch change. The menu-line detail has a curved diagonal approach. The previously fixed counter framing now has a small diagonal slide.
- The napkin-assisted plate demonstration moves sideways across the near table edge. It does not move toward the dish. The phone remains upright on its bottom edge, lens facing the plate. Cup-height steam guidance also has a short lateral slide; the high steam approach changes angle and position together.
- All three pours keep the spout above a receiving point inside the cup. The pitcher starts upright, tilts toward the cup, then returns upright. Flow starts after tilting; the straight stream follows gravity vertically. Its leading front and last tail fall over the gravity travel time. Flow is absent from the final hold. The overhead version finishes on its completed milk art.
- The two handoff entries now demonstrate **after-service** object framing with the cup/saucer and plate stationary on their support. No unseen carrier, airborne plate, modeled hand or eating action is animated. They keep the same IDs with clearer titles and instructions.
- `bite_pip_dish` is a back-camera dish-detail alternative with a resting fork and a short camera curve. The person/eating/PiP-selfie portion is deferred; this guide does not demonstrate eating or a fork grip.
- Both room guides have opposed usable place settings, cups, glasses, menu cards, plants and faint low partition planes. Windows and fixtures motivate fixed light. Broad wall/floor fills are omitted.

Human hand-rotation comments were superseded by the later instruction to make this revision object-only. No human models were regenerated. Step-card illustrations remain separate from the animation assets.

## Replaced in place

| Existing ID | Current title |
|---|---|
| entrance_walk_in | Walk in through the door |
| entrance_door_low | Through the door at hip height |
| entrance_sign_tilt | Sign down to the door |
| menu_board_truck | Slide along the board |
| menu_board_tilt_up | Counter edge up to the board |
| menu_card_top | Menu flat on the table |
| menu_card_push | Into the dish name |
| counter_over_shoulder | Over your shoulder at the counter |
| counter_edge_to_pass | Along the counter to the pass |
| plate_tissue_slide | Tissue slide to the plate |
| handoff_counter_cup | Your cup at the counter |
| handoff_plate_lands | Plate at your place |
| pour_top_down_latte | Latte art from above |
| pour_side_low | Pour at cup height |
| pour_upside_down | Upside-down at the counter |
| steam_low_backlit | Steam against the window |
| steam_push_in_high | Into the steam |
| bite_pip_dish | Dish detail before the bite |
| room_reveal_cup | Room from behind your cup |
| room_seated_pan | Slow pan from your seat |

## Retained

`plate_low_push_in`, `plate_high_orbit`, `steam_orbit_eye`.

## Deferred

- `bite_selfie_eye`: Person/selfie demonstration deferred by the owner; revisit human resources later.
- `sip_selfie_eye`: Person/selfie demonstration deferred by the owner; revisit human resources later.
- `sip_high_lean`: Person/selfie demonstration deferred by the owner; revisit human resources later.
- `verdict_eye_level`: Person/selfie demonstration deferred by the owner; revisit human resources later.
- `verdict_high_plate`: Person/selfie demonstration deferred by the owner; revisit human resources later.

## Publication and verification

The gallery and local Scriptwriter API use the replacement assets. `/v1/shot-types` still has twelve registered types; sip and verdict currently have no active animation choices. Affected step guide lists omit the deferred IDs. Their script steps and step pictures remain available. The original 178-guide legacy endpoint is retained separately from this P0 collection.

Canonical local animation filenames and IDs remain stable. API file URLs include their content hash, so a new render gets a new cache URL through the same guide entry. The staged and published catalog/registry bytes match.

- `revision-checks.json`: exactly twenty existing IDs changed hashes, three retained their hashes, and no new IDs appeared.
- `completion-checks.json`: all 23 active guides show actual pixel changes, contain no people or hands, fit the target hero band and pass timing, alpha, poster, fixed-lens/light and phone-travel checks.
- `saved-scene-checks.json`: actual saved Blender camera keys match metadata; source surfaces are hidden. All three pour meshes have vertical flow, dry initial/final poses and a pitcher tilted toward the cup. Served cup/plate props stay stationary on their supports.
- `browser-checks.json`: all 23 gallery previews load; the menu slider visibly moves in Chrome, holds its final target and uses 65% image-view opacity.
- `staged-api-checks.json` / `live-api-checks.json`: all 23 active P0 trios and all 308 stored step endpoints checked, along with the 178 legacy guides, authentication, empty/deferred choices and coffee/dining picture variants. No pending P0 renders.

Physical phone capture and the mobile app UI were not exercised. Native scenes were tested in installed Blender 5.2.3 LTS. Blender UI was not opened. No paid model generation or image generation was used for this revision.
