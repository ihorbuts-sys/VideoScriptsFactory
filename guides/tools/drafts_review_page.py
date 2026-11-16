"""Writes guides/revisions/<date>/drafts.html: every draft guide of that revision day (a folder with record.json and
export/), its looping animation, contact sheet, record facts and the owner questions from owner_questions.json, with
approve / needs work / reject and a comment saved through review_server.py (decisions/drafts-<date>.json).

Run: python3 -I guides/tools/drafts_review_page.py 2026-11-11  ->  http://127.0.0.1:8770/revisions/<date>/drafts.html
"""
import html
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_review_page import looping_copy  # noqa: E402

GUIDES = Path(__file__).resolve().parents[1]


def esc(text):
    return html.escape(str(text or ""))


def main(date):
    day = GUIDES / "revisions" / date
    questions = json.loads((day / "owner_questions.json").read_text()) if (day / "owner_questions.json").exists() else {}
    loop_dir = day / "_loop"
    loop_dir.mkdir(exist_ok=True)
    cards = []
    decisions_path = GUIDES / "review" / "decisions" / f"drafts-{date}.json"
    decisions = json.loads(decisions_path.read_text()) if decisions_path.exists() else {}
    hidden = []
    for record_path in sorted(day.rglob("record.json")):
        folder = record_path.parent
        if "archive" in folder.relative_to(day).parts:
            continue
        rec = json.loads(record_path.read_text())
        gid = rec["id"]
        anim = folder / "export" / f"{gid}.png"
        if not anim.exists():
            continue
        decided = decisions.get(gid, {})
        # Approved cards drop off the page; one re-rendered after the approval comes back for another look.
        if decided.get("choice") == "approve" and datetime.fromtimestamp(anim.stat().st_mtime).isoformat(timespec="seconds") <= decided.get("savedAt", ""):
            hidden.append(gid)
            continue
        looping_copy(anim, loop_dir / f"{gid}.png")
        published = GUIDES / "p0" / "renders" / f"{gid}.png"
        if published.exists():
            looping_copy(published, loop_dir / f"{gid}_published.png")
            media = (f'<figure><img class="anim" src="_loop/{gid}_published.png" alt=""><figcaption>Published</figcaption></figure>'
                     f'<figure><img class="anim" src="_loop/{gid}.png" alt=""><figcaption>New</figcaption></figure>')
        else:
            media = f'<figure><img class="anim" src="_loop/{gid}.png" alt=""><figcaption>New</figcaption></figure>'
        rel = lambda p: p.relative_to(day).as_posix()
        sheet = folder / "sheet.png"
        # A re-render of a live guide shows the published poster next to the new one (before / after).
        before, after = folder / "published_poster.png", folder / "export" / f"{gid}_poster.png"
        compare = (f'<div class="ba"><figure><img src="{rel(before)}" alt=""><figcaption>Published</figcaption></figure>'
                   f'<figure><img src="{rel(after)}" alt=""><figcaption>Re-render</figcaption></figure></div>'
                   if before.exists() and after.exists() and not published.exists() else "")
        extras = "".join(f'<figure><img class="extra" src="{rel(folder / n)}" alt=""><figcaption>{c}</figcaption></figure>'
                         for n, c in (("overlay.png", "Your red lines on frame 1"), ("wrist_crop.png", "Wrist close-up"))
                         if (folder / n).exists())
        compare = compare + (f'<div class="extras">{extras}</div>' if extras else "")
        facts = [("Shot type", rec.get("shotType")), ("Length", f'{rec.get("durationSec")} s'),
                 ("Start", rec.get("startTrigger")), ("Camera", rec.get("camera")),
                 ("Orientation", rec.get("phoneOrientation")), ("Based on", rec.get("sourceScene")),
                 ("New objects", rec.get("newObjects"))]
        preset = rec.get("capturePreset") or {}
        facts += [("Stabilization", preset.get("stabilization")), ("Frame rate", preset.get("frameRate"))]
        dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in facts if v not in (None, ""))
        qs = "".join(f"<li>{esc(q)}</li>" for q in questions.get(gid, {}).get("questions", []))
        step = questions.get(gid, {}).get("step", "")
        cards.append(
            f'<section class="obj" data-key="{esc(gid)}"><div class="media">{media}</div><div class="body"><h3>{esc(rec.get("title"))}</h3><code>{esc(gid)}</code>'
            f'<p class="mut">{esc(step)}</p>{compare}<p>{esc(rec.get("invariant"))}</p><dl>{dl}</dl>'
            f'{"<p class=lbl>Questions for you</p><ul>" + qs + "</ul>" if qs else ""}'
            f'{f"<details><summary>Contact sheet</summary><img class=sheet src={rel(sheet)} alt=></details>" if sheet.exists() else ""}'
            f'<form class="decide"><label><input type="radio" name="d-{esc(gid)}" value="approve"> approve</label>'
            f'<label><input type="radio" name="d-{esc(gid)}" value="needs work"> needs work</label>'
            f'<label><input type="radio" name="d-{esc(gid)}" value="reject"> reject</label> <span class="state"></span>'
            f'<textarea rows="3" placeholder="Comment, or your answers to the questions"></textarea></form></div></section>')
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Draft Guides Review</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1f;--mut:#6b6b70;--card:#fff;--line:#e2e0da;--acc:#b8860b;--anim:#24352d}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141416;--fg:#ececee;--mut:#9a9aa2;--card:#1f1f23;--line:#33333a;--acc:#e3b23c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,system-ui,sans-serif}}
header{{padding:16px;border-bottom:1px solid var(--line)}}h1{{margin:0;font-size:20px}}main{{padding:0 16px 40px;max-width:1100px;margin:auto}}
.obj{{display:flex;gap:16px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}}
.obj.done{{border-color:#3a9a5b}}.media{{flex:0 0 auto;display:flex;gap:8px}}.extras{{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}}.extras figure{{margin:0;font-size:12px;color:var(--mut)}}.extra{{max-width:100%;width:420px;border-radius:6px}}.media figure{{margin:0;text-align:center;font-size:12px;color:var(--mut)}}.anim{{width:200px;aspect-ratio:9/16;background:var(--anim);border-radius:8px;object-fit:contain}}
.body{{flex:1;min-width:0}}h3{{margin:0}}code,.mut,.state{{color:var(--mut);font-size:12px}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:1px 10px;font-size:12px}}dt{{color:var(--mut)}}dd{{margin:0}}
.lbl{{font-weight:600;color:var(--acc);margin:8px 0 2px}}ul{{margin:0 0 6px 18px;padding:0}}.sheet{{width:100%;border-radius:6px;margin-top:6px}}
.decide{{border-top:1px solid var(--line);margin-top:8px;padding-top:6px}}.decide label{{margin-right:12px}}
.ba{{display:flex;gap:8px;margin:8px 0}}.ba figure{{margin:0;flex:0 1 160px}}.ba img{{width:100%;aspect-ratio:9/16;background:var(--anim);border-radius:6px;object-fit:contain}}
.ba figcaption{{font-size:12px;color:var(--mut);text-align:center}}
textarea{{width:100%;font:inherit;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px;margin-top:4px}}
@media (max-width:640px){{.obj{{flex-direction:column}}.media{{flex-basis:auto}}}}
</style></head><body><header><h1>Draft guides {esc(date)}</h1><p class="mut" id="status"></p><p class="mut">{len(hidden)} approved drafts hidden: {esc(", ".join(hidden)) or "none"}</p></header><main>{"".join(cards)}</main>
<script>
const API = "/api/decisions/drafts-{esc(date)}";
const cards = [...document.querySelectorAll(".obj")], status = document.getElementById("status"), timers = {{}};
const read = c => {{ const r = c.querySelector("input:checked"); return {{choice: r ? r.value : "", comment: c.querySelector("textarea").value}}; }};
const paint = (c, note) => {{ c.classList.toggle("done", !!read(c).choice); c.querySelector(".state").textContent = note || ""; }};
const count = () => status.textContent = cards.filter(c => read(c).choice).length + " of " + cards.length + " drafts decided. Animations loop here.";
function save(c) {{
  paint(c); count(); const k = c.dataset.key; clearTimeout(timers[k]);
  timers[k] = setTimeout(async () => {{ const b = {{}}; b[k] = read(c);
    try {{ const j = await (await fetch(API, {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify(b)}})).json(); paint(c, "saved " + j.at.slice(11, 16)); }}
    catch (e) {{ paint(c, "not saved: is review_server.py running?"); }} }}, 500);
}}
(async () => {{
  let saved = {{}}; try {{ saved = await (await fetch(API)).json(); }} catch (e) {{}}
  cards.forEach(c => {{ const d = saved[c.dataset.key] || {{}};
    if (d.choice) {{ const r = c.querySelector(`input[value="${{d.choice}}"]`); if (r) r.checked = true; }}
    c.querySelector("textarea").value = d.comment || "";
    c.addEventListener("input", () => save(c)); c.addEventListener("change", () => save(c));
    paint(c, d.savedAt ? "saved " + d.savedAt.slice(11, 16) : ""); }});
  count();
}})();
</script></body></html>"""
    (day / "drafts.html").write_text(page)
    print(day / "drafts.html", len(cards), "drafts")


if __name__ == "__main__":
    main(sys.argv[1])
