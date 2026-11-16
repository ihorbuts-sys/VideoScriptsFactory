"""Publish the composition and static-take review without changing guide assets.

Recommendations are editorial judgments from 178 four-frame strip reviews,
descriptions, script assignments, live validation code and 178 timed APNG checks.
"""
import collections
import hashlib
import html
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

PROFILES={
    'room_reveal':dict(title='Room reveals',techniques=['foreground framing','linear perspective','tonal separation','symmetry when the room supports it'],
        observation='The foreground reveal works, but the final room often reads as a small isolated painting with similar detail strength across its depth.',
        film='From a visitor-accessible doorway or aisle, use one jamb or station edge as a near frame. Let a floor, counter or bench line lead to one clear destination. Finish with the chair, table or reception area unobstructed. Use a centered axis only when the architecture supports it and the camera is not reflected in a mirror.',
        animation='Keep the current reveal direction and angle. Compose the final room first, then its blocker. Separate near edge, focal subject and quieter distance with line weight and pigment value; keep final global alpha at 0.5. A transparent painting margin is not negative space in the recorded room.',
        payoff='High',effort='Medium: matching room composition and depth layers'),
    'interior':dict(title='Rooms and environmental shots',techniques=['linear perspective','foreground/midground/background','tonal separation','visual hierarchy'],
        observation='The move often traverses equal-detail scenery without a clearly preferred opening and landing composition.',
        film='Choose a public position with a near edge, a useful middle-distance subject and a deeper room line. Start and finish on a specific table, rack, stage or window-lit area. Keep bright windows from turning the subject into an unreadable silhouette. High views must come from public visitor platforms.',
        animation='Mark strong opening and landing frames. Reduce distant detail, preserve one coherent vanishing structure and use actual depth layers only where source art supports them. Preserve the prescribed pan, push or pull; a flat panorama does not create new 3D perspective.',
        payoff='High',effort='Medium to high: several matching room masters are missing'),
    'display':dict(title='Repeated shelves, rails and bars',techniques=['rhythm','variation within repetition','diagonal leading lines','selective emphasis'],
        observation='Repeated objects create rhythm already, but several traversals give each object equal emphasis and no clear visual destination.',
        film='Keep the camera at the specified height. Let repeated shelves, rims or handles lead toward the chosen item or counter section. Use one natural gap or distinctive object to break the pattern, then let the existing final hold make it readable. Keep the camera on the customer side.',
        animation='Retain the current measured speed, including the deliberately gentle bar truck. Compose the chosen item at the landing frame; avoid arbitrarily enlarging every move. Use depth-separated layers only for real near/far differences, not a fake orbit.',
        payoff='High',effort='Low to medium for current masters; new art if the landing item is absent'),
    'food':dict(title='Food and texture heroes',techniques=['asymmetrical balance','visual hierarchy','figure/background separation','motivated diagonals'],
        observation='Several shots begin with a small centered food island or grow a still action picture without establishing a clear hero and quiet supporting background.',
        film='Keep the prescribed low, high or resource-height angle. Give the food a clean silhouette against a simpler background and place the cut face or texture where the move ends. At your own table, use available side light and fewer competing objects. Keep a centered subject for through-crops and orbits that require it.',
        animation='Plan a recognizable start and a specific texture landing. Make cut faces and utensil directions lead the eye. Add food/hand action as independent layers where required; enlarging the whole painting does not show a tear, cut or pour. Use only visitor-accessible viewpoints.',
        payoff='High',effort='Medium; several plate masters need the correct angle and subject first'),
    'drink':dict(title='Drink heroes',techniques=['negative space for the action','rim/background separation','diagonal action path','tonal separation'],
        observation='Some drink compositions are already strong, but busy bar detail can compete with the glass; held takes can omit steam or landing action.',
        film='At the stated glass or cup height, put a simpler or contrasting background behind the rim. Use public-side window or bar light to reveal the liquid without blowing out the glass. Leave space above a pouring stream or steam, and enough room for the handle. An orbit keeps its subject centered.',
        animation='Keep the cup/glass geometry fixed. Animate only the intended pour, foam, steam or hand layer over a locked background. Do not add a generic camera push to a prescribed hold. Preserve the existing 50% final alpha and single pigment.',
        payoff='High',effort='Low to medium for rigid props; higher for liquid/contact action'),
    'flatlay':dict(title='Tabletop layouts',techniques=['asymmetrical balance','grouping and hierarchy','diagonal flow','functional negative space'],
        observation='Centered flatlays are readable, but some spread shots only reveal one hero dish rather than a deliberately arranged group.',
        film='Keep the specified top-down or high angle. Make one dish or item dominant; place a small number of supporting objects along a balanced diagonal, with clear gaps between their silhouettes. Keep the active hand path clear and preserve space for the script text. Arrange only your own items.',
        animation='Compose both the tight crop and the complete final arrangement. A pull-out should reveal useful relationships rather than a bigger empty margin. Separate arriving plates or items from the fixed tabletop when the description calls for placement.',
        payoff='High',effort='Medium: secondary items and clean table layers may need new source art'),
    'portrait':dict(title='Portraits and spoken holds',techniques=['headroom and hierarchy','background separation','balanced negative space','asymmetry in the background'],
        observation='The two most reused selfie guides remain original schematics; the general staff portrait also carries a bakery-specific background into other contexts.',
        film='Keep the face within the current centered face slot, with clear headroom and a quieter background. Avoid poles, shelves or lights appearing to grow out of the head. Use a visitor-facing view and available soft light. Balance the background or held object rather than forcing the face onto a third.',
        animation='Use a context-appropriate mouthless portrait and a clear subject silhouette. A spoken guide can remain still; do not invent lip, blink, breathing or camera motion just to make it animate. Off-center face targets require matching validator and ghost changes.',
        payoff='High reach; moderate individual-shot payoff',effort='Medium: new shared portrait artwork; validator work only for off-center variants'),
    'paired':dict(title='Before/after and result comparisons',techniques=['matched framing','repeatable symmetry','silhouette separation','continuity'],
        observation='Aesthetic framing is useful only if before and after keep comparable crop, camera distance, angle and lighting. Some current instructions disagree about whether the subject turns.',
        film='Record the before and after from the same visitor position, with the same lens, head size, eye line and lighting. Keep the hair, brows or garment boundary clear against the background. If the comparison includes a turn, show corresponding angles in both takes.',
        animation='Build paired guides from one placement specification. Preserve centered turns and genuine orbit viewpoints. Do not improve the after by changing light or angle so much that the comparison stops being meaningful. Resolve source/step disagreements before changing the art.',
        payoff='High',effort='Medium to high: paired sources or consistent pose views'),
    'manual':dict(title='Hands, tools and craft',techniques=['action hierarchy','diagonal tool path','foreground framing','tonal separation'],
        observation='The contact point should dominate. Frozen working hands or a tool from the wrong service cannot teach the intended shot.',
        film='Keep the assigned camera angle. Frame the relevant hand, tool or handoff contact, with the surrounding work area quieter. Film from your own workstation or the public side; never move behind a staff kitchen, till or restricted prep bench.',
        animation='Use a fixed clean background and stable tool/hand cutouts. Show one correct contact action, not a moving whole scene. Articulation needs consistent hand poses; do not warp anatomy. Shared camera mechanics may need separate subject artwork for different services.',
        payoff='High when the action is currently missing',effort='Medium to high: clean plates, task variants and articulated poses'),
    'readable':dict(title='Prices, labels and useful information',techniques=['visual hierarchy','alignment','quiet negative space','controlled diagonals'],
        observation='The main job is locating and reading one meaningful line; decorative imbalance or excess motion can make the result worse.',
        film='Keep the assigned angle and make the actual price, name or schedule line readable. Avoid glare, competing signs and fingertips covering the information. Use the existing hold; leave space around the selected line instead of filling every corner.',
        animation='Let a pointer arrive once and settle when requested. Keep the card and background locked. Maintain the same target through the push or tilt. Generated sketch text remains schematic; real footage must show the venue’s actual words.',
        payoff='Medium aesthetic payoff; high practical value',effort='Low to medium; a clean card and separate pointer may be needed'),
    'arrival':dict(title='Entrances and venue identity',techniques=['architectural symmetry','frame within frame','linear perspective','negative space for identity'],
        observation='Centered entrances suit the camera move already; the main opportunity is a purposeful axis and an uncluttered sign-to-door relationship.',
        film='Use a public pavement or entrance position. Align door edges and verticals without changing the specified camera elevation. Center a genuinely symmetrical entrance; use balanced asymmetry when the facade is irregular. Keep the important name and the walking path readable.',
        animation='Keep one coherent facade and door axis. Avoid perspective changes from independently generated facade views. Door opening needs a real foreground/background or hinge plan. Preserve quiet end-card holds; do not add a move solely because a still looks plain.',
        payoff='Medium to high',effort='Low for crop/alignment; high for continuous door opening'),
    'workspace':dict(title='Workspaces and environmental details',techniques=['leading edges','asymmetrical balance','foreground/background separation','visual hierarchy'],
        observation='The useful object and the surrounding context need different visual weights so the viewer immediately knows why this space matters.',
        film='From a public seat, aisle or permitted visitor position, use a bench or table edge to lead toward the seat, instrument, outlet or equipment. Keep the specified angle. Remove only your own clutter and keep the important object separate from background tangents.',
        animation='Choose a meaningful landing object. Preserve the intended push, pull or tilt and give the context a quieter line/value treatment. Do not create a high or low camera view by cropping art from a different angle.',
        payoff='Medium to high',effort='Medium: several matching environmental masters are missing'),
    'retail_hero':dict(title='A picked product',techniques=['figure/background separation','asymmetrical balance','directional hand framing','hierarchy'],
        observation='The picked object and its tag should read before the rest of the shop; a busy rail can compete with both.',
        film='Keep the product at the specified POV distance and angle, against a quieter visitor-side background. Use the holding hand as a natural frame while keeping the product silhouette and tag visible. Keep the pick recognizable through the approach.',
        animation='Use the same product master for the entire push. Animate the holding hand only if the description requests it. Preserve the tag landing and avoid adding another object merely to fill negative space.',
        payoff='High',effort='Low to medium for current matching masters'),
    'body':dict(title='Full-body demonstration',techniques=['functional negative space','silhouette separation','repeatable framing','motion rhythm'],
        observation='The camera is correctly held still, but the current source freezes a kettlebell pose instead of showing a rep and is also reused for a sauna doorway walk.',
        film='Keep the phone propped at the specified low position. Leave room for the entire movement, including the highest hand position and planted feet. Use a clear background and keep other visitors outside the frame. The sauna step is a separate solo doorway action.',
        animation='Keep the camera, floor and foot contacts fixed. Use consistent articulated poses for a real rep; do not slide the whole body up/down. A doorway walk needs a different scene and pose sequence, not the gym illustration.',
        payoff='High because the action is the shot',effort='High: consistent pose artwork and task-specific variants'),
    'clink':dict(title='Balanced two-prop action',techniques=['symmetry','converging diagonals','negative space','rhythm through contact and hold'],
        observation='The centered meeting point and two-hand limit already make the action clear. This is a strength to preserve.',
        film='Keep the phone still and the meeting point centered. Leave room for both glasses and let the hands guide the eye inward. Hold briefly after contact; avoid cropping the rims.',
        animation='Keep the existing stable sprites, centered contact and two visible hands. Refine contact geometry only if needed; arbitrary asymmetry or camera motion would weaken the instruction.',
        payoff='Low additional payoff; preserve current strength',effort='Low'),
    'reaction':dict(title='Product-to-person reaction',techniques=['foreground/background relationship','action clearance','headroom','continuity'],
        observation='The product entering the frame should lead to the person without hiding the eyes or making the guide dependent on drawn mouths.',
        film='Keep the face in its validated slot. Let the food or drink enter from below with clear space around the eyes. Preserve the prescribed push or pull, and keep the same product visible across the cut.',
        animation='Separate the product/hand from the mouthless face; keep their identities stable. Show the intended approach or withdrawal without drawing lips or adding extra hands. Do not move the whole portrait to imitate a hand action.',
        payoff='Medium to high',effort='Medium to high: most matching reaction artwork is pending'),
}

