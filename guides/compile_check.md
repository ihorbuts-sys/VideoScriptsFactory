# Compile check

Pinned `live` steps against the compiler's own reading of the camera timeline (follow actions only; holds and stills are authored). A difference is not an error: the pinned list is what ships, the heuristic reading is listed so a wrong camera path shows up.

Scenes: 178, heuristic reads differently: 5, reused scenes whose steps differ from the kit: 0

- `facade_line_eye_panr_ww_whipout`: pinned [('follow', 'pan', 'right'), ('follow', 'whip', 'right')] / heuristic [('follow', 'truck', 'right'), ('follow', 'whip', 'right')]
- `glass_pour_eye_in_cd_through`: pinned [('follow', 'dolly_in', None)] / heuristic [('follow', 'tilt', 'down')]
- `pov_door_entry`: pinned [('follow', 'dolly_in', None), ('follow', 'dolly_in', None)] / heuristic [('follow', 'dolly_in', None)]
- `room_crowd_eye_panr_ww_whipout`: pinned [('follow', 'pan', 'right'), ('follow', 'whip', 'right')] / heuristic [('follow', 'truck', 'right'), ('follow', 'whip', 'right')]
- `room_eye_panr_ww_whipout`: pinned [('follow', 'pan', 'right'), ('follow', 'whip', 'right')] / heuristic [('follow', 'truck', 'right'), ('follow', 'whip', 'right')]
