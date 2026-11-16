"""Read-only, depth-tested 3D reflection cues for cup/plate rims and window frames.

The physical light stays fixed. The small warm reflection moves only as the view or object moves.
No saved Blender project is modified.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

BASE=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:]
root=BASE/'catalog/blender-animations'
if '--root' in args:
    i=args.index('--root');root=Path(args[i+1]);args=args[:i]+args[i+2:]


def identify(obj):
    name=obj.name.lower()
    if any(word in name for word in ['hollow ceramic body','open bowl','plate with formed rim','dinner plate','saucer']):
        vertices=[v.co for v in obj.data.vertices];highest=max(v.z for v in vertices)
        if 'plate' in name or 'saucer' in name:
            radius=max(math.hypot(v.x,v.y) for v in vertices)
            z=max(v.z for v in vertices if math.hypot(v.x,v.y)>radius-.0002)
        else:
            radius=max(math.hypot(v.x,v.y) for v in vertices if v.z>highest-.0002);z=highest
        return dict(kind='rim',radius=radius,z=z+.0005)
    if name.startswith(('window side','window crossbar','window mullion')):
        points=[Vector(c) for c in obj.bound_box];lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
        axis=max(range(3),key=lambda i:hi[i]-lo[i]);return dict(kind='window',lo=list(lo),hi=list(hi),axis=axis)
    return None


def project(scene,cam,deps,obj,point):
    world=obj.matrix_world@point;q=world_to_camera_view(scene,cam,world)
    if not (0<=q.x<=1 and 0<=q.y<=1 and q.z>cam.data.clip_start):return None
    origin=cam.matrix_world.translation;delta=world-origin;distance=delta.length
    hit,location,normal,index,other,matrix=scene.ray_cast(deps,origin,delta.normalized(),distance=distance+.003)
    if hit and other.original.name!=obj.original.name and (location-origin).length<distance-.004:return None
    return [round(q.x*540,3),round((1-q.y)*960,3)]


for gid in args:
    folder=root/gid;spec=json.loads((folder/'scene-spec.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    surfaces=[(obj,kind) for obj in scene.objects if obj.type=='MESH' and (kind:=identify(obj))]
    lights=[o for o in scene.objects if o.type=='LIGHT'];assert all(o.animation_data is None for o in lights)
    stages=[(round(row['t']*15)+1,bpy.data.objects[row['name']]) for row in spec['camera_stages']]
    frames=[];path_count=0
    for f in range(1,spec['frame_count']+1):
        scene.frame_set(f);bpy.context.view_layer.update();cam=[c for start,c in stages if start<=f][-1];deps=bpy.context.evaluated_depsgraph_get();paths=[]
        for obj,kind in surfaces:
            centre=obj.matrix_world.translation;view=(cam.matrix_world.translation-centre).normalized()
            light=(lights[0].matrix_world.translation-centre).normalized() if lights else Vector((-.6,-.2,.6)).normalized()
            if kind['kind']=='rim':
                half=obj.matrix_world.to_3x3().inverted()@(view+light);angle=math.atan2(half.y,half.x)
                points=[Vector((kind['radius']*math.cos(angle+math.radians(-13+j*26/8)),kind['radius']*math.sin(angle+math.radians(-13+j*26/8)),kind['z'])) for j in range(9)]
            else:
                lo=Vector(kind['lo']);hi=Vector(kind['hi']);axis=kind['axis'];local_view=obj.matrix_world.inverted()@cam.matrix_world.translation-(lo+hi)/2
                across=[i for i in range(3) if i!=axis];face=max(across,key=lambda i:abs(local_view[i]));point=(lo+hi)/2
                point[face]=(hi[face]+.0006) if local_view[face]>=0 else (lo[face]-.0006)
                middle=(lo[axis]+hi[axis])/2+.14*(hi[axis]-lo[axis])*math.tanh(local_view[axis]);length=min(.14,(hi[axis]-lo[axis])*.25)
                points=[]
                for j in range(5):p=point.copy();p[axis]=middle+length*(j/4-.5);points.append(p)
            segment=[]
            for point in points:
                projected=project(scene,cam,deps,obj,point)
                if projected is None:
                    if len(segment)>1:paths.append(dict(points=segment,kind=kind['kind'],object=obj.name))
                    segment=[]
                else:segment.append(projected)
            if len(segment)>1:paths.append(dict(points=segment,kind=kind['kind'],object=obj.name))
        path_count+=len(paths);frames.append(paths)
    record=dict(version=1,guide=gid,frames=frames,frame_count=spec['frame_count'],eligible_surfaces=len(surfaces),visible_paths=path_count,
                fixed_physical_light=True,view_dependent=True,depth_tested=True,world_geometry_unchanged=True,
                rgba=[226,181,69,140],width=1.3,build_fingerprint=spec['build_fingerprint'])
    (folder/'gliding-light.json').write_text(json.dumps(record,separators=(',',':'))+'\n')
    print('GLIDING_LIGHT',gid,'surfaces',len(surfaces),'visible paths',path_count,flush=True)
