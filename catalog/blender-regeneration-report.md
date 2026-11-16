## Approved glass rollout (29 October 2026)

14 unique guides are published in the approved object-only glass style, plus the complete Morning ritual sequence. [Current report](glass-rollout/report.md) · [Playable batch](glass-rollout/coffee/index.html). Earlier counts below describe previous artwork generations.

# Blender guide rollout (updated 27 October 2026)

Current publication: [65% whole-overlay opacity](opacity-65/report.md), with the [cafe and step-boundary corrections](cafe-review/report.md), verified on 27 October 2026.

Latest correction: [stationary resting hand and off-centre table settings](table-placement-review/report.md).

Latest: [33-guide cinematic revision](cinematic-revision/report.md), including the imported CC0 guitar, anatomical hand poses, continuous transitions, reflection cues and separate viewfinder/level UI. All 178 API guides were refreshed to 50% whole-overlay opacity and checked. The sections below retain the rollout history.

137 of 178 guides now use reviewed Blender object/hand animations. This run added 109 object guides. The 41 guides requiring faces, heads, full bodies or people in the scene are deferred at the owner's request; their previous API artwork remains available.

There are 169 script-specific object guide animations, including 78 transitions into the actual next object shot. The complete object-only `cafe-morning-ritual` sequence runs for 21.267 seconds. The other 55 full-script sequences and people handovers are deferred. No new people were published from the stopped render queue.

Published overlays use 50% whole-image opacity, with fainter context, fixed lighting, real perspective and phone-feasible camera paths. Required hand actions use at most two visible hands. The published native frame ranges were checked to contain no visible people.

[Play all guides](animations.html) · [Review script handovers](context-animations/index.html) · [API verification](../api/blender-live-api-check.json)

## Continuity and support repairs

The [continuity audit](continuity-audit/report.md) reviewed 137 active native guides and 78 object handovers. It rebuilt 24 native guides plus two seasonal-drink variants, fixing the handoff/unwrap mismatch, unsupported prop actions, 80 reversed chairs across 14 scenes, vessel changes and the shopping-haul item mismatch. Contextual previews for 27 scripts were refreshed. People generation remains deferred.

## Connected bar-to-table revision

`bar_low_truckr_mm` now uses one shared interior and one continuous 12-second camera path: 0–4 seconds along the bar, 4–8 seconds lifting and turning through the public seating aisle, then 8–12 seconds settling and leaning over the best table. The following `restaurant-room-tour.seat` guide reuses those same table frames. No cut, crossfade, relocated table or new people are used. Main fills remain 25%.

