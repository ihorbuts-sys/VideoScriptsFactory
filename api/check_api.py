"""Exercise the real HTTP handlers against the prepared bundle, or a live server."""
import argparse
import concurrent.futures
import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile
import threading
import urllib.error
import urllib.request
from collections import Counter
from http.server import ThreadingHTTPServer
from pathlib import Path

import opacity_assets
from PIL import Image

HERE=Path(__file__).resolve().parent
SERVER=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/server.py')
FPS=15


def check(base,token,bundle,registry):
    def request(path,authorized=True):
        url=path if path.startswith('http') else base+path
        headers={'Authorization':'Bearer '+token} if authorized else {}
        return urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30)
    def get(path):
        with request(path) as response:return json.load(response)
    def status(path,expected):
        try:
            with request(path,False) as response:actual=response.status
        except urllib.error.HTTPError as error:actual=error.code
        assert actual==expected,(path,actual)
    status('/v1/guides',401);status('/v1/guides/bar_low_truckr_mm',401)
    status('/v1/files/overlays/bar_low_truckr_mm.png',401)
    guides=[];page=0
    while page is not None:
        response=get(f'/v1/guides?page={page}&pageSize=17')
        assert response['total']==len(bundle['guides'])
        guides.extend(response['guides']);page=response['nextPage']
    assert len(guides)==len({g['id'] for g in guides})==178
    assert {g['id'] for g in guides}==set(bundle['guides'])
    styles=dict(Counter(g['style'] for g in guides))
    assert styles==dict(Counter(g['style'] for g in bundle['guides'].values()))
    for guide in guides:
        assert guide['overlayURL'].endswith('.png?token='+token)
        assert guide['scenarioURL'] and guide['posterURL'] and guide['stripURL']
    def asset_check(guide):
        with request(guide['overlayURL']) as response:
            assert response.headers['Content-Type']=='image/png'
            data=response.read()
        assert hashlib.sha256(data).hexdigest()==guide['sha256']==bundle['guides'][guide['id']]['sha256']
        with Image.open(io.BytesIO(data)) as image:
            # Image-view records carry full alpha; the app applies the opacity.
            view=guide.get('opacityAppliedIn')=='image_view'
            expected=(540,960) if guide['style']=='blender' and not view else (405,720)
            assert image.size==expected and image.is_animated,guide['id']
            assert guide['alphaFactor']==(1 if view else opacity_assets.TARGET)
            maximum=0
            for i in range(image.n_frames):image.seek(i);maximum=max(maximum,image.convert('RGBA').getchannel('A').getextrema()[1])
            assert view or maximum==opacity_assets.MAX_ALPHA,guide['id']
            if guide['style']=='blender':
                seconds=sum(image.seek(i) or image.info['duration'] for i in range(image.n_frames))/1000
                assert abs(seconds-guide['animationSeconds'])<.01
        for field in ('scenarioURL','model3DURL','posterURL','stripURL'):
            with request(guide[field]) as response:
                data=response.read();assert data
                if field.endswith('3DURL') or field=='scenarioURL':json.loads(data)
        return guide['id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        assets=list(pool.map(asset_check,guides))
    def step_check(pair):
        template,step=pair;response=get(f'/v1/steps/{template["id"]}.{step["id"]}/guides')
        assert [g['id'] for g in response['guides']]==step['guides'],(template['id'],step['id'])
        assert all(g['shotType']==step['shotType'] for g in response['guides'])
        return response['stepID']
    pairs=[(t,s) for t in bundle['templates'] for s in t['steps']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        steps=list(pool.map(step_check,pairs))
    gid='bar_low_truckr_mm';single=get('/v1/guides/'+gid)
    assert single==next(g for g in guides if g['id']==gid)
    stretched=get('/v1/guides/'+gid+'?duration=20');assert abs(stretched['seconds']-20)<.01
    assert stretched['overlayURL']==single['overlayURL']
    with request(stretched['scenarioURL']) as response:assert json.load(response)['steps']
    try:get('/v1/guides/not-a-real-guide')
    except urllib.error.HTTPError as error:assert error.code==404
    else:raise AssertionError('Unknown guide was accepted')
    with request('/v1/files/overlays/'+gid+'.png?token='+token) as response:
        assert hashlib.sha256(response.read()).hexdigest()==single['sha256']
    report=dict(guides=len(assets),styles=styles,step_endpoints=len(steps),asset_downloads=len(assets)*5,
                authentication_checked=True,unknown_guide_404=True,duration_stretch_checked=True,
                legacy_file_link_checked=True,overlay_hashes_match=True)
    report.update(check_p0(get,request,status,bundle,registry))
    return report


def check_p0(get,request,status,bundle,registry):
    status('/v1/shot-types',401)
    types=get('/v1/shot-types')['shotTypes']
    assert types==registry['shotTypes'] and len(types)==12
    deferred=set(registry.get('deferredGuides',{}))
    if deferred:
        assert deferred=={'bite_selfie_eye','sip_selfie_eye','sip_high_lean','verdict_eye_level','verdict_high_plate'}
        assert not deferred.intersection(registry['guides'])
    for kind in types:
        guides=get(f'/v1/shot-types/{kind["id"]}/guides')['guides']
        assert [g['id'] for g in guides]==kind['guides'] and len(guides)==len({g['id'] for g in guides}),kind['id']
        if not guides:assert kind.get('availability')=='deferred' and kind['deferredGuideIDs']
        for guide in guides:
            assert guide['shotType']==kind['id']
            assert guide['invariant'] and guide['startTrigger'] in ('still','motion','countdown') and guide['capturePreset']
            assert 3<=guide['durationSec']<=8
            if guide.get('content')=='canonical-character':
                assert guide['camera'] in ['front','back']
                assert guide['previewMirrored']==(guide['camera']=='front')
                assert guide['filmingMode']=='selfie' if guide['camera']=='front' else guide['filmingMode'] in ('friend','propped')
                assert guide['facialAnimation'] is False
            assert all(guide[key].endswith('.png?token='+guide[key].split('token=')[1]) for key in ('animation','selector','poster'))
    try:get('/v1/shot-types/not-a-type/guides')
    except urllib.error.HTTPError as error:assert error.code==404
    else:raise AssertionError('Unknown shot type was accepted')
    def step(key):return get(f'/v1/steps/{key}/guides')
    drink=step('first-visit.drink')
    # Guided v0 (owner 2026-11-10): the drink step films the cup on the table (complex steam guides, 2 to 3).
    assert 2<=len(drink['guides'])<=3 and drink['shotType']=='steam'
    stretched=get('/v1/steps/first-visit.drink/guides?duration=20')
    # Step length rule (owner 2026-11-10): the step keeps its catalog seconds (first guide's loop or the line's time).
    canonical=next(s for t in bundle['templates'] if t['id']=='first-visit' for s in t['steps'] if s['id']=='drink')
    assert stretched['seconds']==drink['seconds']==canonical['seconds']>=drink['guides'][0]['durationSec'] and stretched['guides']==drink['guides']
    assert step('salon-fade.blend')['guides']==[]
    coffee=next(t for t in get('/v1/scripts?venueKind=coffee&pageSize=100')['templates'] if t['id']=='first-visit')
    assert coffee['steps'][0]['id']=='entrance' and [s['captureOrder'] for s in coffee['steps']]==[1,2,3,4,5]
    cup=next(s for s in coffee['steps'] if s['id']=='drink')
    assert cup['required'] and 2<=len(cup['guides'])<=3 and cup['editOrder']==1
    dining=next(t for t in get('/v1/scripts?venueKind=dining&pageSize=100')['templates'] if t['id']=='first-visit')
    assert [s['id'] for s in dining['steps']]==['entrance','menu','plate','forkful','room','verdict']
    # One-dish steps never offer a shared-spread guide, and no P0 step offers an upside-down guide (owner 2026-11-10).
    table_ids={'table_spread_orbit','glass_slide_close','pancake_clear_path'}
    for key in ['food-review.dish','first-visit.plate']:
        response=step(key)
        assert response['shotType']=='plate-reveal' and not table_ids.intersection(g['id'] for g in response['guides']),key
    for template in [coffee,dining]:
        for s in template['steps']:assert 'pour_upside_down' not in [g if isinstance(g,str) else g.get('id') for g in s.get('guides',[])],s['id']
    for response,kind in ((coffee,'coffee'),(dining,'dining')):
        for image_step in response['steps']:
            canonical=next(s for t in bundle['templates'] if t['id']=='first-visit' for s in t['steps'] if s['id']==image_step['id'])
            expected=canonical.get('previewByVenueKind',{}).get(kind,canonical['imageURL'])
            assert '/v1/files/'+expected+'?' in image_step['imageURL']
            assert image_step['examplePreview']==image_step['imageURL']
    assert coffee['steps'][0]['imageURL']!=dining['steps'][0]['imageURL']
    library=[];page=0
    while page is not None:
        response=get(f'/v1/steps?page={page}&pageSize=50')
        library+=[s for g in response['groups'] for s in g['steps']];page=response['nextPage']
    assert library and all(s['access']!='staff' for s in library)
    staff=sum(s['access']=='staff' for t in bundle['templates'] for s in t['steps'])
    def files(guide):
        if guide['sha256'] is None:return None
        frames={}
        for key,size in (('animation',(405,720)),('selector',(120,213)),('poster',(405,720))):
            with request(guide[key]) as response:data=response.read()
            with Image.open(io.BytesIO(data)) as image:
                assert image.format=='PNG' and image.size==size,(guide['id'],key,image.size)
                assert image.mode=='RGBA' or 'transparency' in image.info,(guide['id'],key)
                if key!='poster':
                    seconds=sum(image.seek(i) or image.info['duration'] for i in range(image.n_frames))/1000
                    expected=.5+guide['setupBeatSeconds']+guide['durationSec']+.5
                    assert abs(seconds-expected)<=1/FPS,(guide['id'],key,seconds,expected)
                image.seek(0);frames[key]=image.convert('RGBA').tobytes()
        assert frames['animation']==frames['poster'],guide['id']
        return guide['id']
    records=[g for kind in types for g in get(f'/v1/shot-types/{kind["id"]}/guides')['guides']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rendered=[gid for gid in pool.map(files,records) if gid]
    pending=sorted(g['id'] for g in records if g['sha256'] is None)
    assert sorted(registry['pendingRenders'])==pending
    examples=[g for g in records if g.get('examplePreview')]
    # handoff_counter_cup (archived 2026-11-10) kept its example picture; its replacement has none yet.
    assert {g['id'] for g in examples}=={'handoff_plate_lands'}
    for guide in examples:
        with request(guide['examplePreview']) as response:
            with Image.open(io.BytesIO(response.read())) as image:assert image.size==(1080,1920)
    return dict(shot_types=len(types),p0_guides=len(records),p0_files_checked=len(rendered),p0_pending_renders=pending,
                drink_guides=[g['id'] for g in drink['guides']],empty_step_checked=True,duration_ignored_checked=True,
                library_steps=len(library),staff_steps_hidden=staff,venue_preview_variants_checked=True,handoff_examples_checked=len(examples),
                deferred_person_guides=sorted(deferred),one_dish_steps_without_spread_guides=True,no_p0_upside_down_guides=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url');parser.add_argument('--token-file')
    parser.add_argument('--bundle',default=str(HERE/'bundle'),help='the bundle the server serves')
    parser.add_argument('--server',default=str(SERVER),help='server.py to stage when no --base-url is given')
    parser.add_argument('--report',default=str(HERE/'staged-api-check.json'));args=parser.parse_args()
    folder_in=Path(args.bundle).resolve()
    bundle=json.loads((folder_in/'catalog.json').read_text());registry=json.loads((folder_in/'shot_types.json').read_text())
    if args.base_url:
        report=check(args.base_url,Path(args.token_file).read_text().strip(),bundle,registry)
        report['base_url']=args.base_url
    else:
        spec=importlib.util.spec_from_file_location('prepared_scriptwriter',args.server)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix='loca-guide-api-') as temp:
            folder=Path(temp);index=folder/'catalog.json';index.write_text(json.dumps(bundle))
            (folder/'shot_types.json').write_text(json.dumps(registry))
            for name in ('overlays','previews','scenarios','3d'):(folder/name).symlink_to(folder_in/name,target_is_directory=True)
            module.CATALOG_DIR=str(folder);module.Handler.token='guide-api-check'
            server=ThreadingHTTPServer(('127.0.0.1',0),module.Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            with contextlib.redirect_stdout(io.StringIO()):
                thread.start()
                try:
                    base=f'http://127.0.0.1:{server.server_port}';report=check(base,module.Handler.token,bundle,registry)
                    written=module.with_shot_types({'venueKind':'coffee','steps':[{'id':'cup','title':'The pour','shot':'detail',
                        'direction':'Hold the phone above the cup while the barista pours.'},{'id':'end','title':'Bye','shot':'selfie'}]},
                        [{'id':'cup','seconds':9,'direction':'Phone above the cup while the milk is poured.'},{'id':'end','seconds':7}])
                    pour=next(t for t in registry['shotTypes'] if t['id']=='pour')['guides']
                    assert written[0]['shotType']=='pour' and [g['id'] if isinstance(g,dict) else g for g in written[0]['guides']]==pour and written[0]['seconds']==5
                    assert written[1]['shotType']=='verdict'
                    assert written[1]['seconds']==(7 if registry.get('deferredGuides') else 6)
                    assert bool(written[1]['guides'])==(not bool(registry.get('deferredGuides')));report['written_steps_checked']=True
                    updated=dict(bundle);updated['revisionCheck']='updated';temporary=folder/'catalog.tmp'
                    temporary.write_text(json.dumps(updated));temporary.replace(index)
                    assert module.catalog()['revisionCheck']=='updated';report['atomic_catalog_reload_checked']=True
                finally:server.shutdown();server.server_close();thread.join()
    Path(args.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
