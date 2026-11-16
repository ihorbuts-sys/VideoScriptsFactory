"""Verify every published coffee binding, media file and context-specific scenario."""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(server):
    token=(server/'.token').read_text().strip()
    base='http://127.0.0.1:8765'
    catalog=json.loads((server/'catalog/catalog.json').read_text())
    manifest=json.loads((BASE/'catalog/clay-scenes/active-revisions.json').read_text())
    def get(path):
        request=urllib.request.Request(base+path,headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(request,timeout=30) as response:
            assert response.status==200
            return json.load(response)
    files={};bindings=[]
    def fetch(url,expected):
        key=urllib.parse.urlparse(url).path
        if key not in files:
            sha=hashlib.sha256();length=0
            with urllib.request.urlopen(url,timeout=60) as response:
                assert response.status==200
                while block:=response.read(1024*1024):sha.update(block);length+=len(block)
            files[key]=dict(sha256=sha.hexdigest(),bytes=length)
        assert files[key]['sha256']==expected,key
    records=list(manifest['guides'].items())+[(row['guide_id'],row) for row in manifest.get('guide_variants',{}).values()]
    for gid,row in records:
        if row.get('opacity_mode')!='image_view':continue
        folder=BASE/row['folder']
        for context in row['contexts']:
            tid,sid=context['template'],context['step'];key=tid+'.'+sid
            response=get('/v1/steps/'+key+'/guides')
            guide=next(g for g in response['guides'] if g['id']==gid)
            assert guide['alphaFactor']==1 and guide['imageViewOpacity']==.65
            assert guide['opacityAppliedIn']=='image_view'
            assert guide.get('nextGuideID')==context['next_guide']
            assert abs(guide['seconds']-context['capture_seconds'])<.01,(key,guide['seconds'])
            for field,name in [('overlayURL','view-overlay.png'),('posterURL','view-overlay-poster.png'),
                               ('stripURL','view-overlay-strip.jpg'),('colorVideoURL','color.mp4')]:
                fetch(guide[field],row['files'][name])
            with urllib.request.urlopen(guide['scenarioURL'],timeout=20) as response:scenario=json.load(response)
            total=sum(1.2 if s['kind']=='frame' else s.get('duration',1) for s in scenario['steps'])
            assert abs(total-context['capture_seconds'])<.01,(key,total)
            action=next((s['action'] for s in scenario['steps'] if s['kind']=='follow'),'still')
            assert action in guide['moves']
            if gid in ['talking_head_eye_level','selfie_one_high_hold']:
                assert scenario['camera']=='front' and scenario['anchor']['kind']=='face'
                assert action=='still' and scenario['steps'][0]['icon']['symbol']=='find_face'
            if gid=='cup_eye_hold_whipout':assert action=='dolly_out'
            if gid=='interior_pan':assert scenario['steps'][1]['direction']=='left'
            template=next(t for t in catalog['templates'] if t['id']==tid)
            step=next(s for s in template['steps'] if s['id']==sid)
            if context.get('update_capture_seconds'):assert abs(step['seconds']-context['capture_seconds'])<.01
            bindings.append(dict(guide=gid,template=tid,template_title=template['title'],step=sid,
                step_title=step['title'],capture_seconds=context['capture_seconds'],animation_seconds=guide['animationSeconds'],
                action=action,scenario_seconds=total))
    expected={gid for gid,row in records if row.get('opacity_mode')=='image_view'}
    assert {r['guide'] for r in bindings}==expected
    assert len(bindings)==sum(len(row['contexts']) for gid,row in records if row.get('opacity_mode')=='image_view')
    assert get('/v1/guides?pageSize=1')['total']==len(catalog['guides'])==178
    before_path=BASE/'catalog/clay-scenes/publication/catalog-before-57d6da51c9335704.json'
    before=json.loads(before_path.read_text())
    assert catalog['previewArt']==before['previewArt']
    new_sequences={tid:row for tid,row in manifest.get('sequences',{}).items() if row.get('opacity_mode')=='image_view'}
    for tid,sequence in before['scriptGuideSequences'].items():
        if tid not in new_sequences:assert catalog['scriptGuideSequences'][tid]==sequence
    for tid,row in new_sequences.items():
        sequence=get('/v1/scripts/'+tid+'/guide-sequence')
        assert sequence['alphaFactor']==1 and sequence['imageViewOpacity']==.65
        assert sequence['fullScriptSequenceComplete'] and not sequence['viewfinderEmbedded']
        folder=BASE/row['folder']
        for field,name in [('overlayURL','ghost.png'),('videoURL','preview.mp4'),('posterURL','poster.png'),('stripURL','strip.jpg')]:
            fetch(sequence[field],row['files'][name])
        assert [s['step_id'] for s in sequence['steps']]==[s['id'] for t in catalog['templates'] if t['id']==tid for s in t['steps']]
    changed={g for g in catalog['guides'] if catalog['guides'][g]!=before['guides'][g]}
    allowed={r['guide'] for r in bindings}
    assert changed<=allowed,changed-allowed
    for scoped in [gid for gid in expected if not any(r.get('update_global',True) for g,r in records if g==gid)]:
        assert catalog['guides'][scoped]==before['guides'][scoped]
    for key,overrides in before['stepGuideOverrides'].items():
        if key not in {r['template']+'.'+r['step'] for r in bindings}:
            assert catalog['stepGuideOverrides'][key]==overrides,key
    for folder in (BASE/'catalog/glass-rollout/coffee').iterdir():
        if not folder.is_dir() or not (folder/'publication.json').exists():continue
        collection=get('/v1/guide-collections/coffee-guide-'+folder.name)
        assert collection['alphaFactor']==1 and collection['imageViewOpacity']==.65
        assert collection['backgroundDelaySeconds']==2 and not collection['viewfinderEmbedded']
        assert not collection['wallsEmbedded'] and not collection['floorEmbedded']
        fetch(collection['overlayURL'],digest(folder/'view-overlay.png'))
    report=dict(status='passed',unique_glass_guides=len(expected),template_bindings=len(bindings),total_guides=178,
        other_guides_remaining=178-len(expected),bindings=bindings,downloaded_assets=len(files),files=files,
        preview_art_preserved=True,unrelated_context_overrides_preserved=True,
        unrelated_full_script_sequences_preserved=True,complete_glass_sequences=list(new_sequences),public_guide_api_verified=True)
    out=BASE/'catalog/glass-rollout/live-api-check.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['files','bindings']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--server',type=Path,required=True);args=parser.parse_args();run(args.server)
