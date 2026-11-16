"""A small filming-lesson gallery: purpose, setup and move for each shot."""
import html,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
OUT=BASE/'catalog/commercial-core'
KEYS=['commercial-texture','commercial-display','commercial-room']

def run():
    OUT.mkdir(exist_ok=True);cards=[];rows=[]
    for key in KEYS:
        folder=ROOT/key
        if not (folder/'scene-spec.json').exists():continue
        s=json.loads((folder/'scene-spec.json').read_text());published=(folder/'publication.json').exists()
        target='../glass-rollout/coffee/'+key+'/'
        image='color-poster.png' if published else 'probes-color/frame_0001.png'
        link=f'<a class="play" href="{target}index.html">Play the filming guide</a>' if published else '<span>Native rendering and playback checks in progress</span>'
        setup=''.join('<li>'+html.escape(r)+'</li>' for r in s['staging'])
        cards.append(f'<article><h2>{html.escape(s["title"])}</h2><p><strong>{html.escape(s["commercial_purpose"])}</strong></p><img src="{target}{image}" alt="{html.escape(s["title"])}"><p>{link}</p><ul>{setup}</ul><p>{html.escape(s["direction"])}</p><p>{s["duration_s"]:g} seconds. <a href="{target}commercial-review.json">Staging and camera checks</a></p></article>')
        rows.append(dict(scene=key,status='published' if published else 'rendering',purpose=s['commercial_purpose'],bindings=s['guide_bindings']))
    refresh='<meta http-equiv="refresh" content="20">' if any(r['status']!='published' for r in rows) else ''
    existing='''<h2>Reuse these existing lessons</h2><ul>
<li>Product hero: <a href="../glass-rollout/coffee/cup-orbit/index.html">cup orbit</a>, <a href="../glass-rollout/coffee/burger-hero/index.html">low burger approach</a> and <a href="../glass-rollout/coffee/dessert-orbit/index.html">dessert arc</a>.</li>
<li>Related products: <a href="../glass-rollout/coffee/morning-pair/index.html">cup and opened pastry in one connected take</a>.</li>
<li>Arrival: <a href="../glass-rollout/coffee/entrance/index.html">public entrance approach</a>.</li>
<li>Choice: <a href="../glass-rollout/coffee/menu-to-cup/index.html">menu board to the same counter drink</a>.</li>
</ul>'''
    (OUT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'''+refresh+'''<title>Loca / practical commercial shots</title><style>body{font:16px/1.5 system-ui;color:#293b32;background:#f2ede3;max-width:1160px;margin:auto;padding:24px}h1{line-height:1.15}h2{font-size:22px}a{color:#326c52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:22px}article{min-width:0;background:#fffaf0;border-radius:20px;padding:22px}img{display:block;width:100%;height:390px;object-fit:contain;border-radius:12px}.play{display:inline-block;background:#326c52;color:white;padding:10px 18px;border-radius:24px}p,li{overflow-wrap:anywhere}</style><p><a href="../animations.html">All guides</a> · <a href="priorities.md">Shot priorities</a></p><h1>Practical commercial shots</h1><p>Show what is worth ordering, what is available and what visiting feels like. Each of the three new lessons demonstrates the subject setup and a short phone move, without characters or hand manipulation. Color and 65% transparent ghost variants share the same native scene; viewfinder and level stay separate.</p><div class="grid">'''+''.join(cards)+'</div>'+existing+'</html>\n')
    (OUT/'progress.json').write_text(json.dumps(dict(scenes=rows,complete=len(rows)==3 and all(r['status']=='published' for r in rows)),indent=2)+'\n')
    main=BASE/'catalog/animations.html';text=main.read_text()
    if 'id="commercial-core"' not in text:text=text.replace('<p id="coffee-glass-rollout">','<p id="commercial-core"><strong>Practical commercial shots:</strong> <a href="commercial-core/index.html">Product detail, pastry range and a room reveal, without animated hands</a>.</p><p id="coffee-glass-rollout">',1)
    text=text.replace('Pastry selection, coffee presentation and box packing','Display selection and withdrawn hand-interaction studies')
    main.write_text(text)
    print(json.dumps(dict(status='updated',published=sum(r['status']=='published' for r in rows),scenes=len(rows))))

if __name__=='__main__':run()
