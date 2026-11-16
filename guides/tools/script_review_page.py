"""Writes guides/review/scripts.html: every guided (v0) script as served by the Scriptwriter dev catalog, one row per
step with its preview picture, prompter or line, captions, and each of its guides looping with its camera preset.

Run: python3 guides/tools/script_review_page.py [--catalog ~/Documents/Development/Scriptwriter/catalog]
Serve: python3 -m http.server 8770 --bind 127.0.0.1 --directory guides  ->  /review/scripts.html
"""
import argparse
import html
import json
import re
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "guides" / "review"


def looping_copy(src, dst):
    """Copies an APNG with its acTL play count set to 0 (loop forever)."""
    data = bytearray(src.read_bytes())
    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = bytes(data[pos + 4:pos + 8])
        if kind == b"acTL":
            body = data[pos + 8:pos + 8 + length]
            body[4:8] = struct.pack(">I", 0)
            data[pos + 8:pos + 8 + length] = body
            crc = zlib.crc32(kind + bytes(body)) & 0xFFFFFFFF
            data[pos + 8 + length:pos + 12 + length] = struct.pack(">I", crc)
            break
        pos += 12 + length
    dst.write_bytes(bytes(data))


def asset(catalog, rel, loop=False):
    if not rel:
        return None
    src = catalog / rel
    if not src.exists():
        return None
    dst = OUT / "assets" / rel.replace("/", "_")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if loop:
        looping_copy(src, dst)
    else:
        shutil.copyfile(src, dst)
    return "assets/" + dst.name


def esc(text):
    return html.escape(str(text or ""))


def preset_rows(guide):
    p = guide.get("capturePreset") or {}
    rows = [
        ("Camera", guide.get("camera")),
        ("Length", f"{guide.get('durationSec')} s"),
        ("Start", guide.get("startTrigger")),
        ("Stabilization", p.get("stabilization")),
        ("Frame rate", p.get("frameRate")),
        ("Continuous focus", "yes" if p.get("continuousFocus") else "no"),
        ("Locks focus, exposure, WB", "yes" if p.get("locksFocusExposureWhiteBalance") else "no"),
        ("Lens locked", "yes" if p.get("lensLocked") else "no"),
    ]
    for key in sorted(set(p) - {"stabilization", "frameRate", "continuousFocus", "locksFocusExposureWhiteBalance",
                                "lensLocked"}):
        rows.append((key, p[key]))
    return "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows if v not in (None, ""))


def guide_card(catalog, gid, guide, recommended):
    if guide is None:
        return f'<div class="guide missing"><b>{esc(gid)}</b><p>Not served (archived or missing).</p></div>'
    anim = asset(catalog, guide.get("animation"), loop=True)
    tag = '<span class="tag">recommended</span>' if recommended else ""
    media = f'<img class="anim" src="{anim}" alt="" loading="lazy">' if anim else '<div class="anim empty">no file</div>'
    return (f'<div class="guide">{media}<div class="meta"><b>{esc(guide.get("title"))}</b> {tag}'
            f'<code>{esc(gid)}</code><p class="inv">{esc(guide.get("invariant"))}</p>'
            f'<dl>{preset_rows(guide)}</dl></div></div>')


AUDIT = ROOT / "research" / "spoken_lines" / "audit_live_lines.md"


def audit_rows():
    """'template / step' -> (result, why, proposal) from the line audit table."""
    out = {}
    if not AUDIT.exists():
        return out
    for line in AUDIT.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and " / " in cells[0] and cells[3] in ("matches", "weaker", "breaks"):
            out[cells[0]] = (cells[3], cells[4], cells[5])
    return out


LABELS = {"matches": "Live line is fine", "weaker": "Live line could be better",
          "breaks": "Live line breaks a rule"}


def audit_block(entry):
    if not entry:
        return ""
    result, why, proposal = entry
    prop = "" if proposal.startswith("keep") else f'<p><span class="lbl">Proposed</span> <b>{esc(proposal)}</b></p>'
    note = f' ({esc(proposal)})' if proposal.startswith("keep") and proposal != "keep" else ""
    return (f'<div class="audit {result}"><p><span class="res">{esc(LABELS[result])}</span>{note} {esc(why)}</p>{prop}</div>')


