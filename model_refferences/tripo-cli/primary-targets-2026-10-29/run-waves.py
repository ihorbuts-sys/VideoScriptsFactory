"""Resume the authorized 640-credit object batch, never submit paid retries."""
from pathlib import Path
import subprocess,time,json
ROOT=Path(__file__).resolve().parent
CWD=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit')
start=time.monotonic()
# Wave 1 was started interactively. Wait for its persisted success records.
while True:
 state=ROOT/'wave1.yaml.state.json'
 if state.exists():
  jobs=json.loads(state.read_text()).get('jobs',{})
  if len(jobs)==4 and all(r.get('status')=='success' for r in jobs.values()):break
  assert not any(r.get('status') in ['failed','needs_attention'] for r in jobs.values()),'Recover the existing wave-1 task; do not regenerate'
 assert time.monotonic()-start<1800
 time.sleep(3)
for wave in [2,3,4]:
 path=ROOT/f'wave{wave}.yaml'
 while not path.exists():
  assert time.monotonic()-start<7200,'Reference review not completed'
  time.sleep(3)
 data=json.loads(path.read_text());assert len(data['jobs'])==4
 assert all(j['model']=='tripo-v3.1' and j['params']['texture_quality']=='detailed' for j in data['jobs'])
 with (ROOT/f'wave{wave}-result.json').open('w') as out,(ROOT/f'wave{wave}-progress.log').open('w') as err:
  subprocess.run(['tripo','batch','run',str(path),'--concurrency','3','--retries','0','--no-open','--json'],cwd=CWD,stdout=out,stderr=err,check=True)
 result=json.loads((ROOT/f'wave{wave}-result.json').read_text());assert result['success']==4
 print('PRIMARY_TARGET_WAVE_COMPLETE',wave,flush=True)
print('PRIMARY_TARGET_GENERATION_COMPLETE',flush=True)
