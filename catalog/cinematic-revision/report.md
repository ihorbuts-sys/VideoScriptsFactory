# Cinematic guide revision — 27 October 2026

Current publication: [65% whole-overlay opacity](../opacity-65/report.md), with the [cafe and step-boundary corrections](../cafe-review/report.md), verified on 27 October 2026.

Latest treatment revision: [close-up massage action](../massage-review/report.md) replaces the previous resting-hand hold.


Follow-up: [resting-hand and 21 dining-table corrections](../table-placement-review/report.md). The resting-hand guide now holds still, and personal plates are kept away from table centres.

33 existing native guides were regenerated, and three new script-specific entrance variants were added. The local API now serves the revised files. The catalog has 178 guides: 137 Blender object/hand guides, 19 previous watercolor guides and 22 previous schematics. The 41 people-dependent guides remain deferred.

[Play all guides](../animations.html) · [Play the 33 revised videos](index.html) · [Script-specific playback](../context-animations/index.html) · [Verification data](verification.json)

## What changed

- Camera paths coordinate XYZ travel and changing pitch with smooth acceleration. Source descriptions, composition, support/contact and public-side access were reviewed before rendering.
- The specified door, case, menu, drink and box demonstrations now continue through the same physical scene. There are 17 continuous handovers in the script catalog, including the previously connected bar/table guide. The remaining 61 object handovers use separate shots.
- The burger box travels from the ledge to the table, then opens during one continuous 10.4-second camera move. The following unwrap step reuses frames 91–156 of that same scene.
- Water from the kettle reaches the cup beside the plate. Bar drink views stay on the customer side. Opened pastries show cream/chocolate filling.
- Actual imported anatomical hand geometry replaces the specified broken hands. The held-menu scene uses a left support hand and a right pointing hand. A helper films the two-hand demonstration. Unsupported grips or playing hands were replaced by supported alternatives where appropriate.
- Both guitar guides use the imported CC0 acoustic guitar, including its sound hole, bridge, frets, tuners and six strings. The rack framing was corrected to show complete instruments.
- The reflection pass checked all 137 native scenes. 68 contain visible, depth-tested warm rim/edge highlights on cups, glasses, plates or window frames. Highlights depend on camera/object movement; physical lights stay fixed. Geometry and archived Blender projects were not modified by this pass.
- Eight active contextual variants were exported again, including the three new entrance interiors.

## Published opacity and UI

Every published animation uses 50% whole-overlay opacity, including its lines. The maximum alpha is 128/255; background hierarchy stays fainter. The result is derived once from a preserved master with RGB unchanged. Do not apply another 50% CSS or app opacity multiplier. Engineering masters retain their earlier alpha settings.

Published native APNGs and review MP4s contain no baked viewfinder. Catalog corners, composition references and X or X/Y reference levels are a separate browser UI layer with a toggle. The browser references are not live sensor readings. The camera app now draws its own viewfinder and live gravity-based X level, switching to two axes near overhead with hysteresis. Missing sensor data does not show a false level indication. Rebuild the mobile app to include this UI change.

The API camera-angle adaptation was corrected to use positive downward tilt, matching the phone motion sensor. Canonical scenario JSON was preserved. API-only directions and capture durations describe supported alternatives, shared landing frames and helper requirements. Existing guide IDs remain stable even when their historical names mention hands.

## Regenerated native guides

