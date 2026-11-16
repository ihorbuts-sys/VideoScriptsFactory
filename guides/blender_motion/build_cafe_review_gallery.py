"""Playable review of the owner-requested cafe step corrections."""
from pathlib import Path
import html
import json
import os
import sys

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'api'))
import opacity_assets
OUT=BASE/'catalog/cafe-review';OUT.mkdir(exist_ok=True)
manifest=json.loads((BASE/'catalog/context-animations/index.json').read_text())
rows=[
    ('cafe-first-visit.pour','First Visit: The Pour','A visible milk pitcher pours into the cup. A flat milk heart spreads on the coffee surface, followed by a brief entrance landing.'),
    ('cafe-first-visit.counter','First Visit: Order','The original schematic cup-and-machine hierarchy rebuilt in Blender. Hold the visitor-side phone steady as espresso enters the supported cup.'),
    ('cafe-morning-ritual.cup','Morning Ritual: The Cup','Start on the steaming cup and reveal the croissant beside it on the same table. The short handover previews only the beginning of the next detail move.'),
    ('cafe-morning-ritual.pastry','Morning Ritual: Something Sweet','Continue from the same table arrangement toward the supported pastry and its filling. No laptop shot is appended.'),
    ('cafe-before-opening.lights','Before Opening: Lights On','The schematic room layout, with four pendant lamps switching on once. The phone, furniture and light positions stay still; no people or chair-lowering animation.')]
cards=[]
for key,title,description in rows:
    row=manifest['steps'][key]
    asset=opacity_assets.assets(BASE/row['folder']/'guide.png',video=True)
    rel=os.path.relpath(BASE/asset['folder'],OUT)
    cards.append(f'''<article id="{key}"><h2>{html.escape(title)}</h2>
<p>{row['duration']:g} seconds · {opacity_assets.PERCENT}% whole-overlay opacity</p>
<video controls playsinline muted loop preload="metadata" poster="{rel}/poster.png"><source src="{rel}/preview.mp4" type="video/mp4"></video>
<p>{html.escape(description)}</p><p><a href="{rel}/guide.png">Transparent animation</a> · <a href="{rel}/strip.jpg">Frame samples</a></p></article>''')
content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cafe guide corrections</title>
<style>body{margin:0;background:#efede7;color:#293d49;font:16px/1.5 system-ui}main{max-width:1450px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:20px}article{padding:18px;background:#fbfaf5;border:1px solid #ccd4d7;border-radius:10px}h2{font-size:19px}video{display:block;width:100%;aspect-ratio:9/16;background:#f7f5ef}a{color:#326881}</style>
<main><a href="../animations.html">All guide animations</a><h1>Cafe guide corrections</h1>
<p>Each step teaches its own shot. Cuts end the step; explicit handovers show a brief landing or a connected in-scene move. Complete next shots are not appended automatically.</p>
<p><a href="report.md">What changed and verification</a></p><div class="grid">'''+''.join(cards)+'</div></main></html>'
(OUT/'index.html').write_text(content)
print('CAFE_REVIEW_READY',len(rows),opacity_assets.PERCENT)
