"""Writes guides/review/objects.html from OBJECTS.md: open requests, approved P0 objects, line-art studies, library
models and rejected items. Each object shows its single-object line-art render first (guides/review/objects_renders,
written by guides/tools/render_objects.py, with size and face count), then the posters of active guides that use it
(approved) or its design picture (study, library). Study, library and candidate renders are labelled test renders.

Run: python3 guides/tools/objects_page.py   Serve: the guides/ http.server on 8770 -> /review/objects.html
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "guides" / "review"
ASSETS = OUT / "objects_assets"
RENDERS = ROOT / "guides" / "p0" / "renders"
OBJECT_RENDERS = OUT / "objects_renders"
MODELS = ROOT / "model_refferences" / "objects"
PICTURE_NAMES = ("preview.png", "three-quarter.png", "projections.jpg", "model-projections.jpg", "sheet.png")


def esc(text):
    return html.escape(str(text or ""))


def inline(text):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(text))


def tables(md):
    """Yields (section heading, header cells, rows) for every markdown table."""
    heading, rows, header = "", [], None
    for line in md.splitlines() + [""]:
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif not set("".join(cells)) <= set("-: "):
                rows.append(cells)
        elif header is not None:
            yield heading, header, rows
            header, rows = None, []


def active_guides():
    plan = json.loads((ROOT / "guides" / "p0" / "plan.json").read_text())
    records = plan.get("guides", plan) if isinstance(plan, dict) else plan
    ids = [r["id"] for r in records] if isinstance(records, list) else list(records)
    archived = set(json.loads((ROOT / "guides" / "p0" / "promoted.json").read_text()).get("archived", []))
    return {g for g in ids if g not in archived and (RENDERS / f"{g}_poster.png").exists()}


def guide_objects():
    """guide id -> its Objects column text from GUIDE_INDEX.md."""
    out = {}
    for _, header, rows in tables((ROOT / "GUIDE_INDEX.md").read_text()):
        if "Objects" in header:
            i = header.index("Objects")
            for r in rows:
                if len(r) > i:
                    out[r[0]] = r[i]
    return out


def copy(src):
    ASSETS.mkdir(parents=True, exist_ok=True)
    dst = ASSETS / str(src.relative_to(ROOT)).replace("/", "_")
    shutil.copyfile(src, dst)
    return "objects_assets/" + dst.name


def posters_for(row_text, active, objects, limit=4):
    named = [g for g in sorted(active, key=len, reverse=True) if re.search(rf"\b{re.escape(g)}\b", row_text)]
    if not named:
        helpers = re.findall(r"`([a-z_]+)(?:\(\))?`", row_text.split("|")[0] if "|" in row_text else row_text)
        named = [g for g, text in objects.items() if g in active and any(f"`{h}`" in text or f"existing `{h}`" in text
                                                                          for h in helpers)]
    seen, out = set(), []
    for g in named:
        if g not in seen and len(out) < limit:
            seen.add(g)
            out.append((g, copy(RENDERS / f"{g}_poster.png")))
    return out


def model_picture(name):
    folder = MODELS / name
    if not folder.is_dir():
        return None
    for pic in PICTURE_NAMES:
        found = sorted(folder.rglob(pic))
        if found:
            return copy(found[0])
    return None


def figure(src, caption):
    return f'<figure><img src="{src}" alt="" loading="lazy"><figcaption>{esc(caption)}</figcaption></figure>'


def object_index():
    path = OBJECT_RENDERS / "index.json"
    return json.loads(path.read_text()).get("objects", []) if path.exists() else []


def facts(entry):
    out = []
    if entry.get("dimensions_m"):
        out.append(" x ".join(f"{v:.3f}" for v in entry["dimensions_m"]) + " m")
    if entry.get("faces") is not None:
        out.append(f"{entry['faces']:,} faces")
    return ", ".join(out)


def renders(entry):
    """The object's own line-art stills, or why it has none."""
    files = [f for f in entry.get("files") or [] if (OBJECT_RENDERS / f).exists()]
    if not files:
        reason = entry.get("error") or "; ".join(entry.get("notes") or []) or "not rendered yet"
        return f'<p class="mut">No render: {esc(reason)}</p>'
    def pic(f, caption):
        return (f'<figure class="render"><a href="objects_renders/{esc(f)}"><img src="objects_renders/{esc(f)}" alt="" '
                f'loading="lazy"></a><figcaption>{esc(caption)}</figcaption></figure>')
    out = []
    for f in files:
        view = "top view" if f.endswith("_top.png") else "front view" if f.endswith("_front.png") else "three-quarter, 30 deg down"
        before = f[:-4] + "_before.png"
        if (OBJECT_RENDERS / before).exists():
            out.append(pic(before, "before dot cleanup, " + view) + pic(f, "after dot cleanup, " + view))
        else:
            out.append(pic(f, view))
    return f'<div class="pics renders">{"".join(out)}</div>'


