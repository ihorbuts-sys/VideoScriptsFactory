"""One Meshy creator comparison task; original references and downloaded model are retained."""
import argparse,base64,hashlib,json,mimetypes,os,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
API='https://api.meshy.ai/openapi/v1/multi-image-to-3d'

def credentials():
    key=os.environ.get('MESHY_API_KEY','').strip()
    local=ROOT/'.env'
    if not key and local.exists():
        for line in local.read_text().splitlines():
            if line.strip().startswith('MESHY_API_KEY='):
                key=line.partition('=')[2].strip().strip('\"\'')
    if not key or key=='replace_with_your_key_locally':
        raise RuntimeError('Meshy API access is not configured. Set MESHY_API_KEY in the environment or the adjacent .env file; do not paste it into chat.')
    return key

def request(url,key,data=None):
    headers={'Authorization':'Bearer '+key}
    if data is not None:headers['Content-Type']='application/json'
    body=json.dumps(data).encode() if data is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url,body,headers),timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # The key and request headers are never logged.
        message=error.read().decode(errors='replace').replace(key,'[redacted]')
        raise RuntimeError(f'Meshy HTTP {error.code}: {message[:1000]}') from None

def submit(key):
    task_file=ROOT/'task.json'
    if task_file.exists():
        task=json.loads(task_file.read_text());print(json.dumps(dict(action='existing_task_reused',task_id=task['id'])));return
    marker=ROOT/'submission-attempt.json'
    if marker.exists():
        raise RuntimeError('A submission was already attempted without a saved task ID. Check the Meshy task history before submitting again; a paid request is not retried automatically.')
    settings=json.loads((ROOT/'settings.json').read_text());inputs=json.loads((ROOT/'inputs.json').read_text());urls=[]
    for image in inputs['views']:
        p=ROOT/image['path'];data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==image['sha256']
        assert len(data)<=20*1024*1024
        urls.append('data:'+mimetypes.guess_type(p.name)[0]+';base64,'+base64.b64encode(data).decode())
    assert len(urls)==4 and inputs['views'][0]['view']=='front'
    marker.write_text(json.dumps(dict(attempted_at_unix=time.time(),estimated_credits=inputs['expected_credits'],settings=settings),indent=2)+'\n')
    result=request(API,key,{**settings,'image_urls':urls});task_id=result['result']
    task_file.write_text(json.dumps(dict(id=task_id,endpoint=API,submitted_at_unix=time.time(),estimated_credits=inputs['expected_credits']),indent=2)+'\n')
    print(json.dumps(dict(action='submitted',task_id=task_id)))

def status(key):
    task=json.loads((ROOT/'task.json').read_text());result=request(API+'/'+task['id'],key)
    (ROOT/'task-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result.get(k) for k in ['id','status','progress','consumed_credits','task_error']}));return result

def download(key):
    result=status(key)
    if result['status']!='SUCCEEDED':raise RuntimeError('The Meshy task has not succeeded; no result was substituted')
    out=ROOT/'original';out.mkdir(exist_ok=True);files={}
    assets={'creator.glb':result['model_urls']['glb']}
    for view,url in result.get('thumbnail_urls',{}).items():assets['thumbnail-'+view+'.png']=url
    if result.get('thumbnail_url'):assets['thumbnail.png']=result['thumbnail_url']
    for name,url in assets.items():
        p=out/name
        if not p.exists():
            with urllib.request.urlopen(url,timeout=120) as response:data=response.read()
            temporary=p.with_suffix(p.suffix+'.tmp');temporary.write_bytes(data);temporary.replace(p)
        files[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
    (ROOT/'download-checks.json').write_text(json.dumps(dict(task_id=result['id'],files=files,model_unmodified=True),indent=2)+'\n')
    print(json.dumps(dict(action='downloaded',files=list(files))))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['submit','status','download']);args=parser.parse_args()
    try:
        key=credentials();{'submit':submit,'status':status,'download':download}[args.action](key)
    except (RuntimeError,FileNotFoundError) as error:
        parser.exit(1,str(error)+'\n')
