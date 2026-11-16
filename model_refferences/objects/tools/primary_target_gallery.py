"""Offline review gallery for independently placeable filming targets."""
import html
import json
import os
from pathlib import Path

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'model_refferences/tripo-cli/primary-targets-2026-10-29'
OUT=BASE/'catalog/primary-targets'


def link(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_name(target.name+'.tmp');temporary.unlink(missing_ok=True)
    os.link(source,temporary);os.replace(temporary,target)


STYLE='''*{box-sizing:border-box}body{margin:0;background:#f1ede3;color:#2c4438;font:16px/1.5 system-ui}main{max-width:1320px;margin:auto;padding:24px}a{color:#376e52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}article{background:#fffaf0;padding:20px;border-radius:18px}h1{line-height:1.2}h2{font-size:21px}img{width:100%;height:auto;display:block;border-radius:12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}.ghost{background:#283f36}.ghost img{opacity:.65}.tag{font-size:13px}.downloads{display:flex;gap:14px;flex-wrap:wrap;margin:16px 0}select{font:inherit;padding:8px;border-radius:10px;border:1px solid #9baa98}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.views figure{margin:0}small{color:#5c7164}@media(max-width:650px){main{padding:16px}.views{grid-template-columns:repeat(2,1fr)}}'''


def page(title,body):return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{STYLE}</style><main>{body}</main></html>'


def run():
    plan=json.loads((ROOT/'plan.json').read_text());cards=[];records=[];ready=0;actual_credits=0
    OUT.mkdir(parents=True,exist_ok=True)
    for row in plan['objects']:
        aid=row['id'];review=BASE/'model_refferences/objects'/aid/'tripo-generated/review'
        source=BASE/row['reference_folder'];title=aid.replace('_',' ').title()
        downloaded=list((review.parent/'tripo-out').glob('*/task.json'))
        if downloaded:
            task=json.loads(downloaded[0].read_text())
            if task.get('status')=='success':actual_credits+=task.get('credits_consumed',0)
        if not (review/'ghost-preview.png').exists() or not (review/'native-ready.json').exists():
            cards.append(f'<article><h2>{title}</h2><p>Reference or native model preparation in progress.</p><p>{html.escape(row["reason"])}</p></article>')
            continue
        ready+=1;dest=OUT/aid;dest.mkdir(exist_ok=True)
        data=json.loads((review/'component.json').read_text())
        for name in ['model.glb','geometry-proxy.glb','model.usdz','geometry-proxy.usdz','model.blend','asset.blend','component.json']:
            if (review/name).exists():link(review/name,dest/name)
        for name in ['preview','front','back','left','right','top','bottom']:link(review/'rendered'/(name+'.png'),dest/(name+'.png'))
        link(review/'ghost-preview.png',dest/'ghost.png');link(source/'sheet.png',dest/'design-sheet.png')
        version=str((dest/'preview.png').stat().st_mtime_ns)
        views=''.join(f'<figure><img src="{v}.png?v={version}" alt="{v} view"><figcaption>{v.title()}</figcaption></figure>' for v in ['front','back','left','right','top','bottom'])
        usdz='<a href="model.usdz">iOS USDZ</a> · <a href="geometry-proxy.usdz">Proxy USDZ</a> · ' if (dest/'model.usdz').exists() else ''
        body=f'''<p><a href="../index.html">All primary targets</a></p><h1>{title}</h1><p>{html.escape(row['reason'])}</p><p>Independent component with measured model bounds, support origin and named alignment anchors. Reference art uses the built-in imagegen tool; reconstruction uses Tripo. LiDAR device registration has not been validated.</p>
<div class="downloads">{usdz}<a href="model.glb">Normalized GLB</a><a href="geometry-proxy.glb">Geometry proxy</a><a href="model.blend">Blender project</a><a href="asset.blend">Appendable Blender asset</a><a href="component.json">Measurements and anchors</a></div>
<div class="pair"><article><h2>Full color</h2><img src="preview.png?v={version}" alt="Native {title}"></article><article class="ghost"><h2 style="color:#eee9de">Static ghost / 65% view opacity</h2><img src="ghost.png?v={version}" alt="Static transparent {title}"></article></div>
<p>Blender units: metres, Z up. GLB/USDZ use metres and Y up. Model shape follows the clay reference; actual real-world pose and size must be aligned separately. Proxy: {data['geometry_proxy']['triangles']:,} triangles.</p><h2>Six rendered projections</h2><div class="views">{views}</div><h2>Reconstruction reference</h2><img src="design-sheet.png" alt="Eight-view design reference"><p><small>No animation, floor or scene is embedded in the component exports. The ghost is full strength in the file; this page applies 65% opacity once.</small></p>'''
        (dest/'index.html').write_text(page(title,body))
        cards.append(f'<article><h2><a href="{aid}/index.html">{title}</a></h2><div class="pair"><img src="{aid}/preview.png?v={version}" alt="{title}"><div class="ghost"><img src="{aid}/ghost.png?v={version}" alt="Static ghost"></div></div><p>{html.escape(row["reason"])}</p><p class="tag">{data["geometry_proxy"]["triangles"]:,} proxy triangles · {data["credits_consumed"]:g} credits</p><p><a href="{aid}/index.html">Inspect six projections, models and anchors</a></p></article>')
        records.append(dict(id=aid,status=row['status'],primary_target=True,category=row['category'],proxy_triangles=data['geometry_proxy']['triangles'],model='primary-targets/'+aid+'/model.glb'))
    body=f'''<p><a href="../animations.html">Guide animations</a></p><h1>Primary filming targets</h1><p>{ready}/16 components prepared. New targets are kept separate from food supports, rooms and decoration, for reuse in both guide animations and static overlays on real objects. No new live-guide animations are claimed by this model batch.</p><p>Budget: 640 of 645 authorized credits. Downloaded successful generations: {actual_credits:g} credits. <a href="plan.md">Priority plan</a> · <a href="index.json">Component index</a></p><div class="grid">'''+''.join(cards)+'</div>'
    (OUT/'index.html').write_text(page('Loca / primary filming targets',body))
    link(ROOT/'plan.md',OUT/'plan.md')
    (OUT/'index.json').write_text(json.dumps(dict(prepared=ready,planned=16,downloaded_generation_credits=actual_credits,objects=records),indent=2)+'\n')
    print('PRIMARY_TARGET_GALLERY',ready,16,flush=True)


if __name__=='__main__':run()