# Each entry is a concrete missing action, not a generic request for more motion.
ACTIONS={
    'card_menu_top_hold':('One pointer enters, lands on the intended line, and settles. Keep the page fixed.','Separate page and one hand; clean page art needed.','Medium'),
    'card_pricelist_top_hold':('One finger reaches the starting-price line and holds beside it without covering it.','Separate card/pointer; retain the same line through the hold.','Medium'),
    'glass_drink_high_hold':('Lower the existing glass/hand onto a fixed bar, then settle once. Keep the high camera fixed.','Isolate the matching glass and hand over a clean bar; preserve glass identity.','Medium'),
    'hands_guitar_high_hold':('Show one short, correct pluck or key press, then settle. Keep the instrument and camera fixed.','Consistent finger/wrist poses and contact geometry; do not warp a still hand.','High'),
    'hands_high_hold':('Show the task-specific tool or grip action while the background stays fixed.','Resolve the three incompatible task contexts before creating hand/tool variants.','High'),
    'hands_stance_top_hold':('Move the two feet into the demonstrated stance once, then hold.','Separate shoe cutouts over a clean floor; do not move the floor with the feet.','Medium'),
    'hands_tool_top_hold':('Show one tool contact or short correct working stroke. Keep the overhead view fixed.','Clean work surface and consistent hand/tool articulation.','High'),
    'person_barber_eye_hold':('Show the clipper climbing the intended side while the client, chair and camera stay fixed.','Separate clipper/hand from the head; retain safe anatomy and the same hair outline.','High'),
    'person_full_low_hold':('Show one complete rep with planted feet; use a separate solo doorway-walk variant for the sauna.','Consistent articulated body poses; mirrored motion must not be invented from a flat slide.','High'),
    'person_mirror_eye_hold':('Show the actual outfit turn with a corresponding reflection, then hold.','Consistent front/side poses and physically corresponding reflection; camera stays fixed.','High'),
    'plate_bite_top_hold':('Have the existing hand reach for the glass while the plate and table stay fixed.','Separate hand/glass and table layers; keep the glass and food in the same positions until touched.','Medium'),
    'plate_kids_top_hold':('Bring the plate into its final position once, release/withdraw the hand, and hold.','Matching plate plus at most two hands over a clean table.','Medium'),
    'plate_spread_top_hold':('Let supporting dishes enter around the lunch plate, then hold the finished arrangement.','Fixed hero plate/table plus a few matching secondary dish cutouts; real gaps between objects.','Medium'),
    'cup_eye_hold_whipout':('Add a subtle painted steam layer rising above the fixed cup before the existing exit whip.','Separate AI-painted steam cutout; no procedural line illustration or whole-scene drift.','Low to medium'),
    'hands_tool_top_hold_whipout':('Show the described incorrect technique in the held take, then retain the existing whip.','Task-specific wrong/right hand/tool poses; do not flip the correct source to fake an incorrect action.','High'),
}

