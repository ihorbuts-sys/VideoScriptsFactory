"""Audit saved native P0 scenes in Blender without opening its UI."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view


def world_bounds(obj):
    points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    return [min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]


def requested_scene_layout(scene,meta,guide_id):
    meshes=[o for o in scene.objects if o.type=='MESH']
    samples=[s for s in meta['camera_samples'] if s['phase']=='demonstration']
    if guide_id=='room_reveal_plant':
        plant=next(o for o in scene.objects if o.get('p0_reveal_plant'))
        parts=[o for o in plant.children_recursive if o.type=='MESH']
        tables=[o for o in meshes if o.name.startswith('Quiet tabletop')]
        assert len(tables)==3 and all(world_bounds(o)[0][1]>1.9 for o in tables),'No table belongs beneath the foreground leaves or phone'
        for table in tables:
            lo,hi=world_bounds(table)
            for part in parts:
                a,b=world_bounds(part)
                assert b[0]<lo[0] or a[0]>hi[0] or b[1]<lo[1] or a[1]>hi[1],'Plant and table footprints must be separate'
        for sample in samples:
            camera=Vector(sample['camera_position'])
            assert camera.y<.3
            assert min((camera-(o.matrix_world@v.co)).length for o in parts for v in o.data.vertices)>.1,'Keep the phone clear of the leaves'
        return dict(no_foreground_table=True,plant_and_table_footprints_separate=True,phone_clear_of_leaves=True)
    if guide_id.startswith('steam_'):
        plant=next(o for o in scene.objects if o.get('p0_window_plant'))
        assert plant.location.y>1.0 and abs(plant.location.z)<1e-5
        return dict(floor_plant_behind_cup_near_window=True)
    if guide_id=='handoff_counter_cup':
        cabinet=next(o for o in meshes if o.name=='Customer counter cabinet')
        top=next(o for o in meshes if o.name=='Customer counter top')
        assert world_bounds(cabinet)[1][2]>=world_bounds(top)[0][2]
        assert abs(world_bounds(top)[1][2]-1.05)<1e-5
        for sample in [samples[0],samples[-1]]:
            scene.frame_set(sample['frame'])
            corners=[world_to_camera_view(scene,scene.camera,Vector((-1.4,y,1.05))) for y in [-.15,.75]]
            assert any(0<p.x<1 and 0<p.y<1 for p in corners),'Show a real corner of the serving counter outline'
        return dict(full_height_cabinet_supports_counter=True,counter_corner_visible=True)
    if guide_id=='entrance_sign_tilt':
        assert max(s['camera_position'][1] for s in samples)-min(s['camera_position'][1] for s in samples)<1e-5,'No pull-back during the sign-to-door shot'
        assert abs(samples[-1]['camera_position'][1]+1.4)<1e-5
        assert abs(samples[0]['camera_position'][2]-samples[-1]['camera_position'][2]-.45)<1e-5
        return dict(close_distance_m=1.4,downward_travel_m=.45,no_pullback=True)
    return None


def table_physics(scene, samples, guide_id):
    """Check the actual animated meshes, not just the builder's declared contacts."""
    drinks=[o for o in scene.objects if 'cocktail_index' in o]
    if not drinks:return None
    orientations={};previous_props=None
    for sample in samples:
        if sample['phase']!='demonstration':continue
        scene.frame_set(sample['frame']);bpy.context.view_layer.update()
        if guide_id=='pancake_clear_path':
            hands=[o for o in scene.objects if o.get('p0_hand')]
            assert len(hands)==2 and sorted(o['p0_entry_side'] for o in hands)==[-1,1]
            left=next(o for o in hands if o['p0_entry_side']==-1);right=next(o for o in hands if o['p0_entry_side']==1)
            salad=bpy.data.objects['Sliding salad and plate']
            assert left.matrix_world.translation.x<.14+salad.location.x-.05,'Left hand stays outside the left rim'
            assert right.matrix_world.translation.x>.21,'Right hand stays on the right side'
            props=[d.location.x for d in sorted(drinks,key=lambda o:o['cocktail_index'])]+[salad.location.x]
            if previous_props is not None:
                assert props[0]>=previous_props[0]-1e-5 and props[1]>=previous_props[1]-1e-5,'Drinks are pulled right, never pushed left'
                assert props[2]<=previous_props[2]+1e-5,'Salad is pulled left, never pushed right'
            previous_props=props
        for drink in drinks:
            assert abs(drink.matrix_world.translation.z-.785)<1e-5,'Glass base must stay on the tabletop'
            inverse=drink.matrix_world.inverted()
            cubes=[o for o in drink.children_recursive if o.get('ice_cube')]
            assert len(cubes)==3
            centers=[];radii=[]
            for cube in cubes:
                points=[inverse@(cube.matrix_world@v.co) for v in cube.data.vertices]
                center=inverse@cube.matrix_world.translation
                centers.append(center);radii.append(max((v-center).length for v in points))
                for p in points:
                    assert .014<p.z<.19,'Ice must remain above the floor and below the rim'
                    inner_radius=.034+(p.z-.014)*(.006/.176)
                    assert math.hypot(p.x,p.y)<inner_radius,'Ice must not cross the glass wall'
                orientations.setdefault(cube.name,[]).append(tuple(cube.rotation_euler))
            assert all((centers[i]-centers[j]).length>radii[i]+radii[j] for i in range(3) for j in range(i)),'Ice cubes must remain separated'
        for hand in [o for o in scene.objects if o.get('p0_grip_style')=='vertical_side_grip']:
            normal=hand.matrix_world.to_3x3()@Vector((0,0,1))
            assert abs(normal.z)<.01,'Glass grips must be side-on rather than palm up'
            if guide_id=='glass_slide_close':
                mesh=next(o for o in hand.children_recursive if o.type=='MESH')
                palm=mesh.matrix_world@Vector(json.loads(mesh['landmarks'])['hand'])
                assert palm.y>drinks[0].matrix_world.translation.y+.015,'Palm should grip from the back side of the glass'
        # Resting bases, rather than overhanging plate rims, must be supported.
        for obj in scene.objects:
            if obj.type!='MESH' or not (obj.name.startswith('Plate with formed rim') or obj.name.startswith('Broad flat serving plate')):continue
            z=min(v.co.z for v in obj.data.vertices)
            if guide_id=='table_spread_orbit':
                for vertex in obj.data.vertices:
                    p=obj.matrix_world@vertex.co
                    assert math.hypot(p.x-.14,p.y-.18)<.65-.06,'Every plate rim needs at least 6 cm from the table edge'
            for vertex in obj.data.vertices:
                if vertex.co.z>z+.0001:continue
                p=obj.matrix_world@vertex.co
                assert abs(p.z-.785)<1e-5,'Plate bases must stay on the tabletop'
                if guide_id=='pancake_clear_path':assert abs(p.x)<.7 and -.775<p.y<1.875
                else:
                    center=Vector((.14,.18,0)) if guide_id=='table_spread_orbit' else Vector((.12,.20,0))
                    assert math.hypot(p.x-center.x,p.y-center.y)<.65
    assert all(len(set(values))>10 for values in orientations.values()),'Ice should visibly rotate through the take'
    return dict(glasses_supported=True,plate_bases_supported=True,ice_inside_glass=True,
                ice_cubes_separated=True,ice_rotates=True,glasses=len(drinks),
                plate_rim_margin_6cm=guide_id=='table_spread_orbit',opposite_side_outward_pulls=guide_id=='pancake_clear_path')


