#!/usr/bin/env python3
"""Builds catalog/catalog.html (and catalog/strips/) from scripts/, research/, previews/ and guides/.
Render with Chrome headless afterwards (see README in this folder).

    <venv python with Pillow> build_catalog.py
"""
import datetime, html, json, os, re, shutil
from zoneinfo import ZoneInfo
from PIL import Image, ImageSequence
import build_playback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
GUIDES = os.path.join(ROOT, "guides")
RESEARCH = os.path.join(ROOT, "research")

templates = json.load(open(os.path.join(GUIDES, "script_templates.json"), encoding="utf-8"))
shot_plan = json.load(open(os.path.join(ROOT, "scripts", "shot_plan.json"), encoding="utf-8"))
kinds = templates["venueKinds"]
kind_title = {k["id"]: k["title"] for k in kinds}
playback = {entry['id']:entry for entry in build_playback.entries()}
new_preview_count = sum(entry['watercolor'] for entry in playback.values())
catalog_date = os.environ.get('CATALOG_DATE', datetime.datetime.now(ZoneInfo('Europe/Kyiv')).date().isoformat())


# ---------------------------------------------------------------- strips from the APNG guides
def strip(gid):
    out = os.path.join(HERE, "strips", gid + ".png")
    if os.path.exists(out):
        return
    existing = os.path.join(GUIDES, "overlays", "schematic", gid + "_strip.png")
    if os.path.isfile(existing):
        shutil.copy2(existing, out)
        return
    im = Image.open(os.path.join(GUIDES, "overlays", "schematic", gid + ".png"))
    frames, times, clock = [], [], 0.0
    for fr in ImageSequence.Iterator(im):
        frames.append(fr.convert("RGBA"))
        times.append(clock)
        clock += fr.info.get("duration", 67) / 1000
    picks = [max(i for i, t in enumerate(times) if t <= clock * k / 6 + 0.3) for k in range(6)]
    w = 180
    h = round(frames[0].height * w / frames[0].width)
    sheet = Image.new("RGB", (w * 6 + 10, h + 4), (28, 28, 32))
    for k, i in enumerate(picks):
        bg = Image.new("RGBA", frames[i].size, (44, 44, 50, 255))
        bg.alpha_composite(frames[i])
        sheet.paste(bg.convert("RGB").resize((w, h), Image.LANCZOS), (2 + k * (w + 1), 2))
    sheet.save(out)


os.makedirs(os.path.join(HERE, "strips"), exist_ok=True)
guide_ids = sorted({o for t in templates["templates"] for s in t["steps"] for o in s["overlays"]})
for gid in guide_ids:
    strip(gid)


