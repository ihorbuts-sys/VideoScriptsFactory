"""Exercise the prepared context-aware handlers without changing the live server."""
from pathlib import Path
import copy
import types
import hashlib
import importlib.util
import json
import shutil
import tempfile
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
HERE=Path(__file__).resolve().parent
module=types.ModuleType('context_server_check');module.__file__='/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/server.py'
exec(compile((HERE/'context-server.py').read_text(),str(HERE/'context-server.py'),'exec'),module.__dict__)
fixture=copy.deepcopy(json.loads((HERE/'bundle/catalog.json').read_text()))
template,step=next((t,s) for t in fixture['templates'] for s in t['steps'] if s['overlays']==['cup_eye_orbitr_cc'])
key=template['id']+'.'+step['id'];chosen=fixture['guides']['cup_high_out_dm']
fixture['stepGuideOverrides']={key:{'cup_eye_orbitr_cc':dict(overlay=chosen['overlay'],poster=chosen['poster'],strip=chosen['strip'],sha256=chosen['sha256'],scope='shot_and_handover',handoverStatus='included',contextTemplateID=template['id'],contextStepID=step['id'],nextGuideID='selfie_sip_eye_in_mc')}}
fixture['scriptGuideSequenceStatus']={'pending-check':dict(status='deferred_people',title='Pending script',deferredSteps=['person'],objectSteps=['cup'])}
fixture['scriptGuideSequences']={template['id']:dict(id=template['id'],title=template['title'],seconds=7.4,sha256=chosen['sha256'],steps=[dict(stepID=step['id'],guideID='cup_eye_orbitr_cc')],overlay=chosen['overlay'],video='sequences/check.mp4',poster=chosen['poster'],strip=chosen['strip'])}
with tempfile.TemporaryDirectory(prefix='loca-guide-context-check-') as directory:
    catalog=Path(directory)
    for name in ['overlays','previews','scenarios','3d']:(catalog/name).symlink_to(HERE/'bundle'/name,target_is_directory=True)
    (catalog/'sequences').mkdir();shutil.copy2(HERE.parent/'catalog/blender-animations/cup_eye_orbitr_cc/preview.mp4',catalog/'sequences/check.mp4')
    (catalog/'catalog.json').write_text(json.dumps(fixture));module.CATALOG_DIR=str(catalog);module.catalog=lambda:fixture
    module.Handler.token='isolated-context-check';module.Handler.log_message=lambda *args:None
    server=ThreadingHTTPServer(('127.0.0.1',0),module.Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    def fetch(path,authorized=True):
        url=path if path.startswith('http') else base+path
        request=urllib.request.Request(url,headers={'Authorization':'Bearer '+module.Handler.token} if authorized else {})
        return urllib.request.urlopen(request,timeout=20)
    try:
        with fetch('/v1/steps/'+key+'/guides') as response:record=json.load(response)['guides'][0]
        assert record['id']=='cup_eye_orbitr_cc' and record['sha256']==chosen['sha256']
        assert record['contextTemplateID']==template['id'] and record['nextGuideID']=='selfie_sip_eye_in_mc'
        linked=module.template_with_links(template,base,module.Handler.token)
        assert next(s for s in linked['steps'] if s['id']==step['id'])['overlays'][0]==record['overlayURL']
        with fetch('/v1/scripts/pending-check/guide-sequence') as response:
            pending=json.load(response);assert pending['scope']=='deferred_people' and 'overlayURL' not in pending
        with fetch(record['overlayURL']) as response:assert hashlib.sha256(response.read()).hexdigest()==chosen['sha256']
        with fetch('/v1/guides/cup_eye_orbitr_cc') as response:assert json.load(response)['sha256']==fixture['guides']['cup_eye_orbitr_cc']['sha256']
        route='/v1/scripts/'+template['id']+'/guide-sequence'
        with fetch(route) as response:sequence=json.load(response)
        assert sequence['scope']=='full_script_instruction_sequence' and sequence['steps']
        with fetch(sequence['videoURL']) as response:assert response.headers['Content-Type']=='video/mp4' and response.read(100)
        for path,authorized,expected in [(route,False,401),('/v1/scripts/not-a-script/guide-sequence',True,404)]:
            try:fetch(path,authorized)
            except urllib.error.HTTPError as error:assert error.code==expected
            else:raise AssertionError(path)
    finally:server.shutdown();server.server_close();thread.join()
report=dict(per_step_context_asset_selected=True,canonical_guide_preserved=True,context_hash_download_verified=True,full_script_sequence_endpoint=True,mp4_content_type=True,authentication_checked=True,unknown_sequence_404=True,live_server_changed=False)
(HERE/'context-server-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
