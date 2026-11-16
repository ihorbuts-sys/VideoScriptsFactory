"""Prepare small sibling-kit edits, preserving its existing uncommitted work."""
import difflib
import hashlib
import json
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
KIT=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit')


def main():
    plan=[]
    def stage(relative,updated):
        target=KIT/relative;source=target.read_text() if target.exists() else ''
        staged=HERE/'patches'/relative;staged.parent.mkdir(parents=True,exist_ok=True);staged.write_text(updated)
        plan.append(dict(target=str(target),staged=str(staged),before_sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None))
        (HERE/'patches'/(target.name+'.diff')).write_text(''.join(difflib.unified_diff(source.splitlines(True),updated.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative)))

    relative='tools/scriptwriter/server.py';s=(KIT/relative).read_text()
    s=s.replace('import secrets\n','import secrets\nimport shutil\n',1)
    s=s.replace('_catalog = None\n','_catalog = None\n_catalog_revision = None\n',1)
    start=s.index('def catalog():');end=s.index('\n\ndef file_url',start)
    s=s[:start]+'''def catalog():
    """Reload a completely published catalog when its atomic index changes."""
    global _catalog, _catalog_revision
    path = os.path.join(CATALOG_DIR, "catalog.json")
    if not os.path.isfile(path):
        raise RuntimeError(f"no script catalog at {path}: run ScriptsAndGuides/guides/tools/build_bundle.py")
    stat = os.stat(path)
    revision = (stat.st_mtime_ns, stat.st_size)
    if _catalog is None or revision != _catalog_revision:
        with open(path, encoding="utf-8") as file:
            updated = json.load(file)
        _catalog = updated
        _catalog_revision = revision
        _venue_kind_cache.clear()
    return _catalog
'''+s[end:]
    start=s.index('def step_guides(');end=s.index('\n\n',s.index('    return {"stepID":',start))
    s=s[:start]+'''def guide_with_links(gid, base_url, token, duration=None):
    guide = catalog()["guides"][gid]
    seconds = guide["seconds"]
    scenario_url = file_url(base_url, token, guide["scenario"])
    if duration:
        with open(os.path.join(CATALOG_DIR, guide["scenario"]), encoding="utf-8") as file:
            _, seconds = stretched(json.load(file), duration)
        scenario_url += f"&duration={duration}"
    result = {
        "id": gid,
        "overlayURL": file_url(base_url, token, guide["overlay"]),
        "scenarioURL": scenario_url,
        "model3DURL": file_url(base_url, token, guide["model3D"]),
        "seconds": seconds,
        "camera": guide["camera"],
        "moves": guide["moves"],
        "subject": guide["subject"],
        "style": guide.get("style", "schematic"),
    }
    for key in ("sha256", "animationSeconds", "alphaFactor", "rendering"):
        if guide.get(key) is not None:
            result[key] = guide[key]
    for key in ("poster", "strip"):
        if guide.get(key):
            result[key + "URL"] = file_url(base_url, token, guide[key])
    return result


def all_guides(page, page_size, base_url, token):
    ids = sorted(catalog()["guides"])
    chosen, next_page = paged(ids, page, page_size)
    return {"guides": [guide_with_links(gid, base_url, token) for gid in chosen],
            "total": len(ids), "nextPage": next_page}


def step_guides(step_id, venue_id, duration, base_url, token):
    template, step = find_step(step_id)
    if step is None:
        raise RuntimeError(f"unknown step {step_id}")
    guides = catalog()["guides"]
    out = [guide_with_links(gid, base_url, token, duration)
           for gid in step.get("overlays", []) if gid in guides]
    kind = venue_kind(venue_id) if venue_id else None
    return {"stepID": step_id, "templateID": template["id"], "venueKind": kind, "seconds": duration or step["seconds"], "guides": out}
'''+s[end:]
    needle='        if url.path == "/v1/venue-kinds":'
    insert='''        if url.path == "/v1/guides":
            return self.run(lambda: all_guides(page, page_size, base_url, self.token))
        guide_parts = url.path.strip("/").split("/")
        if len(guide_parts) == 3 and guide_parts[:2] == ["v1", "guides"]:
            if guide_parts[2] not in catalog()["guides"]:
                return self.reply(404, {"error": "unknown guide"})
            duration = query.get("duration", [None])[0]
            return self.run(lambda: guide_with_links(guide_parts[2], base_url, self.token,
                                                     float(duration) if duration else None))
'''
    assert s.count(needle)==1;s=s.replace(needle,insert+needle)
    needle='''        else:
            body = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(os.path.splitext(path)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
'''
    replacement='''        else:
            body = None
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(os.path.splitext(path)[1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(body) if body is not None else os.path.getsize(path)))
        self.end_headers()
        try:
            if body is not None:
                self.wfile.write(body)
            else:
                with open(path, "rb") as file:
                    shutil.copyfileobj(file, self.wfile, length=64 * 1024)
        except (BrokenPipeError, ConnectionResetError):
            pass
'''
    assert s.count(needle)==1;s=s.replace(needle,replacement)
    s=s.replace('GET  /v1/steps/{templateID.stepID}/guides?', 'GET  /v1/guides?page=0&pageSize=20  all unique guides with animation, poster and strip links\nGET  /v1/guides/{id}?duration=  a guide by id\nGET  /v1/steps/{templateID.stepID}/guides?',1)
    compile(s,relative,'exec');stage(relative,s)
    shutil.copy2(KIT/'tools/scriptwriter/response_schema.json',HERE/'patches/tools/scriptwriter/response_schema.json')
    relative='Sources/VideoScripts/ScriptCatalogGateway.swift';s=(KIT/relative).read_text()
    assert s.count('key: key + ".png")')==1 and s.count('key: key + ".json")')==1
    s=s.replace('key: key + ".png")','key: key + "-" + guide.overlayURL.path)',1)
    s=s.replace('key: key + ".json")','key: key + "-" + url.path)',1)
    stage(relative,s)
    stage('Tests/VideoScriptsTests/GuideAssetRevisionTests.swift','''import Foundation
import Testing
import VideoEditorCatalog
@testable import VideoScripts

private actor RevisionGuides: ShotGuideGateway {
    var revision = 1

    func update() { revision += 1 }

    func guides(for step: ScriptStep, templateID: String, venueID: String?, seconds: Double?) async throws -> [ShotGuide] {
        [ShotGuide(id: "same-guide",
                   overlayURL: URL(string: "https://example.com/v1/files/overlays/revision-\\(revision)/same-guide.png")!,
                   scenarioURL: URL(string: "https://example.com/v1/files/scenarios/revision-\\(revision)/same-guide.json")!)]
    }
}

private actor RevisionTransport: DataGateway {
    private(set) var count = 0

    func data(from url: URL) async throws -> Data {
        count += 1
        return Data(url.path.utf8)
    }
}

struct GuideAssetRevisionTests {
    @Test func changedAssetPathsRefreshWithoutChangingGuideIdentity() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: directory) }
        let catalog = try BundledScriptCatalogGateway()
        let template = try await catalog.templates(venueKind: "coffee", page: 0, pageSize: 1).templates[0]
        let step = try #require(template.steps.first)
        let guides = RevisionGuides()
        let transport = RevisionTransport()
        let files = RemoteFileCache(directory: directory, gateway: transport)
        let repository = ScriptTemplateRepository(gateway: catalog, files: files, guides: guides)

        let first = try #require(await repository.localGuides(for: step, in: template, venueID: nil, seconds: nil).first)
        await guides.update()
        let second = try #require(await repository.localGuides(for: step, in: template, venueID: nil, seconds: nil).first)
        let repeated = try #require(await repository.localGuides(for: step, in: template, venueID: nil, seconds: nil).first)

        #expect(first.id == second.id)
        #expect(first.overlayURL != second.overlayURL)
        #expect(first.scenarioURL != second.scenarioURL)
        #expect(try Data(contentsOf: second.overlayURL) == Data("/v1/files/overlays/revision-2/same-guide.png".utf8))
        #expect(try Data(contentsOf: #require(second.scenarioURL)) == Data("/v1/files/scenarios/revision-2/same-guide.json".utf8))
        #expect(repeated == second)
        #expect(await transport.count == 4)
    }
}
''')
    relative='tools/scriptwriter/README.md';s=(KIT/relative).read_text()
    s+='''
## Complete animation library

`GET /v1/guides?page=0&pageSize=20` pages all 178 unique guides: `{ "guides": [...], "total": 178,
"nextPage": 1 }`. `GET /v1/guides/{id}?duration=` returns one guide. Both use the existing bearer token.
The existing per-step endpoint continues to return the same guide objects.

Each guide includes `id`, `overlayURL` (transparent APNG, without baked viewfinder UI), `scenarioURL`,
`model3DURL`, `posterURL`, `stripURL`, `seconds`, `camera`, `moves`, `subject`, `style` and `sha256`.
Reviewed watercolor guides also include `alphaFactor: 0.5`, `animationSeconds` and the rendering method.
`seconds` describes the live scenario; `animationSeconds` describes the demonstration APNG loop.

The bundle builder defaults to reviewed watercolor artwork where available (currently 96 guides),
falling back to original schematics for the other 82. `--overlays schematic` builds the original set.
It preserves the source previews and sensor scenarios. The global 50% alpha is already in watercolor
APNGs; clients must not apply it again.

Changed overlays and scenarios have content-versioned URLs; flat legacy file links remain valid.
The iOS repository includes asset paths in cache keys, so a rebuilt app refreshes changed guide assets.
The server reloads a catalog when its atomic catalog.json index changes; future bundle rebuilds need
no server restart. Asset files are installed before the index is replaced.
'''
    stage(relative,s)
    (HERE/'publication-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('Prepared',len(plan),'targeted edits; original files unchanged.')


if __name__=='__main__':main()
