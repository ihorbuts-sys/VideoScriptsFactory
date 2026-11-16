"""Round-trip full and proxy exports to verify units, axes and support origin."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'model_refferences/tripo-cli/primary-targets-2026-10-29'


def run():
    plan=json.loads((ROOT/'plan.json').read_text());results=[]
    for row in plan['objects']:
        folder=BASE/'model_refferences/objects'/row['id']/'tripo-generated/review'
        component=json.loads((folder/'component.json').read_text())
        expected=component['bounds_blender_m'];extent=max(component['actual_dimensions_m'])
        for filename in ['model.glb','model.usdz','geometry-proxy.glb','geometry-proxy.usdz']:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            path=folder/filename
            if path.suffix=='.glb':bpy.ops.import_scene.gltf(filepath=str(path))
            else:bpy.ops.wm.usd_import(filepath=str(path),import_cameras=False,import_lights=False)
            meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
            assert meshes and not any(o.type in ['CAMERA','LIGHT','ARMATURE'] for o in bpy.context.scene.objects)
            bpy.context.view_layer.update()
            points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
            lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
            error=max(abs(a-b) for actual,source in zip([lo,hi],expected) for a,b in zip(actual,source))
            allowed=extent*.026 if filename.startswith('geometry') else .0002
            assert error<allowed,(row['id'],filename,error,allowed,[lo,hi],expected)
            assert abs(lo[2])<max(.0002,extent*.01),(row['id'],filename,lo)
            results.append(dict(id=row['id'],file=filename,max_bounds_error_m=error,
                origin_on_support_plane=True,axis_and_scale_roundtrip=True))
        print('PRIMARY_EXPORT_ROUNDTRIP_PASSED',row['id'],flush=True)
    (ROOT/'export-roundtrip.json').write_text(json.dumps(dict(status='passed',objects=16,files=len(results),checks=results),indent=2)+'\n')


if __name__=='__main__':run()
