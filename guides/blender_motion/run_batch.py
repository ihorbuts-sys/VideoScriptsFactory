"""Run independent Blender jobs with bounded CPU/GPU concurrency."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]
OUT=BASE/"catalog/blender-animations"
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
PYTHON=sys.executable
probes="--probes" in sys.argv
complete="--complete" in sys.argv
gids=[arg for arg in sys.argv[1:] if not arg.startswith("--")]


def job(gid):
    assert all(c.isalnum() or c=="_" for c in gid)
    log=OUT/(gid+("-probe-job.log" if probes else "-render-job.log"))
    command=[BLENDER,"--background","--factory-startup","--python-exit-code","1","--python",str(ROOT/"build_scenes.py"),"--",gid]
    if not complete:command.append("--take-only")
    if probes:command.append("--probes")
    with log.open("w") as stream:
        result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        if result.returncode:return dict(id=gid,status="failed",log=str(log),exit_code=result.returncode)
        export=[PYTHON,str(ROOT/"export_shot.py"),gid]
        if probes:export.append("--probes")
        result=subprocess.run(export,stdout=stream,stderr=subprocess.STDOUT)
    return dict(id=gid,status="probes_ready" if probes and result.returncode==0 else "exported" if result.returncode==0 else "failed",log=str(log))


results=[]
with ThreadPoolExecutor(max_workers=2) as pool:
    for future in as_completed([pool.submit(job,gid) for gid in gids]):
        result=future.result();results.append(result);print(json.dumps(result),flush=True)
        (OUT/"batch-progress.json").write_text(json.dumps(dict(phase="probes" if probes else "full_shots",results=results,total=len(gids)),indent=2)+"\n")
subprocess.run([PYTHON,str(ROOT/"build_gallery.py")],check=True)
if any(r["status"]=="failed" for r in results):sys.exit(1)
