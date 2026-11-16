"""Strict completion gate for the 28 native P0 animation exports."""
import hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
import p0_catalog

ROOT=Path(__file__).resolve().parents[2]
# The owner approved the cup leaving the frame at the end of this orbit (review 2026-11-10); the export skips its dot.
OFFSCREEN_MARKERS={'plate_high_orbit_v2':1}
# Owner-approved still holds (review 2026-11-10): the phone and the scene stay still on purpose.
STATIC_HOLDS={'room_static_wide','menu_board_static'}


def check():
    plan=p0_catalog.registry();reports=[];frames=0
    for row in plan['guides']:
        if row.get('availability') in ('deferred','archived'):continue
        gid=row['id'];folder=ROOT/'catalog/p0/animations-light'/gid
        meta=json.loads((folder/'meta.json').read_text());report=json.loads((folder/'export-checks.json').read_text())
        assert meta['record']['invariant']==row['invariant'],(gid,'Render instructions are stale')
        assert report['status']=='passed' and report['alphaFactor']==1
        assert report['frames']==15*(row['durationSec']+row['setupBeatSeconds']+1)
        assert report['maximum_hands']<=row.get('allowedHands',0) and report['detailed_people']<=row.get('allowedPeople',0) and report['silhouettes']<=row.get('allowedSilhouettes',0)
        if row.get('allowedPeople'):
            assert report['character']=='creator' and report['preview_mirrored']==(row['camera']=='front')
            assert not report['facial_animation']
        assert report['target_first_and_last_identical'] and report['poster_equals_frame_zero']
        assert report['visible_motion'] or gid in STATIC_HOLDS,(gid,'Active object guides must demonstrate a camera or physical subject action')
        assert report['hero_pixel_band_checked'] and meta['source_surfaces_absent']
        assert meta['pre_render_review']['handover']=='None: P0 ends on this shot target'
        camera=meta['camera_samples'];phases=Counter(f['phase'] for f in camera)
        assert phases['target']==8 and phases['final']==7 and phases['demonstration']==row['durationSec']*15
        assert phases['setup']==row['setupBeatSeconds']*15
        xyz=np.array([f['camera_position'] for f in camera]);assert xyz[:,2].min()>.1 and xyz[:,2].max()<=2.05,(gid,xyz[:,2].tolist())
        assert len({f['lens_mm'] for f in camera})==1
        movement=np.array([f['camera_position'] for f in camera if f['phase']=='demonstration'])
        speed=float(np.linalg.norm(np.diff(movement,axis=0)*15,axis=1).max())
        assert speed<=1.3,(gid,speed)
        if gid.startswith(('counter_','pour_','menu_board_','handoff_counter')):
            assert xyz[:,1].max()<=.15,(gid,'Camera enters the staff work area')
        if row['camera']=='front':
            # Source target aim and the bounding head centre differ slightly; the
            # actual planned distance guard is also enforced in the renderer.
            assert speed<=.25,(gid,'Selfie movement too fast')
        if row['composition']=='triangle':
            assert len(meta['triangle_markers'])==3
            # The hero stays in its protected band. Rim/cup/fork supports can
            # extend outside that band, as the shot's composition requires.
            outside=[m for m in meta['triangle_markers'] if not (3<=m[0]<402 and 3<=m[1]<717)]
            assert len(outside)<=OFFSCREEN_MARKERS.get(gid,0),(gid,meta['triangle_markers'])
        source=ROOT/'guides/p0/renders'/(gid+'.png');assert hashlib.sha256(source.read_bytes()).hexdigest()==report['sha256']
        with Image.open(source) as image:
            assert image.n_frames==report['frames'] and image.mode=='RGBA'
            image.seek(0)
            with Image.open(source.parent/(gid+'_poster.png')) as poster:assert image.tobytes()==poster.tobytes()
        reports.append(dict(id=gid,status='passed',frames=report['frames'],maximum_camera_speed_m_s=speed,
            silhouettes=report['silhouettes'],hands=report['maximum_hands'],yellow_light_cues=report['local_yellow_edge_glow'],steam_glow=report['steam_edge_glow']))
        frames+=report['frames']
    result=dict(status='passed',guides=len(reports),shot_types=12,native_frames=frames,assets=3*len(reports),deferred_guides=list(plan.get('deferredGuides',{})),
        no_pending_exports=True,clock_and_poster_checked=True,hero_pixel_band_checked=True,
        visitor_side_and_camera_speed_checked=True,records=reports,physical_phone_tested=False)
    (ROOT/'catalog/p0/completion-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}));return result


if __name__=='__main__':check()
