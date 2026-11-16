"""Apply the owner's off-centre place-setting policy to saved scenes, preserving their full contents."""
import bpy,json,hashlib,shutil,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import table_composition
args=sys.argv[sys.argv.index('--')+1:];apply='--apply' in args;out=BASE/'catalog/table-placement-review';out.mkdir(exist_ok=True)
rows=json.loads(Path(args[0]).read_text());results=[]
for row in rows:
    if not row['needs_correction']:continue
    gid=row['guide'];folder=BASE/'catalog/blender-animations'/gid;spec=json.loads((folder/'scene-spec.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    result=table_composition.enforce(scene);result['guide']=gid;results.append(result)
    if apply:
        backup=out/'originals'/gid;backup.mkdir(exist_ok=True,parents=True)
        for name in ['scene.blend','scene-spec.json','review.json']:
            if not (backup/name).exists():shutil.copy2(folder/name,backup/name)
        spec['table_composition_review']=result
        spec['build_fingerprint']=hashlib.sha256((spec['build_fingerprint']+json.dumps(result,sort_keys=True)).encode()).hexdigest()
        spec['status']='layout_updated_pending_render'
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'))
        (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    print('TABLE_LAYOUT',gid,'applied' if apply else 'reviewed',result['changes'],flush=True)
(out/('applied.json' if apply else 'proposed.json')).write_text(json.dumps(results,indent=2)+'\n')
print('Reviewed tables:',len(results),flush=True)
