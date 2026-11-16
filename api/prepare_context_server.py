"""Prepare a minimal context-aware guide API patch without editing the running server."""
from pathlib import Path
import hashlib
import json
BASE=Path(__file__).resolve().parent
source=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/server.py')
text=source.read_text();original=hashlib.sha256(source.read_bytes()).hexdigest()
assert 'def script_guide_sequence(' not in text
text=text.replace('def guide_with_links(gid, base_url, token, duration=None):\n    guide = catalog()["guides"][gid]', 'def guide_with_links(gid, base_url, token, duration=None, override=None):\n    guide = dict(catalog()["guides"][gid])\n    if override:\n        guide.update(override)')
text=text.replace('for key in ("sha256", "animationSeconds", "alphaFactor", "rendering"):', 'for key in ("sha256", "animationSeconds", "alphaFactor", "rendering", "scope", "handoverStatus", "contextTemplateID", "contextStepID", "nextGuideID"):')
text=text.replace('    out = [guide_with_links(gid, base_url, token, duration)\n           for gid in step.get("overlays", []) if gid in guides]', '    overrides = catalog().get("stepGuideOverrides", {}).get(step_id, {})\n    out = [guide_with_links(gid, base_url, token, duration, overrides.get(gid))\n           for gid in step.get("overlays", []) if gid in guides]')
text=text.replace('def with_links(step, base_url, token):','def with_links(step, base_url, token, template_id=None):')
text=text.replace('    out["overlays"] = [file_url(base_url, token, guides[g]["overlay"]) for g in step.get("overlays", []) if g in guides]', '    owner = template_id or step.get("templateID")\n    key = owner + "." + step["id"] if owner else ""\n    overrides = catalog().get("stepGuideOverrides", {}).get(key, {})\n    out["overlays"] = [file_url(base_url, token, overrides.get(g, {}).get("overlay", guides[g]["overlay"])) for g in step.get("overlays", []) if g in guides]')
text=text.replace('with_links(step, base_url, token) for step in template["steps"]','with_links(step, base_url, token, template["id"]) for step in template["steps"]')
addition='''

def script_guide_sequence(template_id, base_url, token):
    sequence = catalog().get("scriptGuideSequences", {}).get(template_id)
    if sequence is None:
        status = catalog().get("scriptGuideSequenceStatus", {}).get(template_id)
        if status:
            return {"id": template_id, "scope": "deferred_people", **status}
        return None
    result = {key: sequence[key] for key in ("id", "title", "seconds", "sha256", "steps")}
    for key in ("overlay", "video", "poster", "strip"):
        if sequence.get(key):
            result[key + "URL"] = file_url(base_url, token, sequence[key])
    result["scope"] = "full_script_instruction_sequence"
    return result
'''
text=text.replace('\n\n\nCONTENT_TYPES =',addition+'\n\nCONTENT_TYPES =')
text=text.replace('kind not in ("previews", "overlays", "scenarios", "3d")','kind not in ("previews", "overlays", "scenarios", "3d", "sequences")')
text=text.replace('".usdz": "model/vnd.usdz+zip"}', '".usdz": "model/vnd.usdz+zip", ".mp4": "video/mp4"}')
needle='        if url.path == "/v1/venue-kinds":'
route='''        if len(guide_parts) == 4 and guide_parts[:2] == ["v1", "scripts"] and guide_parts[3] == "guide-sequence":
            sequence = script_guide_sequence(guide_parts[2], base_url, self.token)
            if sequence is None:
                return self.reply(404, {"error": "unknown script sequence"})
            return self.reply(200, sequence)
'''
assert needle in text;text=text.replace(needle,route+needle)
assert 'overrides.get(gid)' in text and 'override=None' in text and 'video/mp4' in text
(BASE/'context-server.py').write_text(text)
(BASE/'context-server-preparation.json').write_text(json.dumps(dict(source=str(source),source_sha256=original,prepared_sha256=hashlib.sha256(text.encode()).hexdigest(),changes=['Per-step guide assets use their actual script handover','Full-script guide sequence endpoint','Expose scope/context and handover metadata','MP4 content type']),indent=2)+'\n')
print('Prepared context-aware API patch; live server unchanged')
