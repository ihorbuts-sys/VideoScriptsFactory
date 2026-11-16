"""Check actual RGBA output, camera motion, frame bounds and the final hold."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image


def solid_interior(mask, kernel=17):
    """Exact square erosion using summed areas, without a slow rank filter."""
    radius=kernel//2
    padded=np.pad(mask.astype(np.int32),((radius,radius),(radius,radius)))
    integral=np.pad(padded.cumsum(axis=0,dtype=np.int32).cumsum(axis=1,dtype=np.int32),((1,0),(1,0)))
    areas=integral[kernel:,kernel:]-integral[:-kernel,kernel:]-integral[kernel:,:-kernel]+integral[:-kernel,:-kernel]
    return areas==kernel*kernel


def validate(folder):
    meta=json.loads((folder/'meta.json').read_text());count=meta['frame_count']
    files=sorted(folder.glob('frame_*.png'))
    assert [p.name for p in files]==[f'frame_{n:04d}.png' for n in range(1,count+1)]
    assert meta['surface_isolation_check']['max_alpha_without_strokes']==0
    assert meta['meshes']['materials']==0 and not meta['meshes']['render_visible']
    assert meta['strokes']['fill'] is False
    hashes=[];ink=[];dense=[];black=white=0
    width,height=meta['resolution']
    for path,row in zip(files,meta['frames']):
        with Image.open(path) as image:
            assert image.mode=='RGBA' and image.size==(1080,1920)
            rgba=np.asarray(image);alpha=rgba[:,:,3];mask=alpha>0;rgb=rgba[:,:,:3]
            assert mask.any(),('No visible strokes',path)
            assert (alpha==0).any(),('No transparent background',path)
            # Stroke support must be sparse and contain no broad solid regions.
            interior=solid_interior(alpha>8)
            assert int(interior.sum())<=20,('Broad filled region, not thin line art',path,int(interior.sum()))
            assert mask.mean()<.15,('Unexpectedly dense alpha coverage',path,float(mask.mean()))
            assert np.max(np.ptp(rgb[mask].astype(int),axis=1))<=1,('Unexpected colored surface',path)
            black+=int(((rgb.max(axis=2)<8)&(alpha>20)).sum())
            white+=int(((rgb.min(axis=2)>245)&(alpha>80)).sum())
            bounds=row['bbox_pixels_top_left'];x0=max(0,math.floor(bounds[0])-8);x1=min(width,math.ceil(bounds[2])+8)
            y0=max(0,math.floor(bounds[1])-8);y1=min(height,math.ceil(bounds[3])+8)
            outside=mask.copy();outside[y0:y1,x0:x1]=False
            assert not outside.any(),('Strokes outside projected model bounds',path,int(outside.sum()))
            hashes.append(hashlib.sha256(rgba.tobytes()).hexdigest());ink.append(int(mask.sum()));dense.append(int(interior.sum()))
    assert black>0 and white>0,('Missing black underlay or white contour',black,white)
    hold=meta['final_hold_frames']
    if hold:assert len(set(hashes[-hold:]))==1,'The final half-second does not hold still'
    samples=meta['frames'];distances=np.array([r['camera_distance'] for r in samples]);end=meta['motion_end_frame']
    if meta['move']!='none':assert len(set(hashes[:end]))>1,'The requested camera move produced a static image sequence'
    if meta['move'] in ['push-in','pull-out']:
        assert np.ptp(np.diff(distances[:end]))<1e-5,'Camera distance is not linear'
        expected=1.6 if meta['move']=='pull-out' else 1/1.6
        assert abs(distances[-1]/distances[0]-expected)<1e-5
    if meta['move'] in ['orbit','tilt','pan']:
        assert np.ptp(distances)<1e-5,'Camera distance changed during a fixed-distance move'
    if meta['move']=='pan':
        positions=np.array([r['camera_position'] for r in samples]);assert np.max(np.ptp(positions,axis=0))<1e-6
    if meta['lens']=='wide':assert distances.min()>=.15-1e-6
    if meta['move']=='none' and not meta['minimum_focus_limited']:
        assert abs(meta['actual_final_height_fraction']-meta['requested_height_fraction'])<1e-5
    report=dict(status='passed',frames=count,resolution=[width,height],all_frames_RGBA=True,
        transparent_background=True,mesh_surface_isolation=True,no_broad_filled_regions=True,
        max_dense_interior_pixels=max(dense),ink_pixel_range=[min(ink),max(ink)],
        white_contours_present=True,black_underlay_present=True,projected_bounds_checked=True,
        final_hold_frames=hold,final_hold_identical=bool(hold),move=meta['move'],visible_motion=meta['move']!='none' and len(set(hashes[:end]))>1,
        final_camera_distance=meta['final_camera_distance'],minimum_focus_limited=meta['minimum_focus_limited'],
        fits_frame=meta['fits_frame'],every_frame_fits=meta['every_frame_fits'],
        requested_height_fraction=meta['requested_height_fraction'],actual_final_height_fraction=meta['actual_final_height_fraction'])
    (folder/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folders',nargs='+',type=Path);a=p.parse_args()
    for folder in a.folders:print(json.dumps(dict(folder=str(folder),**validate(folder))))