|Guide|Seconds|Pitch change, degrees|Phone travel, metres|Demonstrated action|
|---|---|---|---|---|
|`card_menu_high_in_cd_whipout`|9|33.8|0.84|A menu is held at 50 degrees while the other hand points to the lunch offer; A diagonal rising arc changes pitch and reveals all dishes on the same table|
|`card_menu_top_hold`|5|5.3|0.19|One anatomical index settles beside the selected treatment line; Menu categories and price-list hierarchy remain visibly distinct and readable|
|`card_pricelist_top_hold`|5|5.3|0.19|One anatomical index settles beside the selected price line; Menu categories and price-list hierarchy remain visibly distinct and readable|
|`card_label_high_hold_whipout`|8|13.7|0.68|Maker detail and price tag belong to the same recognisable folded garment; A curved diagonal move changes distance and pitch while the text remains readable|
|`card_tag_high_hold`|5|13.8|0.28|Maker detail and price tag belong to the same recognisable folded garment; A curved diagonal move changes distance and pitch while the text remains readable|
|`card_tag_top_in_cd`|5|13.8|0.28|Maker detail and price tag belong to the same recognisable folded garment; A curved diagonal move changes distance and pitch while the text remains readable|
|`card_tag_top_in_cd_through`|5|13.8|0.28|Maker detail and price tag belong to the same recognisable folded garment; A curved diagonal move changes distance and pitch while the text remains readable|
|`hands_garment_high_hold`|5|19.3|0.32|Collar, folded sleeves and placket show the garment right way up; The tag remains physically attached; no hanger floats beneath the garment|
|`hands_during_top_hold`|6.8|0.0|0.00|Fixed-camera close-up: one anatomical hand presses, glides and releases over a cropped curved back surface.|
|`hands_guitar_high_hold`|6|20.4|0.58|The instrument remains supported on the table; A curved pitch-changing detail move follows strings toward the body; no unverified playing hands are drawn|
|`case_eye_in_mc_through`|9|60.9|1.48|Select the pastry from the customer side of the case; Move along the same public counter to an opened filled croissant resting on its plate|
|`hand_pov_pastry_pov_in_mc`|5|23.2|0.39|Opened croissant halves show crust and filling while supported by a plate; A smooth rising arc changes X-axis pitch and reveals the cut faces without uncertain hands|
|`pastry_tear_open`|5|23.2|0.39|Opened croissant halves show crust and filling while supported by a plate; A smooth rising arc changes X-axis pitch and reveals the cut faces without uncertain hands|
|`pastry_break_eye_hold`|5|23.2|0.39|Opened croissant halves show crust and filling while supported by a plate; A smooth rising arc changes X-axis pitch and reveals the cut faces without uncertain hands|
|`door_eye_in_wd_through`|11|12.1|3.62|The hinged door opens while the camera waits outside; Walk through the same doorway and along its clear public dining aisle|
|`door_pov_in_wc_through`|11|6.5|3.62|The hinged door opens while the camera waits outside; Walk through the same doorway and along its clear public waiting aisle|
|`door_pov_in_wd_through`|11|14.5|3.62|The hinged door opens while the camera waits outside; Walk through the same doorway and along its clear public salon aisle|
|`facade_eye_hold`|5|17.1|0.96|A curved public-side approach reveals sign, entrance and window depth; Camera height and X-axis pitch change together as attention moves toward the door|
|`facade_truck_eye_in_wm`|8|5.5|1.91|An open serving window reveals the real food rack inside the truck; A curved approach changes height and pitch entirely outside the visitor-facing ledge|
|`facade_window_pov_hold`|4|2.2|0.47|An open serving window reveals the real food rack inside the truck; A curved approach changes height and pitch entirely outside the visitor-facing ledge|
|`facade_window_eye_in_wm_whipout`|4|2.2|0.47|An open serving window reveals the real food rack inside the truck; A curved approach changes height and pitch entirely outside the visitor-facing ledge|
|`cup_pour_eye_hold`|9|35.6|0.72|Water starts at the actual tilted kettle spout and lands inside the cup; A diagonal rising arc reveals that cup and the neighbouring plate on the same table|
|`cup_shot_eye_in_cd_through`|5|25.3|0.19|The same cup rests on its saucer and public counter; A small curved rise changes pitch and reveals the coffee context without an unreliable pickup grip|
|`cup_high_out_dm`|5|18.7|0.42|The same cup rests on its saucer and public counter; A small curved rise changes pitch and reveals the coffee context without an unreliable pickup grip|
|`glass_drink_high_hold`|9|54.9|0.62|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`glass_flight_high_truckr_cc`|10|50.5|1.05|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`glass_outro_high_out_dm`|5|22.9|0.71|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`glass_pour_eye_in_cd_through`|9|32.3|0.70|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`glass_pour_low_in_cd`|8|28.1|0.72|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`glass_eye_tiltd_cc`|5|1.1|0.38|Served vessels stay physically supported at the customer edge; Smooth diagonal travel and changing pitch connect the drink to the same bar context|
|`rail_guitar_pov_truckr_mm`|4|1.4|0.84|Detailed CC0 guitars remain supported on one customer-facing display; A short curved rightward walk changes height and pitch while keeping bodies and headstocks together in frame|
|`bag_handoff_low_hold`|10.4|93.9|1.38|Carry one burger box from its ledge to the table, then follow it with one smooth camera rise and open the same box overhead|
|`topdown_unwrap_top_in_cd`|4|0.0|0.23|Open the supported takeaway box from above, revealing the whole burger resting on its base|

