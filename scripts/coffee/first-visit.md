# first-visit

## Guided v0 (2026-11-10, p0/tasks/09)

Story: Coffee: you walk into {venue.name}, order what the barista suggests, show the cup on your table, take the first sip and say why you would come back. Dining: you walk in, read the menu, show the plate when it lands, take the first forkful, show the room from your seat and say why you would come back.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| entrance | coffee, dining | easy | the hook spoken at the door | entrance_door_low, entrance_sign_tilt, entrance_walk_in | - | First time at {venue.name}. Let's see if it's worth the hype. | {venue.name} | The front of the place, so people can find it. |
| counter | coffee | easy | the order said aloud while one slide passes the counter | counter_over_shoulder, counter_edge_to_pass | - | Asking the barista what first timers should order here. | Ordering at the counter | Where you order, with the menu or the barista in view. |
| menu | dining | easy | what to order, said over a short move above the menu | menu_card_top, menu_card_push | - | Asking what the kitchen here is known for. | The menu | The menu on the table, with the dish you are ordering. |
| drink | coffee | complex | silent visual beat: the orbit or slide needs attention | steam_orbit_eye, steam_slide_pull_out | - | (none) | (none) | Your drink on the table, close enough to see the steam. |
| plate | dining | complex | silent visual beat on the shared example plate | plate_high_orbit, plate_tissue_slide | plate_rise_overhead | (none) | (none) | The dish on the table, close enough to see what it is. |
| sip | coffee | easy | the reaction to the lens | sip_selfie_eye, sip_high_lean, sip_friend_side | - | Okay, first sip. Here's how it tastes. | First sip | You taking the first sip, your face and the cup in frame. |
| forkful | dining | easy | the reaction to the lens | bite_selfie_eye, bite_pip_dish, bite_friend_three_quarter | - | First forkful of what they told me to order. Okay. | First bite | You taking the first bite, your face and the food in frame. |
| room | dining | complex | silent visual beat: the reveal from behind the cup or the plant | room_reveal_cup, room_reveal_plant | - | (none) | (none) | The room from your seat, so people see where they would sit. |
| verdict | coffee, dining | easy | why to come back, to the lens | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | That's {venue.name}. Here's why I'd come back. | {venue.name} | You, looking at the lens, saying why you would come back. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.

