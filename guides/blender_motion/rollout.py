"""Bounded background-only orchestration for the remaining source-reviewed guides."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parents[1];OUT=BASE/'catalog/blender-animations'
stage=sys.argv[1];assert stage in ['build','probes','render']
work=json.loads((ROOT/'work-plan.json').read_text())
ids=sys.argv[2:] or [g['id'] for g in work['guides'] if g['status'] not in ['approved_prototype','base_shot_reviewed','shot_and_handover_reviewed','final_shot_reviewed','deferred_people']]

if not ids:
    print('No eligible unfinished guides; people generation remains deferred')
    sys.exit(0)

def worker(index):
    chunk=ids[index::2];queue=OUT/('rollout-'+stage+'-'+str(index)+'.json');queue.write_text(json.dumps(chunk,indent=2)+'\n')
    log=queue.with_suffix('.log')
    with log.open('w') as stream:
        result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup','--python-exit-code','1','--python',str(ROOT/'rollout_worker.py'),'--',str(queue),stage],stdout=stream,stderr=subprocess.STDOUT)
    assert result.returncode==0,str(log)
    results=json.loads(queue.with_suffix('.progress.json').read_text())['results']
    if stage!='build':
        for row in results:
            if row['status']=='failed':continue
            with (OUT/(row['id']+'-'+stage+'-export.log')).open('w') as stream:
                cmd=[sys.executable,str(ROOT/'export_shot.py'),row['id']]
                if stage=='probes':cmd.append('--probes')
                status=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
            row['status']='failed' if status.returncode else 'probes_ready' if stage=='probes' else 'exported'
    return results
results=[]
with ThreadPoolExecutor(max_workers=2) as pool:
    for future in as_completed([pool.submit(worker,i) for i in range(2)]):
        results.extend(future.result());print(json.dumps(dict(stage=stage,completed=len(results),total=len(ids),failed=[r for r in results if r['status']=='failed'])),flush=True)
(OUT/('rollout-'+stage+'-results.json')).write_text(json.dumps(results,indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'build_gallery.py')],check=True)
if any(r['status']=='failed' for r in results):sys.exit(1)
