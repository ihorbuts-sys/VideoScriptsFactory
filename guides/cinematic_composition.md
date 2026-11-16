# Composition direction for live filming guides

This is the authoring standard for the Blender experiment and future guide revisions.
It is a design method, not a claim that the existing 178 animations have been rebuilt.
The first implementation is `catalog/blender-study/`: a low bar truck and the contextual
handover to a high table shot from `restaurant-room-tour`.

The guide should teach a viewer how to produce attractive, readable footage. Each object,
camera position, light cue and transition must contribute to that outcome. Model detail by
itself is not a composition decision. Commercial clarity means the intended subject reads
quickly and the footage supports the script; it does not require a glossy or artificial look.

## Start with the promised shot

Read the script step, shot plan, scene description, live scenario and actual next step together.
Write one sentence identifying what the audience should notice and what the camera should do.
Distinguish a venue/space shot from a product shot before choosing a hero. In the room-tour bar
step, the counter and seating explain the visit; a glass is supporting context, not the main
commercial subject. A menu-item review would need a different hierarchy and framing.
Choose the intended finishing frame before adding decorative objects. Preserve the specified
angle, motion direction, subject action and meaningful transition. If a fixed starting angle
is adapted for composition, record the change explicitly. Do not silently turn a truck into
an orbit or a held action into a push-in.

The opening frame should be achievable by an ordinary visitor. The ending frame should show
the advertised payoff and make sense beside the next shot. A cut between steps is a cut;
continuous travel should only be shown when the creator can actually make that move.

## Give every visible object a job

Record the role, position, reason, contact/support, visual weight and motion relationship of
each visible subject or repeated group. Instances inherit a group purpose but retain their
actual placement. Remove an object when it neither explains the venue/action nor improves
the composition. A distant object can be important; proximity is not the priority system.
Walls are absent from the ghost unless a specific edge explains framing, a doorway, a reveal
or another useful spatial relationship. Such edges stay very faint. Full room walls, ceilings
and floors may support lighting calculations without becoming visible overlay surfaces.

| Role | Placement purpose | Ghost treatment |
|---|---|---|
| Hero | The intended subject, action/contact or primary framing anchor | Clearest contours; enough separation to read immediately |
| Support | Explains the hero, use, scale, setting or action | Visible but subordinate |
| Important background | A selected landmark or destination that the viewer must notice | Clearer than nearby decoration despite its distance |
| Foreground frame | Establishes depth or motivates a reveal | Restrained; does not cover the hero for the entire take |
| Background context | Establishes place, pattern or distance | Faintest useful contours and fewer details |
| Lighting cue | Explains a useful light direction, rim, light footprint or shadow boundary | Selective yellow marks; most pixels remain transparent |

The Blender proof uses final alpha ceilings of 0.50 for heroes, 0.34 for support, 0.39 for
important background anchors, 0.24 for foreground framing, 0.20 for structure and 0.125 for
decorative background. These are initial settings to judge on both light and busy footage,
not universal constants. Individual overlaps can raise a pixel's opacity before the final
whole-image alpha pass. Export multiplies final frame alpha by 0.5 exactly once, preserving RGB.

## Design the frame as an arrangement

1. Establish one clear visual priority. Use position, size, contour contrast, separation and
   motion to support it. Check the image at phone size, where small decorative details vanish.
2. Choose symmetry when it communicates the subject: two usable place settings, a centred
   doorway or a deliberate comparison. Choose weighted asymmetry when it gives a hero room,
   creates direction or balances a smaller secondary subject. Do not force every shot onto thirds.
3. Use thirds as a placement option, then check actual anchor and face-validation tolerances.
   The project's face target is centred; an off-centre face variant requires compatible guide
   and validation data. Avoid clipping a subject merely to satisfy a grid.
4. Leave deliberate quiet areas around important silhouettes and in app UI zones. Negative
   space should help the subject read or anticipate action, rather than be random empty sky.
5. Use an existing counter edge, aisle, tabletop edge, shelf or action path to connect the
   foreground to the destination. Check where the line ends. It should not lead out of frame
   while the intended subject is elsewhere.
6. Separate depth planes. Keep enough distance between foreground, subject and background for
   a real truck to reveal parallax. Avoid stacking every prop on one flat plane.
7. Repeat with intention. Groups of bottles, chairs or tools can establish rhythm; a chosen
   gap, changed silhouette or selected item creates a destination within the pattern.
8. Inspect mergers and tangencies: a bottle should not appear to grow out of a glass, a tool
   should not merge with a hand outline, and an edge should not graze the subject's silhouette
   by one confusing pixel. Check the entire move, not only the first frame.