The path travels 1.83 metres at phone heights of 1.18–1.57 metres with a fixed 26 mm virtual lens. Both opposed place settings remain usable. All 180 frames of the bar preview and all 60 frames of the next table step match the reviewed source render. [Play the connected guide](animations.html#bar_low_truckr_mm) · [Continuity checks](blender-animations/bar_low_truckr_mm/connected-transition-checks.json).

The dining-chair orientation was corrected: both seats face the best table, and the four background dining chairs face their own tables. Geometry checks measure the actual backrest placement, with all six facing inward.

The original prototype and canonical capture definitions remain preserved. This revision replaces the demonstration's original hard cut; it does not change unrelated script previews or restart people generation.

## Completed Blender guides

- `bag_handoff_low_hold`
- `bar_low_truckr_mm`
- `burger_cut_high_in_cd_through`
- `burger_cut_high_in_cd_whipout`
- `burger_cut_low_in_cd`
- `burger_low_in_mc`
- `card_label_high_hold_whipout`
- `card_menu_high_in_cd_whipout`
- `card_menu_top_hold`
- `card_pricelist_top_hold`
- `card_receipt_top_hold`
- `card_tag_high_hold`
- `card_tag_top_in_cd`
- `card_tag_top_in_cd_through`
- `card_ticket_eye_in_cd`
- `case_eye_in_mc_through`
- `case_eye_out_cm`
- `case_eye_truckr_mm`
- `chair_reveal_frame`
- `cup_eye_hold_whipout`
- `cup_eye_orbitr_cc`
- `cup_high_out_dm`
- `cup_pour_eye_hold`
- `cup_shot_eye_in_cd_through`
- `details_salon_high_whip_dd_whipout`
- `door_curtain_eye_in_md_through`
- `door_eye_in_wd_through`
- `door_pov_in_wc_through`
- `door_pov_in_wd_through`
- `door_sauna_eye_in_mc_through`
- `facade_eye_hold`
- `facade_eye_in_wm`
- `facade_truck_eye_in_wm`
- `facade_window_eye_in_wm_whipout`
- `facade_window_pov_hold`
- `glass_build_eye_hold`
- `glass_drink_high_hold`
- `glass_eye_tiltd_cc`
- `glass_flight_high_truckr_cc`
- `glass_outro_high_out_dm`
- `glass_pour_eye_in_cd_through`
- `glass_pour_low_in_cd`
- `glasses_clink_center`
- `hand_pov_garment_pov_in_mc`
- `hand_pov_item_pov_in_mc`
- `hand_pov_pastry_pov_in_mc`
- `hands_dough_top_hold`
- `hands_during_top_hold`
- `hands_garment_high_hold`
- `hands_griddle_high_hold`
- `hands_guitar_high_hold`
- `hands_high_hold`
- `hands_stance_top_hold`
- `hands_tool_top_hold`
- `hands_tool_top_hold_whipout`
- `hands_top_hold`
- `hands_work_high_hold`
- `hands_work_high_hold_whipout`
- `hands_work_high_in_cd`
- `hands_wrap_top_hold`
- `interior_pan`
- `latte_top_in_cd`
- `latte_top_in_cd_whipout`
- `machine_low_in_mc_whipout`
- `menu_board_eye_truckr_mm`
- `menu_board_low_tiltd_mm`
- `menu_board_low_truckl_mm`
- `menu_desk_high_hold`
- `menu_event_low_in_cd`
- `menu_hours_low_out_dc`
- `menu_pricelist_eye_in_mc`
- `menu_pricelist_eye_out_dm`
- `menu_schedule_eye_in_mc`
- `menu_schedule_low_tiltd_mm`
- `menu_score_low_out_dc`
- `nails_accent_top_hold`
- `nails_tech_pov_hold`
- `nails_turns_eye_hold`
- `oven_tray_eye_in_mc`
- `oven_tray_eye_in_md_through`
- `pastry_break_eye_hold`
- `pastry_tear_open`
- `plate_bite_top_hold`
- `plate_high_orbitl_cc`
- `plate_kids_top_hold`
- `plate_low_in_cd_through`
- `plate_low_in_cd_whipout`
- `plate_low_in_mc`
- `plate_sizzle_low_in_cd`
- `plate_spread_eye_out_dw`
- `plate_spread_top_hold`
- `plate_spread_top_out_cw`
- `plate_spread_top_out_dw`
- `plate_yolk_high_in_cd`
- `pov_door_entry`
- `rail_bottle_eye_truckr_mm`
- `rail_dumbbell_eye_truckr_cc`
- `rail_garment_eye_truckr_cc_whipout`
- `rail_garment_eye_truckr_mm`
- `rail_guitar_pov_truckr_mm`
- `rail_shelf_eye_truckr_mm_whipout`
- `room_changing_pov_reveal_cm`
- `room_crowd_eye_panr_ww_whipout`
- `room_cupreveal_eye_reveal_dw`
- `room_dining_eye_reveal_cw`
- `room_dining_eye_reveal_cw_whipout`
- `room_eye_panl_ww`
- `room_eye_panr_ww_whipout`
- `room_game_pov_panl_mm_whipout`
- `room_gym_eye_panr_ww`
- `room_lesson_eye_reveal_cw`
- `room_park_high_panr_ww_whipout`
- `room_ride_pov_in_wm`
- `room_sauna_high_out_cw`
- `room_shop_eye_out_cw`
- `room_shop_eye_panr_mm`
- `room_treatment_eye_reveal_cm`
- `room_waiting_eye_reveal_cw`
- `shelf_slide_left`
- `sign_plate_eye_out_cm`
- `sign_tilt_down_reveal`
- `table_corner_pov_out_mw`
- `table_desk_pov_in_mc`
- `table_outlets_high_tiltd_cc`
- `table_seat_high_in_mc`
- `table_treatment_eye_in_mc`
- `tap_pour_glass`
- `tap_taps_low_tiltd_mm`
- `tools_closeup_hands`
- `tools_tray_top_hold`
- `topdown_bag_top_hold`
- `topdown_box_top_out_cm`
- `topdown_first_top_hold_whipout`
- `topdown_haul_top_out_dw`
- `topdown_kidstuff_high_in_cd_whipout`
- `topdown_unwrap_top_in_cd`
- `tray_high_in_mc`

## Deferred people guides

- `before_front_back`
- `counter_barista_side`
- `facade_line_eye_panr_ww_whipout`
- `glass_favorite_eye_in_cd`
- `hair_blend_high_orbitr_cc`
- `hair_signature_high_orbitr_cc`
- `hair_work_high_in_cd_through`
- `over_shoulder_counter_os_hold`
- `over_shoulder_hands_os_in_cd`
- `over_shoulder_hands_os_in_mc`
- `over_shoulder_machine_os_hold`
- `over_shoulder_menu_os_in_mc`
- `over_shoulder_rail_os_hold`
- `over_shoulder_till_os_in_md`
- `person_barber_eye_hold`
- `person_curtain_low_reveal_dm`
- `person_full_low_hold`
- `person_group_eye_hold`
- `person_host_eye_whip_mm`
- `person_mirror_eye_hold`
- `person_mirror_eye_out_cm`
- `person_one_eye_hold`
- `person_player_eye_out_dm`
- `person_process_pov_in_mc_through`
- `room_lights_eye_hold`
- `room_stage_low_in_wm_whipout`
- `selfie_bag_high_hold`
- `selfie_bite_eye_in_mc`
- `selfie_bite_eye_out_cm`
- `selfie_bite_reaction`
- `selfie_close_eye_hold`
- `selfie_close_high_hold`
- `selfie_one_high_hold`
- `selfie_reveal_eye_reveal_cc`
- `selfie_reveal_eye_reveal_cm`
- `selfie_sip_eye_in_mc`
- `selfie_sip_reaction`
- `selfie_two_eye_hold`
- `selfie_two_high_hold`
- `table_bench_eye_out_dw`
- `talking_head_eye_level`

## Verification and limits

The live API check covers 178 animation hashes, 890 asset downloads and 304 step endpoints. [Contextual API checks](../api/context-live-api-check.json) cover 169 per-step animations, one complete sequence and 55 explicit sequence-deferral responses. Canonical source previews and scenarios remain unchanged; sensor-angle corrections are API-only adaptations.

Camera reach, short travel, fixed lenses/light sources, contacts and hand counts were checked in the native scenes. Physical phone capture, venue-specific access and automatic resource recognition were not tested on a device.

The saved Blender projects remain intact. Six older projects still contain their archived people stages; published animation exports stop before those stages. The render policy blocks new people generation and no Blender UI is opened automatically.