HOLD_REASONS={
    'card_label_high_hold_whipout':'The label needs a readable held take; the exit whip already supplies motion.',
    'card_receipt_top_hold':'The total should be still and readable. Improve crop/glare guidance, not camera motion.',
    'card_tag_high_hold':'The tag settles after a flick. A quiet hold is appropriate.',
    'facade_eye_hold':'The storefront is the end-card background; preserve usable negative space and steadiness.',
    'facade_window_pov_hold':'The purpose is a stable ordering viewpoint. An optional small gesture can help, but speech need not be animated.',
    'hands_garment_high_hold':'The pick/tag is deliberately held after the flick; composition and readability matter more than added movement.',
    'menu_desk_high_hold':'The price/booking line needs a stable frame. Preserve its hold.',
    'person_host_eye_whip_mm':'The entry whip already lands on the host. Keep the subsequent spoken hold steady.',
    'person_one_eye_hold':'Talking is represented by a stable mouthless figure; do not add artificial lip or camera animation.',
}

LEGACY_ACTIONS={
    'bag_handoff_low_hold':'Lower the matching tray and two staff hands toward the visitor lens over a fixed public-side window; preserve the low view.',
    'cup_pour_eye_hold':'First correct cup-versus-plate subject mismatch, then animate the sauce stream and contact on the same plate at resource height.',
    'glass_build_eye_hold':'Keep the glass silhouette fixed and show the intended liquid/layer levels building; preserve the fixed camera.',
    'hands_dough_top_hold':'Show one anatomically consistent fold at a visitor-accessible own table or public demonstration position, with the overhead camera fixed.',
    'hands_griddle_high_hold':'Use a public viewing position first; show food/heat action independently of the fixed griddle and camera.',
    'hands_top_hold':'Show the correct plating hand/contact action from an allowed visitor-side demonstration or own table; do not enter staff prep space.',
    'hands_wrap_top_hold':'Show one clear fold of the actual wrapping material with two consistent hands; keep the overhead background fixed.',
    'hands_work_high_hold_whipout':'During the held first-service shot, show the actual job/tool contact if that script action requires it; keep the camera fixed and retain the exit whip.',
    'nails_accent_top_hold':'Let a small painted highlight move across one stable nail; keep nail shape, hand and camera fixed.',
    'nails_tech_pov_hold':'Move the brush over the same nail in a controlled stroke; keep the patient hand and camera fixed, with schematic cosmetics.',
    'nails_turns_eye_hold':'Use consistent hand-angle poses for the three requested turns; do not flip or distort one flat hand.',
    'over_shoulder_counter_os_hold':'Show the cup handoff with separate hands/cup from the visitor side; preserve the fixed camera and hand limit.',
    'over_shoulder_machine_os_hold':'Show a real tamp/lock contact action from the customer-side or public demonstration position; match the actual tool.',
    'over_shoulder_rail_os_hold':'Move the selected garment and one coherent hand out from a fixed rail; stop with a clear product silhouette.',
    'pastry_break_eye_hold':'Open the pastry halves with two consistent hands and a fixed background; preserve crumb identity and the eye-level angle.',
    'person_group_eye_hold':'Show one small reaction gesture or nod from consistent poses, keeping every other hand hidden and faces mouthless.',
    'room_lights_eye_hold':'Keep the dim public-side room still and animate a small, task-correct baker action in its focal area.',
    'selfie_bite_reaction':'Move the same food/hand toward the mouthless face with eye clearance; do not animate lips or move the whole portrait.',
    'tap_pour_glass':'Keep tap/glass geometry fixed while the stream and foam level change; film from the customer side.',
    'tools_tray_top_hold':'Rotate/translate a separate brush in the same bowl while the tray and overhead camera stay fixed.',
    'topdown_bag_top_hold':'Place a small number of matching items into fixed positions one at a time, with no more than two visible hands.',
    'topdown_first_top_hold_whipout':'Show one hand taking the first item during the held take; keep the table fixed, then retain the exit whip.',
}
LEGACY_HOLDS={
    'hands_during_top_hold':'Resting hands are intentionally still; a treatment action should not be invented.',
    'hands_work_high_hold':'The finished result repeats the problem framing and is intentionally held for comparison.',
    'selfie_close_eye_hold':'The before brows/eyes need a steady repeatable comparison crop.',
    'selfie_close_high_hold':'The spoken price/end-card needs a readable steady close portrait.',
    'selfie_one_high_hold':'A spoken verdict/price hold can stay still; improve portrait composition and source artwork.',
    'selfie_two_eye_hold':'Two-person spoken framing can stay still; keep both faces readable.',
    'selfie_two_high_hold':'The shared spoken hold needs stable two-person framing, not an added camera move.',
    'talking_head_eye_level':'Very small schematic changes do not justify extra camera motion for a spoken hold.',
}

