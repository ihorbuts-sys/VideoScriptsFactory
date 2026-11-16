"""Register the checked espresso clip for the existing Before opening step."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'catalog/coffee-ordering-v2'
MANIFEST = BASE / 'catalog/clay-scenes/active-revisions.json'
GUIDE = 'cup_shot_eye_in_cd_through'


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def prepare():
    source = json.loads((SOURCE / 'scene-spec.json').read_text())
    export = json.loads((SOURCE / 'export-checks.json').read_text())
    browser = json.loads((SOURCE / 'browser-check.json').read_text())
    audit = json.loads((SOURCE / 'scene-audit.json').read_text())
    assert export['status'] == browser['status'] == audit['status'] == 'passed'
    assert browser['ghost_sha256'] == export['files']['ghost.png']
    assert export['whole_overlay_alpha'] == .65 and export['max_alpha'] <= 166
    phase = next(p for p in source['exported_phases'] if p['id'] == 'extraction')
    folder = SOURCE / 'phases/extraction'
    files = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
             for name in ['ghost.png', 'ghost-poster.png', 'ghost-strip.jpg', 'color.mp4']}
    write(folder / 'scene-spec.json', dict(
        id=GUIDE, scope='complete_final_shot', duration_s=phase['animation_seconds'],
        capture_seconds=5, fps=source['fps'], frame_count=phase['frames'],
        handover_status='cut_to_next_step', next_guide='cup_high_out_dm',
        transition_method='cut_at_step_boundary', source_scene='../../scene.blend',
        source_first_frame=phase['source_first_frame'],
        source_last_frame=phase['source_last_frame'],
        same_scene_settle_seconds=phase['handover_seconds'],
        whole_overlay_alpha=.65, viewfinder_embedded=False,
        ghost_style=source.get('ghost_style'),
        note='Espresso extraction and a continuous camera settle in the same scene. '
             'The next script step is a cut; no handoff performance is claimed.'))
    write(folder / 'export-checks.json', dict(
        status='passed', whole_overlay_alpha=.65,
        max_ghost_alpha=phase['export_checks']['max_alpha'],
        files=files, frames=phase['frames'], seconds=phase['animation_seconds'],
        source_export_checks='../../export-checks.json'))
    manifest = json.loads(MANIFEST.read_text())
    manifest['guides'][GUIDE] = dict(
        reviewed=True,
        reviewer='Rendered frame review, scene geometry audit, APNG timing/alpha and browser playback checks',
        scope='complete_final_shot', handover_status='cut_to_next_step',
        folder=str(folder.relative_to(BASE)), context_template='cafe-before-opening',
        context_step='shot', revision=source.get('revision', 'coffee-left-milk-v2'),
        rendering='native-3d-clay-espresso-extraction-and-camera-settle'
                  + ('; smooth-contours-v1' if source.get('ghost_style') else ''),
        direction='Stay on the customer side at cup height. Follow both espresso streams '
                  'with a slow diagonal lean toward the cup, then raise the phone slightly '
                  'and settle. Keep the cup and crema in focus. Record about five seconds; '
                  'cut to the next step after the shot.',
        files=files)
    write(MANIFEST, manifest)
    print(json.dumps(dict(status='prepared', template='cafe-before-opening', step='shot',
                         guide=GUIDE, animation_seconds=phase['animation_seconds'])))


if __name__ == '__main__':
    prepare()
