# Catalog versions

Each folder is a full snapshot of the script catalog at one version, so a release can be rolled back.

| Folder | Holds |
|---|---|
| `_parts/` | the per-kind source files (`scripts/_parts/*.json`) |
| top level | `script_templates.json`, `opinion_sets.json`, `shot_plan.json`, `p0_scope.json`, `step_shot_types.json` |
| `scriptwriter_catalog/` | the served dev catalog (`Scriptwriter/catalog/catalog.json`, `shot_types.json`) |
| `kit/` | the editor kit's bundled `script_templates.json` |
| `manifest.json` | every file, where it restores to, sha256 and size |

Roll back (dry run first, then apply; live files are saved to `_replaced/<timestamp>/` before overwrite):

    python3 -I scripts/versions/restore.py v2_2026-11-16
    python3 -I scripts/versions/restore.py v2_2026-11-16 --apply

After a restore: `check_scripts.py --merge`, the bundle build, then publish through the `guide-publish` skill. The
backend doc has its own snapshots in `Loca/.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/doc_versions/`.

Take a new snapshot before every catalog version change (copy the files, write the manifest with sha256), and add a
line to `CHANGELOG.md`.
