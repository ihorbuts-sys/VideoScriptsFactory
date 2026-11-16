# Visitor-access viewpoint review

User requirement: never generate images from viewpoints in places restricted to visitors. This also governs
reuse. The camera must stay on the visitor side for the whole shot, including close shots, top-down shots and
camera moves. A staff member may be the subject without the creator entering their workspace. Do not assume
special permission or invent public access to justify the shot.

This targeted review identifies existing examples requiring correction or access verification. It is not a
complete clearance of the 304-step set. Historical image approvals and successful export validation predate
this constraint; they do not certify that a visitor can stand at the illustrated camera position. No images
were regenerated in this policy update.

## Flagged existing viewpoints

| Preview | Issue | Visitor-side alternative |
|---|---|---|
| `bakery-fresh-batch_oven` | Camera inside the bakery's oven/prep workspace. | Show the tray presented at the customer counter; show oven work only through an actual public viewing window. |
| `bakery-morning-shift_lights` | View into the production area rather than the customer shop. | View from the public street through the shopfront, or from customer seating during visitor access. |
| `bakery-morning-shift_oven` | Camera beside the baker in the oven workspace. | Fresh tray arriving at the customer-facing display. |
| `bakery-ask-the-baker_hands` | Directly above dough on a staff prep bench. | Customer-side view across a visible public counter; otherwise show the baker presenting the finished pastry. |
| `bakery-morning-shift_dough` | Shares the same prep-bench image. | Update with its canonical image after visitor-side review. |
| `cafe-before-opening_dial` | Behind the barista at the grinder and espresso machine. | Watch from the customer side, with the counter boundary visible. |
| `cafe-before-opening_shot` | Close view at the machine's staff working position. | Espresso served at the public pickup counter; retain extraction only if visible from a visitor position. |
| `restaurant-chef-pick_hands` | Overhead inside the kitchen plating workspace. | Plate presented across the customer-facing service boundary or finished plate on a dining table. |
| `restaurant-chef-pick_cook` | Behind the chef in the kitchen. | Face the chef from a public viewing position, or show the dish arriving at the table. |
| `quick-the-build_grill` | Camera over the staff-side griddle workspace. | View from a real public counter/window, otherwise use the finished burger at pickup. |
| `quick-late-night_griddle` | Shares the same griddle image. | Update with its canonical image after visitor-side review. |
| `quick-the-build_build` | Behind the cook on the preparation line. | Customer-side view of assembly only if visible across the public counter. |
| `quick-the-build_wrap` | Overhead prep-line viewpoint needs a visitor-access check. | Wrapped order handed across the customer pickup counter. |
| `pro-before-after_detail` | Over the technician's shoulder at the repair bench. | Face the technician across the customer counter; show the repaired object on the visitor side. |
| `pro-meet-the-owner_craft` | Behind the owner at the repair bench. | Face the owner from the customer side of the counter. |
| `pro-what-it-costs_three` | Over the repair technician's shoulder at the bench. | Customer-facing demonstration across the service counter, or the finished result. |
| `shop-budget-challenge_till` | Behind the cashier, looking at the staff-facing register. | Customer-side payment terminal, receipt, or packed purchases. |

Also verify the camera position for tap pours (`bar-happy-hour_pour`, `food-review-pour_build`) and other
equipment close-ups. A staff subject facing the lens does not establish that the camera is on the public side.
An over-the-shoulder shot is acceptable when it is over the visitor's shoulder in a customer area; the angle
name alone does not determine access.

## Before the next generation or reuse

1. State where an ordinary visitor can stand and keep that boundary clear in the prompt.
2. Adapt conflicting script directions and shot plans, recording the visitor-side alternative. Keep the
   subject and action when visible from the public area; otherwise use the served item or hand-off.
3. Append the mandatory visitor-access constraint from `prompts.md`. Treat reference images as style input;
   their camera positions are not exemptions.
4. Inspect the generated or reused image for the physical camera position before approving it. Fix canonical
   images and all their shared aliases together. Preserve historical prompts as provenance.
