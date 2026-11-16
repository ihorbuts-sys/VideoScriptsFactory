"""Verify actual saved scene contacts and phone-feasible continuous camera motion."""
import bpy,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_reconstructed_scene as C

def run(gid):
    out=C.BASE/'catalog/clay-scenes'/gid
    bpy.ops.wm.open_mainfile(filepath=str(out/'scene.blend'))
    scene=bpy.context.scene;spec=json.loads((out/'scene-spec.json').read_text());scene.frame_set(1)
    deps=bpy.context.evaluated_depsgraph_get();contacts=[]
    for contact in spec.get('contacts',[]):
        if not isinstance(contact,dict):continue
        roots=[o for o in scene.objects if o.get('asset_id')==contact['asset']]
        position=contact['position'];root=min(roots,key=lambda o:sum((o.location[i]-position[i])**2 for i in range(3)))
        assert sum((root.location[i]-position[i])**2 for i in range(3))<1e-6
        base=min((o.evaluated_get(deps).matrix_world@v.co).z for o in C.meshes(root) for v in o.evaluated_get(deps).data.vertices)
        error=abs(base-position[2]);assert error<.002,(root.name,'Unsupported object',error)
        contacts.append(dict(asset=contact['asset'],support=contact['support'],base_z=base,support_z=position[2],error_m=error))
    old_pos=None;old_rot=None;max_speed=0;max_turn=0
    for frame in range(scene.frame_start,scene.frame_end+1):
        scene.frame_set(frame);position=scene.camera.matrix_world.translation.copy();rotation=scene.camera.matrix_world.to_quaternion()
        assert position.y<-.85,'Camera enters staff area'
        if old_pos is not None:max_speed=max(max_speed,(position-old_pos).length*scene.render.fps)
        if old_rot is not None:max_turn=max(max_turn,math.degrees(old_rot.rotation_difference(rotation).angle)*scene.render.fps)
        old_pos=position;old_rot=rotation
    assert max_speed<.8,(max_speed,'Excessive phone speed');assert max_turn<90,(max_turn,'Abrupt turn')
    report=dict(status='passed',scene=gid,contacts=contacts,contact_tolerance_m=.002,
        max_camera_speed_m_s=max_speed,max_camera_turn_deg_s=max_turn,visitor_side_only=True,
        one_camera_continuous_world=True,frames=scene.frame_end-scene.frame_start+1,
        limitations=['Reference fidelity remains a visual review','No collision simulation or real-phone trial was performed'])
    (out/'scene-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RECONSTRUCTED_SCENE_CHECKS_PASSED',len(contacts),max_speed,max_turn)

if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
