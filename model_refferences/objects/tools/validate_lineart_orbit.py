"""Check actual contour pixels plus the smooth physical orbit and coffee occlusion."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from validate_lineart import validate


def run(folder):
    alpha=validate(folder);m=json.loads((folder/'meta.json').read_text());p=m['camera_profile'];rows=m['frames']
    center=np.asarray(m['object_bbox_world']['center']);xyz=np.asarray([r['camera_position'] for r in rows]);relative=xyz-center
    distance=np.linalg.norm(relative,axis=1);pitch=np.degrees(np.arcsin(relative[:,2]/distance));yaw=np.degrees(np.arctan2(relative[:,0],-relative[:,1]))
    assert np.ptp(distance)<2e-6,'Radius changed during orbit'
    assert np.max(np.abs(pitch-[r['pitch_degrees'] for r in rows]))<1e-4
    assert np.max(np.abs(yaw-[r['azimuth_degrees'] for r in rows]))<1e-4
    assert abs(yaw[-1]-yaw[0]-p['arc_degrees'])<1e-4
    assert np.all(xyz[:,1]<center[1]),'Camera moves behind the cup'
    assert all(r['fits_frame'] for r in rows)
    if p['profile']=='steady':assert np.max(np.abs(pitch-45))<1e-4
    else:
        assert abs(pitch.min()-37)<.02 and abs(pitch.max()-53)<.02
        assert abs(pitch[0]-45)<1e-4 and abs(pitch[-1]-45)<1e-4
    velocity=np.diff(xyz,axis=0)*m['fps'];acceleration=np.diff(velocity,axis=0)*m['fps']
    speed=np.linalg.norm(velocity,axis=1);accel=np.linalg.norm(acceleration,axis=1)
    assert speed.max()<.3 and accel.max()<.3,'Abrupt physical camera motion'
    lead=p['initial_drawing_hold_through'];hashes=[]
    for n in range(1,lead+1):
        with Image.open(folder/f'frame_{n:04d}.png') as image:hashes.append(hashlib.sha256(image.tobytes()).hexdigest())
    assert len(set(hashes))==1,'Opening pose jitters'
    coffee=p['coffee'];assert coffee['heart'] and coffee['opening_occlusion_check']=='passed' and coffee['opening_occlusion_rays']>=100
    assert not coffee['source_faces_rendered']
    assert hashlib.sha256(Path(m['model']).read_bytes()).hexdigest()==m['model_sha256'],'Input model changed'
    report=dict(status='passed',profile=p['profile'],frames=len(rows),seconds=len(rows)/m['fps'],
        line_only_alpha=alpha['no_broad_filled_regions'],visible_motion=alpha['visible_motion'],
        opening_pose_identical=True,final_hold_identical=alpha['final_hold_identical'],
        pitch_range=[float(pitch.min()),float(pitch.max())],orbit_arc_degrees=float(yaw[-1]-yaw[0]),
        constant_radius_m=float(distance.mean()),camera_height_change_m=float(np.ptp(xyz[:,2])),
        max_speed_m_s=float(speed.max()),max_acceleration_m_s2=float(accel.max()),max_turn_deg_s=p['max_turn_deg_s'],
        all_frames_fit=True,public_front_side_only=True,coffee_heart=True,opening_occlusion_rays=coffee['opening_occlusion_rays'],
        source_model_preserved=True)
    (folder/'orbit-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folders',nargs='+',type=Path);a=p.parse_args()
    for folder in a.folders:run(folder)
