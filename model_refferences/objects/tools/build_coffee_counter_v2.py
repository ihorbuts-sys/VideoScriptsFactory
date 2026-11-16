"""Place the reconstructed coffee kit in one usable scene and animate extraction.

This is a scene/contact proof, not a replacement for the five-step first-visit
script. Its camera stays in the visitor aisle throughout.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
import prepare_creator_tripo as B
from prepare_rigged_characters import named
from prepare_coffee_functional import circle
from coffee_scene_details import environment, Grip, outlets, polish_practicals

OUT = P.BASE / 'catalog/coffee-ordering-v2'
FPS = 15
COUNT = 240


def remove(root):
    for item in list(root.children_recursive)[::-1] + [root]:
        bpy.data.objects.remove(item, do_unlink=True)


def anchor(root, function):
    item = next(o for o in root.children_recursive if o.get('function') == function)
    return item.matrix_world.translation.copy()


def set_anchor(root, function, target):
    bpy.context.view_layer.update()
    root.location += Vector(target) - anchor(root, function)
    bpy.context.view_layer.update()


def add_cast(aid, location, turn):
    source = P.ROOT.parent / aid / 'tripo-rigged/review/asset.blend'
    with bpy.data.libraries.load(str(source), link=False) as (src, dst):
        dst.collections = [src.collections[0]]
    collection = dst.collections[0]
    bpy.context.scene.collection.children.link(collection)
    members = set(collection.objects)
    roots = [o for o in members if o.parent not in members]
    assert len(roots) == 1
    placement = P.empty('Cast placement / ' + aid, location)
    placement.rotation_euler.z = turn
    roots[0].parent = placement
    placement['asset_family'] = aid
    placement['source_file'] = str(source.relative_to(P.BASE))
    C.role(placement, 'support')
    arm = next(o for o in placement.children_recursive if o.type == 'ARMATURE')
    return placement, arm


def linear_actions():
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'native-ready.json').unlink(missing_ok=True)
    scene, baseline = C.setup('cafe', OUT, full_height=True)
    scene.name = 'Loca / coffee ordering / extraction contact proof'
    scene.frame_end = COUNT
    camera = scene.camera
    camera.animation_data_clear()
    counter = next(o for o in scene.objects if o.get('asset_family') == 'bar_counter')
    counter.location.y = 4.0
    counter.scale.x = 1.12
    counter.scale.y = .70
    counter.scale.z = .68
    bpy.context.view_layer.update()
    # Remove the previous placeholder service props before placing the real kit.
    placeholders = [root for root in scene.objects
                    if root.get('asset_family') in ['kettle', 'latte_cup'] and root.location.y > 4]
    for root in placeholders:
        remove(root)
    C.CONTACTS.clear()
    dressing = environment(scene)
    menu = next(o for o in scene.objects if o.get('asset_family') == 'menu_board')
    menu.location = (-.035, 5.12, 2.25)
    polish_practicals(scene)
    machine = C.supported('espresso_machine', counter, .60, 4.10,
                          turn=math.pi / 2, quality='functional')
    grinder = C.supported('coffee_grinder', counter, .0, 4.10, quality='functional')
    pitcher = C.supported('milk_pitcher', counter, .99, 4.27, turn=math.pi/2, quality='functional')
    for aid, x in [('coffee_tamper', .20), ('knock_box', -.26)]:
        if (P.ROOT / aid / 'tripo-generated/review/asset.blend').exists():
            tool = C.supported(aid, counter, x, 4.13)
            C.role(tool, 'context')
    tray = C.supported('serving_tray', counter, -.83, 3.80)
    takeaway = C.supported('takeaway_cup', tray, -.83, 3.80)
    box = C.supported('pastry_box', counter, -.82, 4.19)
    for x in [-.89, -.75]:
        C.supported('croissant', box, x, 4.16, scale=.72, quality='approved-v2')
    rack = C.load('pastry_rack', (1.90, 4.10, 0))
    rack_lo, rack_hi = B.bounds(C.meshes(rack))
    for ratio in [.20, .43, .65, .87]:
        for x in [1.73, 1.90, 2.07]:
            z = C.surface(rack, x, 4.10, from_z=rack_hi.z * ratio)
            pastry = C.load('croissant', (x, 4.10, 0), scale=.72, quality='approved-v2')
            pastry_lo, pastry_hi = B.bounds(C.meshes(pastry))
            pastry.location.z += z - pastry_lo.z + .0005
            C.role(pastry, 'context')
    for obj in [rack, tray, takeaway, box]:
        C.role(obj, 'context')
    socket = anchor(machine, 'socket')
    portafilter = C.load('portafilter', turn=0, quality='functional')
    # Fit the basket alone: including the handle skews the mouth centre.
    bottom = anchor(portafilter, 'spout')
    verts = [o.matrix_world @ v.co for o in C.meshes(portafilter) for v in o.data.vertices]
    highest = max(p.z for p in verts)
    basket = [p for p in verts if p.z > highest * .94 and (p.xy - bottom.xy).length < .044]
    centre, radius = circle(basket)
    centre.z = highest
    marker = next(o for o in portafilter.children_recursive if o.get('function') == 'rim')
    marker.location = marker.parent.matrix_world.inverted() @ centre
    bpy.context.view_layer.update()
    # Find the real underside of the group instead of using a material centroid.
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in C.meshes(machine):
        evaluated = obj.evaluated_get(deps)
        inverse = evaluated.matrix_world.inverted()
        origin = Vector((socket.x, socket.y, machine.location.z + .17))
        hit, point, normal, index = evaluated.ray_cast(inverse @ origin, inverse.to_3x3() @ Vector((0, 0, 1)))
        if hit:
            world_normal = evaluated.matrix_world.to_3x3().inverted().transposed() @ normal
            if world_normal.z < -.35:
                socket.z = (evaluated.matrix_world @ point).z
    set_anchor(portafilter, 'rim', socket + Vector((0, 0, .001)))
    discharge = outlets(portafilter)
    outlet = (discharge[0][0] + discharge[1][0]) / 2
    cup = C.load('latte_cup', turn=-math.pi / 4, scale=.67, quality='functional')
    cup.scale.x = cup.scale.y = .72
    # The support ray begins below the group head and finds the actual drip tray.
    tray_z = max(C.surface(machine, outlet.x+dx, outlet.y+dy, from_z=socket.z-.09)
                 for dx, dy in [(0, 0), (-.020, 0), (.020, 0), (0, -.020), (0, .020),
                                (-.014, -.014), (.014, .014), (-.014, .014), (.014, -.014)])
    cup_rim = anchor(cup, 'rim')
    riser = P.lathe('Machine / low cup support', [(0, 0), (.032, 0), (.034, .003),
        (.032, .006), (0, .006)], (outlet.x, outlet.y, tray_z), 'charcoal')
    riser['asset_family'] = 'cup_riser_local'
    riser.color = (.015, .18, 0, 1)
    cup.location += Vector((outlet.x - cup_rim.x, outlet.y - cup_rim.y, tray_z + .0065))
    bpy.context.view_layer.update()
    rim = anchor(cup, 'rim')
    lo, hi = B.bounds(C.meshes(cup))
    assert abs(lo.z - tray_z - .0065) < .001
    assert rim.z < min(p.z for p, sign in discharge) - .007, ('Cup intersects spout', list(rim), list(outlet))
    C.CONTACTS.append(dict(asset='latte_cup', support='espresso_machine/6mm_cup_riser',
        surface_z=tray_z+.006, lowest_vertex_z=lo.z, centre_contact_error_m=abs(lo.z - tray_z-.006)))
    coffee = P.lathe('Coffee / rising real liquid surface',
        [(0, -.002), (.030, -.002), (.030, 0), (0, 0)],
        (rim.x, rim.y, lo.z + .015), 'coffee')
    coffee['asset_family'] = 'espresso_liquid_local'
    streams = []
    for i, (point, outward) in enumerate(discharge):
        stream = P.tube('Espresso / real outlet ' + str(i+1),
            [(0, 0, 0), (-outward.x*.0015, -outward.y*.0015, -.15),
             (-outward.x*.004, -outward.y*.004, -1)], .0012, 'coffee')
        stream['asset_family'] = 'espresso_stream_local'
        streams.append(stream)
    barista, arm = add_cast('barista', (.85, 4.60, 0), 0)
    bpy.context.view_layer.update()
    head = named(arm, 'Head')
    chest = named(arm, 'Spine2')
    head_axis = (arm.matrix_world @ head.bone.matrix_local).to_3x3().inverted() @ Vector((0, 0, 1))
    head_tilt_axis = (arm.matrix_world @ head.bone.matrix_local).to_3x3().inverted() @ Vector((1, 0, 0))
    chest_axis = (arm.matrix_world @ chest.bone.matrix_local).to_3x3().inverted() @ Vector((1, 0, 0))
    grip = Grip(arm, side='Left')
    pitcher_rim = anchor(pitcher, 'rim')
    rough_grip = anchor(pitcher, 'grip')
    handle_direction = rough_grip-pitcher_rim
    handle_direction.z = 0
    handle_direction.normalize()
    points = np.array([o.matrix_world @ v.co for o in C.meshes(pitcher) for v in o.data.vertices])
    band = points[np.abs(points[:, 2]-rough_grip.z) < .018]
    projections = band[:, :2] @ np.array(handle_direction[:2])
    outer = band[projections > np.quantile(projections, .95)]
    hand_target = Vector(np.mean(outer, axis=0).tolist())
    hand_target.z = rough_grip.z
    pitcher_lo, pitcher_hi = B.bounds(C.meshes(pitcher))
    milk = P.lathe('Pitcher / milk ready for steaming', [(0, -.002), (.038, -.002), (.038, 0), (0, 0)],
        (pitcher_rim.x, pitcher_rim.y, pitcher_lo.z+.130), 'cream')
    milk.color = (.050876, 1, 0, 1)
    milk['asset_family'] = 'milk_liquid_local'
    for root in [machine, grinder, pitcher]:
        C.role(root, 'support')
    for root in [cup, portafilter, pitcher]:
        C.role(root, 'hero')
    for point, outward in discharge:
        arrival = point-outward*.004
        assert (arrival.xy-rim.xy).length < .030*.82+.002, ('Stream misses the coffee surface', list(arrival), list(rim))
    for obj in [coffee, *streams]:
        obj.color = (0.050876, 1, 0, 1)
        obj['guide_role'] = 'hero'
    # No invented moving practical lights. Reflections change with the phone.
    camera.data.lens = 32
    camera.data.clip_start = .025
    camera.data.dof.use_dof = False
    cx, cy, cz = rim
    positions = [(0, (1.90, 1.2, 1.60)), (2, (1.85, 2.0, 1.54)),
        (4, (1.70, 2.75, 1.38)), (6, (1.50, 3.20, 1.24)),
        (9, (1.15, 3.46, 1.22)), (12, (1.10, 3.46, 1.40)),
        (16, (1.40, 3.15, 1.52))]
    shared_target = ((cx+pitcher_rim.x)/2, (cy+pitcher_rim.y)/2, cz+.025)
    targets = [(0, (.65, 4.40, 1.45)), (2, (.85, 4.40, 1.40)),
        (5, shared_target), (9, (cx, cy, cz + .005)),
        (12, (cx, cy, cz - .015)), (16, shared_target)]
    lenses = [(0, (18, 0, 0)), (2, (25, 0, 0)), (4, (36, 0, 0)), (9, (62, 0, 0)),
              (12, (62, 0, 0)), (16, (40, 0, 0))]
    previous = rotation_previous = None
    maximum_speed = maximum_turn = 0
    records = []
    grip_checks = []
    for frame in range(1, COUNT + 1):
        t = (frame - 1) / FPS
        p = C.cubic(positions, t)
        target = C.cubic(targets, t)
        p.z += .0015 * math.sin(t * 2.1)
        rotation = (target - p).to_track_quat('-Z', 'Y')
        if rotation_previous and rotation_previous.dot(rotation) < 0:
            rotation.negate()
        camera.location = p
        camera.rotation_mode = 'QUATERNION'
        camera.rotation_quaternion = rotation
        camera.data.lens = C.cubic(lenses, t).x
        camera.keyframe_insert('location', frame=frame)
        camera.keyframe_insert('rotation_quaternion', frame=frame)
        camera.data.keyframe_insert('lens', frame=frame)
        fill = C.smooth(t, 4.0, 11.5)
        liquid_z = lo.z + .015 + .034 * fill
        coffee.location.z = liquid_z
        coffee.scale.x = coffee.scale.y = .82 + .18 * fill
        coffee.keyframe_insert('location', frame=frame)
        coffee.keyframe_insert('scale', frame=frame)
        for i, (stream, (point, sign)) in enumerate(zip(streams, discharge)):
            stream.location = point
            stream.scale.z = max(.001, point.z - liquid_z)
            flow = C.smooth(t, 3.9+i*.07, 4.4+i*.07) * (1 - C.smooth(t, 11.2+i*.05, 11.8+i*.05))
            stream.scale.x = stream.scale.y = max(.0001, flow)
            stream.keyframe_insert('location', frame=frame)
            stream.keyframe_insert('scale', frame=frame)
        head.rotation_mode = chest.rotation_mode = 'QUATERNION'
        # Quiet acknowledgement, then attention to the cup. Hands remain neutral.
        head.rotation_quaternion = Quaternion(head_axis, math.radians(12 - 24 * C.smooth(t, 2, 5))) @ Quaternion(head_tilt_axis, math.radians(6 * C.smooth(t, 2, 5)))
        chest.rotation_quaternion = Quaternion(chest_axis, .006 * math.sin(t * 1.35))
        head.keyframe_insert('rotation_quaternion', frame=frame)
        chest.keyframe_insert('rotation_quaternion', frame=frame)
        bpy.context.view_layer.update()
        grip_checks.append(grip.pose(hand_target, frame, forward=-handle_direction,
                                    across=Vector((0, 0, 1)), wrist_offset=.075))
        if previous is not None:
            maximum_speed = max(maximum_speed, (p - previous).length * FPS)
            maximum_turn = max(maximum_turn, math.degrees(rotation_previous.rotation_difference(rotation).angle) * FPS)
        previous, rotation_previous = p.copy(), rotation.copy()
        assert p.y < 3.50, ('Phone entered service area', frame)
        assert liquid_z < rim.z - .01
        records.append(dict(frame=frame, position=list(p), target=list(target),
            liquid_z=liquid_z, spout=list(outlet), stream_inside_cup=True))
    assert maximum_speed < .45, maximum_speed
    assert maximum_turn < 45, maximum_turn
    linear_actions()
    for label, frame in [('Order / establish the counter', 1), ('Follow the same machine', 61),
                         ('Espresso reaches the cup', 91), ('Rise around the cup', 151)]:
        scene.timeline_markers.new(label, frame=frame)
    scene.frame_set(1)
    scene.render.fps = FPS
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.eevee.taa_render_samples = 32
    spec = dict(id='coffee-ordering-extraction-proof', venue='coffee',
        title='Coffee ordering / counter to espresso', status='probes_pending',
        fps=FPS, frame_count=COUNT, duration_s=COUNT / FPS,
        scope='coffee_counter_and_extraction_contact_proof',
        handover_status='one_continuous_camera_in_one_scene', human_performance_included=True,
        human_action='Barista behind the counter, left hand holding the milk pitcher while espresso brews; right arm rests clear of the machine.',
        grip_hand='Left', grip_object='milk_pitcher', portafilter_rotation_change_deg=-90,
        grip_checks=grip_checks, dressing=dressing,
        revision='coffee-left-milk-smooth-v3', ghost_style='smooth-contours-v1',
        source_guide='cup_shot_eye_in_cd_through', canonical_guide_replaced=False,
        guide_difference='Adds an establishing counter view and a rising phone arc; canonical script montage remains unchanged.',
        assets=sorted({o.get('asset_family') for o in scene.objects if o.get('asset_family')}),
        probe_frames=[1, 31, 61, 91, 121, 151, 181, 211, 240],
        camera=dict(visitor_side_only=True, max_speed_m_s=maximum_speed,
                    max_angular_speed_deg_s=maximum_turn, samples=records),
        contacts=list(C.CONTACTS), cup_rim=list(rim), spout=list(outlet),
        outlets=[list(point) for point, sign in discharge], cup_lift_m=.006,
        cup_type='60-mm-high espresso demitasse adapted from the same ceramic cup',
        whole_overlay_alpha=.65, viewfinder_embedded=False, walls_absent_in_ghost=True,
        full_script_sequence_complete=False, published=False,
        composition=['Menu and operator establish the order before the detail',
            'Counter and machine form distinct foreground and background planes',
            'Short diagonal approach becomes a small rising arc around the same cup',
            'Fixed window light; no bloom or moving fixtures'],
        lighting='Fixed morning sun and broad window key',
        mobile='Stay in the public aisle, lean toward the visible machine, then raise the phone slightly.',
        phases=[dict(id='order', start_s=0, end_s=4),
                dict(id='extraction', start_s=4, end_s=12),
                dict(id='cup-detail', start_s=12, end_s=16)])
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'scene.blend'), compress=True)
    (OUT / 'scene-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    (OUT / 'native-ready.json').write_text(json.dumps(dict(status='ready', revision='left-milk')) + '\n')
    print('COFFEE_SCENE_BUILT', json.dumps(dict(cup_rim=list(rim), spout=list(outlet),
        tray_z=tray_z, contact_error_m=abs(lo.z-tray_z), maximum_speed=maximum_speed)), flush=True)
    return scene, spec


def render(scene, spec, probes):
    numbers = spec['probe_frames'] if probes else range(1, COUNT + 1)
    C.render(scene, OUT, spec, probes=probes, frames=numbers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--probes', action='store_true')
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.resume:
        bpy.ops.wm.open_mainfile(filepath=str(OUT / 'scene.blend'))
        scene = bpy.context.scene
        spec = json.loads((OUT / 'scene-spec.json').read_text())
        P.MATS.clear()
        scene.frame_set(1)
        polish_practicals(scene)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'scene.blend'), compress=True)
        (OUT / 'native-ready.json').write_text(json.dumps(dict(status='ready', revision='v2')) + '\n')
    else:
        scene, spec = build()
    if not args.build_only:
        render(scene, spec, args.probes)
