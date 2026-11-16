# API artwork coverage

2026-10-26. Live checks passed for all 178 guide hashes and all 304 per-step endpoints. The reviewed catalog and served watercolor subset have identical guide IDs.

Guide coverage: 96 watercolor and 82 original schematic. Step coverage: 131 watercolor and 173 schematic, because guide reuse is uneven.

## Bakery: Food review

| Step | Title | Guide | Served artwork | Replacement status |
|---|---|---|---|---|
| 1 | The dish | plate_low_in_cd_whipout | schematic | pending |
| 2 | Arrive | facade_eye_in_wm | watercolor | keyframes_reviewed |
| 3 | Order | over_shoulder_menu_os_in_mc | schematic | pending |
| 4 | First bite | selfie_bite_eye_in_mc | schematic | pending |
| 5 | Verdict | talking_head_eye_level | schematic | pending |

The exact reported pattern is expected from the current API: only Arrive has a reviewed watercolor replacement. Publishing all existing guide IDs did not finish the missing replacements. Completing this script requires four more matching guide sources and their animation exports. The talking-head replacement is also reused by 29 other steps, and the bite replacement by six other steps.

## Remaining original guides

| Guide | Step assignments | Artwork status |
|---|---|---|
| selfie_one_high_hold | 30 | pending |
| talking_head_eye_level | 30 | pending |
| selfie_bite_eye_in_mc | 7 | pending |
| selfie_sip_eye_in_mc | 4 | pending |
| selfie_two_high_hold | 4 | pending |
| sign_tilt_down_reveal | 4 | pending |
| hand_pov_pastry_pov_in_mc | 3 | pending |
| interior_pan | 3 | pending |
| pastry_break_eye_hold | 3 | pending |
| hands_dough_top_hold | 2 | pending |
| hands_griddle_high_hold | 2 | needs_revision |
| hands_top_hold | 2 | pending |
| hands_work_high_hold | 2 | pending |
| menu_schedule_eye_in_mc | 2 | pending |
| over_shoulder_counter_os_hold | 2 | pending |
| over_shoulder_hands_os_in_cd | 2 | pending |
| pastry_tear_open | 2 | pending |
| room_lights_eye_hold | 2 | pending |
| selfie_bag_high_hold | 2 | pending |
| selfie_bite_eye_out_cm | 2 | pending |
| selfie_bite_reaction | 2 | pending |
| bag_handoff_low_hold | 1 | needs_revision |
| cup_pour_eye_hold | 1 | needs_revision |
| cup_shot_eye_in_cd_through | 1 | needs_revision |
| door_sauna_eye_in_mc_through | 1 | needs_revision |
| glass_build_eye_hold | 1 | needs_revision |
| hands_during_top_hold | 1 | pending |
| hands_work_high_hold_whipout | 1 | pending |
| hands_work_high_in_cd | 1 | pending |
| hands_wrap_top_hold | 1 | pending |
| menu_event_low_in_cd | 1 | pending |
| menu_hours_low_out_dc | 1 | pending |
| menu_schedule_low_tiltd_mm | 1 | pending |
| menu_score_low_out_dc | 1 | pending |
| nails_accent_top_hold | 1 | pending |
| nails_tech_pov_hold | 1 | pending |
| nails_turns_eye_hold | 1 | pending |
| oven_tray_eye_in_mc | 1 | pending |
| oven_tray_eye_in_md_through | 1 | pending |
| over_shoulder_machine_os_hold | 1 | pending |
| over_shoulder_menu_os_in_mc | 1 | pending |
| over_shoulder_rail_os_hold | 1 | pending |
| person_curtain_low_reveal_dm | 1 | pending |
| person_group_eye_hold | 1 | pending |
| plate_high_orbitl_cc | 1 | pending |
| plate_low_in_cd_through | 1 | pending |
| plate_low_in_cd_whipout | 1 | pending |
| plate_low_in_mc | 1 | pending |
| plate_sizzle_low_in_cd | 1 | pending |
| plate_spread_eye_out_dw | 1 | pending |
| plate_yolk_high_in_cd | 1 | pending |
| pov_door_entry | 1 | pending |
| room_eye_panl_ww | 1 | pending |
| room_game_pov_panl_mm_whipout | 1 | pending |
| room_gym_eye_panr_ww | 1 | pending |
| room_park_high_panr_ww_whipout | 1 | pending |
| room_ride_pov_in_wm | 1 | pending |
| room_sauna_high_out_cw | 1 | pending |
| room_shop_eye_out_cw | 1 | pending |
| room_shop_eye_panr_mm | 1 | pending |
| room_stage_low_in_wm_whipout | 1 | pending |
| selfie_close_eye_hold | 1 | pending |
| selfie_close_high_hold | 1 | pending |
| selfie_sip_reaction | 1 | pending |
| selfie_two_eye_hold | 1 | pending |
| sign_plate_eye_out_cm | 1 | pending |
| table_bench_eye_out_dw | 1 | pending |
| table_corner_pov_out_mw | 1 | pending |
| table_desk_pov_in_mc | 1 | pending |
| table_outlets_high_tiltd_cc | 1 | pending |
| table_seat_high_in_mc | 1 | pending |
| table_treatment_eye_in_mc | 1 | pending |
| tap_pour_glass | 1 | pending |
| tap_taps_low_tiltd_mm | 1 | pending |
| tools_closeup_hands | 1 | pending |
| tools_tray_top_hold | 1 | pending |
| topdown_bag_top_hold | 1 | pending |
| topdown_first_top_hold_whipout | 1 | pending |
| topdown_haul_top_out_dw | 1 | pending |
| topdown_kidstuff_high_in_cd_whipout | 1 | pending |
| topdown_unwrap_top_in_cd | 1 | pending |
| tray_high_in_mc | 1 | pending |

The current app source has the asset-path cache correction, but an installed app binary was not inspected. It also defaults to model mode; APNG artwork is displayed in Animation mode. These are separate display/cache possibilities for a guide that already has a reviewed replacement, and are not needed to explain this Food review example.
