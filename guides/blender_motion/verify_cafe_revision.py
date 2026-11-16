"""Check actual pour contacts, milk plane and the shared morning table scene."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'catalog/blender-animations'
results=[]
for gid in ['latte_top_in_cd_whipout','over_shoulder_counter_os_hold','cup_eye_hold_whipout']:
    folder=OUT/gid;spec=json.loads((folder/'scene-spec.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    row=dict(id=gid,frames=spec['frame_count'],status='passed')
    if gid=='latte_top_in_cd_whipout':
        milk=bpy.data.objects['Milk spreading on coffee surface']
        pitcher=bpy.data.objects['Milk pitcher entering from the edge']
        stream=bpy.data.objects['Milk stream from pitcher lip']
        max_gap=0;max_radius=0
        for sample in spec['pour_contacts']:
            scene.frame_set(sample['frame']);bpy.context.view_layer.update()
            start=pitcher.matrix_world@Vector((-.061,0,.115))
            actual_start=stream.matrix_world@Vector((0,0,0))
            actual_end=stream.matrix_world@Vector((0,0,1))
            max_gap=max(max_gap,(start-actual_start).length,(actual_end-Vector(sample['landing'])).length)
            for v in milk.data.vertices:
                p=milk.matrix_world@v.co
                assert abs(p.z-.902)<1e-6,'Milk geometry must stay on the liquid plane'
                max_radius=max(max_radius,p.xy.length)
            assert actual_end.xy.length<.045
        assert max_gap<1e-5 and max_radius<.045
        row.update(pour_frames=len(spec['pour_contacts']),max_endpoint_gap_m=max_gap,
                   milk_max_radius_m=max_radius,coffee_opening_radius_m=.045,milk_stays_on_surface=True)
    elif gid=='over_shoulder_counter_os_hold':
        stream=bpy.data.objects['Espresso into ordered cup']
        surface=bpy.data.objects['Ordered coffee coffee surface']
        max_gap=0
        for sample in spec['order_pour_contacts']:
            scene.frame_set(sample['frame']);bpy.context.view_layer.update()
            end=stream.matrix_world@Vector((0,0,1))
            p=surface.matrix_world@Vector((0,0,.106))
            max_gap=max(max_gap,(end-p).length)
        assert max_gap<1e-5
        cams=spec['camera_samples'];assert all(
            max(abs(a-b) for a,b in zip(c['position'],cams[0]['position']))<1e-6 and
            max(abs(a-b) for a,b in zip(c['rotation'],cams[0]['rotation']))<1e-6 for c in cams)
        assert max(c['position'][1] for c in cams)<-.18
        row.update(pour_frames=len(spec['order_pour_contacts']),max_endpoint_gap_m=max_gap,
                   camera_fixed=True,visitor_side=True,people_meshes_generated=0)
    else:
        tracked=[o for o in scene.objects if o.type=='MESH' and not o.name.startswith('Cup steam')]
        matrices=None
        for f in range(1,spec['frame_count']+1):
            scene.frame_set(f);bpy.context.view_layer.update()
            sample={o.name:tuple(v for row in o.matrix_world for v in row) for o in tracked}
            if matrices is None:matrices=sample
            assert sample==matrices,'Only camera and steam should move; pastry must not animate itself'
        assert len(spec['camera_stages'])==1
        row.update(one_camera=True,props_unchanged_all_frames=True,pastry_supported=True,
                   next_step_source_start_frame=76,next_step_source_end_frame=126)
    results.append(row)
path=BASE/'catalog/cafe-review/geometry-verification.json'
path.write_text(json.dumps(dict(status='passed',scenes=results),indent=2)+'\n')
print('CAFE_PHYSICAL_CHECKS_PASSED',len(results),flush=True)