These choices adapt established photographic ideas to the live-guide use case. Nikon's
[leading-lines guidance](https://nikonschool.co.uk/hints-and-tips/using-leading-lines-in-your-compositions)
describes how line direction connects attention and conveys depth. Its
[composition examples](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/composing-photographs)
also demonstrate improving a frame by changing viewpoint and removing competing context.
The specific layouts, opacity hierarchy and review requirements here are project decisions.

## Preserve real use and physical relationships

The arrangement should work in life. Seats face their own place settings. Forks and knives
are oriented from each diner's viewpoint, with knives facing the plates. Glasses have usable
clearance. A decorative accent must not occupy a diner's working space or block the main view.
Respect the number of people; do not add a third setting just to obtain an odd-number pattern.

Keep glass bases on their supports, hands attached to grips, feet on the floor and tools at
the action contact. Rigid supports and their resting objects retain their real relationship
unless a deliberate emphasis is clearly motivated and physically coherent. The camera move
creates parallax; the furniture should not slide independently to imitate it.

In an actual venue, choose a better visitor-side camera position around fixed fixtures.
Rearrange only the creator's own portable items where appropriate. Never imply moving venue
furniture, entering a staff area, or having special access is required for the result.

## Use lighting when it explains a better shot

Choose a lighting idea with a visible purpose: side light to reveal form, backlight to show
clear liquid or steam, a soft window source for a portrait, or restrained practical lights
to separate a bar's layers. Nikon's
[food-lighting guide](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/create-your-light-food-photography-at-home)
discusses directional side light, backlight for suitable subjects, restrained props and useful
negative space. Apply these options selectively to the subject and venue.

Light stays fixed during an ordinary take. Camera/subject movement may change highlights and
visible shadows. A moving-light demonstration needs to be explicitly about changing the light;
do not animate the sun racing across a table to suggest an ordinary four-second shot.
For an ordinary bar visit, assume existing fixed venue lights. Teach camera positioning and
movement within that light; do not require restaging fixtures or catching a staged shelf glow.

For a ghost, use a few window-facing rim accents or a faint light/shadow boundary attached to
the actual surface. A light shape may be modelled as an instructional object when that is more
legible than realistic shading. Preserve transparency; full-frame opaque room shading belongs
only in a separate lighting reference video. Do not make every object yellow or obscure the
real camera image with a painted light patch. A yellow light cue is part of the design; runtime
caught-state tinting still needs its own integration check.

## Compose motion, not only still pictures

Design opening, midpoint and finishing frames together. During a truck, let a near edge reveal
the destination instead of crossing the hero at the end. During a push, preserve the hero and
let excess context leave the frame. During an orbit, retain a stable subject while actual new
surfaces appear. During a tilt, reveal meaningful vertical information. A deliberate hold can
be the right choice for speech, a subtle action or a clear result.

Use a controlled start and settle. Exaggeration can clarify a depth relationship or selected
action, but it should preserve contact and the camera move's identity. Avoid decorative
rocking, unrelated zooms, geometry drift and constant motion simply to prevent a still frame.
The instruction's timing must show the complete action and actual handover, not stretch a
short loop to fill time. The full script should preserve the relationship between those beats.

## Practical applications by shot family

| Shot family | Useful starting idea | What to verify |
|---|---|---|
| Bar/room truck | Oblique leading edges, a near frame, grouped background rhythm | Fixed camera orientation; stronger near parallax; destination remains clear |
| Doorway reveal | Natural architectural framing and a useful occluder | Opening stays transparent; the revealed subject has a clean landing frame |
| Dish/drink hero | Clear silhouette, a quiet supporting surface and motivated side/back light | The actual dish/action stays the subject; reflections and props do not overwhelm it |
| High table view | Functional place settings and a depth diagonal | Diner-relative orientation, surface contacts, reachable items and open centre |
| Top-down arrangement | Deliberate spacing, balanced groups and a clear action area | No unnecessary perspective change; tool/hand paths remain readable |
| Portrait/selfie | Useful headroom, background separation and relevant context | Existing face target, mouthless artwork, no distracting line mergers |
| Work/hands | A clear tool-to-resource contact and an uncluttered support surface | Correct task, at most two hands, no detached grip or restricted viewpoint |
| Orbit | A centred subject with stable scale and changing visible surfaces | Genuine viewpoint change; optional quiet background rather than an unrelated reveal |
| Comparison | Consistent angle, scale, light and framing | Composition does not falsely exaggerate the before/after result |

## Review every scene before rollout

For each visible object, inspect why it is present, why it is there, whether it belongs to
that script context, how it is supported, what it may occlude and how much attention it deserves.
Check the start, several moving frames and the landing at actual phone size. Review the ghost
over a bright backing, a dark backing and a busy real-image sample. Verify that the angle,
camera move, subject action and actual next shot are understandable without reading a label.

Check both visual appeal and instructional truth. A pleasing still does not prove a usable
move. A passing geometry check does not prove a beautiful image. Record the source, changes,
per-object reasons and limitations beside the output. The Blender study's
`object-composition-plan.json`, `scene-report.json`, `lighting-report.json` and
`export-checks.json` provide the first concrete example of this review trail.
