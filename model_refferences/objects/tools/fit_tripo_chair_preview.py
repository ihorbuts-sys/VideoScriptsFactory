"""Fit the review camera to the actual chair silhouette, preserving semantic anchors."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
OUT=P.ROOT/'dining_chair/tripo-generated/review'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'))
scene=bpy.context.scene;root=next(o for o in scene.objects if o.get('asset_id')=='dining_chair_tripo');camera=scene.camera
meshes=[o for o in root.children_recursive if o.type=='MESH'];bpy.context.view_layer.update()
world=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];inverse=camera.matrix_world.inverted();points=[inverse@v for v in world]
low=Vector((min(p.x for p in points),min(p.y for p in points),0));high=Vector((max(p.x for p in points),max(p.y for p in points),0))
camera.location+=camera.matrix_world.to_3x3()@((low+high)/2)
camera.data.ortho_scale=max(high.x-low.x,high.y-low.y)/.88
bpy.context.view_layer.update();projected=[world_to_camera_view(scene,camera,p) for p in world]
bounds=dict(min_x=min(p.x for p in projected),max_x=max(p.x for p in projected),min_y=min(p.y for p in projected),max_y=max(p.y for p in projected))
assert min(bounds['min_x'],bounds['min_y'])>.045 and max(bounds['max_x'],bounds['max_y'])<.955,bounds
scene.view_layers[0].material_override=None
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
for folder,override in [('rendered',None),('shape',P.material('cream'))]:
    scene.view_layers[0].material_override=override;scene.render.filepath=str(OUT/folder/'preview.png');bpy.ops.render.render(write_still=True)
metadata=json.loads((OUT/'metadata.json').read_text());metadata['preview_camera_bounds']=bounds
metadata['preview_camera_fitted_to_actual_mesh']=True;(OUT/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('CHAIR_PREVIEW_FRAME_VERIFIED',bounds)
