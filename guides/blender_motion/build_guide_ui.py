"""Refresh browser reference axes from each rendered starting camera, or its source tilt."""
from pathlib import Path
import importlib.util,json,re,sys
BASE=Path(__file__).resolve().parents[2]
tool=BASE/'guides/tools/build_bundle.py';sys.path.insert(0,str(tool.parent))
spec=importlib.util.spec_from_file_location('guide_bundle_angles',tool);bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
axes={}
for path in (BASE/'guides/templates').glob('*.json'):
    source=json.loads(path.read_text());steps=source.get('live',{}).get('steps',[])
    tilt=next((s['tilt']['target'] for s in steps if s.get('tilt')),0)
    native=BASE/'catalog/blender-animations'/path.stem/'scene-spec.json'
    if native.exists():
        scene=json.loads(native.read_text())
        if scene.get('camera_samples'):tilt=bundle.camera_down_tilt(scene['camera_samples'][0])
    axes[path.stem]='XY' if tilt>=70 else 'X'
p=BASE/'catalog/guide-ui.js';text=p.read_text();text,count=re.subn(r'const axes = .*?;\n','const axes = '+json.dumps(axes,separators=(',',':'))+';\n',text,count=1)
assert count==1;p.write_text(text)
print('Separate reference axes:',len(axes),'guides;',sum(value=='XY' for value in axes.values()),'overhead starts')
