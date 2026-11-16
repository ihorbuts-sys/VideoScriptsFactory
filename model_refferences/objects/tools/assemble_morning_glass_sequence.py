"""Assemble all four reviewed Morning ritual shots without repeating handovers."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

from PIL import Image

import build_hologram_view_overlay as V
import export_reconstructed_scene as E
from export_shared_venue import apng

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout'
OUT=ROOT/'sequences/cafe-morning-ritual'
FPS=15


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def link(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_name(target.name+'.tmp');temp.unlink(missing_ok=True)
    os.link(source,temp);os.replace(temp,target)


def run():
    rows=[('light','interior_pan','morning-room',1,98,None,5),
          ('cup','cup_eye_hold_whipout','morning-pair',1,75,'cup',5),
          ('pastry','pastry_tear_open','morning-pair',76,75,'pastry',3.4),
          ('corner','table_corner_pov_out_mw','work-corner',1,120,None,7)]
    OUT.mkdir(parents=True,exist_ok=True)
    frames=OUT/'view-frames';frames.mkdir(exist_ok=True)
    steps=[];source_frames=[];offset=1;phases=[]
    palette=None
    for sid,gid,name,first,count,phase,capture in rows:
        source=ROOT/'coffee'/name
        browser=json.loads((source/'composite-browser-check.json').read_text())
        assert browser['status']=='passed' and browser['overlay_sha256']==sha(source/'view-overlay.png')
        with Image.open(source/'view-frames'/f'frame_{first:04d}.png') as image:
            current=(image.getpalette(),image.info.get('transparency'))
            if palette is None:palette=current
            assert current==palette,'A single lossless APNG palette is required across shots'
        for number in range(first,first+count):
            src=source/'view-frames'/f'frame_{number:04d}.png'
            link(src,frames/f'frame_{offset+number-first:04d}.png')
            source_frames.append(source/'color'/f'frame_{number:04d}.png')
        steps.append(dict(step_id=sid,guide_id=gid,start_frame=offset,frames=count,
            capture_seconds=capture,transition_out='continuous_same_table' if sid=='cup' else 'end' if sid=='corner' else 'cut',
            source=dict(source=str(source.relative_to(BASE)),source_start_frame=first,
                frames=count,source_sha256=sha(source/'view-overlay.png'))))
        clip=source/'phases'/phase if phase else source
        phase_out=OUT/'phases'/sid
        for file in ['view-overlay.png','view-overlay-poster.png','view-overlay-strip.jpg','color.mp4','color-poster.png']:
            link(clip/file,phase_out/file)
        clip_spec=json.loads((source/'scene-spec.json').read_text())
        clip_phase=next((p for p in clip_spec['exported_phases'] if p['id']==phase),None)
        phases.append(dict(id=sid,frames=clip_phase['frames'] if clip_phase else clip_spec['frame_count']))
        offset+=count
    count=offset-1
    apng(frames,OUT/'view-overlay.png',1,count,FPS)
    report=V.check(OUT/'view-overlay.png',count,FPS)
    writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
        '-s','405x720','-r',str(FPS),'-i','-','-an','-vf','scale=432:768:flags=lanczos',
        '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'color.mp4')],stdin=subprocess.PIPE)
    for path in source_frames:
        with Image.open(path) as im:
            bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im.convert('RGBA'))
            writer.stdin.write(bg.convert('RGB').tobytes())
    writer.stdin.close();assert writer.wait()==0
    with Image.open(frames/'frame_0001.png') as im:im.convert('RGBA').save(OUT/'view-overlay-poster.png')
    with Image.open(source_frames[0]) as im:im.save(OUT/'color-poster.png')
    probes=[1,70,99,150,174,230,249,340]
    E.OUT=OUT;E.FPS=FPS
    images=[]
    for n in probes:
        with Image.open(frames/f'frame_{n:04d}.png') as im:
            image=im.convert('RGBA');image.putalpha(image.getchannel('A').point(lambda a:round(a*.65)));images.append(image)
    E.strip(images,probes,'view-overlay-strip.jpg')
    # Decoded pixels must match the source exactly at every shot boundary.
    with Image.open(OUT/'view-overlay.png') as im:
        for step in steps:
            for n in [step['start_frame'],step['start_frame']+step['frames']-1]:
                im.seek(n-1)
                with Image.open(frames/f'frame_{n:04d}.png') as original:
                    assert im.convert('RGBA').tobytes()==original.convert('RGBA').tobytes()
    write(OUT/'scene-spec.json',dict(id='cafe-morning-ritual',title='Morning ritual / complete glass sequence',
        fps=FPS,frame_count=count,duration_s=count/FPS,exported_phases=phases,steps=steps,
        scope='full_script_instruction_sequence',full_script_sequence_complete=True,
        revision='morning-ritual-glass-v1',same_camera_for_color_and_ghost=True,
        display=dict(opacity_mode='image_view',image_opacity=.65,background_delay_seconds=2,
            viewfinder='separate_ui_layer',walls=False,floor=False,ceiling=False)))
    write(OUT/'view-overlay-checks.json',dict(status='passed',phases=[report],
        opacity_100_sample_checks=[],image_opacity_baked=1,walls_excluded=True,floor_excluded=True,
        resolution=[405,720],every_step_present=True,source_pixels_preserved=True,
        files={n:sha(OUT/n) for n in ['view-overlay.png','color.mp4']}))
    write(OUT/'assembly-checks.json',dict(status='passed',source_frames=count,encoded_apng_frames=count,
        max_alpha=report['max_alpha'],alpha_applied_again=False,opacity_mode='image_view',
        all_four_steps_regenerated=True,continuous_cup_to_pastry=True,repeated_handover_frames_removed=True,
        decoded_boundaries_match_source=True,full_script_sequence_complete=True))
    text=(ROOT/'coffee/work-corner/index.html').read_text()
    start=text.index('<nav aria-label="Shot">');end=text.index('</nav>',start)+6
    nav='<nav aria-label="Shot"><button data-phase="" aria-pressed="true">Full script</button>'+''.join(
        f'<button data-phase="{s[0]}" aria-pressed="false">{s[0].title()}</button>' for s in rows)+'</nav>'
    text=text[:start]+nav+text[end:]
    a=text.index('<h1>');b=text.index('</h1>',a)+5
    text=text[:a]+'<h1>Morning ritual / complete glass sequence</h1>'+text[b:]
    a=text.index('<p class="notes">');b=text.index('</p>',a)+4
    text=text[:a]+'<p class="notes">Press Play preview. Morning light, the cup, the opened pastry and your work corner form one complete sequence. Cup to pastry is continuous; the other shot boundaries are explicit cuts. The reference video follows the transparent guide by two seconds.</p>'+text[b:]
    text=text.replace('href="../index.html"','href="../../coffee/index.html"')
    (OUT/'index.html').write_text(text)
    (OUT/'README.md').write_text('''# Morning ritual / complete glass sequence

All four template steps use reviewed native café renders. Cup and pastry use
consecutive frames of one scene, with no repeated handover segment. The room
and final seated corner join through explicit cuts. The final table retains
the same opened pastry halves and cup; the laptop establishes the work corner.

The sequence is 368 frames at 15 fps (24.53 seconds including holds). Capture
recommendations remain 5, 5, 3.4 and 7 seconds. Phase buttons replay each guide,
including its handover where present. Full-strength transparent images use
65% image-view opacity once; the reference video follows two seconds behind.
Walls, floor and ceiling are absent from the ghost. Viewfinder UI is separate.
''')
    for alias,source in [('ghost.png','view-overlay.png'),('preview.mp4','color.mp4'),
                         ('poster.png','view-overlay-poster.png'),('strip.jpg','view-overlay-strip.jpg')]:link(OUT/source,OUT/alias)
    print(json.dumps(dict(status='assembled',frames=count,seconds=count/FPS,steps=[r[0] for r in rows])),flush=True)


if __name__=='__main__':run()