# ---------------------------------------------------------------- research extracts
def md_table(path, heading):
    """Rows of the first markdown table under `heading` (cells as text)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith(heading))
    rows = []
    for l in lines[start + 1:]:
        if rows and not l.startswith("|"):
            break
        if l.startswith("|") and not re.match(r"^\|\s*-", l):
            rows.append([c.strip() for c in l.strip("|").split("|")])
    return rows


def best_practice_lines(kind):
    """One line per section a reviewer needs: the first bullet of hooks, shot orders, pacing, name and price, avoid."""
    text = open(os.path.join(RESEARCH, "best_practices", kind + ".md"), encoding="utf-8").read()
    wanted = ("Hooks", "Shot orders", "Length", "Lengths", "Name, location", "Where name", "What to avoid")
    out = []
    for section in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = section.partition("\n")
        if not title.startswith(wanted):
            continue
        first = next((l.strip()[2:] for l in body.split("\n") if l.strip().startswith(("- ", "1. ")) or re.match(r"^\s*1\. ", l)), None)
        if first:
            first = re.sub(r"\s*\[[A-Z]\d+\]", "", first)
            out.append((title.split(" that ")[0].split(" and ")[0] if title.startswith("Hooks") else title, first))
    return out[:5]


venue_kind_rows = md_table(os.path.join(RESEARCH, "venue_kinds.md"), "| Kind id")
slugs_by_kind = {re.sub(r"`", "", r[0]): r[3] for r in venue_kind_rows if len(r) > 3}
menu_rows = md_table(os.path.join(RESEARCH, "menu_item_kinds.md"), "| Review kind")
coverage_rows = md_table(os.path.join(GUIDES, "coverage.md"), "| script | step")


# ---------------------------------------------------------------- html
def e(s):
    return html.escape(str(s))


def step_line(step):
    if step["captions"]:
        c = step["captions"][0]
        return f'<span class="text">{e(c["text"])}</span> {e(c["script"])}'
    return e(step["prompter"]) if step["prompter"] else "<span class=\"muted\">nothing said</span>"


parts = []
parts.append(f"""<!doctype html><html><head><meta charset="utf-8"><title>Scripts and guides</title>
<style>
@page {{ size: A4 landscape; margin: 12mm; }}
body {{ font: 9.5pt/1.3 -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; color: #111; margin: 0; }}
h1 {{ font-size: 26pt; margin: 0 0 6pt; }} h2 {{ font-size: 18pt; margin: 0 0 4pt; }} h3 {{ font-size: 13pt; margin: 0 0 2pt; }}
.cover {{ page-break-after: always; padding-top: 60mm; }}
.kind {{ page-break-before: always; page-break-after: always; }}
.kind ul {{ margin: 6pt 0 0 14pt; }} .kind li {{ margin-bottom: 3pt; }}
.script {{ page-break-before: always; page-break-inside: avoid; }}
.muted {{ color: #777; }} .small {{ font-size: 8pt; color: #555; }}
.steprow {{ display: flex; gap: 5pt; align-items: flex-start; page-break-inside: avoid; margin: 0 0 5pt; padding-top: 4pt; border-top: 1px solid #ddd; }}
.steprow .preview {{ width: 23mm; height: 41mm; object-fit: cover; border-radius: 3pt; display: block; flex: none; }}
.steprow .info {{ width: 50mm; flex: none; font-size: 8pt; }} .steprow .info .t {{ font-size: 10pt; font-weight: 600; }}
.steprow .info .s {{ color: #555; }} .steprow .info .line {{ margin-top: 2pt; }} .text {{ font-weight: 600; }}
.steprow .info code {{ font-size: 7pt; word-break: break-all; }}
.steprow .schematic {{ height: 30mm; display: block; flex: none; }} .steprow .model {{ height: 41mm; display: block; flex: none; }}
.gcap {{ font-size: 7pt; color: #555; margin-top: 1pt; }}
table {{ border-collapse: collapse; font-size: 7.5pt; width: 100%; }} th, td {{ border: 1px solid #ccc; padding: 2pt 4pt; text-align: left; vertical-align: top; }}
th {{ background: #eee; }} .appendix {{ page-break-before: always; }}
body {{ width: 273mm; }}
.script {{ height: 185mm; box-sizing: border-box; break-inside: avoid; }}
.script>p {{ font-size: 8pt; margin: 3pt 0 7pt; }}
.steps {{ display: grid; gap: 3mm; align-items: start; }}
.steprow {{ display: flex; flex-direction: column; min-width: 0; gap: 3pt; margin: 0; padding-top: 5pt; }}
.steprow .preview {{ width: auto; max-width: 100%; height: 44mm; margin: 0 auto; }}
.steprow .info {{ width: 100%; min-height: 35mm; font-size: 6.6pt; line-height: 1.24; }}
.steprow .info .t {{ font-size: 8pt; min-height: 8mm; }}
.steprow .info .s {{ font-size: 6pt; }}
.steprow>div {{ width: 100%; min-width: 0; }}
.steprow .schematic {{ width: 100%; height: auto; max-height: 18mm; object-fit: contain; }}
.steprow .model {{ width: 100%; height: auto; max-height: 29mm; object-fit: contain; }}
.gcap {{ font-size: 5.5pt; line-height: 1.2; overflow-wrap: anywhere; }}
.motion-card {{ display: none; }}
.gcap a {{ color: #326079; }}
@media screen {{
body {{ width: auto; max-width: 1400px; padding: 24px; margin: auto; background: #f2f0ea; }}
.cover {{ padding-top: 0; }}
.kind {{ margin-top: 36px; }}
.script {{ height: auto; padding: 16px; margin: 24px 0; background: white; border: 1px solid #c9d0d0; border-radius: 8px; }}
.motion-card {{ display: block; }}
.motion-stage {{ height: 220px; position: relative; overflow: hidden; background: #23343e; }}
.motion-image,.fixed-sights {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }}
.fixed-sights {{ pointer-events: none; }}
.motion-controls {{ display: flex; gap: 4px; margin: 5px 0; }}
.motion-controls button {{ font: inherit; font-size: 10px; padding: 5px; border: 1px solid #a5b5ba; border-radius: 4px; background: white; cursor: pointer; }}
}}
@media screen and (max-width: 700px) {{ .steps {{ grid-template-columns: repeat(2,minmax(0,1fr)) !important; }} body {{ padding: 10px; }} }}
</style></head><body>""")

n_steps = sum(len(t["steps"]) for t in templates["templates"])
parts.append(f"""<div class="cover"><h1>Loca venue scripts and live guides</h1>
<p>{catalog_date}. {len(kinds)} venue kinds, {len(templates["templates"])} scripts, {n_steps} steps, {len(guide_ids)} guides with 3D camera references.</p>
<p><a href="animations.html">Play guide animations in the browser</a></p>
<p class="small">{new_preview_count} watercolor animation previews at 50% alpha; {len(guide_ids)-new_preview_count} original schematic animations. Open animations.html or catalog.html in a browser for playback; this PDF contains printable six-frame strips and links. The full watercolor replacement remains incomplete. The brunch-pour schematic still uses the legacy cup subject; its corrected 3D reference specifies plated food.</p>
<p class="small">Sources: ScriptsAndGuides/scripts (catalog and shot plan), research (best practices, category mapping, menu audit), previews (step pictures), guides (scenes, schematic and 3D guides, coverage).</p></div>""")

for kind in kinds:
    kid = kind["id"]
    parts.append(f'<div class="kind"><h2>{e(kind["title"])} <span class="muted">({e(kid)})</span></h2>')
    parts.append(f'<p>Production categories: {e(slugs_by_kind.get(kid, kid))}.</p><ul>')
    for title, line in best_practice_lines(kid):
        parts.append(f"<li><b>{e(title)}.</b> {e(line)}</li>")
    scripts = [t for t in templates["templates"] if t["venueKinds"][0] == kid]
    shared = [t for t in templates["templates"] if kid in t["venueKinds"][1:]]
    parts.append("</ul><p class=\"small\">Scripts: " + ", ".join(e(t["title"]) for t in scripts)
                 + (" (also shown here: " + ", ".join(e(t["title"]) for t in shared) + ")" if shared else "")
                 + f". Reasoning: scripts/{e(kid)}/ and research/best_practices/{e(kid)}.md.</p></div>")
    for t in scripts:
        parts.append(f'<div class="script"><h3>{e(t["title"])} <span class="muted">{e(t["id"])}, {int(sum(s["seconds"] for s in t["steps"]))} s'
                     + (", reviews a menu item" if t.get("featuresMenuItem") else "") + "</span></h3>")
        parts.append(f'<p>{e(t["summary"])}</p>')
        parts.append(f'<div class="steps" style="grid-template-columns: repeat({len(t["steps"])}, minmax(0, 1fr))">')
        for i, s in enumerate(t["steps"], 1):
            plan = shot_plan[t["id"]][s["id"]]
            gid = s["overlays"][0] if s["overlays"] else None
            motion = playback.get(gid)
            guide_strip = motion['strip'] if motion else f'strips/{gid}.png'
            guide_label = motion['label'] if motion else 'Schematic guide'
            guide_html = ((build_playback.player(motion,compact=True) if motion else '') +
                          f'<div><a href="animations.html#{e(gid)}"><img class="schematic" src="{e(guide_strip)}" alt="Six-frame guide {e(gid)}"></a><div class="gcap">{e(guide_label)} <a href="animations.html#{e(gid)}">{e(gid)} / play</a></div></div>'
                          f'<div><img class="model" src="../guides/overlays/3d/{e(gid)}_strip.png"><div class="gcap">3D ghost, camera path</div></div>') if gid else '<div class="muted">no guide</div>'
            if gid == "cup_pour_eye_hold":
                guide_html += '<div class="gcap">Subject correction pending: sauce on plated brunch; legacy schematic depicts a cup.</div>'
            parts.append(f'<div class="steprow"><img class="preview" src="previews/{e(s["imageURL"])}">'
                         f'<div class="info"><div class="t">{i}. {e(s["title"])}</div>'
                         f'<div class="s">{e(s["shot"])} shot, {e(plan["angle"])}, {e(plan["start"])} to {e(plan["end"])}, {e(plan["move"])}, then {e(plan["transitionOut"])}, {int(s["seconds"])} s'
                         + (", both cameras" if s["pip"] else "") + "</div>"
                         f'<div class="line">{step_line(s)}</div>'
                         f'<div class="s" style="margin-top:2pt">{e(s["position"])}</div></div>{guide_html}</div>')
        parts.append("</div></div>")

parts.append('<div class="appendix"><h2>Menu item kinds and the review script for each</h2><table><tr><th>Review kind</th><th>Opening shot</th><th>Line pattern</th><th>Script</th></tr>')
for r in menu_rows:
    if len(r) >= 6:
        parts.append(f"<tr><td>{e(r[0])}</td><td>{e(r[3])}</td><td>{e(r[4])}</td><td>{e(r[5].strip('`'))}</td></tr>")
parts.append("</table></div>")
parts.append('<div class="appendix"><h2>Guide coverage</h2><p class="small">From guides/coverage.md: every step, its guide, whether a kit scene was reused, the move and hand-over, the jump check and the simulation result.</p>'
             '<table><tr><th>Script</th><th>Step</th><th>Guide</th><th>Reused</th><th>Angle</th><th>Move</th><th>Hand-over</th><th>Jump check</th><th>Simulation</th></tr>')
for r in coverage_rows:
    if len(r) >= 12:
        parts.append("<tr>" + "".join(f"<td>{e(c.strip('`'))}</td>" for c in (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[10], r[11])) + "</tr>")
parts.append("</table></div><script>"+build_playback.PLAYER_SCRIPT+"</script></body></html>")
open(os.path.join(HERE, "catalog.html"), "w", encoding="utf-8").write("\n".join(parts))
missing = [p for p in re.findall(r'src="([^"]+)"', "\n".join(parts)) if not os.path.exists(os.path.join(HERE, p))]
print(f"catalog.html: {len(templates['templates'])} scripts, {len(guide_ids)} strips, {len(menu_rows)} menu kinds, {len(coverage_rows)} coverage rows, missing images {len(missing)}")
