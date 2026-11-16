# First Blender guide experiment

This study implements `bar_low_truckr_mm` from the existing scene description and the
`restaurant-room-tour` script. The owner requested a Blender test after stopping the
sprite rollout. This is a separate proof, not a catalog-wide replacement.

The installed Blender is 5.2.3 LTS. No connector, add-on, downloaded model, or generated
sprite is required. Geometry, cameras, animation and visible contours are native Blender data.

Open `Play in Blender.command` to launch the saved scene with timeline playback started
automatically. Space pauses and resumes. The left panel plays the actual transparent ghost
with fixed framing guides. The right panel shows the editable, lit 3D camera view with the
same timing. The native preview references the local `ghost_frames/` PNG sequence.
`viewport-state.json` reports actual UI playback state while this launcher is running.

The sources are `guides/templates/bar_low_truckr_mm.json`, the corresponding live scenario
and 3D camera reference, and `guides/script_templates.json`. The bar step specifies a rightward
truck followed by a cut; its actual successor is `seat`, using `table_seat_high_in_mc`.
The sample follows that cut rather than inventing continuous travel between those locations.
The composition pass uses a fixed 10-degree oblique bar view for converging leading lines;
the low elevation, rightward truck and 0.8 m travel remain intact. The high table camera is
slightly oblique so the opposing settings form a depth diagonal rather than a flat row.

| Time | Action |
|---|---|
| 0.0–1.2 s | Hold the low bar framing |
| 1.2–3.0 s | Move the camera 0.8 m right with constant lens, orientation and height |
| 3.0–4.0 s | Hold the finishing bar frame |
| 4.0–5.6 s | Cut to the actual next shot: a high table view, beginning its approach |

The low camera is 1.05 m above the floor, points upward by 12 degrees, and stays in the public
customer aisle at y=-2.2 m. The counter top is at z=1.14 m. Glass bases are fixed at exactly
that height. The 48 cm dining chairs face their own plates, with forks on each diner's left,
inward-facing knives on their right and water glasses above the knives. Stools, the counter,
taps and backbar shelves occupy real depths. Their different
screen speeds and occlusion follow the camera projection, with no per-object drift or zoom.

The table segment demonstrates the handover and beginning of the next step, not that step's
entire four-second take. This proof has no actor or hand animation. It establishes camera
translation, depth, physical contacts and a contextual cut; it does not establish a production
workflow for all other guide types or the final watercolor treatment. The composition method
and source references are in `../../guides/cinematic_composition.md`.

`build_scene.py` creates reusable lathed hollow glassware, bottle profiles, rounded joinery,
curved stool legs/backs, swept tap pipes, shelves and place settings. Mesh surfaces provide
occlusion but are excluded from the final picture. Freestyle's visible-line pass supplies
the pale blue contours on transparency. A subsequent owner-requested trial adds faint flat
pale-blue surface fills, now 25% on main objects and 6.25–20% on other roles. Walls, ceilings,
floors and lighting-set geometry stay unfilled. The previous contour-only exports are preserved
in `bar_low_truckr_mm/outline-only/`. Masks are depth-tested native Blender renders, so overlapping
objects do not accumulate fill. The only 2D drawing
in export is the review viewfinder, level reference and thirds grid.

Ghost opacity follows instructional role: main objects 50%, useful background landmarks 39%,
support 34%, near framing 24%, structure 20%, decorative background 12.5%. These are nominal
maximum layer values after the final alpha pass; crossing strokes can combine. Depth alone
does not determine opacity. The taps and selected distant bottles remain clearer than nearby
decorative context. `object-composition-plan.json` records roles, locations and reasons for
125 mesh components, plus the selected lighting cues.

Fixed morning sunlight enters through a real side window in the separate lighting scene.
For the ghost, window-facing portions of the glass/plate rims are yellow. Faint yellow lines
mark actual projected window/shadow boundaries clipped to the tabletop and occluded by its
objects. These are world-attached 3D cues, not a full-frame shaded picture. The companion
`lighting.mp4` shows the underlying illumination, while `lighting_setup.png` shows the window.
Light sources have no animation. The cue geometry is excluded from the lighting reference.

Raw renders remain unchanged in `bar_low_truckr_mm/frames/`. The exporter copies RGB unchanged
and multiplies alpha by 0.5 once. The page displays the resulting artwork without another opacity
multiplier. The neutral backing in the MP4 and contact sheet is for review only.

Outputs are `scene.blend`, transparent `guide.png`, `guide_with_guides.png`, `preview.mp4`, `lighting.mp4`,
`strip.jpg`, and the scene/export check reports in `bar_low_truckr_mm/`.
The 84 timeline frames play at 15 fps for 5.6 seconds. The APNG encodes 52 frames because
identical hold frames are combined, preserving the exact total duration.

Checks cover monotonically rightward travel, constant camera orientation, customer-side
positions, ordered near/middle/far image displacement, glass contact, stable holds, visible
truck movement, a visible next-shot cut, alpha/RGB preservation and output duration. The
contact sheet was visually reviewed. No people are present. Blender's Freestyle renderer
prints some triangle-correction warnings and empty-stroke messages for groups outside the
current shot; all frames rendered successfully. Actual ghost frames have about 96.6–98.4%
fully transparent pixels in the sampled start, middle and table views.

To rebuild from this directory:

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" --background --factory-startup --python build_scene.py --python add_lighting.py
"/Applications/Blender.app/Contents/MacOS/Blender" --background bar_low_truckr_mm/scene.blend --python render_sequence.py
/private/tmp/loca-guide-playback-venv/bin/python export_sequence.py
"/Applications/Blender.app/Contents/MacOS/Blender" --background bar_low_truckr_mm/scene.blend --python render_sequence.py -- --lighting
"/Applications/Blender.app/Contents/MacOS/Blender" --background bar_low_truckr_mm/scene.blend --python render_sequence.py -- --lighting --probes
/private/tmp/loca-guide-playback-venv/bin/python export_lighting.py
"/Applications/Blender.app/Contents/MacOS/Blender" --background bar_low_truckr_mm/scene.blend --python add_native_preview.py
```

Open `index.html` for the looping transparent preview and the framing-guide controls.
The existing catalog, production overlays, script previews, PDF and API assets are unchanged.

To reproduce the faint-fill trial, run `render_color_fill.py` in Blender after the scene file,
then run `export_sequence.py` again. `fill_frames/` retains the source masks and
`color-fill-settings.json` records the pigment and nominal alpha values. Composition happens
before the single final whole-frame alpha pass. The native preview has a separate
`app-preview-filled25.mp4`. The earlier 10% and outline-only recordings remain available
for comparison, along with the 10% exported assets in `bar_low_truckr_mm/fill-10/`.
