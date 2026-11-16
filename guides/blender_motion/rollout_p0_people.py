"""Render/export the restored canonical cast in isolated Blender processes."""
import argparse,hashlib,json,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'guides/tools'))
import p0_catalog
from export_p0 import export
from p0_gallery import build


def render(row,out):
    gid=row['id'];folder=out/'animations-light'/gid;folder.mkdir(parents=True,exist_ok=True)
    print('RENDERING',gid,flush=True)
    with (folder/'render.log').open('w') as log:
        subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--python-exit-code','1',
            '-P',str(HERE/'render_p0.py'),'--','--id',gid,'--out',str(folder),'--replace'],stdout=log,stderr=subprocess.STDOUT,check=True)
    return gid,folder


def run(workers=1,ids=None):
    rows=[r for r in p0_catalog.registry()['guides'] if r.get('allowedPeople')]
    if ids:
        assert set(ids)<={r['id'] for r in rows},'Unknown character guide'
        rows=[r for r in rows if r['id'] in ids]
    out=ROOT/'catalog/p0';report=out/'people-rollout.json'
    baseline=out/'people-before.json'
    if not baseline.exists():
        baseline.write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'guides/p0/renders').glob('*.png')},indent=2)+'\n')
    p0_catalog.write();build();results=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs=[pool.submit(render,row,out) for row in rows]
        for job in as_completed(jobs):
            gid,folder=job.result()
            # Export and gallery updates stay serial; only isolated renders run concurrently.
            checks=export(folder);build();results.append(dict(id=gid,status='passed',frames=checks['frames'],sha256=checks['sha256']))
            report.write_text(json.dumps(dict(status='complete' if len(results)==len(rows) else 'rendering',ready=len(results),total=len(rows),records=results),indent=2)+'\n')
            print('READY',gid,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,choices=[1,2],default=1)
    p.add_argument('--ids',nargs='+');a=p.parse_args();run(a.workers,a.ids)