SPECIAL={
    'bar_low_truckr_mm':('The low panorama now moves coherently, but bottles, rail and stools have similar detail weight.','Keep the deliberate 75 px rightward camera crop. Use the counter edge as a leading diagonal and quieter distant bottles; choose a clear bar section at the landing.'),
    'chair_reveal_frame':('The wall reveals a chair cleanly, but the final chair/mirror composition has a small footprint and no explicit hierarchy.','Use the station or doorway as a natural frame and a floor/bench edge to lead to the chair. Avoid an on-axis mirror view that exposes the camera; finish with the chair fully readable.'),
    'room_dining_eye_reveal_cw':('The reveal works; the final dining area needs a clearer focal table and depth hierarchy.','Compose one focal table first, a near doorway edge second, and a lighter/quieter distance third. Retain the existing camera height and reveal direction.'),
    'room_cupreveal_eye_reveal_dw':('The foreground cup establishes scale, but a busy room can be revealed without a clear place for the eye to land.','Let the cup uncover a specific visitor table or group silhouette. Keep foreground, focal middle distance and far windows distinct; do not reveal every corner at equal contrast.'),
    'room_eye_panr_ww_whipout':('The panorama is stable; the move can feel like a survey unless the opening and destination are composed.','Open on a window-lit table and land on the creator’s own table. Use converging table/floor edges and preserve the existing whip direction.'),
    'glass_flight_high_truckr_cc':('The current near/mid/far glass diagonal and different speeds already show rhythm and parallax.','Preserve the current depth order. Only refine the dark/light progression and ensure a clear final rim silhouette; do not replace this with a generic centered row.'),
    'cup_eye_orbitr_cc':('The cup-height view and centered handle reveal already teach a real orbit.','Keep the centered orbit target and clear handle silhouette. Improve supporting background/tonal separation without pushing the cup onto a third or simulating new sides from one flat image.'),
    'latte_top_in_cd':('The diagonal pitcher-to-cup relationship already directs the eye effectively.','Preserve that diagonal and the overhead angle. Improve cup/background separation and ensure any future pour animation changes liquid/action layers, not the cup geometry.'),
    'latte_top_in_cd_whipout':('The pour/cup diagonal is strong; the exit is already clear.','Preserve the diagonal and make the initial latte art readable. Do not add a second arbitrary motion before the whip.'),
    'glasses_clink_center':('Centered convergence, stable glass cutouts and exactly two hands are already a good composition.','Preserve the symmetry and contact hold; check rim contact rather than forcing asymmetry.'),
    'plate_spread_top_out_cw':('The pull-out currently expands a one-plate/two-cup painting; it does not demonstrate a fuller table grouping.','Keep one hero plate and add a small number of secondary dishes in a balanced diagonal. The end should reveal useful table relationships, not just more transparent margin.'),
    'plate_spread_top_out_dw':('The start is a strong texture detail, but the wider end still has one main plate.','Make the full spread a composed landing with one dominant dish, secondary dishes and clear gaps. Keep the same overhead perspective and dish identity.'),
    'talking_head_eye_level':('This original schematic serves 30 steps and remains a large gap in the approved watercolor presentation.','Create a reusable mouthless head-and-shoulders composition with clear headroom, quiet background and centered face validation; use background asymmetry rather than an off-center face.'),
    'selfie_one_high_hold':('This original schematic serves another 30 steps, often price or verdict lines.','Keep the assigned slightly high camera and centered face slot. Compose the held item below the eyes and balance the background around text/PiP needs without adding camera movement.'),
    'person_one_eye_hold':('The current baker/pastry-counter master is shared by ten steps including a coach, clinician, stylist and shop staff.','Retain the common portrait mechanics but use neutral or context-specific visitor-side backgrounds and the correct held prop; do not force bakery scenery into every service.'),
    'cup_pour_eye_hold':('The script/description calls for sauce on a plate, while the served original schematic still depicts a cup.','Resolve the plated-food subject and resource-height camera first. Then use the pour path and a quiet background for hierarchy; never copy the incorrect cup composition.'),
    'before_front_back':('Both assigned before steps say to keep still, while the guide description and artwork turn the head front to back.','Agree on a repeatable comparison first. A held before needs a matching held after; a turn needs corresponding angles in the after. Keep position, crop and lighting consistent.'),
    'over_shoulder_hands_os_in_mc':('One hair/scissors master is shared by five steps, including plating, burger assembly and non-hair craft. Two script positions ask for the cook’s staff-side shoulder.','Reuse camera mechanics only. Create task-appropriate artwork and visitor-side food variants; do not frame from behind a restricted kitchen or prep bench. Then emphasize the correct tool/contact point.'),
    'hands_high_hold':('A mortar/pestle picture is shared by a repair/desk task, a first lesson and a gym grip.','Split subject artwork by task before styling the action. The camera can remain common; the tool, hand contact and background must match the actual step.'),
    'person_full_low_hold':('A frozen gym kettlebell pose is also assigned to walking into a sauna; it shows neither a rep nor a doorway walk.','Separate the gym and sauna scenes, then show their actual actions from the existing low fixed-camera viewpoint.'),
}

P0={'before_front_back','over_shoulder_hands_os_in_mc','hands_high_hold','person_full_low_hold','cup_pour_eye_hold'}
P1=set(ACTIONS)|{'chair_reveal_frame','bar_low_truckr_mm','room_dining_eye_reveal_cw','room_dining_eye_reveal_cw_whipout','room_cupreveal_eye_reveal_dw','room_eye_panr_ww_whipout','room_lesson_eye_reveal_cw','room_treatment_eye_reveal_cm','room_waiting_eye_reveal_cw','plate_spread_top_out_cw','plate_spread_top_out_dw','burger_cut_high_in_cd_through','burger_low_in_mc','talking_head_eye_level','selfie_one_high_hold','selfie_reveal_eye_reveal_cc','selfie_reveal_eye_reveal_cm','person_one_eye_hold'}


