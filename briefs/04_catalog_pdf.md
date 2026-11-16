# Brief 04: the catalog PDF

Skill to load: `guides-catalog-pdf` (`Loca/.claude/skills/guides-catalog-pdf/SKILL.md`).
Input: everything in `ScriptsAndGuides/scripts/`, `previews/` and `guides/`.
Output: `ScriptsAndGuides/catalog/scripts-and-guides.pdf` and the HTML it was built from.

## What to deliver

One PDF, A4 landscape, one chapter per script kind:

1. A kind page: the kind's title, the production categories it covers, the best-practice summary (five lines at
   most, from `research/best_practices/<kind>.md`).
2. One page per script: title and summary; a row of step previews (the images from `previews/`) with the step
   title, shot, length and the spoken line or text under each; under that, the guide previews for each step in
   both styles (a strip of 4 to 6 frames from the schematic APNG, and the 3D preview strip), with the guide's id.
3. An appendix: the menu-item kinds audit and which review script covers each; the guide coverage table.

## How to work

- Build HTML first (one file, local images), then render to PDF with the method in the skill; check page breaks
  so a script never splits a step row from its guide row.
- Strips from APNGs: extract 4 to 6 evenly spaced frames with the skill's script; do not paste a single frame.
- Keep text to what a reviewer needs to pick scripts and judge guides; the reasoning files stay in the folders.

## Done when

Every script in `script_templates.json` has its page, every page shows every step's preview and both guide
strips, and the PDF opens with no missing images.
