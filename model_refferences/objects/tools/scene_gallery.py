"""Paired full-color and transparent-ghost scene review pages."""
import html,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[3]
STYLE='''body{font:16px system-ui;color:#293e32;background:#eee9dd;margin:24px auto;padding:0 20px;max-width:1250px}article{background:#fffaf0;border-radius:20px;padding:24px;margin:24px 0}.players{display:grid;grid-template-columns:1fr 1fr;gap:24px}img{width:100%;height:auto;object-fit:contain}a{color:#34654d}p{line-height:1.5}video,.ghost{width:100%;max-height:75vh;aspect-ratio:9/16;object-fit:contain;border-radius:18px}.ghost{background:repeating-conic-gradient(#303b42 0 25%,#36434b 0 50%) 0/32px 32px}.ghost img{height:100%;object-fit:contain}button{border:1px solid #66816c;border-radius:20px;background:#f8f4e9;padding:9px 16px;cursor:pointer}@media(max-width:700px){.players{grid-template-columns:1fr}}'''

def page(title,body,script=''):
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title><style>{STYLE}</style><main>{body}</main>{script}</html>'

def build():
    root=BASE/'catalog/clay-scenes';cards=[];records=[]
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or not (folder/'export-checks.json').exists():continue
        spec=json.loads((folder/'scene-spec.json').read_text());checks=json.loads((folder/'export-checks.json').read_text())
        gid=spec['id'];title='Bar counter to the best table' if gid=='bar_low_truckr_mm' else 'Coffee cup orbit'
        v=checks['files']['ghost.png'][:12];duration=spec['duration_s'];published=spec.get('published',False)
        status='Published replacement guide' if published else 'Local proof; not published'
        scope='Continuous shot and handover in one physical scene' if spec['scope']=='shot_and_handover' else 'Base shot only; creator-sip handover pending character rigging and contact review'
        details=''.join(f'<p>{html.escape(p)}</p>' for p in spec.get('composition',[]))
        phases=''.join(f'<p>{p["start_s"]:g}–{p["end_s"]:g} s: {html.escape(p["action"])}</p>' for p in spec.get('phases',[]))
        body=f'''<p><a href="../index.html">All new scenes</a> · <a href="../../../model_refferences/objects/reconstructed.html">Model library</a></p><h1>{title}</h1><p>{duration:g} seconds · {spec['frame_count']} source frames · {spec['fps']} fps · {status}</p><p>{scope}.</p><p><button onclick="replayBoth()">Replay both versions</button> · <a href="color.mp4">Color video</a> · <a href="ghost.png">Transparent ghost APNG</a></p><div class="players"><article><h2>Full color</h2><video src="color.mp4?v={v}" autoplay loop muted playsinline controls poster="color-poster.png?v={v}"></video></article><article><h2>Ghost overlay</h2><div class="ghost"><img src="ghost.png?v={v}" alt="Animated transparent ghost guide"></div><p>65% overall opacity. Subject contours remain stronger than context; walls are absent. The app draws its viewfinder and level separately.</p><button onclick="document.querySelector('.ghost').style.background='#f7f2e7'">Light background</button> <button onclick="document.querySelector('.ghost').style.background='#23313b'">Dark background</button></article></div><article><h2>Filming instructions</h2>{phases}{details}<p>{html.escape(spec['mobile'])}</p><p>{html.escape(spec['lighting'])}</p><p><a href="scene.blend">Animated Blender scene</a> · <a href="scene-spec.json">Camera path and contact checks</a> · <a href="export-checks.json">Export verification</a></p></article><article><h2>Color frames</h2><img src="color-strip.jpg?v={v}" alt="Color frames"><h2>Ghost frames</h2><img src="ghost-strip.jpg?v={v}" alt="Ghost frames"></article>'''
        script='''<script>
const video=document.querySelector('video');
const source=document.querySelector('.ghost img').getAttribute('src');
function replayBoth(){video.pause();video.currentTime=0;const old=document.querySelector('.ghost img'),fresh=old.cloneNode(false);fresh.onload=()=>{video.currentTime=0;video.play().catch(()=>{});};fresh.src=source+'&replay='+Date.now();old.replaceWith(fresh);}
video.pause();if(video.readyState>=2)replayBoth();else video.addEventListener('loadeddata',replayBoth,{once:true});
</script>'''
        (folder/'index.html').write_text(page(title,body,script))
        cards.append(f'<article><h2><a href="{gid}/index.html">{title}</a></h2><p>{duration:g} seconds · {status}. {scope}.</p><a href="{gid}/index.html"><img src="{gid}/color-strip.jpg?v={v}" alt="{title} frames"></a><p><a href="{gid}/index.html">Play color and ghost together</a> · <a href="{gid}/scene.blend">Blender scene</a></p></article>')
        records.append(dict(id=gid,duration_s=duration,scope=spec['scope'],published=published,files=checks['files']))
    manifest=root/'active-revisions.json'
    for tid,row in json.loads(manifest.read_text()).get('sequences',{}).items() if manifest.exists() else []:
        folder=BASE/row['folder'];title=row['title']+' / full script'
        sequence_body=f'''<p><a href="../../index.html">All new scenes</a></p><h1>{html.escape(title)}</h1><p>{row['seconds']:g} seconds. The Bar and Best Table section uses the new continuous twelve-second clay scene. Other steps retain their existing artwork, including the human sections.</p><article><video src="preview.mp4" controls playsinline loop muted preload="metadata" poster="poster.png"></video><p><a href="ghost.png">Transparent full-script APNG</a> · <a href="preview.mp4">MP4 preview</a> · <a href="assembly-checks.json">Assembly checks</a></p></article><article><img src="strip.jpg" alt="Updated full-script frames"></article>'''
        (folder/'index.html').write_text(page(title,sequence_body))
        cards.append(f'<article><h2><a href="sequences/{tid}/index.html">{html.escape(title)}</a></h2><p>The connected bar-to-table section is refreshed. Other steps retain their existing artwork.</p><a href="sequences/{tid}/index.html"><img src="sequences/{tid}/strip.jpg" alt="Full-script sequence frames"></a></article>')
    body='<h1>Image-driven clay guide scenes</h1><p>Color and ghost exports share the same reconstructed models, physical supports and camera movement. Each page explains its scope and publication status.</p><p><a href="../animations.html">All existing guide animations</a> · <a href="../../model_refferences/objects/reconstructed.html">Reconstructed model library</a></p>'+''.join(cards)
    (root/'index.html').write_text(page('Loca clay scene reviews',body))
    (root/'index.json').write_text(json.dumps(dict(scenes=records),indent=2)+'\n')

if __name__=='__main__':build()