def run():
    root = Path(__file__).resolve().parents[2]
    plan = json.loads((root / 'guides/p0/plan.json').read_text())
    results = []
    for record in plan['guides']:
        if record.get('availability') in ('deferred','archived'):continue
        folder = root / 'catalog/p0/animations-light' / record['id']
        meta = json.loads((folder / 'meta.json').read_text())
        bpy.ops.wm.open_mainfile(filepath=str(folder / 'scene.blend'))
        scene = bpy.context.scene
        assert scene.frame_end == meta['frame_count']
        assert scene.render.fps == 15 and scene.render.film_transparent
        meshes = [o for o in scene.objects if o.type == 'MESH']
        assert meshes and all(o.hide_render for o in meshes)
        assert any(o.type == 'GREASEPENCIL' and not o.hide_render for o in scene.objects)
        hands = [o for o in scene.objects if o.get('p0_hand')]
        if record.get('allowedPeople'):
            rigs=[o for o in scene.objects if o.type=='ARMATURE']
            assert len(rigs)==1 and meta['maximum_hands']==2 and meta['detailed_people']==1
            assert all(any(b.name.endswith(side+'Hand') for b in rigs[0].pose.bones) for side in ['Left','Right'])
            assert not hands,'No detached replacement hand is allowed on a canonical character'
        else:assert len(hands) == meta['maximum_hands'] <= 2
        lights = [o for o in scene.objects if o.type == 'LIGHT']
        assert lights and all(o.animation_data is None and o.data.animation_data is None for o in lights)
        camera = scene.camera
        previous = None
        max_turn = 0.
        resting_transforms = None
        for sample in meta['camera_samples']:
            scene.frame_set(sample['frame'])
            assert (camera.location - Vector(sample['camera_position'])).length < 1e-5
            rotation = camera.rotation_quaternion
            assert rotation.rotation_difference(Quaternion(sample['camera_rotation_quaternion'])).angle < .001
            assert camera.data.lens == sample['lens_mm'] == (18 if record.get('allowedPeople') and record['camera']=='front' else 24)
            if sample['phase'] == 'demonstration':
                if record['id'] in ['handoff_counter_cup','handoff_plate_lands']:
                    transforms={o.name:tuple(v for row in o.matrix_world for v in row) for o in meshes}
                    if resting_transforms is None:resting_transforms=transforms
                    else:assert all(max(abs(a-b) for a,b in zip(values,resting_transforms[name]))<1e-5 for name,values in transforms.items()),'Served objects must stay on their support'
                if previous is not None:
                    angle = math.degrees(rotation.rotation_difference(previous).angle)
                    max_turn = max(max_turn, min(angle, 360 - angle) * 15)
                previous = rotation.copy()
        assert max_turn < 120, (record['id'], max_turn)
        pour_checks=None
        if record['id'].startswith('pour_'):
            stream=next(o for o in meshes if o.name.startswith('Milk stream /'))
            pivot=bpy.data.objects['Pitcher spout pivot']
            samples=[s for s in meta['camera_samples'] if s['phase']=='demonstration']
            def stream_vertices(sample):
                scene.frame_set(sample['frame']);bpy.context.view_layer.update()
                evaluated=stream.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
                points=[stream.matrix_world@v.co for v in mesh.vertices];evaluated.to_mesh_clear();return points
            for sample in [samples[0],samples[-1]]:
                points=stream_vertices(sample)
                assert max((v-points[0]).length for v in points)<1e-5,'Flow must be absent before tilting and after the last drop lands'
                assert abs(pivot.rotation_euler.y)<1e-5,'Pitcher starts and ends upright'
            points=stream_vertices(samples[len(samples)//2])
            assert min(v.z for v in points)<max(v.z for v in points)-.07
            assert max(v.x for v in points)-min(v.x for v in points)<.006
            assert max(v.y for v in points)-min(v.y for v in points)<.006
            assert pivot.rotation_euler.y>math.radians(25),'Tilt the pitcher toward the cup during the pour'
            contact=next(c for c in meta['pre_render_review']['contacts'] if c['kind']=='stream')
            vessel=next(o for o in scene.objects if 'spout_local' in o)
            assert (vessel.matrix_world@Vector(vessel['spout_local'])-Vector(contact['source'])).length<1e-4,'Stream must stay attached to the reused vessel outlet'
            assert abs(min(v.z for v in points)-contact['receiver'][2])<.004
            assert abs(max(v.z for v in points)-contact['source'][2])<.004
            pour_checks=dict(vertical_stream_in_saved_geometry=True,starts_and_ends_dry=True,tilts_toward_cup=True,actual_vessel_outlet_connected=True)
        table_checks=table_physics(scene,meta['camera_samples'],record['id'])
        layout_checks=requested_scene_layout(scene,meta,record['id'])
        results.append(dict(id=record['id'], status='passed', frames=scene.frame_end,
                            source_meshes_hidden=True, fixed_lights=len(lights), hands=meta['maximum_hands'],detached_hand_models=len(hands),
                            maximum_camera_turn_degrees_s=round(max_turn, 3),pour=pour_checks,table=table_checks,layout=layout_checks,
                            served_objects_stay_on_support=resting_transforms is not None))
    report = dict(status='passed', scenes=len(results), records=results,
                  blender_version=bpy.app.version_string, saved_scene_camera_matches_metadata=True)
    (root / 'catalog/p0/saved-scene-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'records'}))


if __name__=='__main__':run()
