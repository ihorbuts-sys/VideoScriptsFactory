"""Review the corrected resting hand and off-centre dining settings as exports become ready."""
from pathlib import Path
import html,json,os,sys
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'catalog/table-placement-review';sys.path.insert(0,str(BASE/'api'));import opacity_assets
ready=json.loads((OUT/'export-progress.json').read_text()) if (OUT/'export-progress.json').exists() else []
rows=['hands_during_top_hold']+ready;cards=[]
for gid in rows:
 folder=BASE/'catalog/blender-animations'/gid;spec=json.loads((folder/'scene-spec.json').read_text());checks=json.loads((folder/'export-checks.json').read_text());assert checks['build_fingerprint']==spec['build_fingerprint']
 asset=opacity_assets.assets(folder/'guide.png',video=True);relative=os.path.relpath(BASE/asset['folder'],OUT)
 caption=spec['intent'] if gid=='hands_during_top_hold' else 'The dish remains at a supported personal place setting, away from the dining-table centre.'
 cards.append(f'<article id="{gid}"><h2>{gid}</h2><p>{html.escape(caption)}</p><video controls playsinline loop preload="none" poster="{relative}/poster.png"><source src="{relative}/preview.mp4" type="video/mp4"></video><p><a href="{relative}/guide.png">Transparent animation</a> · {spec["frame_count"]/15:g} seconds · 65% opacity</p></article>')
verified=(OUT/'verification.json').exists();note='Published to the local API and verified.' if verified else f'{len(ready)} of 21 table corrections ready for review. The massage correction is already published; the table batch is being checked.'
page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Massage and table setting corrections</title><style>body{font:15px/1.5 system-ui;margin:25px;background:#f7f5ef;color:#29404c}main{max-width:1400px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:25px}article{padding:15px;border:1px solid #b9c5cb;border-radius:8px}h2{font-size:17px;overflow-wrap:anywhere}video{width:100%;max-height:600px;background:#f7f5ef}a{color:#326881}</style><main><a href="../animations.html">All guide animations</a><h1>Massage and table setting corrections</h1><p>'+note+'</p><div class="grid">'+''.join(cards)+'</div></main></html>'
(OUT/'index.html').write_text(page);print('Table correction review videos:',len(cards))
