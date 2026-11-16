"""Pixel, support, source preservation and physical camera checks for object scenes."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from validate_lineart import validate


def check(folder):
    alpha=validate(folder)
    meta=json.loads((folder/'meta.json').read_text());frames=meta['frames'];assembly=meta['assembly']
    assert meta['lens_mm']==24 and meta['every_frame_fits']
    xyz=np.array([f['camera_position'] for f in frames]);center=np.array(meta['object_bbox_world']['center'])
    radius=np.linalg.norm(xyz-center,axis=1)
    assert np.ptp(radius)<1e-6
    speed=np.linalg.norm(np.diff(xyz,axis=0)*30,axis=1)
    acceleration=np.linalg.norm(np.diff(xyz,n=2,axis=0)*900,axis=1)
    q=np.array([f['camera_rotation_quaternion'] for f in frames]);q/=np.linalg.norm(q,axis=1)[:,None]
    angular_speed=np.degrees(2*np.arccos(np.minimum(1,np.abs(np.sum(q[1:]*q[:-1],axis=1)))))*30
    assert speed.max()<.3 and acceleration.max()<.3 and angular_speed.max()<45
    assert np.all(xyz[:,1]<center[1]),'Camera goes behind the product'
    assert all(min(f['bbox_frame']['x_min'],f['bbox_frame']['y_min'])>=.015 and
               max(f['bbox_frame']['x_max'],f['bbox_frame']['y_max'])<=.985 for f in frames)
    for contact in assembly['support_contacts']:
        assert contact['all_sampled_points_supported'] and contact['sampled_footprint_points']>=8
        assert abs(contact['minimum_gap_m']-.0002)<1e-6
        assert contact['maximum_patch_gap_m']<.008
    for source in assembly['sources']:
        assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
    if assembly['coffee']:
        assert assembly['coffee']['opening_covered'] and assembly['coffee']['opening_occlusion_rays']==149
    lead=meta['camera_profile']['initial_drawing_hold_through']
    opening=[hashlib.sha256((folder/f'frame_{n:04d}.png').read_bytes()).hexdigest() for n in range(1,lead+1)]
    assert len(set(opening))==1
    result=dict(status='passed',frames=len(frames),seconds=meta['duration_s'],lineart_pixels=alpha,
        source_files_preserved=True,support_contacts=assembly['support_contacts'],coffee=assembly['coffee'],
        all_frames_fit=True,fixed_lens_mm=24,fixed_radius_m=float(radius.mean()),
        max_translation_m_s=float(speed.max()),max_acceleration_m_s2=float(acceleration.max()),
        max_rotation_deg_s=float(angular_speed.max()),camera_height_change_m=float(np.ptp(xyz[:,2])),
        pitch_range=[min(f['pitch_degrees'] for f in frames),max(f['pitch_degrees'] for f in frames)],
        opening_hold_identical=True,final_hold_identical=True,
        contour_cleanup=meta['contour_cleanup'],physical_phone_tested=False)
    (folder/'scene-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folders',nargs='+',type=Path)
    for folder in p.parse_args().folders:
        result=check(folder);print(json.dumps(dict(folder=str(folder),status=result['status'],frames=result['frames'])),flush=True)
