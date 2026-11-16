"""Index the reviewed canonical-creator guide performances and their evidence."""
import html
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
OUT=BASE/'catalog/creator-scenes'


def run():
    OUT.mkdir(exist_ok=True)
    catalog=json.loads(Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/catalog.json').read_text())
    cards=[];rows=[]
    for key in ['creator-cafe','creator-bakery']:
        p=ROOT/key;s=json.loads((p/'scene-spec.json').read_text())
        performance=json.loads((p/'performance-check.json').read_text())
        browser=json.loads((p/'composite-browser-check.json').read_text())
        assert performance['status']==browser['status']=='passed'
        assert json.loads((p/'publication.json').read_text())['status']=='published'
        t=next(t for t in catalog['templates'] if t['id']==s['template'])
        step=next(step for step in t['steps'] if step['id']==s['step'])
        prefix='../glass-rollout/coffee/'+key+'/'
        cards.append(f'''<article><h2>{html.escape(s['title'])}</h2><p>{html.escape(t['title'])} / {html.escape(step['title'])}</p>
<img class="poster" src="{prefix}color/frame_0039.png" alt="{html.escape(s['title'])} / gesture pose">
<p><a class="play" href="{prefix}index.html">Play color and ghost</a></p><p>{html.escape(s['direction'])}</p>
<p>{s['duration_s']:g} seconds at 15 fps; {s['capture_seconds']:g}-second capture.</p>
<details><summary>Frames and source</summary><img class="strip" src="{prefix}color-strip.jpg" alt="Creator pose samples">
<p><a href="{prefix}scene.blend">Blender scene</a> · <a href="{prefix}performance-check.json">Pose checks</a></p></details></article>''')
        rows.append(dict(scene=key,title=s['title'],template=s['template'],step=s['step'],guide=s['guide'],
            app_template=t['title'],app_step=step['title'],frames=s['frame_count'],seconds=s['duration_s'],
            step_endpoint='/v1/steps/'+s['template']+'.'+s['step']+'/guides',
            collection_endpoint='/v1/guide-collections/coffee-guide-'+key,performance=performance))
    (OUT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loca / creator scenes</title><style>body{font:16px/1.5 system-ui;background:#f2ede3;color:#293b32;max-width:1050px;margin:auto;padding:24px;box-sizing:border-box}h1{line-height:1.15}h2{font-size:22px}a{color:#326c52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:22px}article{min-width:0;padding:24px;border-radius:22px;background:#fffaf0}.poster{display:block;width:100%;height:470px;object-fit:contain;border-radius:14px}.strip{width:100%;object-fit:contain}.play{display:inline-block;background:#326c52;color:white;border-radius:30px;padding:10px 18px}summary{cursor:pointer}p{overflow-wrap:anywhere}</style>
<p><a href="../animations.html">All guides</a> · <a href="../food-scenes/index.html">Food scenes</a></p><h1>Our creator / two performances</h1>
<p>The same canonical creator, animated with her existing body rig. Each player includes full-color video and an object-only glass guide at 65% image-view opacity, with separate viewfinder and level. Press Play; the demonstration background follows two seconds behind the guide.</p>
<p>These clips demonstrate framing, eye contact and small gestures. Her original facial expression is preserved; lip sync has not been added. Both shots end with a deliberate cut to the next step.</p><div class="grid">'''+''.join(cards)+'</div></html>\n')
    completion=dict(status='published',date='2026-10-30',scenes=rows,new_tripo_credits=0,
        canonical_character='creator',source_frames=sum(r['frames'] for r in rows),
        total_seconds=sum(r['seconds'] for r in rows),image_view_opacity=.65,raw_global_opacity=1,
        viewfinder_embedded=False,architecture_embedded_in_ghost=False,full_script_sequence_complete=False,
        lip_sync_added=False,physical_iphone_capture_verified=False)
    (OUT/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')
    lines=['# Canonical creator scenes, 30 October 2026','',
        '[Play both creator scenes](http://127.0.0.1:8766/creator-scenes/index.html).','',
        '|App template|Step|Guide|Animation|Capture|','|---|---|---|---|---|']
    lines += [f"|{r['app_template']}|{r['app_step']}|`{r['guide']}`|{r['seconds']:g} s|6 s|" for r in rows]
    lines += ['',
        'Both shots reuse the canonical female creator and her original 65-bone rig. No model generation, paid rigging or segmentation was submitted. The original GLB is hash-verified and preserved. Scene-only simplification reduces large mesh parts while retaining the rig, original face, hair, clothing, bag and hand anatomy.',
        '',
        'The cafe performance uses a small open-hand acknowledgement and nod. The higher-angle bakery performance presents the actual pastry case from its customer side. The cafe coffee setup is removed in that bakery scene; the case and rack stand on the floor. The free hand follows a two-bone reach with an explicit elbow pole, comfortable wrist limits and the original finger chains. The other arm remains relaxed. Head and neck share the turn; chest motion provides gentle breathing. Phone drift is small and the lens is fixed throughout each take.',
        '',
        'All 210 native frames are checked for face visibility, hand scale, wrist bend and planted feet. Hairstyle bounds are checked at the start, gesture and end poses. Both movies have browser Play/Stop/replay, independent opacity/viewfinder, mobile layout and APNG-only motion checks. See completion.json and the per-scene performance-check.json and composite-browser-check.json.',
        '',
        'These are context-specific replacements: cafe-first-visit.outro and bakery-box.hook. Other scripts sharing the two guide IDs retain their existing artwork. Each clip is a complete individual take with an explicit cut, not a new full-script sequence. Recommended capture remains six seconds.',
        '',
        'Color and ghost use the same native camera and timing. Color uses native denoising; the ghost passes remain unfiltered. The raw APNG has full-strength hero surfaces and transparent empty space; one 65% multiplier belongs to the image view. Background context is softer. Walls, floor and ceiling are omitted from the ghost, and viewfinder/level are separate UI. The preview reference has a two-second delay; real camera capture is not delayed.',
        '',
        'The original facial expression remains: no lip sync, audio, mouth controls or blink animation was added. These demonstrate framing and body gestures. Physical iPhone capture remains untested. The PDF has not been rebuilt.',
        '',
        'Native files: ../glass-rollout/coffee/{creator-cafe,creator-bakery}/scene.blend. Rebuild with model_refferences/objects/tools/build_creator_guides.py; audit with check_creator_performances.py. The shared exporter/publisher packages the checked files.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    main=BASE/'catalog/animations.html';text=main.read_text()
    if 'id="canonical-creator-scenes"' not in text:
        text=text.replace('<p id="coffee-glass-rollout">','<p id="canonical-creator-scenes"><strong>Our creator:</strong> <a href="creator-scenes/index.html">Play the cafe and bakery performances in color and ghost form</a>.</p><p id="coffee-glass-rollout">',1)
    main.write_text(text)
    print(json.dumps(dict(status='published',scenes=2,frames=completion['source_frames'],seconds=completion['total_seconds'])))


if __name__=='__main__':run()