def render_card(entry, extra=""):
    test = entry["section"] != "approved"
    label = '<p class="warn">Test render, not approved</p>' if test else ""
    notes = "".join(f"<li>{esc(n)}</li>" for n in entry.get("notes") or [])
    notes = f'<details><summary>Render notes</summary><ul>{notes}</ul></details>' if notes and entry.get("files") else ""
    return (f'<div class="obj"><h3>{esc(entry.get("label") or entry["id"])}</h3>{label}{renders(entry)}'
            f'<p><span class="tag">{esc(entry["id"])}</span> {esc(facts(entry))}</p>'
            f'<p class="mut">{esc(entry.get("status"))} - <code>{esc(entry.get("source"))}</code></p>{notes}{extra}</div>')


def table_html(header, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


IMAGE = re.compile(r"[\w./-]+\.(?:png|jpe?g|webp)", re.I)


def row_pictures(row, limit=4):
    """Images a request row names by path; a bare file name resolves next to the last full path before it."""
    out, base = [], None
    for match in IMAGE.findall(" | ".join(row)):
        path = ROOT / match if "/" in match else (base / match if base else None)
        if "/" in match:
            base = (ROOT / match).parent
        if path is None or not path.is_file():
            hits = sorted(OUT.rglob(Path(match).name)) if path is None or not path.exists() else []
            path = hits[0] if hits else None
        if path and path.is_file() and path not in [p for p, _ in out]:
            out.append((path, path.name))
        if len(out) == limit:
            break
    # Rows that name no image get the renders of the existing objects they mention (the "nearest existing" ones).
    if not out:
        text = " | ".join(row).lower()
        index = json.loads((OUT / "objects_renders" / "index.json").read_text())["objects"]
        builders = set(re.findall(r"(\w+)\(", text)) | set(re.findall(r"\b\w+\.(\w+)\b", text))
        seen = set()
        for e in index:
            base = e["id"].removeprefix("candidate_")
            pic = OUT / "objects_renders" / f"{e['id']}.png"
            names = {base, base.replace("_", " ")}
            named = any(re.search(rf"(?<![\w]){re.escape(n)}(?![\w])", text) for n in names)
            built = any(base.startswith(b) for b in builders if len(b) > 3)
            if pic.is_file() and base not in seen and (named or built):
                seen.add(base)
                out.append((pic, f"nearest: {e.get('label') or base}"))
            if len(out) == 3:
                break
    return "".join(f'<a href="{(src := copy(p))}" target="_blank">{figure(src, name)}</a>' for p, name in out)


def requests_table(header, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in header) + "<th>Pictures</th>"
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r)
                   + f'<td class="pics">{row_pictures(r) or "<span class=mut>none</span>"}</td></tr>' for r in rows)
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


