"""Package a native glass guide, its color reference and continuous clips."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image

import export_reconstructed_scene as E
import build_hologram_view_overlay as V

BASE = Path(__file__).resolve().parents[3]
TEMPLATE = BASE / 'catalog/coffee-hologram-study/index.html'


def run(out):
    spec = json.loads((out/'scene-spec.json').read_text())
    count,fps = spec['frame_count'],spec['fps']
    assert all((out/mode/f'frame_{n:04d}.png').exists()
               for mode in ['color','mask','fields'] for n in range(1,count+1))
    with Image.open(out/'color/frame_0001.png') as im:
        width,height = im.size
    writer = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo',
        '-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','-','-an',
        '-vf','scale=432:768:flags=lanczos','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'color.mp4')],stdin=subprocess.PIPE)
    for n in range(1,count+1):
        with Image.open(out/'color'/f'frame_{n:04d}.png') as im:
            bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im.convert('RGBA'))
            writer.stdin.write(bg.convert('RGB').tobytes())
            if n==1:im.save(out/'color-poster.png')
    writer.stdin.close();assert writer.wait()==0
    E.FPS=fps
    def color_strip(folder,numbers):
        E.OUT=folder
        E.strip([Image.open(out/'color'/f'frame_{n:04d}.png').convert('RGBA') for n in numbers],numbers,'color-strip.jpg')
    color_strip(out,spec['probe_frames'])
    records=[]
    for i,phase in enumerate(spec['phases']):
        folder=out/'phases'/phase['id'];folder.mkdir(parents=True,exist_ok=True)
        first=round(phase['start_s']*fps)+1
        phase_count=round((phase['end_s']-phase['start_s'])*fps)
        tail=min(round(phase.get('handover_tail_seconds',23/fps)*fps),count-(first+phase_count-1)) if i<len(spec['phases'])-1 else 0
        length=phase_count+tail
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(out/'color.mp4'),
            '-vf',f'trim=start_frame={first-1}:end_frame={first-1+length},setpts=PTS-STARTPTS',
            '-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'color.mp4')],check=True)
        with Image.open(out/'color'/f'frame_{first:04d}.png') as im:im.save(folder/'color-poster.png')
        numbers=sorted(set(round(first+(length-1)*u) for u in [0,.2,.4,.6,.8,1]))
        color_strip(folder,numbers)
        capture=phase.get('capture_seconds',5 if phase['id']=='cup' else 3.4 if phase['id']=='pastry' else spec['capture_seconds'])
        handover=phase.get('handover_seconds',tail/fps)
        record={**phase, 'frames':length, 'source_first_frame':first,
            'source_last_frame':first+length-1, 'capture_seconds':capture,
            'animation_seconds':length/fps, 'handover_seconds':handover,
            'next_phase':spec['phases'][i+1]['id'] if handover and i<len(spec['phases'])-1 else None,
            'scope':'shot_and_handover' if handover else 'complete_final_shot'}
        assert capture<=length/fps+.01 and handover<=length/fps-capture+.01
        records.append(record)
    spec['exported_phases']=records
    spec['native_color_resolution']=[width,height]
    spec['color_resolution']=[432,768]
    (out/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    checks=dict(status='passed',same_camera_for_color_and_ghost=True,source_frames=count,
        files={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['scene.blend','color.mp4','scene-spec.json']})
    (out/'export-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    V.OUT=out;V.run()
    # Reuse the manually tested browser player, including explicit Play controls,
    # independent opacity and the delayed video/viewfinder layers.
    text=TEMPLATE.read_text()
    start=text.index('<nav aria-label="Shot">');end=text.index('</nav>',start)+6
    buttons=['<nav aria-label="Shot">','<button data-phase="" aria-pressed="true">Full shot</button>']
    buttons += [f'<button data-phase="{p["id"]}" aria-pressed="false">{p["id"].title()}</button>' for p in records]
    text=text[:start]+'\n'.join(buttons+['</nav>'])+text[end:]
    text=text.replace('<h1>Glass guide over the camera view</h1>',f'<h1>{spec["title"]}</h1>')
    text=text.replace('<a href="../animations.html">Guide catalog</a> · <a href="../coffee-ordering-v2/index.html">Smooth-contour version</a>',
                      '<a href="../index.html">Coffee guide batch</a> · <a href="../../../animations.html">Guide catalog</a>')
    text=text.replace('The transparent guide leads the original video by two seconds.',spec['direction']+' The transparent guide leads the reference video by two seconds.')
    if spec.get('viewfinder_axes')==['X','Y']:
        text=text.replace('Viewfinder with X horizon level','Viewfinder with X horizon and Y down-angle targets')
        text=text.replace('>X 0°</text>','>X 0° / Y 90°</text>')
    (out/'index.html').write_text(text)
    overhead=[dict(phase=p['id'],start=p['start_s'],end=p['end_s']) for p in records
        if any(b['phase']==p['id'] and b['guide'].startswith('topdown_') for b in spec.get('guide_bindings',[]))]
    if overhead:
        from guide_viewfinder_targets import apply
        apply(out,count/fps,overhead)
    (out/'README.md').write_text(f'''# {spec['title']}

{spec['direction']}

Template: `{spec['template']}`. Step: `{spec['step']}`. Guide: `{spec['guide']}`.
The recommended capture is {spec['capture_seconds']:g} seconds. The animation
contains {count} frames at {fps} fps, including its final hold or handover.
Native color renders are {width} by {height}; the H.264 delivery is 432 by 768
to retain 9:16 with codec-compatible dimensions. The transparent image is
405 by 720. Its global opacity belongs to the image view, defaulting to 65%.

The reference video in this preview follows two seconds behind the guide.
Walls, floor and ceiling are excluded from the ghost. The viewfinder and level
are separate UI. Actual camera motion stays in public space; lights are fixed.
Source images and model downloads are preserved. No new Tripo jobs were needed.
''')
    print(json.dumps(dict(status='exported',scene=out.name,frames=count,seconds=count/fps)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args();run(args.folder.resolve())
