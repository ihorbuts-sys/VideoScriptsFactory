# Workflow: a new script with its shot guides

Repo: this folder (`~/Documents/Development/VideoGuides` links here). Code, rules, briefs and data are in git;
renders, scenes and models stay on disk, pinned by `assets/manifest.json` (`guides/tools/asset_manifest.py`).

| Role | Skill | Runs in | Output |
|---|---|---|---|
| Script composer | `skills/script-composer` | the main agent | the script in `scripts/_parts/<kind>.json`, `scripts/<kind>/<template id>/NOTE.md`, guide requests |
| Guide animator | `skills/guide-animator` (agent `agents/guide-animator.md`) | a separate agent per guide request | a draft guide in `scripts/<kind>/<template id>/guides/<guide id>/`, or an object request |
| Guide objects | `skills/guide-objects` | both | object checks, swap templates, requests in `OBJECTS.md` |
| Object renderer | `skills/object-renderer` (agent `agents/object-renderer.md`) | a separate agent per run | line-art stills of objects in `guides/review/objects_renders/`, the objects page, candidate renders for requests |
| Step previews | `skills/step-previews` | the main agent (generation in an image model) | one plasticine picture per step, the scene all of its guides share |
| Guide publish | `skills/guide-publish` | the main agent, after the owner approves | registry entry, `guides/p0/renders/`, manifest, index, live server |

```
owner brief
  -> script-composer: story, steps, levels, reuse from GUIDE_INDEX.md (recommended / option)
       -> missing guide at the step's level: guide request (requests/<guide id>.md)
            -> guide-animator agent (own context): template, objects check
                 -> object missing: object request in OBJECTS.md, stop, owner decides
                 -> else: draft render + export + checks + contact sheet in the script folder
  -> step-previews: one preview per step, the scene all of its guides share, from an angle none contradicts
  -> owner reviews the script note, the drafts and the previews
  -> guide-publish: promote approved drafts, rebuild, stage, diff, publish, verify
```

Step length (owner 2026-11-10): a guided step lasts its first guide's loop, or longer so the creator can finish the
line: min(8, max(guide durationSec, ceil(words / 2.5 + 1))). A line that would need over 8 s or 140 characters is
an error in `check_scripts.py` and in the Scriptwriter writer; `step_fields.step_seconds` is the one computation.

Shared files: `STYLE.md` (the one style), `GUIDE_INDEX.md` (generated reuse table), `OBJECTS.md` (objects and
requests), `guides/p0/guide_levels.json` (levels and beats), `catalog/p0/RUNBOOK.md` (exact commands).

Never: commit, publish or generate a model without the owner's word; use a retired style (`STYLE.md` lists them);
edit an active guide's scene code without re-rendering it and the guides that share its builder.