def decision_form(key, live, audit, guide_ids):
    proposal = re.sub(r"\s*\([^)]*\)\s*$", "", audit[2]) if audit and not audit[2].startswith("keep") else ""
    opts = [("keep", f"Keep live: {live}" if live else "Keep as is")]
    if proposal:
        opts.append(("proposal", f"Use proposal: {proposal}"))
    opts.append(("own", "My own text"))
    radios = "".join(f'<label class="opt"><input type="radio" name="{esc(key)}" value="{v}"> {esc(t)}</label>'
                     for v, t in opts)
    guide_sel = "".join(f'<label class="gsel">{esc(g)} <select data-guide="{esc(g)}"><option value="">-</option>'
                        f'<option value="keep">keep</option><option value="drop">drop</option></select></label>'
                        for g in guide_ids)
    return (f'<form class="decide" data-key="{esc(key)}" data-proposal="{esc(proposal)}" data-live="{esc(live)}">'
            f'<p class="lbl">Your decision <span class="state"></span></p>{radios}'
            f'<textarea class="own" placeholder="Your line (placeholders like {{venue.name}} work)" rows="2"></textarea>'
            f'{"<p class=lbl>Guides</p><div class=gsels>" + guide_sel + "</div>" if guide_sel else ""}'
            f'<textarea class="comment" placeholder="Comment (optional)" rows="2"></textarea></form>')


def step_row(catalog, step, guides, audit=None, key=""):
    preview = asset(catalog, step.get("imageURL"))
    img = f'<img class="preview" src="{preview}" alt="">' if preview else '<div class="preview empty">no preview</div>'
    prompter = step.get("prompter") or ""
    words = []
    if prompter:
        words.append(f'<p><span class="lbl">Prompter</span> {esc(prompter)}</p>')
    if step.get("line") and step.get("line") != prompter:
        words.append(f'<p><span class="lbl">Line</span> {esc(step["line"])}</p>')
    caps = step.get("captions") or []
    if caps:
        words.append('<p><span class="lbl">Captions</span></p><ul>' + "".join(
            f'<li><b>{esc(c.get("text"))}</b> - {esc(c.get("script"))}</li>' for c in caps) + "</ul>")
    words.append(audit_block(audit))
    head = (f'<h3>{esc(step.get("title"))} <code>{esc(step.get("id"))}</code></h3>'
            f'<p class="facts">{esc(step.get("shotType"))} - {esc(step.get("complexity"))} - {esc(step.get("camera"))} '
            f'camera - {esc(step.get("seconds"))} s - {esc(step.get("voice"))}</p>'
            f'<p class="idea">{esc(step.get("idea"))}</p><p class="dir">{esc(step.get("direction"))}</p>')
    ids = step.get("guides") or []
    words.append(decision_form(key, step.get("line") or prompter, audit, ids))
    cards = "".join(guide_card(catalog, g, guides.get(g), i == 0) for i, g in enumerate(ids))
    return (f'<section class="step"><div class="left">{img}</div><div class="right">{head}{"".join(words)}'
            f'<div class="guides">{cards or "<p>No guides.</p>"}</div></div></section>')


JS = r'''
<script>
const API = "/api/decisions/lines";
const forms = [...document.querySelectorAll("form.decide")];
const status = document.getElementById("status");
let saved = {};
function read(f) {
  const r = f.querySelector("input[type=radio]:checked");
  const guides = {};
  f.querySelectorAll("select[data-guide]").forEach(s => { if (s.value) guides[s.dataset.guide] = s.value; });
  const choice = r ? r.value : "";
  const text = choice === "own" ? f.querySelector(".own").value : choice === "proposal" ? f.dataset.proposal : choice === "keep" ? f.dataset.live : "";
  return {choice, text, own: f.querySelector(".own").value, comment: f.querySelector(".comment").value, guides};
}
function paint(f) {
  const d = read(f);
  f.classList.toggle("ownon", d.choice === "own");
  f.classList.toggle("done", !!d.choice);
  const s = saved[f.dataset.key];
  f.querySelector(".state").textContent = s && s.savedAt ? "saved " + s.savedAt.slice(11, 16) : "";
}
function count() {
  const n = forms.filter(f => read(f).choice).length;
  status.textContent = n + " of " + forms.length + " steps decided";
}
const timers = {};
function save(f) {
  paint(f); count();
  clearTimeout(timers[f.dataset.key]);
  timers[f.dataset.key] = setTimeout(async () => {
    const body = {}; body[f.dataset.key] = read(f);
    try {
      const r = await fetch(API, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
      const j = await r.json();
      saved[f.dataset.key] = {...body[f.dataset.key], savedAt: j.at};
      paint(f);
    } catch (e) { f.querySelector(".state").textContent = "not saved: is review_server.py running?"; }
  }, 500);
}
(async () => {
  try { saved = await (await fetch(API)).json(); } catch (e) { status.textContent = "Saving needs guides/tools/review_server.py"; }
  forms.forEach(f => {
    const d = saved[f.dataset.key];
    if (d) {
      const r = f.querySelector(`input[value="${d.choice}"]`); if (r) r.checked = true;
      f.querySelector(".own").value = d.own || "";
      f.querySelector(".comment").value = d.comment || "";
      Object.entries(d.guides || {}).forEach(([g, v]) => { const s = f.querySelector(`select[data-guide="${g}"]`); if (s) s.value = v; });
    }
    f.addEventListener("input", () => save(f));
    f.addEventListener("change", () => save(f));
    paint(f);
  });
  count();
})();
</script>'''