JS = r'''<script>
const API = "/api/decisions/objects";
const cards = [...document.querySelectorAll(".obj")];
const status = document.getElementById("status");
let saved = {};
const timers = {};
function keyOf(c) { return (c.closest("section,div[id]") ? "" : "") + c.querySelector("h3").textContent.trim(); }
function count() { status.textContent = cards.filter(c => c.querySelector("input:checked")).length + " of " + cards.length + " objects decided"; }
function read(c) { const r = c.querySelector("input:checked"); return {choice: r ? r.value : "", comment: c.querySelector("textarea").value}; }
function paint(c, note) { c.classList.toggle("done", !!read(c).choice); c.querySelector(".state").textContent = note || ""; }
function save(c) {
  paint(c); count();
  const k = keyOf(c);
  clearTimeout(timers[k]);
  timers[k] = setTimeout(async () => {
    const body = {}; body[k] = read(c);
    try { const j = await (await fetch(API, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)})).json(); paint(c, "saved " + j.at.slice(11, 16)); }
    catch (e) { paint(c, "not saved: is review_server.py running?"); }
  }, 500);
}
(async () => {
  try { saved = await (await fetch(API)).json(); } catch (e) { status.textContent = "Saving needs guides/tools/review_server.py"; }
  cards.forEach((c, i) => {
    const k = keyOf(c), d = saved[k] || {};
    const f = document.createElement("form"); f.className = "decide";
    f.innerHTML = ["approve", "needs work", "reject"].map(v => `<label><input type="radio" name="o${i}" value="${v}"> ${v}</label>`).join(" ")
      + ' <span class="state"></span><textarea rows="2" placeholder="Comment (optional)"></textarea>';
    c.appendChild(f);
    if (d.choice) { const r = f.querySelector(`input[value="${d.choice}"]`); if (r) r.checked = true; }
    f.querySelector("textarea").value = d.comment || "";
    f.addEventListener("input", () => save(c)); f.addEventListener("change", () => save(c));
    paint(c, d.savedAt ? "saved " + d.savedAt.slice(11, 16) : "");
  });
  count();
})();
</script>'''

CSS = """
.decide{margin-top:8px;border-top:1px solid var(--line);padding-top:6px;font-size:13px}.decide label{margin-right:10px}.obj.done{border-color:#3a9a5b}.state{color:var(--mut);font-size:12px}.decide textarea{width:100%;font:inherit;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px;margin-top:4px}#status{font-size:12px;color:var(--mut)}
:root{--bg:#f6f5f2;--fg:#1d1d1f;--mut:#6b6b70;--card:#fff;--line:#e2e0da;--acc:#b8860b;--img:#2a2a2e}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececee;--mut:#9a9aa2;--card:#1f1f23;--line:#33333a;--acc:#e3b23c;--img:#000}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,system-ui,sans-serif}
header{padding:16px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2}
h1{margin:0 0 6px;font-size:20px}nav a{margin-right:12px;color:var(--acc);text-decoration:none}
main{padding:0 16px 40px;max-width:1400px;margin:auto}h2{margin:32px 0 4px}.mut{color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.obj{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
.obj h3{margin:0 0 4px;font-size:15px}.obj p{margin:2px 0}code{font-size:12px;color:var(--mut)}
.pics{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}figure{margin:0;width:88px}
figure img{width:88px;aspect-ratio:9/16;object-fit:contain;background:var(--img);border-radius:6px;display:block}
td.pics{min-width:200px}td.pics figure{width:96px}td.pics figure img{width:96px;aspect-ratio:auto;max-height:170px}td.pics a{display:block}.wide figure{width:140px}.wide figure img{width:140px;aspect-ratio:1;object-fit:contain;background:#fff}
figcaption{font-size:10px;color:var(--mut);word-break:break-all}
.renders figure.render{width:calc(50% - 3px);min-width:140px}.renders figure.render img{width:100%;aspect-ratio:1;object-fit:contain;background:#24352d}
.renders figure.render:only-child{width:100%}
.warn{color:var(--acc);font-weight:600;font-size:12px}.sub{border-top:1px solid var(--line);padding-top:6px;margin-top:6px}
h3.cat{margin:20px 0 2px;font-size:16px}details{font-size:12px;color:var(--mut)}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.tag{font-size:11px;border-radius:4px;padding:1px 5px;background:var(--line)}
"""


