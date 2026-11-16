"""Soften unimportant background objects without rerendering color footage."""
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_primary_food_scenes as F
import build_shared_venue as C
import build_coffee_glass_batch as G

for key in F.SCENES:
    folder=G.ROOT/key
    assert (folder/'render-ready.json').exists()
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene=bpy.context.scene
    preserve=set()
    for root in scene.objects:
        if root.get('asset_family') in ['dining_table','dining_chair','dinner_plate','burger',
            'cake_slice','brunch_toast','saucer','latte_cup'] and root.location.y<2.5:
            preserve.update(C.meshes(root))
    F.soften_background(scene,preserve)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    spec=json.loads((folder/'scene-spec.json').read_text())
    spec['background_emphasis']='Context surfaces at 55% raw strength; food at full strength; one global 65% image-view multiplier'
    spec['viewfinder_axes']=['X','Y'] if key=='brunch-spread' else ['X']
    spec['revision']='primary-food-glass-2026-10-30-v2'
    (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    G.render(key,False,modes=['mask'])