CSS = """
:root{--bg:#f6f5f2;--fg:#1d1d1f;--mut:#6b6b70;--card:#fff;--line:#e2e0da;--acc:#b8860b;--anim:#2a2a2e}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececee;--mut:#9a9aa2;--card:#1f1f23;--line:#33333a;--acc:#e3b23c;--anim:#000}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,system-ui,sans-serif}
header{padding:16px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2}
nav a{margin-right:12px;color:var(--acc);text-decoration:none;white-space:nowrap}h1{margin:0 0 6px;font-size:20px}
main{padding:0 16px 40px;max-width:1400px;margin:auto}h2{margin:32px 0 4px}.sum{color:var(--mut);margin:0 0 12px}
.step{display:flex;gap:16px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0}
.left{flex:0 0 180px}.preview{width:180px;aspect-ratio:9/16;object-fit:cover;border-radius:8px;display:block}
.empty{display:flex;align-items:center;justify-content:center;color:var(--mut);border:1px dashed var(--line)}
.right{flex:1;min-width:0}h3{margin:0}code{font-size:12px;color:var(--mut);margin-left:6px}
.facts,.idea{color:var(--mut);margin:2px 0}.dir{margin:4px 0}.lbl{font-weight:600;color:var(--acc);margin-right:6px}
ul{margin:2px 0 6px 18px;padding:0}.guides{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px}
.guide{display:flex;gap:10px;width:380px;max-width:100%;border:1px solid var(--line);border-radius:10px;padding:8px}
.anim{width:120px;aspect-ratio:9/16;background:var(--anim);border-radius:6px;object-fit:contain;flex:0 0 120px}
.meta{min-width:0}.meta code{display:block;margin:2px 0}.inv{margin:4px 0;font-size:13px}
.tag{font-size:11px;background:var(--acc);color:#000;border-radius:4px;padding:1px 5px}
dl{display:grid;grid-template-columns:auto 1fr;gap:1px 8px;margin:4px 0 0;font-size:12px}dt{color:var(--mut)}dd{margin:0}
.missing{color:var(--mut)}
.audit{border-left:3px solid var(--line);padding:4px 10px;margin:6px 0;background:var(--bg);border-radius:4px}
.audit p{margin:2px 0}.res{font-weight:700;text-transform:uppercase;font-size:11px;margin-right:6px}
.decide{border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:8px 0}
.decide.done{border-color:#3a9a5b}.opt{display:block;margin:3px 0}.state{font-weight:400;color:var(--mut);margin-left:6px}
textarea{width:100%;font:inherit;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px;margin-top:4px}
.own{display:none}.decide.ownon .own{display:block}.gsels{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px}
select{font:inherit;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:4px}
#status{font-size:12px;color:var(--mut)}
.audit.matches{border-color:#3a9a5b}.audit.weaker{border-color:#d4a017}.audit.breaks{border-color:#d0453a}
@media (max-width:640px){.step{flex-direction:column}.left{flex-basis:auto}.guide{width:100%}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=str(Path.home() / "Documents/Development/Scriptwriter/catalog"))
    catalog = Path(ap.parse_args().catalog).expanduser()
    cat = json.loads((catalog / "catalog.json").read_text())
    guides = json.loads((catalog / "shot_types.json").read_text())["guides"]
    if (OUT / "assets").exists():
        shutil.rmtree(OUT / "assets")
    audits = audit_rows()
    scripts = [t for t in cat["templates"] if any("complexity" in s for s in t["steps"])]
    nav = "".join(f'<a href="#{esc(t["id"])}">{esc(t["title"])} ({esc(t["id"])})</a>' for t in scripts)
    body = []
    for t in scripts:
        total = sum(s.get("seconds", 0) for s in t["steps"])
        body.append(f'<h2 id="{esc(t["id"])}">{esc(t["title"])} <code>{esc(t["id"])}</code></h2>'
                    f'<p class="sum">{esc(t.get("summary"))} - {", ".join(map(esc, t.get("venueKinds", [])))} - '
                    f'{len(t["steps"])} steps, {total} s</p>')
        body.extend(step_row(catalog, s, guides, audits.get(f'{t["id"]} / {s["id"]}'), f'{t["id"]}/{s["id"]}') for s in t["steps"])
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>Live Guided Scripts</title>'
            f'<style>{CSS}</style></head><body><header><h1>Live guided scripts</h1>'
            f'<p class="sum">From the dev catalog generated {esc(cat.get("generatedAt"))}. Guides loop here; in the '
            f'app they play once per take. Each step’s live line is rated: green fine, yellow could be better (the proposal is stronger), red breaks a rule. Proposals are not live until you pick them.</p><p id="status"></p><nav>{nav}</nav></header><main>{"".join(body)}</main>{JS}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "scripts.html").write_text(page)
    print(OUT / "scripts.html", len(scripts), "scripts")


if __name__ == "__main__":
    main()