def main():
    md = (ROOT / "OBJECTS.md").read_text()
    active, objects = active_guides(), guide_objects()
    index = object_index()
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    sections = []
    for heading, header, rows in tables(md):
        if heading.startswith("Requests"):
            rows = [r for r in rows if not r[0].startswith("(add")]
            sections.append(("requests", "Open requests (you decide each)", requests_table(header, rows)))
        elif heading.startswith("1a"):
            cards = []
            for r in rows:
                pics = posters_for(" | ".join(r), active, objects)
                strip = "".join(figure(src, g) for g, src in pics) or '<p class="mut">No active guide poster found.</p>'
                own = [e for e in index if e["section"] == "approved" and e.get("row") and e["row"] in r[0]]
                own_html = "".join(f'<div class="sub"><p><b>{esc(e.get("label"))}</b> <span class="tag">{esc(e["id"])}</span> '
                                   f'{esc(facts(e))}</p>{renders(e)}</div>' for e in own) or renders({})
                cards.append(f'<div class="obj"><h3>{inline(r[0])}</h3><p><span class="tag">{esc(r[1])}</span> '
                             f'{esc(r[4])}</p>{own_html}<p class="mut">{inline(r[3])} - {inline(r[2])}</p>'
                             f'<p class="mut">Used in: {inline(r[5])}</p><p class="mut">In the guides:</p>'
                             f'<div class="pics">{strip}</div></div>')
            sections.append(("approved", f"Approved in P0 line art ({len(rows)})",
                             '<p class="mut">Each object alone in the guide line art first, then the posters of active '
                             'guides that use it.</p><div class="grid">' + "".join(cards) + "</div>"))
        elif heading.startswith("1b"):
            cards = []
            for r in rows:
                name = r[2].strip("`").split("/")[0] if "/" in r[2] else r[0].split()[0]
                pic = model_picture(name)
                own = [e for e in index if e["section"] == "study" and e.get("row") == r[0]]
                design = f'<p class="mut">Design picture:</p><div class="pics wide">{figure(pic, name)}</div>' if pic else ""
                if own:
                    cards.append(render_card(own[0], f'<p class="mut">{inline(r[3])} - {inline(r[2])}</p>{design}'))
                else:
                    cards.append(f'<div class="obj"><h3>{inline(r[0])}</h3><p class="warn">Test render, not approved</p>'
                                 f'{renders({})}<p><span class="tag">{esc(r[1])}</span> {inline(r[4])}</p>'
                                 f'<p class="mut">{inline(r[3])} - {inline(r[2])}</p>{design}</div>')
            sections.append(("study", "Line-art study only, not in P0",
                             '<p class="mut">Line-art renders here are test renders, not approvals.</p>'
                             '<div class="grid">' + "".join(cards) + "</div>"))
        elif heading.startswith("1c"):
            cards = []
            for r in rows:
                own = [e for e in index if e["section"] == "library" and e.get("row") == r[0]]
                rendered = {e["id"] for e in own}
                names = sorted({n for n in re.findall(r"\b([a-z][a-z_]+)\b", r[1]) if (MODELS / n).is_dir()} - rendered)
                pics = "".join(figure(p, n) for n in names if (p := model_picture(n)))
                models = []
                for e in own:
                    pic = model_picture(e["id"]) if (MODELS / e["id"]).is_dir() else None
                    design = f'<p class="mut">Design picture:</p><div class="pics wide">{figure(pic, e["id"])}</div>' if pic else ""
                    models.append(render_card(e, design))
                rest = f'<p class="mut">Other pictures:</p><div class="pics wide">{pics}</div>' if pics else ""
                cards.append(f'<h3 class="cat">{esc(r[0])}</h3><p class="mut">{inline(r[1])}</p>{rest}'
                             f'<div class="grid">{"".join(models)}</div>')
            sections.append(("library", "Library models never rendered in P0 line art",
                             '<p class="mut">Each model\'s line-art render first (a test render, not an approval), then its '
                             'design or model picture, which is not the guide style. Each needs your approval of a line-art '
                             'render before a guide uses it.</p>' + "".join(cards)))
            candidates = [e for e in index if e["section"] == "candidate"]
            if candidates:
                sections.append(("candidates", "Request candidates",
                                 '<div class="grid">' + "".join(render_card(e) for e in candidates) + "</div>"))
        elif heading.startswith("1d"):
            sections.append(("rejected", "Rejected or withdrawn", table_html(header, rows)))
    nav = "".join(f'<a href="#{k}">{esc(t)}</a>' for k, t, _ in sections)
    body = "".join(f'<h2 id="{k}">{esc(t)}</h2>{c}' for k, t, c in sections)
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>Guide Objects</title><style>{CSS}</style></head>'
            f'<body><header><h1>Guide objects</h1><p class="mut">Generated from OBJECTS.md and the active P0 '
            f'guides.</p><p id="status"></p><nav>{nav}</nav></header><main>{body}</main>{JS}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "objects.html").write_text(page)
    print(OUT / "objects.html", [(k, c.count('class="obj"')) for k, _, c in sections])


if __name__ == "__main__":
    main()
