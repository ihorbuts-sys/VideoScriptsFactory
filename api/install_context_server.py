"""Install the tested context handlers and restart only the existing development API."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parent
preparation=json.loads((HERE/'context-server-preparation.json').read_text());source=Path(preparation['source']);prepared=HERE/'context-server.py'
assert hashlib.sha256(source.read_bytes()).hexdigest()==preparation['source_sha256'],'Running source changed; prepare the patch again'
check=json.loads((HERE/'context-server-check.json').read_text());assert check['per_step_context_asset_selected'] and check['authentication_checked']
publication=json.loads((HERE/'publication.json').read_text());pid=publication['pid'];port=publication['port']
command=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,check=True).stdout.strip();argv=shlex.split(command)
index=next(i for i,item in enumerate(argv) if item.endswith('server.py'))
launched=Path(argv[index])
if not launched.is_absolute():
 cwd_lines=subprocess.run(['lsof','-a','-p',str(pid),'-d','cwd','-Fn'],capture_output=True,text=True,check=True).stdout.splitlines()
 cwd=Path(next(line[1:] for line in cwd_lines if line.startswith('n')))
 launched=cwd/launched
assert launched.resolve()==source.resolve()
args=argv[index+1:];assert '--write' not in args
stamp=datetime.datetime.now(ZoneInfo('Europe/Kyiv')).strftime('%Y%m%d-%H%M%S');backup=HERE/'context-server-backups'/stamp;backup.mkdir(parents=True)
shutil.copy2(source,backup/'server.py')
(HERE/'context-server.diff').write_text(''.join(difflib.unified_diff(source.read_text().splitlines(True),prepared.read_text().splitlines(True),fromfile='server.py before',tofile='server.py context handlers')))
shutil.copy2(prepared,source)
os.kill(pid,signal.SIGTERM)
log=(HERE/'context-server-runtime.log').open('a');environment=dict(os.environ);environment['SCRIPT_CATALOG_DIR']=str(source.parent/'catalog')
process=None;healthy=False
for attempt in range(3):
 time.sleep(.20)
 process=subprocess.Popen([sys.executable,str(source),*args],cwd=str(source.parent),env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(30):
  if process.poll() is not None:break
  try:
   with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/v1/health',timeout=1) as response:healthy=json.load(response).get('ok',False)
   if healthy:break
  except (OSError,ValueError):time.sleep(.10)
 if healthy:break
if not healthy:
 shutil.copy2(backup/'server.py',source)
 subprocess.Popen([sys.executable,str(source),*args],cwd=str(source.parent),env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 raise RuntimeError('Context API did not start; restored the previous source and restarted it')
report=dict(pid=process.pid,previous_pid=pid,port=port,backup=str(backup),prepared_sha256=preparation['prepared_sha256'],token_unchanged=True,healthy=True,source=str(source))
(HERE/'context-server-publication.json').write_text(json.dumps(report,indent=2)+'\n');publication.update(pid=process.pid,previous_pid=pid,context_handlers=True);(HERE/'publication.json').write_text(json.dumps(publication,indent=2)+'\n')
print(json.dumps(dict(pid=process.pid,port=port,healthy=True,token_unchanged=True,context_handlers=True)))
