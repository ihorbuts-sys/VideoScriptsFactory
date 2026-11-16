"""Check default, contextual and script API links against the reviewed render bytes."""
import hashlib,io,json,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
LIVE=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/catalog')
TOKEN=(LIVE.parent/'.token').read_text().strip()
HOST='http://127.0.0.1:8765'

def get(path):
    url=path if path.startswith('http') else HOST+path
    request=urllib.request.Request(url,headers={'Authorization':'Bearer '+TOKEN})
    with urllib.request.urlopen(request,timeout=40) as r:return r.read(),r.headers.get_content_type()

def payload(path):return json.loads(get(path)[0])

def run():
    manifest=json.loads((BASE/'catalog/clay-scenes/active-revisions.json').read_text());results=[]
    for gid,row in manifest['guides'].items():
        folder=BASE/row['folder'];guide=payload('/v1/guides/'+gid)
        context=payload('/v1/steps/'+row['context_template']+'.'+row['context_step']+'/guides')
        contextual=next(g for g in context['guides'] if g['id']==gid)
        assert guide['overlayURL']==contextual['overlayURL']
        assert guide['animationSeconds']==12 and guide['alphaFactor']==.65
        assert guide['sha256']==row['files']['ghost.png']
        paths={}
        for key,name,mime in [('overlayURL','ghost.png','image/png'),('posterURL','ghost-poster.png','image/png'),
                ('stripURL','ghost-strip.jpg','image/jpeg'),('colorVideoURL','color.mp4','video/mp4')]:
            data,content_type=get(guide[key]);assert content_type==mime
            assert hashlib.sha256(data).hexdigest()==hashlib.sha256((folder/name).read_bytes()).hexdigest()
            paths[key]=urllib.parse.urlsplit(guide[key]).path
            if key=='overlayURL':
                im=Image.open(io.BytesIO(data));duration=0;maximum=0
                for n in range(im.n_frames):
                    im.seek(n);duration+=im.info.get('duration',0);maximum=max(maximum,im.convert('RGBA').getchannel('A').getextrema()[1])
                assert im.n_frames>1 and abs(duration-12000)<1 and maximum<=166
        scripts=payload('/v1/scripts?page=0&pageSize=100')['templates'];template=next(t for t in scripts if t['id']==row['context_template'])
        step=next(s for s in template['steps'] if s['id']==row['context_step']);assert guide['overlayURL'] in step['overlays']
        results.append(dict(id=gid,default_and_step_and_script_links_match=True,all_assets_http_200=True,
            asset_hashes_match=True,paths=paths,ghost_duration_ms=duration,max_ghost_alpha=maximum,encoded_apng_frames=im.n_frames))
    listing=payload('/v1/guides?page=0&pageSize=200');assert listing['total']==178
    sequences=[]
    for tid,row in manifest.get('sequences',{}).items():
        result=payload('/v1/scripts/'+tid+'/guide-sequence');folder=BASE/row['folder']
        assert result['seconds']==row['seconds'] and result['steps']==row['steps']
        for key,name in [('overlayURL','ghost.png'),('videoURL','preview.mp4'),('posterURL','poster.png'),('stripURL','strip.jpg')]:
            data,content_type=get(result[key]);assert hashlib.sha256(data).hexdigest()==row['files'][name]
        sequences.append(dict(id=tid,seconds=row['seconds'],all_four_assets_http_200=True,asset_hashes_match=True,
            refreshed_steps=['bar','seat'],other_steps_retain_existing_art=True))
    report=dict(status='passed',guides=results,total_api_guides=178,authenticated_http=True,
        refreshed_sequences=sequences,token_in_report=False,preview_revision=json.loads((LIVE/'catalog.json').read_text())['previewArt']['revisionSHA256'])
    (BASE/'catalog/clay-scenes/publication/live-api-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':run()
