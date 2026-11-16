# Grasping and sliding a drinking glass on a table (2026-11-11)

Why: owner note on pancake_clear_path (round 2, 2026-11-11): "new hand grip cup unnaturally - thumb rotated somehow
weird, overall it just touch the glass with middle finger and slides, no actual grabbing - research how it should look
like"; on glass_slide_close: "the arm is 2d". Used by `guides/blender_motion/real_hands.py` (`wrap`) and
`guides/blender_motion/p0_table_compositions.py` (`glass_grasp`, `CLEAR_GRASP`, `SLIDE_GRASP`).

## Sources

| Ref | Source | URL | Status |
|---|---|---|---|
| GG1 | Feix T, Romero J, Schmiedmayer HB, Dollar AM, Kragic D. The GRASP taxonomy of human grasp types. IEEE Trans Human-Machine Systems 46(1):66-77, 2016 | https://www.eng.yale.edu/grablab/pubs/Feix_THMS2016.pdf | opened (PDF text extracted locally; the grasp chart itself is an image) |
| GG2 | Bullock IM, Feix T, Dollar AM. Finding small, versatile sets of human grasps to span common objects. ICRA 2013 | https://www.eng.yale.edu/grablab/pubs/Bullock_ICRA2013.pdf | opened (PDF text extracted locally) |
| GG3 | Cutkosky MR. On grasp choice, grasp models, and the design of hands for manufacturing tasks. IEEE Trans Robotics and Automation 5(3), 1989 | https://manuscript.isc.ac/Inventory/49/1227120.htm | search-only (the Harvard copy returned 404; tree structure from secondary summaries) |
| GG4 | Murphy MA, Sunnerhagen KS, Johnels B, Willen C. Three-dimensional kinematic motion analysis of a daily activity drinking from a glass: a pilot study. J NeuroEng Rehabil 3:18, 2006 | https://jneuroengrehab.biomedcentral.com/articles/10.1186/1743-0003-3-18 | search-only (table pages redirect to a Springer login; PMC asked for a captcha) |
| GG5 | Ryu J, Cooney WP et al. Functional ranges of motion of the wrist joint. J Hand Surg 1991 / Palmer AK et al. 1985, functional wrist motion | https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_81166379 | search-only (snippets: drinking and eating need about 5-10 deg flexion to 35 deg extension) |
| GG6 | Hand anthropometry, young adults (PMC5702813, Table 1) | https://pmc.ncbi.nlm.nih.gov/articles/PMC5702813/table/tbl_001 | search-only (snippet values) |
| GG7 | Drawing references for hands holding a glass (Quote the Anime hand poses; Daisie blog; Arteza) | https://quotetheanime.com/drawing/how-to-draw-hand-poses-step-by-step/ | search-only (generic: draw the glass first, fit the curled fingers round it; photograph your own hand) |

## Findings and numbers

- Grasp type (GG1): a glass held round its side is a full-hand wrap, palm opposition: "the palm of the hand is assigned
  to VF 1 and the four fingers act against it as VF 2". Wraps are split by object size into large diameter (#1), small
  diameter (#2) and medium wrap (#3); a power grip is a rigid hand-object relation, "all movements of the object have to
  be evoked by the arm" - so a slide moves the forearm, not the fingers. GG1 names the glass of water explicitly as a
  valid (orientation-constrained) grasp.
- Thumb (GG1): "In order for the thumb to oppose the fingers, the thumb has to be in abducted position"; adducted only
  for side opposition (lateral pinch) or "to get out of the way". A wrap on a glass is therefore thumb abducted, thumb
  pad on the glass wall opposite the fingers - not rotated along the side of the index (the round-2 fault).
- Grasp axis (GG2): medium wrap is the most-used general-purpose grasp, "especially well suited to larger, cylindrical
  objects"; its main grasping axis is radial-ulnar, so the line of knuckles runs along the glass's long axis (the hand
  stands upright beside the glass, thumb uppermost).
- Contact (GG1, Discussion): wrap differs from a "prismatic 4 finger" grasp only by the extra palm contact. The round-2
  pinch had pad contact on one finger only; the rebuilt grasp has palm + every phalanx on the wall.
- Size: the cocktail shell is 8.0-8.8 cm across (radius 4.0-4.4 cm), so it is a large-diameter wrap: fingers cover
  about half the circumference and the thumb closes on the opposite side (judgement from GG1 classes and GG6 hand size).
- Hand size (GG6): hand length 181 mm (male) / 169 mm (female), breadth 87 / 76 mm, middle finger 106 / 99 mm. The CC0
  hand library keeps its 190 mm wrist-to-fingertip scale (existing guides; judgement, about 5 percent above the male
  mean).
- Wrist (GG4, GG5): drinking from a glass needs about 25-36 deg wrist extension at peak; the functional arc for eating
  and drinking is about 10 deg flexion to 35 deg extension; extension can reach about 60-70 deg. Wrist extension is what
  swings the forearm sideways while the hand stays wrapped on the glass.
- Drawing (GG7): draw the glass, then the fingers as curved bands that follow its ellipse; the thumb crosses the near
  side, the finger tips appear at the far edge.

## How the guides use it

- `real_hands.wrap` poses the original CC0 rig (not the pre-baked pinch): palm seated on the wall (contact point 9.5 cm
  from the wrist, the distal palm), then each finger closes MCP -> PIP -> DIP (later joints coupled at 0.8) until a link
  touches the wall (bisection, 1 mm gap, which absorbs the 0.1 mm the subdivision surface adds); the thumb metacarpal swings to the opposite side, abducted and lifted toward
  the radial side, and its joints close the same way about the glass axis. Joint limits 90/105/80 deg (fingers),
  60/60/80 deg (thumb), common adult active ranges (judgement). Skin left inside the wall by blended joint weights is
  settled onto the wall; the per-hand amount is recorded on the hand root (`wrap_skin_settled_mm`).
- pancake_clear_path (companion's right hand from the right, camera at table height), `CLEAR_GRASP`: palm 30 deg
  behind the entry side, wrist 60 deg extension (above GG4's 36 deg drinking peak, inside the 60-70 deg range; judgement,
  needed to turn the forearm out to the right) and 20 deg ulnar deviation (raises the forearm), palm 7.5 cm up the glass.
  The hand arrives and lets go along the one level direction its wrap leaves open, found by sweeping the evaluated skin
  25 cm in 2 deg steps (`p0_release`; 14 deg behind the entry side here, 0 mm swept penetration).
- glass_slide_close (the creator's own left hand, camera above and to the right), `SLIDE_GRASP`: palm 25 deg toward the
  lens, wrist 50 deg extension, palm 6 cm up the glass so the rim and top ice stay clear.
- Result, both guides: closure angles MCP 11-31 deg with PIP/DIP following at 0.8, thumb CMC 7 deg after the swing;
  skin settled 0.6-0.7 mm per hand; rendered hand-to-glass clearance 0.09-0.16 mm on every frame with a grip, 0 mm
  penetration.
- Orientation trade-off (judgement): with the knuckle line upright (GG2) the back of the hand faces the side the palm
  sits on, so turning the back of the hand toward the lens also turns the forearm toward the lens. Where the hand belongs
  to someone beside the table (pancake) the forearm must leave frame on its own side, so the palm sits a little behind
  the glass and the lens sees the thumb across the front, the knuckle edge and a raised forearm. Where it is the
  creator's own hand (glass_slide_close) the forearm comes from the lens side and the back of the hand faces the lens.
