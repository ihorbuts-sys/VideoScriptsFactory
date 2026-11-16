"""Execute queued background Blender jobs, retaining failures for focused correction."""
import bpy
import json
import sys
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import build_scenes
args=sys.argv[sys.argv.index('--')+1:]
queue=Path(args[0]);stage=args[1];rows=json.loads(queue.read_text());results=[]
for gid in rows:
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build_scenes.run(gid,probes=stage=='probes',build_only=stage=='build',take_only=False)
        result=dict(id=gid,status='built' if stage=='build' else 'probes_rendered' if stage=='probes' else 'frames_rendered')
    except Exception as error:
        traceback.print_exc();result=dict(id=gid,status='failed',error=str(error))
    results.append(result)
    queue.with_suffix('.progress.json').write_text(json.dumps(dict(stage=stage,results=results,total=len(rows)),indent=2)+'\n')
    print('ROLLOUT_PROGRESS',json.dumps(result),flush=True)
