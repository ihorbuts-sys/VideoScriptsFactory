"""Keep a review page available while the interaction clips finish."""
import html,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
OUT=BASE/'catalog/interaction-scenes'
KEYS=['creator-pastry-select','creator-coffee-present','creator-pack-box','creator-box-total']

def run():
    OUT.mkdir(exist_ok=True);cards=[];records=[]
    for key in KEYS:
        p=ROOT/key;s=json.loads((p/'scene-spec.json').read_text());published=(p/'publication.json').exists()
        review=p/'review-status.json';rejected=review.exists() and json.loads(review.read_text()).get('status')=='rejected'
        ready=published and json.loads((p/'composite-browser-check.json').read_text())['status']=='passed'
        prefix='../glass-rollout/coffee/'+key+'/'
        n=s['probe_frames'][1];picture=('color/' if ready else 'probes-color/')+f'frame_{n:04d}.png'
        links=f'<a class="play" href="{prefix}index.html">Play color and ghost</a>' if ready else '<span>Rejected grip / removed from active API</span>' if rejected else '<span>Rendering and playback review</span>'
        bindings='; '.join(f"{b['template']} / {b['step']} ({b['capture']:g} s capture)" for b in s['guide_bindings'])
        cards.append(f'''<article><h2>{html.escape(s['title'])}</h2><p class="status">{'Rejected study' if rejected else 'Published' if ready else 'In progress'}</p>
<img class="poster" src="{prefix}{picture}" alt="{html.escape(s['title'])}"><p>{links}</p><p>{html.escape(s['direction'])}</p>
<p>{s['duration_s']:g} seconds at 15 fps. {html.escape(bindings)}</p>
<details><summary>Native scene and contact checks</summary><p><a href="{prefix}scene.blend">Blender scene</a> · <a href="{prefix}interaction-review.json">Contact review</a></p></details></article>''')
        records.append(dict(id=key,status='rejected' if rejected else 'published' if ready else 'rendering',frames=s['frame_count'],seconds=s['duration_s'],bindings=s['guide_bindings']))
    sequence=BASE/'catalog/glass-rollout/sequences/bakery-box/publication.json'
    sequence_link='<p class="sequence"><a href="../glass-rollout/sequences/bakery-box/index.html">Play the complete Build a box sequence / 35 seconds / all five steps</a></p>' if sequence.exists() else '<p>The complete five-step bakery sequence will appear here after its last shot passes review.</p>'
    if (sequence.parent/'review-status.json').exists():sequence_link='<p>The bakery sequence and cup/tong studies were withdrawn after owner review. The hand grips were unnatural. Object-only commercial shots take priority.</p>'
    (OUT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loca / creator interactions</title><style>body{font:16px/1.5 system-ui;background:#f2ede3;color:#293b32;max-width:1180px;margin:auto;padding:24px;box-sizing:border-box}h1{line-height:1.15}h2{font-size:21px}a{color:#326c52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:20px}article{min-width:0;border-radius:22px;background:#fffaf0;padding:22px}.poster{display:block;width:100%;height:420px;object-fit:contain;border-radius:14px}.play{display:inline-block;padding:10px 18px;border-radius:30px;background:#326c52;color:white}.status{font-weight:600}.sequence{background:#e2e9d7;border-radius:18px;padding:18px}p{overflow-wrap:anywhere}summary{cursor:pointer}</style>
<p><a href="../animations.html">All guides</a> · <a href="../creator-scenes/index.html">Creator portraits</a> · <a href="../food-scenes/index.html">Food scenes</a></p>
<h1>Creator / pastry and coffee interactions</h1><p>Existing models, real jointed hands and coupled object movement. Every player has a color reference and a transparent ghost at 65% image-view opacity. Viewfinder and level are separate; the demonstration background follows two seconds behind.</p>
'''+sequence_link+'<div class="grid">'+''.join(cards)+'</div></html>\n')
    if any(r['status']=='rendering' for r in records):
        p=OUT/'index.html';p.write_text(p.read_text().replace('<meta charset="utf-8">','<meta charset="utf-8"><meta http-equiv="refresh" content="20">',1))
    (OUT/'progress.json').write_text(json.dumps(dict(scenes=records,complete=all(r['status']=='published' for r in records),full_bakery_sequence=sequence.exists()),indent=2)+'\n')
    main=BASE/'catalog/animations.html';text=main.read_text()
    if 'id="creator-interactions"' not in text:
        text=text.replace('<p id="coffee-glass-rollout">','<p id="creator-interactions"><strong>Creator interactions:</strong> <a href="interaction-scenes/index.html">Pastry selection, coffee presentation and box packing</a>.</p><p id="coffee-glass-rollout">',1)
    main.write_text(text)
    print(json.dumps(dict(status='updated',published=sum(r['status']=='published' for r in records),scenes=4,full_bakery_sequence=sequence.exists())))

if __name__=='__main__':run()
