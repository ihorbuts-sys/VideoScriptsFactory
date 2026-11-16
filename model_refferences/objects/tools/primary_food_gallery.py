"""Publish the reviewed three-scene food batch as a small browsable collection."""
import html
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
OUT=BASE/'catalog/food-scenes'
KEYS=['burger-hero','brunch-spread','dessert-orbit']


def run():
    OUT.mkdir(exist_ok=True)
    catalog=json.loads(Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/catalog.json').read_text())
    cards=[];rows=[]
    for key in KEYS:
        folder=ROOT/key
        spec=json.loads((folder/'scene-spec.json').read_text())
        assert json.loads((folder/'composite-browser-check.json').read_text())['status']=='passed'
        assert json.loads((folder/'publication.json').read_text())['status']=='published'
        assert max(c['centre_contact_error_m'] for c in spec['contacts'])<.0006
        visibility=json.loads((folder/'camera-visibility-check.json').read_text())
        assert visibility['status']=='passed' and visibility['frames']==spec['frame_count']
        template=next(t for t in catalog['templates'] if t['id']==spec['template'])
        step=next(s for s in template['steps'] if s['id']==spec['step'])
        prefix='../glass-rollout/coffee/'+key+'/'
        cards.append(f'''<article><h2>{html.escape(spec['title'])}</h2>
<p>{html.escape(template['title'])} / {html.escape(step['title'])}</p>
<img src="{prefix}color-poster.png" alt="{html.escape(spec['title'])}">
<p><a class="play" href="{prefix}index.html">Play color and ghost</a></p>
<p>{html.escape(spec['direction'])}</p><p>{spec['duration_s']:g} seconds at 15 fps; 5-second capture.</p>
<details><summary>Frames and source</summary><img class="strip" src="{prefix}color-strip.jpg" alt="Camera motion samples">
<p><a href="{prefix}scene.blend">Blender scene</a> · <a href="{prefix}scene-spec.json">Camera, placement and API bindings</a></p></details></article>''')
        rows.append(dict(id=key,template=spec['template'],step=spec['step'],guide=spec['guide'],
            title=spec['title'],seconds=spec['duration_s'],frames=spec['frame_count'],
            collection_endpoint='/v1/guide-collections/coffee-guide-'+key,
            step_endpoint='/v1/steps/'+spec['template']+'.'+spec['step']+'/guides',
            reused_primary_objects=spec['reused_primary_objects'],new_generation_credits=0,
            contacts=spec['contacts'],final_framing=spec['final_framing'],
            camera_visibility=visibility,
            camera_max_speed_m_s=spec['camera']['max_speed_m_s'],
            camera_max_turn_deg_s=spec['camera']['max_turn_deg_s']))
    (OUT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / food scene guides</title>
<style>body{font:16px/1.5 system-ui;background:#f2ede3;color:#293b32;max-width:1180px;margin:auto;padding:24px;box-sizing:border-box}h1{line-height:1.15}h2{font-size:21px}a{color:#326c52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px}article{min-width:0;padding:20px;background:#fffaf0;border-radius:20px}img{display:block;width:100%;max-height:420px;object-fit:contain;border-radius:12px}.strip{max-height:180px}.play{display:inline-block;background:#326c52;color:white;border-radius:30px;padding:10px 18px}p{overflow-wrap:anywhere}summary{cursor:pointer}</style>
<p><a href="../animations.html">All guides</a> · <a href="../primary-targets/index.html">Reusable objects</a></p>
<h1>Three food scenes</h1><p>Native Blender animation with the reviewed clay models. Each player includes the full-color film, a transparent ghost, separate viewfinder and level, and a 65% image-view opacity control. Press Play in the player; the demonstration background follows two seconds behind the guide.</p>
<p>These are complete individual takes with deliberate cuts to the following steps. They do not claim to be complete script sequences. The burger replaces only the Ten dollar run table shot; its shared handheld version stays separate.</p><div class="grid">'''+''.join(cards)+'</div></html>\n')
    report=dict(status='published',date='2026-10-30',scenes=rows,scene_count=3,source_frames=sum(r['frames'] for r in rows),
        total_animation_seconds=sum(r['seconds'] for r in rows),fps=15,new_tripo_credits=0,
        image_view_opacity=.65,raw_global_opacity=1,viewfinder_embedded=False,
        architecture_embedded_in_ghost=False,full_script_sequence_complete=False,
        physical_phone_capture_verified=False)
    (OUT/'completion.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'README.md').write_text('''# Primary food scenes, 30 October 2026

[Play the three scenes](http://127.0.0.1:8766/food-scenes/index.html).

|Scene|App template and step|Guide|Animation|Capture|
|---|---|---|---|---|
|Low diagonal burger approach|Ten dollar run / Item two|`burger_low_in_mc`|6 s|5 s|
|One toast plate to two complete place settings|Weekend brunch / The spread|`plate_spread_top_out_cw`|7 s|5 s|
|Descending seated dessert arc|Date night / The plate|`plate_high_orbitl_cc`|7 s|5 s|

The batch reuses the new burger, brunch toast, cake slice and dinner plate models, plus the existing calibrated café furniture and hollow cups. Coffee is placed at each cup's calibrated fill height. Every plate is off the table centre, in one of two reachable opposing settings. Actual-mesh raycasts validate eight contacts per scene to within 0.6 mm; independent settings have disjoint footprints. The whole brunch table fits the final phone frame. Its rising camera remains below 1.8 m. The dessert camera traces a 54-degree arc while descending 9 cm. All camera lenses remain fixed.

Each color and ghost pair shares its native camera and timing. Glass surfaces retain full hero strength in the raw transparent APNG; one 65% multiplier belongs to the image view. Ghosts exclude walls, floor and ceiling. Viewfinder and level remain separate. The two-second background delay applies to this demonstration player, not to live camera capture.

These are three individual shots, with an explicit cut to the next script step. The burger updates only `quick-budget-run.second`: the shared handheld guide is preserved. No human performance, fake fork action, yolk break or cross-section is implied. They are rendered at 15 fps with 32 color samples. Identical static holds reuse exact rendered frames; moving frames are rendered independently from the same native geometry. This avoids generative drift and unnecessary render work. No new paid model jobs were submitted.

Each scene is checked with the embedded-browser playback test, including Play, Stop, replay, APNG motion, independent viewfinder, opacity and mobile layout. See `completion.json`, each scene's checks, and `../glass-rollout/live-api-check.json` for final evidence. Physical iPhone capture and device LiDAR alignment remain unverified. No new full-script sequences or PDF were generated.

Native scenes and frame sources are in `../glass-rollout/coffee/{burger-hero,brunch-spread,dessert-orbit}/`. Rebuild with `model_refferences/objects/tools/build_primary_food_scenes.py` in headless Blender. The existing exporter and publisher package the reviewed shots; `primary_food_gallery.py` rebuilds this index.
''')
    gallery=BASE/'catalog/animations.html'
    text=gallery.read_text()
    if 'id="primary-food-scenes"' not in text:
        marker='<p id="coffee-glass-rollout">'
        text=text.replace(marker,'<p id="primary-food-scenes"><strong>New food scenes:</strong> <a href="food-scenes/index.html">Burger, brunch spread and dessert / color and ghost players</a>.</p>'+marker,1)
    gallery.write_text(text)
    print(json.dumps(dict(status='published',scenes=3,frames=report['source_frames'],seconds=report['total_animation_seconds'])))


if __name__=='__main__':run()
