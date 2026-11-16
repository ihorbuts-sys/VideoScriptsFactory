"""Check all active native and contextual scenes against the owner's dining-layout rule."""
import bpy,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_place_settings import inspect
work=json.loads((BASE/'guides/blender_motion/work-plan.json').read_text());folders=[BASE/'catalog/blender-animations'/r['id'] for r in work['guides'] if r['status']!='deferred_people']
folders+=[BASE/rel for rel in dict.fromkeys(json.loads((BASE/'catalog/context-animations/variant-sources.json').read_text()).values())];results=[]
for folder in folders:
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    rows=inspect(scene);results.append(dict(id=folder.name,source=str(folder.relative_to(BASE)),plates=rows,status='failed' if any(row['too_central'] for row in rows) else 'passed'))
out=BASE/'catalog/table-placement-review';out.mkdir(exist_ok=True)
(out/'audit.json').write_text(json.dumps(results,indent=2)+'\n')
failed=[r['id'] for r in results if r['status']=='failed'];print('TABLE_POLICY',len(results),'scenes;',sum(len(r['plates']) for r in results),'resting plates;',len(failed),'failures',flush=True)
if failed:raise SystemExit(1)
