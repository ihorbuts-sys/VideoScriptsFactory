"""Keep the three commercial lessons visible, then verify their API and report scope."""
import json,shutil,subprocess,sys,time
from pathlib import Path
import commercial_core_gallery as gallery
BASE=gallery.BASE
ROOT=BASE/'catalog/glass-rollout'
SERVER=Path('/Users/ihor.buts/Documents/Development/Scriptwriter')
KEYS=['commercial-display','commercial-texture','commercial-room']
TARGETS={'bakery-fresh-batch.shelf','bakery-fresh-batch.break','bakery-sell-out.break','bakery-ask-the-baker.inside','restaurant-date-night.room'}
def read(p):return json.loads(p.read_text())
def write(p,r):p.write_text(json.dumps(r,indent=2)+'\n')

def run():
    deadline=time.monotonic()+7200;previous=None
    while True:
        ready=tuple(k for k in KEYS if (ROOT/'coffee'/k/'publication.json').exists())
        if ready!=previous:gallery.run();previous=ready
        if len(ready)==3:break
        assert time.monotonic()<deadline
        time.sleep(5)
    subprocess.run([sys.executable,str(BASE/'api/check_glass_batch_live.py'),'--server',str(SERVER)],check=True)
    subprocess.run([sys.executable,str(BASE/'api/check_withdrawn_grips.py')],check=True)
    with (ROOT/'validation/typed-scenarios.json').open('w') as out,(ROOT/'validation/typed-scenarios.log').open('w') as err:
        subprocess.run(['swift','run','--package-path','/private/tmp/loca-glass-scenario-check','--scratch-path','/private/tmp/loca-glass-scenario-check/.build','--disable-index-store','ScenarioCheck',str(BASE)],stdout=out,stderr=err,check=True)
    before=read(gallery.OUT/'catalog-before.json');after=read(SERVER/'catalog/catalog.json')
    assert before['guides']==after['guides'] and before['previewArt']==after['previewArt']
    for t in before['templates']:
        current=next(r for r in after['templates'] if r['id']==t['id'])
        for s in t['steps']:
            if t['id']+'.'+s['id'] not in TARGETS:assert s==next(r for r in current['steps'] if r['id']==s['id'])
    for key,value in before['stepGuideOverrides'].items():
        if key not in TARGETS:assert value==after['stepGuideOverrides'][key]
    assert before['scriptGuideSequences']==after['scriptGuideSequences']
    scope=dict(status='passed',changed_step_bindings=sorted(TARGETS),guide_defaults_preserved=True,preview_art_preserved=True,
        unrelated_steps_preserved=True,unrelated_overrides_preserved=True,full_script_sequences_preserved=True)
    write(gallery.OUT/'api-scope-check.json',scope)
    live=read(ROOT/'live-api-check.json');typed=read(ROOT/'validation/typed-scenarios.json')
    assert live['unique_glass_guides']==23 and live['template_bindings']==26 and len(typed['guides'])==23
    reviews={k:read(ROOT/'coffee'/k/'commercial-review.json') for k in KEYS}
    assert all(r['status']=='passed' and r['no_humans'] and r['no_hand_animation'] and r['visual_preview_review'] for r in reviews.values())
    result=dict(status='complete',date='2026-11-02',scenes=KEYS,new_step_bindings=sorted(TARGETS),native_frames=330,native_animation_seconds=22,
        no_humans=True,no_hand_animation=True,paid_generation_credits_used=0,commercial_reviews=reviews,
        embedded_browser_checks_passed=True,api_scope_check='api-scope-check.json',rejected_hand_studies_withdrawn=True,
        unique_glass_guides=23,total_step_bindings=26,typed_scenarios=23,live_downloaded_assets=live['downloaded_assets'],
        image_view_opacity=.65,architecture_in_ghost=False,viewfinder_separate=True,preview_background_delay_seconds=2,
        physical_iphone_recording_verified=False,pdf_regenerated=False)
    write(gallery.OUT/'completion.json',result)
    (gallery.OUT/'README.md').write_text('''# Practical commercial shots, 2 November 2026

[Play the three lessons](http://127.0.0.1:8766/commercial-core/index.html). Each has a filming purpose, staging notes, an achievable visitor-side phone move, a color reference and an object-only ghost.

|Template|Step|Guide|Capture|Animation|
|---|---|---|---|---|
|Fresh batch|The case|shelf_slide_left|5 s|7 s|
|Fresh batch|The break|pastry_break_eye_hold|5 s|7 s|
|Before it sells out|Inside|pastry_break_eye_hold|5 s|7 s|
|Ask the baker|Inside|pastry_break_eye_hold|5 s|7 s|
|Date night|The room|room_dining_eye_reveal_cw|6 s|8 s|

Display: show the available range with a level row and a short sideways step. Product detail: show already-opened halves and filling from a rising arc while the food stays supported. Room: move backward and slightly right while rising, revealing the same table, chairs, window and lighting. No characters, animated hands, moving props or digital zoom. The three shots are separate takes with deliberate cuts.

The batch reuses the existing display case, approved pastry halves, plates, cups, dining table/chairs and café set. No paid generation. All 330 native camera positions pass 8 cm geometry-clearance tests. Product framing and support are checked, and source color probes were visually inspected before full rendering. These checks constrain the guide; they do not promise a commercial result in every real venue.

Raw hero surfaces remain full strength. Apply 65% opacity once in the image view. Context is softer, walls/floor/ceiling are excluded, and viewfinder/level remain separate UI. Only the review simulation delays the background reference by two seconds.

The coffee and tong grips from the earlier batch were rejected by the owner and withdrawn from the active API. Their prior step bindings and bakery sequence are restored. Hand manipulation is deferred; numeric contact and wrist checks do not establish a natural grasp. [Withdrawal evidence](../interaction-scenes/withdrawal/live-api-check.json).

See [shot priorities](priorities.md), [completion](completion.json), [API scope checks](api-scope-check.json), and each scene's commercial-review.json and composite-browser-check.json. Physical iPhone capture is untested. The PDF is not rebuilt.

Builder: model_refferences/objects/tools/build_commercial_core.py. Source scene files: ../glass-rollout/coffee/commercial-*/scene.blend.
''')
    archive=ROOT/'creator-interaction-2026-11-02-withdrawn.json'
    if not archive.exists():shutil.copy2(ROOT/'completion.json',archive)
    current=read(ROOT/'completion.json');current.update(status='commercial_core_batch_complete',date='2026-11-02',unique_guides=23,step_bindings=26,
        remaining_guides=155,new_guides=['shelf_slide_left','pastry_break_eye_hold','room_dining_eye_reveal_cw'],new_context_variants=[],
        complete_glass_script_sequences=live['complete_glass_sequences'],live_downloads=live['downloaded_assets'],typed_scenarios=23,
        current_batch_frames=330,current_batch_animation_seconds=22,rejected_hand_studies_withdrawn=True,
        previous_milestone=archive.name,canonical_character=None,reused_primary_models=['display_case','croissant_oozing','dinner_plate','latte_cup','dining_table','dining_chair'])
    write(ROOT/'completion.json',current)
    report=ROOT/'report.md';s=report.read_text();s=s.replace('20/178 unique guides across 21 step bindings','23/178 unique guides across 26 step bindings').replace('158 remain for this treatment','155 remain for this treatment')
    section='''## Practical commercial lessons, 2 November 2026

[Play the three new camera-only guides](http://127.0.0.1:8766/commercial-core/index.html): a level pastry-display sweep, a rising filling-detail arc and a window-side room reveal. They update five script steps using existing models, no characters and no paid generation. All 330 native frames passed camera-clearance checks; staging, product support, framing and color probes were reviewed. Each player passed embedded-browser playback, opacity and separate-viewfinder checks.

These lessons teach available range, product detail and atmosphere. They are individual takes with deliberate cuts. Full color and 65% object-only ghosts share the same camera. See [purpose and setup](../commercial-core/README.md), [priorities](../commercial-core/priorities.md), and [evidence](../commercial-core/completion.json). The earlier coffee and tong attempts remain withdrawn after owner review.

'''
    s=s.replace('## Current priority:',section+'## Current priority:',1)
    rows='''|Fresh batch|The case|`shelf_slide_left`|5|7.00|
|Fresh batch|The break|`pastry_break_eye_hold`|5|7.00|
|Before it sells out|Inside|`pastry_break_eye_hold`|5|7.00|
|Ask the baker|Inside|`pastry_break_eye_hold`|5|7.00|
|Date night|The room|`room_dining_eye_reveal_cw`|6|8.00|
'''
    s=s.replace('\n\n## Display and verification','\n'+rows+'\n## Display and verification',1)
    lines=s.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('- Last live API check:'):lines[i]='- Last live API check: 23 guides / 26 bindings / '+str(live['downloaded_assets'])+' downloaded, hash-checked assets. The complete Morning ritual remains published. Rejected grip collections return 404; their prior step bindings and bakery sequence are restored. Preview art and unrelated overrides are preserved.'
        if line.startswith('- Last typed Swift scenario check:'):lines[i]='- Last typed Swift scenario check: 23 active guide scenarios. No SDK source changes were needed for this batch.'
    report.write_text('\n'.join(lines)+'\n')
    p=BASE/'README.md';s=p.read_text();needle='## Current priority: practical commercial shots';intro='''## New camera-only commercial guides (2 November 2026)

[Play the three lessons](http://127.0.0.1:8766/commercial-core/index.html): pastry-display range, opened-pastry detail and a window-side room reveal. Three native scenes update five script steps, with no human rigs or hand manipulation. Existing models, color and 65% ghosts, separate viewfinder/level and API publication. Camera, embedded-browser, scope-preservation and typed checks passed. See [report and app steps](catalog/commercial-core/README.md).

''';s=s.replace(needle,intro+needle,1);p.write_text(s)
    subprocess.run([sys.executable,str(Path(__file__).with_name('coffee_glass_progress.py'))],check=True)
    gallery.run();print('COMMERCIAL_CORE_COMPLETE',flush=True)

if __name__=='__main__':run()
