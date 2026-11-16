# truck_window_line (new; catalog v3, owner go-ahead 2026-11-16)

Steps: dish-review/place, drink-review/place, venue-review/place (serviceKind truck).

Shot type **room**, level **easy**, back camera, portrait, about 5 s.

Research: commercial_shots.md room-pan; best_practices/fast-food.md (the truck window, the line).

Scene: Closer: the truck's window and awning from about 12 ft, slow pan right along the side to the window. A line of people is not available (one creator rig max): no people.

Status: after truck cache.

Common rules (all v3 requests): approved objects only (OBJECTS.md inventory, plus the owner approvals of
2026-11-16: food truck, burger, cake_slice, serving_bowl, salon_chair, wall_shelf, display_case, serving_tray,
treatment_bed one-hole copy, hair_clipper, dumbbell, takeaway_cup, laptop, reception desk composition, dessert spoon,
teaspoon, dessert knife, paper wrap closed/opened, paper tray). Not available: t-shirt (owner regenerating), salon mirror
(candidate). A missing object: stop and write an OBJECTS.md request (guide-objects skill). Generic stand-ins (owner:
"as generic as possible"). Place setting per STYLE.md "Objects" (pastry, pizza, bakery and handhelds: no cutlery;
desserts: dessert plate; mains and salad: fork and knife 3/4 in clear). US units in every text (titles, beats,
directions). Line-art P0 style, 9:16, hero inside the 28% / 35% band. Draft only: no publish, no commit; report per the
guide-animator skill. Metadata in record.json: showsFace, needsHelper, guideVisibleToCreator, units "us", zoomHint.

## Rework r2 (guide-animator, owner review 2026-11-17)

Owner: "put the cooker (barista model) inside, add some burgers, clean dots". v1 archived in
`archive/2026-11-16-v1/`. Same move and timing (30 deg pan right from 12 ft, 5 s). Easy guide: no beats.
- Cook: the approved barista rig in the counter_edge_to_pass_v2 working pose, as in truck_across_street r2.
- Burgers: three approved Tripo burgers (default dot cleanup in memory) on the truck's inner counter (top z 1.45 m)
  right of the pots, about 7 in apart, supporting opacity; no wrap, no cutlery (handheld rule). The outer window
  ledge is only about 4 in deep with a sill hump, so it cannot hold them.
- Dots: truck strokes under 12 px removed per frame, this guide only (`drafts/truck_cook.py`).
- Open for the owner: the burgers read small at 12 ft (about 16 px wide each), seen nearly edge-on at eye level.

## Rework r3 (guide-animator, owner review 2026-11-16 14:52)

Owner: "the window shape is unclear". r2 archived in `archive/2026-11-16-r2/` (`record.r2.json`, request, render,
export, sheet, scene code copies of `truck_window_line.py` and `truck_cook.py`). Same pan, cook, burgers, timing.
Easy guide: no beats.
- Why it was unclear: the cache draws no contour on the opening's top and right edges (the wall and the soffit both
  face the lens; contour-only line art), so the window read as a sill and one post with the interior lines on top.
- Window frame: a thin closed rectangle (the curb line's 1.2 mm tube, square corners, hero role) traces the opening on
  the wall, 5 mm in front of it: x -0.675..1.86 m, z 1.19..2.135 m (about 8 ft 4 in x 3 ft 1 in), from a 1 cm ray
  probe of the cache (`scratch/r3/probe_edges.py`). Assumption: this code-built outline counts as a drawing aid like
  the curb line, not a new object; the owner may prefer it removed if the quieter interior alone reads.
- Interior quieter: the truck's own strokes that project inside the opening (inset 4 px) are drawn at 40% of the hero
  opacity (counter, shelf, pots, tap; about 27% of the truck's points); the cook (character) and burgers (support)
  keep their roles. This guide only (`install_interior_quieting`, wraps strokes_setup after the dot filter).
- The right frame edge breaks for a few px where the awning strut passes in front (real occlusion).