## Continuous script handovers

The next step reuses landing frames from the connected scene.

|Script step|Guide|
|---|---|
|`salon-quick-tour.door`|`door_pov_in_wd_through`|
|`restaurant-date-night.entrance`|`door_eye_in_wd_through`|
|`restaurant-weekend-brunch.pour`|`cup_pour_eye_hold`|
|`restaurant-room-tour.door`|`door_pov_in_wd_through`|
|`restaurant-room-tour.bar`|`bar_low_truckr_mm`|
|`restaurant-lunch-deal.menu`|`card_menu_high_in_cd_whipout`|
|`bar-tasting.flight`|`glass_flight_high_truckr_cc`|
|`night-live-music.drink`|`glass_drink_high_hold`|
|`bar-happy-hour.pour`|`glass_pour_eye_in_cd_through`|
|`quick-truck-find.truck`|`facade_truck_eye_in_wm`|
|`quick-truck-find.handoff`|`bag_handoff_low_hold`|
|`food-review-pour.build`|`glass_pour_low_in_cd`|
|`food-review-sweet.case`|`case_eye_in_mc_through`|
|`shop-find-of-the-day.label`|`card_label_high_hold_whipout`|
|`shop-tour.door`|`door_pov_in_wd_through`|
|`fit-first-class.door`|`door_pov_in_wd_through`|
|`fit-first-appointment.door`|`door_pov_in_wc_through`|

## Reusable source models

- [Innerscene acoustic guitar, CC0](https://www.innerscene.com/tools/library/3d-parts/dreadnought-acoustic-guitar-39847fd7): original GLB retained in `guides/blender_motion/vendor/innerscene-guitar/`; 91 meshes and 30,497 vertices. Source, license and file hash are recorded beside it. Shared ghost materials replace the original render materials.
- [FPS Arms by para / MakeHuman, CC0](https://opengameart.org/content/fps-arms-rigged-only): original archive and model retained in `guides/blender_motion/vendor/para-fps-arms/`. Cropped anatomical hand meshes and baked relaxed, pointing and pinch poses are reused. Pose preparation code and contact landmarks are retained.

## Verification

- All 33 revised native scenes passed geometry checks: no visible people, at most two visible hands, fixed lights/lenses and reachable phone paths. Phone heights across these scenes are 0.90–1.77 metres; the connected entrance walks use clear visitor aisles.
- All 178 guides, 890 supporting-file downloads and 304 step endpoints passed the live API checks, including authorization, immutable file hashes and compatibility links.
- All 169 contextual object clips passed hash, duration, opacity and poster/strip checks. Their 78 object handovers and the complete 21.267-second `cafe-morning-ritual` sequence are available.
- Four gravity-level math tests and six camera-orientation checks passed. The camera target compiled with the iOS device SDK. The existing Cinematic dependency is unavailable in the simulator SDK.
- All 789 snapshotted inputs are unchanged, including 304 source preview JPEGs, their 304 catalog copies and 178 guide definitions. All referenced media files exist across the four review pages. Headless Chrome loaded the separate browser reference UI.

## Limits

People remain deferred: 41 guide IDs and 135 script steps retain their previous artwork. Their 55 complete script sequences remain explicitly deferred; no incomplete full sequence is presented as complete. Other native camera paths were not all redesigned in this revision. Geometry and rendered frames were reviewed locally, but physical phone capture and the updated sensor UI were not exercised on a device. The static PDF was not regenerated in this animation revision; use the HTML catalog for the current moving previews. Blender UI was not launched.
