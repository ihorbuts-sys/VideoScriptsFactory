"""CC0 MakeHuman people baked per pose, placed by their eye and grip landmarks."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
import assets as A
import geometry as G

LIBRARY=Path(__file__).resolve().parent/'vendor/makehuman-mpfb/people.blend'


def place(person,pose='stand',position=(0,0,0),turn=0,eyes_at=None,role='hero',reason='Whole CC0 MakeHuman person; body, clothes and hair stay one connected figure'):
    """Feet stand at `position`; with `eyes_at`, the figure is scaled and moved so its eye midpoint lands there instead."""
    name=person+'_'+pose
    with bpy.data.libraries.load(str(LIBRARY),link=False) as (src,dst):dst.objects=[name]
    mesh=dst.objects[0];bpy.context.collection.objects.link(mesh)
    mesh.name='MakeHuman person '+name
    mesh.data.materials.clear();mesh.data.materials.append(G.MAT)
    A.tag(mesh,role,reason)
    root=A.empty('Person placement '+name,position);root.rotation_euler.z=turn
    mesh.parent=root
    marks={key:Vector(value) for key,value in json.loads(mesh['landmarks']).items()}
    if eyes_at is not None:
        scale=Vector(eyes_at).z/marks['eyes'].z
        root.scale=(scale,)*3
        root.location=Vector(eyes_at)-root.matrix_basis.to_3x3()@marks['eyes']
    root['landmarks']=mesh['landmarks'];root['person_source']=mesh['person_source']
    return root


def landmark(root,key):
    bpy.context.view_layer.update()
    return root.matrix_world@Vector(json.loads(root['landmarks'])[key])


def raise_to(root,frame,u):
    """Keys the baked raise at `u` (0 = hands hanging, 1 = the raised pose); returns {side: world grip} at that frame."""
    mesh=next(c for c in root.children if c.type=='MESH')
    data=json.loads(mesh['raise']);final=json.loads(root['landmarks'])
    grips=data['grips']+[{side:final['grip_'+side] for side in data['sides']}]
    keys=mesh.data.shape_keys.key_blocks;n=len(grips)-1
    x=min(max(u,0),1)*n;k=min(int(x),n-1);t=x-k
    for i in range(n):
        keys[f'raise_{i}'].value=1-t if i==k else t if i==k+1 else 0
        keys[f'raise_{i}'].keyframe_insert('value',frame=frame)
    bpy.context.view_layer.update()
    return {side:root.matrix_world@Vector(grips[k][side]).lerp(Vector(grips[k+1][side]),t) for side in data['sides']}
