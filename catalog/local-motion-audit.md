# Local animation audit

All 178 guides were checked for camera/subject mechanics and matching reusable artwork. Fixed paintings and cutouts preserve linework between frames. Source script previews and sensor scenarios are unchanged.

New source artwork: 12 immutable AI-painted resources, reused across multiple guides. Global alpha is multiplied by 0.5 once after composition. No artwork is drawn with geometric primitives.

A crop/pan is an image-plane camera approximation, not a newly reconstructed 3D viewpoint. True orbits and actor turns require consistent perspective/pose artwork. Independent finger, steam, pouring and working actions are not synthesized in camera-only guides.

| Result | Guides |
|---|---|
| applied | 92 |
| needs matching art | 56 |
| needs matching layers | 24 |
| requires viewpoints | 6 |

| Guide | Result / mechanic | Reason / limitation |
|---|---|---|
| [bag_handoff_low_hold](animations.html#bag_handoff_low_hold) | needs matching layers / isolated action layers or corrected camera master | Needs isolated tray/hands over the fixed window; holding the whole scene would omit the handoff. |
| [bar_low_truckr_mm](animations.html#bar_low_truckr_mm) | applied / pan | One immutable painted image; deterministic camera window, no generated intermediate frames. |
| [before_front_back](animations.html#before_front_back) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [burger_cut_high_in_cd_through](animations.html#burger_cut_high_in_cd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [burger_cut_high_in_cd_whipout](animations.html#burger_cut_high_in_cd_whipout) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [burger_cut_low_in_cd](animations.html#burger_cut_low_in_cd) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [burger_low_in_mc](animations.html#burger_low_in_mc) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_label_high_hold_whipout](animations.html#card_label_high_hold_whipout) | applied / whip | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [card_menu_high_in_cd_whipout](animations.html#card_menu_high_in_cd_whipout) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_menu_top_hold](animations.html#card_menu_top_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_pricelist_top_hold](animations.html#card_pricelist_top_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_receipt_top_hold](animations.html#card_receipt_top_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_tag_high_hold](animations.html#card_tag_high_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_tag_top_in_cd](animations.html#card_tag_top_in_cd) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_tag_top_in_cd_through](animations.html#card_tag_top_in_cd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [card_ticket_eye_in_cd](animations.html#card_ticket_eye_in_cd) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [case_eye_in_mc_through](animations.html#case_eye_in_mc_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [case_eye_out_cm](animations.html#case_eye_out_cm) | applied / dolly_out | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [case_eye_truckr_mm](animations.html#case_eye_truckr_mm) | applied / pan | One immutable painted image; deterministic camera window, no generated intermediate frames. |
| [chair_reveal_frame](animations.html#chair_reveal_frame) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [counter_barista_side](animations.html#counter_barista_side) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [cup_eye_hold_whipout](animations.html#cup_eye_hold_whipout) | applied / whip | Whip exits the shot. The next pastry shot is a separate take; steam is held, not synthesized. |
| [cup_eye_orbitr_cc](animations.html#cup_eye_orbitr_cc) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [cup_high_out_dm](animations.html#cup_high_out_dm) | applied / dolly_out | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [cup_pour_eye_hold](animations.html#cup_pour_eye_hold) | needs matching layers / isolated action layers or corrected camera master | Existing art looks down onto the plate; required resource-height camera is missing. |
| [cup_shot_eye_in_cd_through](animations.html#cup_shot_eye_in_cd_through) | needs matching layers / isolated action layers or corrected camera master | Existing cup angle looks down; requires resource-height master. |
| [details_salon_high_whip_dd_whipout](animations.html#details_salon_high_whip_dd_whipout) | applied / pan | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [door_curtain_eye_in_md_through](animations.html#door_curtain_eye_in_md_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [door_eye_in_wd_through](animations.html#door_eye_in_wd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [door_pov_in_wc_through](animations.html#door_pov_in_wc_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [door_pov_in_wd_through](animations.html#door_pov_in_wd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [door_sauna_eye_in_mc_through](animations.html#door_sauna_eye_in_mc_through) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [facade_eye_hold](animations.html#facade_eye_hold) | applied / hold | One immutable painted image; deterministic camera window, no generated intermediate frames. |
| [facade_eye_in_wm](animations.html#facade_eye_in_wm) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [facade_line_eye_panr_ww_whipout](animations.html#facade_line_eye_panr_ww_whipout) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [facade_truck_eye_in_wm](animations.html#facade_truck_eye_in_wm) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [facade_window_eye_in_wm_whipout](animations.html#facade_window_eye_in_wm_whipout) | applied / dolly_in | Downward exit follows the written shot. Legacy sensor direction is retained unchanged. |
| [facade_window_pov_hold](animations.html#facade_window_pov_hold) | applied / hold | Camera hold is demonstrated; the ordering gesture is not newly animated. |
| [glass_build_eye_hold](animations.html#glass_build_eye_hold) | needs matching layers / isolated action layers or corrected camera master | Needs isolated pouring/building layers; holding the finished glass would omit the action. |
| [glass_drink_high_hold](animations.html#glass_drink_high_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [glass_eye_tiltd_cc](animations.html#glass_eye_tiltd_cc) | applied / tilt_follow | Rigid glass/hand lowers while the camera tilts; no finger articulation. |
| [glass_favorite_eye_in_cd](animations.html#glass_favorite_eye_in_cd) | applied / prop_reveal | One rigid glass-and-hand cutout rises over the mouthless face. |
| [glass_flight_high_truckr_cc](animations.html#glass_flight_high_truckr_cc) | applied / parallax | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [glass_outro_high_out_dm](animations.html#glass_outro_high_out_dm) | applied / dolly_out | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [glass_pour_eye_in_cd_through](animations.html#glass_pour_eye_in_cd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [glass_pour_low_in_cd](animations.html#glass_pour_low_in_cd) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [glasses_clink_center](animations.html#glasses_clink_center) | applied / clink | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [hair_blend_high_orbitr_cc](animations.html#hair_blend_high_orbitr_cc) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [hair_signature_high_orbitr_cc](animations.html#hair_signature_high_orbitr_cc) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [hair_work_high_in_cd_through](animations.html#hair_work_high_in_cd_through) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hand_pov_garment_pov_in_mc](animations.html#hand_pov_garment_pov_in_mc) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hand_pov_item_pov_in_mc](animations.html#hand_pov_item_pov_in_mc) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hand_pov_pastry_pov_in_mc](animations.html#hand_pov_pastry_pov_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [hands_dough_top_hold](animations.html#hands_dough_top_hold) | needs matching layers / isolated action layers or corrected camera master | Existing art is oblique, not strict overhead; visitor-side access unproven. |
| [hands_during_top_hold](animations.html#hands_during_top_hold) | needs matching layers / isolated action layers or corrected camera master | Existing patient POV does not establish the required overhead angle. |
| [hands_garment_high_hold](animations.html#hands_garment_high_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [hands_griddle_high_hold](animations.html#hands_griddle_high_hold) | needs matching layers / isolated action layers or corrected camera master | Existing art implies restricted staff prep viewpoint. |
| [hands_guitar_high_hold](animations.html#hands_guitar_high_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hands_high_hold](animations.html#hands_high_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hands_stance_top_hold](animations.html#hands_stance_top_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hands_tool_top_hold](animations.html#hands_tool_top_hold) | applied / hold | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [hands_tool_top_hold_whipout](animations.html#hands_tool_top_hold_whipout) | applied / whip | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [hands_top_hold](animations.html#hands_top_hold) | needs matching layers / isolated action layers or corrected camera master | Existing art is oblique, not strict overhead; visitor-side access unproven. |
| [hands_work_high_hold](animations.html#hands_work_high_hold) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [hands_work_high_hold_whipout](animations.html#hands_work_high_hold_whipout) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [hands_work_high_in_cd](animations.html#hands_work_high_in_cd) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [hands_wrap_top_hold](animations.html#hands_wrap_top_hold) | needs matching layers / isolated action layers or corrected camera master | Existing art is oblique, not strict overhead; visitor-side access unproven. |
| [interior_pan](animations.html#interior_pan) | needs matching art / panorama | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [latte_top_in_cd](animations.html#latte_top_in_cd) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [latte_top_in_cd_whipout](animations.html#latte_top_in_cd_whipout) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [machine_low_in_mc_whipout](animations.html#machine_low_in_mc_whipout) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [menu_board_eye_truckr_mm](animations.html#menu_board_eye_truckr_mm) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [menu_board_low_tiltd_mm](animations.html#menu_board_low_tiltd_mm) | applied / tilt | One immutable painted image; deterministic camera window, no generated intermediate frames. |
| [menu_board_low_truckl_mm](animations.html#menu_board_low_truckl_mm) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [menu_desk_high_hold](animations.html#menu_desk_high_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [menu_event_low_in_cd](animations.html#menu_event_low_in_cd) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [menu_hours_low_out_dc](animations.html#menu_hours_low_out_dc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [menu_pricelist_eye_in_mc](animations.html#menu_pricelist_eye_in_mc) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [menu_pricelist_eye_out_dm](animations.html#menu_pricelist_eye_out_dm) | applied / dolly_out | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [menu_schedule_eye_in_mc](animations.html#menu_schedule_eye_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [menu_schedule_low_tiltd_mm](animations.html#menu_schedule_low_tiltd_mm) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [menu_score_low_out_dc](animations.html#menu_score_low_out_dc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [nails_accent_top_hold](animations.html#nails_accent_top_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [nails_tech_pov_hold](animations.html#nails_tech_pov_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [nails_turns_eye_hold](animations.html#nails_turns_eye_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [oven_tray_eye_in_mc](animations.html#oven_tray_eye_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [oven_tray_eye_in_md_through](animations.html#oven_tray_eye_in_md_through) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_counter_os_hold](animations.html#over_shoulder_counter_os_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_hands_os_in_cd](animations.html#over_shoulder_hands_os_in_cd) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_hands_os_in_mc](animations.html#over_shoulder_hands_os_in_mc) | applied / dolly_in | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [over_shoulder_machine_os_hold](animations.html#over_shoulder_machine_os_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_menu_os_in_mc](animations.html#over_shoulder_menu_os_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_rail_os_hold](animations.html#over_shoulder_rail_os_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [over_shoulder_till_os_in_md](animations.html#over_shoulder_till_os_in_md) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [pastry_break_eye_hold](animations.html#pastry_break_eye_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [pastry_tear_open](animations.html#pastry_tear_open) | needs matching layers / isolated action layers or corrected camera master | Needs separate hands/pastry halves over a fixed plate; source has baked-in background. |
| [person_barber_eye_hold](animations.html#person_barber_eye_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_curtain_low_reveal_dm](animations.html#person_curtain_low_reveal_dm) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [person_full_low_hold](animations.html#person_full_low_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_group_eye_hold](animations.html#person_group_eye_hold) | needs matching layers / isolated action layers or corrected camera master | Existing image exceeds two visible hands. |
| [person_host_eye_whip_mm](animations.html#person_host_eye_whip_mm) | applied / whip | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_mirror_eye_hold](animations.html#person_mirror_eye_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_mirror_eye_out_cm](animations.html#person_mirror_eye_out_cm) | applied / dolly_out | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_one_eye_hold](animations.html#person_one_eye_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_player_eye_out_dm](animations.html#person_player_eye_out_dm) | applied / dolly_out | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [person_process_pov_in_mc_through](animations.html#person_process_pov_in_mc_through) | applied / dolly_in | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_bite_top_hold](animations.html#plate_bite_top_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_high_orbitl_cc](animations.html#plate_high_orbitl_cc) | requires viewpoints / consistent perspective/pose keyframes | A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot. |
| [plate_kids_top_hold](animations.html#plate_kids_top_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_low_in_cd_through](animations.html#plate_low_in_cd_through) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [plate_low_in_cd_whipout](animations.html#plate_low_in_cd_whipout) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [plate_low_in_mc](animations.html#plate_low_in_mc) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [plate_sizzle_low_in_cd](animations.html#plate_sizzle_low_in_cd) | needs matching layers / isolated action layers or corrected camera master | Existing art has the wrong food/action and camera height. |
| [plate_spread_eye_out_dw](animations.html#plate_spread_eye_out_dw) | needs matching layers / isolated action layers or corrected camera master | Existing art looks down instead of from resource height. |
| [plate_spread_top_hold](animations.html#plate_spread_top_hold) | applied / hold | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_spread_top_out_cw](animations.html#plate_spread_top_out_cw) | applied / dolly_out | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_spread_top_out_dw](animations.html#plate_spread_top_out_dw) | applied / dolly_out | Camera movement/hold is illustrated. Independent finger or working actions are not synthesized. |
| [plate_yolk_high_in_cd](animations.html#plate_yolk_high_in_cd) | needs matching layers / isolated action layers or corrected camera master | Existing art is overhead instead of the required oblique high view. |
| [pov_door_entry](animations.html#pov_door_entry) | needs matching layers / isolated action layers or corrected camera master | Existing artwork cannot provide the required angle/action without new matching layers. |
| [rail_bottle_eye_truckr_mm](animations.html#rail_bottle_eye_truckr_mm) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [rail_dumbbell_eye_truckr_cc](animations.html#rail_dumbbell_eye_truckr_cc) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [rail_garment_eye_truckr_cc_whipout](animations.html#rail_garment_eye_truckr_cc_whipout) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [rail_garment_eye_truckr_mm](animations.html#rail_garment_eye_truckr_mm) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [rail_guitar_pov_truckr_mm](animations.html#rail_guitar_pov_truckr_mm) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [rail_shelf_eye_truckr_mm_whipout](animations.html#rail_shelf_eye_truckr_mm_whipout) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [room_changing_pov_reveal_cm](animations.html#room_changing_pov_reveal_cm) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_crowd_eye_panr_ww_whipout](animations.html#room_crowd_eye_panr_ww_whipout) | applied / pan | Image-plane panorama approximates camera yaw. The source artwork remains fixed. |
| [room_cupreveal_eye_reveal_dw](animations.html#room_cupreveal_eye_reveal_dw) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_dining_eye_reveal_cw](animations.html#room_dining_eye_reveal_cw) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_dining_eye_reveal_cw_whipout](animations.html#room_dining_eye_reveal_cw_whipout) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_eye_panl_ww](animations.html#room_eye_panl_ww) | needs matching art / panorama | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_eye_panr_ww_whipout](animations.html#room_eye_panr_ww_whipout) | applied / pan | Image-plane panorama approximates camera yaw. The source artwork remains fixed. |
| [room_game_pov_panl_mm_whipout](animations.html#room_game_pov_panl_mm_whipout) | needs matching layers / isolated action layers or corrected camera master | Existing audience and player exceed two visible hands. |
| [room_gym_eye_panr_ww](animations.html#room_gym_eye_panr_ww) | needs matching art / panorama | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_lesson_eye_reveal_cw](animations.html#room_lesson_eye_reveal_cw) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_lights_eye_hold](animations.html#room_lights_eye_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_park_high_panr_ww_whipout](animations.html#room_park_high_panr_ww_whipout) | needs matching art / panorama | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_ride_pov_in_wm](animations.html#room_ride_pov_in_wm) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_sauna_high_out_cw](animations.html#room_sauna_high_out_cw) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_shop_eye_out_cw](animations.html#room_shop_eye_out_cw) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_shop_eye_panr_mm](animations.html#room_shop_eye_panr_mm) | needs matching art / panorama | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_stage_low_in_wm_whipout](animations.html#room_stage_low_in_wm_whipout) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [room_treatment_eye_reveal_cm](animations.html#room_treatment_eye_reveal_cm) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [room_waiting_eye_reveal_cw](animations.html#room_waiting_eye_reveal_cw) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [selfie_bag_high_hold](animations.html#selfie_bag_high_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_bite_eye_in_mc](animations.html#selfie_bite_eye_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_bite_eye_out_cm](animations.html#selfie_bite_eye_out_cm) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_bite_reaction](animations.html#selfie_bite_reaction) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_close_eye_hold](animations.html#selfie_close_eye_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_close_high_hold](animations.html#selfie_close_high_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_one_high_hold](animations.html#selfie_one_high_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_reveal_eye_reveal_cc](animations.html#selfie_reveal_eye_reveal_cc) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [selfie_reveal_eye_reveal_cm](animations.html#selfie_reveal_eye_reveal_cm) | applied / reveal | Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses. |
| [selfie_sip_eye_in_mc](animations.html#selfie_sip_eye_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_sip_reaction](animations.html#selfie_sip_reaction) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_two_eye_hold](animations.html#selfie_two_eye_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [selfie_two_high_hold](animations.html#selfie_two_high_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [shelf_slide_left](animations.html#shelf_slide_left) | applied / pan | Fixed painting approximates camera translation; no new perspective is synthesized. |
| [sign_plate_eye_out_cm](animations.html#sign_plate_eye_out_cm) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [sign_tilt_down_reveal](animations.html#sign_tilt_down_reveal) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_bench_eye_out_dw](animations.html#table_bench_eye_out_dw) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_corner_pov_out_mw](animations.html#table_corner_pov_out_mw) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_desk_pov_in_mc](animations.html#table_desk_pov_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_outlets_high_tiltd_cc](animations.html#table_outlets_high_tiltd_cc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_seat_high_in_mc](animations.html#table_seat_high_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [table_treatment_eye_in_mc](animations.html#table_treatment_eye_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [talking_head_eye_level](animations.html#talking_head_eye_level) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [tap_pour_glass](animations.html#tap_pour_glass) | needs matching layers / isolated action layers or corrected camera master | Existing art shows cocktail pouring rather than a beer tap. |
| [tap_taps_low_tiltd_mm](animations.html#tap_taps_low_tiltd_mm) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [tools_closeup_hands](animations.html#tools_closeup_hands) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [tools_tray_top_hold](animations.html#tools_tray_top_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [topdown_bag_top_hold](animations.html#topdown_bag_top_hold) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [topdown_box_top_out_cm](animations.html#topdown_box_top_out_cm) | applied / dolly_out | Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing. |
| [topdown_first_top_hold_whipout](animations.html#topdown_first_top_hold_whipout) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [topdown_haul_top_out_dw](animations.html#topdown_haul_top_out_dw) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [topdown_kidstuff_high_in_cd_whipout](animations.html#topdown_kidstuff_high_in_cd_whipout) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [topdown_unwrap_top_in_cd](animations.html#topdown_unwrap_top_in_cd) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
| [tray_high_in_mc](animations.html#tray_high_in_mc) | needs matching art / single master and camera crop | Local mechanics are feasible, but no matching, individually verified source is available in this batch. |
