"""Build a local gallery with explicit rollout and handover status."""
from pathlib import Path
import html
import hashlib
import json
import time
import subprocess
import sys
import os

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'api'))
import opacity_assets
OUT=BASE/"catalog/blender-animations"
plan=json.loads((BASE/"guides/blender_motion/work-plan.json").read_text())
cards=[];index=[]
for row in plan["guides"]:
    gid=row["id"];folder=OUT/gid
    if row.get("status")=="deferred_people":continue
    if not (folder/"scene-spec.json").exists():continue
    spec=json.loads((folder/"scene-spec.json").read_text())
    checks=json.loads((folder/"export-checks.json").read_text()) if (folder/"export-checks.json").exists() else {}
    exported=(folder/"guide.png").exists() and spec.get("build_fingerprint") is not None and checks.get("build_fingerprint")==spec["build_fingerprint"]
    review=json.loads((folder/"review.json").read_text()) if (folder/"review.json").exists() else {}
    checked=exported and review.get("guide_sha256")==hashlib.sha256((folder/"guide.png").read_bytes()).hexdigest()
    base_only=spec.get("scope") not in ["shot_and_handover","complete_final_shot"]
    status=("Base shot reviewed" if base_only else "Shot and handover reviewed" if spec.get("scope")=="shot_and_handover" else "Final shot reviewed") if checked and exported else "Exported; visual review pending" if exported else "Framing review"
    source=gid+("/guide_with_guides.png" if exported else "/proof.jpg")
    opacity=opacity_assets.assets(folder/'guide.png',video=True) if exported and checked else None
    if opacity:source=os.path.relpath(BASE/opacity['overlay'],OUT)
    if not exported and not (folder/"proof.jpg").exists():continue
    duration=spec["frame_count"]/spec["fps"]
    controls=f'<a href="{gid}/guide.png">Transparent APNG</a> · <a href="{gid}/preview.mp4">Video preview</a> · ' if exported else ''
    if opacity:controls=f'<a href="{os.path.relpath(BASE/opacity["overlay"],OUT)}">Transparent APNG</a> · <a href="{os.path.relpath(BASE/opacity["video"],OUT)}">Video preview</a> · '
    note="One continuous camera move connects both resources." if spec.get("shared_scene_handover") else "Reusable base shot. Contextual handover is pending the next pass." if base_only else "Includes the actual next-shot handover as a separate take." if spec.get("scope")=="shot_and_handover" else "Complete final shot; holds for the script ending."
    body=f'''<article id="{gid}"><h2>{html.escape(gid)}</h2><p class="status">{status} · {duration:g} s</p><div class="stage"><img loading="lazy" src="{source}?v={time.time_ns()}" alt="{html.escape(spec['description'])}"></div><p>{html.escape(spec['intent'])}</p><p><strong>Lighting:</strong> {html.escape(spec.get('pre_render_review',{}).get('lighting','Under review'))}</p><p>{controls}<a href="{gid}/scene.blend">Blender scene</a> · <a href="{gid}/pre-render-review.json">Script/composition review</a></p><p class="note">{note}</p></article>'''
    cards.append(body)
    index.append(dict(id=gid,status=status,seconds=duration,exported=exported,reviewed=checked,base_shot_only=base_only,handovers="pending" if base_only else spec.get("handover_status"),source=source))
ready=sum(x["exported"] for x in index)
content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blender guide rollout</title><style>*{box-sizing:border-box}body{margin:0;background:#eeece6;color:#293d49;font:15px/1.6 system-ui,sans-serif}main{max-width:1400px;padding:24px;margin:auto}h1{font-size:30px}h2{font:600 16px/1.4 system-ui;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}article{background:#faf9f4;border:1px solid #cad3d5;border-radius:9px;padding:17px}.stage{aspect-ratio:9/16;background:#fdfcf8;overflow:hidden;display:flex;align-items:center;justify-content:center}.stage img{width:100%;height:100%;object-fit:contain}.dark .stage{background:#273a47}.status,.note{font-size:13px;color:#607783}a{color:#326881}button{font:inherit;padding:7px 12px;border:1px solid #a8b8c0;border-radius:6px;background:#fff;cursor:pointer}nav{display:flex;gap:15px;align-items:center;margin:20px 0}</style><main><a href="../blender-study/index.html">Approved bar/table study</a><h1>Blender guide rollout</h1>'''
content+=f'<p>{ready} new guides exported from the 178-guide rollout. These previews use real 3D cameras, 65% whole-overlay opacity and fainter context. Each card distinguishes base shots from completed shot-and-handover sequences.</p>'
content+='<p>Each scene has a pre-render script review covering angle, movement, focal point, spacing, lighting and the relevance of composition techniques.</p><nav><button onclick="document.body.classList.toggle(\'dark\')">Light / dark background</button><a href="../../guides/blender_motion/work-plan.json">Rollout status</a></nav><div class="grid">'+''.join(cards)+'</div></main></html>'
from gallery_ui import attach
content=attach(content,"../guide-ui.js")
(OUT/"index.html").write_text(content)
(OUT/"index.json").write_text(json.dumps(dict(base_shots_exported=sum(x["exported"] and x["base_shot_only"] for x in index),guides_exported=ready,library_guides=178,shots=index),indent=2)+"\n")
print("Gallery:",ready,"exported base shots")
subprocess.run([sys.executable,str(Path(__file__).with_name("sync_catalog_gallery.py"))],check=True)
