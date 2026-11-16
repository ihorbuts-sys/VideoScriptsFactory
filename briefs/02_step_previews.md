# Brief 02: step preview images

Skill to load: `step-previews` (`Loca/.claude/skills/step-previews/SKILL.md`).
Input: `ScriptsAndGuides/scripts/script_templates.json` and `scripts/<kind>/*.md` from agent 01.
Output folder: `ScriptsAndGuides/previews/`.

## What to deliver

1. One image per step of every script: `previews/<template id>_<step id>.png`, 1080 x 1920, the step as the
   creator will see it in the step card: the subject, the framing the step asks for, the venue type readable at a
   glance. Same style across the whole set (the style block is in the skill).
2. `previews/prompts.md`: the prompt used for every image, so a step can be regenerated later.
3. `previews/review.md`: which images missed the step's framing or subject and were redone; which steps have no
   good image yet.

## How to work

- Draw makeup scenes more schematically: simple face contours, minimal facial marks, flat cosmetic color
  areas and a clear applicator/action. Avoid realistic skin, detailed lashes or eyes and glossy beauty shading.
  Apply the same check before reusing an image.
- At most two visible hands total per image, including partial hands and hands across different people.
  Frame other hands out; reject extra, duplicated or detached hands. Check reused images too.
- Use only viewpoints accessible to ordinary visitors, including for reused images. Film staff activity from
  the customer side of a counter or a public viewing window; never from a kitchen, staff prep area, behind
  a till, or another restricted position. Do not assume special access. Adapt conflicting shot plans before
  generation and record the visitor-side alternative. Check the camera's position as well as its subject.
- The step card shows the image small (about 72 pt tall in a strip, larger on the card), so one clear subject and
  a readable framing matter more than detail.
- The existing 38 step images are in `VideoEditorKit/Sources/VideoScripts/Resources/StepPreviews/`; match their
  look so old and new scripts sit together.
- Generate in batches per script, check the whole script's strip together for consistency, then move on.

## Done when

Every step in `script_templates.json` has an image with the exact file name its `imageURL` names, and
`prompts.md` lists them all.
