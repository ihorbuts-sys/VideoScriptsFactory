"""Verify every contextual object preview through the running development API."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import opacity_assets
from PIL import Image
import hashlib
import io
import json
import urllib.request
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
bundle=json.loads((HERE/'bundle/catalog.json').read_text());manifest=json.loads((BASE/'catalog/context-animations/index.json').read_text());token=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/.token').read_text().strip();url='http://127.0.0.1:8765'
blocked=set(json.loads((BASE/'guides/blender_motion/people-policy.json').read_text())['deferred_guides'])
def get(path):
    request=urllib.request.Request(path if path.startswith('http') else url+path,headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(request,timeout=40) as response:return response.read()
def one(pair):
    key,expected=pair;data=json.loads(get('/v1/steps/'+key+'/guides'))['guides'];assert len(data)==1
    guide=data[0];gid=expected['guide_id'];assert guide['id']==gid
    if expected.get('status')=='deferred_people':
        assert gid in blocked and guide['style']!='blender';return 'deferred'
    assert guide['contextTemplateID']==expected['template_id'] and guide['contextStepID']==expected['step_id']
    assert guide['handoverStatus']==expected['handover_status'] and guide['scope']==expected['scope']
    published=bundle['stepGuideOverrides'][key][gid]
    assert published['sourceSha256']==expected['sha256']
    body=get(guide['overlayURL']);assert hashlib.sha256(body).hexdigest()==published['sha256']==guide['sha256']
    with Image.open(io.BytesIO(body)) as image:
        assert image.size==(540,960) and image.is_animated
        duration=0;maximum=0
        for index in range(image.n_frames):
            image.seek(index);duration+=image.info['duration'];maximum=max(maximum,image.convert('RGBA').getchannel('A').getextrema()[1])
        assert abs(duration/1000-guide['animationSeconds'])<.001 and maximum==opacity_assets.MAX_ALPHA
    checks=json.loads((BASE/expected['folder']/'assembly-checks.json').read_text())
    for stage in checks['stages']:assert stage['source']['guide_id'] not in blocked
    if expected['handover_status']=='included':assert expected['next_guide'] not in blocked
    for field in ['posterURL','stripURL']:
        with Image.open(io.BytesIO(get(guide[field]))) as image:image.verify()
    return 'object'
with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,manifest['steps'].items()))
for gid in blocked:
    guide=json.loads(get('/v1/guides/'+gid));assert guide['style']!='blender'
for template_id,row in manifest['scripts'].items():
    record=json.loads(get('/v1/scripts/'+template_id+'/guide-sequence'))
    if row.get('status')=='deferred_people':
        assert record['scope']=='deferred_people' and record['deferredSteps']==row['deferred_steps'] and 'overlayURL' not in record
    else:
        published=bundle['scriptGuideSequences'][template_id]
        assert record['scope']=='full_script_instruction_sequence' and record['sha256']==published['sha256']
        assert hashlib.sha256(get(record['overlayURL'])).hexdigest()==published['sha256']
        request=urllib.request.Request(record['videoURL'],headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(request,timeout=30) as response:assert response.headers['Content-Type']=='video/mp4' and response.read(256)
# Script-library links agree with the dedicated per-step endpoint.
scripts=json.loads(get('/v1/scripts?page=0&pageSize=100'))['templates']
for template in scripts:
    for step in template['steps']:
        key=template['id']+'.'+step['id']
        if key in bundle['stepGuideOverrides']:
            gid=manifest['steps'][key]['guide_id'];assert '/v1/files/'+bundle['stepGuideOverrides'][key][gid]['overlay']+'?' in step['overlays'][0]
report=dict(step_endpoints=len(results),object_previews=results.count('object'),deferred_people_steps=results.count('deferred'),object_handovers=sum(r.get('handover_status')=='included' for r in manifest['steps'].values()),deferred_people_guides=len(blocked),deferred_full_script_sequences=sum(r.get('status')=='deferred_people' for r in manifest['scripts'].values()),complete_full_script_sequences=sum(bool(r.get('folder')) for r in manifest['scripts'].values()),context_hashes_match=True,poster_and_strip_downloads_checked=True,animation_durations_checked=True,alpha_not_doubled=True,max_alpha=opacity_assets.MAX_ALPHA,whole_overlay_opacity=opacity_assets.TARGET,new_people_in_context_sources=0,script_library_links_match_contexts=True)
(HERE/'context-live-api-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