def profile(gid):
    if gid=='glasses_clink_center':return 'clink'
    if gid in {'before_front_back','selfie_close_eye_hold','selfie_reveal_eye_reveal_cc','selfie_reveal_eye_reveal_cm','person_curtain_low_reveal_dm','person_mirror_eye_hold','person_mirror_eye_out_cm'} or gid.startswith(('hair_','hands_work_')):return 'paired'
    if gid.startswith(('selfie_bite','selfie_sip')):return 'reaction'
    if gid=='person_full_low_hold':return 'body'
    if gid.startswith('selfie_') or gid in {'talking_head_eye_level','person_one_eye_hold','person_host_eye_whip_mm','person_group_eye_hold'}:return 'portrait'
    if gid=='chair_reveal_frame' or gid.startswith(('room_changing','room_dining','room_lesson','room_treatment','room_waiting')):return 'room_reveal'
    if gid.startswith('room_') or gid=='interior_pan':return 'interior'
    if gid.startswith(('card_','menu_')) or gid=='table_outlets_high_tiltd_cc':return 'readable'
    if gid.startswith(('bar_','case_','rail_')) or gid in {'shelf_slide_left','glass_flight_high_truckr_cc','facade_line_eye_panr_ww_whipout','tap_taps_low_tiltd_mm'}:return 'display'
    if gid.startswith(('door_','facade_','sign_')) or gid=='pov_door_entry':return 'arrival'
    if gid.startswith(('topdown_','plate_spread_top')) or gid in {'plate_bite_top_hold','plate_kids_top_hold','details_salon_high_whip_dd_whipout'}:return 'flatlay'
    if gid=='cup_pour_eye_hold' or gid.startswith(('burger_','plate_','pastry_','oven_','tray_')) or gid=='hand_pov_pastry_pov_in_mc':return 'food'
    if gid.startswith(('cup_','glass_','latte_')) or gid=='tap_pour_glass':return 'drink'
    if gid.startswith('hand_pov_'):return 'retail_hero'
    if gid.startswith(('hands_','over_shoulder_','nails_','tools_')) or gid in {'bag_handoff_low_hold','counter_barista_side','person_barber_eye_hold','person_player_eye_out_dm','person_process_pov_in_mc_through'}:return 'manual'
    if gid.startswith(('table_','machine_')):return 'workspace'
    raise ValueError('Unclassified guide: '+gid)


