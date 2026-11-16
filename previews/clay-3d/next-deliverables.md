# Authorized follow-up deliverables

The user requested these after finishing the current step-preview collection:

1. Publish the finished reviewed illustrations through the existing API, preserving older art and avoiding stale image URLs.
2. Inventory reusable objects used by the guide animations.
3. Make six-view object reference pictures: front, back, left, right, top and bottom.
4. Create reusable Blender models matching the approved whole-world plasticine art direction, so guide animations can use the same style.

Keep Blender closed unless the user explicitly asks to launch it. Prefer shared object families over duplicate models per scene. Existing character references are in `model_refferences/`; preserve the three accepted identities and the locs friend's accepted appearance. Preview illustration rollout remains the first priority. Do not rerun `tools/plasticine_v2.py`, which invalidates existing revisions; resume `manifest.json` through `tools/workflow.py` and the built-in image generator.
