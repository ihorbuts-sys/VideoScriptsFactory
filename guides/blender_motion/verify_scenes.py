"""Check source-prescribed camera geometry and fixed lighting in saved scenes."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/"catalog/blender-animations"
args=sys.argv[sys.argv.index("--")+1:]
results=[]
for gid in args:
    folder=OUT/gid;spec=json.loads((folder/"scene-spec.json").read_text())
    bpy.ops.wm.open_mainfile(filepath=str(folder/"scene.blend"))
    scene=bpy.data.scenes["01 Ghost contours"];bpy.context.window.scene=scene
    camera=bpy.data.objects[spec["camera_stages"][0]["name"]]
    positions=[];rotations=[];projections=[];meshes=[]
    focus=Vector((0,0,.854)) if gid=="cup_eye_orbitr_cc" else Vector((0,0,.825)) if gid=="plate_high_orbitl_cc" else None
    for frame in [1,round(scene.frame_end*.25),round(scene.frame_end*.50),round(scene.frame_end*.75),scene.frame_end]:
        scene.frame_set(frame);bpy.context.view_layer.update()
        positions.append(tuple(camera.location));rotations.append(tuple(camera.rotation_euler))
        meshes.append({o.name:tuple(round(v,6) for row in o.matrix_world for v in row) for o in scene.objects if o.type=="MESH"})
        if focus is not None:
            projected=world_to_camera_view(scene,camera,focus);projections.append((projected.x,projected.y))
    assert all(m==meshes[0] for m in meshes),"Simple camera shots must not deform or slide their subjects"
    assert camera.data.animation_data is None,"Lens must stay fixed"
    assert not any(o.type=="MESH" and "wall" in o.name.lower() for o in scene.objects)
    lights=[o for o in scene.objects if o.type=="LIGHT"]
    assert lights and all(o.animation_data is None and o.data.animation_data is None for o in lights)
    source=json.loads((BASE/"guides/templates"/(gid+".json")).read_text())
    orbit=next((step for step in source["live"]["steps"] if step.get("action")=="orbit"),None)
    facts=dict(geometry_stationary=True,lens_fixed=True,lighting_fixed=True,light_count=len(lights),walls_omitted=True,
               visible_hand_roots=sum(o.name.startswith("One hand") for o in scene.objects),
               pre_render_review=spec["pre_render_review"]["status"],physical_contacts=spec.get("physical_contact_checks",[]))
    assert facts["visible_hand_roots"]<=2
    if orbit:
        angles=[math.degrees(math.atan2(p[0],-p[1])) for p in positions]
        arc=angles[-1]-angles[0];expected=orbit["arc"]*(1 if orbit["direction"]=="right" else -1)
        assert abs(arc-expected)<.02,(gid,arc,expected)
        radii=[math.hypot(p[0],p[1]) for p in positions]
        assert max(radii)-min(radii)<1e-5
        error=max(max(abs(x-.5),abs(y-.5)) for x,y in projections)
        assert error<.001,"Orbit's composition centre must stay stable"
        facts.update(orbit_arc_deg=arc,orbit_radius_m=radii[0],focal_centre_max_error=error)
    elif "truck" in gid:
        assert max(abs(v-rotations[0][i]) for r in rotations for i,v in enumerate(r))<1e-6
        direction=1 if "truckr" in gid else -1
        assert (positions[-1][0]-positions[0][0])*direction>0
        facts["orientation_constant_during_truck"]=True
    elif gid=="plate_spread_top_out_cw":
        assert all(abs(p[0]-positions[0][0])<1e-6 and abs(p[1]-positions[0][1])<1e-6 for p in positions)
        assert positions[-1][2]>positions[0][2]
        direction=camera.matrix_world.to_quaternion()@Vector((0,0,-1))
        assert direction.z<-.9999
        table=next(o for o in scene.objects if o.name.startswith("Quiet tabletop"))
        points=[world_to_camera_view(scene,camera,table.matrix_world@v.co) for v in table.data.vertices]
        assert all(0<=p.x<=1 and 0<=p.y<=1 for p in points),"Whole table must fit in the finishing frame"
        facts["whole_table_fits_finishing_frame"]=True
    elif gid=="menu_board_low_tiltd_mm":
        assert all((Vector(p)-Vector(positions[0])).length<1e-6 for p in positions)
        pitches=[]
        for r in rotations:
            from mathutils import Euler
            direction=Euler(r).to_quaternion()@Vector((0,0,-1))
            pitches.append(math.degrees(math.atan2(direction.z,math.hypot(direction.x,direction.y))))
        assert pitches[0]>20 and pitches[-1]<-20
        facts.update(tilt_start_deg=pitches[0],tilt_end_deg=pitches[-1],source_hold_tilt_conflict_requires_integration_fix=True)
    elif gid in ["plate_low_in_mc","menu_schedule_eye_in_mc","menu_event_low_in_cd","menu_hours_low_out_dc","menu_score_low_out_dc"]:
        source_move=next(step for step in source["live"]["steps"] if step.get("action") in ["dolly_in","dolly_out"])
        focus=Vector((0,-.36,.845)) if gid=="plate_low_in_mc" else Vector((.02 if "_out_" in gid else -.02,.35,1.755))
        distances=[(Vector(p)-focus).length for p in positions]
        ratio=distances[0]/distances[-1]
        assert abs(ratio-source_move["amount"])<.002,(gid,ratio,source_move["amount"])
        assert max(abs(v-rotations[0][i]) for r in rotations for i,v in enumerate(r))<1e-6
        facts.update(source_scale_factor=source_move["amount"],actual_scale_factor=ratio,orientation_constant=True)
        if gid.startswith("menu_"):
            chosen=[o for o in scene.objects if o.type=="MESH" and o.name.startswith("Menu resource lettering") and abs(o.location.z-.055)<.001]
            points=[world_to_camera_view(scene,camera,o.matrix_world@v.co) for o in chosen for v in o.data.vertices]
            assert points and all(.015<p.x<.985 and .25<p.y<.75 for p in points),"Selected resource fields must fit the useful recording band"
            facts["selected_resource_fields_fit_recording_band"]=True
            if "_out_" in gid:
                lower=[o for o in scene.objects if o.type=="MESH" and o.name.startswith("Menu resource lettering") and o.location.z<-.1]
                points=[world_to_camera_view(scene,camera,o.matrix_world@v.co) for o in lower for v in o.data.vertices]
                assert all(.01<p.x<.99 and .25<p.y<.75 for p in points),"All revealed rows must fit above the recording controls"
                facts["all_revealed_rows_above_controls"]=True
    facts.update(id=gid,status="passed",scope="Reusable base shot; contextual handover remains pending")
    (folder/"geometry-checks.json").write_text(json.dumps(facts,indent=2)+"\n")
    results.append(facts)
(OUT/"geometry-checks.json").write_text(json.dumps(results,indent=2)+"\n")
print("VERIFIED_BASE_SHOTS",len(results))