def main():
    inventory=json.loads((HERE/'checks/composition/inventory.json').read_text())
    measurements=json.loads((HERE/'checks/composition/motion-measurements.json').read_text())
    measured={r['id']:r for r in measurements['guides']}
    ready=set(json.loads((HERE/'animations/index.json').read_text())['guides'])
    records=[]
    for index,entry in enumerate(inventory):
        gid=entry['id'];key=profile(gid);p=PROFILES[key];metric=measured.get(gid)
        scenario=json.loads((ROOT/'guides/scenarios'/(gid+'.json')).read_text())
        anchor_kind=scenario.get('anchor',{}).get('kind')
        action=ACTIONS.get(gid);hold=HOLD_REASONS.get(gid)
        state='missing_subject_action' if action else ('intentional_hold' if hold else ('visible_change' if gid in ready else ('legacy_action_candidate' if gid in LEGACY_ACTIONS else ('legacy_intentional_hold' if gid in LEGACY_HOLDS else 'legacy_schematic_review'))))
        finding,change=SPECIAL.get(gid,(p['observation'],p['animation']))
        notes=[]
        if gid not in ready:notes.append('Current served asset is an original schematic; final watercolor composition cannot yet be assessed. Pixel changes can be focus/guidance graphics rather than the requested subject action.')
        if anchor_kind=='face':notes.append('Face anchors currently use a centered slot. An off-center face illustration alone would conflict with live framing checks.')
        if gid in P0:notes.append('Resolve the documented subject, access or instruction mismatch before composition polish.')
        if any(w in gid for w in ('orbit','front_back','person_mirror_eye_hold')):notes.append('True turns/orbits require consistent new viewpoints; do not fake them with a sliding or mirrored flat painting.')
        records.append(dict(id=gid,priority='P0' if gid in P0 else ('P1' if gid in P1 else ('P3' if gid in {'glasses_clink_center','cup_eye_orbitr_cc','glass_flight_high_truckr_cc','latte_top_in_cd','latte_top_in_cd_whipout'} else 'P2')),
                            profile=key,profile_title=p['title'],techniques=p['techniques'],payoff=p['payoff'],effort=action[2] if action else p['effort'],
                            finding=finding,film_instruction=p['film'],animation_recommendation=change,
                            static_assessment=state,subject_action_recipe=action[0] if action else None,rig_requirements=action[1] if action else None,
                            schematic_followup_recipe=LEGACY_ACTIONS.get(gid),hold_reason=hold or LEGACY_HOLDS.get(gid),limitations=notes,uses=entry['uses'],step_count=len(entry['uses']),status=entry['status'],
                            description=entry['description'],anchor_kind=anchor_kind,motion_measurement=metric,
                            visual_evidence=f'checks/composition/contact-{index//12+1:02}.jpg',
                            strip=f'strips/{gid}.png',animation=f'animations/{gid}/guide_with_guides.png' if gid in ready else f'../guides/overlays/schematic/{gid}.png',
                            gallery=f'animations.html#{gid}'))
    assert len(records)==178 and len({r['id'] for r in records})==178
    frozen={r['id'] for r in records if r['id'] in ready and r.get('motion_measurement',{} ) and r['motion_measurement']['classification']=='identical_take_samples'}
    assert frozen==set(ACTIONS)|set(HOLD_REASONS),(frozen-(set(ACTIONS)|set(HOLD_REASONS)),(set(ACTIONS)|set(HOLD_REASONS))-frozen)
    legacy_candidates={r['id'] for r in records if r['id'] not in ready and r['motion_measurement']['classification']!='visible_change'}
    assert legacy_candidates==set(LEGACY_ACTIONS)|set(LEGACY_HOLDS)
    groups=[
        ('restore_action','First: restore the described action',list(ACTIONS),'High: makes the intended footage understandable','Medium to high; maintain the static camera','Fifteen frozen action takes should show a local prop/hand/body action. Do this before decorative camera movement.'),
        ('rooms','Strongest environmental payoff: room depth and framing',[r['id'] for r in records if r['profile']=='room_reveal']+['room_eye_panr_ww_whipout','room_crowd_eye_panr_ww_whipout','interior_pan'],'High','Medium; several usable masters already exist','A purposeful near frame, focal middle distance and quiet far depth will improve the final room shot more than another generic pan.'),
        ('heroes','Strongest product payoff: food and drink hierarchy',['burger_low_in_mc','burger_cut_high_in_cd_through','burger_cut_low_in_cd','cup_eye_hold_whipout','cup_eye_orbitr_cc','glass_drink_high_hold','glass_eye_tiltd_cc','glass_pour_low_in_cd','latte_top_in_cd','plate_spread_top_out_cw','plate_spread_top_out_dw'],'High','Low to medium for current masters; some action layers needed','Use a clear hero silhouette, purposeful action path and supporting background. Keep useful centered orbits centered.'),
        ('rhythm','Rhythm with a visual destination',[r['id'] for r in records if r['profile']=='display'],'High','Low to medium','Repeated shelves/glasses already supply a pattern; improve its hierarchy and landing, not just its speed.'),
        ('portrait_reach','Largest reuse: two shared portrait guides',['talking_head_eye_level','selfie_one_high_hold'],'High catalog reach; moderate per-shot payoff','Medium: approved-style portraits still missing','These two guide IDs cover 60 steps in 45 scripts. Improve headroom, background separation and text/PiP clearance while retaining the current centered face slot.'),
        ('comparison','Matched before/after compositions',['before_front_back','selfie_close_eye_hold','selfie_reveal_eye_reveal_cc','selfie_reveal_eye_reveal_cm','person_mirror_eye_hold','hands_work_high_in_cd','hands_work_high_hold'],'High','Medium to high; paired sources and instruction decisions','Use the same position, scale, angle and light before and after. Resolve the keep-still versus turn conflict and match actual comparison views.'),
        ('tabletop','Grouped tabletop arrangements',[r['id'] for r in records if r['profile']=='flatlay'],'High for food/retail sequences','Medium','One dominant object, a few supporting objects and clear gaps are more useful than simply filling the frame or forcing symmetry.'),
        ('readability','Keep information shots calm',[r['id'] for r in records if r['profile']=='readable'],'Medium aesthetic payoff; high usefulness','Low to medium','Align and isolate the relevant real line, control glare and animate a pointer only when requested. Preserve the readable hold.'),
    ]
    by_id={r['id']:r for r in records};opportunities=[]
    for rank,(key,title,ids,payoff,effort,reason) in enumerate(groups,1):
        ids=list(dict.fromkeys(ids));uses=sorted({u for gid in ids for u in by_id[gid]['uses']})
        opportunities.append(dict(rank=rank,id=key,title=title,guide_ids=ids,guides=len(ids),steps=len(uses),scripts=len({u.rsplit('.',1)[0] for u in uses}),payoff=payoff,effort=effort,reason=reason))
    pilots=['chair_reveal_frame','bar_low_truckr_mm','plate_spread_top_out_cw','glass_drink_high_hold','cup_eye_hold_whipout','talking_head_eye_level']
    input_paths=[ROOT/'guides/watercolor_motion/manifest.json',ROOT/'guides/script_templates.json',HERE/'animations/index.json']
    validator=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/Sources/LiveGuide/FrameStep.swift')
    report=dict(date='2026-10-26',scope=dict(guides=178,script_steps=304,visual_strip_reviews=178,contact_sheets=15,timed_apng_reviews=178,timed_watercolor_reviews=96,timed_schematic_reviews=82,timed_samples_per_clip=5),
                judgment='Editorial prioritization, not measured aesthetic uplift. Real footage and device UI have not been reviewed.',
                constraints=['Preserve visitor-accessible viewpoints, specified angles, motion direction and stable identity.','Maximum two visible hands; no drawn mouths; schematic cosmetics.','Keep approved single-pigment artwork and final global alpha 0.5.','New face or product placement must match the scenario anchor and live ghost/validator targets.','Off-center face targets need matching live validator/ghost support.','Do not treat transparent illustration margins as negative space in actual footage.'],
                motion_counts=measurements['by_style'],
                static_summary=dict(identical_take_samples_all=measurements['counts']['identical_take_samples'],low_visible_change_candidates_all=measurements['counts']['low_visible_change_candidate'],watercolor_identical_take_samples=24,missing_subject_action_guides=15,missing_subject_action_steps=sum(by_id[g]['step_count'] for g in ACTIONS),watercolor_intentional_holds=9,watercolor_other_visible_change=72,schematic_action_followups=len(LEGACY_ACTIONS),schematic_intentional_holds=len(LEGACY_HOLDS),schematic_other_visible_change=measurements['by_style']['schematic']['visible_change']),
                portrait_reach=dict(guides=2,steps=60,scripts=45,share_of_steps=round(60/304,4)),
                source_integrity={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},
                validator_reference=dict(path=str(validator),sha256=hashlib.sha256(validator.read_bytes()).hexdigest(),face_slot_center=[.5,.36],face_center_tolerance=.12),
                priorities=dict(collections.Counter(r['priority'] for r in records)),opportunities=opportunities,pilot_order=pilots,guides=records,
                assets_changed=False,api_changed=False,sensor_scenarios_changed=False)
    (HERE/'composition-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    write_markdown(report,by_id);write_html(report)
    print(json.dumps({k:report[k] for k in ('scope','static_summary','portrait_reach','priorities','pilot_order','assets_changed')}))


def write_markdown(report,by_id):
    lines=['# Composition and static-take audit','','2026-10-26. Reviewed all 178 guide frame strips, descriptions and their 304 script assignments. Five timed pixel checks cover every APNG: 96 watercolor and 82 schematic. This is an audit: no artwork, API data or sensor scenarios were changed.','',
           '[Interactive review](composition-audit.html) | [Machine-readable recommendations](composition-audit.json) | [Timed motion evidence](checks/composition/motion-measurements.json)','',
           'The recommendations concern the footage a person will shoot. Making the watercolor illustration prettier does not establish real negative space, lighting or depth in that footage. Per-guide instructions below describe both the actual filming position/composition and the future animation work. Aesthetic payoff is editorial judgment; there is no measured uplift or device/footage validation.','',
           '## Main findings','',
           '- The strongest environmental opportunities are room reveals and interiors: natural foreground framing, a clear focal destination, leading lines and quieter distance.',
           '- Food and drink heroes benefit from silhouette/background separation, a motivated diagonal action path and deliberate opening/landing crops. Keep useful centered orbits centered.',
           '- Repeated shelves, bottles and glasses already offer rhythm. Give the pattern a chosen item or gap to land on instead of increasing every camera move.',
           '- Two shared portrait guides cover 60 of 304 steps (19.7%) across 45 scripts. They remain original schematics. Better headroom/background separation has large reuse value.',
           '- The validator centers face anchors: `FrameStep.target(for:)` uses a face slot centered at x=0.5, y=0.36 with center tolerance 0.12. Moving a face to x=1/3 is outside that center tolerance at the same height. Off-center face variants need validator/ghost changes, not only different art.',
           '- Twenty-four watercolor takes have identical sampled pictures during the take. Fifteen (23 step assignments) omit the described subject action. Nine are useful readable or spoken holds.',
           '- Several shared camera guides acquired task-specific paintings. Hair/scissors used for plating, a mortar used for a gym grip, and a kettlebell pose used for a sauna walk are subject mismatches that composition polish cannot fix.',
           '- The two `before_front_back` script steps say keep still, while the guide turns the head. Resolve that comparison plan before matching the after.',
           '', '## Ranked opportunities','','Groups overlap; guide/step counts must not be added together. Rank balances shot clarity, expected aesthetic value and available artwork, not a computed quality score.','',
           '| Rank | Opportunity | Guides / steps | Expected payoff | Effort |','|---|---|---|---|---|']
    for o in report['opportunities']:lines.append(f'| {o["rank"]} | {o["title"]} | {o["guides"]} / {o["steps"]} | {o["payoff"]} | {o["effort"]} |')
    lines+=['','## Static-looking takes','',
            'Five samples are taken during the intended take, excluding entry holds, exit whips and fade. For six single-whip guides, the held take before/after the whip is measured; the two-whip salon sequence retains its first detail-to-detail move. RGB is compared on charcoal without added viewfinder UI. This detects unchanged pictures, not physical camera movement. Sparse samples could miss cyclic motion; descriptions and frame strips were also reviewed. Schematic focus/guidance graphics can change without showing the requested real subject action.','',
            '| Cohort | Identical samples | Very low change candidates | Visible change |','|---|---|---|---|','| Watercolor | 24 | 0 | 72 |',f'| Original schematic | {report["motion_counts"]["schematic"]["identical_take_samples"]} | {report["motion_counts"]["schematic"]["low_visible_change_candidate"]} | {report["motion_counts"]["schematic"]["visible_change"]} |','',
            '### Restore the action while keeping the camera still','','| Guide | Steps | Missing action / proposed mechanics | Requirements |','|---|---|---|---|']
    for gid,(recipe,requirements,effort) in ACTIONS.items():lines.append(f'| [{gid}](animations.html#{gid}) | {by_id[gid]["step_count"]} | {recipe} | {effort}: {requirements} |')
    lines+=['','### Preserve these nine deliberate holds','']
    lines += [f'- [{gid}](animations.html#{gid}): {reason}' for gid,reason in HOLD_REASONS.items()]
    lines+=['','### Original schematic follow-ups','',f'Of {len(LEGACY_ACTIONS)+len(LEGACY_HOLDS)} original schematics with identical or very low-change sampled takes, {len(LEGACY_ACTIONS)} need task-specific subject-action review in their final artwork. These are review/production candidates, not confirmed frozen watercolor animations. The other eight are valid resting, comparison or spoken holds.','',
            '| Schematic action candidate | Treatment to review/create |','|---|---|']
    lines += [f'| [{gid}](animations.html#{gid}) | {recipe} |' for gid,recipe in LEGACY_ACTIONS.items()]
    lines+=['','Keep these original holds steady: '+', '.join(f'`{gid}`' for gid in LEGACY_HOLDS)+'.']
    lines+=['','A static camera and a static subject are different requirements. Do not add a generic zoom to a rep, tool stroke, plate placement or clipper pass. Keep the background/phone fixed and animate only the requested subject action. Camera movement in the other 72 clips does not prove that every liquid or finger action is already complete.','',
            '## First composition/action pilots','','These are recommendations for a subsequent implementation pass. No new samples were generated.','']
    for i,gid in enumerate(report['pilot_order'],1):
        r=by_id[gid];lines += [f'{i}. **[{gid}](animations.html#{gid})** — {r["finding"]} {r["subject_action_recipe"] or r["animation_recommendation"]}']
    lines+=['','## Existing strengths to preserve','',
            '- `glasses_clink_center`: centered convergence, two hands and a contact hold.',
            '- `cup_eye_orbitr_cc`: centered subject and genuine changing handle viewpoint.',
            '- `glass_flight_high_truckr_cc`: a diagonal near/mid/far rhythm with different layer speeds.',
            '- `latte_top_in_cd` and its whip variant: an effective pitcher-to-cup diagonal.',
            '- `bar_low_truckr_mm`: coherent gentle movement from one panorama; composition can improve without changing its deliberate speed.','',
            '## Before changing assets','',
            '- Preserve the shot angle, direction, visitor-accessible position and current global 50% alpha. Do not darken the whole overlay to create depth.',
            '- Check product placement as well as faces against each scenario anchor and its ghost/validator target. Repositioning the painting alone can teach a framing the live guide rejects.',
            '- Tonal perspective in the sketch should use selective line/value hierarchy. In real footage, separation comes from available light, camera position and subject/background relationships. It is not guaranteed by fading a background layer.',
            '- Keep the focal subject readable at capture size and with the real prompter/PiP/controls. No device safe-zone dimensions were measured here.',
            '- Match paired before/after framing and check the full motion path, not only a pretty first or last frame.',
            '- Shared mechanics can remain shared; incompatible resources require subject variants. Staff-side kitchen/till/prep camera positions remain disallowed even where older script wording mentions permission.','',
            '## Every guide','','P0: resolve a concrete source/instruction/access conflict. P1: strongest action/composition opportunity. P2: useful family-level refinement. P3: preserve a current strength; optional polish. Priorities are editorial judgments.','',
            '| Guide | Priority | Steps | Techniques | Static assessment | Recommendation |','|---|---|---|---|---|---|']
    for r in report['guides']:
        advice=r['subject_action_recipe'] or r['schematic_followup_recipe'] or r['animation_recommendation']
        lines.append(f'| [{r["id"]}](animations.html#{r["id"]}) | {r["priority"]} | {r["step_count"]} | {", ".join(r["techniques"])} | {r["static_assessment"].replace("_"," ")} | {advice} |')
    (HERE/'composition-audit.md').write_text('\n'.join(lines)+'\n')


def write_html(report):
    e=html.escape
    options=''.join(f'<option value="{e(k)}">{e(v["title"])}</option>' for k,v in PROFILES.items())
    groups=''.join(f'<li><button class="jump" data-ids="{e(" ".join(o["guide_ids"]))}">{o["rank"]}. {e(o["title"])}</button> — {o["guides"]} guides / {o["steps"]} steps. {e(o["reason"])}</li>' for o in report['opportunities'])
    cards=[]
    for r in sorted(report['guides'],key=lambda r:(r['priority'],report['pilot_order'].index(r['id']) if r['id'] in report['pilot_order'] else 100,-r['step_count'],r['id'])):
        limits=''.join(f'<li>{e(n)}</li>' for n in r['limitations'])
        action=f'<p><strong>Missing action:</strong> {e(r["subject_action_recipe"])}</p><p><strong>Rig:</strong> {e(r["rig_requirements"])}</p>' if r['subject_action_recipe'] else ''
        if r['schematic_followup_recipe']:action=f'<p><strong>Schematic action follow-up:</strong> {e(r["schematic_followup_recipe"])}</p>'
        if r['hold_reason']:action+=f'<p><strong>Keep the hold:</strong> {e(r["hold_reason"])}</p>'
        metric=r['motion_measurement'];evidence='Timed APNG samples: '+metric['classification'].replace('_',' ')
        cards.append(f'''<article id="{e(r['id'])}" class="card" data-priority="{r['priority']}" data-profile="{r['profile']}" data-state="{r['static_assessment']}" data-search="{e((r['id']+' '+r['description']+' '+' '.join(r['techniques'])+' '+' '.join(r['uses'])).lower())}">
<header><span class="priority">{r['priority']}</span><h2>{e(r['id'])}</h2><p>{r['step_count']} step assignments · {e(r['profile_title'])}</p></header>
<img class="strip" loading="lazy" src="{e(r['strip'])}" alt="Existing animation frames">
<p class="tags">{e(' / '.join(r['techniques']))}</p><p>{e(r['finding'])}</p>{action}
<details><summary>Filming instruction and implementation</summary><p><strong>Film:</strong> {e(r['film_instruction'])}</p><p><strong>Guide:</strong> {e(r['animation_recommendation'])}</p><p><strong>Effort:</strong> {e(r['effort'])}</p><ul>{limits}</ul><p><strong>Used by:</strong> {e(', '.join(r['uses']))}</p><p>{e(evidence)}</p><a href="{e(r['visual_evidence'])}">Review contact sheet</a></details>
<footer><button class="play" data-src="{e(r['animation'])}" data-id="{e(r['id'])}">Play existing animation</button><a href="{e(r['gallery'])}">Open gallery</a></footer></article>''')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Composition and motion audit</title><style>
*{box-sizing:border-box}body{margin:0;background:#f1efe8;color:#253943;font:15px/1.5 system-ui,sans-serif}main{max-width:1450px;margin:auto;padding:25px}h1{font-size:30px}h2{font-size:16px;overflow-wrap:anywhere;margin:6px 0}a{color:#315e75}header p{margin:6px 0}.intro{max-width:1050px}.findings{background:#fffdf7;border:1px solid #c4cfce;padding:20px;max-width:1100px}.findings li{margin:9px 0}.jump{border:0;padding:0;text-align:left;background:none;color:#315e75;text-decoration:underline;cursor:pointer}nav{display:flex;gap:8px;flex-wrap:wrap;background:#f1efe8;padding:14px 0;position:sticky;top:0;z-index:2}input,select,button{font:inherit;padding:7px;border:1px solid #a9b9bc;border-radius:4px;color:inherit;background:white}input{flex:1;min-width:200px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}.card{background:#fffdf7;border:1px solid #c7d1ce;border-radius:7px;padding:15px}.card[hidden]{display:none}.strip{width:100%;display:block;margin:12px 0}.tags{font-size:12px;color:#52717c}.priority{display:inline-block;background:#dde8e2;font-weight:650;padding:2px 7px;border-radius:4px}details{font-size:13px}summary{cursor:pointer;color:#315e75}footer{display:flex;gap:12px;align-items:center;margin-top:14px;font-size:12px}dialog{border:1px solid #abbab9;border-radius:8px;padding:15px;max-width:95vw}dialog::backdrop{background:#14252bd9}dialog img{display:block;height:70vh;max-width:85vw;aspect-ratio:9/16;object-fit:contain;background:#23343e}dialog h2{max-width:405px}#count{align-self:center;font-size:13px}@media(max-width:650px){main{padding:14px}.cards{grid-template-columns:1fr}nav{position:static}}
</style></head><body><main><div class="intro"><a href="animations.html">Animations</a> / <a href="composition-audit.md">Written audit</a> / <a href="composition-audit.json">JSON</a><h1>Where composition and action will help most</h1>
<p>178 guide strips reviewed against 304 script assignments. Five timed samples from every APNG: 96 watercolor and 82 schematic. These are recommendations for future footage and guides; no assets, live scenarios or API data changed.</p>
<p><strong>24 unchanged watercolor takes: 15 missing subject actions (23 steps), 9 deliberate holds.</strong> The other 72 watercolor clips show visible change. Of the schematics, __LEGACY_SAME__ have identical samples and __LEGACY_LOW__ have very low change; __LEGACY_ACTIONS__ need task-specific subject-action review and __LEGACY_HOLDS__ are intentional holds.</p>
<p>Face framing currently expects a centered target. Transparent watercolor margins are not negative space in the actual room. Aesthetic payoff is editorial judgment; real footage and device UI were not evaluated.</p></div>
<section class="findings"><h2>Ranked opportunities</h2><p>Click a group to inspect its current guides. Counts overlap.</p><ol style="list-style:none;padding-left:0">'''+groups+'''</ol></section>
<nav><input id="search" placeholder="Guide, technique or script"><select id="priority"><option value="">All priorities</option><option>P0</option><option>P1</option><option>P2</option><option>P3</option></select><select id="profile"><option value="">All shot families</option>'''+options+'''</select><select id="state"><option value="">All motion states</option><option value="missing_subject_action">Missing watercolor action</option><option value="intentional_hold">Intentional watercolor hold</option><option value="visible_change">Watercolor visible change</option><option value="legacy_action_candidate">Schematic action follow-up</option><option value="legacy_intentional_hold">Intentional schematic hold</option><option value="legacy_schematic_review">Other original schematic</option></select><button id="reset">Show all</button><span id="count"></span></nav><div class="cards">'''+''.join(cards)+'''</div></main>
<dialog id="preview"><button id="close">Close</button><h2 id="preview-title"></h2><p>Current animation, before any proposed changes.</p><img id="preview-image" alt="Existing guide animation"><button id="replay">Replay</button></dialog>
<script>
const search=document.getElementById('search'),priority=document.getElementById('priority'),profile=document.getElementById('profile'),state=document.getElementById('state');let selected=null;
function apply(){let n=0;document.querySelectorAll('.card').forEach(c=>{c.hidden=!!((selected&&!selected.has(c.id))||(priority.value&&c.dataset.priority!==priority.value)||(profile.value&&c.dataset.profile!==profile.value)||(state.value&&c.dataset.state!==state.value)||!c.dataset.search.includes(search.value.toLowerCase().trim()));if(!c.hidden)n++;});document.getElementById('count').textContent=n+' guides';}
[search,priority,profile,state].forEach(c=>c.addEventListener(c===search?'input':'change',apply));
document.getElementById('reset').onclick=()=>{selected=null;search.value=priority.value=profile.value=state.value='';apply();};
document.querySelectorAll('.jump').forEach(b=>b.onclick=()=>{selected=new Set(b.dataset.ids.split(' '));search.value=priority.value=profile.value=state.value='';apply();document.querySelector('nav').scrollIntoView();});
const dialog=document.getElementById('preview'),image=document.getElementById('preview-image');let source='';function replay(){image.src=source+'?audit_play='+Date.now();}
document.querySelectorAll('.play').forEach(b=>b.onclick=()=>{source=b.dataset.src;document.getElementById('preview-title').textContent=b.dataset.id;dialog.showModal();replay();});
document.getElementById('replay').onclick=replay;document.getElementById('close').onclick=()=>dialog.close();dialog.addEventListener('close',()=>image.removeAttribute('src'));apply();
</script></body></html>'''
    page=page.replace('__LEGACY_SAME__',str(report['motion_counts']['schematic']['identical_take_samples'])).replace('__LEGACY_LOW__',str(report['motion_counts']['schematic']['low_visible_change_candidate'])).replace('__LEGACY_ACTIONS__',str(len(LEGACY_ACTIONS))).replace('__LEGACY_HOLDS__',str(len(LEGACY_HOLDS)))
    (HERE/'composition-audit.html').write_text(page)


if __name__=='__main__':main()
