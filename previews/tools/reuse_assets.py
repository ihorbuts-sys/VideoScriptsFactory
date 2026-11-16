"""Apply reviewed reuse decisions while preserving superseded exports and provenance."""
import copy
import fcntl
import json
import re
import shutil

from preview_assets import ROOT, OLD, normalize, save


def main():
    plan = json.loads((ROOT/'reuse-plan.json').read_text())
    old_notes = (ROOT.parent.parent/'script-image-prompts.md').read_text()
    old_prompts = dict(re.findall(r'\*\*([^*]+)\.png\*\*[^\n]*\n\n(.*?)\n\nSize:', old_notes, re.S))
    archive = ROOT/'reuse-audit/superseded'
    archive.mkdir(parents=True, exist_ok=True)
    with (ROOT/'.manifest.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads((ROOT/'manifest.json').read_text())
        entries = {e['stem']: e for e in manifest['entries']}

        def preserve(entry):
            stem = entry['stem']
            metadata = archive/f'{stem}.json'
            if not metadata.exists():
                metadata.write_text(json.dumps(entry, indent=2)+'\n')
                for suffix in ('png', 'jpg'):
                    shutil.copy2(ROOT/f'{stem}.{suffix}', archive/f'{stem}.{suffix}')
            entry['superseded_for_reuse'] = str(metadata.relative_to(ROOT))

        for stem in plan['restore_project']:
            entry = entries[stem]
            if entry.get('reuse', {}).get('kind') == 'project-original':
                continue
            preserve(entry)
            source = OLD/entry['imageURL']
            entry.update(status='reused', source=str(source), source_size=normalize(source, stem),
                         prompt=old_prompts[stem], reference_images=[],
                         reuse=dict(kind='project-original', canonical_stem=stem,
                                    reason='Original project image fits the step subject and starting view; reuse preferred.'),
                         review='Original project illustration restored after reuse audit; subject and starting view reviewed.')
            entry.pop('replaces_existing', None)

        for decision in plan['aliases']:
            entry = entries[decision['target']]
            canonical = entries[decision['canonical']]
            if canonical.get('reuse', {}).get('canonical_stem', canonical['stem']) != canonical['stem']:
                raise ValueError('Canonical sources must be roots, not aliases.')
            preserve(entry)
            for suffix in ('png', 'jpg'):
                shutil.copy2(ROOT/f'{canonical["stem"]}.{suffix}', ROOT/f'{entry["stem"]}.{suffix}')
            entry.update(status='reused', prompt=canonical['prompt'], source=canonical['source'],
                         source_size=canonical['source_size'],
                         reference_images=copy.deepcopy(canonical.get('reference_images', [])),
                         reuse=dict(kind='shared-step', canonical_stem=canonical['stem'], reason=decision['reason']),
                         review='Shared illustration visually reviewed for subject, viewpoint and starting framing. '+decision['reason'])
            entry.pop('replaces_existing', None)
        save(manifest)
    print(f'Restored {len(plan["restore_project"])} originals; shared images for {len(plan["aliases"])} additional steps.')


if __name__ == '__main__':
    main()
