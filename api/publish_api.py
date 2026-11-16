"""Install the verified bundle and targeted kit edits, then reload the dev server."""
import datetime
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
KIT=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit')
SERVER=KIT/'tools/scriptwriter'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    check=json.loads((HERE/'staged-api-check.json').read_text())
    assert check['guides']==178 and check['step_endpoints']==304 and check['overlay_hashes_match']
    plan=json.loads((HERE/'publication-plan.json').read_text())
    for item in plan:
        target=Path(item['target']);actual=digest(target) if target.exists() else None
        assert actual==item['before_sha256'],f'Changed since preparation: {target}'
    running=subprocess.run(['lsof','-t','-iTCP:8765','-sTCP:LISTEN'],capture_output=True,text=True)
    pids=set(running.stdout.split());assert len(pids)<=1,'Multiple listeners on development port'
    old_pid=int(next(iter(pids))) if pids else None
    if old_pid:
        command=subprocess.check_output(['ps','-p',str(old_pid),'-o','args='],text=True)
        assert 'server.py' in command and '--port 8765' in command,'Unexpected server on port 8765'
        children=subprocess.run(['pgrep','-P',str(old_pid)],capture_output=True,text=True)
        assert not children.stdout.strip(),'The development server has an active child job; retry when it finishes.'
    stamp=datetime.datetime.now(ZoneInfo('Europe/Kyiv')).strftime('%Y%m%d-%H%M%S')
    backup=HERE/'publication-backups'/stamp;backup.mkdir(parents=True)
    for item in plan:
        target=Path(item['target'])
        if target.exists():
            dest=backup/target.relative_to(KIT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
    catalog=SERVER/'catalog';catalog.mkdir(exist_ok=True)
    if (catalog/'catalog.json').exists():shutil.copy2(catalog/'catalog.json',backup/'catalog.json')
    linked={};files=0
    for kind in ('previews','overlays','scenarios','3d'):
        for source in sorted((HERE/'bundle'/kind).rglob('*')):
            if not source.is_file():continue
            target=catalog/source.relative_to(HERE/'bundle');target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_name(target.name+'.publishing')
            if temporary.exists():temporary.unlink()
            stat=source.stat();identity=(stat.st_dev,stat.st_ino)
            if identity in linked:
                os.link(linked[identity],temporary);temporary.replace(target)
            elif not target.exists() or target.stat().st_size!=stat.st_size or target.stat().st_mtime_ns!=stat.st_mtime_ns:
                shutil.copy2(source,temporary);temporary.replace(target)
            linked[identity]=target;files+=1
    bundle=json.loads((HERE/'bundle/catalog.json').read_text())
    for gid,guide in bundle['guides'].items():
        assert digest(catalog/guide['overlay'])==guide['sha256'],gid
        for key in ('scenario','model3D','poster','strip'):assert (catalog/guide[key]).is_file(),(gid,key)
    for item in plan:
        target=Path(item['target']);target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_name(target.name+'.publishing');shutil.copy2(item['staged'],temporary);temporary.replace(target)
    temporary=catalog/'catalog.json.publishing';shutil.copy2(HERE/'bundle/catalog.json',temporary);temporary.replace(catalog/'catalog.json')
    if old_pid:
        os.kill(old_pid,signal.SIGTERM)
        for _ in range(100):
            probe=subprocess.run(['lsof','-t','-iTCP:8765','-sTCP:LISTEN'],capture_output=True,text=True)
            if not probe.stdout.strip():break
            time.sleep(.05)
        else:raise RuntimeError('Previous server has not released port 8765')
    environment=os.environ.copy();environment['SCRIPT_CATALOG_DIR']=str(catalog)
    log_path=HERE/'server.log'
    with log_path.open('ab',buffering=0) as log:
        process=subprocess.Popen([sys.executable,'server.py','--port','8765'],cwd=SERVER,env=environment,
                                 stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    token=(SERVER/'.token').read_text().strip()
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        if process.poll() is not None:raise RuntimeError(f'Server exited; inspect {log_path}')
        try:
            req=urllib.request.Request('http://127.0.0.1:8765/v1/guides?pageSize=1',headers={'Authorization':'Bearer '+token})
            with urllib.request.urlopen(req,timeout=2) as response:
                assert json.load(response)['total']==178
            break
        except OSError:time.sleep(.1)
    else:raise RuntimeError(f'Server readiness timed out; inspect {log_path}')
    report=dict(date=datetime.datetime.now(ZoneInfo('Europe/Kyiv')).isoformat(),pid=process.pid,
                previous_pid=old_pid,port=8765,catalog=str(catalog),source_edits=[e['target'] for e in plan],
                backup=str(backup),asset_files=files,guides=178,watercolor=96,schematic=82,
                source_previews_and_scenarios_changed=False)
    (HERE/'publication.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
