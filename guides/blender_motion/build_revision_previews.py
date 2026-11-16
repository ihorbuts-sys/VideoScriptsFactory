"""Expose current revision renders immediately while final API checks are pending."""
from pathlib import Path
import html,json,re,sys,os
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'api'))
import opacity_assets
out=BASE/'catalog/cinematic-revision';out.mkdir(exist_ok=True)
ready=out/'ready-previews.json';selected=json.loads(ready.read_text()) if ready.exists() else []
if isinstance(selected,dict):selected=selected.get('guides',[])
selected=list(dict.fromkeys(selected+sys.argv[1:]));cards=[];published=[]
page=BASE/'catalog/animations.html';main=page.read_text()
for gid in selected:
 folder=BASE/'catalog/blender-animations'/gid;spec=json.loads((folder/'scene-spec.json').read_text());checks=json.loads((folder/'export-checks.json').read_text())
 if checks.get('build_fingerprint')!=spec['build_fingerprint']:continue
 artifact=opacity_assets.assets(folder/'guide.png',video=True);relative=os.path.relpath(BASE/artifact['folder'],out)
 description=html.escape(spec['intent']);seconds=spec['frame_count']/15
 cards.append(f'<article id="{gid}"><h2>{gid}</h2><p>{description}</p><video controls playsinline loop preload="none" poster="{relative}/poster.png"><source src="{relative}/preview.mp4" type="video/mp4"></video><p><a href="{relative}/guide.png">Transparent APNG</a> · {seconds:g} seconds · 65% overlay opacity</p></article>');published.append(gid)
 pattern=r'<article class="guide" id="'+re.escape(gid)+r'".*?</article>';match=re.search(pattern,main,re.S)
 if not match:continue
 card=match.group();relative=os.path.relpath(BASE/artifact['folder'],page.parent)
 card=re.sub(r'<img class="motion-image"[^>]*>',f'<img class="motion-image" loading="lazy" src="{relative}/poster.png" data-poster="{relative}/poster.png" data-animation="{relative}/guide.png" alt="Updated {gid}">',card,count=1)
 card=re.sub(r'<img class="fixed-sights"[^>]*>','',card)
 card=re.sub(r'<p class="description">.*?</p>',f'<p class="description">{description}</p>',card,count=1,flags=re.S)
 card=re.sub(r'<img class="strip"[^>]*>',f'<img class="strip" loading="lazy" src="{relative}/strip.jpg" alt="Updated motion samples">',card,count=1)
 card=re.sub(r'<footer>.*?</footer>',f'<footer><a href="{relative}/guide.png">Transparent APNG</a><a href="cinematic-revision/index.html#{gid}">Play updated video</a></footer>',card,count=1,flags=re.S)
 main=main.replace(match.group(),card,1)
body='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Updated cinematic guide previews</title><style>body{font:15px/1.5 system-ui;margin:25px;background:#f7f5ef;color:#29404c}main{max-width:1400px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:25px}article{padding:15px;border:1px solid #b9c5cb;border-radius:8px}h2{font-size:17px;overflow-wrap:anywhere}video{width:100%;max-height:600px;background:#f7f5ef}a{color:#326881}</style><main><a href="../animations.html">All guide animations</a><h1>Updated cinematic previews</h1><p>New renders at 65% whole-overlay opacity, with no viewfinder baked into the video. API publication follows the final checks.</p><div class="grid">'+''.join(cards)+'</div></main></html>'
(out/'index.html').write_text(body);ready.write_text(json.dumps(published,indent=2)+'\n')
main=re.sub(r'<[^>]+ id="cinematic-progress".*?</(?:p|section|div)>',f'<p id="cinematic-progress">{len(published)} updated previews ready. <a href="cinematic-revision/index.html">Play the new videos</a>. API publication is pending final checks.</p>',main,count=1,flags=re.S)
page.write_text(main);print('Updated revision previews:',len(published))
