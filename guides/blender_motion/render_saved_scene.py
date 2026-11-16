"""Render only the published frame range of an existing project, preserving archived stages."""
import bpy,json,sys,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:];gid=args[0];out=BASE/'catalog/blender-animations'/gid
spec=json.loads((out/'scene-spec.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(out/'scene.blend'))
scene=bpy.data.scenes['01 Ghost contours'];fill=bpy.data.scenes['02 Flat fill masks']
stages=[(round(row['t']*15)+1,bpy.data.objects[row['name']]) for row in spec['camera_stages']]
for current,folder in [(scene,'contours'),(fill,'fills')]:
    bpy.context.window.scene=current;current.render.threads_mode='FIXED';current.render.threads=2;rendered={};destination=out/folder;destination.mkdir(exist_ok=True)
    if current==fill:current.timeline_markers.clear()
    for f in range(1,spec['frame_count']+1):
        current.frame_set(f);current.camera=[cam for start,cam in stages if start<=f][-1];bpy.context.view_layer.update();current.render.filepath=str(destination/('frame_%04d.png'%f))
        signature=tuple(round(v,7) for row in current.camera.matrix_world for v in row)
        for obj in sorted((o for o in current.objects if o.type=='MESH'),key=lambda o:o.name):
            signature+=tuple(round(v,7) for row in obj.matrix_world for v in row)
            if obj.data.shape_keys:signature+=tuple(round(k.value,6) for k in obj.data.shape_keys.key_blocks)
        if signature in rendered:shutil.copy2(rendered[signature],current.render.filepath)
        else:bpy.ops.render.render(write_still=True,scene=current.name);rendered[signature]=current.render.filepath
    print('SAVED_SCENE_RENDERED',gid,folder,spec['frame_count'],flush=True)
spec['status']='frames_rendered';(out/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
